"""LED 열 랜드 안 비아 인 패드 후보 좌표 (O-44: 견적 뒤 결정용). 전면 형상 JSON(route_export.py)의 LED 패드 2(애노드 열 랜드) 다각형 안,
가장자리에서 0.35mm 안쪽, 0.8mm 격자. 출력은 M-001 O 기준(+Y 위) mm. 사용: python vip_candidates.py <front-geom.json>
"""
import json
import sys

import numpy as np


def inside(poly, x, y):
    n, c = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


g = json.load(open(sys.argv[1], encoding="utf-8"))
for ref in ("D_IR_A1", "D_IR_A2", "D_IR_B1", "D_IR_B2"):
    polys = [poly for p in g["pads"] if p["ref"] == ref and p["num"] == "2" for poly in p["polys"]["F.Cu"]]
    pts = [q for poly in polys for q in poly]
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    cand = []
    for x in np.arange(min(xs), max(xs) + 1e-6, 0.1):
        for y in np.arange(min(ys), max(ys) + 1e-6, 0.1):
            ring = [(x + dx, y + dy) for dx in (-0.35, 0, 0.35) for dy in (-0.35, 0, 0.35)]
            if all(any(inside(poly, a, b) for poly in polys) for a, b in ring):
                cand.append((x, y))
    out = []  # 서로 0.9mm 이상 (Ø0.6 비아 + 0.3)
    for x, y in cand:
        if all((x - a) ** 2 + (y - b) ** 2 >= 0.81 for a, b in out):
            out.append((x, y))
    out = [(round(x - 100, 2), round(100 - y, 2)) for x, y in out]
    print(f"{ref} ({len(out)}): " + " ".join(f"({a},{b})" for a, b in out))
