"""배선기 3단계 (KiCad pcbnew): route.py 결과를 보드에 넣고 GND 면을 채운다.

- 잠기지 않은 트랙·비아는 지운다(스크립트 배선을 다시 돌릴 수 있게). 잠긴 것은 둔다.
- GND 면: F.Cu·In1.Cu·In2.Cu·B.Cu 전체(외곽 안), 간격 0.2, 최소 폭 0.2, 열 완화 0.3/0.3.
사용: <KiCad>/bin/python.exe route_apply.py <board.kicad_pcb> <routes.json>
"""
import json
import sys

import pcbnew

MM = pcbnew.FromMM
CU = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}


def V(p):
    return pcbnew.VECTOR2I(MM(p[0]), MM(p[1]))


def main():
    path, rpath = sys.argv[1], sys.argv[2]
    b = pcbnew.LoadBoard(path)
    r = json.load(open(rpath, encoding="utf-8"))
    for t in list(b.GetTracks()):
        if not t.IsLocked():
            b.Delete(t)
    for z in list(b.Zones()):
        if (not z.GetIsRuleArea() and z.GetZoneName().startswith("AUTO_GND")) or (z.GetIsRuleArea() and z.GetZoneName() == "DP_BRK"):
            b.Delete(z)
    for a in r.get("areas", []):  # 고속 탈출 구역(제한 없음, DRU dp_breakout_* 가 intersectsArea('DP_BRK') 로 쓴다)
        z = pcbnew.ZONE(b)
        z.SetIsRuleArea(True)
        z.SetZoneName(a["name"])
        z.SetLayer(CU[a["layer"]])
        for f in (z.SetDoNotAllowTracks, z.SetDoNotAllowVias, z.SetDoNotAllowPads, z.SetDoNotAllowZoneFills, z.SetDoNotAllowFootprints):
            f(False)
        x0, y0, x1, y1 = a["rect"]
        ol = z.Outline()
        ol.NewOutline()
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(MM(x), MM(y))
        b.Add(z)
    nets = {n: b.FindNet(n) for n in {t["net"] for t in r["tracks"]} | {v["net"] for v in r["vias"]} | {"/GND"}}
    for t in r["tracks"]:
        s = pcbnew.PCB_TRACK(b)
        s.SetStart(V(t["a"]))
        s.SetEnd(V(t["b"]))
        s.SetWidth(MM(t["w"]))
        s.SetLayer(CU[t["layer"]])
        s.SetNet(nets[t["net"]])
        b.Add(s)
    for v in r["vias"]:
        s = pcbnew.PCB_VIA(b)
        s.SetPosition(V(v["pos"]))
        s.SetWidth(MM(v["dia"]))
        s.SetDrill(MM(v["drill"]))
        s.SetViaType(pcbnew.VIATYPE_THROUGH)
        s.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        s.SetNet(nets[v["net"]])
        b.Add(s)
    # 열 구리(thermal.py): 넷 영역(우선순위 1, 패드 직결)과 마스크 개구
    for d in list(b.GetDrawings()):
        if d.GetLayer() in (pcbnew.F_Mask, pcbnew.B_Mask) and d.GetShape() == pcbnew.SHAPE_T_RECT:
            b.Delete(d)
    for z in list(b.Zones()):
        if not z.GetIsRuleArea() and z.GetZoneName().startswith("THERMAL_"):
            b.Delete(z)
    for k, zd in enumerate(r.get("zones", [])):
        net = b.FindNet(zd["net"])
        z = pcbnew.ZONE(b)
        z.SetLayer(CU[zd["layer"]])
        z.SetNet(net)
        z.SetZoneName(f"THERMAL_{k}")
        z.SetAssignedPriority(zd["priority"])
        z.SetLocalClearance(MM(0.2))
        z.SetMinThickness(MM(0.2))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)
        x0, y0, x1, y1 = zd["rect"]
        ol = z.Outline()
        ol.NewOutline()
        for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
            ol.Append(MM(x), MM(y))
        b.Add(z)
    for m in r.get("masks", []):
        s = pcbnew.PCB_SHAPE(b, pcbnew.SHAPE_T_RECT)
        x0, y0, x1, y1 = m["rect"]
        s.SetStart(V((x0, y0)))
        s.SetEnd(V((x1, y1)))
        s.SetFilled(True)
        s.SetWidth(0)
        s.SetLayer(pcbnew.B_Mask if m["layer"] == "B.Mask" else pcbnew.F_Mask)
        b.Add(s)
    bb = b.GetBoardEdgesBoundingBox()
    for name, lid in CU.items():
        z = pcbnew.ZONE(b)
        z.SetLayer(lid)
        z.SetNet(nets["/GND"])
        z.SetZoneName(f"AUTO_GND_{name}")
        z.SetLocalClearance(MM(0.2))
        z.SetMinThickness(MM(0.2))
        z.SetThermalReliefGap(MM(0.3))
        z.SetThermalReliefSpokeWidth(MM(0.3))
        # THT 패드만 열 완화, SMD 패드는 직결 — 외층 열 완화 살이 트랙에 막혀 1개만 남던 문제(starved_thermal, P-003) 해소.
        # 리플로 조립에서 흔한 설정. 0402 툼스톤 위험은 조립 검사(AOI)로 본다.
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THT_THERMAL)
        z.SetIslandRemovalMode(pcbnew.ISLAND_REMOVAL_MODE_ALWAYS)
        ol = z.Outline()
        ol.NewOutline()
        for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()), (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
            ol.Append(x, y)
        b.Add(z)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(path)
    print(f"트랙 {len(r['tracks'])} · 비아 {len(r['vias'])} · GND 면 4 · 배선 실패 {len(r['failed'])}")


if __name__ == "__main__":
    main()
