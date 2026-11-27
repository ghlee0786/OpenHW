# -*- coding: utf-8 -*-
"""V-005 A. 설계 규칙 독립 계산 (KiCad 10 pcbnew, 읽기 전용).

사용: <KiCad>/bin/python.exe -I v005_rules.py <board.kicad_pcb> <out.json>
계산 (DRC 결과를 쓰지 않고 보드 파일에서 직접):
  1. 고속 넷클래스(CSI_100·MDI_100·USB_90) 트랙 층·선폭 분포, 비아 크기 분포
  2. 차동쌍: P/N 트랙 길이·비아 수·쌍 안 길이 차, 결합 길이(평행 세그먼트 투영 겹침, 간격 ≤ 문턱), 비결합 길이
     · 결합 간격 분포와 IPC-2141A 근사 Zdiff(적층은 보드 파일 stackup 값)
  3. CSI 레인 skew(넷 길이 최대-최소)
  4. 규칙 영역(DP_TWIST·DP_BRK·DP_TUNE): 영역 크기, 그 영역에 걸친 고속 트랙 중 영역 밖 길이(규칙 완화가 새는 길이),
     쌍 비아가 영역 안에만 있는지
  5b. 뒷면 고속선과 In2(기준층) 위 신호선 교차 목록, 내층 신호 배선 길이
  5. 고속 트랙 아래 기준면(F.Cu→In1, B.Cu→In2 GND 채움) 연속성: 0.05mm 간격 표본 중 기준면 밖 길이(비아 0.55mm 안 제외)
  6. IR LED 열 비아(LED 애노드 넷의 윗면 열 구리 영역 안 비아 수, 그중 뒷면 노출 패드에 닿는 수)와 O-43 노출 패드(B.Cu THERMAL 영역)
     · 넷·틈·외곽 거리·다른 넷 구리 거리·B.Mask 개구 안 다른 넷 구리
"""
import sys, json, math, re, collections
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
mm = pcbnew.ToMM
FM = pcbnew.FromMM
ERR = FM(0.005)
HS = ('CSI_100', 'MDI_100', 'USB_90')

path, out = sys.argv[1], sys.argv[2]
b = pcbnew.LoadBoard(path)
R = {'board': path, 'kicad': pcbnew.Version()}


def ln(name):
    return b.GetLayerName(name)


def sps_outlines(s):
    res = []
    for i in range(s.OutlineCount()):
        o = s.Outline(i)
        res.append([(mm(o.CPoint(j).x), mm(o.CPoint(j).y)) for j in range(o.PointCount())])
        for h in range(s.HoleCount(i)):
            hh = s.Hole(i, h)
            res.append([(mm(hh.CPoint(j).x), mm(hh.CPoint(j).y)) for j in range(hh.PointCount())])
    return res


def V(x, y):
    return pcbnew.VECTOR2I(FM(x), FM(y))


# ---------- 적층 (파일 텍스트에서) ----------
txt = open(path, encoding='utf-8').read()
stk = re.findall(r'\(layer "([^"]+)"\s*\(type "([^"]+)"\)(?:\s*\(color "[^"]*"\))?\s*\(thickness ([\d.]+)\)(?:\s*\(material "([^"]*)"\))?(?:\s*\(epsilon_r ([\d.]+)\))?', txt)
R['stackup'] = [dict(layer=a, type=t, thickness=float(th), material=m, er=(float(e) if e else None)) for a, t, th, m, e in stk]

# ---------- 넷클래스 ----------
netcls = {}
for code, n in b.GetNetInfo().NetsByNetcode().items():
    netcls[n.GetNetname()] = n.GetNetClassName()

tracks = [t for t in b.Tracks() if t.GetClass() in ('PCB_TRACK', 'PCB_ARC')]
vias = [t for t in b.Tracks() if t.GetClass() == 'PCB_VIA']
R['counts'] = dict(tracks=len(tracks), arcs=sum(1 for t in tracks if t.GetClass() == 'PCB_ARC'), vias=len(vias))
R['via_sizes'] = collections.Counter('%.3f/%.3f' % (mm(v.GetWidth(pcbnew.F_Cu)), mm(v.GetDrill())) for v in vias)
R['track_min_width_all'] = min(mm(t.GetWidth()) for t in tracks) if tracks else None

