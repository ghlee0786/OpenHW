#!/bin/bash
# bringup-check.sh 사전 시험: 가짜 ROOT 트리 3개(낮 정상 · 밤 정상 · 고장)로 PASS/FAIL 판정과 종료 코드 확인
# 실행: docker run --rm -v <저장소>/firmware:/fw:ro -v <모델 폴더>:/models:ro recamera-os-builder bash /fw/scripts/test-bringup-check.sh
#   <모델 폴더> = C:/Users/gh/.local/share/openhw-tools/models (BF16 cvimodel, P1 sha256 시험용)
set -u
command -v busybox >/dev/null || { apt-get update -qq >/dev/null 2>&1; apt-get install -y -qq busybox shellcheck >/dev/null 2>&1; }
SCR=/fw/scripts/bringup-check.sh
mk() { # $1 root $2 mode $3 en $4 duty $5 1883addr
  r=$1; mkdir -p $r/proc/device-tree $r/sys/class/gpio/gpiochip416 $r/sys/class/gpio/gpiochip480 $r/sys/class/gpio/gpio358 $r/sys/class/gpio/gpio431 \
    $r/sys/class/pwm/pwmchip0/pwm2 $r/sys/class/net/eth0 $r/proc/net $r/run/daynight $r/etc/openhw $r/usr/share/openhw/models
  printf 'Seeed reCamera\0' > $r/proc/device-tree/model
  echo 416 > $r/sys/class/gpio/gpiochip416/base; echo 4080000.gpio > $r/sys/class/gpio/gpiochip416/label
  echo 480 > $r/sys/class/gpio/gpiochip480/base; echo 3020000.gpio > $r/sys/class/gpio/gpiochip480/label
  echo 1 > $r/sys/class/gpio/gpio358/value; echo $3 > $r/sys/class/gpio/gpio431/value; echo $2 > $r/run/daynight/mode
  echo 2500000 > $r/sys/class/pwm/pwmchip0/pwm2/period; echo $4 > $r/sys/class/pwm/pwmchip0/pwm2/duty_cycle; echo 1 > $r/sys/class/pwm/pwmchip0/pwm2/enable
  echo 1 > $r/sys/class/net/eth0/carrier; echo 100 > $r/sys/class/net/eth0/speed; echo full > $r/sys/class/net/eth0/duplex
  printf '  sl  local_address rem_address   st\n   0: %s:075B 00000000:0000 0A\n   1: 00000000:0016 00000000:0000 0A\n' $5 > $r/proc/net/tcp
  printf 'rtsp = 1\nrtsp_pass =\n' > $r/etc/openhw/persond.conf
  cp /models/yolox_nano_person_416_bf16_cv181x.cvimodel $r/usr/share/openhw/models/
  i=100; for d in mosquitto sscma-node daynight persond; do mkdir -p $r/proc/$i; echo $d > $r/proc/$i/comm; i=$((i+1)); done
}
mk /t/day day 0 2499999 0100007F
mk /t/night night 1 1875000 0100007F
mk /t/bad night 1 1250000 00000000
rm /t/bad/proc/103/comm; printf 'X\0' > /t/bad/proc/device-tree/model
for sh in "busybox sh" dash bash; do $sh -n $SCR && echo "syntax($sh) rc=0" || echo "syntax($sh) rc=$?"; done
if command -v shellcheck >/dev/null; then shellcheck -s sh -S warning $SCR; echo "shellcheck rc=$?"; else echo "shellcheck 없음"; fi
bad=0
for t in day:0 night:0 bad:4; do
  n=${t%%:*}; want=${t#*:}; echo "== $n"; ROOT=/t/$n busybox sh $SCR; rc=$?; echo "rc($n)=$rc 기대 $want"
  [ "$rc" = "$want" ] || bad=$((bad + 1))
done
echo "사전 시험 불일치 ${bad}건"; exit $bad
