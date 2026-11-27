"""캐리어 미세 손질 (KiCad pcbnew, GUI 닫고): 비아 옮기기(끝이 그 비아에 닿은 트랙 끝도 같이) · 트랙 폭 바꾸기 · 비아 지우기.

사용: <KiCad>/bin/python.exe c005_nudge.py <carrier.kicad_pcb> <nudge.json>
nudge.json: [{"op":"move","net":"/N","from":[x,y],"to":[x,y]}, {"op":"width","net":"/N","layer":"F.Cu","a":[x,y],"b":[x,y],"w":0.15},
             {"op":"delvia","net":"/N","pos":[x,y]}, {"op":"viasize","net":"/N","pos":[x,y],"dia":0.5,"drill":0.2}]
"""
import json
import sys

import pcbnew

MM = pcbnew.FromMM
TOL = MM(0.002)


def at(p, q):
    return abs(p.x - MM(q[0])) <= TOL and abs(p.y - MM(q[1])) <= TOL


b = pcbnew.LoadBoard(sys.argv[1])
n = 0
for e in json.load(open(sys.argv[2], encoding="utf-8")):
    hit = 0
    for t in list(b.GetTracks()):
        if t.GetNetname() != e["net"]:
            continue
        isvia = t.GetClass() == "PCB_VIA"
        if e["op"] == "move":
            to = pcbnew.VECTOR2I(MM(e["to"][0]), MM(e["to"][1]))
            if isvia and at(t.GetPosition(), e["from"]):
                t.SetPosition(to)
                hit += 1
            elif not isvia:
                if at(t.GetStart(), e["from"]):
                    t.SetStart(to)
                    hit += 1
                if at(t.GetEnd(), e["from"]):
                    t.SetEnd(to)
                    hit += 1
        elif e["op"] == "width" and not isvia and b.GetLayerName(t.GetLayer()) == e["layer"]:
            if (at(t.GetStart(), e["a"]) and at(t.GetEnd(), e["b"])) or (at(t.GetStart(), e["b"]) and at(t.GetEnd(), e["a"])):
                t.SetWidth(MM(e["w"]))
                hit += 1
        elif e["op"] == "delvia" and isvia and at(t.GetPosition(), e["pos"]):
            b.Delete(t)
            hit += 1
        elif e["op"] == "viasize" and isvia and at(t.GetPosition(), e["pos"]):
            t.SetWidth(MM(e["dia"]))
            t.SetDrill(MM(e["drill"]))
            hit += 1
    if not hit:
        raise SystemExit(f"대상 없음: {e}")
    n += hit
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print("손질", n)
