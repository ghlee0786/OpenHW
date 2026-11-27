"""P-005 전면: GND 가 아닌 구리 영역(IR LED 열 구리 THERMAL_* 등)의 외곽을 JSON 으로 (KiCad pcbnew, 보드는 바꾸지 않음).
배선 계산이 이 영역을 그 넷의 구리로 본다 — 다른 넷 트랙이 지나가면 영역 채움이 잘려 그 넷이 끊긴다(P-005 SCL 첫 시도에서 IRB_M).
사용: <KiCad>/bin/python.exe p005_zones.py <board.kicad_pcb> <out.json>
"""
import json
import sys

import pcbnew

TO = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
out = []
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() in ("/GND", ""):
        continue
    o = z.Outline()
    for k in range(o.OutlineCount()):
        ol = o.Outline(k)
        pts = [[round(TO(ol.CPoint(i).x), 4), round(TO(ol.CPoint(i).y), 4)] for i in range(ol.PointCount())]
        out.append({"name": z.GetZoneName(), "net": z.GetNetname(), "layers": [b.GetLayerName(l) for l in z.GetLayerSet().Seq()], "outline": pts})
        print(z.GetZoneName(), z.GetNetname(), out[-1]["layers"], [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)])
json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
