"""P-005 전면: 저속 넷만 다시 깐다 (시스템 파이썬, 보드는 바꾸지 않음). O-105 A — 고속 · 전원 굵은 선 · IR LED 넷은 그대로(잠금).

근거: 저속 트랙을 모두 걷은 판에서는 선폭 0.15 로 갇히는 패드가 없다(trap 진단) → 막힘은 배치가 아니라 배선 순서.
순서
 1) 잠금 아닌 넷(P5_LOCK 밖)의 트랙 · 비아를 모두 걷는다. GND 는 잠금(패드 비아 · 짧은 선 유지).
 2) GND 섬 패드(인자로 준 ref.num 목록)마다 그 층으로 닿는 가장 가까운 자리에 GND 비아(+짧은 선)를 먼저 놓는다.
 3) 넷을 '가장 좁게 갇힌 패드의 닿는 넓이'가 작은 순으로 잇는다(p005_route.route_net). 폭 = 지금 그 넷의 가장 굵은 폭 → 0.2 → 0.15.
 4) 실패한 넷은 이웃 넷 하나(둘)를 뜯고 다시 깔기(뜯은 넷이 더 끊기지 않을 때만).
사용: python p005_reroute.py <geom-all.json> <out.json> [GND 패드 ref.num ...]
출력: {"replace": {넷: {tracks, vias}}, "routes": [GND 더하기]} — p005_apply.py.
"""
import itertools
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p005_gnd as pg  # noqa: E402
import p005_rip as rip  # noqa: E402
import p005_route as pr  # noqa: E402
import route  # noqa: E402

LAYERS = [0, 3, 2]


