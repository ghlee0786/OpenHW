#!/bin/bash
# F-007 호스트 도구 시험 — 하드웨어 없이, 네트워크는 127.0.0.1 만.
# 실행: docker run --rm -v <저장소>/firmware:/fw:ro recamera-os-builder bash /fw/tools/host/test_host_tools.sh
# 가짜 RTSP 서버(GStreamer videotestsrc 15fps) · 로컬 mosquitto(18830) · 가짜 JSONL/CSV 로 각 도구의 종료 코드를 기대값과 맞춘다.
# 종료 코드 = 기대와 다른 시험 수.
set -u
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq ffmpeg mosquitto mosquitto-clients python3-gi gir1.2-gst-rtsp-server-1.0 \
  gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly >/dev/null 2>&1 || echo "apt 일부 실패"
H=/fw/tools/host
W=$(mktemp -d)
cd "$W" || exit 99
miss=0
expect() { # $1 이름 $2 기대 종료 코드, 나머지 = 명령
  name=$1 want=$2; shift 2
  out=$(timeout 120 "$@" 2>&1); rc=$?   # 한 시험이 멈춰도 전체가 멈추지 않게
  if [ "$rc" = "$want" ]; then echo "ok   $name rc=$rc"; else echo "MISS $name rc=$rc 기대 $want"; miss=$((miss + 1)); fi
  echo "$out" | sed 's/^/       /' | head -8
}

# ---------- ① RTSP ----------
cat > srv.py <<'EOF'
import gi
gi.require_version("Gst", "1.0"); gi.require_version("GstRtspServer", "1.0")
from gi.repository import Gst, GstRtspServer, GLib
Gst.init(None)
s = GstRtspServer.RTSPServer(); s.set_address("127.0.0.1"); s.set_service("8554")
f = GstRtspServer.RTSPMediaFactory()
f.set_launch("( videotestsrc is-live=true ! video/x-raw,width=1280,height=720,framerate=15/1 ! x264enc tune=zerolatency speed-preset=ultrafast ! rtph264pay name=pay0 pt=96 )")
f.set_shared(True)
s.get_mount_points().add_factory("/live", f); s.attach(None)
GLib.MainLoop().run()
EOF
python3 srv.py & SRV=$!
sleep 3
U=rtsp://127.0.0.1:8554/live
expect R1-live-15fps 0 python3 $H/rtsp_check.py probe $U --seconds 8 --expect-fps 15
expect R2-live-expect30 1 python3 $H/rtsp_check.py probe $U --seconds 5 --expect-fps 30
expect R3-no-server 2 python3 $H/rtsp_check.py probe rtsp://127.0.0.1:8599/none --seconds 3
expect R4-record 0 python3 $H/rtsp_check.py record $U rec.mkv --seconds 4
expect R5-probe-recording 0 python3 $H/rtsp_check.py probe rec.mkv --seconds 10 --expect-fps 15
expect R6-latency-frame 0 python3 $H/rtsp_check.py latency $U frame.png
kill $SRV 2>/dev/null
ffmpeg -v error -y -f lavfi -i testsrc=size=640x360:rate=5 -t 6 -c:v libx264 slow5.mkv
expect R7-file-5fps 1 python3 $H/rtsp_check.py probe slow5.mkv --expect-fps 15
ffmpeg -v error -y -f lavfi -i testsrc=size=640x360:rate=15 -t 6 -vf "select='not(between(t,2,3))'" -fps_mode vfr -c:v libx264 gap.mkv
expect R8-file-1s-gap 1 python3 $H/rtsp_check.py probe gap.mkv --expect-fps 10

