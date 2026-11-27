"""P-005 전면: 손 배선 편집 목록을 보드에 넣는다 (KiCad pcbnew). 좌표 mm, 끝점 일치 허용 0.6µm … 아니라 0.002mm.
편집 JSON: [{"op":"del","net","layer","a":[x,y],"b":[x,y]}, {"op":"add","net","layer","a","b","w"},
            {"op":"via","net","pos","dia","drill"}, {"op":"delvia","net","pos"}]
사용: <KiCad>/bin/python.exe p005_edit.py <board.kicad_pcb> <edits.json>
"""
import json
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM
LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "GND": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "GND_PWR": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}
TOL = 0.002


def near(p, q):
    return abs(TO(p.x) - q[0]) < TOL and abs(TO(p.y) - q[1]) < TOL


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    ed = json.load(open(sys.argv[2], encoding="utf-8"))
    cnt = {}
    for e in ed:
        op = e["op"]
        if op == "del":
            hit = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK" and t.GetNetname() == e["net"]
                   and t.GetLayer() == LAY[e["layer"]]
                   and ((near(t.GetStart(), e["a"]) and near(t.GetEnd(), e["b"])) or (near(t.GetStart(), e["b"]) and near(t.GetEnd(), e["a"])))]
            if not hit:
                print("못 찾음:", e)
                sys.exit(2)
            for t in hit:
                b.Delete(t)
        elif op == "delvia":
            hit = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA" and t.GetNetname() == e["net"] and near(t.GetPosition(), e["pos"])]
            if not hit:
                print("못 찾음:", e)
                sys.exit(2)
            for t in hit:
                b.Delete(t)
        elif op == "add":
            s = pcbnew.PCB_TRACK(b)
            s.SetStart(pcbnew.VECTOR2I(MM(e["a"][0]), MM(e["a"][1])))
            s.SetEnd(pcbnew.VECTOR2I(MM(e["b"][0]), MM(e["b"][1])))
            s.SetWidth(MM(e["w"]))
            s.SetLayer(LAY[e["layer"]])
            s.SetNet(b.FindNet(e["net"]))
            b.Add(s)
        elif op == "via":
            s = pcbnew.PCB_VIA(b)
            s.SetPosition(pcbnew.VECTOR2I(MM(e["pos"][0]), MM(e["pos"][1])))
            s.SetWidth(MM(e.get("dia", 0.65)))
            s.SetDrill(MM(e.get("drill", 0.3)))
            s.SetNet(b.FindNet(e["net"]))
            b.Add(s)
        cnt[op] = cnt.get(op, 0) + 1
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])
    print("편집", cnt)


if __name__ == "__main__":
    main()
