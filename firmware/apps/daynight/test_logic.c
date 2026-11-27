/* 호스트 시험: make test */
#include "daynight_logic.h"

#include <math.h>
#include <stdio.h>

static int pass, fail;
#define CHECK(cond, name) do { if (cond) { pass++; } else { fail++; printf("FAIL %s (%s:%d)\n", name, __FILE__, __LINE__); } } while (0)

static int index_of(const dn_action *a, int n, dn_action x)
{
    for (int i = 0; i < n; i++)
        if (a[i] == x) return i;
    return -1;
}

static void t_hysteresis(void)
{
    dn_config c; dn_config_default(&c); dn_config_finalize(&c);
    dn_hyst h; dn_hyst_init(&h, DN_DAY);
    CHECK(dn_hyst_update(&h, &c, 1.0) == 0 && h.mode == DN_DAY, "hyst: 1회 어두움은 유지");
    CHECK(dn_hyst_update(&h, &c, 1.0) == 0, "hyst: 2회 유지");
    CHECK(dn_hyst_update(&h, &c, 1.0) == 1 && h.mode == DN_NIGHT, "hyst: 3회 연속 → 밤");
    /* 밤에서 night_lux~day_lux 사이 값은 전환 없음 */
    for (int i = 0; i < 10; i++) dn_hyst_update(&h, &c, 10.0);
    CHECK(h.mode == DN_NIGHT, "hyst: 중간 대역(10 lux)은 밤 유지");
    dn_hyst_update(&h, &c, 50.0); dn_hyst_update(&h, &c, 50.0);
    dn_hyst_update(&h, &c, 1.0);  /* 연속이 끊김 */
    dn_hyst_update(&h, &c, 50.0); dn_hyst_update(&h, &c, 50.0);
    CHECK(h.mode == DN_NIGHT, "hyst: 연속이 끊기면 다시 센다");
    CHECK(dn_hyst_update(&h, &c, 50.0) == 1 && h.mode == DN_DAY, "hyst: 3회 연속 밝음 → 낮");
    /* 경계값: 정확히 night_lux 는 어둡지 않다 */
    dn_hyst_init(&h, DN_DAY);
    for (int i = 0; i < 5; i++) dn_hyst_update(&h, &c, c.night_lux);
    CHECK(h.mode == DN_DAY, "hyst: night_lux 경계값은 낮 유지");
}

static void t_duty_limit(void)
{
    CHECK(dn_clamp_on_ratio(0.9) == DN_ON_RATIO_MAX, "duty: 0.9 요청 → 0.25");
    CHECK(dn_clamp_on_ratio(0.25) == 0.25, "duty: 0.25 그대로");
    CHECK(dn_clamp_on_ratio(0.1) == 0.1, "duty: 0.1 그대로");
    CHECK(dn_clamp_on_ratio(-1) == 0, "duty: 음수 → 0");
    CHECK(dn_clamp_on_ratio(NAN) == 0, "duty: NaN → 0");

    dn_config c; dn_config_default(&c);
    dn_config_set(&c, "ir_on_ratio", "1.0");
    dn_config_set(&c, "pwm_freq_hz", "20000");
    dn_config_finalize(&c);
    CHECK(c.ir_on_ratio <= DN_ON_RATIO_MAX, "duty: 설정 1.0 도 0.25 로 강제");
    CHECK(c.pwm_freq_hz <= DN_PWM_FREQ_MAX_HZ, "pwm: 주파수 ≤500Hz 강제");

    /* 모든 주파수·요청에서 Low(켬) 시간 / 주기 ≤ 0.25 */
    int ok = 1;
    for (int f = 1; f <= 2000; f += 7)
        for (int r = 0; r <= 100; r++) {
            uint32_t p = dn_pwm_period_ns(f);
            uint32_t d = dn_pwm_duty_ns(p, r / 100.0);
            if (d > p || (double)(p - d) / p > DN_ON_RATIO_MAX + 1e-12 || p < 1000000000u / DN_PWM_FREQ_MAX_HZ)
                ok = 0;
        }
    CHECK(ok, "duty: 전 범위에서 켬 비율 ≤25%·주파수 ≤500Hz");
    CHECK(dn_pwm_duty_ns(2500000, 0) == 2500000, "duty: 켬 0 → 전기 High 100%");
    CHECK(dn_pwm_duty_ns(2500000, 0.25) == 1875000, "duty: 400Hz 25% → High 1.875ms");
}

static void t_sequence(void)
{
    dn_action a[DN_PLAN_MAX];
    int n = dn_plan(DN_NIGHT, a);
    int off = index_of(a, n, DN_ACT_IR_PWM_OFF), en = index_of(a, n, DN_ACT_IR_EN_ON), set = index_of(a, n, DN_ACT_IR_PWM_SET);
    CHECK(off >= 0 && en >= 0 && off < en, "seq: 밤 — IR_PWM High 가 IR_LED_EN 보다 먼저");
    CHECK(set > en, "seq: 밤 — 켬 비율 설정은 EN 뒤");
    CHECK(index_of(a, n, DN_ACT_ICR_NIGHT) >= 0 && index_of(a, n, DN_ACT_ISP_NIGHT) >= 0, "seq: 밤 — ICR·ISP 포함");
    n = dn_plan(DN_DAY, a);
    off = index_of(a, n, DN_ACT_IR_PWM_OFF); int enoff = index_of(a, n, DN_ACT_IR_EN_OFF);
    CHECK(enoff == 0 && off > enoff, "seq: 낮 — EN 을 맨 먼저 끄고 그 뒤 IR_PWM High");
    CHECK(index_of(a, n, DN_ACT_IR_EN_ON) < 0 && index_of(a, n, DN_ACT_IR_PWM_SET) < 0, "seq: 낮 — IR 켜는 동작 없음");
}

