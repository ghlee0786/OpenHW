#!/usr/bin/env python3
"""변환한 cvimodel(INT8, 전처리 융합)을 tpu-mlir 호스트 모의 실행으로 돌려 원본 float ONNX 와 비교한다.
보드 없이 할 수 있는 검증: 같은 이미지에서 사람 점수·박스·검출 수가 얼마나 맞는지. 실물 정확도·FPS 는 아니다.
사용(tpuc_dev 컨테이너 안): verify_cvimodel.py <sscma.onnx> <cvimodel> <이미지 폴더> <개수> <사람 없는 이미지>
기준(문서 f004-person-event.md 8.1, 결과 전에 정함): 21장 = 폴더 이름순 앞 <개수>장 + 사람 없는 1장
  K1 사람 판정(최고 점수 ≥0.5) 일치 ≥90%   K2 사람 이미지 최고 점수 차 평균 ≤0.10·각 ≤0.20
  K3 ONNX 검출별 최대 IoU 평균 ≥0.80   K4 검출 수 같은 이미지 ≥90%·차이 ≤1   K5 사람 없는 이미지 검출 0
  검출 = score ≥0.5, NMS IoU 0.45.  종료 코드 0 = 합격
"""
import glob
import math
import sys

import cv2
import numpy as np
import onnxruntime as ort
from tools.model_runner import model_inference

TH, NMS = 0.5, 0.45


def letterbox(img, size=416):
    h, w = img.shape[:2]
    r = min(size / h, size / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    out = np.zeros((size, size, 3), np.uint8)          # tpu-mlir 전처리와 같게: 가운데 정렬, 0 채움
    top, left = (size - nh) // 2, (size - nw) // 2
    out[top:top + nh, left:left + nw] = cv2.resize(img, (nw, nh))
    return out


def aligned_rgb(bgr, align=64):
    """--aligned_input cvimodel 입력 [1,1,H,ceil(W*3/64)*64] uint8: 행마다 RGB_PACKED 뒤 0 패딩.
    [1,H,W,3] 을 그대로 주면 모의 실행기가 평탄화해 받아 둘째 행부터 픽셀이 밀린다(원인 L, F-004c)."""
    h, w = bgr.shape[:2]
    stride = (w * 3 + align - 1) // align * align
    out = np.zeros((1, 1, h, stride), np.uint8)
    out[0, 0, :, :w * 3] = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).reshape(h, w * 3)
    return out


def iou(a, b):
    ax1, ay1, ax2, ay2 = a[0] - a[2] / 2, a[1] - a[3] / 2, a[0] + a[2] / 2, a[1] + a[3] / 2
    bx1, by1, bx2, by2 = b[0] - b[2] / 2, b[1] - b[3] / 2, b[0] + b[2] / 2, b[1] + b[3] / 2
    iw, ih = max(0, min(ax2, bx2) - max(ax1, bx1)), max(0, min(ay2, by2) - max(ay1, by1))
    inter = iw * ih
    u = a[2] * a[3] + b[2] * b[3] - inter
    return inter / u if u > 0 else 0.0


def detect(rec):
    keep = []
    for i in np.argsort(-rec[:, 4]):
        if rec[i, 4] < TH:
            break
        if all(iou(rec[i, :4], rec[k, :4]) <= NMS for k in keep):
            keep.append(i)
    return [rec[i] for i in keep]


def main(onnx_path, cvimodel, folder, count, negative):
    sess = ort.InferenceSession(onnx_path)
    name = sess.get_inputs()[0].name
    files = sorted(glob.glob(folder + "/*.jpg"))[:count] + [negative]
    agree, same_n, n_diff_max, dscore, ious, neg_n = 0, 0, 0, [], [], None
    for f in files:
        bgr = letterbox(cv2.imread(f))
        ref = sess.run(None, {name: bgr.transpose(2, 0, 1)[None].astype(np.float32)})[0][0]
        outs = model_inference({"images_raw": aligned_rgb(bgr)}, cvimodel)   # 입력 이름 (model_tool --info)
        got = np.array(list(outs.values())[-1], np.float32).reshape(ref.shape)
        rs, gs = float(ref[:, 4].max()), float(got[:, 4].max())
        rd, gd = detect(ref), detect(got)
        agree += (rs >= TH) == (gs >= TH)
        if rs >= TH:
            dscore.append(abs(rs - gs))
        for d in rd:
            ious.append(max((iou(d[:4], g[:4]) for g in gd), default=0.0))
        same_n += len(rd) == len(gd)
        n_diff_max = max(n_diff_max, abs(len(rd) - len(gd)))
        if f == negative:
            neg_n = len(gd)
        print(f"{f.split('/')[-1]}: top onnx={rs:.3f} cvimodel={gs:.3f}  det onnx={len(rd)} cvimodel={len(gd)}")
    n = len(files)
    k = {
        "K1 agree": (agree / n, agree >= math.ceil(0.9 * n)),
        "K2 mean|dscore|": (float(np.mean(dscore)) if dscore else 0.0,
                            (not dscore) or (np.mean(dscore) <= 0.10 and max(dscore) <= 0.20)),
        "K2 max|dscore|": (max(dscore) if dscore else 0.0, True),
        "K3 mean_iou": (float(np.mean(ious)) if ious else 1.0, (not ious) or np.mean(ious) >= 0.80),
        "K4 same_count": (same_n / n, same_n >= math.ceil(0.9 * n) and n_diff_max <= 1),
        "K4 max_count_diff": (n_diff_max, True),
        "K5 negative_dets": (neg_n, neg_n == 0),
    }
    for key, (v, ok) in k.items():
        print(f"{key} = {v:.4f}  {'ok' if ok else 'FAIL'}" if isinstance(v, float) else f"{key} = {v}  {'ok' if ok else 'FAIL'}")
    print(f"images={n} person_images={len(dscore)} onnx_dets={len(ious)}")
    ok = all(v[1] for v in k.values())
    print("VERIFY", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]))
