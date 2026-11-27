"""캐리어: 한 넷의 한 구간(사각형 안에 두 끝이 다 든 트랙)을 지우고 새 꺾은선으로 바꾼다 (KiCad pcbnew, GUI 닫고).

고속 쌍 길이 보정 굴곡을 손으로 고칠 때 쓴다(RQ-5/6). 판정은 뒤의 kicad-cli DRC.
사용: <KiCad>/bin/python.exe c005_repath.py <carrier.kicad_pcb> <repath.json>
repath.json: [{"net": "/N", "layer": "F.Cu", "box": [x0, y0, x1, y1], "path": [[x, y], ...], "w": 0.15}]
"""
import json
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
for e in json.load(open(sys.argv[2], encoding="utf-8")):
    x0, y0, x1, y1 = e["box"]

    def inside(p):
        return x0 <= TO(p.x) <= x1 and y0 <= TO(p.y) <= y1

    nd = 0
    for t in list(b.GetTracks()):
        if t.GetClass() == "PCB_TRACK" and t.GetNetname() == e["net"] and b.GetLayerName(t.GetLayer()) == e["layer"] \
                and inside(t.GetStart()) and inside(t.GetEnd()):
            b.Delete(t)
            nd += 1
    for a, c in zip(e["path"][:-1], e["path"][1:]):
        s = pcbnew.PCB_TRACK(b)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
        s.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
        s.SetWidth(MM(e["w"]))
        s.SetLayer(b.GetLayerID(e["layer"]))
        s.SetNet(b.FindNet(e["net"]))
        s.SetLocked(True)
        b.Add(s)
    print(e["net"], "지움", nd, "넣음", len(e["path"]) - 1)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
