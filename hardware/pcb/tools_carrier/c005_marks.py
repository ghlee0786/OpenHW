"""캐리어 보드 실크 표시(풋프린트 밖 보드 그림 — 사본 라이브러리와 무관, lib_footprint_mismatch 없음) (KiCad pcbnew, GUI 닫고).

J7(JST GH 6핀) 1번 핀 점: 표준 풋프린트의 1번 표시가 패드 둘레 자르기에서 없어져(검토 V-006a) 1번 패드 동쪽에 지름 0.5 점을 둔다.
사용: <KiCad>/bin/python.exe c005_marks.py <carrier.kicad_pcb>
"""
import sys

import pcbnew

MM = pcbnew.FromMM
MARKS = [("J7", "1", 0.56, 0.0, 0.175)]  # 참조, 핀, 패드 동쪽 끝에서 중심까지 dx, dy, 반지름(선폭 0.15 원 → 바깥 지름 0.5)

b = pcbnew.LoadBoard(sys.argv[1])
fps = {f.GetReference(): f for f in b.GetFootprints()}
n = 0
for ref, pin, dx, dy, r in MARKS:
    p = [q for q in fps[ref].Pads() if q.GetNumber() == pin][0]
    bb = p.GetBoundingBox()
    c = pcbnew.VECTOR2I(bb.GetRight() + MM(dx), bb.GetCenter().y + MM(dy))
    if any(d.GetClass() == "PCB_SHAPE" and d.GetLayer() == pcbnew.F_SilkS and d.GetShape() == pcbnew.SHAPE_T_CIRCLE and d.GetCenter() == c for d in b.GetDrawings()):
        continue
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_CIRCLE)
    s.SetLayer(pcbnew.F_SilkS)
    s.SetCenter(c)
    s.SetEnd(pcbnew.VECTOR2I(c.x + MM(r), c.y))
    s.SetWidth(MM(0.15))
    s.SetFilled(True)
    b.Add(s)
    n += 1
    print(ref, pin, round(pcbnew.ToMM(c.x), 3), round(pcbnew.ToMM(c.y), 3))
b.Save(sys.argv[1])
print("표시", n)
