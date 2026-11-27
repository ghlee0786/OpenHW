/* openhw-daynight: 조도 → 히스테리시스 → ICR(DRV8837) · IR LED · ISP IR 모드 전환 데몬.
 * 계약 C-001 v1.8 7절 GPIO, O-31(켬 비율 ≤25%), O-33(IR_PWM 극성·순서, CAM_EN=1 일 때만 폴링), V-004b R2(5ms).
 * 하드웨어 접근은 sysfs gpio/pwm 와 i2c-dev 만 쓴다. ISP 전환은 sscma-node 가 /run/daynight/mode 를 읽어 한다. */
#include "daynight_logic.h"

#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define GPIO_ICR_IN1   495  /* GPIO15/IR_CUT, XGPIOA_15 */
#define GPIO_ICR_IN2   352  /* WH_PWM, PWR_GPIO_0 */
#define GPIO_IR_EN     431  /* IR_LED_EN, XGPIOC_15 (portc 베이스 416 추론) */
#define GPIO_CAM_EN    358  /* CAM_EN, PWR_GPIO_6 — S70hardware 가 켠다. 데몬은 읽기만 */
#define PWM_CHANNEL    2    /* PWM_2 = pwm0 컨트롤러 채널 2 */
#define LTR329_ADDR    0x29
#define LTR329_GAIN    1
#define LTR329_INT_MS  100
#define MODE_DIR       "/run/daynight"
#define MODE_FILE      MODE_DIR "/mode"

static volatile sig_atomic_t g_stop;
static dn_config g_cfg;
static char g_conf_path[256] = "/etc/openhw/daynight.conf";
static char g_i2c_dev[160] = "/dev/i2c-2";
static char g_pwm_chip[128] = "/sys/class/pwm/pwmchip0";
static char g_als_source[160] = "ltr329";     /* ltr329 | adc (차선: LIGHT_SENSE ADC1) */
static char g_adc_path[160] = "";             /* ADC 드라이버·경로 미확인 — 설정으로 준다 */
static double g_adc_lux_per_count = 1.0;
static uint32_t g_pwm_period;

static int64_t now_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void sleep_ms(int ms)
{
    struct timespec ts = { ms / 1000, (long)(ms % 1000) * 1000000L };
    while (nanosleep(&ts, &ts) == -1 && errno == EINTR)
        ;
}

static int write_str(const char *path, const char *s)
{
    int fd = open(path, O_WRONLY);
    if (fd < 0)
        return -1;
    ssize_t n = write(fd, s, strlen(s));
    close(fd);
    return n == (ssize_t)strlen(s) ? 0 : -1;
}

static int write_u32(const char *path, uint32_t v)
{
    char b[16];
    snprintf(b, sizeof b, "%u", v);
    return write_str(path, b);
}

static int read_long(const char *path, long *v)
{
    char b[32] = {0};
    int fd = open(path, O_RDONLY);
    if (fd < 0)
        return -1;
    ssize_t n = read(fd, b, sizeof b - 1);
    close(fd);
    if (n <= 0)
        return -1;
    *v = strtol(b, NULL, 10);
    return 0;
}

static int gpio_prepare(int gpio, int output)
{
    char p[64];
    snprintf(p, sizeof p, "/sys/class/gpio/gpio%d", gpio);
    if (access(p, F_OK) != 0) {
        char n[8];
        snprintf(n, sizeof n, "%d", gpio);
        if (write_str("/sys/class/gpio/export", n) != 0)
            return -1;
    }
    if (!output)
        return 0;
    snprintf(p, sizeof p, "/sys/class/gpio/gpio%d/direction", gpio);
    return write_str(p, "low");   /* 출력 Low 로 시작 (계약 7절 기본 상태) */
}

static int gpio_set(int gpio, int v)
{
    char p[64];
    snprintf(p, sizeof p, "/sys/class/gpio/gpio%d/value", gpio);
    return write_str(p, v ? "1" : "0");
}

static int gpio_get(int gpio)
{
    char p[64];
    long v;
    snprintf(p, sizeof p, "/sys/class/gpio/gpio%d/value", gpio);
    return read_long(p, &v) == 0 ? (int)v : -1;
}

static int pwm_attr(const char *attr, uint32_t v)
{
    char p[200];
    snprintf(p, sizeof p, "%s/pwm%d/%s", g_pwm_chip, PWM_CHANNEL, attr);
    return write_u32(p, v);
}

