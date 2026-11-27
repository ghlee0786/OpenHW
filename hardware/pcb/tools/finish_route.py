"""남은 미연결 마무리 (시스템 파이썬 + scipy, O-105 A/C): 지금 보드의 배선 전부를 장애물로 두고, 넷마다 끊어진 구리 덩어리를 잇는다.
보드는 바꾸지 않는다 — 결과 JSON 을 apply_assist.py 가 넣는다. 규칙은 배선기(route.py free_maps)와 같다.

assist_route.py(창 안 A*, 연결당 수 분)와 다른 점:
  - 덩어리 = 그 넷 구리(패드 · 트랙 · 비아)의 래스터 연결 성분. DRC 미연결 항목이 아니라 덩어리 ↔ 덩어리 최단 경로를 찾는다.
  - 탐색 = 격자 그래프 전체에 scipy dijkstra (여러 출발점 한 번에, 연결당 수 초) — 경로가 있으면 반드시 찾고, 없으면 '경로 없음'이 확정이다.
  - 같은 넷 비아 원 안에는 꺾임점을 두지 않는다(track_not_centered_on_via): 비아는 중심에서 8방향 직선으로만 드나든다.
사용: python finish_route.py <geom-all.json> <out.json> [넷 정규식]      (환경: FIN_IN1=1 이면 In1 짧은 점프 허용 — O-105 C)
"""
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route  # noqa: E402

G = route.G
LMAP = {"F.Cu": 0, "In1.Cu": 1, "GND": 1, "In2.Cu": 2, "GND_PWR": 2, "B.Cu": 3}
MINW = {"PWR_12V_IN": 0.8, "PWR_12V_IR": 0.55, "PWR_5V": 0.6, "PWR_LOGIC": 0.3}
IN1 = os.environ.get("FIN_IN1") == "1"
VIA_COST = 30.0
DIRS = ((0, 1), (1, 0), (1, 1), (1, -1))


def clusters(B, net):
    nid = B.netid[net]
    lab, off = [], 0
    for L in range(4):
        l, n = ndimage.label(B.occ[L] == nid, structure=np.ones((3, 3), int))
        l[l > 0] += off
        lab.append(l)
        off += n
    parent = list(range(off + 1))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    pts = [v["pos"] for v in B.vias if v["net"] == net] + [p["pos"] for p in B.pads if p["net"] == net and p["drill"]]
    for pos in pts:
        r, c = B.cell(*pos)
        ids = [int(lab[L][r, c]) for L in range(4) if lab[L][r, c] > 0]
        for x in ids[1:]:
            parent[find(x)] = find(ids[0])
    root = np.array([find(i) for i in range(off + 1)])
    lab = [root[l] for l in lab]
    padc = {}
    for p in B.pads:
        if p["net"] != net:
            continue
        r, c = B.cell(*p["pos"])
        cid = next((int(lab[route.LAYERS.index(ln)][r, c]) for ln in p["layers"] if lab[route.LAYERS.index(ln)][r, c] > 0), 0)
        if cid:
            padc.setdefault(cid, []).append(p)
    return lab, padc


def set_disc(arr, r, c, k, val):
    H, W = arr.shape
    a0, a1, b0, b1 = max(r - k, 0), min(r + k, H - 1), max(c - k, 0), min(c + k, W - 1)
    yy, xx = np.ogrid[a0 - r:a1 - r + 1, b0 - c:b1 - c + 1]
    arr[a0:a1 + 1, b0:b1 + 1][yy * yy + xx * xx <= k * k] = val


