"""뜯고 다시 깔기 마무리 (시스템 파이썬 + scipy, O-105 A): 고속 쌍 · 전원 굵은 선 · IR 열 · GND 는 고정(hard),
저속 신호(Default · PWR_LOGIC 넷클래스)의 기존 트랙 · 비아는 '뜯을 수 있음'(soft)으로 두고 끊어진 덩어리를 잇는다.

- 경로 탐색은 hard 구리만 장애물로 본 격자 전체 dijkstra. soft 구리의 간격 띠를 지나면 벌점(넷이 뜯긴 횟수만큼 커짐) —
  꼭 필요할 때만 남의 저속선을 뜯는다. 뜯긴 넷은 다음 바퀴에 다시 잇는다.
- 보드는 바꾸지 않는다. 결과 JSON(soft 넷 전체의 새 트랙 · 비아 + 전원 넷에 더한 것)을 apply_rr.py 가 넣는다.
사용: python rr_finish.py <geom-all.json> <out.json> [분 상한=12]
"""
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route  # noqa: E402
from finish_route import DIRS, LMAP, MINW, VIA_COST, set_disc  # noqa: E402

G, CLR, EPS = route.G, route.CLR, route.EPS
SOFT_CLASSES = ("Default", "PWR_LOGIC")
IR_NETS = {"/IRA_SET", "/IRA_M", "/IRB_SET", "/IRB_M"}
BASE_PEN = 15.0
IN1 = __import__("os").environ.get("RR_IN1") == "1"   # O-105 C (D-003 #54): In1(GND) 짧은 저속 점프 — 윗면 고속 쌍 투영 밖, 비용 4배로 길이 최소
LAYERS = [0, 3, 2, 1] if IN1 else [0, 3, 2]
LCOST = {0: 1.0, 3: 1.0, 2: 1.6, 1: 4.0}


POWER_SOFT = __import__("os").environ.get("RR_POWER_SOFT") == "1"  # 전원 굵은 선도 뜯을 수 있게(벌점 6배) — 핀 출구를 막는 곳만 뜯긴다
HIST = 6.0
_h = __import__("os").environ.get("RR_HARD")  # 뜯지 않을 넷(정규식) — 예: USB-C 0.5 피치 VBUS · CC 탈출
HARD_RE = __import__("re").compile(_h) if _h else None


def is_soft(net):
    if net == "/GND" or net in IR_NETS or (HARD_RE and HARD_RE.search(net)):
        return False
    name = route.netclass(net)["name"]
    return name in SOFT_CLASSES or (POWER_SOFT and name not in route.HS)


def pen_of(S, net):
    f = 6.0 if route.netclass(net)["name"] not in SOFT_CLASSES else 1.0
    return BASE_PEN * f * (1 + S.rip.get(net, 0)) ** 2


def paint(arr, Bh, a, b, rad, val):
    ra, ca = Bh.cell(*a)
    rb, cb = Bh.cell(*b)
    k = int(math.ceil(rad / G)) + 1
    r0, r1 = max(min(ra, rb) - k, 0), min(max(ra, rb) + k, Bh.ny - 1)
    c0, c1 = max(min(ca, cb) - k, 0), min(max(ca, cb) + k, Bh.nx - 1)
    if r1 < r0 or c1 < c0:
        return
    ys, xs = np.mgrid[r0:r1 + 1, c0:c1 + 1].astype(float)
    dr, dc = rb - ra, cb - ca
    L2 = dr * dr + dc * dc
    t = np.clip(((ys - ra) * dr + (xs - ca) * dc) / L2, 0, 1) if L2 else 0.0
    m = (ys - ra - t * dr) ** 2 + (xs - ca - t * dc) ** 2 <= (rad / G) ** 2
    sub = arr[r0:r1 + 1, c0:c1 + 1]
    if arr.dtype == bool:
        sub[m] = True
    elif val < 0:
        sub[m] = -val  # 정수 id 대입
    else:
        sub[m] = np.maximum(sub[m], val)


def seg_dist(p1, p2, q1, q2):
    """두 선분 사이 최소 거리."""
    def pt_seg(p, a, b):
        ax, ay, bx, by = a[0], a[1], b[0], b[1]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
        return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)

    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])
    if (ccw(p1, q1, q2) > 0) != (ccw(p2, q1, q2) > 0) and (ccw(p1, p2, q1) > 0) != (ccw(p1, p2, q2) > 0):
        return 0.0
    return min(pt_seg(p1, q1, q2), pt_seg(p2, q1, q2), pt_seg(q1, p1, p2), pt_seg(q2, p1, p2))