/* IR_PWM 을 전기 High(끔)로 둔다. 켬 비율 0 = duty == period */
static int pwm_off(void)
{
    return pwm_attr("duty_cycle", dn_pwm_duty_ns(g_pwm_period, 0));
}

static int pwm_prepare(void)
{
    char p[200];
    snprintf(p, sizeof p, "%s/pwm%d", g_pwm_chip, PWM_CHANNEL);
    if (access(p, F_OK) != 0) {
        snprintf(p, sizeof p, "%s/export", g_pwm_chip);
        char n[4];
        snprintf(n, sizeof n, "%d", PWM_CHANNEL);
        if (write_str(p, n) != 0)
            return -1;
    }
    g_pwm_period = dn_pwm_period_ns(g_cfg.pwm_freq_hz);
    /* duty ≤ period 를 지키려고 duty 를 0 으로 내린 뒤 period → duty(High 100%) → enable.
     * 이 동안 IR_LED_EN 은 Low 라 LED 전원이 없다. */
    pwm_attr("duty_cycle", 0);
    if (pwm_attr("period", g_pwm_period) != 0 || pwm_off() != 0)
        return -1;
    return pwm_attr("enable", 1);
}

static void icr_pulse(int in1)
{
    gpio_set(GPIO_ICR_IN1, in1);
    gpio_set(GPIO_ICR_IN2, !in1);
    sleep_ms(g_cfg.icr_pulse_ms);
    gpio_set(GPIO_ICR_IN1, 0);   /* 0/0 = 코스트(무전류) */
    gpio_set(GPIO_ICR_IN2, 0);
}

static void write_mode(dn_mode m)
{
    const char *s = m == DN_NIGHT ? "night\n" : "day\n";
    mkdir(MODE_DIR, 0755);
    int fd = open(MODE_DIR "/mode.tmp", O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0 || write(fd, s, strlen(s)) != (ssize_t)strlen(s))
        perror("daynight: mode");
    if (fd >= 0)
        close(fd);
    rename(MODE_DIR "/mode.tmp", MODE_FILE);   /* sscma-node 가 반쯤 쓴 파일을 읽지 않게 */
}

static void apply(dn_mode to)
{
    dn_action a[DN_PLAN_MAX];
    int n = dn_plan(to, a);
    for (int i = 0; i < n; i++) {
        switch (a[i]) {
        case DN_ACT_IR_PWM_OFF: pwm_off(); break;
        case DN_ACT_IR_EN_ON:   gpio_set(GPIO_IR_EN, 1); break;
        case DN_ACT_IR_EN_OFF:  gpio_set(GPIO_IR_EN, 0); break;
        case DN_ACT_IR_PWM_SET: pwm_attr("duty_cycle", dn_pwm_duty_ns(g_pwm_period, g_cfg.ir_on_ratio)); break;
        case DN_ACT_ICR_NIGHT:  icr_pulse(g_cfg.icr_night_in1); break;
        case DN_ACT_ICR_DAY:    icr_pulse(!g_cfg.icr_night_in1); break;
        case DN_ACT_ISP_NIGHT:  write_mode(DN_NIGHT); break;
        case DN_ACT_ISP_DAY:    write_mode(DN_DAY); break;
        }
    }
    fprintf(stderr, "daynight: -> %s\n", to == DN_NIGHT ? "night" : "day");
}

static int ltr_write(int fd, uint8_t reg, uint8_t val)
{
    uint8_t b[2] = { reg, val };
    return write(fd, b, 2) == 2 ? 0 : -1;
}

static int ltr_open(void)
{
    int fd = open(g_i2c_dev, O_RDWR);
    if (fd < 0)
        return -1;
    if (ioctl(fd, I2C_SLAVE, LTR329_ADDR) < 0 ||
        ltr_write(fd, 0x85, 0x03) != 0 ||   /* MEAS_RATE: 적분 100ms, 반복 500ms */
        ltr_write(fd, 0x80, 0x01) != 0) {   /* ALS_CONTR: active, gain 1x */
        close(fd);
        return -1;
    }
    return fd;
}

