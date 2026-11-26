#!/usr/bin/env bash
# F-004: apply-f003.sh(모든 reCamera-OS 패치·daynight·sscma 패치) + persond 소스·사람 모델을 패키지 src 로 넣는다.
# 다시 돌려도 된다. 모델은 firmware/models/convert-yolox-person.sh 결과(MODEL_DIR)에서 가져온다.
set -euo pipefail
export MSYS_NO_PATHCONV=1

HERE="$(cd "$(dirname "$0")" && pwd)"
VOL="${VOL:-openhw-recamera-sdk}"
IMAGE="recamera-os-builder"
TARGET="${TARGET:-sg2002_recamera_emmc}"
MODEL_DIR="${MODEL_DIR:-C:/Users/gh/.local/share/openhw-tools/models}"
MODEL=yolox_nano_person_416_bf16_cv181x.cvimodel
if [ "${SKIP_MODEL:-0}" != 1 ] && [ ! -f "$MODEL_DIR/$MODEL" ]; then echo "모델 없음: $MODEL_DIR/$MODEL (convert-yolox-person.sh 먼저, 또는 SKIP_MODEL=1)" >&2; exit 2; fi

bash "$HERE/apply-f003.sh"

FW="$(cd "$HERE/.." && pwd)"
command -v cygpath >/dev/null && FW="$(cygpath -w "$FW")"
docker run --rm -v "$VOL":/work -v "$FW":/fw:ro -v "$(mkdir -p "$MODEL_DIR" && echo "$MODEL_DIR")":/models:ro --workdir /work/src "$IMAGE" bash -c '
  set -e
  id builder >/dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash builder
  D=external/br2-external/openhw-persond/src
  rm -rf "$D" && mkdir -p "$D"
  cp /fw/apps/persond/{Makefile,persond.c,persond_logic.c,persond_logic.h,persond.conf,S97persond} "$D/"
  if [ "'"${SKIP_MODEL:-0}"'" = 1 ]; then echo "모델 넣지 않음 (SKIP_MODEL=1)"; else
    cp /models/'"$MODEL"' "$D/" && sha256sum "$D/'"$MODEL"'"; fi
  chown -R 1000:1000 external/br2-external/openhw-persond
  cd output/'"$TARGET"'/buildroot-2021.05
  O=$(ls -d output/cvitek_*)
  sudo -u builder HOME=/work/home make O=$O openhw-persond-dirclean
  echo "apply-f004 완료"'
