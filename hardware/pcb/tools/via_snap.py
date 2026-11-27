"""track_not_centered_on_via 정리 (KiCad pcbnew, GUI 닫고): 같은 넷 비아 구리 안에서 중심이 아닌 곳에 끝난 트랙 끝점을 비아 중심으로 옮긴다.
고속 쌍(CSI/MDI/USB)은 건드리지 않는다. 사용: via_snap.py <board.kicad_pcb>
"""
import math
import sys

import pcbnew

HS = ("EPHY", "/USB_DP", "/USB_DN", "CAM_RX")
b = pcbnew.LoadBoard(sys.argv[1])
vias = {}
for v in b.GetTracks():
    if v.GetClass() == "PCB_VIA":
        vias.setdefault(v.GetNetname(), []).append((v.GetPosition(), v.GetWidth(pcbnew.F_Cu) / 2))
n = 0
for t in b.GetTracks():
    if t.GetClass() != "PCB_TRACK" or any(k in t.GetNetname() for k in HS):
        continue
    for get, setp in ((t.GetStart, t.SetStart), (t.GetEnd, t.SetEnd)):
        p = get()
        for c, r in vias.get(t.GetNetname(), []):
            d = math.hypot(p.x - c.x, p.y - c.y)
            if 1000 < d < r:
                setp(pcbnew.VECTOR2I(c.x, c.y))
                n += 1
                break
if n:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])
print("snapped", n)
