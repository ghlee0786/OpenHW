#include "persond_logic.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

void pn_config_default(pn_config *c)
{
    c->min_score = 0.5;
    c->enter_frames = 3;
    c->leave_ms = 5000;
    c->cooldown_ms = 30000;
}

int pn_config_set(pn_config *c, const char *key, const char *val)
{
    char *end;
    double v = strtod(val, &end);
    if (end == val || *end != '\0')
        return -1;
    if (!strcmp(key, "min_score"))         c->min_score = v;
    else if (!strcmp(key, "enter_frames")) c->enter_frames = (int)v;
    else if (!strcmp(key, "leave_ms"))     c->leave_ms = (int)v;
    else if (!strcmp(key, "cooldown_ms"))  c->cooldown_ms = (int)v;
    else return -1;
    return 0;
}

void pn_config_finalize(pn_config *c)
{
    if (!(c->min_score >= 0.05)) c->min_score = 0.05;
    if (c->min_score > 0.99) c->min_score = 0.99;
    if (c->enter_frames < 1) c->enter_frames = 1;
    if (c->leave_ms < 500) c->leave_ms = 500;
    if (c->cooldown_ms < 0) c->cooldown_ms = 0;
}

void pn_init(pn_state *s)
{
    s->present = 0;
    s->hits = 0;
    s->last_seen_ms = 0;
    s->last_enter_ms = -1;
}

pn_event pn_frame(pn_state *s, const pn_config *c, int64_t now_ms, int n_person)
{
    if (n_person <= 0) {
        s->hits = 0;
        return pn_tick(s, c, now_ms);
    }
    s->hits++;
    s->last_seen_ms = now_ms;
    if (s->present || s->hits < c->enter_frames)
        return PN_NONE;
    if (s->last_enter_ms >= 0 && now_ms - s->last_enter_ms < c->cooldown_ms)
        return PN_NONE;   /* 쿨다운 중: 등장으로 치지 않고 다음 프레임에 다시 본다 */
    s->present = 1;
    s->last_enter_ms = now_ms;
    return PN_ENTER;
}

pn_event pn_tick(pn_state *s, const pn_config *c, int64_t now_ms)
{
    if (s->present && now_ms - s->last_seen_ms >= c->leave_ms) {
        s->present = 0;
        s->hits = 0;
        return PN_LEAVE;
    }
    return PN_NONE;
}

int pn_filter(const double (*raw)[6], int n_raw, int res_w, int res_h,
              double min_score, pn_box *out, int max)
{
    int n = 0;
    if (res_w <= 0 || res_h <= 0 || max <= 0)
        return 0;
    for (int i = 0; i < n_raw; i++) {
        double score = raw[i][4] / 100.0;
        if ((int)raw[i][5] != 0 || !(score >= min_score))
            continue;
        pn_box b = { raw[i][0] / res_w, raw[i][1] / res_h, raw[i][2] / res_w, raw[i][3] / res_h, score };
        /* 점수 내림차순 삽입, max 개 유지 */
        int pos = n < max ? n : max;
        while (pos > 0 && out[pos - 1].score < b.score) {
            if (pos < max)
                out[pos] = out[pos - 1];
            pos--;
        }
        if (pos < max) {
            out[pos] = b;
            if (n < max)
                n++;
        }
    }
    return n;
}

int pn_format_event(char *buf, size_t len, pn_event ev, int64_t epoch_ms, const char *mode,
                    const pn_box *boxes, int n, int res_w, int res_h, const char *device)
{
    char ts[64];
    time_t sec = (time_t)(epoch_ms / 1000);
    struct tm tm;
    gmtime_r(&sec, &tm);
    snprintf(ts, sizeof ts, "%04d-%02d-%02dT%02d:%02d:%02d.%03dZ", tm.tm_year + 1900, tm.tm_mon + 1,
             tm.tm_mday, tm.tm_hour, tm.tm_min, tm.tm_sec, (int)(epoch_ms % 1000));
    double best = 0;
    for (int i = 0; i < n; i++)
        if (boxes[i].score > best)
            best = boxes[i].score;
    size_t off = 0;
    int r = snprintf(buf, len,
                     "{\"event\":\"%s\",\"ts\":\"%s\",\"device\":\"%s\",\"mode\":\"%s\",\"score\":%.3f,"
                     "\"count\":%d,\"resolution\":[%d,%d],\"boxes\":[",
                     ev == PN_ENTER ? "person_enter" : "person_leave", ts, device ? device : "",
                     mode ? mode : "unknown", best, n, res_w, res_h);
    if (r < 0 || (size_t)r >= len)
        return -1;
    off = (size_t)r;
    for (int i = 0; i < n; i++) {
        r = snprintf(buf + off, len - off, "%s[%.4f,%.4f,%.4f,%.4f,%.3f]", i ? "," : "",
                     boxes[i].cx, boxes[i].cy, boxes[i].w, boxes[i].h, boxes[i].score);
        if (r < 0 || (size_t)r >= len - off)
            return -1;
        off += (size_t)r;
    }
    r = snprintf(buf + off, len - off, "]}");
    if (r < 0 || (size_t)r >= len - off)
        return -1;
    return (int)(off + (size_t)r);
}