class State:
    def __init__(self, geom):
        # D-003 #58: 덮인(tented) 비아 위 실크는 허용 — 실크 선 · 글자 둘레 비아 금지(SILK*)는 배선 단계에서 뺀다(글자는 배선 뒤 다시 놓음)
        geom["keepouts"] = [k for k in geom["keepouts"] if not k["name"].startswith("SILK")]
        self.Bh = route.Board(geom)
        self.soft, self.soft_vias, self.hard_add_t, self.hard_add_v = [], [], [], []
        for t in geom["tracks"]:
            if t["net"] not in self.Bh.netid:
                continue
            if is_soft(t["net"]):
                self.soft.append({"net": t["net"], "L": LMAP[t["layer"]], "a": tuple(t["a"]), "b": tuple(t["b"]), "w": t["w"]})
            else:
                self.Bh.add_track(t["net"], LMAP[t["layer"]], tuple(t["a"]), tuple(t["b"]), t["w"])
        for v in geom["vias"]:
            if v["net"] not in self.Bh.netid:
                continue
            if is_soft(v["net"]):
                self.soft_vias.append({"net": v["net"], "pos": tuple(v["pos"]), "dia": v["dia"], "drill": v["drill"]})
            else:
                self.Bh.add_via(v["net"], tuple(v["pos"]), {"dia": v["dia"], "drill": v["drill"]})
        self.rip = {}
        self.padid = [np.zeros((self.Bh.ny, self.Bh.nx), np.int32) for _ in range(4)]
        for i, p in enumerate(self.Bh.pads):
            p["idx"] = i
            for ln, polys in p["polys"].items():
                m = np.zeros((self.Bh.ny, self.Bh.nx), bool)
                for poly in polys:
                    self.Bh.raster_poly_mask(m, poly)
                self.padid[route.LAYERS.index(ln)][m] = i + 1
        self.hist = {L: np.zeros((self.Bh.ny, self.Bh.nx), np.float32) for L in LAYERS}  # 뜯긴 자리 이력 벌점(다투는 길목을 피하게)

    def clusters(self, net):
        """KiCad 연결 판정(끝점이 상대 구리 안)에 맞춘 덩어리: 패드 · 트랙 · 비아를 항목 그래프로 묶는다.
        (래스터 이웃으로 묶으면 0.05 안에 스치기만 한 같은 넷 구리를 이어진 것으로 잘못 본다 — O-105 A 1차 실패 원인)"""
        Bh = self.Bh
        pads = [p for p in Bh.pads if p["net"] == net]
        trs = [{"L": route.LAYERS.index(t["layer"]), "a": tuple(t["a"]), "b": tuple(t["b"]), "w": t["w"]} for t in Bh.tracks if t["net"] == net]
        trs += [t for t in self.soft if t["net"] == net]
        vs = [v for v in Bh.vias if v["net"] == net] + [v for v in self.soft_vias if v["net"] == net]
        nP, nT = len(pads), len(trs)
        parent = list(range(nP + nT + len(vs)))

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def uni(a, b):
            parent[find(a)] = find(b)
        pidx = {p["idx"]: i for i, p in enumerate(pads)}

        def pad_at(L, pos):
            r, c = Bh.cell(*pos)
            k = int(self.padid[L][r, c])
            return pidx.get(k - 1) if k else None
        for i, t in enumerate(trs):
            x0, x1 = min(t["a"][0], t["b"][0]) - t["w"], max(t["a"][0], t["b"][0]) + t["w"]
            y0, y1 = min(t["a"][1], t["b"][1]) - t["w"], max(t["a"][1], t["b"][1]) + t["w"]
            for e in ("a", "b"):
                k = pad_at(t["L"], t[e])
                if k is not None:
                    uni(nP + i, k)
            for k, p in enumerate(pads):
                if route.LAYERS[t["L"]] in p["layers"] and x0 <= p["pos"][0] <= x1 and y0 <= p["pos"][1] <= y1 and \
                        seg_dist(p["pos"], p["pos"], t["a"], t["b"]) <= t["w"] / 2:
                    uni(nP + i, k)
            for j in range(i + 1, nT):
                o = trs[j]
                if o["L"] != t["L"] or max(o["a"][0], o["b"][0]) + o["w"] < x0 or min(o["a"][0], o["b"][0]) - o["w"] > x1 or \
                        max(o["a"][1], o["b"][1]) + o["w"] < y0 or min(o["a"][1], o["b"][1]) - o["w"] > y1:
                    continue
                if any(seg_dist(t[e], t[e], o["a"], o["b"]) <= o["w"] / 2 + 1e-4 for e in ("a", "b")) or \
                        any(seg_dist(o[e], o[e], t["a"], t["b"]) <= t["w"] / 2 + 1e-4 for e in ("a", "b")):
                    uni(nP + i, nP + j)
            for j, v in enumerate(vs):
                if any(math.dist(t[e], v["pos"]) <= v["dia"] / 2 + 1e-4 for e in ("a", "b")) or \
                        seg_dist(v["pos"], v["pos"], t["a"], t["b"]) <= t["w"] / 2:
                    uni(nP + i, nP + nT + j)
        for j, v in enumerate(vs):
            for L in range(4):
                k = pad_at(L, v["pos"])
                if k is not None:
                    uni(nP + nT + j, k)
            for j2 in range(j + 1, len(vs)):
                if math.dist(v["pos"], vs[j2]["pos"]) < 1e-3:
                    uni(nP + nT + j, nP + nT + j2)
        lab = [None] * 4
        pmap = np.zeros(len(Bh.pads) + 1, np.int32)
        for i, p in enumerate(pads):
            pmap[p["idx"] + 1] = find(i) + 1
        for L in range(4):
            lab[L] = pmap[self.padid[L]]
        for i, t in enumerate(trs):
            paint(lab[t["L"]], Bh, t["a"], t["b"], t["w"] / 2, -(find(nP + i) + 1))
        for j, v in enumerate(vs):
            for L in range(4):
                paint(lab[L], Bh, v["pos"], v["pos"], v["dia"] / 2, -(find(nP + nT + j) + 1))
        padc = {}
        for i, p in enumerate(pads):
            padc.setdefault(find(i) + 1, []).append(p)
        self._items = (trs, vs, [find(nP + i) for i in range(nT)], [find(nP + nT + j) for j in range(len(vs))], {find(i) for i in range(nP)})
        return lab, padc

    def purge(self, net):
        """패드에 닿지 않는 조각(뜯긴 뒤 남은 부스러기)을 지운다 — 남겨 두면 벌점 띠로 길을 막고 DRC 에서 미연결 · 끝 뜬 트랙이 된다."""
        self.clusters(net)
        trs, vs, tr_r, v_r, pad_r = self._items
        dt = {id(t) for t, r in zip(trs, tr_r) if r not in pad_r}
        dv = {id(v) for v, r in zip(vs, v_r) if r not in pad_r}
        n = len(self.soft) + len(self.soft_vias)
        self.soft = [t for t in self.soft if id(t) not in dt]
        self.soft_vias = [v for v in self.soft_vias if id(v) not in dv]
        return n - len(self.soft) - len(self.soft_vias)

    def connect(self, net, lab, A, others, w, vtype, margin=8.0, hard=False):
        Bh = self.Bh
        nid = Bh.netid[net]
        vrad = vtype["dia"] / 2
        tmask = [np.isin(lab[L], others) for L in range(4)]
        rs, cs = [], []
        for L in range(4):
            for m in (lab[L] == A, tmask[L]):
                r_, c_ = np.nonzero(m)
                if len(r_):
                    rs += [r_.min(), r_.max()]
                    cs += [c_.min(), c_.max()]
        k = int(margin / G)
        r0, r1, c0, c1 = max(min(rs) - k, 0), min(max(rs) + k, Bh.ny - 1), max(min(cs) - k, 0), min(max(cs) + k, Bh.nx - 1)
        win = (r0, r1, c0, c1)
        sl = (slice(r0, r1 + 1), slice(c0, c1 + 1))
        passable, viaok = Bh.free_maps(win, {nid}, w / 2, vrad, LAYERS)
        H, W = viaok.shape
        if IN1:
            hs0 = Bh.trk[0][sl] & np.isin(Bh.occ[0][sl], list(Bh.hs_ids))
            if hs0.any():
                passable[1] &= ndimage.distance_transform_edt(~hs0) * G >= 0.6 + w / 2
        # soft 구리 벌점
        pen = {L: np.zeros((Bh.ny, Bh.nx), np.float32) for L in LAYERS}
        penv = np.zeros((Bh.ny, Bh.nx), np.float32)
        for t in self.soft:
            if t["net"] == net:
                continue
            P = 1e6 if hard else pen_of(self, t["net"])
            if t["L"] in pen:
                paint(pen[t["L"]], Bh, t["a"], t["b"], t["w"] / 2 + CLR + EPS + w / 2, P)
            paint(penv, Bh, t["a"], t["b"], t["w"] / 2 + CLR + EPS + vrad, P * 4)
        for v in self.soft_vias:
            if v["net"] == net:
                continue
            P = 1e6 if hard else pen_of(self, v["net"])
            for L in LAYERS:
                paint(pen[L], Bh, v["pos"], v["pos"], v["dia"] / 2 + CLR + EPS + w / 2, P * 2)
            paint(penv, Bh, v["pos"], v["pos"], max(v["dia"] / 2 + CLR + EPS + vrad, 0.85), P * 4)
        pen = {L: pen[L][sl] + (0 if hard else self.hist[L][sl]) for L in LAYERS}
        penv = penv[sl]
        orig = {L: passable[L].copy() for L in LAYERS}
        own_vias = []
        for v in [v for v in Bh.vias if v["net"] == net] + [v for v in self.soft_vias if v["net"] == net]:
            r, c = Bh.cell(*v["pos"])
            if r0 <= r <= r1 and c0 <= c <= c1:
                kk = int(math.ceil((v["dia"] / 2 + 0.03) / G))
                own_vias.append((r - r0, c - c0, kk))
                for L in LAYERS:
                    set_disc(passable[L], r - r0, c - c0, kk, False)
        nL = len(LAYERS)
        idx = np.arange(H * W, dtype=np.int64).reshape(H, W)
        src_, dst_, wt_ = [], [], []
        for li, L in enumerate(LAYERS):
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
                    m = m & p[(slice(dr, H), a[1])] & p[(a[0], b[1])]
                s = idx[a][m] + base
                d = idx[b][m] + base
                cst = LCOST[L] * (1.41421356 if dr and dc else 1.0)
                src_ += [s, d]
                dst_ += [d, s]
                wt_ += [cst + pen[L][b][m], cst + pen[L][a][m]]
        for i in range(nL):
            for j in range(i + 1, nL):
                m = viaok & passable[LAYERS[i]] & passable[LAYERS[j]]
                s = idx[m] + i * H * W
                d = idx[m] + j * H * W
                cv = VIA_COST + penv[m]
                src_ += [s, d]
                dst_ += [d, s]
                wt_ += [cv, cv]
        for r, c, kk in own_vias:
            for li, L in enumerate(LAYERS):
                for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    rr, cc = r + dr * (kk + 1), c + dc * (kk + 1)
                    if not (0 <= rr < H and 0 <= cc < W) or not passable[L][rr, cc]:
                        continue
                    if all(orig[L][r + dr * i, c + dc * i] for i in range(kk + 2)):
                        a_, b_ = idx[r, c] + li * H * W, idx[rr, cc] + li * H * W
                        cst = LCOST[L] * (kk + 1) * (1.41421356 if dr and dc else 1.0)
                        src_ += [np.array([a_, b_])]
                        dst_ += [np.array([b_, a_])]
                        wt_ += [np.array([cst + pen[L][rr, cc], cst])]
            for i in range(nL):
                for j in range(i + 1, nL):
                    a_, b_ = idx[r, c] + i * H * W, idx[r, c] + j * H * W
                    src_ += [np.array([a_, b_])]
                    dst_ += [np.array([b_, a_])]
                    wt_ += [np.full(2, 0.01)]
        N = nL * H * W
        g = coo_matrix((np.concatenate(wt_).astype(np.float64), (np.concatenate(src_), np.concatenate(dst_))), shape=(N, N)).tocsr()

        def nodes_of(masks):
            out = []
            for li, L in enumerate(LAYERS):
                out.append(idx[masks[L][sl] & passable[L]] + li * H * W)
                for r, c, kk in own_vias:
                    if any(masks[Lx][sl][r, c] for Lx in range(4)):
                        out.append(np.array([idx[r, c] + li * H * W]))
            return np.unique(np.concatenate(out))
        S = nodes_of([lab[L] == A for L in range(4)])
        T = nodes_of(tmask)
        if not len(S) or not len(T):
            return None, "출발/도착 칸 없음"
        dist, pred, _ = dijkstra(g, directed=True, indices=S, return_predecessors=True, min_only=True)
        best = T[np.argmin(dist[T])]
        if not np.isfinite(dist[best]):
            return None, "경로 없음(고정 구리에 갇힘)"
        path = [int(best)]
        while pred[path[-1]] >= 0:
            path.append(int(pred[path[-1]]))
        path.reverse()
        dec = [(LAYERS[n // (H * W)], (n % (H * W)) // W, (n % (H * W)) % W) for n in path]
        centers = {(r, c): kk * G for r, c, kk in own_vias}
        tracks, vias, runs, run = [], [], [], [dec[0]]
        newv = set()
        for a, b in zip(dec[:-1], dec[1:]):
            if a[0] != b[0]:
                runs.append(run)
                if (a[1], a[2]) not in centers:
                    vias.append(Bh.xy(a[1] + r0, a[2] + c0))
                    newv.add((a[1], a[2]))
                run = [b]
            else:
                run.append(b)
        runs.append(run)

        def canon(p, q, order):
            dr, dc = q[0] - p[0], q[1] - p[1]
            sr, sc = (dr > 0) - (dr < 0), (dc > 0) - (dc < 0)
            nd = min(abs(dr), abs(dc))
            ns = max(abs(dr), abs(dc)) - nd
            tr_, tc_ = (sr, 0) if abs(dr) > abs(dc) else (0, sc)
            steps = [(sr, sc)] * nd + [(tr_, tc_)] * ns if order == 0 else [(tr_, tc_)] * ns + [(sr, sc)] * nd
            cells, r, c = [p], p[0], p[1]
            for a_, b_ in steps:
                r, c = r + a_, c + b_
                cells.append((r, c))
            corner = cells[nd] if order == 0 else cells[ns]
            return cells, (corner if nd and ns else None)

        for run in runs:
            L = run[0][0]
            cl = [(r, c) for _, r, c in run]
            ok = passable[L] & (pen[L] <= 0)
            out, i, n = [cl[0]], 0, len(cl)
            while i < n - 1:
                j, got = n - 1, None
                while j > i + 1 and got is None:
                    for order in (0, 1):
                        cells, corner = canon(cl[i], cl[j], order)
                        rr_ = np.array([x[0] for x in cells])
                        cc_ = np.array([x[1] for x in cells])
                        if ok[rr_, cc_].all() and ok[rr_[1:], cc_[:-1]].all() and ok[rr_[:-1], cc_[1:]].all():
                            got = (j, corner)
                            break
                    if got is None:
                        j = i + max((j - i) * 2 // 3, 1) if j - i > 3 else j - 1
                if got is None:
                    out.append(cl[i + 1])
                    i += 1
                else:
                    if got[1] is not None:
                        out.append(got[1])
                    out.append(cl[got[0]])
                    i = got[0]
            pts = [Bh.xy(r + r0, c + c0) for r, c in out]
            # 비아(새것 · 같은 넷 기존) 원 안에는 꺾임점을 두지 않는다 — 중심에서 원 밖 첫 점까지 곧게
            rs_ = centers.get(cl[0], (vtype["dia"] / 2 + 0.03) if cl[0] in newv else 0)
            re_ = centers.get(cl[-1], (vtype["dia"] / 2 + 0.03) if cl[-1] in newv else 0)
            while rs_ and len(pts) > 2 and math.dist(pts[1], pts[0]) < rs_:
                del pts[1]
            while re_ and len(pts) > 2 and math.dist(pts[-2], pts[-1]) < re_:
                del pts[-2]
            simp = [pts[0]]
            for i in range(1, len(pts) - 1):
                (x0, y0), (x1, y1), (x2, y2) = simp[-1], pts[i], pts[i + 1]
                if abs((x1 - x0) * (y2 - y1) - (y1 - y0) * (x2 - x1)) > 1e-6:
                    simp.append(pts[i])
            if len(pts) > 1:
                simp.append(pts[-1])
            tracks += [(L, a, b) for a, b in zip(simp[:-1], simp[1:]) if math.dist(a, b) > 1e-4]
        for i, va in enumerate(vias):
            if any(math.dist(va, vb) < 0.85 for vb in vias[i + 1:]):
                return None, "새 비아 둘이 너무 가까움"
        return (tracks, vias), ""

    def conflicts(self, net, tracks, vias, w, vtype):
        vrad = vtype["dia"] / 2
        m = 0.02
        ct, cv = set(), set()
        for i, t in enumerate(self.soft):
            if t["net"] == net:
                continue
            for L, a, b in tracks:
                if L == t["L"] and seg_dist(a, b, t["a"], t["b"]) < w / 2 + t["w"] / 2 + CLR + m:
                    ct.add(i)
                    break
            else:
                if any(seg_dist(v, v, t["a"], t["b"]) < vrad + t["w"] / 2 + CLR + m for v in vias):
                    ct.add(i)
        for i, sv in enumerate(self.soft_vias):
            if sv["net"] == net:
                continue
            if any(seg_dist(a, b, sv["pos"], sv["pos"]) < w / 2 + sv["dia"] / 2 + CLR + m for _, a, b in tracks) or \
                    any(math.dist(v, sv["pos"]) < max(vrad + sv["dia"] / 2 + CLR + m, 0.85) for v in vias):
                cv.add(i)
        return ct, cv


def trans_main(S, nets, budget, out_path):
    """거래식 뜯고 다시 깔기: 열린 연결 하나를 잇느라 뜯은 넷을 '아무것도 더 뜯지 않고' 모두 다시 이을 수 있을 때만 받아들인다.
    아니면 되돌린다 → 열린 연결 수는 줄기만 한다(1차 rr 은 바퀴마다 13~23 을 오가며 수렴하지 못했다)."""
    Bh = S.Bh
    t00 = time.time()

    def wv(net):
        nc = route.netclass(net)
        widths = [nc["track_width"]]
        mw = MINW.get(nc["name"], 0.15)
        if mw < widths[0]:
            widths.append(mw)
        if nc["name"] == "PWR_5V":
            widths.append(0.3)
        return widths, (route.VIA_PWR if nc["name"].startswith("PWR_") and nc["name"] != "PWR_LOGIC" else route.VIA)

    def add(net, tracks, vias, w, vtype):
        if is_soft(net):
            S.soft += [{"net": net, "L": L, "a": a, "b": b, "w": w} for L, a, b in tracks]
            S.soft_vias += [{"net": net, "pos": v, "dia": vtype["dia"], "drill": vtype["drill"]} for v in vias]
        else:
            for L, a, b in tracks:
                Bh.add_track(net, L, a, b, w)
                S.hard_add_t.append({"net": net, "layer": route.LAYERS[L], "a": list(a), "b": list(b), "w": w})
            for v in vias:
                Bh.add_via(net, v, vtype)
                S.hard_add_v.append({"net": net, "pos": list(v), "dia": vtype["dia"], "drill": vtype["drill"]})

    def n_open(net):
        return max(len(S.clusters(net)[1]) - 1, 0)

    def join_once(net, hard, skip=()):
        """net 의 가장 작은 덩어리 하나를 잇는다. (결과, 뜯을 것) 또는 None."""
        lab, padc = S.clusters(net)
        cids = sorted(padc, key=lambda c: len(padc[c]))
        for A in cids[:-1]:
            rep_ = (padc[A][0]["ref"], padc[A][0]["num"])
            if rep_ in skip:
                continue
            widths, vtype = wv(net)
            for w in widths:
                res, why = S.connect(net, lab, A, [c for c in cids if c != A], w, vtype, hard=hard)
                if res:
                    ct, cv = S.conflicts(net, res[0], res[1], w, vtype)
                    if hard and (ct or cv):
                        continue
                    return res, ct, cv, w, vtype, rep_
            return None, None, None, None, None, rep_
        return None

    log, sweep = [], 0
    print("부스러기 치움:", sum(S.purge(n) for n in nets if is_soft(n)), flush=True)
    total = sum(n_open(n) for n in nets)
    print(f"거래식 시작: 열린 연결 {total}", flush=True)
    dead = set()
    while time.time() - t00 < budget and total > 0:
        sweep += 1
        gained = 0
        for net in nets:
            if time.time() - t00 > budget:
                break
            tries = 0
            while n_open(net) > 0 and tries < 4 and time.time() - t00 < budget:
                tries += 1
                skip = {r for (n_, r) in dead if n_ == net}
                # 1) 아무것도 안 뜯고
                r = join_once(net, True, skip)
                if r and r[0]:
                    add(net, r[0][0], r[0][1], r[3], r[4])
                    gained += 1
                    print(f"[{sweep}] 연결(안 뜯음) {net} {r[5]} · {time.time() - t00:.0f}s", flush=True)
                    continue
                if not is_soft(net):
                    break
                # 2) 뜯되, 뜯긴 넷을 모두 안 뜯고 되살릴 수 있을 때만
                r = join_once(net, False, skip)
                if r is None:
                    break
                if not r[0]:
                    dead.add((net, r[5]))
                    print(f"[{sweep}] 갇힘 {net} {r[5]}", flush=True)
                    continue
                (tracks, vias), ct, cv, w, vtype, rep_ = r
                victims = sorted({S.soft[i]["net"] for i in ct} | {S.soft_vias[i]["net"] for i in cv})
                snap = (list(S.soft), list(S.soft_vias))
                before = {n: n_open(n) for n in victims}
                S.soft = [t_ for i, t_ in enumerate(S.soft) if i not in ct]
                S.soft_vias = [v_ for i, v_ in enumerate(S.soft_vias) if i not in cv]
                add(net, tracks, vias, w, vtype)
                for n in victims:
                    S.purge(n)
                ok = True
                for n in victims:
                    guard = 0
                    while n_open(n) > before[n] and guard < 6:
                        guard += 1
                        r2 = join_once(n, True)
                        if not r2 or not r2[0]:
                            ok = False
                            break
                        add(n, r2[0][0], r2[0][1], r2[3], r2[4])
                    if not ok or n_open(n) > before[n]:
                        ok = False
                        break
                if ok:
                    gained += 1
                    print(f"[{sweep}] 연결(뜯고 되살림 {victims}) {net} {rep_} · {time.time() - t00:.0f}s", flush=True)
                else:
                    S.soft, S.soft_vias = snap
                    for n in victims:
                        S.rip[n] = S.rip.get(n, 0) + 1   # 다음 시도는 다른 넷을 뜯게
                    print(f"[{sweep}] 되돌림 {net} {rep_} (뜯긴 {victims} 중 못 되살림) · {time.time() - t00:.0f}s", flush=True)
        total = sum(n_open(n) for n in nets)
        print(f"== 훑기 {sweep} 끝: 열린 연결 {total} · 이번에 줄인 수 {gained} · {time.time() - t00:.0f}s", flush=True)
        dump(S, nets, out_path, log, {})
        if gained == 0:
            break
    return log


def dump(S, nets, path, log, hard_fail):
    Bh = S.Bh
    remaining = []
    for net in nets:
        _, padc = S.clusters(net)
        if len(padc) > 1:
            remaining.append({"net": net, "clusters": [[f"{p['ref']}.{p['num']}" for p in ps[:6]] for ps in padc.values()]})
    out = {"soft_nets": sorted(n for n in Bh.netid if is_soft(n)),
           "soft_tracks": [{"net": t["net"], "layer": route.LAYERS[t["L"]], "a": list(t["a"]), "b": list(t["b"]), "w": t["w"]} for t in S.soft],
           "soft_vias": [{"net": v["net"], "pos": list(v["pos"]), "dia": v["dia"], "drill": v["drill"]} for v in S.soft_vias],
           "hard_add_tracks": S.hard_add_t, "hard_add_vias": S.hard_add_v,
           "log": log, "remaining": remaining, "hard_fail": [{"net": k[0], "from": k[1], "why": v} for k, v in hard_fail.items()]}
    json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return remaining


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    budget = float(sys.argv[3]) * 60 if len(sys.argv) > 3 else 720
    S = State(geom)
    Bh = S.Bh
    nets = sorted((n for n in Bh.netid if n != "/GND" and route.netclass(n)["name"] not in route.HS),
                  key=lambda n: (not route.netclass(n)["name"].startswith("PWR_"), n))
    if len(sys.argv) > 4:  # 앞선 결과(rr.json)의 soft 상태에서 이어서
        prev = json.load(open(sys.argv[4], encoding="utf-8"))
        S.soft = [{"net": t["net"], "L": route.LAYERS.index(t["layer"]), "a": tuple(t["a"]), "b": tuple(t["b"]), "w": t["w"]}
                  for t in prev["soft_tracks"] if math.dist(t["a"], t["b"]) > 1e-4]
        S.soft_vias = [{"net": v["net"], "pos": tuple(v["pos"]), "dia": v["dia"], "drill": v["drill"]} for v in prev["soft_vias"]]
    if __import__("os").environ.get("RR_TRANS") == "1":
        trans_main(S, nets, budget, sys.argv[2])
        rem = dump(S, nets, sys.argv[2], [], {})
        print(f"끝(거래식): 남은 넷 {len(rem)} {[r['net'] for r in rem]}")
        return
    t00 = time.time()
    hard_fail = {}
    fail_n = {}
    log = []
    rounds = 0
    best = None

    def open_count():
        return sum(max(len(S.clusters(n)[1]) - 1, 0) for n in nets)

    def snap(n_open):
        return {"open": n_open, "soft": [dict(t) for t in S.soft], "soft_vias": [dict(v) for v in S.soft_vias],
                "hard_t": list(S.hard_add_t), "hard_v": list(S.hard_add_v), "nlog": len(log)}
    while time.time() - t00 < budget and rounds < 12:
        rounds += 1
        any_ok = False
        open_n = 0
        for net in nets:
            nc = route.netclass(net)
            widths = [nc["track_width"]]
            mw = MINW.get(nc["name"], 0.15)
            if mw < widths[0]:
                widths.append(mw)
            if nc["name"] == "PWR_5V":
                widths.append(0.3)
            vtype = route.VIA_PWR if nc["name"].startswith("PWR_") and nc["name"] != "PWR_LOGIC" else route.VIA
            failed = set()
            while time.time() - t00 < budget:
                lab, padc = S.clusters(net)
                cids = sorted(padc, key=lambda c: len(padc[c]))
                if len(cids) <= 1:
                    break
                cand = [c for c in cids if (padc[c][0]["ref"], padc[c][0]["num"]) not in failed
                        and fail_n.get((net, padc[c][0]["ref"], padc[c][0]["num"]), 0) < 2]
                if not cand:
                    open_n += len(cids) - 1
                    break
                A = cand[0]
                rep = (padc[A][0]["ref"], padc[A][0]["num"])
                name = ",".join(f"{p['ref']}.{p['num']}" for p in padc[A][:4])
                res, why, w = None, "", widths[0]
                for w in widths:
                    res, why = S.connect(net, lab, A, [c for c in cids if c != A], w, vtype)
                    if res:
                        break
                if not res:
                    failed.add(rep)
                    fail_n[(net,) + rep] = fail_n.get((net,) + rep, 0) + 1
                    hard_fail[(net, name)] = why
                    print(f"[{rounds}] 실패 {net} [{name}] {why}", flush=True)
                    continue
                hard_fail.pop((net, name), None)
                tracks, vias = res
                ct, cv = S.conflicts(net, tracks, vias, w, vtype)
                ripped = sorted({S.soft[i]["net"] for i in ct} | {S.soft_vias[i]["net"] for i in cv})
                for n in ripped:
                    S.rip[n] = S.rip.get(n, 0) + 1
                for i in ct:
                    t_ = S.soft[i]
                    if t_["L"] in S.hist:
                        tmp = np.zeros_like(S.hist[t_["L"]])
                        paint(tmp, Bh, t_["a"], t_["b"], t_["w"] / 2 + CLR, HIST)
                        S.hist[t_["L"]] += tmp
                S.soft = [t for i, t in enumerate(S.soft) if i not in ct]
                S.soft_vias = [v for i, v in enumerate(S.soft_vias) if i not in cv]
                if is_soft(net):
                    S.soft += [{"net": net, "L": L, "a": a, "b": b, "w": w} for L, a, b in tracks]
                    S.soft_vias += [{"net": net, "pos": v, "dia": vtype["dia"], "drill": vtype["drill"]} for v in vias]
                else:
                    for L, a, b in tracks:
                        Bh.add_track(net, L, a, b, w)
                        S.hard_add_t.append({"net": net, "layer": route.LAYERS[L], "a": list(a), "b": list(b), "w": w})
                    for v in vias:
                        Bh.add_via(net, v, vtype)
                        S.hard_add_v.append({"net": net, "pos": list(v), "dia": vtype["dia"], "drill": vtype["drill"]})
                any_ok = True
                ln = sum(math.dist(a, b) for _, a, b in tracks)
                log.append({"net": net, "from": name, "w": w, "len": round(ln, 2), "vias": len(vias), "ripped": ripped})
                print(f"[{rounds}] 연결 {net} [{name}] 폭 {w} · {ln:.1f}mm · 비아 {len(vias)} · 뜯음 {ripped} · {time.time() - t00:.0f}s", flush=True)
        n_open = open_count()
        print(f"== 바퀴 {rounds} 끝: 남은 연결 {n_open} · {time.time() - t00:.0f}s", flush=True)
        if best is None or n_open < best["open"]:
            best = snap(n_open)
            json.dump({"open": n_open, "round": rounds}, open(sys.argv[2] + ".best", "w"))
        if not any_ok or n_open == 0:
            break
    if best is not None and best["open"] < open_count():
        S.soft, S.soft_vias, S.hard_add_t, S.hard_add_v = best["soft"], best["soft_vias"], best["hard_t"], best["hard_v"]
        log = log[:best["nlog"]]
        print(f"가장 좋은 중간 상태로 되돌림: 남은 연결 {best['open']}", flush=True)
    remaining = []
    for net in nets:
        _, padc = S.clusters(net)
        if len(padc) > 1:
            remaining.append({"net": net, "clusters": [[f"{p['ref']}.{p['num']}" for p in ps[:6]] for ps in padc.values()]})
    out = {"soft_nets": sorted(n for n in Bh.netid if is_soft(n)),
           "soft_tracks": [{"net": t["net"], "layer": route.LAYERS[t["L"]], "a": list(t["a"]), "b": list(t["b"]), "w": t["w"]} for t in S.soft],
           "soft_vias": [{"net": v["net"], "pos": list(v["pos"]), "dia": v["dia"], "drill": v["drill"]} for v in S.soft_vias],
           "hard_add_tracks": S.hard_add_t, "hard_add_vias": S.hard_add_v,
           "log": log, "remaining": remaining, "hard_fail": [{"net": k[0], "from": k[1], "why": v} for k, v in hard_fail.items()]}
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"끝: 바퀴 {rounds} · 연결 {len(log)} · 남은 넷 {len(remaining)} {[r['net'] for r in remaining]} · {time.time() - t00:.0f}s")


if __name__ == "__main__":
    main()