# ---------- ② MQTT 이벤트 ----------
mosquitto -p 18830 -d; sleep 0.5
python3 $H/event_log.py record -o ev.jsonl --port 18830 --seconds 4 & REC=$!
sleep 1
ev() { printf '{"event":"%s","ts":"%s","device":"t","mode":"night","score":%s,"count":1,"resolution":[1280,720],"boxes":[]}' "$1" "$2" "${3:-0.88}"; }
for m in "$(ev person_enter 2026-11-27T01:00:00.000Z)" "$(ev person_leave 2026-11-27T01:00:12.000Z)" \
         "$(ev person_enter 2026-11-27T01:00:45.000Z)" "$(ev person_leave 2026-11-27T01:01:00.500Z)"; do
  mosquitto_pub -h 127.0.0.1 -p 18830 -t openhw/v1/event -q 1 -m "$m"
done
wait $REC
expect E1-recorded-good 0 python3 $H/event_log.py check ev.jsonl
{ echo "openhw/v1/event $(ev person_enter 2026-11-27T02:00:00.000Z)"
  echo "openhw/v1/event $(ev person_enter 2026-11-27T02:00:05.000Z)"          # 등장 중 등장 + 쿨다운
  echo "openhw/v1/event $(ev person_leave 2026-11-27T02:00:20.000Z)"
  echo "openhw/v1/event $(ev person_leave 2026-11-27T02:00:30.000Z)"          # 없는데 퇴장
  echo 'openhw/v1/event {"event":"person_enter","ts":"2026-11-27T02:01:00Z"}' # 필드 누락
} | python3 $H/event_log.py record --stdin -o bad.jsonl >/dev/null
expect E2-faults-4 4 python3 $H/event_log.py check bad.jsonl
: > empty.jsonl
expect E3-empty 2 python3 $H/event_log.py check empty.jsonl
echo "openhw/v1/event $(ev person_enter 2026-11-27T03:00:00.000Z 0.30)" | python3 $H/event_log.py record --stdin -o low.jsonl >/dev/null
expect E4-low-score 1 python3 $H/event_log.py check low.jsonl

# ---------- ③ FPS ----------
python3 - <<'EOF'
import json
with open("inv.jsonl", "w") as f:
    for k in range(900):                       # 60s, 15fps
        if k % 100 == 50: continue               # MQTT 누락 흉내
        f.write(json.dumps({"rx": 1000 + k / 15, "topic": "sscma/v0/recamera/node/out/openhw_person",
                            "msg": {"type": 1, "name": "invoke", "code": 0,
                                    "data": {"count": k + 1, "perf": [[6 + k % 3, 52 + k % 7, 3]]}}}) + "\n")
EOF
expect F1-fps15 0 python3 $H/fps_stats.py inv.jsonl
expect F2-min-fps20 1 python3 $H/fps_stats.py inv.jsonl --min-fps 20
expect F3-empty 2 python3 $H/fps_stats.py empty.jsonl

# ---------- ④ 12V 전류 CSV ----------
python3 - <<'EOF'
import datetime as dt
def w(name, n, f, head="time_s,current_A", iso=False):
    with open(name, "w") as o:
        o.write(head + "\n")
        t0 = dt.datetime(2026, 11, 27, 10, 0, 0)
        for s in range(n):
            t = (t0 + dt.timedelta(seconds=s)).isoformat(sep=" ") if iso else s
            o.write(f"{t},{f(s)}\n")
w("ok.csv", 1900, lambda s: 2.2 if s % 400 == 0 else 1.5)        # 평균 1.5, 순간 2.2 (경고만)
w("over.csv", 1900, lambda s: 1.95)
w("short.csv", 600, lambda s: 1.5)
w("ma.csv", 1900, lambda s: 1500, head="timestamp,current_mA", iso=True)
w("late.csv", 3600, lambda s: 1.5 if s < 1800 else 2.0)        # 전체 1.75 < 1.9, 뒤 30분 창 2.0
EOF
expect C1-ok-peak-warn 0 python3 $H/current_csv.py ok.csv
expect C2-over 1 python3 $H/current_csv.py over.csv
expect C3-short 2 python3 $H/current_csv.py short.csv
expect C4-mA-iso 0 python3 $H/current_csv.py ma.csv
expect C5-window-catches 1 python3 $H/current_csv.py late.csv

echo "호스트 도구 시험: 기대와 다른 시험 ${miss}건"
exit $miss
