#!/usr/bin/env python3
"""F-004c K-1 층별 비교: float top MLIR · INT8 tpu MLIR · cvimodel(층 묶음 끔) 의 모든 텐서를 top 순서대로 비교한다.
진단용(변환 시도 아님). 사용(tpuc_dev, PYTHONPATH=$TP/python:$TP, cd <진단 폴더>):
  layer_compare.py <top.mlir> <tpu.mlir> <cvimodel> [이미지]
출력: 층마다 cos(top,tpu) cos(top,cvi) · 최대값, 그리고 obj 경로(top.Sigmoid 1채널 입력 쪽)에서 처음 cos<0.9 인 층.
"""
import sys

import cv2
import numpy as np
from tools.model_runner import mlir_inference, model_inference
from utils.mlir_parser import MlirParser
from verify_cvimodel import aligned_rgb

TOP, TPU, CVI = sys.argv[1:4]
IMG = sys.argv[4] if len(sys.argv) > 4 else "/w/tpu-mlir/regression/dataset/COCO2017/000000085329.jpg"


def letterbox(img, size=416):
    h, w = img.shape[:2]
    r = min(size / h, size / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    out = np.zeros((size, size, 3), np.uint8)
    top, left = (size - nh) // 2, (size - nw) // 2
    out[top:top + nh, left:left + nw] = cv2.resize(img, (nw, nh))
    return out


def cos(a, b):
    a, b = np.asarray(a, np.float64).ravel(), np.asarray(b, np.float64).ravel()
    if a.size != b.size:
        return float("nan")
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


def feed(parser, bgr):
    i = parser.inputs[0]
    if i.shape[1] == 3:                        # top: NCHW BGR float
        return {i.name: bgr.transpose(2, 0, 1)[None].astype(np.float32)}
    x = aligned_rgb(bgr)                       # 전처리 융합 + 행 정렬 입력
    assert list(x.shape) == list(i.shape), (x.shape, i.shape)
    return {i.name: x.astype(np.float32)}


bgr = letterbox(cv2.imread(IMG))
tp, qp = MlirParser(TOP), MlirParser(TPU)
top = mlir_inference(feed(tp, bgr), TOP, dump_all=True)
tpu = mlir_inference(feed(qp, bgr), TPU, dump_all=True)
cvi = model_inference({"images_raw": aligned_rgb(bgr)}, CVI, dump_all=True)


def pick(d, k):
    if k in d:
        return d[k]
    for s in ("_f32", "_si8", "_i8", "_bf16"):
        if k + s in d:
            return d[k + s]
    return None


ops = [op for op in tp.ops if op.type not in ("top.Weight", "top.None", "top.Input")]
names = {op.name: op for op in ops}
rows = []
for op in ops:
    if op.name not in top:
        continue
    t = top[op.name]
    q, c = pick(tpu, op.name), pick(cvi, op.name)
    rows.append((op.name, op.type, cos(t, q) if q is not None else float("nan"),
                 cos(t, c) if c is not None else float("nan"), float(np.max(t)),
                 float(np.max(q)) if q is not None else float("nan"),
                 float(np.max(c)) if c is not None else float("nan")))
print(f"{'name':48s} {'type':16s} {'cos_tpu':>8s} {'cos_cvi':>8s} {'max_top':>9s} {'max_tpu':>9s} {'max_cvi':>9s}")
for r in rows:
    print(f"{r[0][:48]:48s} {r[1][:16]:16s} {r[2]:8.4f} {r[3]:8.4f} {r[4]:9.3f} {r[5]:9.3f} {r[6]:9.3f}")

# obj 경로: 1채널 Sigmoid(stride 별 3개)의 입력을 거슬러 올라간다
print("== obj 경로 (1채널 Sigmoid 에서 위로) ==")
byname = {r[0]: r for r in rows}
for op in ops:
    if op.type == "top.Sigmoid" and op.shape[1] == 1:
        chain, cur = [], op
        while cur is not None:
            chain.append(cur.name)
            prev = [p for p in cur.opds if p in names]
            cur = names[prev[0]] if prev else None
        first = None
        for n in reversed(chain):
            r = byname.get(n)
            mark = ""
            if r and first is None and (r[2] < 0.9 or r[3] < 0.9):
                first, mark = n, "  <== 처음 cos<0.9"
            if r:
                print(f"  {n[:48]:48s} {r[1]:16s} cos_tpu={r[2]:.4f} cos_cvi={r[3]:.4f} max top/tpu/cvi={r[4]:.3f}/{r[5]:.3f}/{r[6]:.3f}{mark}")
        print(f"  -> first bad: {first}")
