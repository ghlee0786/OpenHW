"""배선기 2단계 (시스템 파이썬 + numpy·scipy): 격자 A* 스크립트 배선 (O-35 (B)). 자동 배선 결과를 최적이라 주장하지 않는다.

입력: route_export.py JSON (KiCad mm, y 아래) + hardware/pcb/rules/netclasses.json
출력: JSON {tracks:[{net,layer,w,a,b}], vias:[{net,pos,dia,drill}], failed:[...]} — route_apply.py 가 보드에 넣는다.

방법
- 격자 0.05mm, 층 F.Cu·In1.Cu·In2.Cu·B.Cu. In1은 GND 면 전용(배선 금지). 고속(CSI·MDI·USB)은 F/B만, 그 밖은 F/B 우선·In2 허용(비용 1.6배).
- 간격: 다른 넷 구리까지 거리(scipy EDT) ≥ 0.16(DRU 최소) + 반폭 + 0.035(격자 오차). 구멍(NPTH) 0.25, 외곽 0.40, 금지 영역(KO_*)은 반폭.
- 자기 패드 안은 항상 지날 수 있다(0.4mm 피치 탈출).
- 넷 연결: 가장 가까운 미연결 패드를 이미 이어진 나무(패드·트랙·비아)에 잇는다(다중 목표 A*, 꺾임 벌점).
- 차동 쌍: 중심선(반폭 = w + g/2)을 찾고 ±(w+g)/2 로 띄운 P/N 선을 만든다. 층 바꿈은 진행 방향에 직각으로 ±0.45 쌍 비아 + 바깥쪽 GND 귀환 비아.
- GND: 트랙 대신 SMD GND 패드마다 1.5mm 안 비아(짧은 트랙) — 면(In1·In2·외층 채움)이 잇는다.
사용: python route.py <geom.json> <board> <out.json>
"""
import fnmatch
import heapq
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

G = 0.05
CLR = 0.16
HS_CLR = 0.30  # DRU hs_track_spacing
EPS = 0.045
VIA = {"dia": 0.65, "drill": 0.30}
VIA_PWR = {"dia": 0.80, "drill": 0.40}
LAYERS = ["F.Cu", "In1.Cu", "In2.Cu", "B.Cu"]
DIRS = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
ROOT = Path(__file__).resolve().parents[3]
NC = json.loads((ROOT / "hardware/pcb/rules/netclasses.json").read_text(encoding="utf-8"))
HS = {"CSI_100", "MDI_100", "USB_90"}

# 차동 쌍 (보드별): 이름 → (P넷, N넷, 시작 패드쌍 (refP, numP, refN, numN), 끝 패드쌍)
PAIRS = {
    "front": [
        # 순서: D0 먼저 — J1 쪽(+x부터 CLK·D0·D1)과 DF30 쪽(D0·CLK·D1)에서 D0·CLK 순서가 엇갈려 D0가 CLK를 층으로 넘어가야 한다
        ("CSI_D0", "/CAM_RX0_0P", "/CAM_RX0_0N", ("J1", "18", "J1", "16"), ("J3", "7", "J3", "5")),
        ("CSI_CLK", "/CAM_RX0_CLKP", "/CAM_RX0_CLKN", ("J1", "12", "J1", "10"), ("J3", "11", "J3", "9")),
        ("CSI_D1", "/CAM_RX0_1P", "/CAM_RX0_1N", ("J1", "24", "J1", "22"), ("J3", "15", "J3", "13")),
    ],
    "carrier": [
        # MDI: J1(위→아래 TX·RX)과 RJ45 핀(동→서 TX·RX) 순서가 엇갈려 한 쌍은 층을 바꿔 넘어가야 한다 → RX 먼저, TX가 넘는다
        ("MDI_RX", "/EPHY_RXP", "/EPHY_RXN", ("J1", "8", "J1", "10"), ("D5", "1", "D5", "2")),
        ("MDI_TX", "/EPHY_TXP", "/EPHY_TXN", ("J1", "2", "J1", "4"), ("D4", "1", "D4", "2")),
        # USB: U3(USBLC6-2SC6)는 관통형(1↔6 DP, 3↔4 DN) — 배치 회전에 따라 P/N 좌우가 맞는 쪽 핀쌍을 고른다
        ("USB_A", "/USB_DP", "/USB_DN", ("J1", "3", "J1", "1"), [("U3", "6", "U3", "4"), ("U3", "1", "U3", "3")]),
    ],
}


def netclass(net):
    name = net.lstrip("/")
    best = None
    for p in NC["patterns"]:
        pat = p["pattern"]
        if fnmatch.fnmatchcase(net, pat) or fnmatch.fnmatchcase(name, pat):
            c = next(c for c in NC["classes"] if c["name"] == p["netclass"])
            if best is None or c.get("priority", 99) < best.get("priority", 99):
                best = c
    return best or NC["classes"][0]


