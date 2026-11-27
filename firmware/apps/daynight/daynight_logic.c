#include "daynight_logic.h"

#include <stdlib.h>
#include <string.h>

void dn_config_default(dn_config *c)
{
    c->night_lux = 5.0;
    c->day_lux = 20.0;
    c->samples = 3;
    c->icr_pulse_ms = 200;
    c->icr_night_in1 = 1;
    c->ir_on_ratio = DN_ON_RATIO_MAX;
    c->pwm_freq_hz = 400;
    c->poll_ms = 1000;
    c->isp_mirror_flip = 1;
}

static int parse_num(const char *s, double *out)
{
    char *end;
    double v = strtod(s, &end);
    if (end == s || *end != '\0')
        return -1;
    *out = v;
    return 0;
}

int dn_config_set(dn_config *c, const char *key, const char *val)
{
    double v;
    if (parse_num(val, &v) != 0)
        return -1;
    if (!strcmp(key, "night_lux"))            c->night_lux = v;
    else if (!strcmp(key, "day_lux"))         c->day_lux = v;
    else if (!strcmp(key, "samples"))         c->samples = (int)v;
    else if (!strcmp(key, "icr_pulse_ms"))    c->icr_pulse_ms = (int)v;
    else if (!strcmp(key, "icr_night_in1"))   c->icr_night_in1 = v != 0;
    else if (!strcmp(key, "ir_on_ratio"))     c->ir_on_ratio = v;
    else if (!strcmp(key, "pwm_freq_hz"))     c->pwm_freq_hz = (int)v;
    else if (!strcmp(key, "poll_ms"))         c->poll_ms = (int)v;
    else if (!strcmp(key, "isp_mirror_flip")) c->isp_mirror_flip = v != 0;
    else return -1;
    return 0;
}

int dn_config_finalize(dn_config *c)
{
    if (c->icr_pulse_ms < DN_ICR_PULSE_MIN_MS) c->icr_pulse_ms = DN_ICR_PULSE_MIN_MS;
    if (c->icr_pulse_ms > DN_ICR_PULSE_MAX_MS) c->icr_pulse_ms = DN_ICR_PULSE_MAX_MS;
    c->ir_on_ratio = dn_clamp_on_ratio(c->ir_on_ratio);
    if (c->pwm_freq_hz < 1) c->pwm_freq_hz = 1;
    if (c->pwm_freq_hz > DN_PWM_FREQ_MAX_HZ) c->pwm_freq_hz = DN_PWM_FREQ_MAX_HZ;
    if (c->samples < 1) c->samples = 1;
    if (c->poll_ms < 100) c->poll_ms = 100;
    if (!(c->night_lux >= 0 && c->night_lux < c->day_lux))
        return -1;
    return 0;
}

void dn_hyst_init(dn_hyst *h, dn_mode start)
{
    h->mode = start;
    h->count = 0;
}

int dn_hyst_update(dn_hyst *h, const dn_config *c, double lux)
{
    int toward_other = (h->mode == DN_DAY) ? (lux < c->night_lux) : (lux > c->day_lux);
    if (!toward_other) {
        h->count = 0;
        return 0;
    }
    if (++h->count < c->samples)
        return 0;
    h->mode = (h->mode == DN_DAY) ? DN_NIGHT : DN_DAY;
    h->count = 0;
    return 1;
}

double dn_clamp_on_ratio(double requested)
{
    if (!(requested > 0))   /* NaN·음수 → 0 */
        return 0;
    return requested > DN_ON_RATIO_MAX ? DN_ON_RATIO_MAX : requested;
}

uint32_t dn_pwm_period_ns(int freq_hz)
{
    if (freq_hz < 1) freq_hz = 1;
    if (freq_hz > DN_PWM_FREQ_MAX_HZ) freq_hz = DN_PWM_FREQ_MAX_HZ;
    return (uint32_t)(1000000000u / (uint32_t)freq_hz);
}

uint32_t dn_pwm_duty_ns(uint32_t period_ns, double on_ratio)
{
    on_ratio = dn_clamp_on_ratio(on_ratio);
    /* 켬(Low) 시간을 내림해 상한을 넘지 않게 한다 */
    uint32_t on_ns = (uint32_t)((double)period_ns * on_ratio);
    return period_ns - on_ns;
}

int dn_plan(dn_mode to, dn_action out[DN_PLAN_MAX])
{
    int n = 0;
    if (to == DN_NIGHT) {
        out[n++] = DN_ACT_ICR_NIGHT;
        out[n++] = DN_ACT_IR_PWM_OFF;   /* IR_LED_EN 전에 반드시 High (O-33) */
        out[n++] = DN_ACT_IR_EN_ON;
        out[n++] = DN_ACT_IR_PWM_SET;
        out[n++] = DN_ACT_ISP_NIGHT;
    } else {
        /* 끌 때는 EN(부하 스위치·eFuse SHDN) 먼저: cvi_pwm 이 duty==period 를 period-1 로 깎아
         * PWM 만으로는 완전한 High(끔)가 안 된다(F-003 미확인 2). EN 을 끊어야 확실히 꺼진다. */
        out[n++] = DN_ACT_IR_EN_OFF;
        out[n++] = DN_ACT_IR_PWM_OFF;
        out[n++] = DN_ACT_ICR_DAY;
        out[n++] = DN_ACT_ISP_DAY;
    }
    return n;
}

int dn_may_poll(int cam_en, int64_t ms_since_cam_on)
{
    return cam_en == 1 && ms_since_cam_on >= DN_CAM_SETTLE_MS;
}

double dn_ltr329_lux(uint16_t ch0, uint16_t ch1, int gain, int integ_ms)
{
    double sum = (double)ch0 + (double)ch1;
    double lux;
    if (sum <= 0 || gain <= 0 || integ_ms <= 0)
        return 0;
    double ratio = (double)ch1 / sum;
    if (ratio < 0.45)
        lux = 1.7743 * ch0 + 1.1059 * ch1;
    else if (ratio < 0.64)
        lux = 4.2785 * ch0 - 1.9548 * ch1;
    else if (ratio < 0.85)
        lux = 0.5926 * ch0 + 0.1185 * ch1;
    else
        return 0;
    return lux / gain / (integ_ms / 100.0);
}