hs_tr = [t for t in tracks if netcls.get(t.GetNetname()) in HS]
lw = collections.defaultdict(lambda: collections.Counter())
for t in hs_tr:
    lw[netcls[t.GetNetname()]][(t.GetLayerName(), round(mm(t.GetWidth()), 3))] += round(mm(t.GetLength()), 3)
R['hs_layer_width_len'] = {k: {'%s w=%.3f' % kk: round(v, 2) for kk, v in c.items()} for k, c in lw.items()}

# ---------- 규칙 영역 ----------
areas = collections.defaultdict(list)
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetZoneName().startswith('DP_'):
        bb = z.GetBoundingBox()
        areas[z.GetZoneName()].append(dict(z=z, layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                                           bbox=[round(mm(bb.GetX()), 3), round(mm(bb.GetY()), 3), round(mm(bb.GetRight()), 3), round(mm(bb.GetBottom()), 3)],
                                           w=round(mm(bb.GetWidth()), 3), h=round(mm(bb.GetHeight()), 3)))


def in_area(name, x, y, layer=None):
    for a in areas.get(name, []):
        if layer is not None and layer not in a['layers']:
            continue
        if a['z'].Outline().Contains(V(x, y)):
            return True
    return False


def seg_pts(t, step=0.05):
    s, e = t.GetStart(), t.GetEnd()
    x0, y0, x1, y1 = mm(s.x), mm(s.y), mm(e.x), mm(e.y)
    L = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(L / step))
    return [(x0 + (x1 - x0) * (i + 0.5) / n, y0 + (y1 - y0) * (i + 0.5) / n) for i in range(n)], L / n


def item_intersects_area(t, name):
    # KiCad intersectsArea: 항목 모양이 영역과 겹치면 항목 전체에 규칙 적용
    ts = pcbnew.SHAPE_POLY_SET()
    t.TransformShapeToPolygon(ts, t.GetLayer(), 0, ERR, pcbnew.ERROR_INSIDE)
    for a in areas.get(name, []):
        if t.GetLayerName() not in a['layers']:
            continue
        c = pcbnew.SHAPE_POLY_SET(ts)
        c.BooleanIntersection(a['z'].Outline())
        if c.Area() > 0:
            return True
    return False


R['rule_areas'] = {}
for name, lst in areas.items():
    R['rule_areas'][name] = [dict(layers=a['layers'], bbox=a['bbox'], w=a['w'], h=a['h']) for a in lst]

leak = {}
for name in areas:
    rows = []
    for t in hs_tr:
        if t.GetClass() != 'PCB_TRACK' or not item_intersects_area(t, name):
            continue
        pts, dl = seg_pts(t)
        outside = sum(dl for (x, y) in pts if not in_area(name, x, y, t.GetLayerName()))
        rows.append(dict(net=t.GetNetname(), layer=t.GetLayerName(), len=round(mm(t.GetLength()), 3), outside=round(outside, 3),
                         start=[round(mm(t.GetStart().x), 3), round(mm(t.GetStart().y), 3)], end=[round(mm(t.GetEnd().x), 3), round(mm(t.GetEnd().y), 3)]))
    leak[name] = dict(items=len(rows), total_len=round(sum(r['len'] for r in rows), 3), outside_len=round(sum(r['outside'] for r in rows), 3),
                      worst=sorted(rows, key=lambda r: -r['outside'])[:8])
R['area_rule_leak'] = leak

# ---------- 차동쌍 ----------
pairs = collections.defaultdict(dict)
for n, c in netcls.items():
    if c in HS and n[-1] in 'PN':
        pairs[n[:-1]][n[-1]] = n


def segs_of(net):
    out = []
    for t in hs_tr:
        if t.GetNetname() == net and t.GetClass() == 'PCB_TRACK':
            s, e = t.GetStart(), t.GetEnd()
            out.append(dict(t=t, a=(mm(s.x), mm(s.y)), b=(mm(e.x), mm(e.y)), w=mm(t.GetWidth()), L=t.GetLayerName()))
    return out


