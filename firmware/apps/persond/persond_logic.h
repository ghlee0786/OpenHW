/* 사람 감지 이벤트 순수 로직 — 하드웨어·MQTT 없음, 호스트에서 시험한다 (test_logic.c). */
#ifndef PERSOND_LOGIC_H
#define PERSOND_LOGIC_H

#include <stddef.h>
#include <stdint.h>

#define PN_MAX_BOXES 16

typedef struct {
    double cx, cy, w, h;   /* 0~1 정규화, 박스 중심 */
    double score;          /* 0~1 */
} pn_box;

typedef struct {
    double min_score;      /* 이 점수 미만 박스는 버린다 */
    int    enter_frames;   /* 연속 N 프레임에 사람이 있으면 등장 */
    int    leave_ms;       /* 마지막으로 본 뒤 이만큼 없으면 퇴장 */
    int    cooldown_ms;    /* 등장 이벤트 사이 최소 간격 */
} pn_config;

typedef enum { PN_NONE = 0, PN_ENTER = 1, PN_LEAVE = 2 } pn_event;

typedef struct {
    int     present;
    int     hits;
    int64_t last_seen_ms;
    int64_t last_enter_ms; /* -1 = 아직 없음 */
} pn_state;

void     pn_config_default(pn_config *c);
int      pn_config_set(pn_config *c, const char *key, const char *val);  /* 0 성공, -1 모르는 키·잘못된 값 */
void     pn_config_finalize(pn_config *c);

void     pn_init(pn_state *s);
/* 한 프레임의 (이미 걸러진) 사람 박스 수로 상태를 갱신한다 */
pn_event pn_frame(pn_state *s, const pn_config *c, int64_t now_ms, int n_person);
/* 프레임이 오지 않을 때도 퇴장을 판정하려고 주기적으로 부른다 */
pn_event pn_tick(pn_state *s, const pn_config *c, int64_t now_ms);

/* sscma-node model 노드 박스 [x,y,w,h,score(0~100),target] (픽셀, 중심) → 사람 박스 (정규화).
 * target==0(person) 이고 score ≥ min_score 인 것만, 점수 높은 순으로 최대 max 개. 반환 = 개수 */
int      pn_filter(const double (*raw)[6], int n_raw, int res_w, int res_h,
                   double min_score, pn_box *out, int max);

/* 이벤트 JSON. 반환 = 쓴 길이(잘리면 -1) */
int      pn_format_event(char *buf, size_t len, pn_event ev, int64_t epoch_ms, const char *mode,
                         const pn_box *boxes, int n, int res_w, int res_h, const char *device);

#endif
