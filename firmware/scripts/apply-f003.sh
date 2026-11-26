#!/usr/bin/env bash
# F-003: 기준 빌드 볼륨(reCamera-OS 0.2.4)에 OpenHW 패치와 주야 전환 앱을 넣는다. 다시 돌려도 된다(이미 적용된 패치는 건너뜀).
# 그 뒤 build-baseline.sh build 로 이어 빌드한다.
#   1) firmware/patches/reCamera-OS/*.patch → /work/src (DTS·보드 초기화·br2-external 패키지 openhw-daynight)
#   2) firmware/apps/daynight → external/br2-external/openhw-daynight/src (패키지 소스)
#   3) firmware/patches/sscma-node/*.patch → external/br2-external/sscma-node/ (buildroot 가 패키지 패치로 적용)
#   4) sscma-node · openhw-daynight 를 dirclean 해 패치·소스가 다시 들어가게 한다
set -euo pipefail
export MSYS_NO_PATHCONV=1

VOL="${VOL:-openhw-recamera-sdk}"
IMAGE="recamera-os-builder"
TARGET="${TARGET:-sg2002_recamera_emmc}"
FW="$(cd "$(dirname "$0")/.." && pwd)"
command -v cygpath >/dev/null && FW="$(cygpath -w "$FW")"

docker run --rm -v "$VOL":/work -v "$FW":/fw:ro --workdir /work/src "$IMAGE" bash -c '
  set -e
  id builder >/dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash builder
  # 적용한 패치 이름을 .openhw-applied 에 남긴다(뒤 패치가 같은 파일을 고치면 역적용 시험으로는 판정이 안 된다)
  touch .openhw-applied
  for p in /fw/patches/reCamera-OS/*.patch; do
    n=$(basename "$p")
    if grep -qx "$n" .openhw-applied; then
      echo "이미 적용됨: $n"
    else
      patch -p1 --forward --no-backup-if-mismatch < "$p"
      echo "$n" >> .openhw-applied
    fi
  done
  D=external/br2-external/openhw-daynight/src
  rm -rf "$D" && mkdir -p "$D"
  cp /fw/apps/daynight/{Makefile,daynight.c,daynight_logic.c,daynight_logic.h,daynight.conf,S96daynight} "$D/"
  cp /fw/patches/sscma-node/*.patch external/br2-external/sscma-node/
  chown -R 1000:1000 external/br2-external
  cd output/'"$TARGET"'/buildroot-2021.05
  O=$(ls -d output/cvitek_*)
  sudo -u builder HOME=/work/home make O=$O sscma-node-dirclean openhw-daynight-dirclean
  echo "apply-f003 완료"'
