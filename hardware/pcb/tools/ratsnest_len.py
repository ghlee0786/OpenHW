"""배치 품질 지표: 넷마다 패드 좌표의 최소 신장 트리(유클리드) 길이 합 (mm). GND는 면으로 잇기 때문에 따로 표시한다.

사용: <KiCad>/bin/python.exe ratsnest_len.py <board.kicad_pcb> [...]
"""
import math
import sys

import pcbnew


def mst(pts):
    if len(pts) < 2:
        return 0.0
    used, total = {0}, 0.0
    dist = {i: math.dist(pts[0], pts[i]) for i in range(1, len(pts))}
    while dist:
        j = min(dist, key=dist.get)
        total += dist.pop(j)
        used.add(j)
        for k in dist:
            dist[k] = min(dist[k], math.dist(pts[j], pts[k]))
    return total


for path in sys.argv[1:]:
    b = pcbnew.LoadBoard(path)
    nets = {}
    for fp in list(b.GetFootprints()):
        for p in fp.Pads():
            n = p.GetNetname()
            if n and not n.startswith("unconnected"):
                q = p.GetPosition()
                nets.setdefault(n, []).append((pcbnew.ToMM(q.x), pcbnew.ToMM(q.y)))
    gnd = sum(mst(v) for k, v in nets.items() if k.endswith("GND"))
    sig = sum(mst(v) for k, v in nets.items() if not k.endswith("GND"))
    print(f"{path}: 신호·전원 넷 {sig:8.1f} mm · GND {gnd:8.1f} mm · 넷 {len(nets)}")