def coupled(segA, segB, gapmax):
    """segA 각 세그먼트 길이 중, 같은 층 평행 segB 와 간격 ≤ gapmax 로 겹치는 투영 길이 합, 간격 기록"""
    tot = 0.0
    gaps = []
    for s in segA:
        ax, ay = s['a']; bx, by = s['b']
        L = math.hypot(bx - ax, by - ay)
        if L < 1e-6:
            continue
        ux, uy = (bx - ax) / L, (by - ay) / L
        iv = []
        for o in segB:
            if o['L'] != s['L']:
                continue
            cx, cy = o['a']; dx, dy = o['b']
            M = math.hypot(dx - cx, dy - cy)
            if M < 1e-6:
                continue
            vx, vy = (dx - cx) / M, (dy - cy) / M
            if abs(ux * vy - uy * vx) > math.sin(math.radians(1.0)):
                continue
            d = abs((cx - ax) * (-uy) + (cy - ay) * ux)  # 수직 거리
            gap = d - (s['w'] + o['w']) / 2
            if gap > gapmax + 1e-4 or gap < -1e-4:
                continue
            t0 = (cx - ax) * ux + (cy - ay) * uy
            t1 = (dx - ax) * ux + (dy - ay) * uy
            lo, hi = max(0, min(t0, t1)), min(L, max(t0, t1))
            if hi - lo > 1e-4:
                iv.append((lo, hi, gap))
        iv.sort()
        cur = None
        for lo, hi, g in iv:
            gaps.append((round(g, 3), round(hi - lo, 3), round(s['w'], 3)))
            if cur is None or lo > cur[1]:
                if cur:
                    tot += cur[1] - cur[0]
                cur = [lo, hi]
            else:
                cur[1] = max(cur[1], hi)
        if cur:
            tot += cur[1] - cur[0]
    return tot, gaps


def zdiff_ipc(w, s, h, t, er):
    z0 = 87.0 / math.sqrt(er + 1.41) * math.log(5.98 * h / (0.8 * w + t))
    return 2 * z0 * (1 - 0.48 * math.exp(-0.96 * s / h))


st = {x['layer']: x for x in R['stackup']}
h_pp = st.get('dielectric 1', {}).get('thickness', 0.1855)
er_pp = st.get('dielectric 1', {}).get('er', 4.74)
t_cu = st.get('F.Cu', {}).get('thickness', 0.035)

# 기준면 연속성용 GND 채움
gnd_fill = {}
for z in b.Zones():
    if not z.GetIsRuleArea() and z.GetNetname() == '/GND':
        for l in z.GetLayerSet().Seq():
            if b.GetLayerName(l) in ('In1.Cu', 'In2.Cu', 'GND', 'GND_PWR'):
                gnd_fill.setdefault(l, []).append(z.GetFilledPolysList(l))
ref_layer = {'F.Cu': pcbnew.In1_Cu, 'B.Cu': pcbnew.In2_Cu}


def over_ref(x, y, layername):
    l = ref_layer.get(layername)
    return any(p.Contains(V(x, y)) for p in gnd_fill.get(l, []))


