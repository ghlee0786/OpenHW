/* 주야 전환 순수 로직 — 하드웨어 접근 없음, 호스트에서 시험한다 (test_logic.c). */
#ifndef DAYNIGHT_LOGIC_H
#define DAYNIGHT_LOGIC_H

#include <stdint.h>

/* 계약 v1.8 7절 · O-31 · V-004b R2 */
#define DN_ON_RATIO_MAX      0.25   /* IR_PWM Low(켬) 비율 상한 — 설정으로 넘을 수 없다 */
#define DN_PWM_FREQ_MAX_HZ   500    /* AL8860 CTRL 끌어내림 PWM 상한 (V-001) */
#define DN_ICR_PULSE_MIN_MS  100
#define DN_ICR_PULSE_MAX_MS  500
#define DN_CAM_SETTLE_MS     5      /* CAM_EN 켠 뒤 첫 I2C 접근까지 최소 대기 */

typedef enum { DN_DAY = 0, DN_NIGHT = 1 } dn_mode;

typedef struct {
    double night_lux;      /* 이 값보다 어두우면 밤 후보 */
    double day_lux;        /* 이 값보다 밝으면 낮 후보 (night_lux 보다 커야 한다) */
    int    samples;        /* 연속 몇 번이면 전환 */
    int    icr_pulse_ms;   /* 100~500 으로 강제 */
    int    icr_night_in1;  /* 밤(필터 빼기) 방향: 1 = IN1 High, 0 = IN2 High — 실물 극성 확인 전 */
    double ir_on_ratio;    /* 요청 켬 비율 — DN_ON_RATIO_MAX 로 강제 */
    int    pwm_freq_hz;    /* DN_PWM_FREQ_MAX_HZ 이하로 강제 */
    int    poll_ms;
    int    isp_mirror_flip;/* sscma-node 가 읽는다 — 데몬은 값만 보존 */
} dn_config;

typedef struct {
    dn_mode mode;
    int     count;         /* 반대 모드 후보가 연속으로 나온 횟수 */
} dn_hyst;

/* 하드웨어 동작 순서 — 실행기는 이 목록을 차례로 수행한다 */
typedef enum {
    DN_ACT_IR_PWM_OFF,     /* IR_PWM 전기 High (켬 비율 0) */
    DN_ACT_IR_EN_ON,       /* IR_LED_EN = 1 */
    DN_ACT_IR_EN_OFF,      /* IR_LED_EN = 0 */
    DN_ACT_IR_PWM_SET,     /* IR_PWM 켬 비율 = 설정값(상한 적용) */
    DN_ACT_ICR_NIGHT,      /* ICR 필터 빼기 펄스 */
    DN_ACT_ICR_DAY,        /* ICR 필터 넣기 펄스 */
    DN_ACT_ISP_NIGHT,      /* /run/daynight/mode = night (sscma-node 가 sdr_ir.bin 로드) */
    DN_ACT_ISP_DAY,
} dn_action;

#define DN_PLAN_MAX 8

void   dn_config_default(dn_config *c);
/* 값 하나를 반영한다. 0 = 성공, -1 = 모르는 키 또는 잘못된 값 */
int    dn_config_set(dn_config *c, const char *key, const char *val);
/* 범위 강제·검증. 0 = 성공, -1 = night_lux >= day_lux 등 쓸 수 없는 설정 */
int    dn_config_finalize(dn_config *c);

void   dn_hyst_init(dn_hyst *h, dn_mode start);
/* 새 조도 값 → 전환이 일어났으면 1 (h->mode 가 새 모드), 아니면 0 */
int    dn_hyst_update(dn_hyst *h, const dn_config *c, double lux);

double dn_clamp_on_ratio(double requested);
/* 리눅스 PWM duty_cycle(전기 High 시간, ns). High = 끔 이므로 duty = period × (1 − 켬 비율) */
uint32_t dn_pwm_period_ns(int freq_hz);
uint32_t dn_pwm_duty_ns(uint32_t period_ns, double on_ratio);

/* 모드 전환 순서. 반환 = 동작 개수 */
int    dn_plan(dn_mode to, dn_action out[DN_PLAN_MAX]);

/* LTR-329 폴링 허용: CAM_EN=1 이고 켠 뒤 DN_CAM_SETTLE_MS 이상 지났을 때만 */
int    dn_may_poll(int cam_en, int64_t ms_since_cam_on);

/* LTR-329 원시값 → lux (Lite-On 앱노트 식, gain·적분시간 보정) */
double dn_ltr329_lux(uint16_t ch0, uint16_t ch1, int gain, int integ_ms);

#endif
