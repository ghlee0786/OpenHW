#!/bin/sh
# F-005 bring-up 자동 확인 (보드 안에서 실행, busybox sh). 절차서: firmware/docs/bringup-checklist.md
# 소프트웨어로 판정할 수 있는 항목만 본다(전압·파형·열·LED 눈 확인은 절차서의 계측 항목).
# 사용:  sh bringup-check.sh            → 줄마다 PASS/FAIL/SKIP, 종료 코드 = FAIL 개수(최대 125)
#        SECS=60 sh bringup-check.sh    → FPS 표본 시간(초, 기본 30) · SKIP_FPS=1 이면 FPS 생략
#        ROOT=<폴더>                    → /sys·/proc·/etc·/run·/usr 앞에 붙인다(하드웨어 없는 사전 시험용)
# 기대값 근거: 계약 hw-fw-contract.md v1.10 6·7절, F-003 f003-bsp-daynight.md, F-004 f004-person-event.md 9.3절
R="${ROOT:-}"
SECS="${SECS:-30}"
MODEL_SHA=eee83a224e203248e141ad51426cb6c151f1597c9d5e5b893c66c661baea9835
MODEL="$R/usr/share/openhw/models/yolox_nano_person_416_bf16_cv181x.cvimodel"
fails=0

pass() { echo "PASS $1 — $2"; }
fail() { echo "FAIL $1 — $2"; fails=$((fails + 1)); }
skip() { echo "SKIP $1 — $2"; }
has() { command -v "$1" >/dev/null 2>&1; }
rd() { [ -r "$1" ] && tr -d '\0\n' < "$1"; }

# B1 DTS 모델 문자열: S70hardware 가 "Seeed reCamera" 일 때만 CAM_EN=gpio358 을 쓴다(아니면 gpio495 = 우리 ICR IN1)
m=$(rd "$R/proc/device-tree/model")
[ "$m" = "Seeed reCamera" ] && pass B1 "DT model '$m'" || fail B1 "DT model '$m' (S70hardware 가 gpio495 를 CAM_EN 으로 잘못 쓴다)"

# B2 portc GPIO 베이스 416 (계약 14절 실물 2: gpio428 STATUS_LED · gpio431 IR_LED_EN 이 이 추론에 기댄다)
b=""
for c in "$R"/sys/class/gpio/gpiochip*; do
  [ -r "$c/base" ] || continue
  case "$(rd "$c/label")" in *4080000*|*portc*|*gpio@3022000*) b=$(rd "$c/base") ;; esac
done
if [ -n "$b" ]; then [ "$b" = 416 ] && pass B2 "portc base 416" || fail B2 "portc base $b (gpio428/431 다시 계산)"
else
  list=""; for c in "$R"/sys/class/gpio/gpiochip*; do [ -r "$c/base" ] && list="$list $(rd "$c/base"):$(rd "$c/label")"; done
  skip B2 "portc 라벨을 못 찾음 — 목록:$list (절차서 2-5로 눈 대조)"
fi

# C1 CAM_EN(gpio358)=1
v=$(rd "$R/sys/class/gpio/gpio358/value")
[ "$v" = 1 ] && pass C1 "CAM_EN gpio358=1" || fail C1 "CAM_EN gpio358='$v'"

# C2·C3 I2C2 장치 ID (GC2053 0x3f: 0xf0/0xf1 = 0x20/0x53 — SDK gc2053_sensor_ctl.c · LTR-329 0x29: PART_ID 0x86)
if has i2cget && [ -z "$R" ]; then
  h=$(i2cget -y -f 2 0x3f 0xf0 2>/dev/null); l=$(i2cget -y -f 2 0x3f 0xf1 2>/dev/null)
  [ "$h$l" = 0x200x53 ] && pass C2 "GC2053 id $h $l" || fail C2 "GC2053 id '$h' '$l' (기대 0x20 0x53)"
  p=$(i2cget -y -f 2 0x29 0x86 2>/dev/null)
  [ "$p" = 0xa0 ] && pass C3 "LTR-329 PART_ID $p" || fail C3 "LTR-329 PART_ID '$p' (기대 0xa0, 데이터시트 값 — 실물로 확인)"
else skip C2 "i2cget 없음 또는 ROOT 시험"; skip C3 "i2cget 없음 또는 ROOT 시험"; fi

# P1 모델 파일 sha256
if [ -f "$MODEL" ]; then
  s=$(sha256sum "$MODEL" | cut -d' ' -f1)
  [ "$s" = "$MODEL_SHA" ] && pass P1 "cvimodel sha256 일치" || fail P1 "cvimodel sha256 $s"
else fail P1 "모델 없음 $MODEL"; fi

# P2 데몬 (S50mosquitto · S91sscma-node · S96daynight · S97persond)
for d in mosquitto sscma-node daynight persond; do
  found=""
  for c in "$R"/proc/[0-9]*/comm; do [ "$(rd "$c")" = "$d" ] && { found=1; break; }; done
  [ -n "$found" ] && pass P2 "$d 실행 중" || fail P2 "$d 없음"
done