via_xy = [(mm(v.GetPosition().x), mm(v.GetPosition().y)) for v in vias]
R['pairs'] = {}
for base, pn in sorted(pairs.items()):
    if 'P' not in pn or 'N' not in pn:
        continue
    P, N = segs_of(pn['P']), segs_of(pn['N'])
    lenP = sum(mm(s['t'].GetLength()) for s in P)
    lenN = sum(mm(s['t'].GetLength()) for s in N)
    vP = sum(1 for v in vias if v.GetNetname() == pn['P'])
    vN = sum(1 for v in vias if v.GetNetname() == pn['N'])
    cls = netcls[pn['P']]
    res = {}
    for label, gmax in (('strict_0.18', 0.18), ('loose_2.2', 2.2)):
        cP, gP = coupled(P, N, gmax)
        cN, _ = coupled(N, P, gmax)
        res[label] = dict(coupledP=round(cP, 3), coupledN=round(cN, 3), uncoupledP=round(lenP - cP, 3), uncoupledN=round(lenN - cN, 3),
                          uncoupled_max=round(max(lenP - cP, lenN - cN), 3))
        if label == 'strict_0.18':
            gc = collections.Counter()
            for g, l, w in gP:
                gc[(w, g)] += l
            res['gap_hist'] = {'w=%.3f gap=%.3f' % k: round(v, 3) for k, v in sorted(gc.items())}
            res['zdiff_ipc2141_nomask'] = {'w=%.3f gap=%.3f' % k: round(zdiff_ipc(k[0], k[1], h_pp, t_cu, er_pp), 1) for k in gc}
    # 비결합의 꼬임 영역 안/밖 나눔 (strict)
    def unc_split(A, B):
        ins = outs = 0.0
        for s in A:
            pts, dl = seg_pts(s['t'], 0.05)
            for (x, y) in pts:
                # 이 점이 결합인지: 같은 층 평행 B 세그먼트까지 거리
                cpl = False
                for o in B:
                    if o['L'] != s['L']:
                        continue
                    ax, ay = o['a']; bx, by = o['b']
                    L = math.hypot(bx - ax, by - ay)
                    if L < 1e-6:
                        continue
                    ux, uy = (bx - ax) / L, (by - ay) / L
                    su = (s['b'][0] - s['a'][0], s['b'][1] - s['a'][1]); sl = math.hypot(*su)
                    if abs(ux * su[1] / sl - uy * su[0] / sl) > math.sin(math.radians(1.0)):
                        continue
                    tt = (x - ax) * ux + (y - ay) * uy
                    if tt < 0 or tt > L:
                        continue
                    d = abs((x - ax) * (-uy) + (y - ay) * ux) - (s['w'] + o['w']) / 2
                    if -1e-4 <= d <= 0.18 + 1e-4:
                        cpl = True
                        break
                if not cpl:
                    if in_area('DP_TWIST', x, y, s['L']):
                        ins += dl
                    else:
                        outs += dl
        return ins, outs
    if cls == 'MDI_100':
        iP, oP = unc_split(P, N)
        iN, oN = unc_split(N, P)
        res['uncoupled_in_twist'] = dict(P=round(iP, 3), N=round(iN, 3))
        res['uncoupled_outside_twist'] = dict(P=round(oP, 3), N=round(oN, 3))
        res['vias_in_twist'] = dict(P=sum(1 for v in vias if v.GetNetname() == pn['P'] and in_area('DP_TWIST', mm(v.GetPosition().x), mm(v.GetPosition().y))),
                                    N=sum(1 for v in vias if v.GetNetname() == pn['N'] and in_area('DP_TWIST', mm(v.GetPosition().x), mm(v.GetPosition().y))))
    # 기준면 밖 길이 (비아 중심 0.55mm 안은 층 바꿈 구간이라 뺀다: 비아 0.65 + 내층 반공 여유)
    off = 0.0
    offpts = []
    for s in P + N:
        pts, dl = seg_pts(s['t'], 0.05)
        for (x, y) in pts:
            if min((math.hypot(x - vx, y - vy) for vx, vy in via_xy), default=9) < 0.55:
                continue
            if not over_ref(x, y, s['L']):
                off += dl
                if len(offpts) < 5:
                    offpts.append([round(x, 2), round(y, 2), s['L']])
    R['pairs'][base] = dict(cls=cls, P=pn['P'], N=pn['N'], lenP=round(lenP, 3), lenN=round(lenN, 3), diff=round(abs(lenP - lenN), 3),
                            viasP=vP, viasN=vN, layers=sorted(set(s['L'] for s in P + N)), off_reference_len=round(off, 3), off_reference_pts=offpts, **res)

# 5b. 뒷면(B.Cu) 고속선이 기준층 In2 위 신호선과 교차하는 곳 (기준면이 끊기는 곳)
def _cross(a, c, p, q):
    def cr(o, u, w):
        return (u[0] - o[0]) * (w[1] - o[1]) - (u[1] - o[1]) * (w[0] - o[0])
    return cr(a, c, p) * cr(a, c, q) < 0 and cr(p, q, a) * cr(p, q, c) < 0


