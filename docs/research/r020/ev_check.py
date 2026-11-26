#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""R-020 전기 가상 검증 (orch VD-001 조건 4).

보드 파일(.kicad_pcb)을 pcbnew 로 읽기 전용으로 열어 다음을 계산하고 한도와 비교한다.
  ① 차동쌍 임피던스  — 실측 선폭·쌍 간격 분포 + 보드 적층 → IPC-2141A 닫힌 식 + 솔더마스크 보정
  ② 차동쌍 길이     — 쌍 안 길이 차, CSI 레인 skew(클록 기준), 비결합 길이 (비아 높이 제외/포함)
  ③ 전원           — 주 경로 최소 선폭의 허용 전류(IPC-2152 곡선 맞춤, ΔT 10 K), 경로 비아 허용 전류, 경로 저항·전압 강하

실행 (KiCad 10 동봉 Python):
  python.exe -I ev_check.py --config ev_config.json --board carrier=<carrier.kicad_pcb> --board front=<front.kicad_pcb>
           [--json-out result.json] [--md-out result.md]

종료 코드 = 한도를 넘은 항목 수(최대 125). 0 = 판정한 항목 모두 통과.
「미배선」(패드가 한 덩어리로 이어지지 않은 넷)의 항목은 판정하지 않고 따로 센다 — 종료 코드에 넣지 않는다.
표준 라이브러리 + pcbnew 만 쓴다.
"""
import argparse
import hashlib
import heapq
import json
import math
import os
import sys

import pcbnew

RHO_CU_20C = 1.724e-8     # Ω·m, 구리 20 °C (IACS 100 %)
ALPHA_CU = 0.00393        # 1/K
MIL = 0.0254              # mm


# ---------------------------------------------------------------- 공식
def ipc2141_microstrip_z0(w, h, t, er):
    """IPC-2141A 표면 마이크로스트립 단선 Z0 (마스크 없음). 길이 단위는 같기만 하면 된다."""
    return 87.0 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))


def ipc2141_microstrip_zdiff(w, s, h, t, er):
    """IPC-2141A edge-coupled microstrip: Zdiff = 2·Z0·(1 − 0.48·e^(−0.96·s/h))."""
    return 2.0 * ipc2141_microstrip_z0(w, h, t, er) * (1.0 - 0.48 * math.exp(-0.96 * s / h))


def ipc2141_stripline_z0(w, b, t, er):
    """IPC-2141A 대칭 스트립라인: Z0 = 60/√εr · ln(1.9·b/(0.8w+t)), b = 기준면 사이 거리."""
    return 60.0 / math.sqrt(er) * math.log(1.9 * b / (0.8 * w + t))


def ipc2141_stripline_zdiff(w, s, b, t, er):
    """IPC-2141A edge-coupled stripline: Zdiff = 2·Z0·(1 − 0.347·e^(−2.9·s/b))."""
    return 2.0 * ipc2141_stripline_z0(w, b, t, er) * (1.0 - 0.347 * math.exp(-2.9 * s / b))


def ipc2152_area_mil2(i_a, dt_k):
    """IPC-2152 Figure 5-2 범용 곡선 맞춤 (smps.us): A[mil²] = (117.555·ΔT^-0.913 + 1.15)·I^(0.84·ΔT^-0.108 + 1.159)."""
    return (117.555 * dt_k ** -0.913 + 1.15) * i_a ** (0.84 * dt_k ** -0.108 + 1.159)


def ipc2152_current_a(area_mm2, dt_k):
    """위 식의 역: 단면적 → ΔT 에서 허용 전류."""
    a = area_mm2 / (MIL * MIL)
    k = 117.555 * dt_k ** -0.913 + 1.15
    e = 0.84 * dt_k ** -0.108 + 1.159
    return (a / k) ** (1.0 / e)


def ipc2152_dt_k(i_a, area_mm2):
    """주어진 전류에서 IPC-2152 곡선 맞춤의 온도 상승 (이분법, 1~100 K)."""
    lo, hi = 0.5, 200.0
    if ipc2152_current_a(area_mm2, hi) < i_a:
        return float('inf')
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if ipc2152_current_a(area_mm2, mid) >= i_a:
            hi = mid
        else:
            lo = mid
    return hi


def ipc2221_current_a(area_mm2, dt_k, outer):
    """IPC-2221 (참고·보수 대안): I = k·ΔT^0.44·A^0.725, k = 0.048 외층 / 0.024 내층, A mil²."""
    k = 0.048 if outer else 0.024
    return k * dt_k ** 0.44 * (area_mm2 / (MIL * MIL)) ** 0.725


def via_barrel_area_mm2(drill_mm, plating_mm):
    """도금 원통 단면적 = π·t·(d − t), d = 드릴 지름(도금 전), t = 도금 두께."""
    return math.pi * plating_mm * (drill_mm - plating_mm)


# ---------------------------------------------------------------- 적층
def _sexpr_block(text, key):
    i = text.find('(' + key)
    if i < 0:
        return None
    depth = 0
    for j in range(i, len(text)):
        c = text[j]
        if c == '(':
            depth += 1
        elif c == ')':
            depth -= 1
            if depth == 0:
                return text[i:j + 1]
    return None


def _tokenize(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in '()':
            out.append(c); i += 1
        elif c.isspace():
            i += 1
        elif c == '"':
            j = i + 1
            while s[j] != '"':
                j += 2 if s[j] == '\\' else 1
            out.append(s[i + 1:j]); i = j + 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in '()':
                j += 1
            out.append(s[i:j]); i = j
    return out


def _parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == '(':
            stack.append([])
        elif t == ')':
            x = stack.pop(); stack[-1].append(x)
        else:
            stack[-1].append(t)
    return stack[0][0]


def read_stackup(path):
    """보드 파일의 (setup (stackup …)) 을 그대로 읽는다. 위에서 아래 순서의 층 목록과 구리층 z(위면 기준, mm)."""
    with open(path, encoding='utf-8') as f:
        text = f.read()
    blk = _sexpr_block(text, 'stackup')
    if blk is None:
        raise SystemExit('stackup 블록이 없다: ' + path)
    tree = _parse(_tokenize(blk))
    layers = []
    for item in tree[1:]:
        if isinstance(item, list) and item and item[0] == 'layer':
            d = {'name': item[1]}
            for sub in item[2:]:
                if isinstance(sub, list) and len(sub) >= 2:
                    d[sub[0]] = sub[1]
            layers.append(d)
    z = 0.0
    cu = {}
    stack = []
    for d in layers:
        typ = d.get('type', '')
        th = float(d.get('thickness', 0) or 0)
        if typ == 'copper' or typ in ('core', 'prepreg') or 'dielectric' in d['name']:
            entry = {'name': d['name'], 'type': typ, 'thickness': th,
                     'er': float(d['epsilon_r']) if 'epsilon_r' in d else None, 'z_top': z, 'z_bot': z + th,
                     'material': d.get('material', '')}
            stack.append(entry)
            if typ == 'copper':
                cu[d['name']] = entry
            z += th
        elif 'Mask' in d['name']:
            pass
    masks = {d['name']: {'thickness': float(d.get('thickness', 0) or 0),
                         'er': float(d['epsilon_r']) if 'epsilon_r' in d else None}
             for d in layers if 'Mask' in d['name']}
    return {'stack': stack, 'copper': cu, 'mask': masks, 'total': z, 'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}


def line_geometry(stk, cu_name):
    """신호층의 기준면 거리·εr·구리 두께. 외층 → 마이크로스트립, 내층 → 스트립라인."""
    st = stk['stack']
    idx = next(i for i, e in enumerate(st) if e['name'] == cu_name)
    t = st[idx]['thickness']
    above = st[idx - 1] if idx > 0 else None
    below = st[idx + 1] if idx + 1 < len(st) else None
    outer = above is None or below is None
    if outer:
        diel = below if above is None else above
        return {'kind': 'microstrip', 'h': diel['thickness'], 'er': diel['er'], 't': t, 'dielectric': diel['name']}
    # 스트립라인: 위·아래 유전체 (대칭 가정 b = h1 + t + h2, εr 두께 가중 평균)
    b = above['thickness'] + t + below['thickness']
    er = (above['er'] * above['thickness'] + below['er'] * below['thickness']) / (above['thickness'] + below['thickness'])
    return {'kind': 'stripline', 'b': b, 'er': er, 't': t, 'dielectric': above['name'] + '+' + below['name']}


# ---------------------------------------------------------------- 보드 읽기
def nm2mm(v):
    return v / 1e6


class Board:
    def __init__(self, key, path):
        self.key = key
        self.path = os.path.abspath(path)
        with open(path, 'rb') as f:
            self.sha256 = hashlib.sha256(f.read()).hexdigest()
        self.b = pcbnew.LoadBoard(path)
        self.stk = read_stackup(path)
        self.cu_ids = list(self.b.GetEnabledLayers().CuStack())
        self.std = {l: pcbnew.BOARD.GetStandardLayerName(l) for l in self.cu_ids}
        self.disp = {l: self.b.GetLayerName(l) for l in self.cu_ids}
        self.outer = {pcbnew.F_Cu, pcbnew.B_Cu}
        self.tracks = {}
        self.vias = {}
        for t in self.b.GetTracks():
            n = t.GetNetname()
            if t.GetClass() == 'PCB_VIA':
                self.vias.setdefault(n, []).append(t)
            else:
                self.tracks.setdefault(n, []).append(t)
        self.pads = {}
        for fp in self.b.GetFootprints():
            for p in fp.Pads():
                if p.GetNetname():
                    self.pads.setdefault(p.GetNetname(), []).append((fp.GetReference(), p))
        self.zones = {}
        self.rule_areas = []
        for z in self.b.Zones():
            if z.GetIsRuleArea():
                self.rule_areas.append(z)
            elif z.GetNetname():
                self.zones.setdefault(z.GetNetname(), []).append(z)

    def z_center(self, layer_id):
        e = self.stk['copper'][self.std[layer_id]]
        return 0.5 * (e['z_top'] + e['z_bot'])

    def cu_thick(self, layer_id):
        return self.stk['copper'][self.std[layer_id]]['thickness']

    def via_layers(self, v):
        return [l for l in self.cu_ids if v.IsOnLayer(l)]

    def pad_layers(self, p):
        return [l for l in self.cu_ids if p.IsOnLayer(l)]


def seg_xy(t):
    s, e = t.GetStart(), t.GetEnd()
    return (nm2mm(s.x), nm2mm(s.y)), (nm2mm(e.x), nm2mm(e.y))


def track_len(t):
    if t.GetClass() == 'PCB_ARC':
        return nm2mm(t.GetLength())
    (x1, y1), (x2, y2) = seg_xy(t)
    return math.hypot(x2 - x1, y2 - y1)


def proj_param(p, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return 0.0, math.hypot(p[0] - ax, p[1] - ay)
    u = ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2
    uc = min(1.0, max(0.0, u))
    qx, qy = ax + uc * dx, ay + uc * dy
    return uc, math.hypot(p[0] - qx, p[1] - qy)


def V(p):
    return pcbnew.VECTOR2I(int(round(p[0] * 1e6)), int(round(p[1] * 1e6)))


# ---------------------------------------------------------------- 넷 그래프 (저항망)
class NetGraph:
    """한 넷의 트랙·비아·패드·구리면을 저항 그래프로 만든다. 노드 사이 간선 = (저항 Ω, 정보)."""

    def __init__(self, bd, net, plating_mm):
        self.bd, self.net = bd, net
        self.adj = {}
        self.edges = []
        self.node_info = {}
        self.n = 0
        self.plating = plating_mm
        tracks = bd.tracks.get(net, [])
        vias = bd.vias.get(net, [])
        pads = bd.pads.get(net, [])
        zones = bd.zones.get(net, [])
        self.pad_node = {}
        for ref, p in pads:
            nid = self._new(('pad', ref, p.GetNumber()))
            self.pad_node[(ref, p.GetNumber())] = nid
        self.via_nodes = []
        for v in vias:
            ls = bd.via_layers(v)
            pos = (nm2mm(v.GetPosition().x), nm2mm(v.GetPosition().y))
            ids = {l: self._new(('via', pos, l)) for l in ls}
            drill = nm2mm(v.GetDrillValue())
            area = via_barrel_area_mm2(drill, plating_mm)
            for a, b in zip(ls, ls[1:]):
                dz = abs(bd.z_center(b) - bd.z_center(a))
                r = RHO_CU_20C * (dz * 1e-3) / (area * 1e-6)
                self._edge(ids[a], ids[b], r, {'kind': 'via', 'pos': pos, 'drill': drill, 'dz': dz,
                                               'dia': nm2mm(v.GetWidth(ls[0]))})
            self.via_nodes.append((v, pos, ids, drill))
        self.zone_nodes = []
        for z in zones:
            for l in bd.cu_ids:
                if z.IsOnLayer(l) and z.IsFilled():
                    self.zone_nodes.append((z, l, self._new(('zone', z.GetZoneName(), l))))
        # 트랙: 끝점 + 다른 항목이 닿는 점으로 잘라 간선을 만든다
        tol = 1e-3
        for t in tracks:
            l = t.GetLayer()
            a, b = seg_xy(t)
            w = nm2mm(t.GetWidth())
            L = track_len(t)
            pts = [(0.0, None), (1.0, None)]  # (param, 붙일 노드)
            for o in tracks:
                if o is t or o.GetLayer() != l:
                    continue
                for e in seg_xy(o):
                    u, d = proj_param(e, a, b)
                    if d <= w / 2 + tol:
                        pts.append((u, ('trk', id(o), e)))
            for v, pos, ids, drill in self.via_nodes:
                if l in ids:
                    u, d = proj_param(pos, a, b)
                    if d <= w / 2 + nm2mm(v.GetWidth(l)) / 2:
                        pts.append((u, ids[l]))
            for ref, p in pads:
                if l in bd.pad_layers(p):
                    for u in (0.0, 1.0):
                        q = (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))
                        if p.HitTest(V(q), int(w / 2 * 1e6), l):
                            pts.append((u, self.pad_node[(ref, p.GetNumber())]))
            for z, zl, zn in self.zone_nodes:
                if zl == l:
                    for u in (0.0, 1.0):
                        q = (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))
                        if z.HitTestFilledArea(l, V(q), int(w / 2 * 1e6)):
                            pts.append((u, zn))
            pts.sort(key=lambda x: x[0])
            # 같은 위치는 하나의 노드로
            chain = []
            for u, att in pts:
                if chain and abs(u - chain[-1][0]) * L <= tol:
                    node = chain[-1][1]
                else:
                    q = (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))
                    node = self._key_node((l, round(q[0], 3), round(q[1], 3)))
                    chain.append((u, node))
                if att is not None:
                    if isinstance(att, tuple):
                        e = att[2]
                        on = self._key_node((l, round(e[0], 3), round(e[1], 3)))
                        self._edge(node, on, 0.0, {'kind': 'join'})
                    else:
                        self._edge(node, att, 0.0, {'kind': 'join'})
            area = w * bd.cu_thick(l)
            for (u1, n1), (u2, n2) in zip(chain, chain[1:]):
                dl = (u2 - u1) * L
                r = RHO_CU_20C * (dl * 1e-3) / (area * 1e-6)
                self._edge(n1, n2, r, {'kind': 'track', 'layer': l, 'w': w, 'len': dl})
        # 비아·패드가 서로 겹치거나(비아 인 패드) 면 안에 있으면 잇는다
        for v, pos, ids, drill in self.via_nodes:
            for ref, p in pads:
                for l in bd.pad_layers(p):
                    if l in ids and p.HitTest(V(pos), 0, l):
                        self._edge(ids[l], self.pad_node[(ref, p.GetNumber())], 0.0, {'kind': 'join'})
            for z, zl, zn in self.zone_nodes:
                if zl in ids and z.HitTestFilledArea(zl, V(pos), int(nm2mm(v.GetWidth(zl)) / 2 * 1e6)):
                    self._edge(ids[zl], zn, 0.0, {'kind': 'join'})
        for ref, p in pads:
            pp = p.GetPosition()
            half = int(min(p.GetSizeX(), p.GetSizeY()) / 2)
            for z, zl, zn in self.zone_nodes:
                if zl in bd.pad_layers(p) and z.HitTestFilledArea(zl, pp, half):
                    self._edge(self.pad_node[(ref, p.GetNumber())], zn, 0.0, {'kind': 'join'})

    _keys = None

    def _new(self, info):
        nid = self.n
        self.n += 1
        self.adj[nid] = []
        self.node_info[nid] = info
        return nid

    def _key_node(self, key):
        if self._keys is None:
            self._keys = {}
        if key not in self._keys:
            self._keys[key] = self._new(('pt',) + key)
        return self._keys[key]

    def _edge(self, a, b, r, info):
        self.edges.append((a, b, r, info))
        self.adj[a].append((b, r, info))
        self.adj[b].append((a, r, info))

    def islands_of_pads(self):
        """패드끼리 몇 덩어리로 나뉘는가 → 미연결 수 = 덩어리 − 1."""
        parent = list(range(self.n))

        def f(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        for a, lst in self.adj.items():
            for b, r, info in lst:
                ra, rb = f(a), f(b)
                if ra != rb:
                    parent[ra] = rb
        groups = {}
        for k, nid in self.pad_node.items():
            groups.setdefault(f(nid), []).append(k)
        return list(groups.values())

    def shortest(self, srcs, dsts):
        """저항 최소 경로 (Dijkstra). 반환: (R, 간선 정보 목록) 또는 None."""
        dist = {s: 0.0 for s in srcs}
        prev = {}
        pq = [(0.0, s) for s in srcs]
        heapq.heapify(pq)
        target = set(dsts)
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist.get(u, float('inf')):
                continue
            if u in target:
                path = []
                while u in prev:
                    pu, info = prev[u]
                    path.append(info)
                    u = pu
                return d, list(reversed(path))
            for v, r, info in self.adj[u]:
                nd = d + r + 1e-12
                if nd < dist.get(v, float('inf')):
                    dist[v] = nd
                    prev[v] = (u, info)
                    heapq.heappush(pq, (nd, v))
        return None


# ---------------------------------------------------------------- 차동쌍
def coupled_intervals(seg, others, gap_cap):
    """seg 축 위에서 평행(±1°) 상대 트랙이 겹치는 구간과 간격(가장자리 사이). [(a,b,gap,w_other)] (mm 단위 축 거리)."""
    a, b = seg_xy(seg)
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    if L == 0:
        return [], 0.0
    ux, uy = dx / L, dy / L
    w = nm2mm(seg.GetWidth())
    out = []
    for o in others:
        if o.GetClass() == 'PCB_ARC' or o.GetLayer() != seg.GetLayer():
            continue
        c, e = seg_xy(o)
        ox, oy = e[0] - c[0], e[1] - c[1]
        Lo = math.hypot(ox, oy)
        if Lo == 0:
            continue
        if abs(ux * oy / Lo - uy * ox / Lo) > math.sin(math.radians(1.0)):
            continue
        t1 = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
        t2 = (e[0] - a[0]) * ux + (e[1] - a[1]) * uy
        lo, hi = max(0.0, min(t1, t2)), min(L, max(t1, t2))
        if hi - lo <= 1e-6:
            continue
        dperp = abs((c[0] - a[0]) * uy - (c[1] - a[1]) * ux)
        wo = nm2mm(o.GetWidth())
        gap = dperp - (w + wo) / 2
        if gap <= gap_cap:
            out.append((lo, hi, gap, wo))
    return out, L


def elementary(intervals, L):
    """겹치는 구간들을 잘게 나눠 각 조각의 최소 간격을 준다: [(a,b,gap|None,w_other)]."""
    cuts = sorted({0.0, L} | {x for iv in intervals for x in iv[:2]})
    res = []
    for a, b in zip(cuts, cuts[1:]):
        if b - a <= 1e-9:
            continue
        m = 0.5 * (a + b)
        cov = [iv for iv in intervals if iv[0] <= m <= iv[1]]
        if cov:
            best = min(cov, key=lambda iv: iv[2])
            res.append((a, b, best[2], best[3]))
        else:
            res.append((a, b, None, None))
    return res


def length_in_areas(seg, a_u, b_u, areas):
    """seg 의 축 구간 [a_u,b_u](mm) 중 규칙 영역 안 길이 (0.01 mm 표본)."""
    if not areas:
        return 0.0
    a, b = seg_xy(seg)
    L = math.hypot(b[0] - a[0], b[1] - a[1])
    if L == 0:
        return 0.0
    n = max(1, int((b_u - a_u) / 0.01))
    step = (b_u - a_u) / n
    inside = 0.0
    for k in range(n):
        u = (a_u + (k + 0.5) * step) / L
        q = (a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]))
        if any(z.Outline().Contains(V(q)) for z in areas):
            inside += step
    return inside


def analyse_pair(bd, pair, cfg):
    gap_cap_dist = cfg['gap_distribution_max_mm']
    gap_cpl = cfg['coupled_gap_max_mm']
    mask_dz = cfg['mask_correction']['zdiff_ohm']
    tw_areas = [z for z in bd.rule_areas if z.GetZoneName() in cfg.get('twist_area_names', [])]
    res = {'name': pair['name'], 'board': bd.key, 'p': pair['p'], 'n': pair['n'], 'target': pair['target'],
           'class': pair['class']}
    side = {}
    zlist = []  # (Zdiff_masked, len, layer, w, gap)
    gaps = []   # (gap, len, layer)
    for me, other in ((pair['p'], pair['n']), (pair['n'], pair['p'])):
        tr = bd.tracks.get(me, [])
        ot = bd.tracks.get(other, [])
        L_tr = sum(track_len(t) for t in tr)
        cpl = 0.0
        unc = 0.0
        unc_tw = 0.0
        widths = {}
        for t in tr:
            lname = bd.disp[t.GetLayer()]
            widths.setdefault(lname, set()).add(round(nm2mm(t.GetWidth()), 3))
            if t.GetClass() == 'PCB_ARC':
                unc += track_len(t)
                continue
            ivs, L = coupled_intervals(t, ot, gap_cap_dist)
            for a, b, g, wo in elementary(ivs, L):
                ln = b - a
                if g is not None and me == pair['p']:
                    gaps.append((g, ln, lname))
                if g is not None and g <= gap_cpl:
                    cpl += ln
                    if me == pair['p']:
                        geo = line_geometry(bd.stk, bd.std[t.GetLayer()])
                        w = 0.5 * (nm2mm(t.GetWidth()) + wo)
                        if geo['kind'] == 'microstrip':
                            z = ipc2141_microstrip_zdiff(w, g, geo['h'], geo['t'], geo['er']) + mask_dz
                        else:
                            z = ipc2141_stripline_zdiff(w, g, geo['b'], geo['t'], geo['er'])
                        zlist.append((z, ln, lname, w, g))
                else:
                    unc += ln
                    unc_tw += length_in_areas(t, a, b, tw_areas)
        # 비아 높이: 그 비아에서 이 넷 트랙이 닿는 가장 바깥 두 층 사이 z 거리
        vh_total = 0.0
        vh_unpaired = 0.0
        vias = bd.vias.get(me, [])
        ovias = bd.vias.get(other, [])
        for v in vias:
            pos = (nm2mm(v.GetPosition().x), nm2mm(v.GetPosition().y))
            r = nm2mm(v.GetWidth(pcbnew.F_Cu)) / 2
            used = set()
            for t in tr:
                for e in seg_xy(t):
                    if math.hypot(e[0] - pos[0], e[1] - pos[1]) <= r + nm2mm(t.GetWidth()) / 2:
                        used.add(t.GetLayer())
            for ref, p in bd.pads.get(me, []):
                for l in bd.pad_layers(p):
                    if p.HitTest(V(pos), int(r * 1e6), l):
                        used.add(l)
            h = 0.0
            if len(used) >= 2:
                zs = [bd.z_center(l) for l in used]
                h = max(zs) - min(zs)
            vh_total += h
            paired = any(math.hypot(nm2mm(o.GetPosition().x) - pos[0], nm2mm(o.GetPosition().y) - pos[1])
                         <= cfg['paired_via_max_mm'] for o in ovias)
            if not paired:
                vh_unpaired += h
        side[me] = {'len_track': L_tr, 'len_with_via': L_tr + vh_total, 'vias': len(vias), 'via_h': vh_total,
                    'coupled': cpl, 'uncoupled': unc, 'uncoupled_with_via': unc + vh_unpaired,
                    'uncoupled_in_twist': unc_tw, 'widths': {k: sorted(v) for k, v in widths.items()}}
    res['side'] = side
    P, N = side[pair['p']], side[pair['n']]
    res['mismatch_track'] = abs(P['len_track'] - N['len_track'])
    res['mismatch_with_via'] = abs(P['len_with_via'] - N['len_with_via'])
    res['uncoupled_max'] = max(P['uncoupled'], N['uncoupled'])
    res['uncoupled_max_with_via'] = max(P['uncoupled_with_via'], N['uncoupled_with_via'])
    res['uncoupled_outside_twist'] = max(P['uncoupled'] - P['uncoupled_in_twist'], N['uncoupled'] - N['uncoupled_in_twist'])
    res['uncoupled_outside_twist_with_via'] = max(P['uncoupled_with_via'] - P['uncoupled_in_twist'],
                                                  N['uncoupled_with_via'] - N['uncoupled_in_twist'])
    res['twist_len'] = max(P['uncoupled_in_twist'], N['uncoupled_in_twist'])
    # 간격 분포 (P 기준, 길이 가중)
    def wpct(items, q):
        items = sorted(items)
        tot = sum(l for _, l in items)
        acc = 0.0
        for v, l in items:
            acc += l
            if acc >= q * tot:
                return v
        return items[-1][0] if items else None
    dist = {}
    for lname in sorted({g[2] for g in gaps}):
        it = [(g, l) for g, l, ln in gaps if ln == lname]
        tot = sum(l for _, l in it)
        cp = [(g, l) for g, l in it if g <= gap_cpl]
        dist[lname] = {'len_le_cap': tot, 'len_coupled': sum(l for _, l in cp),
                       'min': min(g for g, _ in it), 'p50': wpct(it, 0.5), 'max': max(g for g, _ in it),
                       'coupled_min': min((g for g, _ in cp), default=None),
                       'coupled_max': max((g for g, _ in cp), default=None),
                       'coupled_mean': (sum(g * l for g, l in cp) / sum(l for _, l in cp)) if cp else None}
    res['gap_dist'] = dist
    tgt = pair['target']
    tol = cfg['impedance_tolerance']
    if zlist:
        tot = sum(l for _, l, *_ in zlist)
        res['z_min'] = min(z for z, *_ in zlist)
        res['z_max'] = max(z for z, *_ in zlist)
        res['z_mean'] = sum(z * l for z, l, *_ in zlist) / tot
        res['z_out_len'] = sum(l for z, l, *_ in zlist if abs(z - tgt) > tol * tgt)
        res['z_coupled_len'] = tot
        res['z_layers'] = sorted({x[2] for x in zlist})
    else:
        res['z_min'] = res['z_max'] = res['z_mean'] = None
        res['z_out_len'] = None
        res['z_coupled_len'] = 0.0
    return res


# ---------------------------------------------------------------- 전원
def _gauss_solve(A, b):
    """부분 피벗 가우스 소거 (표준 라이브러리만)."""
    n = len(b)
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(A[r][c]))
        if abs(A[p][c]) < 1e-30:
            raise ValueError('특이 행렬')
        if p != c:
            A[c], A[p] = A[p], A[c]
            b[c], b[p] = b[p], b[c]
        piv = A[c][c]
        rowc = A[c]
        for r in range(c + 1, n):
            f = A[r][c] / piv
            if f:
                rowr = A[r]
                for k in range(c, n):
                    rowr[k] -= f * rowc[k]
                b[r] -= f * b[c]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        x[r] = (b[r] - sum(A[r][k] * x[k] for k in range(r + 1, n))) / A[r][r]
    return x


def solve_network(g, src_nodes, sinks):
    """직류 저항망 해석. src_nodes 는 한 전위(0 V)로 묶고, sinks = [(노드 목록, 전류 A)] 각 묶음에서 전류가 나간다.
    반환: (간선 전류 목록 [(info, |I|)], 싱크 묶음별 강하 V, 도달 못 한 싱크 묶음 번호)."""
    parent = list(range(g.n))

    def f(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def u(a, b):
        ra, rb = f(a), f(b)
        if ra != rb:
            parent[ra] = rb
    for a, b, r, info in g.edges:
        if r <= 0:
            u(a, b)
    for x in src_nodes[1:]:
        u(src_nodes[0], x)
    for nodes, _ in sinks:
        for x in nodes[1:]:
            u(nodes[0], x)
    res_edges = [(f(a), f(b), r, info) for a, b, r, info in g.edges if r > 0 and f(a) != f(b)]
    adj = {}
    for a, b, r, info in res_edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    gnd = f(src_nodes[0])
    comp = {gnd}
    stack = [gnd]
    while stack:
        x = stack.pop()
        for y in adj.get(x, []):
            if y not in comp:
                comp.add(y)
                stack.append(y)
    reach = [i for i, (nodes, _) in enumerate(sinks) if f(nodes[0]) in comp]
    unreach = [i for i in range(len(sinks)) if i not in reach]
    idx = {nd: k for k, nd in enumerate(sorted(comp - {gnd}))}
    n = len(idx)
    A = [[0.0] * n for _ in range(n)]
    rhs = [0.0] * n
    for a, b, r, info in res_edges:
        if a not in comp:
            continue
        gc = 1.0 / r
        ia, ib = idx.get(a), idx.get(b)
        if ia is not None:
            A[ia][ia] += gc
        if ib is not None:
            A[ib][ib] += gc
        if ia is not None and ib is not None:
            A[ia][ib] -= gc
            A[ib][ia] -= gc
    for i in reach:
        nodes, cur = sinks[i]
        k = idx.get(f(nodes[0]))
        if k is not None:
            rhs[k] -= cur
    volt = _gauss_solve(A, rhs) if n else []

    def V(nd):
        return 0.0 if nd == gnd else volt[idx[nd]]
    currents = [(info, abs(V(a) - V(b)) / r) for a, b, r, info in res_edges if a in comp]
    drops = {i: -V(f(sinks[i][0][0])) for i in reach}
    return currents, drops, unreach


def analyse_power(bd, pw, cfg):
    dt = cfg['delta_t_k']
    plating = cfg['via_plating_mm']
    g = NetGraph(bd, pw['net'], plating)
    res = {'board': bd.key, 'net': pw['net'], 'i_worst': pw['i_worst_a'], 'i_source': pw['i_source']}
    # 넷 전체 층별 최소 선폭
    per_layer = {}
    for t in bd.tracks.get(pw['net'], []):
        ln = bd.disp[t.GetLayer()]
        w = round(nm2mm(t.GetWidth()), 3)
        d = per_layer.setdefault(ln, {'min_w': w, 'len_at_min': 0.0, 'len': 0.0, 'outer': t.GetLayer() in bd.outer})
        d['len'] += track_len(t)
        if w < d['min_w'] - 1e-9:
            d['min_w'], d['len_at_min'] = w, 0.0
        if abs(w - d['min_w']) < 1e-9:
            d['len_at_min'] += track_len(t)
    for ln, d in per_layer.items():
        th = bd.cu_thick(next(l for l in bd.cu_ids if bd.disp[l] == ln))
        d['cu_t'] = th
        d['i2152'] = ipc2152_current_a(d['min_w'] * th, dt)
        d['i2221'] = ipc2221_current_a(d['min_w'] * th, dt, d['outer'])
    res['per_layer'] = per_layer
    vias = bd.vias.get(pw['net'], [])
    res['via_count'] = len(vias)
    res['via_drills'] = sorted({round(nm2mm(v.GetDrillValue()), 3) for v in vias})
    islands = g.islands_of_pads()
    res['islands'] = len(islands)
    res['island_pads'] = [sorted('%s.%s' % k for k in isl) for isl in islands]

    def nodes_of(names):
        return [g.pad_node[tuple(x.split('.', 1))] for x in names if tuple(x.split('.', 1)) in g.pad_node]
    srcs = nodes_of(pw['sources'])
    groups = [nodes_of(grp) for grp in pw['sinks']]
    # 전류 배분: sink_currents 가 있으면 동시 해석, 없으면 묶음마다 전체 전류로 따로 풀어 간선별 최댓값(보수 포락)
    if 'sink_currents' in pw:
        cases = [[(groups[i], pw['sink_currents'][i]) for i in range(len(groups))]]
        mode = '동시(묶음별 %s A)' % '/'.join('%g' % c for c in pw['sink_currents'])
    else:
        cases = [[(groups[i], pw['i_worst_a'])] for i in range(len(groups))]
        mode = '묶음마다 %g A 포락' % pw['i_worst_a']
    res['mode'] = mode
    env_track = {}
    env_via = {}
    drops = {}
    unreach = set()
    tfac = 1 + ALPHA_CU * (cfg['hot_copper_c'] - 20.0)
    for ci, case in enumerate(cases):
        if not srcs or any(not nd for nd, _ in case):
            unreach |= {ci if len(cases) > 1 else i for i, (nd, _) in enumerate(case) if not nd}
            continue
        cur, dr, ur = solve_network(g, srcs, case)
        for i in ur:
            unreach.add(ci if len(cases) > 1 else i)
        for i, v in dr.items():
            drops[ci if len(cases) > 1 else i] = v * tfac
        for info, I in cur:
            if info['kind'] == 'track':
                key = id(info)
                if I > env_track.get(key, (0, None))[0]:
                    env_track[key] = (I, info)
            elif info['kind'] == 'via':
                key = info['pos']
                if I > env_via.get(key, (0, None))[0]:
                    env_via[key] = (I, info)
    # 선마다 이용률 = 흐르는 전류 / IPC-2152 허용
    rows = []
    for I, info in env_track.values():
        th = bd.cu_thick(info['layer'])
        cap = ipc2152_current_a(info['w'] * th, dt)
        rows.append({'w': info['w'], 'layer': bd.disp[info['layer']], 'len': info['len'], 'I': I, 'cap': cap,
                     'cap2221': ipc2221_current_a(info['w'] * th, dt, info['layer'] in bd.outer),
                     'util': I / cap, 'dt_at_I': ipc2152_dt_k(I, info['w'] * th) if I > 1e-9 else 0.0})
    res['track_worst'] = max(rows, key=lambda r: r['util']) if rows else None
    carrying = [r for r in rows if r['I'] >= 0.05 * pw['i_worst_a']]
    res['track_narrowest_carrying'] = min(carrying, key=lambda r: (r['w'], -r['I'])) if carrying else None
    vrows = []
    for I, info in env_via.values():
        area = via_barrel_area_mm2(info['drill'], plating)
        vrows.append({'pos': info['pos'], 'drill': info['drill'], 'I': I, 'cap': ipc2152_current_a(area, dt),
                      'cap2221_int': ipc2221_current_a(area, dt, False)})
    res['vias_carrying'] = sorted([v for v in vrows if v['I'] >= 0.01 * pw['i_worst_a']], key=lambda v: -v['I'])
    res['via_worst'] = max(vrows, key=lambda v: v['I'] / v['cap']) if vrows else None
    res['groups'] = []
    for i, grp in enumerate(pw['sinks']):
        sp = g.shortest(srcs, groups[i]) if srcs and groups[i] else None
        row = {'sinks': grp, 'reached': i not in unreach and sp is not None}
        if sp is not None:
            R, edges = sp
            trk = [e for e in edges if e['kind'] == 'track']
            row.update({'path_len': sum(e['len'] for e in trk), 'path_vias': len({e['pos'] for e in edges if e['kind'] == 'via'}),
                        'path_R20_mohm': R * 1e3,
                        'path_min_w': min((e['w'] for e in trk), default=None)})
        if i in drops:
            row['drop_mv'] = drops[i] * 1e3
        res['groups'].append(row)
    return res


# ---------------------------------------------------------------- 판정
def judge(pairs, powers, cfg, bdmap):
    items = []   # (영역, 대상, 지표, 값, 한도, 결과)  결과 ∈ 통과/불합격/미배선

    def add(area, target, metric, value, limit, ok, unrouted=False):
        items.append({'area': area, 'target': target, 'metric': metric, 'value': value, 'limit': limit,
                      'result': '미배선' if unrouted else ('통과' if ok else '불합격')})
    lim = cfg['limits']
    for r in pairs:
        bd = bdmap[r['board']]
        tag = '%s:%s' % (r['board'], r['name'])
        unr = r.get('unrouted', False)
        tgt, tol = r['target'], cfg['impedance_tolerance']
        if r['z_min'] is None:
            add('①임피던스', tag, 'Zdiff(결합 구간)', '결합 구간 없음', '%g±%d%%' % (tgt, tol * 100), False, unr)
        else:
            ok = r['z_out_len'] <= 1e-9
            add('①임피던스', tag, 'Zdiff 최소/평균/최대 Ω (마스크 보정)',
                '%.1f / %.1f / %.1f (±10%% 밖 %.3f mm)' % (r['z_min'], r['z_mean'], r['z_max'], r['z_out_len']),
                '%g ±%d%% (%.0f~%.0f)' % (tgt, tol * 100, tgt * (1 - tol), tgt * (1 + tol)), ok, unr)
        mm_lim = lim['intra_pair_mismatch_mm'] + lim['mismatch_numeric_tol_mm']
        m = max(r['mismatch_track'], r['mismatch_with_via'])
        add('②차동', tag, '쌍 안 길이 차 mm (트랙 / +비아)', '%.3f / %.3f' % (r['mismatch_track'], r['mismatch_with_via']),
            '%g (수치 허용 %g)' % (lim['intra_pair_mismatch_mm'], lim['mismatch_numeric_tol_mm']), m <= mm_lim, unr)
        ul = lim['uncoupled_mm'][r['class']]
        if r['class'] == 'MDI':
            u = max(r['uncoupled_outside_twist'], r['uncoupled_outside_twist_with_via'])
            add('②차동', tag, '비결합 mm, 꼬임 영역 밖 (트랙 / +비아)',
                '%.3f / %.3f' % (r['uncoupled_outside_twist'], r['uncoupled_outside_twist_with_via']), '≤ %g' % ul, u <= ul, unr)
            ut = lim['uncoupled_mm']['MDI_TWIST_TOTAL']
            u2 = max(r['uncoupled_max'], r['uncoupled_max_with_via'])
            add('②차동', tag, '비결합 mm, 꼬임 포함 전체 (트랙 / +비아)',
                '%.3f / %.3f' % (r['uncoupled_max'], r['uncoupled_max_with_via']), '≤ %g' % ut, u2 <= ut, unr)
        else:
            u = max(r['uncoupled_max'], r['uncoupled_max_with_via'])
            add('②차동', tag, '비결합 mm (트랙 / +비아)', '%.3f / %.3f' % (r['uncoupled_max'], r['uncoupled_max_with_via']),
                '≤ %g' % ul, u <= ul, unr)
    # CSI 레인 skew (클록 기준, 쌍 평균 길이)
    for grp in cfg.get('skew_groups', []):
        by = {r['name']: r for r in pairs if r['board'] == grp['board']}
        clk = by.get(grp['clock'])
        for ln in grp['lanes']:
            r = by.get(ln)
            if not r or not clk:
                continue
            unr = r.get('unrouted') or clk.get('unrouted')

            def avg(x, key):
                return 0.5 * (x['side'][x['p']][key] + x['side'][x['n']][key])
            s1 = abs(avg(r, 'len_track') - avg(clk, 'len_track'))
            s2 = abs(avg(r, 'len_with_via') - avg(clk, 'len_with_via'))
            add('②차동', '%s:%s-%s' % (grp['board'], ln, grp['clock']), '레인 skew mm (트랙 / +비아)',
                '%.3f / %.3f' % (s1, s2), '≤ %g' % lim['csi_lane_skew_mm'], max(s1, s2) <= lim['csi_lane_skew_mm'], unr)
    for p in powers:
        tag = '%s:%s' % (p['board'], p['net'])
        unr_net = p['islands'] > 1
        tw = p['track_worst']
        if tw is None:
            add('③전원', tag, '트랙 전류', '전류가 흐르는 트랙 없음', '—', False, True)
        else:
            add('③전원', tag, '최대 이용률 트랙 (w %.3f mm %s): 흐르는 A / IPC-2152 허용 A (ΔT%gK)' % (tw['w'], tw['layer'], cfg['delta_t_k']),
                '%.2f / %.2f (ΔT@I %.1f K, IPC-2221 %.2f)' % (tw['I'], tw['cap'], tw['dt_at_I'], tw['cap2221']),
                '흐르는 ≤ 허용', tw['I'] <= tw['cap'], unr_net)
        vw = p['via_worst']
        if vw is not None and vw['I'] > 0:
            add('③전원', tag, '최대 부하 비아 (드릴 %.2f, 도금 %g µm): 흐르는 A / 허용 A' % (vw['drill'], cfg['via_plating_mm'] * 1000),
                '%.2f / %.2f (IPC-2221 내층식 %.2f)' % (vw['I'], vw['cap'], vw['cap2221_int']),
                '흐르는 ≤ 허용', vw['I'] <= vw['cap'], unr_net)
        for grp in p['groups']:
            if not grp['reached']:
                add('③전원', tag + '→' + '+'.join(grp['sinks']), '경로', '연결 경로 없음', '—', False, True)
    return items


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--config', required=True)
    ap.add_argument('--board', action='append', required=True, help='키=경로 (예: carrier=carrier.kicad_pcb)')
    ap.add_argument('--json-out')
    ap.add_argument('--md-out')
    a = ap.parse_args(argv)
    with open(a.config, encoding='utf-8') as f:
        cfg = json.load(f)
    bdmap = {}
    for kv in a.board:
        k, p = kv.split('=', 1)
        bdmap[k] = Board(k, p)
    # 미배선: 넷마다 패드 덩어리 수 (KiCad 연결성 합계와 대조)
    unrouted_nets = {}
    for k, bd in bdmap.items():
        bd.b.BuildConnectivity()
        kicad_unc = bd.b.GetConnectivity().GetUnconnectedCount(True)
        mine = 0
        per = {}
        for net in set(bd.pads) | set(bd.tracks):
            if not net:
                continue
            isl = NetGraph(bd, net, cfg['via_plating_mm']).islands_of_pads()
            if len(isl) > 1:
                per[net] = len(isl) - 1
                if net not in bd.zones:
                    mine += len(isl) - 1
        # 구리면이 있는 넷(GND 등)은 면–패드 연결을 근사로만 보므로 합계 대조에서 뺀다
        unrouted_nets[k] = {'kicad_unconnected': kicad_unc, 'script_unconnected_no_zone_nets': mine, 'nets': per,
                            'zone_nets': sorted(bd.zones)}
    pairs = []
    for pr in cfg['pairs']:
        bd = bdmap.get(pr['board'])
        if bd is None:
            continue
        r = analyse_pair(bd, pr, cfg)
        r['unrouted'] = pr['p'] in unrouted_nets[pr['board']]['nets'] or pr['n'] in unrouted_nets[pr['board']]['nets']
        pairs.append(r)
    powers = [analyse_power(bdmap[pw['board']], pw, cfg) for pw in cfg['power'] if pw['board'] in bdmap]
    items = judge(pairs, powers, cfg, bdmap)
    fails = sum(1 for i in items if i['result'] == '불합격')
    unr = sum(1 for i in items if i['result'] == '미배선')
    # 참고: 공칭 형상 대조 (V-005 A6, P-001 §4.2)
    ref = []
    for bk, bd in bdmap.items():
        geo = line_geometry(bd.stk, 'F.Cu')
        for w, s in cfg['nominal_geometries']:
            z = ipc2141_microstrip_zdiff(w, s, geo['h'], geo['t'], geo['er'])
            ref.append({'board': bk, 'w': w, 's': s, 'zdiff_nomask': z, 'zdiff_mask': z + cfg['mask_correction']['zdiff_ohm']})
        break
    out = {'boards': {k: {'path': bd.path, 'sha256': bd.sha256, 'stackup': bd.stk['stack'], 'mask': bd.stk['mask'],
                          'geometry_F': line_geometry(bd.stk, 'F.Cu'), 'geometry_B': line_geometry(bd.stk, 'B.Cu'),
                          'layers': {bd.std[l]: bd.disp[l] for l in bd.cu_ids}} for k, bd in bdmap.items()},
           'unrouted': unrouted_nets, 'pairs': pairs, 'power': powers, 'items': items, 'nominal': ref,
           'fails': fails, 'unrouted_items': unr, 'pcbnew': pcbnew.Version()}
    # 사람이 읽는 요약
    print('R-020 전기 가상 검증 — pcbnew %s' % pcbnew.Version())
    for k, bd in bdmap.items():
        u = unrouted_nets[k]
        print('보드 %s sha256 %s  미연결(KiCad 전체) %d · (스크립트, 면 넷 %s 제외) %d · 미배선 넷 %d' %
              (k, bd.sha256, u['kicad_unconnected'], ','.join(u['zone_nets']), u['script_unconnected_no_zone_nets'], len(u['nets'])))
    for it in items:
        print('[%s] %-6s %-40s %s = %s (한도 %s)' % (it['result'], it['area'], it['target'], it['metric'], it['value'], it['limit']))
    print('불합격 %d · 미배선(판정 안 함) %d · 판정 항목 %d' % (fails, unr, len(items)))
    if a.json_out:
        with open(a.json_out, 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, indent=1, default=str)
    if a.md_out:
        write_md(a.md_out, out, cfg)
    return min(fails, 125)


def write_md(path, out, cfg):
    L = []
    L.append('<!-- ev_check.py 자동 출력 -->')
    L.append('### 입력 보드\n')
    L.append('| 키 | sha256 | 미연결 KiCad 전체 / 스크립트(면 넷 제외) | 미배선 넷 (스크립트, 넷별 미연결 수) |')
    L.append('|---|---|---|---|')
    for k, b in out['boards'].items():
        u = out['unrouted'][k]
        L.append('| %s | `%s` | %d / %d | %s |' % (k, b['sha256'], u['kicad_unconnected'], u['script_unconnected_no_zone_nets'],
                                                  ', '.join('%s(%d)' % (n, c) for n, c in sorted(u['nets'].items())) or '없음'))
    L.append('\n### 판정 항목\n')
    L.append('| 결과 | 영역 | 대상 | 지표 | 값 | 한도 |')
    L.append('|---|---|---|---|---|---|')
    for it in out['items']:
        L.append('| %s | %s | %s | %s | %s | %s |' % (it['result'], it['area'], it['target'], it['metric'], it['value'], it['limit']))
    L.append('\n### ① 쌍 간격·선폭 실측 분포 (P 기준 길이 가중, 간격 = 가장자리 사이)\n')
    L.append('| 쌍 | 층 | 선폭 P / N | 평행 구간(간격 ≤%g) mm | 결합(≤%g) mm | 결합 간격 최소/평균/최대 | 전체 간격 최소/중앙/최대 | Zdiff 최소/평균/최대 (마스크 %+g Ω) |' %
             (cfg['gap_distribution_max_mm'], cfg['coupled_gap_max_mm'], cfg['mask_correction']['zdiff_ohm']))
    L.append('|---|---|---|---|---|---|---|---|')
    for r in out['pairs']:
        P, N = r['side'][r['p']], r['side'][r['n']]
        for ln, d in r['gap_dist'].items():
            f = lambda x: '—' if x is None else '%.3f' % x
            L.append('| %s:%s | %s | %s / %s | %.2f | %.2f | %s / %s / %s | %s / %s / %s | %s |' % (
                r['board'], r['name'], ln, P['widths'].get(ln), N['widths'].get(ln), d['len_le_cap'], d['len_coupled'],
                f(d['coupled_min']), f(d['coupled_mean']), f(d['coupled_max']), f(d['min']), f(d['p50']), f(d['max']),
                '—' if r['z_min'] is None else '%.1f / %.1f / %.1f' % (r['z_min'], r['z_mean'], r['z_max'])))
    L.append('\n### ② 쌍 길이 (mm)\n')
    L.append('| 쌍 | P 트랙 / +비아 | N 트랙 / +비아 | 비아 P/N | 쌍 안 차 트랙 / +비아 | 비결합 P / N (트랙) | 비결합 최대 +짝없는 비아 | 꼬임 영역 안 비결합 |')
    L.append('|---|---|---|---|---|---|---|---|')
    for r in out['pairs']:
        P, N = r['side'][r['p']], r['side'][r['n']]
        L.append('| %s:%s | %.3f / %.3f | %.3f / %.3f | %d / %d | %.3f / %.3f | %.3f / %.3f | %.3f | %.3f |' % (
            r['board'], r['name'], P['len_track'], P['len_with_via'], N['len_track'], N['len_with_via'], P['vias'], N['vias'],
            r['mismatch_track'], r['mismatch_with_via'], P['uncoupled'], N['uncoupled'], r['uncoupled_max_with_via'], r['twist_len']))
    L.append('\n### ③ 전원 (ΔT %g K, 구리 고온 %g °C 저항으로 강하 계산)\n' % (cfg['delta_t_k'], cfg['hot_copper_c']))
    L.append('| 넷 | 최악 전류 A (근거) · 배분 | 층별 넷 최소 선폭 mm (그 폭 길이 mm, 그 폭 허용 A 2152/2221) | 비아 수 (드릴) | 최대 이용률 트랙: w mm 층 · 흐르는/허용 A · ΔT@I | 전류 흐르는 가장 좁은 트랙: w · 흐르는/허용 A | 전류 흐르는 비아: 드릴 · 흐르는/허용 A |')
    L.append('|---|---|---|---|---|---|---|')
    f2 = lambda r: '—' if r is None else '%.3f %s · %.2f/%.2f · %.1f K' % (r['w'], r['layer'], r['I'], r['cap'], r['dt_at_I'])
    f3 = lambda r: '—' if r is None else '%.3f %s · %.2f/%.2f' % (r['w'], r['layer'], r['I'], r['cap'])
    for p in out['power']:
        pl = '<br>'.join('%s %.3f (%.2f, %.2f/%.2f)' % (ln, d['min_w'], d['len_at_min'], d['i2152'], d['i2221'])
                         for ln, d in sorted(p['per_layer'].items()))
        vr = '<br>'.join('Ø%.2f · %.2f/%.2f' % (v['drill'], v['I'], v['cap']) for v in p['vias_carrying']) or '—'
        L.append('| %s:%s | %.3f (%s) · %s | %s | %d (%s) | %s | %s | %s |' % (
            p['board'], p['net'], p['i_worst'], p['i_source'], p['mode'], pl, p['via_count'],
            ','.join('%.2f' % d for d in p['via_drills']), f2(p['track_worst']), f3(p['track_narrowest_carrying']), vr))
    L.append('\n#### ③ 주 경로 (저항 최소 경로 = 소스 → 싱크 묶음)\n')
    L.append('| 넷 | 싱크 묶음 | 경로 길이 mm | 경로 비아 수 | 경로 최소 선폭 mm | 경로 R20 mΩ | 망 해석 강하 mV (%g °C 구리) |' % cfg['hot_copper_c'])
    L.append('|---|---|---|---|---|---|---|')
    for p in out['power']:
        for gr in p['groups']:
            if 'path_len' in gr:
                L.append('| %s:%s | %s | %.2f | %d | %s | %.1f | %s |' % (
                    p['board'], p['net'], '+'.join(gr['sinks']), gr['path_len'], gr['path_vias'],
                    '—' if gr['path_min_w'] is None else '%.3f' % gr['path_min_w'], gr['path_R20_mohm'],
                    '%.1f' % gr['drop_mv'] if 'drop_mv' in gr else '—'))
            else:
                L.append('| %s:%s | %s | 미배선 | | | | |' % (p['board'], p['net'], '+'.join(gr['sinks'])))
    L.append('\n### 공칭 형상 (V-005 A6 · P-001 대조용, F.Cu 적층)\n')
    L.append('| w / s mm | IPC-2141A 마스크 없음 Ω | 마스크 보정 Ω |')
    L.append('|---|---|---|')
    for r in out['nominal']:
        L.append('| %.2f / %.2f | %.1f | %.1f |' % (r['w'], r['s'], r['zdiff_nomask'], r['zdiff_mask']))
    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(L) + '\n')


if __name__ == '__main__':
    sys.exit(main())
