"""넷별 패드 좌표(O 기준, +Y 위)·면·크기 출력. 사용: <KiCad>/bin/python.exe pads_of.py <board> <넷 정규식>"""
import re
import sys

import pcbnew

b = pcbnew.LoadBoard(sys.argv[1])
pat = re.compile(sys.argv[2])
rows = []
for fp in list(b.GetFootprints()):
    for p in fp.Pads():
        n = p.GetNetname()
        if n and pat.search(n):
            q = p.GetPosition()
            s = p.GetBoundingBox()
            rows.append((n, fp.GetReference(), p.GetNumber(), round(pcbnew.ToMM(q.x) - 100, 3), round(100 - pcbnew.ToMM(q.y), 3),
                         "B" if fp.IsFlipped() else "F", round(pcbnew.ToMM(s.GetWidth()), 2), round(pcbnew.ToMM(s.GetHeight()), 2),
                         "THT" if p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH else "SMD"))
for r in sorted(rows):
    print(*r)
