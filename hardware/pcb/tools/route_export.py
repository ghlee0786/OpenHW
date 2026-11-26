"""배선기 1단계 (KiCad pcbnew): 보드 형상을 JSON으로 내보낸다. 좌표는 KiCad mm 그대로(y 아래).

내보내는 것: 외곽 bbox, 구리층 4개, 패드(넷·층·다각형·구멍), 잠긴(locked) 기존 트랙·비아, 금지 규칙 영역(트랙·비아 금지).
사용: <KiCad>/bin/python.exe route_export.py <board.kicad_pcb> <out.json>
"""
import json
import sys

import pcbnew

CU = [("F.Cu", pcbnew.F_Cu), ("In1.Cu", pcbnew.In1_Cu), ("In2.Cu", pcbnew.In2_Cu), ("B.Cu", pcbnew.B_Cu)]
mm = pcbnew.ToMM


def poly_points(ps):
    out = []
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        out.append([(round(mm(o.CPoint(k).x), 4), round(mm(o.CPoint(k).y), 4)) for k in range(o.PointCount())])
    return out


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    bb = b.GetBoardEdgesBoundingBox()
    data = {"edge": [mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())],
            "layers": [n for n, _ in CU], "pads": [], "tracks": [], "vias": [], "keepouts": []}
    for fp in list(b.GetFootprints()):
        for p in fp.Pads():
            layers = [n for n, lid in CU if p.IsOnLayer(lid)]
            polys = {}
            for n, lid in CU:
                if n in layers:
                    ps = pcbnew.SHAPE_POLY_SET()
                    p.TransformShapeToPolygon(ps, lid, 0, pcbnew.FromMM(0.005), pcbnew.ERROR_OUTSIDE)
                    polys[n] = poly_points(ps)
            d = p.GetDrillSize()
            q = p.GetPosition()
            data["pads"].append({
                "ref": fp.GetReference(), "num": p.GetNumber(), "net": p.GetNetname(),
                "layers": layers, "polys": polys, "pos": [mm(q.x), mm(q.y)],
                "drill": mm(min(d.x, d.y)) if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH) else 0.0,
                "npth": p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH,
            })
    for t in b.GetTracks():
        if not t.IsLocked():
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            v = pcbnew.Cast_to_PCB_VIA(t)
            data["vias"].append({"net": v.GetNetname(), "pos": [mm(v.GetPosition().x), mm(v.GetPosition().y)],
                                 "dia": mm(v.GetWidth(pcbnew.F_Cu)), "drill": mm(v.GetDrillValue())})
        else:
            data["tracks"].append({"net": t.GetNetname(), "layer": t.GetLayerName(), "w": mm(t.GetWidth()),
                                   "a": [mm(t.GetStart().x), mm(t.GetStart().y)], "b": [mm(t.GetEnd().x), mm(t.GetEnd().y)]})
    data["areas"] = [{"name": z.GetZoneName(), "layers": [n for n, lid in CU if z.IsOnLayer(lid)], "polys": poly_points(z.Outline())}
                     for z in b.Zones() if z.GetIsRuleArea()]
    fpz = [z for fp in list(b.GetFootprints()) for z in fp.Zones()]  # 풋프린트 안 금지 영역(예: microSD J4)
    for z in list(b.Zones()) + fpz:
        if z.GetIsRuleArea() and (z.GetDoNotAllowTracks() or z.GetDoNotAllowVias()):
            data["keepouts"].append({"name": z.GetZoneName(), "layers": [n for n, lid in CU if z.IsOnLayer(lid)],
                                     "polys": poly_points(z.Outline()), "tracks": z.GetDoNotAllowTracks(),
                                     "vias": z.GetDoNotAllowVias()})
    json.dump(data, open(sys.argv[2], "w", encoding="utf-8"))
    print(f"pads {len(data['pads'])} · locked tracks {len(data['tracks'])} · vias {len(data['vias'])} · keepouts {len(data['keepouts'])}")


if __name__ == "__main__":
    main()