class Board:
    def __init__(self, geom):
        self.g = geom
        x0, y0, x1, y1 = geom["edge"]
        self.x0, self.y0 = x0, y0
        self.nx, self.ny = int(round((x1 - x0) / G)) + 1, int(round((y1 - y0) / G)) + 1
        self.occ = np.zeros((4, self.ny, self.nx), np.int32)   # 넷 id, 0 빈칸, <0 넷 없는 구리
        self.hard = np.zeros((4, self.ny, self.nx), bool)       # 금지 영역(트랙)
        self.hardvia = np.zeros((self.ny, self.nx), bool)       # 금지 영역(비아)
        self.holes = np.zeros((self.ny, self.nx), bool)         # 드릴 구멍(모든 넷)
        self.netid = {}
        self.pads = []
        nid = -10
        for p in geom["pads"]:
            n = p["net"]
            if n and not n.startswith("unconnected"):
                if n not in self.netid:
                    self.netid[n] = len(self.netid) + 1
                i = self.netid[n]
            else:
                nid -= 1
                i = nid
            p["id"] = i
            self.pads.append(p)
            for ln, polys in p["polys"].items():
                L = LAYERS.index(ln)
                for poly in polys:
                    self.raster_poly(L, poly, i)
            if p["drill"]:
                self.disc(self.holes, p["pos"], p["drill"] / 2, True)
                if p["npth"]:
                    for L in range(4):
                        self.disc(self.occ[L], p["pos"], p["drill"] / 2 + 0.09, i)  # NPTH 0.25 간격 ≈ 0.16 + 0.09
        for k in geom["keepouts"]:
            for ln in k["layers"]:
                L = LAYERS.index(ln)
                for poly in k["polys"]:
                    m = np.zeros((self.ny, self.nx), bool)
                    self.raster_poly_mask(m, poly)
                    if k["tracks"]:
                        self.hard[L] |= m
                    if k["vias"]:
                        self.hardvia |= m
        # 고속 넷 id 와 탈출 구역(규칙 영역 CSI_BRK*) — 그 안에서는 고속 간격 대신 CLR
        self.hs_ids = {i for n, i in self.netid.items() if netclass(n)["name"] in HS}
        self.brk = np.zeros((4, self.ny, self.nx), bool)
        for a in geom.get("areas", []):
            if "_BRK" in a["name"]:
                for ln in a["layers"]:
                    for poly in a["polys"]:
                        self.raster_poly_mask(self.brk[LAYERS.index(ln)], poly)
        # 외곽: 0.40 − 0.16 만큼 안쪽까지 넷 없는 구리로 취급
        e = int(math.ceil((0.40 - CLR) / G))
        for L in range(4):
            self.occ[L, :e, :] = -3
            self.occ[L, -e:, :] = -3
            self.occ[L, :, :e] = -3
            self.occ[L, :, -e:] = -3
        self.tracks, self.vias, self.failed = [], [], []

    # --- 좌표 ---
    def cell(self, x, y):
        return int(round((y - self.y0) / G)), int(round((x - self.x0) / G))

    def xy(self, r, c):
        return (round(self.x0 + c * G, 4), round(self.y0 + r * G, 4))

    # --- 래스터 ---
    def raster_poly_mask(self, m, poly):
        pts = np.array(poly)
        r0, c0 = self.cell(pts[:, 0].min(), pts[:, 1].min())
        r1, c1 = self.cell(pts[:, 0].max(), pts[:, 1].max())
        r0, c0 = max(r0 - 1, 0), max(c0 - 1, 0)
        r1, c1 = min(r1 + 1, self.ny - 1), min(c1 + 1, self.nx - 1)
        if r1 < r0 or c1 < c0:
            return
        ys = self.y0 + np.arange(r0, r1 + 1) * G
        xs = self.x0 + np.arange(c0, c1 + 1) * G
        X, Y = np.meshgrid(xs, ys)
        inside = np.zeros(X.shape, bool)
        n = len(pts)
        for k in range(n):
            xa, ya = pts[k]
            xb, yb = pts[(k + 1) % n]
            cond = (ya > Y) != (yb > Y)
            with np.errstate(divide="ignore", invalid="ignore"):
                xint = (xb - xa) * (Y - ya) / (yb - ya) + xa
            inside ^= cond & (X < xint)
        m[r0:r1 + 1, c0:c1 + 1] |= inside

    def raster_poly(self, L, poly, i):
        m = np.zeros((self.ny, self.nx), bool)
        self.raster_poly_mask(m, poly)
        self.occ[L][m] = i

    def disc(self, arr, pos, rad, val):
        r, c = self.cell(*pos)
        k = int(math.ceil(rad / G)) + 1
        r0, r1, c0, c1 = max(r - k, 0), min(r + k, self.ny - 1), max(c - k, 0), min(c + k, self.nx - 1)
        ys, xs = np.mgrid[r0:r1 + 1, c0:c1 + 1]
        m = (ys - r) ** 2 + (xs - c) ** 2 <= (rad / G) ** 2
        sub = arr[r0:r1 + 1, c0:c1 + 1]
        sub[m] = val

    def capsule(self, L, a, b, rad, val):
        ra, ca = self.cell(*a)
        rb, cb = self.cell(*b)
        k = int(math.ceil(rad / G)) + 1
        r0, r1 = max(min(ra, rb) - k, 0), min(max(ra, rb) + k, self.ny - 1)
        c0, c1 = max(min(ca, cb) - k, 0), min(max(ca, cb) + k, self.nx - 1)
        ys, xs = np.mgrid[r0:r1 + 1, c0:c1 + 1].astype(float)
        dr, dc = rb - ra, cb - ca
        L2 = dr * dr + dc * dc
        t = np.clip(((ys - ra) * dr + (xs - ca) * dc) / L2, 0, 1) if L2 else np.zeros_like(ys)
        d2 = (ys - ra - t * dr) ** 2 + (xs - ca - t * dc) ** 2
        sub = self.occ[L, r0:r1 + 1, c0:c1 + 1]
        sub[d2 <= (rad / G) ** 2] = val

    # --- 추가 ---
    def add_track(self, net, L, a, b, w):
        if a == b:
            return
        self.tracks.append({"net": net, "layer": LAYERS[L], "w": w, "a": list(a), "b": list(b)})
        self.capsule(L, a, b, w / 2, self.netid[net])

    def add_via(self, net, pos, v):
        self.vias.append({"net": net, "pos": list(pos), "dia": v["dia"], "drill": v["drill"]})
        for L in range(4):
            self.disc(self.occ[L], pos, v["dia"] / 2, self.netid[net])
        self.disc(self.holes, pos, v["drill"] / 2, True)

    # --- 탐색 창 ---
    def window(self, cells, margin=6.0):
        rs = [c[0] for c in cells]
        cs = [c[1] for c in cells]
        m = int(margin / G)
        return (max(min(rs) - m, 0), min(max(rs) + m, self.ny - 1), max(min(cs) - m, 0), min(max(cs) + m, self.nx - 1))

    def free_maps(self, win, own_ids, hw, vrad, layers, hs=False):
        """창 안에서 층별 '지날 수 있음'과 '비아 가능'. hs=True: 다른 고속 넷 구리와 HS_CLR(DRU hs_track_spacing), 탈출 구역(CSI_BRK*) 안은 CLR."""
        r0, r1, c0, c1 = win
        pad = int((CLR + max(hw, vrad) + 0.2) / G) + 2
        R0, R1, C0, C1 = max(r0 - pad, 0), min(r1 + pad, self.ny - 1), max(c0 - pad, 0), min(c1 + pad, self.nx - 1)
        sl = (slice(R0, R1 + 1), slice(C0, C1 + 1))
        inner = (slice(r0 - R0, r1 - R0 + 1), slice(c0 - C0, c1 - C0 + 1))
        passable, viaok = {}, np.ones((r1 - r0 + 1, c1 - c0 + 1), bool)
        ownpad = {}
        for L in range(4):
            o = self.occ[L][sl]
            other = (o != 0) & ~np.isin(o, list(own_ids))
            d = ndimage.distance_transform_edt(~other) * G
            hd = ndimage.distance_transform_edt(~self.hard[L][sl]) * G
            own = np.isin(o, list(own_ids))
            ownpad[L] = own[inner]
            if L in layers:
                ok = (d >= CLR + hw + EPS) & (hd >= hw + 0.02)
                if hs and self.hs_ids:
                    hso = np.isin(o, list(self.hs_ids - set(own_ids)))
                    dh = ndimage.distance_transform_edt(~hso) * G
                    ok &= (dh >= HS_CLR + hw + EPS) | self.brk[L][sl]
                passable[L] = ok[inner]  # 자기 구리는 원래 장애물이 아님 — 패드 위 예외를 두면 굵은 트랙이 이웃 패드를 덮는다(P-003 DRC)
            viaok &= (d >= CLR + vrad + EPS)[inner]
        hv = ndimage.distance_transform_edt(~self.hardvia[sl]) * G
        hl = ndimage.distance_transform_edt(~self.holes[sl]) * G
        viaok &= (hv >= vrad)[inner] & (hl >= 0.25 + vrad + 0.15)[inner]
        # 자기 SMD 패드 위 비아 금지(비아 인 패드 안 씀)
        for L in (0, 3):
            viaok &= ~ndimage.binary_dilation(ownpad[L] & ~self.holes[sl][inner], iterations=int(vrad / G) + 2)
        return passable, viaok

    # --- A* ---
    def astar(self, win, starts, targets, passable, viaok, layers, via_cost=30.0, pair_off=None, start_dir=8, end_dir=None, cap=200_000,
              no_via_near=None, min_run=0):
        """starts/targets: {(L, r, c)} 창 좌표. pair_off: 쌍 비아 간격(셀) — 비아는 진행 방향 직각 양쪽.
        min_run>0 (쌍): 90° 꺾임 금지, 꺾임·비아 앞뒤 최소 직진 min_run 셀 — 띄운 P/N 선이 뒤집히지 않게."""
        r0, r1, c0, c1 = win
        H, W = r1 - r0 + 1, c1 - c0 + 1
        tset = set(targets)
        if not tset:
            return None
        trs = np.array([t[1] for t in tset])
        tcs = np.array([t[2] for t in tset])
        tr0, tr1, tc0, tc1 = trs.min(), trs.max(), tcs.min(), tcs.max()

        def h(r, c):
            dr = max(tr0 - r, 0, r - tr1)
            dc = max(tc0 - c, 0, c - tc1)
            return max(dr, dc) + 0.414 * min(dr, dc)

        lcost = {0: 1.0, 3: 1.0, 2: 1.6, 1: 99.0}
        max_turn = 1 if min_run else 2
        openh = []
        best = {}
        prev = {}
        for (L, r, c) in starts:
            if L in layers:
                s = (L, r, c, start_dir, min_run)
                best[s] = 0.0
                heapq.heappush(openh, (h(r, c), 0.0, s))
        n = 0
        while openh:
            f, gcost, s = heapq.heappop(openh)
            if best.get(s, 1e18) < gcost - 1e-9:
                continue
            L, r, c, d, run = s
            if (L, r, c) in tset and (end_dir is None or d == end_dir) and run >= min_run:
                path = [s]
                while path[-1] in prev:
                    path.append(prev[path[-1]])
                return [q[:4] for q in path[::-1]]
            n += 1
            if n > cap:
                return None
            for nd, (dc, dr) in enumerate(DIRS):
                if d != 8:
                    turn = min((nd - d) % 8, (d - nd) % 8)
                    if turn > max_turn:
                        continue
                    if turn and run < min_run:
                        continue
                    tp = (0.0, 0.4, 2.0)[turn]
                else:
                    turn, tp = 0, 0.0
                rr, cc = r + dr, c + dc
                if not (0 <= rr < H and 0 <= cc < W) or not passable[L][rr, cc]:
                    continue
                if dr and dc and not (passable[L][r, cc] and passable[L][rr, c]):
                    continue
                nrun = min(run + 1, min_run) if (turn == 0 and d != 8) else (1 if min_run else 0)
                ns = (L, rr, cc, nd, nrun)
                ng = gcost + (1.4142 if dr and dc else 1.0) * lcost[L] + tp
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    prev[ns] = s
                    heapq.heappush(openh, (ng + h(rr, cc), ng, ns))
            # 층 바꿈
            if d == 8 and pair_off:
                continue
            if run < min_run:
                continue
            if no_via_near and any((r - a) ** 2 + (c - b) ** 2 < no_via_near[1] ** 2 for a, b in no_via_near[0]):
                continue
            if pair_off:
                dc, dr = DIRS[d]
                nrm = math.hypot(dr, dc)
                pr, pc = -dc / nrm, dr / nrm  # 진행 방향 직각
                spots = [(int(round(r + pr * pair_off)), int(round(c + pc * pair_off))),
                         (int(round(r - pr * pair_off)), int(round(c - pc * pair_off)))]
                if not all(0 <= a < H and 0 <= b < W and viaok[a, b] for a, b in spots):
                    continue
            elif not viaok[r, c]:
                continue
            for L2 in layers:
                if L2 == L or not passable[L2][r, c]:
                    continue
                ns = (L2, r, c, d, 0)
                ng = gcost + via_cost
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    prev[ns] = s
                    heapq.heappush(openh, (ng + h(r, c), ng, ns))
        return None

    # --- 경로 → 선분 ---
    @staticmethod
    def corners(path):
        """[(L,r,c,d)] → [(L, [(r,c)...])] 층별 꺾임점."""
        out = []
        cur_L, pts = path[0][0], [path[0][1:3]]
        last_d = None
        for k in range(1, len(path)):
            L, r, c, d = path[k]
            if L != cur_L:
                if pts[-1] != (r, c):
                    pts.append((r, c))
                out.append((cur_L, pts))
                cur_L, pts, last_d = L, [(r, c)], None
                continue
            if last_d is not None and d != last_d and pts[-1] != path[k - 1][1:3]:
                pts.append(path[k - 1][1:3])
            last_d = d
        if pts[-1] != path[-1][1:3]:
            pts.append(path[-1][1:3])
        out.append((cur_L, pts))
        return out


