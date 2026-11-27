"""P-005 전면: 트랙 끝이 같은 넷 비아 구리 안에 있지만 중심이 아닌 곳(track_not_centered_on_via)을 비아 중심까지 짧은 선으로 잇는다.
(KiCad pcbnew) 사용: <KiCad>/bin/python.exe p005_viafix.py <board.kicad_pcb>
"""
import math
import sys

import pcbnew

TO = pcbnew.ToMM


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    vias = [t for t in b.GetTracks() if t.GetClass() == "PCB_VIA"]
    segs = [t for t in b.GetTracks() if t.GetClass() == "PCB_TRACK"]
    n = 0
    for v in vias:
        q = v.GetPosition()
        r = v.GetWidth(pcbnew.F_Cu) / 2
        for t in segs:
            if t.GetNetCode() != v.GetNetCode():
                continue
            for e in (t.GetStart(), t.GetEnd()):
                d = math.hypot(e.x - q.x, e.y - q.y)
                if 1000 < d < r:  # 1µm 넘게 어긋나고 비아 구리 안
                    # 이미 이 끝에서 중심으로 가는 선이 있으면 건너뜀
                    if any(s.GetLayer() == t.GetLayer() and s.GetNetCode() == t.GetNetCode() and
                           {(s.GetStart().x, s.GetStart().y), (s.GetEnd().x, s.GetEnd().y)} == {(e.x, e.y), (q.x, q.y)} for s in segs):
                        continue
                    s = pcbnew.PCB_TRACK(b)
                    s.SetStart(pcbnew.VECTOR2I(e.x, e.y))
                    s.SetEnd(pcbnew.VECTOR2I(q.x, q.y))
                    s.SetWidth(t.GetWidth())
                    s.SetLayer(t.GetLayer())
                    s.SetNetCode(t.GetNetCode())
                    b.Add(s)
                    segs.append(s)
                    n += 1
                    print(f"{t.GetNetname()} {b.GetLayerName(t.GetLayer())} ({TO(e.x):.3f},{TO(e.y):.3f}) → 비아 ({TO(q.x):.3f},{TO(q.y):.3f})")
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])
    print(f"이은 끝 {n}")


if __name__ == "__main__":
    main()
