"""O-105 A: J1(BTB) 밑 · 둘레 뒷면을 막는 시험점을 빈자리로 옮길 좌표를 고른다 (KiCad pcbnew, 보드 안 바꿈 → moves json).

BTB J1 핀(0.5 피치 60핀)은 핀 바로 옆에 비아를 떨어뜨려 뒷면 · In2 로 나가야 하는데, 시험점 패드(Ø1.0)들이 J1 밑 뒷면을 차지해
비아 자리가 없었다(O-105 A 진단). 시험점은 탐침만 닿으면 되므로 J1 구역 밖 뒷면 빈자리로 옮긴다.
조건: 같은 면 courtyard 0.2 · 모든 관통 패드/구멍 0.3 · 부품 금지 영역 · 외곽 1.0 · 고속/GND 구리(비아 · 고속 트랙) 0.3 밖.
사용: <KiCad>/bin/python.exe tp_spots.py <board.kicad_pcb> <out moves.json> [x0 y0 x1 y1 = 비울 구역]
"""
import json
import math
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM
HS = ("EPHY", "/USB_DP", "/USB_DN", "CAM_RX")
b = pcbnew.LoadBoard(sys.argv[1])
zone = [float(v) for v in sys.argv[3:7]] if len(sys.argv) > 6 else [107.0, 90.0, 117.5, 110.0]
eb = b.GetBoardEdgesBoundingBox()
ex0, ey0, ex1, ey1 = TO(eb.GetLeft()), TO(eb.GetTop()), TO(eb.GetRight()), TO(eb.GetBottom())


def box(bb, g=0.0):
    return (TO(bb.GetLeft()) - g, TO(bb.GetTop()) - g, TO(bb.GetRight()) + g, TO(bb.GetBottom()) + g)


obst = []   # 뒷면 부품 자리(사각형)
move = []
for fp in b.GetFootprints():
    ref = fp.GetReference()
    cs = fp.GetCourtyard(pcbnew.B_CrtYd)
    p = fp.GetPosition()
    is_tp = ref.startswith("TP") and fp.IsFlipped()
    only = __import__("os").environ.get("TP_REFS", "").split(",")
    if is_tp and (ref in only or (only == [""] and zone[0] <= TO(p.x) <= zone[2] and zone[1] <= TO(p.y) <= zone[3])):
        move.append(fp)
        continue
    if cs.OutlineCount():
        obst.append(box(cs.BBox(), 0.2))
    for pad in fp.Pads():
        if pad.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            obst.append(box(pad.GetBoundingBox(), 0.3))
for z in b.Zones():
    if z.GetIsRuleArea() and (z.GetDoNotAllowFootprints() or z.GetDoNotAllowPads()):
        obst.append(box(z.GetBoundingBox(), 0.1))
keep_pts = []  # 고속 · GND 비아와 고속 트랙(뒷면)
for t in b.GetTracks():
    n = t.GetNetname()
    if t.GetClass() == "PCB_VIA":
        if n == "/GND" or any(k in n for k in HS):
            keep_pts.append((TO(t.GetPosition().x), TO(t.GetPosition().y), TO(t.GetWidth(pcbnew.B_Cu)) / 2))
    elif any(k in n for k in HS) and t.GetLayer() == pcbnew.B_Cu:
        a, c = t.GetStart(), t.GetEnd()
        L = max(math.hypot(TO(c.x - a.x), TO(c.y - a.y)), 0.1)
        for i in range(int(L / 0.2) + 1):
            f = min(i * 0.2 / L, 1.0)
            keep_pts.append((TO(a.x) + f * TO(c.x - a.x), TO(a.y) + f * TO(c.y - a.y), TO(t.GetWidth()) / 2))
R = 1.0    # 시험점 courtyard 반쪽 (TestPoint_Pad_D1.0mm courtyard Ø2.0 — 0.75 로 잡아 4쌍이 겹쳤음)
taken = []


def free(x, y):
    if x - R < ex0 + 1.0 or x + R > ex1 - 1.0 or y - R < ey0 + 1.0 or y + R > ey1 - 1.0:
        return False
    if zone[0] - R <= x <= zone[2] + R and zone[1] - R <= y <= zone[3] + R:
        return False
    for o in obst:
        if x + R > o[0] and x - R < o[2] and y + R > o[1] and y - R < o[3]:
            return False
    if any(math.hypot(x - px, y - py) < 0.5 + pr + 0.3 for px, py, pr in keep_pts):
        return False
    return all(math.hypot(x - tx, y - ty) >= 2 * R + 0.2 for tx, ty in taken)


cands = [(ex0 + 0.5 * i, ey0 + 0.5 * j) for i in range(int((ex1 - ex0) / 0.5) + 1) for j in range(int((ey1 - ey0) / 0.5) + 1)]
out = {}
for fp in sorted(move, key=lambda f: f.GetReference()):
    p = fp.GetPosition()
    px, py = TO(p.x), TO(p.y)
    best = min((c for c in cands if free(*c)), key=lambda c: math.hypot(c[0] - px, c[1] - py), default=None)
    if best is None:
        print(fp.GetReference(), "자리 없음")
        continue
    taken.append(best)
    out[fp.GetReference()] = [round(best[0], 3), round(best[1], 3), fp.GetOrientationDegrees()]
    print(f"{fp.GetReference()} {fp.Pads()[0].GetNetname()}: ({px:.2f}, {py:.2f}) -> {best}  이동 {math.hypot(best[0] - px, best[1] - py):.1f}mm")
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
