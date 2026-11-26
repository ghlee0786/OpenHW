/* 호스트 시험: make test */
#include "persond_logic.h"

#include <stdio.h>
#include <string.h>

static int pass, fail;
#define CHECK(cond, name) do { if (cond) { pass++; } else { fail++; printf("FAIL %s (%s:%d)\n", name, __FILE__, __LINE__); } } while (0)

static pn_config cfg(void)
{
    pn_config c;
    pn_config_default(&c);
    pn_config_finalize(&c);
    return c;
}

static void t_enter_leave(void)
{
    pn_config c = cfg();          /* enter 3, leave 5000, cooldown 30000 */
    pn_state s; pn_init(&s);
    CHECK(pn_frame(&s, &c, 0, 1) == PN_NONE, "enter: 1프레임은 아님");
    CHECK(pn_frame(&s, &c, 100, 1) == PN_NONE, "enter: 2프레임은 아님");
    CHECK(pn_frame(&s, &c, 200, 1) == PN_ENTER, "enter: 연속 3프레임 → 등장");
    CHECK(pn_frame(&s, &c, 300, 2) == PN_NONE, "enter: 이미 있으면 다시 안 냄");
    CHECK(pn_frame(&s, &c, 4000, 0) == PN_NONE, "leave: 3.7초 공백은 유지");
    CHECK(pn_tick(&s, &c, 5299) == PN_NONE, "leave: 4999ms 는 유지");
    CHECK(pn_tick(&s, &c, 5300) == PN_LEAVE, "leave: 5000ms → 퇴장");
    CHECK(pn_tick(&s, &c, 9000) == PN_NONE, "leave: 퇴장은 한 번만");
}

static void t_flicker(void)
{
    pn_config c = cfg();
    pn_state s; pn_init(&s);
    pn_frame(&s, &c, 0, 1);
    pn_frame(&s, &c, 100, 1);
    CHECK(pn_frame(&s, &c, 200, 0) == PN_NONE, "flicker: 끊기면 다시 센다");
    pn_frame(&s, &c, 300, 1);
    pn_frame(&s, &c, 400, 1);
    CHECK(s.present == 0, "flicker: 2연속은 아직 아님");
    CHECK(pn_frame(&s, &c, 500, 1) == PN_ENTER, "flicker: 다시 3연속이면 등장");
    /* 등장 중 잠깐 0 이 끼어도 퇴장하지 않는다 */
    pn_frame(&s, &c, 600, 0);
    CHECK(pn_frame(&s, &c, 700, 1) == PN_NONE && s.present, "flicker: 등장 중 순간 미검출은 유지");
}

static void t_cooldown(void)
{
    pn_config c = cfg();
    pn_state s; pn_init(&s);
    for (int t = 0; t <= 200; t += 100) pn_frame(&s, &c, t, 1);   /* 등장 @200 */
    pn_tick(&s, &c, 5300);                                          /* 퇴장 */
    int ev = 0;
    for (int t = 6000; t < 30200; t += 100)
        if (pn_frame(&s, &c, t, 1) == PN_ENTER) ev++;
    CHECK(ev == 0, "cooldown: 30초 안에 다시 등장 안 냄");
    CHECK(pn_frame(&s, &c, 30200, 1) == PN_ENTER, "cooldown: 30초 지나면 등장");
    /* 1시간 동안 사람이 드나들어도 등장 이벤트 수 ≤ 3600/30 + 1 */
    pn_init(&s);
    int enters = 0;
    for (int t = 0; t < 3600000; t += 100) {
        int person = (t / 7000) % 2;            /* 7초마다 들어왔다 나감 */
        if (pn_frame(&s, &c, t, person) == PN_ENTER) enters++;
    }
    CHECK(enters <= 3600 / 30 + 1, "cooldown: 1시간 등장 이벤트 상한");
    CHECK(enters >= 100, "cooldown: 쿨다운이 지나면 계속 감지");
}

