"""P-005 전면: GND 섬마다 이음 비아(필요하면 짧은 GND 트랙)를 계산한다 (시스템 파이썬, 보드는 바꾸지 않음).

섬 외곽 = p005_islands.py JSON. 자리 조건 = 배선기 간격 지도(route.Board.free_maps 의 viaok: 4층 모두 다른 넷 구리와 0.16 + 여유,
구멍 · 금지 영역 · 외곽 · 자기 SMD 패드 위 금지). In1 은 GND 면이라 비아만 닿으면 이어진다.
 1) 섬 안(가장자리에서 비아 반지름 + 0.05 안쪽)에 자리가 있으면 비아만.
 2) 없으면 섬 구리에서 그 층으로 닿는 가장 가까운 자리까지 GND 트랙(0.2, 안 되면 0.15) + 비아.
사용: python p005_gnd.py <geom-all.json> <islands.json> <out.json>   출력은 apply_assist.py 형식(routes).
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p005_route as pr  # noqa: E402
import route  # noqa: E402

G = route.G
NET = "/GND"


def island_mask(B, o):
    m = np.zeros((B.ny, B.nx), bool)
    B.raster_poly_mask(m, o["outline"])
    for h in o["holes"]:
        hm = np.zeros((B.ny, B.nx), bool)
        B.raster_poly_mask(hm, h)
        m &= ~hm
    return m


def place(B, o):
    """섬 o 에 비아(+트랙)를 놓는다. 성공하면 (tracks, via) — B 에도 더한다. 실패하면 None."""
    own = {B.netid[NET]}
    vt = route.VIA
    L = pr.LMAP[o["layer"]]
    m = island_mask(B, o)
    rs, cs = np.nonzero(m)
    if not len(rs):
        return None
    win = B.window([(rs.min(), cs.min()), (rs.max(), cs.max())], 3.0)
    r0, r1, c0, c1 = win
    sl = (slice(r0, r1 + 1), slice(c0, c1 + 1))
    got = None
    for w in (0.2, 0.15):
        passable, viaok = B.free_maps(win, own, w / 2, vt["dia"] / 2, [L])
        inner = ndimage.binary_erosion(m[sl], iterations=int((vt["dia"] / 2 + 0.05) / G) + 1)
        cand = inner & viaok
        if cand.any():
            d = ndimage.distance_transform_edt(cand)  # 다른 구리에서 가장 먼 자리
            r, c = np.unravel_index(int(np.argmax(d)), d.shape)
            got = (w, (int(r) + r0, int(c) + c0), None)
            break
        # 섬 구리(패드 포함)에서 그 층으로 닿는 구역의 비아 자리
        smask = {L: m[sl] | ((B.occ[L][sl] == B.netid[NET]) & ndimage.binary_dilation(m[sl], iterations=2))}
        pas = {L: passable[L] | m[sl]}
        reg = pr.reach(B, smask, pas, np.zeros_like(viaok), [L])[L]
        cand = reg & viaok & pas[L]
        if not cand.any():
            continue
        crs, ccs = np.nonzero(cand)
        pr_, pc_ = np.nonzero(m[sl])
        k = int(np.argmin((crs - pr_.mean()) ** 2 + (ccs - pc_.mean()) ** 2))
        tgt = (L, int(crs[k]), int(ccs[k]))
        starts = {(L, int(r), int(c)) for r, c in zip(*np.nonzero(smask[L] & pas[L]))}
        path = B.astar(win, starts, {tgt}, pas, np.zeros_like(viaok), [L], cap=400000)
        if path:
            got = (w, (tgt[1] + r0, tgt[2] + c0), path)
            break
    if not got:
        return None
    w, (vr, vc), path = got
    pos = tuple(float(v) for v in B.xy(vr, vc))
    tr = []
    if path:
        for L_, cells in B.corners([(L_, r + r0, c + c0, d) for L_, r, c, d in path]):
            pts = [tuple(float(v) for v in B.xy(*p)) for p in cells]
            for a, b_ in zip(pts[:-1], pts[1:]):
                B.add_track(NET, L_, a, b_, w)
                tr.append({"layer": route.LAYERS[L_], "a": list(a), "b": list(b_), "w": w})
    B.add_via(NET, pos, vt)
    return tr, {"pos": list(pos), "dia": vt["dia"], "drill": vt["drill"]}


def main():
    import itertools
    import p005_rip as rip
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    isl = json.load(open(sys.argv[2], encoding="utf-8"))
    tracks = [dict(t, layer=rip.RL[t["layer"]]) for t in geom["tracks"]]
    vias = [dict(v) for v in geom["vias"]]
    touched, added = set(), []
    margin, cap = float(os.environ.get("P5_MARGIN", "8")), int(os.environ.get("P5_CAP", "3000000"))

    def build(skip=()):
        return pr.load(dict(geom, tracks=[t for t in tracks if t["net"] not in skip], vias=[v for v in vias if v["net"] not in skip]))

    def ncomp(B_, net):
        comp = pr.components(B_, net)
        return len([i for i in np.unique(comp[comp > 0]) if (comp[[0, 2, 3]] == i).any()])

    def save():
        rep = {n: {"tracks": [t for t in tracks if t["net"] == n], "vias": [v for v in vias if v["net"] == n]} for n in sorted(touched)}
        json.dump({"replace": rep, "routes": added}, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def keep(tr, via, n):
        tracks.extend(dict(t, net=NET) for t in tr)
        vias.append(dict(via, net=NET))
        added.append({"net": NET, "ok": True, "island": n, "tracks": tr, "vias": [via]})

    left = []
    for n, o in enumerate(isl):
        B = build()
        r = place(B, o)
        if r:
            keep(*r, n)
            print(f"섬 {n} {o['layer']} {o['pads']}: 바로 — 트랙 {len(r[0])} + 비아 @ {r[1]['pos']}", flush=True)
            save()
            continue
        # 뜯을 후보: 섬 둘레 0.8mm 안(모든 층)의 잠금 아닌 넷 트랙 · 비아
        m = island_mask(B, o)
        ring = ndimage.binary_dilation(m, iterations=int(0.8 / G))
        names = {v: k for k, v in B.netid.items()}
        cnt = {}
        for L in range(4):
            ids, c = np.unique(B.occ[L][ring & B.trk[L]], return_counts=True)
            for i_, c_ in zip(ids, c):
                nm = names.get(int(i_))
                if nm and nm != NET and not rip.LOCK.fullmatch(nm):
                    cnt[nm] = cnt.get(nm, 0) + int(c_)
        cands = [k for k, _ in sorted(cnt.items(), key=lambda kv: -kv[1])][:6]
        if os.environ.get("P5_CANDS"):
            cands = os.environ["P5_CANDS"].split(",")
        print(f"섬 {n} {o['layer']} {o['pads']}: 막힘 — 뜯을 후보 {cands}", flush=True)
        done = False
        for k in (1, 2):
            for combo in itertools.combinations(cands, k):
                base = {x: ncomp(build(), x) for x in combo}
                B = build(skip=set(combo))
                r = place(B, o)
                if not r:
                    continue
                res, good = [], True
                for x in combo:
                    ok2, t2, v2 = pr.route_net(B, x, margin, cap, [0, 3, 2], lambda s_: None)
                    if not ok2 and ncomp(B, x) > base[x]:
                        good = False
                        break
                    res.append((x, t2, v2))
                if not good:
                    print(f"   {combo}: 비아 자리 있음, 다시 못 깖", flush=True)
                    continue
                for x, t2, v2 in res:
                    tracks[:] = [t for t in tracks if t["net"] != x] + [dict(t, net=x) for t in t2]
                    vias[:] = [v for v in vias if v["net"] != x] + [dict(v, net=x) for v in v2]
                    touched.add(x)
                keep(*r, n)
                print(f"섬 {n}: {combo} 뜯고 다시 깔아 비아 @ {r[1]['pos']}", flush=True)
                save()
                done = True
                break
            if done:
                break
        if not done:
            left.append(n)
            print(f"섬 {n}: 실패", flush=True)
    save()
    print(f"섬 {len(isl)} · 남음 {left}")


if __name__ == "__main__":
    main()
