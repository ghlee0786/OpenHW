#!/usr/bin/env python3
"""변환한 cvimodel(INT8, 전처리 융합)을 tpu-mlir 호스트 모의 실행으로 돌려 원본 float ONNX 와 비교한다.
보드 없이 할 수 있는 검증: 같은 이미지에서 사람 점수·박스가 얼마나 맞는지. 실물 정확도·FPS 는 아니다.
사용(tpuc_dev 컨테이너 안): verify_cvimodel.py <sscma.onnx> <cvimodel> <이미지 폴더> [개수=20]
종료 코드 0 = 기준 통과 (점수 최대값 차 평균 ≤0.10, 사람 판정(≥0.5) 일치율 ≥90%, 최고 박스 IoU 평균 ≥0.7)
"""
import glob
import sys

import cv2
import numpy as np
import onnxruntime as ort
from tools.model_runner import model_inference


def letterbox(img, size=416):
    h, w = img.shape[:2]
    r = min(size / h, size / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    out = np.zeros((size, size, 3), np.uint8)          # tpu-mlir 전처리와 같게: 가운데 정렬, 0 채움
    top, left = (size - nh) // 2, (size - nw) // 2
    out[top:top + nh, left:left + nw] = cv2.resize(img, (nw, nh))
    return out


def iou(a, b):
    ax1, ay1, ax2, ay2 = a[0] - a[2] / 2, a[1] - a[3] / 2, a[0] + a[2] / 2, a[1] + a[3] / 2
    bx1, by1, bx2, by2 = b[0] - b[2] / 2, b[1] - b[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2
    iw, ih = max(0, min(ax2, bx2) - max(ax1, bx1)), max(0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    u = a[2] * a[3] + b[2] * b[3] - inter
    return inter / u if u > 0 else 0.0


def main(onnx_path, cvimodel, folder, count=20):
    sess = ort.InferenceSession(onnx_path)
    name = sess.get_inputs()[0].name
    files = sorted(glob.glob(folder + "/*.jpg"))[:count]
    dscore, agree, ious = [], 0, []
    for f in files:
        bgr = letterbox(cv2.imread(f))
        ref = sess.run(None, {name: bgr.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)[None]            # RGB_PACKED uint8 NHWC
        outs = model_inference({"images_raw": rgb}, cvimodel)   # cvimodel 입력 이름 (model_tool --info)
        got = np.array(list(outs.values())[-1], np.float32).reshape(ref.shape)
        rk, gk = int(ref[:, 4].argmax()), int(got[:, 4].argmax())
        rs, gs = float(ref[rk, 4]), float(got[gk, 4])
        dscore.append(abs(rs - gs))
        agree += (rs >= 0.5) == (gs >= 0.5)
        if rs >= 0.5 and gs >= 0.5:
            ious.append(iou(ref[rk, :4], got[gk, :4]))
        print(f"{f.split('/')[-1]}: onnx={rs:.3f} cvimodel={gs:.3f}")
    md, ar = float(np.mean(dscore)), agree / len(files)
    mi = float(np.mean(ious)) if ious else 1.0
    print(f"images={len(files)} mean|dscore|={md:.4f} agree={ar:.2%} mean_iou={mi:.3f} (iou n={len(ious)})")
    ok = md <= 0.10 and ar >= 0.9 and mi >= 0.7
    print("VERIFY", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]) if len(sys.argv) > 4 else 20))
