"""P-005 전면: 한 넷의 트랙을 넓힐 수 있는 구간만 넓힌다 (시스템 파이썬, 보드는 바꾸지 않음).
review V-006a 권고: /CORE_3V3 0.30 은 IPC-2152 여유 3% → 자리가 되는 구간은 0.35 이상.
판정 = 배선기 간격 지도(다른 넷 구리와 0.16 + 반폭 + 0.05, 고속 둘레 0.30, 금지 영역)에서 그 구간 중심선 칸이 모두 통과.
사용: python p005_widen.py <geom-all.json> <out.json> <넷> <새 폭 mm>   출력: {"replace": {넷: …}} — p005_apply.py
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p005_rip as rip  # noqa: E402
import p005_route as pr  # noqa: E402
import route  # noqa: E402


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    net, w = sys.argv[3], float(sys.argv[4])
    B = pr.load(geom)
    win = (0, B.ny - 1, 0, B.nx - 1)
    passable, _ = B.free_maps(win, {B.netid[net]}, w / 2, 0.325, [0, 3, 2])
    tr = [dict(t, layer=rip.RL[t["layer"]]) for t in geom["tracks"] if t["net"] == net]
    vi = [v for v in geom["vias"] if v["net"] == net]
    n = keep = 0
    length = wide = 0.0
    for t in tr:
        L = pr.LMAP[t["layer"]]
        d = math.dist(t["a"], t["b"])
        length += d
        if t["w"] >= w - 1e-6:
            wide += d
            continue
        k = max(1, int(d / (route.G / 2)))
        ok = True
        for i in range(k + 1):
            x = t["a"][0] + (t["b"][0] - t["a"][0]) * i / k
            y = t["a"][1] + (t["b"][1] - t["a"][1]) * i / k
            r, c = B.cell(x, y)
            if not passable[L][r, c]:
                ok = False
                break
        if ok:
            t["w"] = w
            n += 1
            wide += d
        else:
            keep += 1
    json.dump({"replace": {net: {"tracks": tr, "vias": vi}}}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{net}: 넓힘 {n} · 그대로 {keep} · 길이 {length:.1f}mm 중 {w}mm 이상 {wide:.1f}mm ({100 * wide / max(length, 1e-9):.0f}%)")


if __name__ == "__main__":
    main()
