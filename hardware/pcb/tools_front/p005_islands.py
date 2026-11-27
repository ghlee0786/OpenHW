"""P-005 전면: GND 면 섬(그 안에 GND 비아 · 관통 패드가 없는 채움 조각)의 외곽을 JSON 으로 낸다 (KiCad pcbnew, 보드는 바꾸지 않음).
island_vias.py 는 4층 모두 GND 채움인 자리만 찾는다 — 여기서는 외곽만 내고, 자리 찾기는 p005_gnd.py 가 배선기 간격 지도로 한다.
사용: <KiCad>/bin/python.exe p005_islands.py <board.kicad_pcb> <out.json>
"""
import json
import sys

import pcbnew

TO = pcbnew.ToMM


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    links = [v.GetPosition() for v in b.GetTracks() if v.GetClass() == "PCB_VIA" and v.GetNetname() == "/GND"]
    links += [p.GetPosition() for fp in b.GetFootprints() for p in fp.Pads()
              if p.GetNetname() == "/GND" and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    out = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "/GND":
            continue
        for lid in z.GetLayerSet().Seq():
            ps = z.GetFilledPolysList(lid)
            if ps is None:
                continue
            for k in range(ps.OutlineCount()):
                one = pcbnew.SHAPE_POLY_SET()
                one.AddOutline(ps.Outline(k))
                for h in range(ps.HoleCount(k)):
                    one.AddHole(ps.Hole(k, h))
                if any(one.Contains(q) for q in links):
                    continue
                o = ps.Outline(k)
                pts = [[round(TO(o.CPoint(i).x), 4), round(TO(o.CPoint(i).y), 4)] for i in range(o.PointCount())]
                holes = []
                for h in range(ps.HoleCount(k)):
                    ho = ps.Hole(k, h)
                    holes.append([[round(TO(ho.CPoint(i).x), 4), round(TO(ho.CPoint(i).y), 4)] for i in range(ho.PointCount())])
                pads = [f"{fp.GetReference()}.{p.GetNumber()}" for fp in b.GetFootprints() for p in fp.Pads()
                        if p.GetNetname() == "/GND" and p.IsOnLayer(lid) and one.Contains(p.GetPosition())]
                out.append({"layer": b.GetLayerName(lid), "zone": z.GetZoneName(), "outline": pts, "holes": holes, "pads": pads})
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
    for o in out:
        xs = [p[0] for p in o["outline"]]
        ys = [p[1] for p in o["outline"]]
        print(o["layer"], o["zone"], f"bbox {min(xs):.2f},{min(ys):.2f} … {max(xs):.2f},{max(ys):.2f}", "패드", o["pads"])
    print("섬", len(out))


if __name__ == "__main__":
    main()