_P = lambda v: (mm(v.x), mm(v.y))
R['hs_cross_in2_signal'] = []
for h in hs_tr:
    if h.GetClass() != 'PCB_TRACK' or h.GetLayer() != pcbnew.B_Cu:
        continue
    for t in tracks:
        if t.GetLayer() == pcbnew.In2_Cu and _cross(_P(h.GetStart()), _P(h.GetEnd()), _P(t.GetStart()), _P(t.GetEnd())):
            R['hs_cross_in2_signal'].append(dict(hs=h.GetNetname(), in2=t.GetNetname(), in2_w=round(mm(t.GetWidth()), 3),
                                                 in2_seg=[round(x, 2) for x in _P(t.GetStart()) + _P(t.GetEnd())]))
# F.Cu 고속선 아래 In1 신호선 (있으면 같은 문제)
R['hs_cross_in1_signal'] = []
for h in hs_tr:
    if h.GetClass() != 'PCB_TRACK' or h.GetLayer() != pcbnew.F_Cu:
        continue
    for t in tracks:
        if t.GetLayer() == pcbnew.In1_Cu and _cross(_P(h.GetStart()), _P(h.GetEnd()), _P(t.GetStart()), _P(t.GetEnd())):
            R['hs_cross_in1_signal'].append(dict(hs=h.GetNetname(), in1=t.GetNetname()))
R['inner_signal_len'] = {}
for t in tracks:
    if t.GetLayer() in (pcbnew.In1_Cu, pcbnew.In2_Cu):
        k = '%s %s' % (t.GetLayerName(), t.GetNetname())
        R['inner_signal_len'][k] = round(R['inner_signal_len'].get(k, 0) + mm(t.GetLength()), 2)

csi = {k: v for k, v in R['pairs'].items() if v['cls'] == 'CSI_100'}
if csi:
    nl = {}
    for k, v in csi.items():
        nl[v['P']] = v['lenP']; nl[v['N']] = v['lenN']
    R['csi_skew'] = dict(net_len=nl, skew_net=round(max(nl.values()) - min(nl.values()), 3),
                         pair_avg={k: round((v['lenP'] + v['lenN']) / 2, 3) for k, v in csi.items()})
    pa = R['csi_skew']['pair_avg'].values()
    R['csi_skew']['skew_pair_avg'] = round(max(pa) - min(pa), 3)
R['ipc2141_ref'] = dict(h=h_pp, er=er_pp, t=t_cu, note='IPC-2141A edge-coupled microstrip, 마스크 없음. 유효 0.1<w/h<2.0, 0.2<s/h<3.0')
for w, s in ((0.15, 0.16), (0.20, 0.16)):
    R['ipc2141_ref']['w=%.2f s=%.2f' % (w, s)] = round(zdiff_ipc(w, s, h_pp, t_cu, er_pp), 1)

# ---------- IR LED 열 비아 · O-43 노출 패드 ----------
edge = pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(edge, False)
edge_segs = []
for ol in sps_outlines(edge):
    for i in range(len(ol)):
        edge_segs.append((ol[i], ol[(i + 1) % len(ol)]))


def pt_seg(p, a, c):
    ax, ay = a; cx, cy = c; px, py = p
    dx, dy = cx - ax, cy - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def seg_seg(a, c, p, q):
    return min(pt_seg(a, p, q), pt_seg(c, p, q), pt_seg(p, a, c), pt_seg(q, a, c))


def poly_dist(A, Bs, box_margin=3.0):
    """A, Bs: 외곽 목록. 꼭짓점·변 사이 최소 거리(겹치면 0 — 겹침은 따로 확인)"""
    xs = [x for o in A for x, y in o]; ys = [y for o in A for x, y in o]
    bx0, bx1, by0, by1 = min(xs) - box_margin, max(xs) + box_margin, min(ys) - box_margin, max(ys) + box_margin
    sa = [(o[i], o[(i + 1) % len(o)]) for o in A for i in range(len(o))]
    best = 1e9
    for o in Bs:
        for i in range(len(o)):
            p, q = o[i], o[(i + 1) % len(o)]
            if max(p[0], q[0]) < bx0 or min(p[0], q[0]) > bx1 or max(p[1], q[1]) < by0 or min(p[1], q[1]) > by1:
                continue
            for a, c in sa:
                d = seg_seg(a, c, p, q)
                if d < best:
                    best = d
    return best


