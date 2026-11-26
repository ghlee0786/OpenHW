#!/usr/bin/env bash
# 호스트 통합 시험 (컨테이너 안에서만, 외부 서버 없음):
#   mosquitto(127.0.0.1) + persond(호스트 빌드) + 가짜 sscma-node(mosquitto_pub) → 이벤트 확인.
# 사용: docker run --rm -v <persond 폴더>:/src:ro recamera-os-builder bash /src/test_integration.sh
set -u
apt-get update -qq >/dev/null 2>&1
apt-get install -y -qq mosquitto mosquitto-clients libmosquitto-dev libjson-c-dev >/dev/null 2>&1
cp -r /src /tmp/p && cd /tmp/p && make -s persond || exit 2

pass=0; fail=0
check() { if eval "$2"; then pass=$((pass+1)); else fail=$((fail+1)); echo "FAIL $1"; fi; }

mosquitto -p 1883 -d
sleep 0.5
mkdir -p /run/daynight && echo night > /run/daynight/mode
cat > /tmp/p.conf <<EOF
client = recamera
device = test-01
enter_frames = 3
leave_ms = 1500
cooldown_ms = 60000
rtsp = 1
rtsp_pass = testpass
EOF
mosquitto_sub -v -t 'sscma/v0/recamera/node/in/#' > /tmp/in.log &
mosquitto_sub -t 'openhw/v1/event' > /tmp/ev.log &
sleep 0.5
./persond /tmp/p.conf 2> /tmp/persond.err &
PD=$!
sleep 1

OUT=sscma/v0/recamera/node/out/openhw_person
frame() { mosquitto_pub -t $OUT -m "{\"type\":1,\"name\":\"invoke\",\"code\":0,\"data\":{\"count\":$1,\"resolution\":[1280,720],\"boxes\":[$2],\"labels\":[\"person\"],\"perf\":[[1,30,2]],\"image\":\"\"}}"; sleep 0.1; }
P='[640,360,100,300,88,0]'
frame 1 "$P"; frame 1 "$P"
sleep 0.3
check "2프레임으로는 이벤트 없음" '[ ! -s /tmp/ev.log ]'
frame 2 "$P,[100,100,40,80,30,0]"
sleep 0.5
check "3프레임 → person_enter 1건" '[ "$(grep -c person_enter /tmp/ev.log)" = 1 ]'
check "모드 night 포함" 'grep -q "\"mode\":\"night\"" /tmp/ev.log'
check "점수 0.3 박스 제외(count 1)" 'grep -q "\"count\":1" /tmp/ev.log'
check "정규화 박스" 'grep -q "\[0.5000,0.5000,0.0781,0.4167,0.880\]" /tmp/ev.log'
check "device·해상도" 'grep -q "\"device\":\"test-01\"" /tmp/ev.log && grep -q "\"resolution\":\[1280,720\]" /tmp/ev.log'
frame 0 ""
sleep 2
check "1.5초 공백 → person_leave (결과 없이도 tick)" '[ "$(grep -c person_leave /tmp/ev.log)" = 1 ]'
for i in 1 2 3 4; do frame 1 "$P"; done
sleep 0.5
check "쿨다운 60초 안 재등장 없음" '[ "$(grep -c person_enter /tmp/ev.log)" = 1 ]'
check "camera 노드 생성 요청" 'grep -aq "node/in/openhw_cam .*\"type\":\"camera\"" /tmp/in.log'
check "camera dependents 에 model·stream" 'grep -a "node/in/openhw_cam " /tmp/in.log | grep -q "\"dependents\":\[ *\"openhw_person\", *\"openhw_rtsp\" *\]"'
check "model 노드: algorithm 3·모델 경로" 'grep -a "node/in/openhw_person " /tmp/in.log | grep -q "\"algorithm\":3" && grep -q "yolox_nano_person_416_int8_cv181x.cvimodel" /tmp/in.log'
check "stream 노드: 554·비밀번호" 'grep -a "node/in/openhw_rtsp " /tmp/in.log | grep -q "\"port\":554" && grep -a "node/in/openhw_rtsp " /tmp/in.log | grep -q testpass'
check "websocket 끔" '! grep -q "\"websocket\":true" /tmp/in.log'
mosquitto_pub -t $OUT -m 'not json'; mosquitto_pub -t $OUT -m '{"name":"invoke","data":{"boxes":[[1,2]],"resolution":[0,0]}}'
sleep 0.3
check "잘못된 메시지에도 살아 있음" 'kill -0 $PD'
kill $PD; sleep 0.3
check "SIGTERM 으로 종료" '! kill -0 $PD 2>/dev/null'

# RTSP 비밀번호가 비면 stream 노드를 만들지 않는다
: > /tmp/in.log
printf 'client = recamera\nrtsp = 1\n' > /tmp/p2.conf
./persond /tmp/p2.conf 2>/dev/null & PD=$!; sleep 1; kill $PD
check "비밀번호 없으면 RTSP 안 켬" '! grep -aq "node/in/openhw_rtsp" /tmp/in.log && grep -a "node/in/openhw_cam " /tmp/in.log | grep -q "\"dependents\":\[ *\"openhw_person\" *\]"'

echo "--- events"; cat /tmp/ev.log
echo "pass=$pass fail=$fail"
[ $fail -eq 0 ]
