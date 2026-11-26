/* openhw-persond: sscma-node(카메라·NPU)를 MQTT 로 구성하고, 사람 감지 결과를 받아 이벤트 JSON 을 낸다.
 * - 카메라는 sscma-node 가 연다(이 데몬은 프레임을 직접 만지지 않는다).
 * - 노드: camera(openhw_cam) · model(openhw_person, YOLOX-Nano 사람 cvimodel) · stream(openhw_rtsp, RTSP 554).
 * - 결과: sscma/v0/<client>/node/out/openhw_person 의 "invoke" → 걸러서 등장/퇴장 판정 → event_topic 으로 발행.
 * - 주야 모드: /run/daynight/mode (openhw-daynight) 를 이벤트에 넣는다. */
#include "persond_logic.h"

#include <json-c/json.h>
#include <mosquitto.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define NODE_CAM    "openhw_cam"
#define NODE_MODEL  "openhw_person"
#define NODE_STREAM "openhw_rtsp"

static struct {
    char host[64];
    int  port;
    char client[32];            /* sscma-node client id (/etc/sscma.conf 없으면 recamera) */
    char event_host[64];        /* 이벤트 브로커 (기본 = 같은 로컬 브로커) */
    int  event_port;
    char event_topic[128];
    char device[64];
    char model[160];
    int  cam_option;            /* 0=1080p 1=720p 2=360p(640x480) */
    int  cam_fps;
    int  rtsp;                  /* 1 = stream 노드 생성 */
    int  rtsp_port;
    char rtsp_user[32];
    char rtsp_pass[64];
} g = {
    "localhost", 1883, "recamera", "localhost", 1883, "openhw/v1/event", "", "/usr/share/openhw/models/yolox_nano_person_416_bf16_cv181x.cvimodel",
    1, 15, 1, 554, "admin", "",
};

static pn_config g_pn;
static pn_state g_st;
static pn_box g_last[PN_MAX_BOXES];
static int g_last_n, g_res_w, g_res_h;
static struct mosquitto *g_mq, *g_ev;
static volatile sig_atomic_t g_stop;
static char g_out_topic[160];

static int64_t mono_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static int64_t epoch_ms(void)
{
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (int64_t)ts.tv_sec * 1000 + ts.tv_nsec / 1000000;
}

static void read_mode(char *buf, size_t len)
{
    snprintf(buf, len, "unknown");
    FILE *f = fopen("/run/daynight/mode", "r");
    if (!f)
        return;
    char t[16];
    if (fgets(t, sizeof t, f) && (!strncmp(t, "day", 3) || !strncmp(t, "night", 5)))
        snprintf(buf, len, "%s", t[0] == 'd' ? "day" : "night");
    fclose(f);
}

static void emit(pn_event ev)
{
    char mode[16], buf[2048];
    read_mode(mode, sizeof mode);
    int n = ev == PN_ENTER ? g_last_n : 0;
    int r = pn_format_event(buf, sizeof buf, ev, epoch_ms(), mode, g_last, n, g_res_w, g_res_h, g.device);
    if (r < 0)
        return;
    int rc = mosquitto_publish(g_ev, NULL, g.event_topic, r, buf, 1, false);
    fprintf(stderr, "persond: %s (%s)\n", buf, rc == MOSQ_ERR_SUCCESS ? "sent" : mosquitto_strerror(rc));
}

static void request(const char *node, json_object *body)
{
    char topic[160];
    snprintf(topic, sizeof topic, "sscma/v0/%s/node/in/%s", g.client, node);
    const char *s = json_object_to_json_string_ext(body, JSON_C_TO_STRING_PLAIN);
    mosquitto_publish(g_mq, NULL, topic, (int)strlen(s), s, 0, false);
    json_object_put(body);
}

static json_object *create_msg(const char *type, json_object *config, const char *dep_key, const char **deps, int ndeps)
{
    json_object *data = json_object_new_object(), *arr = json_object_new_array(), *m = json_object_new_object();
    json_object_object_add(data, "type", json_object_new_string(type));
    json_object_object_add(data, "config", config);
    for (int i = 0; i < ndeps; i++)
        json_object_array_add(arr, json_object_new_string(deps[i]));
    json_object_object_add(data, dep_key, arr);
    json_object_object_add(m, "name", json_object_new_string("create"));
    json_object_object_add(m, "type", json_object_new_int(3));
    json_object_object_add(m, "data", data);
    return m;
}