static void t_filter(void)
{
    const double raw[][6] = {
        {960, 540, 200, 400, 90, 0},   /* person 0.90 */
        {100, 100, 50, 80, 40, 0},     /* person 0.40 → 버림 */
        {500, 500, 100, 100, 95, 2},   /* car → 버림 */
        {1280, 360, 100, 300, 60, 0},  /* person 0.60 */
        {200, 600, 80, 200, 75, 0},    /* person 0.75 */
    };
    pn_box b[PN_MAX_BOXES];
    int n = pn_filter(raw, 5, 1920, 1080, 0.5, b, PN_MAX_BOXES);
    CHECK(n == 3, "filter: person·점수 기준 3개");
    CHECK(b[0].score > 0.89 && b[1].score > 0.74 && b[2].score > 0.59, "filter: 점수 내림차순");
    CHECK(b[0].cx == 0.5 && b[0].cy == 0.5, "filter: 중심 정규화");
    CHECK(pn_filter(raw, 5, 1920, 1080, 0.5, b, 2) == 2 && b[1].score > 0.74, "filter: 최대 개수 제한은 상위만");
    CHECK(pn_filter(raw, 5, 0, 1080, 0.5, b, 4) == 0, "filter: 해상도 0 이면 0개");
}

static void t_format(void)
{
    pn_box b[2] = { {0.5, 0.5, 0.1, 0.4, 0.9}, {0.2, 0.3, 0.05, 0.1, 0.61} };
    char buf[512];
    int r = pn_format_event(buf, sizeof buf, PN_ENTER, 1795700000123LL, "night", b, 2, 1280, 720, "openhw-01");
    CHECK(r > 0 && (size_t)r == strlen(buf), "format: 길이");
    CHECK(strstr(buf, "\"event\":\"person_enter\"") != NULL, "format: 이벤트 종류");
    CHECK(strstr(buf, "\"ts\":\"2026-11-26T") != NULL && strstr(buf, ".123Z\"") != NULL, "format: UTC 시각 ms");
    CHECK(strstr(buf, "\"mode\":\"night\"") != NULL, "format: 주야 모드");
    CHECK(strstr(buf, "\"score\":0.900") != NULL && strstr(buf, "\"count\":2") != NULL, "format: 최고 점수·개수");
    CHECK(strstr(buf, "\"boxes\":[[0.5000,0.5000,0.1000,0.4000,0.900],[0.2000") != NULL, "format: 박스");
    CHECK(pn_format_event(buf, 40, PN_ENTER, 0, "day", b, 2, 1, 1, "x") == -1, "format: 버퍼 부족이면 -1");
    r = pn_format_event(buf, sizeof buf, PN_LEAVE, 0, NULL, NULL, 0, 1280, 720, "d");
    CHECK(r > 0 && strstr(buf, "\"event\":\"person_leave\"") && strstr(buf, "\"mode\":\"unknown\"") && strstr(buf, "\"boxes\":[]}"), "format: 퇴장·모드 없음");
}

static void t_config(void)
{
    pn_config c; pn_config_default(&c);
    CHECK(pn_config_set(&c, "min_score", "0.7") == 0 && c.min_score == 0.7, "conf: min_score");
    CHECK(pn_config_set(&c, "nope", "1") == -1, "conf: 모르는 키");
    CHECK(pn_config_set(&c, "leave_ms", "x") == -1, "conf: 숫자 아님");
    pn_config_set(&c, "min_score", "0"); pn_config_set(&c, "enter_frames", "0"); pn_config_set(&c, "leave_ms", "1");
    pn_config_finalize(&c);
    CHECK(c.min_score >= 0.05 && c.enter_frames == 1 && c.leave_ms == 500, "conf: 하한 강제");
}

int main(void)
{
    t_enter_leave();
    t_flicker();
    t_cooldown();
    t_filter();
    t_format();
    t_config();
    printf("pass=%d fail=%d\n", pass, fail);
    return fail ? 1 : 0;
}
