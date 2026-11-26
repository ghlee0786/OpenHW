#!/usr/bin/env python3
"""F-004b 하강 단계 비교: float top MLIR 과 cvimodel(호스트 모의)의 중간·출력 텐서를 채널별로 비교한다.
사용(tpuc_dev, PYTHONPATH=$TP/python:$TP, cd /w/work): stage_compare.py [이미지]
cvimodel 덤프에는 층 묶음 때문에 헤드 1158_Reshape(stride 8, [1,85,2704])와 최종 출력만 남는다.
"""
import sys

import cv2
import numpy as np
from tools.model_runner import mlir_inference, model_inference
from verify_cvimodel import aligned_rgb

N = "yolox_nano_person_416"
IMG = sys.argv[1] if len(sys.argv) > 1 else "/w/tpu-mlir/regression/dataset/COCO2017/000000085329.jpg"


def letterbox(img, size=416):
    h, w = img.shape[:2]
    r = min(size / h, size / w)
    nh, nw = int(round(h * r)), int(round(w * r))
    out = np.zeros((size, size, 3), np.uint8)
    top, left = (size - nh) // 2, (size - nw) // 2
    out[top:top + nh, left:left + nw] = cv2.resize(img, (nw, nh))
    return out


def stat(a):
    a = np.asarray(a, np.float32).ravel()
    return f"min={a.min():.4f} max={a.max():.4f} mean={a.mean():.4f}"


def cos(a, b):
    a, b = np.asarray(a, np.float64).ravel(), np.asarray(b, np.float64).ravel()
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))


bgr = letterbox(cv2.imread(IMG))
top = mlir_inference({"images": bgr.transpose(2, 0, 1)[None].astype(np.float32)}, N + ".mlir", dump_all=True)
cvi = model_inference({"images_raw": aligned_rgb(bgr)}, N + "_int8_cv181x.cvimodel", dump_all=True)

print("== 최종 출력 열별 [x,y,w,h,score,person] (앞 3549 행) ==")
a = np.asarray(top["output_sscma_Transpose"], np.float32).reshape(-1, 6)[:3549]
b = np.asarray(cvi["output_sscma_Transpose"], np.float32).reshape(-1, 6)[:3549]
for c in range(6):
    print(f"col{c}: top {stat(a[:, c])} | cvi {stat(b[:, c])} cos={cos(a[:, c], b[:, c]):.4f}")
print("== 헤드 1158_Reshape [85,2704] 채널별 (Slice 앞) ==")
h = np.asarray(top["1158_Reshape"], np.float32).reshape(85, -1)
g = np.asarray(cvi["1158_Reshape"], np.float32).reshape(85, -1)
for nm, sl in (("reg0-3", slice(0, 4)), ("obj4", slice(4, 5)), ("person5", slice(5, 6)), ("cls6-84", slice(6, 85))):
    print(f"{nm}: top {stat(h[sl])} | cvi {stat(g[sl])} cos={cos(h[sl], g[sl]):.4f}")
for c in range(6):
    print(f"  ch{c}: cos={cos(h[c], g[c]):.4f} top_max={h[c].max():.3f} cvi_max={g[c].max():.3f}")