/* 핀 상태 모의: PWM 은 완전 High 가 안 된다(cvi_pwm period-1) → 켬 비율 최소값이 0 이 아니라고 가정.
 * IR LED 에 전류가 흐르는 조건 = EN 이 1 이고 PWM Low 비율 > 0. 모든 전환 과정의 각 단계에서 검사한다. */
static void t_pin_sim(void)
{
    const double residual = 1.0 / 250000;   /* PWM "끔" 에도 남는 Low 비율(예: 400Hz, 100MHz 클록) */
    dn_config c; dn_config_default(&c); dn_config_finalize(&c);
    int en = 0; double low = residual;      /* 시작: 데몬은 EN 을 먼저 Low 로 만든 뒤 PWM 을 준비한다 */
    int ok_on_order = 1, ok_off = 1, ok_cap = 1;
    for (int cycle = 0; cycle < 3; cycle++) {
        for (int to = DN_NIGHT; to >= DN_DAY; to--) {
            dn_action a[DN_PLAN_MAX];
            int n = dn_plan((dn_mode)to, a);
            for (int i = 0; i < n; i++) {
                switch (a[i]) {
                case DN_ACT_IR_PWM_OFF: low = residual; break;
                case DN_ACT_IR_PWM_SET: low = 1.0 - (double)dn_pwm_duty_ns(dn_pwm_period_ns(c.pwm_freq_hz), c.ir_on_ratio) / dn_pwm_period_ns(c.pwm_freq_hz); break;
                case DN_ACT_IR_EN_ON:   if (low > residual) ok_on_order = 0; en = 1; break;
                case DN_ACT_IR_EN_OFF:  en = 0; break;
                default: break;
                }
                if (en && low > DN_ON_RATIO_MAX + 1e-12) ok_cap = 0;
            }
            if (to == DN_DAY && en != 0) ok_off = 0;   /* 낮 = EN 0 → 잔여 Low 와 상관없이 전류 없음 */
        }
    }
    CHECK(ok_on_order, "sim: EN 을 켤 때 PWM 은 항상 끔(High) 상태");
    CHECK(ok_cap, "sim: EN=1 인 동안 켬 비율 ≤25%");
    CHECK(ok_off, "sim: 낮 전환 뒤 EN=0 (PWM 잔여 Low 가 있어도 IR 꺼짐)");
}

static void t_poll_gate(void)
{
    CHECK(!dn_may_poll(0, 100000), "poll: CAM_EN=0 이면 금지");
    CHECK(!dn_may_poll(1, 0), "poll: 켠 직후 0ms 금지");
    CHECK(!dn_may_poll(1, DN_CAM_SETTLE_MS - 1), "poll: 4ms 금지");
    CHECK(dn_may_poll(1, DN_CAM_SETTLE_MS), "poll: 5ms 허용");
}

static void t_config(void)
{
    dn_config c; dn_config_default(&c);
    CHECK(dn_config_finalize(&c) == 0, "conf: 기본값 유효");
    dn_config_set(&c, "icr_pulse_ms", "10");
    dn_config_finalize(&c);
    CHECK(c.icr_pulse_ms == DN_ICR_PULSE_MIN_MS, "conf: 펄스 10ms → 100ms");
    dn_config_set(&c, "icr_pulse_ms", "9000");
    dn_config_finalize(&c);
    CHECK(c.icr_pulse_ms == DN_ICR_PULSE_MAX_MS, "conf: 펄스 9000ms → 500ms");
    dn_config_set(&c, "night_lux", "30");
    CHECK(dn_config_finalize(&c) == -1, "conf: night_lux ≥ day_lux 거부");
    CHECK(dn_config_set(&c, "unknown", "1") == -1, "conf: 모르는 키 거부");
    CHECK(dn_config_set(&c, "day_lux", "abc") == -1, "conf: 숫자 아님 거부");
    CHECK(c.isp_mirror_flip == 1, "conf: mirror_flip 기본 켬");
}

static void t_lux(void)
{
    CHECK(dn_ltr329_lux(0, 0, 1, 100) == 0, "lux: 0");
    double l = dn_ltr329_lux(1000, 100, 1, 100);   /* ratio 0.09 */
    CHECK(fabs(l - (1.7743 * 1000 + 1.1059 * 100)) < 1e-6, "lux: 낮은 ratio 식");
    CHECK(fabs(dn_ltr329_lux(1000, 100, 2, 200) - l / 4) < 1e-6, "lux: gain·적분시간 보정");
    CHECK(dn_ltr329_lux(10, 1000, 1, 100) == 0, "lux: ratio ≥0.85 → 0");
}

int main(void)
{
    t_hysteresis();
    t_duty_limit();
    t_sequence();
    t_pin_sim();
    t_poll_gate();
    t_config();
    t_lux();
    printf("pass=%d fail=%d\n", pass, fail);
    return fail ? 1 : 0;
}
