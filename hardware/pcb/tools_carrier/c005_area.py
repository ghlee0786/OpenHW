"""캐리어: 제한 없는 규칙 영역(이름으로 DRU enclosedByArea 가 쓰는 것)을 사각형으로 넣는다 (KiCad pcbnew, GUI 닫고).
같은 이름 · 같은 사각형이 이미 있으면 넣지 않는다.
사용: <KiCad>/bin/python.exe c005_area.py <carrier.kicad_pcb> <이름> <x0> <y0> <x1> <y1> [층=F.Cu]
"""
import sys

import pcbnew

MM = pcbnew.FromMM
path, name = sys.argv[1], sys.argv[2]
x0, y0, x1, y1 = map(float, sys.argv[3:7])
layer = sys.argv[7] if len(sys.argv) > 7 else "F.Cu"
b = pcbnew.LoadBoard(path)
for z in b.Zones():
    bb = z.GetBoundingBox()
    if z.GetIsRuleArea() and z.GetZoneName() == name and abs(bb.GetLeft() - MM(x0)) < 2000 and abs(bb.GetTop() - MM(y0)) < 2000:
        print("이미 있음")
        raise SystemExit(0)
z = pcbnew.ZONE(b)
z.SetIsRuleArea(True)
z.SetZoneName(name)
z.SetLayer(b.GetLayerID(layer))
for f in (z.SetDoNotAllowTracks, z.SetDoNotAllowVias, z.SetDoNotAllowPads, z.SetDoNotAllowZoneFills, z.SetDoNotAllowFootprints):
    f(False)
ol = z.Outline()
ol.NewOutline()
for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
    ol.Append(MM(x), MM(y))
b.Add(z)
b.Save(path)
print("영역", name, x0, y0, x1, y1, layer)