leds = [f for f in b.Footprints() if f.GetReference().startswith('D_IR')]
R['ir_leds'] = []
for f in leds:
    anode = [p for p in f.Pads() if p.GetNumber() == '2']
    anet = anode[0].GetNetname() if anode else None
    fp = f.GetPosition()
    # 그 LED 의 윗면 열 구리(F.Cu THERMAL 영역, 애노드 넷, LED 중심을 품는 것) 안 비아 = 열 비아
    tz_f = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetZoneName().startswith('THERMAL') and z.GetNetname() == anet
            and z.GetLayerSet().Contains(pcbnew.F_Cu) and z.Outline().Contains(fp)]
    tz_b = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetZoneName().startswith('THERMAL') and z.GetNetname() == anet
            and z.GetLayerSet().Contains(pcbnew.B_Cu)]
    near = [v for v in vias if v.GetNetname() == anet and any(z.Outline().Contains(v.GetPosition()) for z in tz_f)]
    in_bpad = [v for v in near if any(z.Outline().Contains(v.GetPosition()) for z in tz_b)]
    R['ir_leds'].append(dict(ref=f.GetReference(), dnp=f.IsDNP(), anode_net=anet, pos=[round(mm(fp.x), 2), round(mm(fp.y), 2)],
                             pads={p.GetNumber(): p.GetNetname() for p in f.Pads()},
                             thermal_zone_F=[z.GetZoneName() for z in tz_f], thermal_vias=len(near), vias_reaching_B_pad=len(in_bpad), via_sizes=sorted(set('%.2f/%.2f' % (mm(v.GetWidth(pcbnew.F_Cu)), mm(v.GetDrill())) for v in near)),
                             via_pos=[[round(mm(v.GetPosition().x), 2), round(mm(v.GetPosition().y), 2)] for v in near]))

# 노출 패드: B.Cu THERMAL 영역 + B.Mask 개구
bmask = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.B_Mask and d.GetClass() == 'PCB_SHAPE':
        s = pcbnew.SHAPE_POLY_SET()
        d.TransformShapeToPolygon(s, pcbnew.B_Mask, 0, ERR, pcbnew.ERROR_INSIDE)
        bb = d.GetBoundingBox()
        bmask.append(dict(s=s, bbox=[round(mm(bb.GetX()), 3), round(mm(bb.GetY()), 3), round(mm(bb.GetRight()), 3), round(mm(bb.GetBottom()), 3)]))
for z in b.Zones():
    if z.GetIsRuleArea():
        continue
    if z.GetLayerSet().Contains(pcbnew.B_Mask):
        bmask.append(dict(s=z.Outline(), bbox='zone'))

# B.Cu 다른 넷 구리 (트랙·패드·비아·채움)
def bcu_items_except(net):
    outl = []
    for t in b.Tracks():
        if t.GetNetname() == net:
            continue
        if t.GetClass() == 'PCB_VIA' or t.GetLayer() == pcbnew.B_Cu:
            s = pcbnew.SHAPE_POLY_SET()
            t.TransformShapeToPolygon(s, pcbnew.B_Cu, 0, ERR, pcbnew.ERROR_INSIDE)
            outl += sps_outlines(s)
    for f in b.Footprints():
        for p in f.Pads():
            if p.GetNetname() == net or not p.IsOnLayer(pcbnew.B_Cu):
                continue
            s = pcbnew.SHAPE_POLY_SET()
            p.TransformShapeToPolygon(s, pcbnew.B_Cu, 0, ERR, pcbnew.ERROR_INSIDE)
            outl += sps_outlines(s)
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() == net or not z.GetLayerSet().Contains(pcbnew.B_Cu):
            continue
        outl += sps_outlines(z.GetFilledPolysList(pcbnew.B_Cu))
    return outl


R['exposed_pads'] = []
tz = [z for z in b.Zones() if not z.GetIsRuleArea() and z.GetZoneName().startswith('THERMAL') and z.GetLayerSet().Contains(pcbnew.B_Cu)]
fills = {}
for z in tz:
    fills[z.GetZoneName()] = (z.GetNetname(), z.GetFilledPolysList(pcbnew.B_Cu))
