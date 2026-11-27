"""O-105 A 부품 이동 (KiCad pcbnew, GUI 닫고): moves.json {ref: [x, y, rot]} (KiCad mm) 대로 옮기고 기록을 남긴다.
사용: <KiCad>/bin/python.exe move_parts.py <board.kicad_pcb> <moves.json>
"""
import json
import sys

import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
mv = json.load(open(sys.argv[2], encoding="utf-8"))
for fp in b.GetFootprints():
    r = fp.GetReference()
    if r in mv:
        x, y, rot = mv[r]
        old = (round(pcbnew.ToMM(fp.GetPosition().x), 3), round(pcbnew.ToMM(fp.GetPosition().y), 3), fp.GetOrientationDegrees())
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y)))
        fp.SetOrientationDegrees(rot)
        print(f"{r}: {old} -> ({x}, {y}, {rot})")
b.Save(sys.argv[1])
