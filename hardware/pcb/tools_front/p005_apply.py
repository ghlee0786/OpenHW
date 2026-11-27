"""P-005 전면: p005_rip.py 결과를 보드에 넣는다 (KiCad pcbnew, GUI 가 그 보드를 열고 있지 않을 때만).
{"replace": {넷: {tracks, vias}}} — 그 넷의 기존 트랙 · 비아를 모두 지우고 목록으로 바꾼다. 면을 다시 채우고 저장.
사용: <KiCad>/bin/python.exe p005_apply.py <board.kicad_pcb> <rip.json>
"""
import json
import sys

import pcbnew

MM = pcbnew.FromMM
LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "GND_PWR": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    d = json.load(open(sys.argv[2], encoding="utf-8"))
    nd = nt = nv = 0
    for name, r in d["replace"].items():
        net = b.FindNet(name)
        for t in [t for t in b.GetTracks() if t.GetNetname() == name]:
            b.Delete(t)
            nd += 1
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
    print(f"넷 {len(d['replace'])} · 지움 {nd} · 넣음 트랙 {nt} · 비아 {nv}")


if __name__ == "__main__":
    main()