def connect(B, net, lab, A, others, w, vtype, layers, margin):
    nid = B.netid[net]
    lcost = {0: 1.0, 3: 1.0, 2: 1.6, 1: 6.0}
    rs, cs = [], []
    tmask = [np.isin(lab[L], others) for L in range(4)]
    for L in range(4):
        for m in (lab[L] == A, tmask[L]):
            r_, c_ = np.nonzero(m)
            if len(r_):
                rs += [r_.min(), r_.max()]
                cs += [c_.min(), c_.max()]
    k = int(margin / G)
    r0, r1, c0, c1 = max(min(rs) - k, 0), min(max(rs) + k, B.ny - 1), max(min(cs) - k, 0), min(max(cs) + k, B.nx - 1)
    win = (r0, r1, c0, c1)
    passable, viaok = B.free_maps(win, {nid}, w / 2, vtype["dia"] / 2, layers)
    H, W = viaok.shape
    sl = (slice(r0, r1 + 1), slice(c0, c1 + 1))
    if IN1 and 1 in layers:
        # O-105 C (D-003 #54): In1(GND) 짧은 점프 — 윗면 고속 쌍(CSI/MDI/USB) 투영(트랙 가장자리 0.6mm 안) 금지, 층 비용 6배로 길이 최소
        hs0 = B.trk[0][sl] & np.isin(B.occ[0][sl], list(B.hs_ids))
        if hs0.any():
            passable[1] &= ndimage.distance_transform_edt(~hs0) * G >= 0.6 + w / 2
    orig = {L: passable[L].copy() for L in layers}
    own_vias = []
    for v in B.vias:
        if v["net"] != net:
            continue
        r, c = B.cell(*v["pos"])
        if r0 <= r <= r1 and c0 <= c <= c1:
            kk = int(math.ceil((v["dia"] / 2 + 0.03) / G))
            own_vias.append((r - r0, c - c0, kk))
            for L in layers:
                set_disc(passable[L], r - r0, c - c0, kk, False)
    nL = len(layers)
    idx = np.arange(H * W, dtype=np.int64).reshape(H, W)
    src_, dst_, wt_ = [], [], []
    for li, L in enumerate(layers):
        p = passable[L]
        base = li * H * W
        for dr, dc in DIRS:
            if dc >= 0:
                a = (slice(0, H - dr), slice(0, W - dc))
                b = (slice(dr, H), slice(dc, W))
            else:
                a = (slice(0, H - dr), slice(1, W))
                b = (slice(dr, H), slice(0, W - 1))
            m = p[a] & p[b]
            if dr and dc:
                # 대각 이동: 두 직교 이웃도 지날 수 있어야 (모서리 스침 방지)
                n1 = (slice(dr, H), a[1])
                n2 = (a[0], b[1])
                m = m & p[n1] & p[n2]
            s = idx[a][m] + base
            d = idx[b][m] + base
            cst = lcost[L] * (1.41421356 if dr and dc else 1.0)
            src_ += [s, d]
            dst_ += [d, s]
            wt_ += [np.full(len(s), cst), np.full(len(s), cst)]
    for i in range(nL):
        for j in range(i + 1, nL):
            m = viaok & passable[layers[i]] & passable[layers[j]]
            s = idx[m] + i * H * W
            d = idx[m] + j * H * W
            src_ += [s, d]
            dst_ += [d, s]
            wt_ += [np.full(len(s), VIA_COST), np.full(len(s), VIA_COST)]
    # 같은 넷 비아: 중심 ↔ 원 밖 고리 칸(8방향 직선, 길 전체가 간격을 지킬 때만), 층 사이는 공짜
    for r, c, kk in own_vias:
        for li, L in enumerate(layers):
            for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                rr, cc = r + dr * (kk + 1), c + dc * (kk + 1)
                if not (0 <= rr < H and 0 <= cc < W) or not passable[L][rr, cc]:
                    continue
                if all(orig[L][r + dr * i, c + dc * i] for i in range(kk + 2)):
                    a_, b_ = idx[r, c] + li * H * W, idx[rr, cc] + li * H * W
                    cst = lcost[L] * (kk + 1) * (1.41421356 if dr and dc else 1.0)
                    src_ += [np.array([a_, b_])]
                    dst_ += [np.array([b_, a_])]
                    wt_ += [np.full(2, cst)]
        for i in range(nL):
            for j in range(i + 1, nL):
                a_, b_ = idx[r, c] + i * H * W, idx[r, c] + j * H * W
                src_ += [np.array([a_, b_])]
                dst_ += [np.array([b_, a_])]
                wt_ += [np.full(2, 0.01)]
    N = nL * H * W
    g = coo_matrix((np.concatenate(wt_), (np.concatenate(src_), np.concatenate(dst_))), shape=(N, N)).tocsr()

    def nodes_of(maskfn):
        out = []
        for li, L in enumerate(layers):
            m = maskfn(L)[sl] & passable[L]
            out.append(idx[m] + li * H * W)
            for r, c, kk in own_vias:
                if maskfn(L)[sl][r, c] or any(maskfn(Lx)[sl][r, c] for Lx in range(4)):
                    out.append(np.array([idx[r, c] + li * H * W]))
        return np.unique(np.concatenate(out)) if out else np.array([], np.int64)

    S = nodes_of(lambda L: lab[L] == A)
    T = nodes_of(lambda L: tmask[L])
    if not len(S) or not len(T):
        return None, "출발/도착 칸 없음(간격을 지키는 칸이 없다)"
    dist, pred, _ = dijkstra(g, directed=True, indices=S, return_predecessors=True, min_only=True)
    best = T[np.argmin(dist[T])]
    if not np.isfinite(dist[best]):
        return None, "경로 없음"
    path = [int(best)]
    while pred[path[-1]] >= 0:
        path.append(int(pred[path[-1]]))
    path.reverse()
    dec = [(layers[n // (H * W)], (n % (H * W)) // W + r0, (n % (H * W)) % W + c0) for n in path]
    centers = {(r + r0, c + c0) for r, c, _ in own_vias}
    tracks, vias = [], []
    run = [dec[0]]
    runs = []
    for a, b in zip(dec[:-1], dec[1:]):
        if a[0] != b[0]:
            runs.append(run)
            if (a[1], a[2]) not in centers:
                vias.append(B.xy(a[1], a[2]))
            run = [b]
        else:
            run.append(b)
    runs.append(run)
    for run in runs:
        L = run[0][0]
        pts = [B.xy(r, c) for _, r, c in run]
        simp = [pts[0]]
        for i in range(1, len(pts) - 1):
            (x0, y0), (x1, y1), (x2, y2) = simp[-1], pts[i], pts[i + 1]
            if abs((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)) > 1e-6:
                simp.append(pts[i])
        if len(pts) > 1:
            simp.append(pts[-1])
        for a, b in zip(simp[:-1], simp[1:]):
            tracks.append((L, a, b))
    for i, va in enumerate(vias):
        for vb in vias[i + 1:]:
            if math.dist(va, vb) < 0.85:
                return None, "새 비아 둘이 너무 가까움"
    return (tracks, vias, float(dist[best])), ""


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    pat = re.compile(sys.argv[3]) if len(sys.argv) > 3 else None
    # 참조 지정자 글자 둘레 비아 금지(SILKTXT_*)는 뺀다 — 글자는 배선 뒤 silk.py refs 가 비아를 피해 다시 놓는다(자리 없으면 Fab).
    #   (글자 금지가 보드의 21% 를 덮어 J1 둘레에 비아 자리가 0 이었다 — O-105 A 진단). 실크 선 둘레(SILK_*)는 그대로 지킨다.
    drop = "SILK" if os.environ.get("FIN_NOSILK") == "1" else "SILKTXT_"  # FIN_NOSILK=1: 실크 선 둘레도 뺀다(진단 · 뒤에 실크를 잘라야 함)
    geom["keepouts"] = [k for k in geom["keepouts"] if not k["name"].startswith(drop)]
    B = route.Board(geom)
    for t in geom["tracks"]:
        if t["net"] in B.netid:
            B.add_track(t["net"], LMAP[t["layer"]], tuple(t["a"]), tuple(t["b"]), t["w"])
    for v in geom["vias"]:
        if v["net"] in B.netid:
            B.add_via(v["net"], tuple(v["pos"]), {"dia": v["dia"], "drill": v["drill"]})
    layers = [0, 3, 2, 1] if IN1 else [0, 3, 2]
    nets = sorted((n for n in B.netid if n != "/GND" and (not pat or pat.search(n))),
                  key=lambda n: (not route.netclass(n)["name"].startswith("PWR_"), n))
    out = []
    t00 = time.time()
    for net in nets:
        nc = route.netclass(net)
        if nc["name"] in route.HS:
            continue
        widths = [nc["track_width"]]
        mw = MINW.get(nc["name"], 0.15)
        if mw < widths[0]:
            widths.append(mw)
        if nc["name"] == "PWR_5V":
            widths.append(0.3)  # 감지 · 디커플링 가지(0402 패드)와 J1 0.5 피치 핀 탈출 — 본선은 0.6 이상(R-020 RQ-17), 쓴 곳은 기록
        vtype = route.VIA_PWR if nc["name"].startswith("PWR_") and nc["name"] != "PWR_LOGIC" else route.VIA
        failed = set()
        while True:
            lab, padc = clusters(B, net)
            cids = sorted(padc, key=lambda c: len(padc[c]))
            if len(cids) <= 1:
                break
            cand = [c for c in cids if (padc[c][0]["ref"], padc[c][0]["num"]) not in failed]
            if not cand:
                break
            A = cand[0]
            others = [c for c in cids if c != A]
            rep = (padc[A][0]["ref"], padc[A][0]["num"])
            res, why = None, ""
            for w in widths:
                t0 = time.time()
                res, why = connect(B, net, lab, A, others, w, vtype, layers, 6.0)
                if res:
                    break
            name = ",".join(f"{p['ref']}.{p['num']}" for p in padc[A][:4])
            if not res:
                failed.add(rep)
                out.append({"net": net, "from": name, "ok": False, "why": why})
                print(f"실패 {net} [{name}] {why}", flush=True)
                continue
            tr, vi, cost = res
            rec = {"net": net, "from": name, "ok": True, "w": w, "tracks": [], "vias": []}
            for L, a, b in tr:
                B.add_track(net, L, a, b, w)
                rec["tracks"].append({"layer": route.LAYERS[L], "a": list(a), "b": list(b), "w": w})
            for pos in vi:
                B.add_via(net, pos, vtype)
                rec["vias"].append({"pos": list(pos), "dia": vtype["dia"], "drill": vtype["drill"]})
            out.append(rec)
            ln = sum(math.dist(t["a"], t["b"]) for t in rec["tracks"])
            lays = sorted({t["layer"] for t in rec["tracks"]})
            print(f"연결 {net} [{name}] 폭 {w} · 길이 {ln:.2f} · 비아 {len(vi)} · 층 {lays} · {time.time() - t0:.1f}s", flush=True)
    json.dump({"routes": out}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"마무리: 연결 {sum(1 for o in out if o['ok'])} · 실패 {sum(1 for o in out if not o['ok'])} · {time.time() - t00:.0f}s")


if __name__ == "__main__":
    main()