def log(s):
    print(s, flush=True)


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    gnd_pads = sys.argv[3:]
    margin = float(os.environ.get("P5_MARGIN", "8"))
    cap = int(os.environ.get("P5_CAP", "3000000"))
    only = os.environ.get("P5_ONLY")  # 정규식: 이 넷만 걷고 다시 깐다(구역 한정)
    import re
    onlyre = re.compile(only) if only else None

    def rippable(n):
        return bool(n) and not rip.LOCK.fullmatch(n) and (onlyre is None or onlyre.fullmatch(n))

    all_tracks = [dict(t, layer=rip.RL[t["layer"]]) for t in geom["tracks"]]
    all_vias = [dict(v) for v in geom["vias"]]
    maxw = {}
    for t in all_tracks:
        maxw[t["net"]] = max(maxw.get(t["net"], 0), t["w"])
    tracks = [t for t in all_tracks if not rippable(t["net"])]
    vias = [v for v in all_vias if not rippable(v["net"])]
    added = []

    def build(skip=()):
        return pr.load(dict(geom, tracks=[t for t in tracks if t["net"] not in skip], vias=[v for v in vias if v["net"] not in skip]))

    def ncomp(B_, net):
        comp = pr.components(B_, net)
        return len([i for i in np.unique(comp[comp > 0]) if (comp[[0, 2, 3]] == i).any()])

    B = build()
    nets = sorted({p["net"] for p in B.pads if rippable(p["net"]) and p["net"] in B.netid})
    nets = [n for n in nets if sum(1 for p in B.pads if p["net"] == n) >= 2]

    def save(final=False):
        rep = {n: {"tracks": [t for t in tracks if t["net"] == n], "vias": [v for v in vias if v["net"] == n]} for n in nets}
        json.dump({"replace": rep, "routes": added, "final": final}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    # 2) GND 섬 패드 비아 먼저
    for ref in gnd_pads:
        r_, num = ref.split(".")
        p = next((q for q in B.pads if q["ref"] == r_ and q["num"] == num), None)
        if not p or p["net"] != "/GND":
            log(f"GND {ref}: 패드 없음")
            continue
        ln = next(iter(p["polys"]))
        o = {"layer": ln, "outline": p["polys"][ln][0], "holes": []}
        r = pg.place(B, o)
        if r:
            tr, via = r
            tracks.extend(dict(t, net="/GND") for t in tr)
            vias.append(dict(via, net="/GND"))
            added.append({"net": "/GND", "ok": True, "pad": ref, "tracks": tr, "vias": [via]})
            log(f"GND {ref}: 트랙 {len(tr)} + 비아 @ {via['pos']}")
        else:
            log(f"GND {ref}: 자리 없음")
    save()

    # 3) 갇힌 정도 순
    B = build()
    win = (0, B.ny - 1, 0, B.nx - 1)
    score = {}
    for n in nets:
        passable, viaok = B.free_maps(win, {B.netid[n]}, 0.075, 0.325, LAYERS)
        best = None
        for p in B.pads:
            if p["net"] != n:
                continue
            sm = {L: np.zeros((B.ny, B.nx), bool) for L in LAYERS}
            for ln, polys in p["polys"].items():
                L = pr.LMAP[ln]
                if L in sm:
                    for poly in polys:
                        B.raster_poly_mask(sm[L], poly)
            reg = pr.reach(B, sm, passable, np.zeros_like(viaok), LAYERS)  # 비아 없이 그 층에서 닿는 넓이
            a = sum(int(reg[L].sum()) for L in reg)
            best = a if best is None else min(best, a)
        score[n] = best
    order = sorted(nets, key=lambda n: score[n])
    log("순서: " + ", ".join(f"{n.lstrip('/')}({score[n]})" for n in order))

    def widths(n):
        ws = [maxw.get(n, 0.2)] if maxw.get(n, 0.2) > 0.2 else []
        return ws + [0.2, 0.15]

    failed = []
    for n in order:
        os.environ["P5_WIDTHS"] = ",".join(str(w) for w in widths(n))
        pr.BLOCKERS.clear()
        ok, tr, vi = pr.route_net(B, n, margin, cap, LAYERS, lambda s: None)
        tracks.extend(dict(t, net=n) for t in tr)
        vias.extend(dict(v, net=n) for v in vi)
        log(f"{n}: {'이음' if ok else '실패(덩어리 ' + str(ncomp(B, n)) + ')'} · 트랙 {len(tr)} · 비아 {len(vi)}")
        if not ok:
            failed.append((n, dict(pr.BLOCKERS)))
        save()

    # 4) 실패 넷: 이웃 뜯고 다시 깔기
    left = []
    for n, blk in failed:
        base_n = ncomp(build(), n)
        cands = [k for k, _ in sorted(blk.items(), key=lambda kv: -kv[1]) if k.startswith("/") and rippable(k) and k != n][:6]
        log(f"{n}: 덩어리 {base_n} — 뜯을 후보 {cands}")
        done = False
        for k in (1, 2):
            for combo in itertools.combinations(cands, k):
                base_x = {x: ncomp(build(), x) for x in combo}
                Bc = build(skip=set(combo))
                os.environ["P5_WIDTHS"] = ",".join(str(w) for w in widths(n))
                ok1, t1, v1 = pr.route_net(Bc, n, margin, cap, LAYERS, lambda s: None)
                n1 = ncomp(Bc, n)
                if n1 >= base_n:
                    continue
                res, good = [], True
                for x in combo:
                    os.environ["P5_WIDTHS"] = ",".join(str(w) for w in widths(x))
                    ok2, t2, v2 = pr.route_net(Bc, x, margin, cap, LAYERS, lambda s: None)
                    if not ok2 and ncomp(Bc, x) > base_x[x]:
                        good = False
                        break
                    res.append((x, t2, v2))
                if not good:
                    continue
                tracks.extend(dict(t, net=n) for t in t1)
                vias.extend(dict(v, net=n) for v in v1)
                for x, t2, v2 in res:
                    tracks[:] = [t for t in tracks if t["net"] != x] + [dict(t, net=x) for t in t2]
                    vias[:] = [v for v in vias if v["net"] != x] + [dict(v, net=x) for v in v2]
                log(f"{n}: {combo} 뜯고 다시 깔아 덩어리 {base_n}→{n1}")
                base_n = n1
                save()
                done = n1 <= 1
                if done:
                    break
            if done:
                break
        if not done:
            left.append(n)
    Bf = build()
    tot = {n: ncomp(Bf, n) for n in nets}
    log(f"남은 넷 {[(n, c) for n, c in tot.items() if c > 1]} · 미연결 합 {sum(c - 1 for c in tot.values())}")
    save(final=True)


if __name__ == "__main__":
    main()