/* 노드 만들기 순서: camera(dependents) → model → stream. sscma-node 는 의존이 다 갖춰지면 스스로 시작한다 */
static void create_nodes(void)
{
    json_object *c = json_object_new_object();
    json_object_object_add(c, "option", json_object_new_int(g.cam_option));
    json_object_object_add(c, "fps", json_object_new_int(g.cam_fps));
    json_object_object_add(c, "audio", json_object_new_boolean(0));
    json_object_object_add(c, "preview", json_object_new_boolean(0));
    json_object_object_add(c, "websocket", json_object_new_boolean(0));
    const char *dependents[2] = { NODE_MODEL, NODE_STREAM };
    request(NODE_CAM, create_msg("camera", c, "dependents", dependents, g.rtsp ? 2 : 1));

    json_object *m = json_object_new_object();
    json_object_object_add(m, "uri", json_object_new_string(g.model));
    json_object_object_add(m, "algorithm", json_object_new_int(3));   /* MA_MODEL_TYPE_YOLOV5 형식으로 변환한 모델 */
    json_object_object_add(m, "tscore", json_object_new_double(g_pn.min_score));
    json_object_object_add(m, "tiou", json_object_new_double(0.45));
    json_object_object_add(m, "debug", json_object_new_boolean(0));
    json_object_object_add(m, "websocket", json_object_new_boolean(0));
    json_object *labels = json_object_new_array();
    json_object_array_add(labels, json_object_new_string("person"));
    json_object_object_add(m, "labels", labels);
    const char *cam[1] = { NODE_CAM };
    request(NODE_MODEL, create_msg("model", m, "dependencies", cam, 1));

    if (g.rtsp) {
        json_object *s = json_object_new_object();
        json_object_object_add(s, "port", json_object_new_int(g.rtsp_port));
        json_object_object_add(s, "session", json_object_new_string("live"));
        json_object_object_add(s, "username", json_object_new_string(g.rtsp_user));
        json_object_object_add(s, "password", json_object_new_string(g.rtsp_pass));
        request(NODE_STREAM, create_msg("stream", s, "dependencies", cam, 1));
    }
}

static void on_connect(struct mosquitto *mq, void *ud, int rc)
{
    (void)ud;
    if (rc != 0)
        return;
    mosquitto_subscribe(mq, NULL, g_out_topic, 0);
    create_nodes();
}

static void on_message(struct mosquitto *mq, void *ud, const struct mosquitto_message *msg)
{
    (void)mq; (void)ud;
    json_object *root = json_tokener_parse((const char *)msg->payload), *name, *data, *boxes, *res;
    if (!root)
        return;
    if (json_object_object_get_ex(root, "name", &name) && json_object_object_get_ex(root, "data", &data)) {
        const char *nm = json_object_get_string(name);
        if (!strcmp(nm, "invoke") && json_object_object_get_ex(data, "boxes", &boxes) &&
            json_object_object_get_ex(data, "resolution", &res) && json_object_array_length(res) == 2) {
            double raw[64][6];
            int nraw = 0;
            for (size_t i = 0; i < json_object_array_length(boxes) && nraw < 64; i++) {
                json_object *b = json_object_array_get_idx(boxes, i);
                if (json_object_array_length(b) < 6)
                    continue;
                for (int k = 0; k < 6; k++)
                    raw[nraw][k] = json_object_get_double(json_object_array_get_idx(b, k));
                nraw++;
            }
            g_res_w = json_object_get_int(json_object_array_get_idx(res, 0));
            g_res_h = json_object_get_int(json_object_array_get_idx(res, 1));
            int n = pn_filter((const double (*)[6])raw, nraw, g_res_w, g_res_h, g_pn.min_score, g_last, PN_MAX_BOXES);
            if (n > 0)
                g_last_n = n;
            pn_event ev = pn_frame(&g_st, &g_pn, mono_ms(), n);
            if (ev != PN_NONE)
                emit(ev);
        } else if (strcmp(nm, "invoke")) {
            fprintf(stderr, "persond: sscma %s\n", (const char *)msg->payload);   /* create 응답·오류 */
        }
    }
    json_object_put(root);
}

