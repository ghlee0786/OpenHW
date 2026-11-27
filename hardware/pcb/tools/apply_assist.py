"""assist_route.py 결과(트랙 · 비아)를 보드에 넣는다 (KiCad pcbnew, O-105 A — 새 MCP IPC add_via 는 크기를 못 정해 SWIG 폴백).
GUI 가 그 보드를 열고 있지 않을 때만 쓴다(단일 작성자). 넣은 뒤 면을 다시 채우고 저장한다.
사용: <KiCad>/bin/python.exe apply_assist.py <board.kicad_pcb> <assist.json>
"""
import json
import sys

import pcbnew

MM = pcbnew.FromMM
LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    d = json.load(open(sys.argv[2], encoding="utf-8"))
    nt = nv = 0
    for r in d["routes"]:
        if not r["ok"]:
            continue
        net = b.FindNet(r["net"])
        for t in r["tracks"]:
            s = pcbnew.PCB_TRACK(b)
            s.SetStart(pcbnew.VECTOR2I(MM(t["a"][0]), MM(t["a"][1])))
            s.SetEnd(pcbnew.VECTOR2I(MM(t["b"][0]), MM(t["b"][1])))
            s.SetWidth(MM(t["w"]))
            s.SetLayer(LAY[t["layer"]])
            s.SetNet(net)
            b.Add(s)
            nt += 1
        for v in r["vias"]:
            s = pcbnew.PCB_VIA(b)
            s.SetPosition(pcbnew.VECTOR2I(MM(v["pos"][0]), MM(v["pos"][1])))
            s.SetWidth(MM(v["dia"]))
            s.SetDrill(MM(v["drill"]))
            s.SetNet(net)
            b.Add(s)
            nv += 1
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])
    print(f"넣음: 트랙 {nt} · 비아 {nv} · 경로 {sum(1 for r in d['routes'] if r['ok'])}")


if __name__ == "__main__":
    main()