static int ltr_read_lux(int fd, double *lux)
{
    uint8_t reg = 0x88, d[4];   /* CH1 L/H 다음 CH0 L/H 순서로 읽어야 한다 */
    if (write(fd, &reg, 1) != 1 || read(fd, d, 4) != 4)
        return -1;
    uint16_t ch1 = (uint16_t)(d[0] | d[1] << 8), ch0 = (uint16_t)(d[2] | d[3] << 8);
    *lux = dn_ltr329_lux(ch0, ch1, LTR329_GAIN, LTR329_INT_MS);
    return 0;
}

static void load_config(void)
{
    dn_config_default(&g_cfg);
    FILE *f = fopen(g_conf_path, "r");
    if (f) {
        char line[256];
        while (fgets(line, sizeof line, f)) {
            char k[64], v[160];
            if (line[0] == '#' || sscanf(line, " %63[^= ] = %159s", k, v) != 2)
                continue;
            if (!strcmp(k, "als_source"))             snprintf(g_als_source, sizeof g_als_source, "%s", v);
            else if (!strcmp(k, "adc_path"))          snprintf(g_adc_path, sizeof g_adc_path, "%s", v);
            else if (!strcmp(k, "adc_lux_per_count")) g_adc_lux_per_count = strtod(v, NULL);
            else if (!strcmp(k, "i2c_dev"))           snprintf(g_i2c_dev, sizeof g_i2c_dev, "%s", v);
            else if (!strcmp(k, "pwm_chip"))          snprintf(g_pwm_chip, sizeof g_pwm_chip, "%.127s", v);
            else if (dn_config_set(&g_cfg, k, v) != 0)
                fprintf(stderr, "daynight: 설정 무시 %s=%s\n", k, v);
        }
        fclose(f);
    }
    if (dn_config_finalize(&g_cfg) != 0) {
        fprintf(stderr, "daynight: night_lux < day_lux 가 아니라 기본값으로 되돌린다\n");
        dn_config_default(&g_cfg);
        dn_config_finalize(&g_cfg);
    }
}

static void on_signal(int s) { (void)s; g_stop = 1; }

int main(int argc, char **argv)
{
    if (argc > 1)
        snprintf(g_conf_path, sizeof g_conf_path, "%s", argv[1]);
    load_config();
    signal(SIGTERM, on_signal);
    signal(SIGINT, on_signal);

    if (gpio_prepare(GPIO_IR_EN, 1) || gpio_prepare(GPIO_ICR_IN1, 1) || gpio_prepare(GPIO_ICR_IN2, 1) ||
        gpio_prepare(GPIO_CAM_EN, 0) || pwm_prepare()) {
        fprintf(stderr, "daynight: gpio/pwm 준비 실패: %s\n", strerror(errno));
        return 1;
    }

    dn_hyst h;
    dn_hyst_init(&h, DN_DAY);
    apply(DN_DAY);   /* 알려진 상태(필터 넣음·IR 끔)에서 시작 */

    int ltr = -1, prev_cam = 0;
    int64_t cam_on_at = 0;
    while (!g_stop) {
        int cam = gpio_get(GPIO_CAM_EN) == 1;
        if (cam && !prev_cam)
            cam_on_at = now_ms();
        if (!cam && ltr >= 0) {   /* 센서 전원이 꺼지면 LTR-329 도 꺼진다 → 다시 초기화 */
            close(ltr);
            ltr = -1;
        }
        prev_cam = cam;

        double lux;
        int have = 0;
        if (!strcmp(g_als_source, "adc")) {
            long cnt;
            if (g_adc_path[0] && read_long(g_adc_path, &cnt) == 0) {
                lux = cnt * g_adc_lux_per_count;
                have = 1;
            }
        } else if (dn_may_poll(cam, now_ms() - cam_on_at)) {
            if (ltr < 0)
                ltr = ltr_open();   /* 첫 측정은 다음 주기에 읽는다 */
            else if (ltr_read_lux(ltr, &lux) == 0)
                have = 1;
        }
        if (have && dn_hyst_update(&h, &g_cfg, lux))
            apply(h.mode);
        sleep_ms(g_cfg.poll_ms);
    }

    /* 끝낼 때: IR 끔(EN 0 먼저 → PWM High), ICR 은 코스트로 둔다 */
    gpio_set(GPIO_IR_EN, 0);
    pwm_off();
    if (ltr >= 0)
        close(ltr);
    return 0;
}