# D1 주야 모드 파일과 IR 핀 상태 (F-003: 밤 = EN 1 · 켬 비율 ≤25%, 낮 = EN 0 · PWM High)
mode=$(rd "$R/run/daynight/mode")
case "$mode" in day|night) pass D1 "/run/daynight/mode=$mode" ;; *) fail D1 "/run/daynight/mode='$mode'" ;; esac
en=$(rd "$R/sys/class/gpio/gpio431/value")
pw="$R/sys/class/pwm/pwmchip0/pwm2"
per=$(rd "$pw/period"); dut=$(rd "$pw/duty_cycle"); ena=$(rd "$pw/enable")
if [ -n "$per" ] && [ -n "$dut" ] && [ "$per" -gt 0 ]; then
  # 켬(Low) 비율 = 1 − duty/period. cvi_pwm 이 duty==period 를 period−1 카운트로 만드는 것은 허용(F-004 4절)
  on_ppm=$(( (per - dut) * 1000000 / per ))
  [ "$on_ppm" -le 250000 ] && pass D2 "IR 켬 비율 ${on_ppm}ppm ≤ 250000 (period ${per}ns, enable=$ena)" || fail D2 "IR 켬 비율 ${on_ppm}ppm > 25% (O-31)"
  hz=$(( 1000000000 / per ))
  [ "$hz" -le 500 ] && pass D3 "IR PWM ${hz}Hz ≤ 500" || fail D3 "IR PWM ${hz}Hz > 500"
else fail D2 "pwmchip0/pwm2 없음 (cv181x_pwm.ko · S96daynight)"; skip D3 "PWM 없음"; fi
case "$mode:$en" in
  night:1) pass D4 "밤 · IR_LED_EN gpio431=1" ;;
  day:0) [ "${dut:-0}" -ge "${per:-1}" ] 2>/dev/null || [ "$(( ${per:-1} - ${dut:-0} ))" -le $(( ${per:-0} / 1000 + 1 )) ] \
           && pass D4 "낮 · IR_LED_EN=0 · PWM High" || fail D4 "낮인데 PWM duty $dut/$per" ;;
  *) fail D4 "mode '$mode' 와 IR_LED_EN '$en' 이 맞지 않음" ;;
esac

# N1 이더넷 링크 (이미지에 ethtool 없음 → sysfs)
c=$(rd "$R/sys/class/net/eth0/carrier"); sp=$(rd "$R/sys/class/net/eth0/speed"); du=$(rd "$R/sys/class/net/eth0/duplex")
[ "$c" = 1 ] && pass N1 "eth0 링크 ${sp}Mb/s $du" || fail N1 "eth0 carrier='$c'"

# N2 네트워크 노출 (D-003 #30): 1883 은 루프백만, rtsp_pass 가 비면 554 를 열지 않는다
listen() { # $1 = 포트 16진수 4자리 → 루프백 아닌 LISTEN 주소 출력
  for t in "$R/proc/net/tcp" "$R/proc/net/tcp6"; do
    [ -r "$t" ] && awk -v p=":$1" 'NR>1 && $4=="0A" && substr($2,length($2)-4)==p {print $2}' "$t"
  done | grep -v -e '^0100007F:' -e '^00000000000000000000000001000000:'
}
o=$(listen 075B)
[ -z "$o" ] && pass N2 "1883 루프백 전용" || fail N2 "1883 이 밖에서 열림: $o"
rp=$(sed -n 's/^rtsp_pass *= *//p' "$R/etc/openhw/persond.conf" 2>/dev/null)
o=$(listen 022A)
if [ -z "$rp" ]; then [ -z "$o" ] && pass N3 "rtsp_pass 빈 값 · 554 닫힘" || fail N3 "rtsp_pass 빈 값인데 554 열림: $o"
else skip N3 "rtsp_pass 설정됨 — 554 열림은 의도"; fi

# F1 추론 FPS·perf (sscma-node invoke: data.count, data.perf [[pre, inf, post] ms])
if [ "${SKIP_FPS:-0}" = 1 ] || [ -n "$R" ] || ! has mosquitto_sub; then skip F1 "FPS 생략"
else
  out=$(timeout "$SECS" mosquitto_sub -h 127.0.0.1 -t sscma/v0/recamera/node/out/openhw_person 2>/dev/null)
  echo "$out" | awk -v s="$SECS" '
    /"name":"invoke"/ { n++; if (match($0, /"perf":\[\[[0-9.]+,[0-9.]+,[0-9.]+\]/)) {
        split(substr($0, RSTART + 9, RLENGTH - 9), a, ","); pre += a[1]; inf += a[2]; post += a[3]; k++ } }
    END { if (n == 0) { print "FAIL F1 — invoke 0건 (모델 노드 미시작 · persond 로그 확인)"; exit 1 }
          printf "PASS F1 — %d건/%ds = %.2f FPS", n, s, n / s
          if (k) printf " · perf 평균 pre %.1f / inf %.1f / post %.1f ms", pre / k, inf / k, post / k
          print " (목표 수치 없음 — 기록만)" }' || fails=$((fails + 1))
fi

echo "결과: FAIL ${fails}건"
[ "$fails" -gt 125 ] && fails=125
exit "$fails"
