"""배선 전 열 구리 (P-003, O-31·K21): route.py 가 배선 전에 부른다. 좌표는 KiCad mm, 사각형 정의는 O 기준(+Y 위).

전면 IR LED (VSMA1085400, 큰 열 랜드 = 패드 2 = 애노드 넷):
  - 윗면: LED 패드 둘레 사각형을 애노드 넷 구리(F.Cu 영역, 우선순위 1)로.
  - 아랫면: K21 노출 구리 패드(B.Cu 영역 + B.Mask 개구). TP_A 는 A1(IRA_SET)·A2(IRA_M) 넷이 달라 두 장으로 가른다(가운데 0.6 틈).
  - 열 비아: 노출 패드 안, 어느 패드 위도 아닌 곳에 1.0mm 격자로 Ø0.6/0.3 비아(애노드 넷) — 윗면 영역 ↔ 아랫면 패드.
노출 패드(EP)가 있는 GND 부품(면적 ≥ 2mm², 외층): EP 둘레 1.2mm 안 빈자리에 GND 비아 최대 6개 (B/F 면 채움이 EP 와 잇는다).
반환: zones [{net, layer, rect(KiCad), priority}], masks [{layer, rect}], 그리고 B 에 비아·구리 점유를 기록한다.
"""
import math

import numpy as np

# K21 (M-002 3f7ceee §8, M-001e 1504c93), TP_A 는 넷 분리를 위해 둘로 (orch 보고 2026-11-26)
TP = {
    "front": [
        ("D_IR_A1", (-9.5, 16.5, -0.3, 19.5)),
        ("D_IR_A2", (0.3, 16.5, 9.5, 19.5)),
        ("D_IR_B1", (-12.0, -19.5, -6.0, -13.5)),
        ("D_IR_B2", (6.0, -19.5, 12.0, -13.5)),
    ],
    "carrier": [],
}
TVIA = {"dia": 0.6, "drill": 0.3}


def K(x, y):
    return (100.0 + x, 100.0 - y)