for name, (net, fp) in sorted(fills.items()):
    A = sps_outlines(fp)
    if not A:
        R['exposed_pads'].append(dict(zone=name, net=net, filled=False))
        continue
    bb = fp.BBox()
    d_edge = min(pt_seg(p, a, c) for o in A for p in o for a, c in edge_segs)
    others = bcu_items_except(net)
    d_other = poly_dist(A, others)
    # 마스크 개구 덮임 비율, 개구 안 다른 넷 구리
    cov = 0.0
    other_exposed = 0.0
    for m in bmask:
        c = pcbnew.SHAPE_POLY_SET(fp); c.BooleanIntersection(m['s']); cov += c.Area() / 1e12
    R['exposed_pads'].append(dict(zone=name, net=net, area=round(fp.Area() / 1e12, 3),
                                  bbox=[round(mm(bb.GetX()), 3), round(mm(bb.GetY()), 3), round(mm(bb.GetRight()), 3), round(mm(bb.GetBottom()), 3)],
                                  mask_open_area=round(cov, 3), min_dist_edge=round(d_edge, 3), min_dist_other_net_Bcu=round(d_other, 3)))
# 서로 다른 노출 패드 사이 최소 틈
names = sorted(fills)
gapm = []
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        A = sps_outlines(fills[names[i]][1]); Bo = sps_outlines(fills[names[j]][1])
        if A and Bo:
            gapm.append(dict(a=names[i], b=names[j], na=fills[names[i]][0], nb=fills[names[j]][0], gap=round(poly_dist(A, Bo, 1.0), 3)))
R['exposed_pad_gaps'] = sorted(gapm, key=lambda r: r['gap'])[:6]
# B.Mask 개구 안 다른 넷(노출 패드 넷 외) 구리 노출
expo = []
tnets = set(n for n, _ in fills.values())
allB = []
for t in b.Tracks():
    if t.GetClass() == 'PCB_VIA' or t.GetLayer() == pcbnew.B_Cu:
        if t.GetNetname() in tnets:
            continue
        s = pcbnew.SHAPE_POLY_SET(); t.TransformShapeToPolygon(s, pcbnew.B_Cu, 0, ERR, pcbnew.ERROR_INSIDE); allB.append((t.GetNetname(), t.GetClass(), s))
for z in b.Zones():
    if not z.GetIsRuleArea() and z.GetLayerSet().Contains(pcbnew.B_Cu) and z.GetNetname() not in tnets:
        allB.append((z.GetNetname(), 'zone', z.GetFilledPolysList(pcbnew.B_Cu)))
for m in bmask:
    for net, kind, s in allB:
        c = pcbnew.SHAPE_POLY_SET(s); c.BooleanIntersection(m['s'])
        a = c.Area() / 1e12
        if a > 1e-4:
            expo.append(dict(mask=m['bbox'], net=net, kind=kind, area=round(a, 4)))
R['bmask_openings'] = [m['bbox'] for m in bmask]
R['bmask_other_net_exposed'] = expo

# ---------- 7. 작은 비아 (D-003 #21 0.65/0.30, #60 J1 탈출 비아 0.50/0.20 영역 한정 — O-114) ----------
# 영역 = 이름이 ESC_PREFIX 로 시작하는 규칙 영역. 「영역 안」 = 비아 구리 원 둘레 16점과 중심이 모두 영역 안(KiCad enclosedByArea 와 같은 뜻).
ESC_PREFIX = 'J1_'
VIA_STD, ESC_MIN = (0.65, 0.30), (0.50, 0.20)   # 지름/드릴
ESC_RING, ESC_HOLE_GAP, ESC_REACH = 0.15, 0.28, 3.0   # 링, 구멍 가장자리 사이, 영역이 J1 외곽 상자 밖으로 나가도 되는 거리 [가정]
esc_z = [z for z in b.Zones() if z.GetIsRuleArea() and z.GetZoneName().startswith(ESC_PREFIX)]
j1 = next((fp for fp in b.Footprints() if fp.GetReference() == 'J1'), None)
j1_nets = set(p.GetNetname() for p in j1.Pads()) if j1 else set()
j1_bb = j1.GetBoundingBox(False) if j1 else None
holes_all = [(mm(v.GetPosition().x), mm(v.GetPosition().y), mm(v.GetDrill()) / 2, 'via') for v in vias]
for fp in b.Footprints():
    for p in fp.Pads():
        ds = p.GetDrillSize()
        if ds.x > 0:
            holes_all.append((mm(p.GetPosition().x), mm(p.GetPosition().y), mm(max(ds.x, ds.y)) / 2, '%s.%s' % (fp.GetReference(), p.GetNumber())))


