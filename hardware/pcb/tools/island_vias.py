"""G-002 손 마무리 보조 (KiCad pcbnew, 보드는 바꾸지 않음): GND 면 섬(다른 층과 이어지지 않은 채움 조각)마다 이음 비아 자리를 찾는다.

섬 = AUTO_GND_* 채움 조각 중 그 안에 GND 비아도 GND 관통 패드도 없는 것.
자리 = 섬 안 0.1 격자 점 중, 4층 모두에서 GND 채움 안쪽(채움 가장자리에서 비아 반지름 + 0.05 이상)인 첫 점
      → 비아 둘레가 모든 층에서 GND 구리라 다른 넷과 간격 문제가 없다.
출력: JSON [{layer, at:[x,y]} | {layer, none:true, bbox}] — GUI(IPC)에서 add_via 로 넣는다.
사용: <KiCad>/bin/python.exe island_vias.py <board.kicad_pcb> <out.json>
"""
import json
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM
VIA_R = 0.325


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    zones = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetNetname() == "/GND"]
    fills = {}
    for z in zones:
        for lid in z.GetLayerSet().Seq():
            ps = z.GetFilledPolysList(lid)
            if ps is None or ps.OutlineCount() == 0:
                continue
            fills.setdefault(lid, pcbnew.SHAPE_POLY_SET()).Append(ps)
    links = [v.GetPosition() for v in b.GetTracks() if v.GetClass() == "PCB_VIA" and v.GetNetname() == "/GND"]
    links += [p.GetPosition() for fp in b.GetFootprints() for p in fp.Pads()
              if p.GetNetname() == "/GND" and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH]
    out = []
    for lid, ps in fills.items():
        for k in range(ps.OutlineCount()):
            one = pcbnew.SHAPE_POLY_SET()
            one.AddOutline(ps.Outline(k))
            if any(one.Contains(q) for q in links):
                continue
            bb = one.BBox()
            hit = None
            x = bb.GetLeft()
            while x <= bb.GetRight() and not hit:
                y = bb.GetTop()
                while y <= bb.GetBottom() and not hit:
                    q = pcbnew.VECTOR2I(int(x), int(y))
                    if one.Contains(q) and all(f.Contains(q) and f.SquaredDistance(q, True) >= MM(VIA_R + 0.05) ** 2
                                               for f in fills.values()) if False else _ok(q, one, fills):
                        hit = q
                    y += MM(0.1)
                x += MM(0.1)
            name = b.GetLayerName(lid)
            if hit:
                out.append({"layer": name, "at": [round(TO(hit.x), 3), round(TO(hit.y), 3)]})
            else:
                out.append({"layer": name, "none": True,
                            "bbox": [round(TO(v), 3) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())]})
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1)
    print(f"섬 {len(out)} · 자리 찾음 {sum(1 for o in out if 'at' in o)}")


def _ok(q, one, fills):
    """점 q 가 섬 안이고, 4층 모두의 GND 채움 안에서 가장자리와 비아 반지름 + 0.05 이상 떨어졌는가.
    (SHAPE_POLY_SET.SquaredDistance 의 outline-only 는 지원되지 않아, 반지름 둘레 8점이 모두 채움 안인지로 본다)"""
    if not one.Contains(q):
        return False
    r = MM(VIA_R + 0.05)
    ring = [pcbnew.VECTOR2I(q.x + int(r * c), q.y + int(r * s)) for c, s in
            ((1, 0), (-1, 0), (0, 1), (0, -1), (0.707, 0.707), (-0.707, 0.707), (0.707, -0.707), (-0.707, -0.707))]
    return all(f.Contains(q) and all(f.Contains(p) for p in ring) for f in fills.values())


if __name__ == "__main__":
    main()