static void load_config(const char *path)
{
    pn_config_default(&g_pn);
    FILE *f = fopen(path, "r");
    if (f) {
        char line[256], k[64], v[160];
        while (fgets(line, sizeof line, f)) {
            if (line[0] == '#' || sscanf(line, " %63[^= ] = %159s", k, v) != 2)
                continue;
#define S(key, dst) else if (!strcmp(k, key)) snprintf(dst, sizeof dst, "%.*s", (int)sizeof dst - 1, v)
#define I(key, dst) else if (!strcmp(k, key)) dst = atoi(v)
            if (0) {}
            S("host", g.host); I("port", g.port); S("client", g.client);
            S("event_host", g.event_host); I("event_port", g.event_port); S("event_topic", g.event_topic);
            S("device", g.device); S("model", g.model); I("cam_option", g.cam_option); I("cam_fps", g.cam_fps);
            I("rtsp", g.rtsp); I("rtsp_port", g.rtsp_port); S("rtsp_user", g.rtsp_user); S("rtsp_pass", g.rtsp_pass);
            else if (pn_config_set(&g_pn, k, v) != 0)
                fprintf(stderr, "persond: 설정 무시 %s=%s\n", k, v);
#undef S
#undef I
        }
        fclose(f);
    }
    pn_config_finalize(&g_pn);
    if (!g.device[0])
        gethostname(g.device, sizeof g.device - 1);
    if (g.rtsp && !g.rtsp_pass[0]) {
        fprintf(stderr, "persond: rtsp_pass 가 비어 있어 RTSP 를 켜지 않는다\n");
        g.rtsp = 0;
    }
}

static void on_signal(int s) { (void)s; g_stop = 1; }

int main(int argc, char **argv)
{
    load_config(argc > 1 ? argv[1] : "/etc/openhw/persond.conf");
    signal(SIGTERM, on_signal);
    signal(SIGINT, on_signal);
    snprintf(g_out_topic, sizeof g_out_topic, "sscma/v0/%s/node/out/%s", g.client, NODE_MODEL);

    mosquitto_lib_init();
    g_mq = mosquitto_new("openhw-persond", true, NULL);
    mosquitto_connect_callback_set(g_mq, on_connect);
    mosquitto_message_callback_set(g_mq, on_message);
    mosquitto_reconnect_delay_set(g_mq, 1, 10, false);
    int same = !strcmp(g.event_host, g.host) && g.event_port == g.port;
    g_ev = same ? g_mq : mosquitto_new("openhw-persond-ev", true, NULL);
    if (mosquitto_connect(g_mq, g.host, g.port, 30) != MOSQ_ERR_SUCCESS)
        fprintf(stderr, "persond: %s:%d 접속 실패, 다시 시도한다\n", g.host, g.port);
    if (!same) {
        mosquitto_reconnect_delay_set(g_ev, 1, 30, true);
        mosquitto_connect_async(g_ev, g.event_host, g.event_port, 30);
        mosquitto_loop_start(g_ev);
    }
    pn_init(&g_st);
    while (!g_stop) {
        if (mosquitto_loop(g_mq, 200, 1) != MOSQ_ERR_SUCCESS) {
            sleep(1);
            mosquitto_reconnect(g_mq);
        }
        pn_event ev = pn_tick(&g_st, &g_pn, mono_ms());   /* 결과가 끊겨도 퇴장 판정 */
        if (ev != PN_NONE)
            emit(ev);
    }
    if (!same) {
        mosquitto_disconnect(g_ev);
        mosquitto_loop_stop(g_ev, false);
        mosquitto_destroy(g_ev);
    }
    mosquitto_disconnect(g_mq);
    mosquitto_destroy(g_mq);
    mosquitto_lib_cleanup();
    return 0;
}