def via_area_state(v):
    """'in' = 영역 안에 다 들어감, 'straddle' = 걸침, 'out' = 밖 (영역 이름과 함께)"""
    x, y, r = mm(v.GetPosition().x), mm(v.GetPosition().y), mm(v.GetWidth(pcbnew.F_Cu)) / 2
    pts = [(x, y)] + [(x + r * math.cos(2 * math.pi * k / 16), y + r * math.sin(2 * math.pi * k / 16)) for k in range(16)]
    best = ('out', None)
    for z in esc_z:
        n = sum(1 for (px, py) in pts if z.Outline().Contains(V(px, py)))
        if n == len(pts):
            return 'in', z.GetZoneName()
        if n:
            best = ('straddle', z.GetZoneName())
    return best


esc = dict(prefix=ESC_PREFIX, std=VIA_STD, esc_min=ESC_MIN, ring_min=ESC_RING, hole_gap_min=ESC_HOLE_GAP, areas=[], small_total=0,
           inside=[], inside_fail=[], outside_small=[], straddle_small=[], non_j1_net=[])
for z in esc_z:
    bb = z.GetBoundingBox()
    beyond = None
    if j1_bb is not None:
        beyond = round(max(mm(j1_bb.GetX() - bb.GetX()), mm(bb.GetRight() - j1_bb.GetRight()), mm(j1_bb.GetY() - bb.GetY()), mm(bb.GetBottom() - j1_bb.GetBottom()), 0.0), 3)
    esc['areas'].append(dict(name=z.GetZoneName(), layers=[b.GetLayerName(l) for l in z.GetLayerSet().Seq()],
                             bbox=[round(mm(bb.GetX()), 3), round(mm(bb.GetY()), 3), round(mm(bb.GetRight()), 3), round(mm(bb.GetBottom()), 3)],
                             beyond_j1=beyond, beyond_ok=(beyond is not None and beyond <= ESC_REACH + 1e-6)))
for v in vias:
    d, dr = mm(v.GetWidth(pcbnew.F_Cu)), mm(v.GetDrill())
    if d >= VIA_STD[0] - 1e-6 and dr >= VIA_STD[1] - 1e-6:
        continue
    esc['small_total'] += 1
    x, y = mm(v.GetPosition().x), mm(v.GetPosition().y)
    state, zname = via_area_state(v)
    rec = dict(at=[round(x, 3), round(y, 3)], net=v.GetNetname(), dia=round(d, 3), drill=round(dr, 3), ring=round((d - dr) / 2, 4), area=zname)
    if state != 'in':
        esc['outside_small'].append(rec)
        if state == 'straddle':
            esc['straddle_small'].append(rec)
        continue
    gap = min([math.hypot(x - hx, y - hy) - dr / 2 - hr for (hx, hy, hr, _) in holes_all if not (abs(hx - x) < 1e-6 and abs(hy - y) < 1e-6 and abs(hr - dr / 2) < 1e-6)] or [1e9])
    rec['hole_gap'] = round(gap, 4)
    why = []
    if d < ESC_MIN[0] - 1e-6:
        why.append('지름 < %g' % ESC_MIN[0])
    if dr < ESC_MIN[1] - 1e-6:
        why.append('드릴 < %g' % ESC_MIN[1])
    if rec['ring'] < ESC_RING - 1e-6:
        why.append('링 < %g' % ESC_RING)
    if gap < ESC_HOLE_GAP - 1e-6:
        why.append('구멍 간격 < %g' % ESC_HOLE_GAP)
    esc['inside'].append(rec)
    if why:
        esc['inside_fail'].append(dict(rec, why=why))
    if v.GetNetname() not in j1_nets:
        esc['non_j1_net'].append(rec)
R['esc_vias'] = esc

json.dump(R, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print('ok', out)
