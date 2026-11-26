#!/usr/bin/env python3
"""YOLOX-Nano(Apache-2.0) ONNX → sscma-node YoloV5 후처리 형식(사람 1클래스) ONNX.

sscma-micro ma_model_yolov5.cpp generalValid/generalPostProcess 가 받는 형식:
  출력 1개 [1, (s²+m²+l²)·C_in, 6..85], 각 레코드 = [x, y, w, h, score, class...],
  x·y = 박스 중심, 0~1 정규화면 그대로 쓴다(int8 출력은 scale<0.1 이면 정규화로 본다), score = 레코드의 5번째 값.
YOLOX ONNX 출력 [1, 3549, 85] = [reg(4, 격자 기준), obj(sigmoid), cls80(sigmoid)] 이므로
  xy = (reg_xy + grid)·stride / W,  wh = exp(reg_wh)·stride / W,  score = obj·cls[person],  class = cls[person]
을 그래프에 넣고, 레코드 수 3549 를 3549·3 = 10647 로 0 패딩한다(빈 레코드는 score 0 이라 버려진다).
사용: yolox_to_sscma.py in.onnx out.onnx [입력 한 변=416]
"""
import sys

import numpy as np
import onnx
from onnx import TensorProto, helper, numpy_helper


def main(src, dst, size=416):
    m = onnx.load(src)
    g = m.graph
    out = g.output[0]
    dims = [d.dim_value for d in out.type.tensor_type.shape.dim]
    strides = (8, 16, 32)
    n = sum((size // s) ** 2 for s in strides)
    assert dims == [1, n, 85], f"예상과 다른 출력 모양 {dims}"

    grid, stride = [], []
    for s in strides:
        k = size // s
        yv, xv = np.meshgrid(np.arange(k), np.arange(k), indexing="ij")
        grid.append(np.stack((xv, yv), -1).reshape(-1, 2))
        stride.append(np.full((k * k, 1), s))
    grid = np.concatenate(grid).astype(np.float32)[None]          # [1,n,2]
    stride = np.concatenate(stride).astype(np.float32)[None]      # [1,n,1]

    inits = {
        "oh_grid": grid,
        "oh_stride_norm": stride / size,
        "oh_pad": np.zeros((1, n * 2, 6), np.float32),
    }
    for name, arr in inits.items():
        g.initializer.append(numpy_helper.from_array(arr, name))

    def i64(name, vals):
        g.initializer.append(numpy_helper.from_array(np.array(vals, np.int64), name))

    i64("oh_axes", [2])
    nodes = []

    def sl(name, a, b):
        i64(name + "_s", [a])
        i64(name + "_e", [b])
        nodes.append(helper.make_node("Slice", [out.name, name + "_s", name + "_e", "oh_axes"], [name]))

    sl("oh_xy", 0, 2)
    sl("oh_wh", 2, 4)
    sl("oh_obj", 4, 5)
    sl("oh_person", 5, 6)            # COCO 클래스 0 = person
    nodes += [
        helper.make_node("Add", ["oh_xy", "oh_grid"], ["oh_xy_g"]),
        helper.make_node("Mul", ["oh_xy_g", "oh_stride_norm"], ["oh_xy_n"]),
        helper.make_node("Exp", ["oh_wh"], ["oh_wh_e"]),
        helper.make_node("Mul", ["oh_wh_e", "oh_stride_norm"], ["oh_wh_n"]),
        helper.make_node("Mul", ["oh_obj", "oh_person"], ["oh_score"]),
        helper.make_node("Concat", ["oh_xy_n", "oh_wh_n", "oh_score", "oh_person"], ["oh_rec"], axis=2),
        helper.make_node("Concat", ["oh_rec", "oh_pad"], ["output_sscma"], axis=1),
    ]
    g.node.extend(nodes)
    del g.output[:]
    g.output.append(helper.make_tensor_value_info("output_sscma", TensorProto.FLOAT, [1, n * 3, 6]))
    onnx.checker.check_model(m)
    onnx.save(m, dst)
    print(f"{dst}: output_sscma [1,{n * 3},6]")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 416)
