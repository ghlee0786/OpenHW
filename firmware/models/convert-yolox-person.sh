#!/usr/bin/env bash
# F-004: YOLOX-Nano(Apache-2.0) → 사람 감지 cvimodel (cv181x INT8, sscma-node YoloV5 형식).
# 무거운 단계라 hc 칸 + slot 으로 돌린다:
#   node harness/cli.js slot --label F-004-model --timeout-min 240 -- bash firmware/models/convert-yolox-person.sh
# 작업 폴더는 Docker 볼륨 openhw-tpumlir (저장소 밖). 결과: /w/out/*.cvimodel → OUT_DIR 로 복사, sha256 출력.
set -euo pipefail
export MSYS_NO_PATHCONV=1

IMAGE="${TPUC_IMAGE:-sophgo/tpuc_dev:v3.4}"
TPU_MLIR_VER="${TPU_MLIR_VER:-1.28.1}"
VOL="${VOL:-openhw-tpumlir}"
OUT_DIR="${OUT_DIR:-C:/Users/gh/.local/share/openhw-tools/models}"
FW="$(cd "$(dirname "$0")/.." && pwd)"
command -v cygpath >/dev/null && FW="$(cygpath -w "$FW")"
ONNX_URL="https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx"
NAME=yolox_nano_person_416

mkdir -p "$OUT_DIR"
docker volume create "$VOL" >/dev/null
docker run --rm -v "$VOL":/w -v "$FW":/fw:ro -v "$OUT_DIR":/out "$IMAGE" bash -c '
  set -euo pipefail
  cd /w
  python3 -m pip show tpu_mlir 2>/dev/null | grep -q "Version: '"$TPU_MLIR_VER"'" \
    || python3 -m pip install --cache-dir /w/pip "tpu_mlir[onnx]=='"$TPU_MLIR_VER"'"
  [ -f yolox_nano.onnx ] || wget -q -O yolox_nano.onnx "'"$ONNX_URL"'"
  sha256sum yolox_nano.onnx
  if [ ! -d tpu-mlir/regression/dataset/COCO2017 ]; then
    git clone --depth 1 --filter=blob:none --sparse https://github.com/sophgo/tpu-mlir.git
    git -C tpu-mlir sparse-checkout set regression/dataset/COCO2017
  fi
  DS=/w/tpu-mlir/regression/dataset/COCO2017
  echo "calib images: $(ls $DS/*.jpg | wc -l)"
  TEST=$(ls $DS/*.jpg | head -1)
  python3 /fw/models/yolox_to_sscma.py yolox_nano.onnx '"$NAME"'.onnx 416
  mkdir -p work && cd work
  model_transform --model_name '"$NAME"' --model_def ../'"$NAME"'.onnx \
    --input_shapes [[1,3,416,416]] --mean 0,0,0 --scale 1,1,1 --pixel_format bgr --keep_aspect_ratio \
    --test_input $TEST --test_result '"$NAME"'_top.npz --mlir '"$NAME"'.mlir
  run_calibration '"$NAME"'.mlir --dataset $DS --input_num 100 -o '"$NAME"'_cali_table
  # 시험 모의 실행 옵션(--test_input/--test_reference)은 메시지 없이 rc=1(원인 H) → 빼고, 검증은 verify_cvimodel.py 로 따로
  model_deploy --mlir '"$NAME"'.mlir --quantize INT8 --calibration_table '"$NAME"'_cali_table \
    --processor cv181x --quant_input --customization_format RGB_PACKED --fuse_preprocess --aligned_input \
    --model '"$NAME"'_int8_cv181x.cvimodel
  cp '"$NAME"'_int8_cv181x.cvimodel /out/
  cd /out && ls -l '"$NAME"'_int8_cv181x.cvimodel && sha256sum '"$NAME"'_int8_cv181x.cvimodel
'