def offset_poly(pts, dist):
    """꺾은선을 왼쪽(+)으로 dist 만큼 띄운다 (마이터)."""
    P = [np.array(p, float) for p in pts]
    if len(P) < 2:
        return [tuple(p) for p in P]
    normals = []
    for a, b in zip(P[:-1], P[1:]):
        v = b - a
        n = np.array([-v[1], v[0]]) / (np.linalg.norm(v) or 1)
        normals.append(n)
    out = [P[0] + normals[0] * dist]
    for k in range(1, len(P) - 1):
        n1, n2 = normals[k - 1], normals[k]
        m = n1 + n2
        m /= (np.linalg.norm(m) or 1)
        cos = max(float(np.dot(m, n1)), 0.3)
        out.append(P[k] + m * dist / cos)
    out.append(P[-1] + normals[-1] * dist)
    return [tuple(map(float, p)) for p in out]


def plength(pts):
    return sum(math.dist(a, b) for a, b in zip(pts[:-1], pts[1:]))


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    board_name = sys.argv[2]
    B = Board(geom)
    import thermal  # 배선 전 열 구리(LED 애노드 영역·노출 패드·열 비아, EP 둘레 GND 비아) — 이후 배선이 피한다
    th_zones, th_masks = thermal.pre_route(B, board_name, LAYERS, CLR, EPS, G)
    padmap = {(p["ref"], p["num"]): p for p in B.pads}
    report = {"pairs": [], "nets": {}}

    def pad_cells(p, layers):
        out = set()
        for ln in p["layers"]:
            L = LAYERS.index(ln)
            if L not in layers:
                continue
            m = np.zeros((B.ny, B.nx), bool)
            for poly in p["polys"][ln]:
                B.raster_poly_mask(m, poly)
            rs, cs = np.nonzero(m)
            out |= {(L, r, c) for r, c in zip(rs, cs)}
        return out

    # 1) 차동 쌍 — 경로 찾기 → (CSI) 레인 길이 맞춤 → 그리기
    def route_pair(spec):
        """spec 끝(4번째)은 패드쌍 하나 또는 후보 목록(관통형 부품: 같은 넷 패드가 양쪽에 있음). P/N 좌우가 맞는 후보부터."""
        name, pn, nn, (sa, sna, sb, snb), ends = spec
        ends = ends if isinstance(ends, list) else [ends]
        nc = netclass(pn)
        w, gap = nc["diff_pair_width"], nc["diff_pair_gap"]
        hw = w + gap / 2
        own = {B.netid[pn], B.netid[nn]}
        layers = [0, 3]
        P0, N0 = padmap[(sa, sna)], padmap[(sb, snb)]
        mid0 = ((P0["pos"][0] + N0["pos"][0]) / 2, (P0["pos"][1] + N0["pos"][1]) / 2)

        def outward(ref, mid, pad, mate, other):
            """패드 긴 축 방향으로, 부품 패드 중심에서 멀어지는 쪽.
            P·N이 한 부품의 양 끝 패드(예: SOD-323 ESD)라 중심이 같으면: P–N 축의 직각 중 경로 반대쪽 끝(other)을 향하는 쪽."""
            ps = [q["pos"] for q in B.pads if q["ref"] == ref]
            cx, cy = sum(q[0] for q in ps) / len(ps), sum(q[1] for q in ps) / len(ps)
            pts = np.array([q for polys in pad["polys"].values() for poly in polys for q in poly])
            wx, wy = np.ptp(pts[:, 0]), np.ptp(pts[:, 1])
            v = (0, int(np.sign(round(mid[1] - cy, 3)))) if wy >= wx else (int(np.sign(round(mid[0] - cx, 3))), 0)
            if v == (0, 0):
                ax = np.subtract(pad["pos"], mate["pos"])
                v = (0, int(np.sign(other[1] - mid[1]) or 1)) if abs(ax[0]) >= abs(ax[1]) else (int(np.sign(other[0] - mid[0]) or 1), 0)
            return DIRS.index(v)

        def half_len(p, u):  # 패드 중심에서 바깥 방향 끝까지
            pts = [q for polys in p["polys"].values() for poly in polys for q in poly]
            return max((q[0] - p["pos"][0]) * u[0] + (q[1] - p["pos"][1]) * u[1] for q in pts)

        def brk_rect(pa, pb, X, Ls):
            """탈출 구역(패드 둘레 + 탈출점) — 그 안에서만 고속 간격·쌍 간격 완화(DRU dp_breakout_*)."""
            xs = [pa["pos"][0], pb["pos"][0], X[0]]
            ys = [pa["pos"][1], pb["pos"][1], X[1]]
            hl = max(max(abs(q[0] - pa["pos"][0]), abs(q[1] - pa["pos"][1])) for polys in pa["polys"].values() for poly in polys for q in poly)
            r = (min(xs) - hl - 0.2, min(ys) - hl - 0.2, max(xs) + hl + 0.2, max(ys) + hl + 0.2)
            return [(LAYERS[L], r) for L in Ls]

        last_reason = "side"
        for (ea, ena, eb, enb) in ends:
            P1, N1 = padmap[(ea, ena)], padmap[(eb, enb)]
            mid1 = ((P1["pos"][0] + N1["pos"][0]) / 2, (P1["pos"][1] + N1["pos"][1]) / 2)
            sd = outward(sa, mid0, P0, N0, mid1)
            od1 = outward(ea, mid1, P1, N1, mid0)
            ed = (od1 + 4) % 8
            u0, u1 = np.array(DIRS[sd], float), np.array(DIRS[od1], float)
            nrm = np.array([-u0[1], u0[0]])
            sideP = 1 if np.dot(np.subtract(P0["pos"], mid0), nrm) > 0 else -1
            v2 = -u1
            sideP_end = 1 if np.dot(np.subtract(P1["pos"], mid1), np.array([-v2[1], v2[0]])) > 0 else -1
            if sideP != sideP_end:
                continue
            hl0 = max(half_len(P0, u0), half_len(N0, u0))
            hl1 = max(half_len(P1, u1), half_len(N1, u1))
            S = (mid0[0] + u0[0] * (hl0 + 0.35), mid0[1] + u0[1] * (hl0 + 0.35))   # 탈출 뒤 중심선 시작
            E = (mid1[0] + u1[0] * (hl1 + 0.35), mid1[1] + u1[1] * (hl1 + 0.35))
            S_far = (S[0] + u0[0] * 0.5, S[1] + u0[1] * 0.5)                       # 양 끝 0.5mm 직선
            E_far = (E[0] + u1[0] * 0.5, E[1] + u1[1] * 0.5)
            sL = [LAYERS.index(l) for l in P0["layers"] if LAYERS.index(l) in layers]
            eL = [LAYERS.index(l) for l in P1["layers"] if LAYERS.index(l) in layers]
            brks = brk_rect(P0, N0, S, sL) + brk_rect(P1, N1, E, eL)
            for ln, (x0, y0, x1, y1) in brks:  # 탈출 구역을 먼저 표시 → 고속 간격 완화가 이 쌍부터 적용
                ra, ca = B.cell(x0, y0)
                rb, cb = B.cell(x1, y1)
                B.brk[LAYERS.index(ln), ra:rb + 1, ca:cb + 1] = True
            c0, c1 = B.cell(*S_far), B.cell(*E_far)
            win = B.window([c0, c1], 5.0)
            passable, viaok = B.free_maps(win, own, hw, VIA["dia"] / 2, layers, hs=True)
            r0, _, cc0, _ = win
            for (pa, pb, X), Ls in (((P0, N0, S_far), sL), ((P1, N1, E_far), eL)):  # 패드 → 탈출점 직사각형 열기
                cs_ = [B.cell(*pa["pos"]), B.cell(*pb["pos"]), B.cell(*X)]
                rr0, rr1 = min(c[0] for c in cs_) - r0 - 2, max(c[0] for c in cs_) - r0 + 3
                cl0, cl1 = min(c[1] for c in cs_) - cc0 - 2, max(c[1] for c in cs_) - cc0 + 3
                for L in Ls:
                    passable[L][max(rr0, 0):rr1, max(cl0, 0):cl1] = True
            starts = {(L, c0[0] - r0, c0[1] - cc0) for L in sL}
            targets = {(L, c1[0] - r0, c1[1] - cc0) for L in eL}
            nov = [(c0[0] - r0, c0[1] - cc0), (c1[0] - r0, c1[1] - cc0)]  # 탈출점 1.2mm 안에는 쌍 비아 금지
            path = B.astar(win, starts, targets, passable, viaok, layers, via_cost=60.0, pair_off=(VIA["dia"] + 0.25) / 2 / G,
                           start_dir=sd, end_dir=ed, cap=3_000_000, no_via_near=(nov, 1.2 / G), min_run=6)
            if not path:
                diag = {f"start L{L}": bool(passable[L][r, c]) for L, r, c in starts} | \
                       {f"end L{L}": bool(passable[L][r, c]) for L, r, c in targets}
                print(f"  {name} 진단({ea}.{ena}/{eb}.{enb}): S_far {tuple(round(float(v), 2) for v in S_far)} "
                      f"E_far {tuple(round(float(v), 2) for v in E_far)} 방향 {DIRS[sd]}→{DIRS[ed]} 통과 {diag}")
                last_reason = None
                continue
            segs = B.corners([(L, r + r0, c + cc0, d) for L, r, c, d in path])
            segsW = [(L, [B.xy(*q) for q in cells]) for L, cells in segs]
            segsW[0] = (segsW[0][0], [S] + segsW[0][1])
            segsW[-1] = (segsW[-1][0], segsW[-1][1] + [E])
            esc0 = {q["net"]: (q["pos"][0] + u0[0] * (hl0 + 0.15), q["pos"][1] + u0[1] * (hl0 + 0.15)) for q in (P0, N0)}
            esc1 = {q["net"]: (q["pos"][0] + u1[0] * (hl1 + 0.15), q["pos"][1] + u1[1] * (hl1 + 0.15)) for q in (P1, N1)}
            return {"name": name, "P": pn, "N": nn, "w": w, "half": (w + gap + 0.01) / 2, "hw": hw, "own": own, "segs": segsW,
                    "sideP": sideP, "P0": P0, "N0": N0, "P1": P1, "N1": N1, "esc0": esc0, "esc1": esc1, "brk": brks,
                    "end": f"{ea}.{ena}/{eb}.{enb}"}
        return last_reason

    def draw_pair(info, add=True):
        """중심선(segs) → P/N 트랙·쌍 비아·GND 귀환 비아. add=False 면 길이만 계산."""
        pn, nn, w, half, sideP = info["P"], info["N"], info["w"], info["half"], info["sideP"]
        segs = info["segs"]
        lens = {pn: 0.0, nn: 0.0}
        prev_end = {pn: info["P0"]["pos"], nn: info["N0"]["pos"]}
        nvias = 0
        for k, (L, pts) in enumerate(segs):
            for net, sgn in ((pn, sideP), (nn, -sideP)):
                op = offset_poly(pts, sgn * half) if len(pts) > 1 else [pts[0]]
                chain = [tuple(prev_end[net])] + ([tuple(info["esc0"][net])] if k == 0 else []) + op
                if k == len(segs) - 1:
                    chain += [tuple(info["esc1"][net]), tuple((info["P1"] if net == pn else info["N1"])["pos"])]
                if add:
                    for a, b in zip(chain[:-1], chain[1:]):
                        B.add_track(net, L, (round(a[0], 4), round(a[1], 4)), (round(b[0], 4), round(b[1], 4)), w)
                lens[net] += plength(chain)
                prev_end[net] = op[-1]
            if k < len(segs) - 1:  # 쌍 비아 + GND 귀환 비아
                nvias += 1
                cpt = pts[-1]
                vv = np.subtract(pts[-1], pts[-2]) if len(pts) > 1 else np.array([1.0, 0.0])
                nn_ = np.array([-vv[1], vv[0]]) / (np.linalg.norm(vv) or 1)
                off = (VIA["dia"] + 0.25) / 2
                for net, sgn in ((pn, sideP), (nn, -sideP)):
                    vp = (round(cpt[0] + nn_[0] * sgn * off, 4), round(cpt[1] + nn_[1] * sgn * off, 4))
                    if add:
                        B.add_track(net, L, tuple(prev_end[net]), vp, w)
                        B.add_via(net, vp, VIA)
                    lens[net] += math.dist(prev_end[net], vp)
                    prev_end[net] = vp
                if add and "/GND" in B.netid:
                    for sgn in (1, -1):
                        gp = (round(cpt[0] + nn_[0] * sgn * (off + VIA["dia"] + 0.25), 4),
                              round(cpt[1] + nn_[1] * sgn * (off + VIA["dia"] + 0.25), 4))
                        r, c = B.cell(*gp)
                        ok = all(not np.any((B.occ[Lx, r - 9:r + 10, c - 9:c + 10] != 0) &
                                            (B.occ[Lx, r - 9:r + 10, c - 9:c + 10] != B.netid["/GND"])) for Lx in range(4))
                        ok &= all(math.dist(gp, v["pos"]) >= VIA["dia"] + 0.25 for v in B.vias)  # 겹친 GND 비아 방지
                        if ok:
                            B.add_via("/GND", gp, VIA)
        return lens, nvias

    def with_bumps(info, need):
        """가장 긴 B.Cu(없으면 아무 층) 직선 구간에 45° 굴곡을 넣어 중심선 길이를 need 만큼 늘린 segs. 간격 검사 통과한 것만."""
        h, s = 0.6, 0.4
        per = 2 * h * math.sqrt(2) - 2 * h
        k = max(1, math.ceil(need / per))
        hw_ = info["hw"]
        cand = []
        for si, (L, pts) in enumerate(info["segs"]):
            for ei in range(len(pts) - 1):
                a, b = np.array(pts[ei]), np.array(pts[ei + 1])
                cand.append((math.dist(a, b) + (0.5 if L == 3 else 0), si, ei))
        for _, si, ei in sorted(cand, reverse=True):
            L, pts = info["segs"][si]
            a, b = np.array(pts[ei]), np.array(pts[ei + 1])
            Ls = math.dist(a, b)
            gsp = 0.3  # 굴곡 사이 직선 (90° 꺾임 방지)
            for kk in range(k, 0, -1):
                hh = need / (kk * (2 * math.sqrt(2) - 2))
                foot = kk * (2 * hh + s) + (kk - 1) * gsp
                if hh < 0.25 or hh > 1.2 or foot + 1.0 > Ls:
                    continue
                u = (b - a) / Ls
                for side in (1, -1):
                    nrm = np.array([-u[1], u[0]]) * side
                    p = a + u * (Ls - foot) / 2
                    new = [tuple(a)]
                    for j in range(kk):
                        q1 = p + u * hh + nrm * hh
                        q2 = q1 + u * s
                        q3 = q2 + u * hh - nrm * hh
                        new += [tuple(p), tuple(q1), tuple(q2), tuple(q3)]
                        p = q3 + u * gsp
                    new.append(tuple(b))
                    # 간격 검사: 굴곡 바깥 끝(+반폭+고속 간격)까지 다른 넷 구리가 없어야
                    ok = True
                    for t in np.linspace(0, 1, 60):
                        for (x0, y0), (x1, y1) in zip(new[:-1], new[1:]):
                            x, y = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
                            r, c = B.cell(x, y)
                            m = int((hw_ + HS_CLR + EPS) / G) + 1
                            blk = B.occ[L, r - m:r + m + 1, c - m:c + m + 1]
                            if np.any((blk != 0) & ~np.isin(blk, list(info["own"]))):
                                ok = False
                                break
                        if not ok:
                            break
                    if ok:
                        segs = [list(x) for x in info["segs"]]
                        segs[si][1] = pts[:ei] + new + pts[ei + 2:]
                        return [(x[0], x[1]) for x in segs]
        return None

    infos = []
    for spec in PAIRS[board_name]:
        info = route_pair(spec)
        if info is None or info == "side":
            B.failed.append(spec[0] + ("(P/N 좌우)" if info == "side" else ""))
            print(f"쌍 {spec[0]}: {'P/N 좌우가 두 끝에서 다름' if info == 'side' else '실패'}")
            continue
        lens, nv = draw_pair(info)
        info["lens"], info["nvias"] = lens, nv
        infos.append(info)
    # CSI 레인 길이 맞춤: 비아 높이(약 1.5mm/비아, KiCad use_height_for_length_calcs)를 넣은 길이를 가장 긴 레인에 맞춘다
    csi = [i for i in infos if i["name"].startswith("CSI")]
    if csi:
        def eff(i):
            return (i["lens"][i["P"]] + i["lens"][i["N"]]) / 2 + 1.5 * i["nvias"]
        target = max(eff(i) for i in csi)
        for i in csi:
            need = target - eff(i)
            if need < 0.3:
                continue
            segs = with_bumps(i, need)
            if not segs:
                print(f"쌍 {i['name']}: 길이 맞춤 자리 없음 (모자람 {need:.2f} mm)")
                continue
            # 트랙·비아 지우고(그 넷만) 굴곡 경로로 다시 그림
            ids = i["own"]
            B.tracks = [t for t in B.tracks if t["net"] not in (i["P"], i["N"])]
            B.vias = [v for v in B.vias if v["net"] not in (i["P"], i["N"])]
            for L in range(4):
                B.occ[L][np.isin(B.occ[L], list(ids))] = 0
            for p in B.pads:
                if p["id"] in ids:
                    for ln, polys in p["polys"].items():
                        for poly in polys:
                            B.raster_poly(LAYERS.index(ln), poly, p["id"])
            i["segs"] = segs
            i["lens"], i["nvias"] = draw_pair(i)
            print(f"쌍 {i['name']}: 길이 맞춤 +{need:.2f} mm")
    # 쌍 안 길이 보정: 짧은 선에만 짝 반대쪽으로 45° 굴곡 (꺾임 방향 차이로 생긴 P/N 길이차 — 45°마다 약 2·반간격·tan22.5°)
    INTRA = {"CSI_100": 0.15, "USB_90": 0.15, "MDI_100": 1.27}
    tune_areas = []
    for i in infos:
        lim = INTRA[netclass(i["P"])["name"]]
        diff = i["lens"][i["P"]] - i["lens"][i["N"]]
        if abs(diff) <= lim:
            continue
        short, partner = (i["P"], i["N"]) if diff < 0 else (i["N"], i["P"])
        need = abs(diff)
        w = i["w"]
        hh, top, gsp = 0.45, 0.3, 0.3
        per = 2 * hh * (math.sqrt(2) - 1)  # 굴곡 하나가 더하는 길이
        unit = 2 * hh + top + gsp
        pid = B.netid[partner]
        placed = 0
        # 긴 직선부터, 들어가는 만큼 굴곡을 나눠 넣는다
        for t in sorted([t for t in B.tracks if t["net"] == short], key=lambda t: -math.dist(t["a"], t["b"])):
            if need <= lim / 2:
                break
            a, b = np.array(t["a"]), np.array(t["b"])
            Ls = math.dist(a, b)
            kmax = int((Ls - 0.8 + gsp) / unit)
            if kmax < 1:
                break
            k = min(kmax, math.ceil(need / per))
            hk = min(hh, need / (k * 2 * (math.sqrt(2) - 1)))
            foot = k * (2 * hk + top) + (k - 1) * gsp
            L = LAYERS.index(t["layer"])
            u = (b - a) / Ls
            nrm = np.array([-u[1], u[0]])
            m = (a + b) / 2
            r, c = B.cell(*(m + nrm * 2 * i["half"]))
            nrm = nrm * (-1 if B.occ[L, r, c] == pid else 1)  # 짝이 있는 쪽의 반대
            p = a + u * (Ls - foot) / 2
            new = [tuple(a)]
            for j in range(k):
                q1 = p + u * hk + nrm * hk
                q2 = q1 + u * top
                q3 = q2 + u * hk - nrm * hk
                new += [tuple(p), tuple(q1), tuple(q2), tuple(q3)]
                p = q3 + u * gsp
            new.append(tuple(b))
            ok = True
            mrg = int((w / 2 + HS_CLR + EPS) / G) + 1
            for (x0, y0), (x1, y1) in zip(new[:-1], new[1:]):
                for tt in np.linspace(0, 1, 30):
                    rr, cc = B.cell(x0 + (x1 - x0) * tt, y0 + (y1 - y0) * tt)
                    blk = B.occ[L, rr - mrg:rr + mrg + 1, cc - mrg:cc + mrg + 1]
                    if np.any((blk != 0) & (blk != B.netid[short]) & (blk != pid)):
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                continue
            B.tracks.remove(t)
            for x0y0, x1y1 in zip(new[:-1], new[1:]):
                B.add_track(short, L, (round(x0y0[0], 4), round(x0y0[1], 4)), (round(x1y1[0], 4), round(x1y1[1], 4)), w)
            add = sum(math.dist(p_, q_) for p_, q_ in zip(new[:-1], new[1:])) - Ls
            i["lens"][short] += add
            need -= add
            placed += k
            xs = [q[0] for q in new]
            ys = [q[1] for q in new]
            tune_areas.append({"name": "DP_TUNE", "layer": LAYERS[L], "rect": [min(xs) - 0.3, min(ys) - 0.3, max(xs) + 0.3, max(ys) + 0.3]})
        if placed:
            print(f"쌍 {i['name']}: 쌍 안 보정 {short} 굴곡 {placed}개 · 남은 차 {max(need, 0):.2f} mm")
        if need > lim:
            print(f"쌍 {i['name']}: 쌍 안 보정 자리 없음 (차 {need:.2f} mm)")
    for i in infos:
        report["pairs"].append({"pair": i["name"], "P": i["P"], "N": i["N"], "len_P": round(i["lens"][i["P"]], 3),
                                "len_N": round(i["lens"][i["N"]], 3), "skew": round(abs(i["lens"][i["P"]] - i["lens"][i["N"]]), 3),
                                "vias": i["nvias"], "layers": [LAYERS[L] for L, _ in i["segs"]]})
        print(f"쌍 {i['name']}: 층 {[LAYERS[L] for L, _ in i['segs']]} · P {i['lens'][i['P']]:.2f} · N {i['lens'][i['N']]:.2f} · "
              f"차 {abs(i['lens'][i['P']] - i['lens'][i['N']]):.3f} mm · 비아 {i['nvias']}")

    if len(sys.argv) > 4 and sys.argv[4] == "pairs":  # 디버그: 쌍만
        json.dump({"tracks": B.tracks, "vias": B.vias, "failed": B.failed, "report": report,
                "areas": [{"name": "DP_BRK", "layer": ln, "rect": list(r)} for i in infos for ln, r in i["brk"]] + tune_areas, "zones": th_zones, "masks": th_masks}, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        return
    # 2) 단선 넷 (GND 제외, 쌍 넷의 남은 패드 포함)
    pair_nets = {x for p in PAIRS[board_name] for x in (p[1], p[2])}
    nets = {}
    for p in B.pads:
        if p["id"] > 0:
            nets.setdefault(p["net"], []).append(p)
    order = sorted((n for n in nets if n != "/GND" and len(nets[n]) > 1),
                   key=lambda n: (netclass(n)["name"] not in ("PWR_12V_IN", "PWR_5V", "PWR_12V_IR"), len(nets[n])))

    def connect(net, nxt, widths, layers, vtype, margin, cap):
        """패드 nxt 를 그 넷의 이미 이어진 구리(나무)에 잇는다. 성공하면 True."""
        own = {B.netid[net]}
        tree_cells = set()
        for L in range(4):
            rs, cs = np.nonzero(B.occ[L] == B.netid[net])
            tree_cells |= {(L, r, c) for r, c in zip(rs, cs)}
        mine = pad_cells(nxt, layers)
        tree_cells -= mine
        if not tree_cells:
            return False
        tc = np.array([(r, c) for _, r, c in tree_cells])
        pr, pc = B.cell(*nxt["pos"])
        k = int(np.argmin((tc[:, 0] - pr) ** 2 + (tc[:, 1] - pc) ** 2))
        near = (int(tc[k, 0]), int(tc[k, 1]))
        for w in widths:
            win = B.window([(pr, pc), near], margin)
            passable, viaok = B.free_maps(win, own, w / 2, vtype["dia"] / 2, layers)
            r0, r1, c0, c1 = win
            starts = {(L, r - r0, c - c0) for L, r, c in mine if r0 <= r <= r1 and c0 <= c <= c1}
            targets = {(L, r - r0, c - c0) for L, r, c in tree_cells if L in layers and r0 <= r <= r1 and c0 <= c <= c1}
            path = B.astar(win, starts, targets, passable, viaok, layers, cap=cap) if starts and targets else None
            if not path:
                continue
            segs = B.corners([(L, r + r0, c + c0, d) for L, r, c, d in path])
            for kk, (L, cells) in enumerate(segs):
                pts = [B.xy(*p) for p in cells]
                for a, b in zip(pts[:-1], pts[1:]):
                    B.add_track(net, L, a, b, w)
                if kk < len(segs) - 1:
                    B.add_via(net, pts[-1], vtype)
            return True
        return False

    retry = []
    for net in order:
        nc = netclass(net)
        pads = nets[net]
        hs = nc["name"] in HS
        layers = [0, 3] if hs else [0, 3, 2]
        widths = [nc["track_width"]]
        minw = {"PWR_12V_IN": 0.8, "PWR_12V_IR": 0.55, "PWR_5V": 0.3}.get(nc["name"], 0.15)
        if minw < widths[0]:
            widths += sorted({max(minw, widths[0] / 2), minw}, reverse=True)
        elif nc["name"] == "Default":
            widths.append(0.15)
        own = {B.netid[net]}
        vtype = VIA_PWR if nc["name"].startswith("PWR_") and nc["name"] != "PWR_LOGIC" else VIA
        # 나무: 쌍 넷이면 이미 깐 트랙에서 시작
        if net in pair_nets:
            tree_pads = [p for p in pads if any(math.dist(p["pos"], t["a"]) < 0.05 or math.dist(p["pos"], t["b"]) < 0.05
                                                 for t in B.tracks if t["net"] == net)]
        else:
            tree_pads = []
        if not tree_pads:
            cx = sum(p["pos"][0] for p in pads) / len(pads)
            cy = sum(p["pos"][1] for p in pads) / len(pads)
            tree_pads = [min(pads, key=lambda p: math.dist(p["pos"], (cx, cy)))]
        todo = [p for p in pads if p not in tree_pads]
        ok_n, fail_n = 0, 0
        while todo:
            # 나무에서 가장 가까운 패드
            tpos = [p["pos"] for p in tree_pads] + [t["a"] for t in B.tracks if t["net"] == net] + [t["b"] for t in B.tracks if t["net"] == net]
            nxt = min(todo, key=lambda p: min(math.dist(p["pos"], q) for q in tpos))
            todo.remove(nxt)
            if connect(net, nxt, widths, layers, vtype, 4.0, 200_000):
                ok_n += 1
                tree_pads.append(nxt)
            else:
                fail_n += 1
                retry.append((net, nxt, widths[-1:], layers, vtype))
        report["nets"][net] = {"ok": ok_n, "fail": fail_n}
        print(f"{net:22s} {nc['name']:10s} 연결 {ok_n} 실패 {fail_n}")
    # 2차: 실패한 연결을 넓은 창(10mm)·큰 상한·최소 폭으로 다시
    for net, nxt, widths, layers, vtype in retry:
        if connect(net, nxt, widths, layers, vtype, 10.0, 1_500_000):
            report["nets"][net]["ok"] += 1
            report["nets"][net]["fail"] -= 1
            print(f"2차 연결 {net} {nxt['ref']}.{nxt['num']}")
        else:
            B.failed.append(f"{net} {nxt['ref']}.{nxt['num']}")

    # 3) GND 비아 (SMD GND 패드마다)
    gnd_ok = gnd_fail = 0
    if "/GND" in B.netid:
        gid = B.netid["/GND"]
        for p in B.pads:
            if p["net"] != "/GND" or p["drill"]:
                continue
            L = LAYERS.index(p["layers"][0])
            win = B.window([B.cell(*p["pos"])], 1.6)
            passable, viaok = B.free_maps(win, {gid}, 0.10, VIA["dia"] / 2, [L])
            r0, r1, c0, c1 = win
            starts = {(L, r - r0, c - c0) for L2, r, c in pad_cells(p, [L]) if r0 <= r <= r1 and c0 <= c <= c1}
            targets = {(L, r, c) for r, c in zip(*np.nonzero(viaok & passable[L]))}
            path = B.astar(win, starts, targets, passable, viaok, [L]) if targets and starts else None
            if not path:
                gnd_fail += 1
                continue
            cells = B.corners([(Lx, r + r0, c + c0, d) for Lx, r, c, d in path])[0][1]
            pts = [B.xy(*q) for q in cells]  # 첫 칸은 패드 안 (패드 중심에서 직선을 긋지 않는다)
            if len(pts) == 1:
                pts = pts * 2
            for a, b in zip(pts[:-1], pts[1:]):
                B.add_track("/GND", L, a, b, 0.2)
            B.add_via("/GND", pts[-1], VIA)
            gnd_ok += 1
    print(f"GND 패드 비아 {gnd_ok} · 자리 없음 {gnd_fail} (면 채움에 맡김)")
    out = {"tracks": B.tracks, "vias": B.vias, "failed": B.failed, "report": report,
                "areas": [{"name": "DP_BRK", "layer": ln, "rect": list(r)} for i in infos for ln, r in i["brk"]] + tune_areas,
                "zones": th_zones, "masks": th_masks}
    json.dump(out, open(sys.argv[3], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"트랙 {len(B.tracks)} · 비아 {len(B.vias)} · 실패 {len(B.failed)}")


if __name__ == "__main__":
    main()
