"""GND 이음 비아(트랙이 닿지 않은 GND 비아) 걷기 · 다시 깔기 (KiCad pcbnew, O-105 A).

strip: 이음 비아를 모두 지운다(손 배선 통로를 비움). 지운 자리를 JSON 으로 남긴다.
lay:   1.5mm 격자에서 4층 모두 GND 채움 안쪽(가장자리에서 반지름 + 0.05)인 자리에만 다시 깐다 — 다른 넷과 간격 문제가 없다.
사용: <KiCad>/bin/python.exe stitch.py strip|lay <board.kicad_pcb> <log.json>
"""
import json
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM


def free_vias(b):
    ends = set()
    for t in b.GetTracks():
        if t.GetClass() == "PCB_TRACK":
            ends.add((t.GetStart().x, t.GetStart().y))
            ends.add((t.GetEnd().x, t.GetEnd().y))
    pads = [p for fp in b.GetFootprints() for p in fp.Pads() if p.GetNetname() == "/GND"]
    out = []
    for v in b.GetTracks():
        if v.GetClass() != "PCB_VIA" or v.GetNetname() != "/GND" or v.IsLocked():
            continue
        q = v.GetPosition()
        if (q.x, q.y) in ends or any(p.HitTest(q) for p in pads):
            continue
        out.append(v)
    return out


def strip(b, log):
    vs = free_vias(b)
    log["removed"] = [[round(TO(v.GetPosition().x), 3), round(TO(v.GetPosition().y), 3)] for v in vs]
    for v in vs:
        b.Delete(v)


def lay(b, log):
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    fills = {}
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != "/GND":
            continue
        for lid in z.GetLayerSet().Seq():
            ps = z.GetFilledPolysList(lid)
            if ps is not None and ps.OutlineCount():
                fills.setdefault(lid, pcbnew.SHAPE_POLY_SET()).Append(ps)
    eb = b.GetBoardEdgesBoundingBox()
    r = MM(0.325 + 0.05)
    ring = [(1, 0), (-1, 0), (0, 1), (0, -1), (0.707, 0.707), (-0.707, 0.707), (0.707, -0.707), (-0.707, -0.707)]
    added = []
    x = eb.GetLeft() + MM(1.0)
    while x < eb.GetRight() - MM(1.0):
        y = eb.GetTop() + MM(1.0)
        while y < eb.GetBottom() - MM(1.0):
            q = pcbnew.VECTOR2I(int(x), int(y))
            pts = [q] + [pcbnew.VECTOR2I(q.x + int(r * c), q.y + int(r * s)) for c, s in ring]
            if len(fills) == 4 and all(all(f.Contains(p) for p in pts) for f in fills.values()):
                v = pcbnew.PCB_VIA(b)
                v.SetPosition(q)
                v.SetWidth(MM(0.65))
                v.SetDrill(MM(0.3))
                v.SetNet(b.FindNet("/GND"))
                b.Add(v)
                added.append([round(TO(q.x), 3), round(TO(q.y), 3)])
            y += MM(1.5)
        x += MM(1.5)
    log["added"] = added


def main():
    mode, path, rep = sys.argv[1], sys.argv[2], sys.argv[3]
    b = pcbnew.LoadBoard(path)
    log = {}
    (strip if mode == "strip" else lay)(b, log)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(path)
    json.dump(log, open(rep, "w", encoding="utf-8"))
    print(mode, {k: len(v) for k, v in log.items()})


if __name__ == "__main__":
    main()