def rectK(r):
    (x0, y1), (x1, y0) = K(r[0], r[1]), K(r[2], r[3])
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def pre_route(B, board_name, LAYERS, CLR, EPS, G):
    zones, masks = [], []
    pads_by_ref = {}
    for p in B.pads:
        pads_by_ref.setdefault(p["ref"], []).append(p)

    def free_for(net_id, x, y, rad, layers=(0, 1, 2, 3)):
        r, c = B.cell(x, y)
        m = int((rad + CLR + EPS) / G) + 1
        for L in layers:
            blk = B.occ[L, r - m:r + m + 1, c - m:c + m + 1]
            ys, xs = np.mgrid[-m:m + 1, -m:m + 1]
            near = (ys ** 2 + xs ** 2) * G * G <= (rad + CLR + EPS) ** 2
            if np.any(near & (blk != 0) & (blk != net_id)):
                return False
        mv = int(rad / G) + 1
        if np.any(B.hardvia[r - mv:r + mv + 1, c - mv:c + mv + 1]):  # 비아 둘레 전체가 금지 영역 밖
            return False
        h = int((rad + 0.25 + 0.2) / G) + 1
        if np.any(B.holes[r - h:r + h + 1, c - h:c + h + 1]):
            return False
        return True

    def in_any_pad(x, y, margin):
        for p in B.pads:
            for polys in p["polys"].values():
                for poly in polys:
                    xs = [q[0] for q in poly]
                    ys = [q[1] for q in poly]
                    if min(xs) - margin <= x <= max(xs) + margin and min(ys) - margin <= y <= max(ys) + margin:
                        return True
        return False

    # 1) LED 열 구리
    for ref, tp in TP[board_name]:
        if ref not in pads_by_ref:
            continue
        anode = next(p for p in pads_by_ref[ref] if p["num"] == "2")
        net = anode["net"]
        nid = B.netid[net]
        lp = [q for p in pads_by_ref[ref] for polys in p["polys"].values() for poly in polys for q in poly]
        bot = rectK(tp)
        # 윗면 영역 = LED 패드 둘레(+1.0) ∪ 아랫면 노출 패드 범위 — 패드 밖 빈자리(두 LED 사이 등)에 열 비아를 둘 수 있게
        top = (min(min(q[0] for q in lp) - 1.0, bot[0]), min(min(q[1] for q in lp) - 1.0, bot[1]),
               max(max(q[0] for q in lp) + 1.0, bot[2]), max(max(q[1] for q in lp) + 1.0, bot[3]))
        # 윗면 영역은 캐소드 패드(패드 1)를 피해 애노드 쪽 절반만: 캐소드 패드 바깥 경계까지 자른다
        cath = [q for p in pads_by_ref[ref] if p["num"] == "1" for polys in p["polys"].values() for poly in polys for q in poly]
        cy0, cy1 = min(q[1] for q in cath), max(q[1] for q in cath)
        ay = sum(q[1] for q in lp if True) / len(lp)
        if cy1 < anode["pos"][1]:      # 캐소드가 위(작은 y) → 영역은 캐소드 아래부터
            top = (top[0], cy1 + 0.3, top[2], top[3])
        else:                           # 캐소드가 아래
            top = (top[0], top[1], top[2], cy0 - 0.3)
        e = B.g["edge"]
        top = (max(top[0], e[0] + 0.5), max(top[1], e[1] + 0.5), min(top[2], e[2] - 0.5), min(top[3], e[3] - 0.5))
        zones.append({"net": net, "layer": "F.Cu", "rect": list(top), "priority": 1})
        zones.append({"net": net, "layer": "B.Cu", "rect": list(bot), "priority": 1})
        masks.append({"layer": "B.Mask", "rect": list(bot)})
        for L, rr in ((0, top), (3, bot)):  # 점유 기록 → 다른 넷 배선이 피한다
            r0, c0 = B.cell(rr[0], rr[1])
            r1, c1 = B.cell(rr[2], rr[3])
            sub = B.occ[L, r0:r1 + 1, c0:c1 + 1]
            sub[sub == 0] = nid
        # 열 비아: 윗면 영역 ∩ 아랫면 패드, 패드 위 아님, 1.0mm 격자
        x0, y0 = max(top[0], bot[0]) + 0.5, max(top[1], bot[1]) + 0.5
        x1, y1 = min(top[2], bot[2]) - 0.5, min(top[3], bot[3]) - 0.5
        n = 0
        for x in np.arange(x0, x1 + 1e-6, 0.8):
            for y in np.arange(y0, y1 + 1e-6, 0.8):
                if in_any_pad(x, y, 0.45) or not free_for(nid, x, y, TVIA["dia"] / 2):
                    continue
                B.add_via(net, (round(float(x), 4), round(float(y), 4)), TVIA)
                n += 1
        print(f"열: {ref} 애노드 {net} 윗면 영역 + 아랫면 노출 패드 {tuple(round(v, 2) for v in tp)} · 열 비아 {n}")

    # 2) GND EP 둘레 비아
    if "/GND" in B.netid:
        gid = B.netid["/GND"]
        for p in B.pads:
            if p["net"] != "/GND" or p["drill"] or p["layers"][0] not in ("F.Cu", "B.Cu") or not p["ref"].startswith("U"):
                continue
            pts = [q for polys in p["polys"].values() for poly in polys for q in poly]
            w = max(q[0] for q in pts) - min(q[0] for q in pts)
            h = max(q[1] for q in pts) - min(q[1] for q in pts)
            if w * h < 2.0:
                continue
            cx, cy = p["pos"]
            n = 0
            for ang in np.linspace(0, 2 * math.pi, 16, endpoint=False):
                if n >= 6:
                    break
                rad = max(w, h) / 2 + 0.9
                x, y = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
                if in_any_pad(x, y, 0.45) or not free_for(gid, x, y, 0.325):
                    continue
                B.add_via("/GND", (round(x, 4), round(y, 4)), {"dia": 0.65, "drill": 0.30})
                n += 1
            print(f"열: {p['ref']} EP GND 둘레 비아 {n}")
    return zones, masks
