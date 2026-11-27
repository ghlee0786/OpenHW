# -*- coding: utf-8 -*-
"""V-005/V-005b 실크스크린 독립 검사 (KiCad 10 pcbnew, 읽기 전용). 면(F/B)마다 수치로 판정한다.

사용: python.exe -I v005_silk.py <board.kicad_pcb> <out.json> [--edge 0.30] [--netlist <kicadsexpr .net>]
  종료 코드 0 = 검사가 끝까지 돌았다(판정은 json 의 summary). 1 = 입력·실행 오류.

판정 (기준값은 아래 TH, 근거는 docs/review/v005-pcb-review.md):
  S1  실크 잉크 ∩ 마스크 개구(패드 + 실효 마스크 확장, 마스크 그림, 열린 비아) 면적 > 0        → 제조 시 잘림
  S1v 실크 잉크 ∩ 열린(마스크로 안 덮인) 비아 구리 — 덮인(tented) 비아 위 실크는 허용 (D-003 #58, O-110)
  S1h 실크 잉크 ∩ 열린 구멍(패드 드릴·NPTH·안 덮인 비아 드릴) — 덮인 비아 드릴은 마스크 밑이라 제외 (D-003 #58)
  S2  실크–마스크 개구 거리 < 0.15 (DRU fab_silk_to_pad, O-64)
  S3  채우지 않은 실크 선폭 < 0.15
  S4  글자 높이 < 1.0, 획 < 0.15 (DRU) / S4r 획/높이 < 1/5 (PCBWay 1:5, O-65 획 0.2)
  S5  보드 외곽까지 < --edge (기본 0.30, O-66) 또는 외곽 밖
  S6  참조 지정자 숨음: 글자 중심이 같은 면 부품 courtyard 안 / S6t 잉크만 걸침
  S6a 참조 지정자 연결: 자기 부품 courtyard 까지 > 2.0mm(멀다) 또는 다른 부품 courtyard 가 0.3mm 이상 더 가까움(모호)
  S7  글자–글자 잉크 겹침 / S7l 글자–다른 실크 선 겹침 / S7s 글자와 다른 실크 사이 < 0.127 (PCBWay 5mil)
  S8  읽는 방향: 면마다 그려지는 회전각 종류 > 2 / S8m 앞면 글자 거울상 · 뒷면 글자 비거울상
  S9  1번 핀·극성 표시 (규칙은 아래 pin1_rule 주석, 한계는 보고서)
"""
import sys, json, math, re, argparse, collections
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('pcb')
ap.add_argument('out')
ap.add_argument('--edge', type=float, default=0.30)
ap.add_argument('--netlist', default=None)
A = ap.parse_args()

TH = dict(silk_pad=0.15, line_w=0.15, text_h=1.0, text_stroke=0.15, ratio=0.2, edge=A.edge, silk_space=0.127,
          ref_far=2.0, ref_amb=0.3, max_orient=2, pin1_r=2.0, pin1_margin=0.01)
mm = pcbnew.ToMM
FM = pcbnew.FromMM
ERR = FM(0.005)
b = pcbnew.LoadBoard(A.pcb)

SIDES = {'F': dict(silk=pcbnew.F_SilkS, mask=pcbnew.F_Mask, cu=pcbnew.F_Cu, cy=pcbnew.F_CrtYd),
         'B': dict(silk=pcbnew.B_SilkS, mask=pcbnew.B_Mask, cu=pcbnew.B_Cu, cy=pcbnew.B_CrtYd)}


def area(s):
    return s.Area() / 1e12


def inter(a, c):
    x = pcbnew.SHAPE_POLY_SET(a)
    x.BooleanIntersection(c)
    return x


def inflate(a, d):
    x = pcbnew.SHAPE_POLY_SET(a)
    x.Inflate(FM(d), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
    return x


def poly(pts):
    s = pcbnew.SHAPE_POLY_SET()
    s.NewOutline()
    for x, y in pts:
        s.Append(FM(x), FM(y))
    return s


def min_dist(a, c, hi=1.0):
    if area(inter(a, c)) > 0:
        return 0.0
    lo = 0.0
    if area(inter(inflate(a, hi), c)) == 0:
        return None  # hi 보다 멀다
    for _ in range(12):
        m = (lo + hi) / 2
        if area(inter(inflate(a, m), c)) > 0:
            hi = m
        else:
            lo = m
    return round(hi, 3)


def ctr(s):
    c = s.BBox().Centre()
    return mm(c.x), mm(c.y)


# ---------- 핀 기능(캐소드 · +) : 보드 패드 값, 없으면 회로도 넷리스트 ----------
pinfn = {}
if A.netlist:
    txt = open(A.netlist, encoding='utf-8').read()
    for r, p, f in re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)(?:\s+\(pinfunction "([^"]*)"\))?', txt):
        pinfn[(r, p)] = re.sub(r'_[^_]*$', '', f) if f else ''


def pin_function(fp, pad):
    f = pad.GetPinFunction()
    if f:
        return re.sub(r'_[^_]*$', '', f) if re.search(r'_\d+$', f) else f
    return pinfn.get((fp.GetReference(), pad.GetNumber()), '')


# ---------- 실크 항목 ----------
items = []
for fp in b.Footprints():
    texts = [fp.Reference(), fp.Value()] + [x for x in fp.GraphicalItems() if x.GetClass() in ('PCB_TEXT', 'PCB_FIELD')]
    try:
        texts += list(fp.GetFields())
    except Exception:
        pass
    seen = set()
    for t in texts:
        # SWIG 는 같은 글자도 꺼낼 때마다 다른 파이썬 객체를 준다(Reference() 와 GetFields()) → id() 가 아니라 KIID 로 거른다 (V-006a)
        if t is None or t.m_Uuid.AsString() in seen:
            continue
        seen.add(t.m_Uuid.AsString())
        for side, L in SIDES.items():
            if t.GetLayer() != L['silk'] or not t.IsVisible():
                continue
            s = pcbnew.SHAPE_POLY_SET()
            t.TransformTextToPolySet(s, 0, ERR, pcbnew.ERROR_INSIDE)
            shown = t.GetShownText(True)
            items.append(dict(kind='text', owner=fp.GetReference(), side=side, ink=s, obj=t, text=shown,
                              is_ref=(shown == fp.GetReference())))
    for g in fp.GraphicalItems():
        if g.GetClass() != 'PCB_SHAPE':
            continue
        for side, L in SIDES.items():
            if g.GetLayer() != L['silk']:
                continue
            s = pcbnew.SHAPE_POLY_SET()
            g.TransformShapeToPolygon(s, L['silk'], 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='shape', owner=fp.GetReference(), side=side, ink=s, obj=g))
for d in b.GetDrawings():
    for side, L in SIDES.items():
        if d.GetLayer() != L['silk']:
            continue
        s = pcbnew.SHAPE_POLY_SET()
        if d.GetClass() in ('PCB_TEXT', 'PCB_TEXTBOX'):
            d.TransformTextToPolySet(s, 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='text', owner='(보드)', side=side, ink=s, obj=d, text=d.GetShownText(True), is_ref=False))
        else:
            d.TransformShapeToPolygon(s, L['silk'], 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='shape', owner='(보드)', side=side, ink=s, obj=d))
items = [i for i in items if i['ink'].OutlineCount()]

# ---------- 마스크 개구 · 비아 · 구멍 ----------
mask_open, via_cu, holes = {}, {}, pcbnew.SHAPE_POLY_SET()
for side, L in SIDES.items():
    s = pcbnew.SHAPE_POLY_SET()
    vc = pcbnew.SHAPE_POLY_SET()
    for fp in b.Footprints():
        for p in fp.Pads():
            if p.IsOnLayer(L['mask']):
                p.TransformShapeToPolygon(s, L['mask'], max(0, p.GetSolderMaskExpansion(L['mask'])), ERR, pcbnew.ERROR_OUTSIDE)
        for g in fp.GraphicalItems():
            if g.GetLayer() == L['mask'] and g.GetClass() == 'PCB_SHAPE':
                g.TransformShapeToPolygon(s, L['mask'], 0, ERR, pcbnew.ERROR_OUTSIDE)
    for t in b.Tracks():
        if t.GetClass() == 'PCB_VIA':
            tented = True
            try:
                tented = t.IsTented(L['mask'])
            except Exception:
                pass
            if not tented:   # D-003 #58: 덮인 비아 위 실크 허용 → S1v 는 안 덮인 비아 구리만
                t.TransformShapeToPolygon(vc, L['cu'], 0, ERR, pcbnew.ERROR_OUTSIDE)
                t.TransformShapeToPolygon(s, L['mask'], max(0, t.GetSolderMaskExpansion()), ERR, pcbnew.ERROR_OUTSIDE)
    for d in b.GetDrawings():
        if d.GetLayer() == L['mask'] and d.GetClass() == 'PCB_SHAPE':
            d.TransformShapeToPolygon(s, L['mask'], 0, ERR, pcbnew.ERROR_OUTSIDE)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetLayerSet().Contains(L['mask']):
            s.BooleanAdd(z.Outline())
    s.Simplify()
    vc.Simplify()
    mask_open[side] = s
    via_cu[side] = vc


def add_hole(pos, r):
    n = 24
    holes.BooleanAdd(poly([(mm(pos.x) + r * math.cos(2 * math.pi * k / n), mm(pos.y) + r * math.sin(2 * math.pi * k / n)) for k in range(n)]))


for fp in b.Footprints():
    for p in fp.Pads():
        ds = p.GetDrillSize()
        if ds.x > 0:
            add_hole(p.GetPosition(), mm(max(ds.x, ds.y)) / 2)
for t in b.Tracks():
    if t.GetClass() == 'PCB_VIA':
        try:   # D-003 #58: 두 면 모두 덮인 비아의 드릴은 열린 구멍이 아님
            covered = t.IsTented(pcbnew.F_Mask) and t.IsTented(pcbnew.B_Mask)
        except Exception:
            covered = False
        if not covered:
            add_hole(t.GetPosition(), mm(t.GetDrill()) / 2)

edge = pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(edge, False)
edge_in = inflate(edge, -TH['edge'])
_ring = inflate(edge, 5.0)
_ring.BooleanSubtract(edge)

for fp in b.Footprints():
    fp.BuildCourtyardCaches()
cyd = {(fp.GetReference(), s): fp.GetCourtyard(L['cy']) for fp in b.Footprints() for s, L in SIDES.items()}


def desc(it):
    bb = it['ink'].BBox()
    d = dict(owner=it['owner'], side=it['side'], kind=it['kind'],
             at=[round(mm(bb.Centre().x), 2), round(mm(bb.Centre().y), 2)],
             bbox=[round(mm(bb.GetX()), 2), round(mm(bb.GetY()), 2), round(mm(bb.GetRight()), 2), round(mm(bb.GetBottom()), 2)])
    if it['kind'] == 'text':
        d['text'] = it['text']
    else:
        o = it['obj']
        d['shape'] = o.ShowShape() if hasattr(o, 'ShowShape') else o.GetClass()
    return d


KEYS = ['S1_on_mask_open', 'S1v_over_via', 'S1h_over_hole', 'S2_clear_lt_0p15', 'S3_line_lt_0p15', 'S4_text', 'S4r_ratio_lt_1to5',
        'S5_edge', 'S6_ref_hidden', 'S6t_ref_touch', 'S6a_ref_far', 'S6a_ref_ambiguous', 'S7_text_text', 'S7l_text_line', 'S7s_text_space',
        'S8_orient_gt2', 'S8m_mirror', 'S9_missing', 'S9_wrong_side']
S = {k: [] for k in KEYS}

# ---------- S1~S5 ----------
for it in items:
    side, ink, o = it['side'], it['ink'], it['obj']
    a = area(inter(ink, mask_open[side]))
    if a > 1e-5:
        S['S1_on_mask_open'].append(dict(desc(it), area=round(a, 4)))
    else:
        dist = min_dist(ink, mask_open[side], TH['silk_pad'])
        if dist is not None and dist < TH['silk_pad'] - 1e-4:
            S['S2_clear_lt_0p15'].append(dict(desc(it), dist=dist))
    av = area(inter(ink, via_cu[side]))
    if av > 1e-5:
        S['S1v_over_via'].append(dict(desc(it), area=round(av, 4)))
    ah = area(inter(ink, holes))
    if ah > 1e-5:
        S['S1h_over_hole'].append(dict(desc(it), area=round(ah, 4)))
    if it['kind'] == 'shape':
        filled = o.IsSolidFill() if hasattr(o, 'IsSolidFill') else o.IsFilled()
        w = mm(o.GetWidth())
        if not filled and w < TH['line_w'] - 1e-6:
            S['S3_line_lt_0p15'].append(dict(desc(it), width=round(w, 3)))
    else:
        h, th = mm(o.GetTextHeight()), mm(o.GetEffectiveTextPenWidth())
        if h < TH['text_h'] - 1e-6 or th < TH['text_stroke'] - 1e-6:
            S['S4_text'].append(dict(desc(it), height=round(h, 3), stroke=round(th, 3)))
        if th / h < TH['ratio'] - 1e-6:
            S['S4r_ratio_lt_1to5'].append(dict(desc(it), height=round(h, 3), stroke=round(th, 3)))
    out_edge = pcbnew.SHAPE_POLY_SET(ink)
    out_edge.BooleanSubtract(edge_in)
    if area(out_edge) > 1e-5:
        outside = pcbnew.SHAPE_POLY_SET(ink)
        outside.BooleanSubtract(edge)
        S['S5_edge'].append(dict(desc(it), dist_edge=min_dist(ink, _ring, 1.0), area_outside_board=round(area(outside), 4)))

# ---------- S6 참조 지정자 ----------
fps = {fp.GetReference(): fp for fp in b.Footprints()}
refs = [i for i in items if i['kind'] == 'text' and i.get('is_ref')]


def dist_to_poly(pt, s):
    if s.OutlineCount() == 0:
        return None
    v = pcbnew.VECTOR2I(FM(pt[0]), FM(pt[1]))
    if s.Contains(v):
        return 0.0
    return mm(s.Distance(v))


for it in refs:
    side = it['side']
    c = it['ink'].BBox().Centre()
    cxy = (mm(c.x), mm(c.y))
    for ref, fp in fps.items():
        cy = cyd[(ref, side)]
        if cy.OutlineCount() == 0:
            continue
        if cy.Contains(c):
            S['S6_ref_hidden'].append(dict(desc(it), under=ref, own=(ref == it['owner'])))
        else:
            a = area(inter(it['ink'], cy))
            if a > 1e-5:
                S['S6t_ref_touch'].append(dict(desc(it), under=ref, own=(ref == it['owner']), area=round(a, 4)))
    own_cy = cyd.get((it['owner'], side))
    if own_cy is None or own_cy.OutlineCount() == 0:
        fp = fps[it['owner']]
        own_d = math.hypot(cxy[0] - mm(fp.GetPosition().x), cxy[1] - mm(fp.GetPosition().y))
    else:
        own_d = dist_to_poly(cxy, own_cy)
    others = []
    for ref, fp in fps.items():
        if ref == it['owner']:
            continue
        cy = cyd[(ref, side)]
        d = dist_to_poly(cxy, cy)
        if d is not None:
            others.append((d, ref))
    near = min(others) if others else (None, None)
    if own_d > TH['ref_far']:
        S['S6a_ref_far'].append(dict(desc(it), own_dist=round(own_d, 3)))
    if near[0] is not None and near[0] + TH['ref_amb'] < own_d:
        S['S6a_ref_ambiguous'].append(dict(desc(it), own_dist=round(own_d, 3), nearer=near[1], nearer_dist=round(near[0], 3)))

# ---------- S7 겹침 · 간격 ----------
texts = [i for i in items if i['kind'] == 'text']
others_all = [i for i in items]
tidx = {id(t): k for k, t in enumerate(texts)}
for i, A_ in enumerate(texts):
    abb = inflate(A_['ink'], TH['silk_space']).BBox()
    for B_ in others_all:
        if B_ is A_ or B_['side'] != A_['side'] or not abb.Intersects(B_['ink'].BBox()):
            continue
        if B_['kind'] == 'text' and tidx[id(B_)] < i:
            continue  # 글자 쌍은 한 번만
        a = area(inter(A_['ink'], B_['ink']))
        if a > 1e-5:
            key = 'S7_text_text' if B_['kind'] == 'text' else 'S7l_text_line'
            S[key].append(dict(text=desc(A_), other=desc(B_), area=round(a, 4)))
        else:
            d = min_dist(A_['ink'], B_['ink'], TH['silk_space'])
            if d is not None and d < TH['silk_space'] - 1e-4:
                S['S7s_text_space'].append(dict(text=desc(A_), other=desc(B_), dist=d))

# ---------- S8 방향 ----------
orient = {}
for side in SIDES:
    c = collections.Counter()
    for it in texts:
        if it['side'] != side:
            continue
        c[round(it['obj'].GetDrawRotation().AsDegrees()) % 360] += 1
        mir = it['obj'].IsMirrored()
        if (side == 'F' and mir) or (side == 'B' and not mir):
            S['S8m_mirror'].append(dict(desc(it), mirrored=mir))
    orient[side] = {str(k): v for k, v in sorted(c.items())}
    if len(c) > TH['max_orient']:
        S['S8_orient_gt2'].append(dict(side=side, angles=orient[side]))

# ---------- S9 1번 핀 · 극성 ----------
# pin1_rule:
#  대상: 다이오드·LED(핀 기능 K/A), 전해(CP_ 풋프린트, + = 1번), 3핀 이상 IC·트랜지스터·발진기·커넥터(J·U·Q·X).
#  면제: 양방향(핀 A1/A2)·무극성 2핀, 기구적으로 방향이 정해지는 커넥터(USB-C·RJ45·microSD·DC 잭), 구멍·시험점.
#  2단자 극성: 캐소드(+) 패드 중심과 반대 패드 중심을 잇는 축의 가운데 수직선으로 부품 자기 실크(참조·값 글자 제외) 잉크를 나눈다.
#    캐소드 쪽 − 반대쪽 > 여유(0.01mm² 또는 반대쪽의 10%) → ok, 반대가 더 크면 wrong_side, 차이가 여유 안이면 missing.
#  다단자: 부품 축(회전각) 기준 4사분면으로 잉크를 나눈다. 1번 패드가 있는 사분면 잉크가 다른 세 사분면 각각보다 여유 이상 크고,
#    그 사분면 잉크가 1번 패드에서 pin1_r(2.0mm) 안에 있으면 ok(사분면). 아니면 1번 패드 쪽 반평면 잉크가 반대 반평면보다 크면
#    ok_half(약함 — 가운데 홈 같은 표시), 그것도 아니면 missing.
#  표시가 마스크 개구에 잘리는 것은 S1 이 잡는다.
EXEMPT = (('USB_C_Receptacle', '기구 키(USB-C 대칭 삽입)'), ('RJ45', '기구 키(래치·고정 핀)'), ('microSD', '기구 키(카드 슬롯)'),
          ('BarrelJack', '기구 키(DC 잭 몸체)'), ('MountingHole', '구멍'), ('TestPoint', '시험점'))


def pad_centroid(fp, nums):
    xs = ys = w = 0.0
    for p in fp.Pads():
        if p.GetNumber() in nums:
            s = pcbnew.SHAPE_POLY_SET()
            p.TransformShapeToPolygon(s, p.GetPrincipalLayer(), 0, ERR, pcbnew.ERROR_INSIDE)
            a = area(s) or 1e-6
            c = p.GetPosition()
            xs += mm(c.x) * a; ys += mm(c.y) * a; w += a
    return (xs / w, ys / w) if w else None


def halfplane(c, u, big=50.0):
    # 점 c 를 지나고 u 쪽을 향한 반평면 (큰 사각형)
    vx, vy = -u[1], u[0]
    p0 = (c[0] + vx * big, c[1] + vy * big)
    p1 = (c[0] - vx * big, c[1] - vy * big)
    return poly([p0, p1, (p1[0] + u[0] * big, p1[1] + u[1] * big), (p0[0] + u[0] * big, p0[1] + u[1] * big)])


def own_ink(fp, side):
    s = pcbnew.SHAPE_POLY_SET()
    for it in items:
        if it['owner'] == fp.GetReference() and it['side'] == side and not (it['kind'] == 'text' and it['text'] in (fp.GetReference(), fp.GetValue())):
            s.BooleanAdd(it['ink'])
    return s


def own_items(fp, side):
    return [it for it in items if it['owner'] == fp.GetReference() and it['side'] == side
            and not (it['kind'] == 'text' and it['text'] in (fp.GetReference(), fp.GetValue()))]


def unpaired_markers(its, reflections, ok_region, near_pin):
    """짝 없는 작은 표시(점·삼각·+·짧은 선, bbox 긴 변 ≤ 1.5mm): 대칭 위치(reflections 의 각 사상)에 비슷한 항목이 없고,
    ok_region(표시가 있어야 할 쪽) 안, near_pin(1번/캐소드 패드 둘레 pin1_r) 과 겹치는 것"""
    out = []
    info = []
    for it in its:
        bb = it['ink'].BBox()
        info.append((it, ctr(it['ink']), area(it['ink']), max(mm(bb.GetWidth()), mm(bb.GetHeight()))))
    for it, c, a, size in info:
        if size > 1.5:
            continue
        paired = False
        for f in reflections:
            rc = f(c)
            for it2, c2, a2, s2 in info:
                if it2 is it and math.hypot(rc[0] - c[0], rc[1] - c[1]) < 0.3:
                    paired = True  # 대칭축 위 → 자기 자신과 짝(방향 정보 없음)
                    break
                if it2 is not it and math.hypot(rc[0] - c2[0], rc[1] - c2[1]) < 0.3 and abs(a2 - a) <= 0.5 * max(a, a2):
                    paired = True
                    break
            if paired:
                break
        if paired:
            continue
        if area(inter(it['ink'], ok_region)) > 0.5 * a and area(inter(it['ink'], near_pin)) > 0:
            out.append(desc(it))
    return out


cands = []
for fp in b.Footprints():
    ref, fpid = fp.GetReference(), fp.GetFPIDAsString()
    side = 'B' if fp.IsFlipped() else 'F'
    nums = sorted(set(p.GetNumber() for p in fp.Pads() if p.GetNumber() not in ('', 'MP')))
    fns = {n: pin_function(fp, [p for p in fp.Pads() if p.GetNumber() == n][0]) for n in nums}
    rec = dict(ref=ref, side=side, value=fp.GetValue(), fpid=fpid, dnp=fp.IsDNP(), pos=[round(mm(fp.GetPosition().x), 2), round(mm(fp.GetPosition().y), 2)],
               bbox=[round(mm(q), 2) for q in (fp.GetBoundingBox(False).GetX(), fp.GetBoundingBox(False).GetY(), fp.GetBoundingBox(False).GetRight(), fp.GetBoundingBox(False).GetBottom())])
    ex = [r for k, r in EXEMPT if k in fpid]
    if ex:
        if ref[0] in 'JD':
            rec.update(verdict='exempt', reason=ex[0]); cands.append(rec)
        continue
    upper = {n: (fns[n] or '').upper() for n in nums}
    kind = None
    if len(nums) == 2 and ('K' in upper.values()) and set(upper.values()) <= {'K', 'A', 'KA', 'AK'}:
        kind, pos_pin = 'polar2', [n for n in nums if upper[n] == 'K'][0]
    elif len(nums) == 2 and ('CP_' in fpid or 'Elec' in fpid):
        kind, pos_pin = 'polar2', '1'
    elif len(nums) == 2 and ref[0] == 'D' and not any(upper.values()):
        kind, pos_pin = 'polar2', '1'  # 핀 기능 정보 없음 → KiCad 관례 1번 = 캐소드
        rec['note'] = '핀 기능 정보 없음, 1번=캐소드 관례'
    elif len(nums) >= 3 and ref[0] in 'UQXJ':
        kind = 'multi'
    elif len(nums) == 2 and ref[0] == 'J':
        kind = 'multi'  # 2핀 커넥터: 1번 쪽 표시
    if kind is None:
        continue
    ink = own_ink(fp, side)
    rec['kind'] = kind
    if ink.OutlineCount() == 0:
        rec.update(verdict='missing', reason='자기 실크 없음'); cands.append(rec); S['S9_missing'].append(rec); continue
    if kind == 'polar2':
        other = [n for n in nums if n != pos_pin][0]
        k, a_ = pad_centroid(fp, [pos_pin]), pad_centroid(fp, [other])
        L = math.hypot(k[0] - a_[0], k[1] - a_[1]) or 1e-6
        u = ((k[0] - a_[0]) / L, (k[1] - a_[1]) / L)
        mid = ((k[0] + a_[0]) / 2, (k[1] + a_[1]) / 2)
        ak = area(inter(ink, halfplane(mid, u)))
        aa = area(inter(ink, halfplane(mid, (-u[0], -u[1]))))
        marg = max(TH['pin1_margin'], 0.1 * min(ak, aa))
        rec.update(mark_pin=pos_pin, ink_mark_side=round(ak, 4), ink_other_side=round(aa, 4))
        refl = lambda P: (P[0] - 2 * ((P[0] - mid[0]) * u[0] + (P[1] - mid[1]) * u[1]) * u[0], P[1] - 2 * ((P[0] - mid[0]) * u[0] + (P[1] - mid[1]) * u[1]) * u[1])
        kp = pcbnew.SHAPE_POLY_SET()
        for p in fp.Pads():
            if p.GetNumber() == pos_pin:
                p.TransformShapeToPolygon(kp, p.GetPrincipalLayer(), 0, ERR, pcbnew.ERROR_OUTSIDE)
        mk = unpaired_markers(own_items(fp, side), [refl], halfplane(mid, u), inflate(kp, TH['pin1_r']))
        ap_ = pcbnew.SHAPE_POLY_SET()
        for p in fp.Pads():
            if p.GetNumber() == other:
                p.TransformShapeToPolygon(ap_, p.GetPrincipalLayer(), 0, ERR, pcbnew.ERROR_OUTSIDE)
        mk_wrong = unpaired_markers(own_items(fp, side), [refl], halfplane(mid, (-u[0], -u[1])), inflate(ap_, TH['pin1_r']))
        rec['markers'] = [m.get('shape', m.get('text')) + '@' + str(m['at']) for m in mk]
        if ak - aa > marg:
            rec['verdict'] = 'ok'
        elif mk and not mk_wrong:
            rec['verdict'] = 'ok_marker'
        elif aa - ak > marg or (mk_wrong and not mk):
            rec.update(verdict='wrong_side', reason='표시가 %s(반대) 쪽에 치우침' % other)
            S['S9_wrong_side'].append(rec)
        else:
            rec.update(verdict='missing', reason='양쪽 실크가 대칭(극성 표시 없음)')
            S['S9_missing'].append(rec)
    else:
        p1n = '1' if '1' in nums else ('A1' if 'A1' in nums else nums[0])
        p1 = pad_centroid(fp, [p1n])
        # 사분면 중심 = 패드 전체의 가운데. 풋프린트 원점은 쓰지 않는다 — 핀 헤더류는 원점이 1번 패드라 치우침을 가릴 수 없다 (V-006b)
        _px = [mm(p.GetPosition().x) for p in fp.Pads()]
        _py = [mm(p.GetPosition().y) for p in fp.Pads()]
        c = ((min(_px) + max(_px)) / 2, (min(_py) + max(_py)) / 2)
        th = fp.GetOrientation().AsRadians()
        ex_ = (math.cos(th), -math.sin(th))
        ey_ = (math.sin(th), math.cos(th))
        dv = (p1[0] - c[0], p1[1] - c[1])
        sx = 1 if dv[0] * ex_[0] + dv[1] * ex_[1] >= 0 else -1
        sy = 1 if dv[0] * ey_[0] + dv[1] * ey_[1] >= 0 else -1
        q = {}
        for qx in (1, -1):
            for qy in (1, -1):
                hp = inter(halfplane(c, (ex_[0] * qx, ex_[1] * qx)), halfplane(c, (ey_[0] * qy, ey_[1] * qy)))
                q[(qx, qy)] = area(inter(ink, hp))
        mine = q[(sx, sy)]
        rest = [v for kq, v in q.items() if kq != (sx, sy)]
        p1s = pcbnew.SHAPE_POLY_SET()
        for p in fp.Pads():
            if p.GetNumber() == p1n:
                p.TransformShapeToPolygon(p1s, p.GetPrincipalLayer(), 0, ERR, pcbnew.ERROR_OUTSIDE)
        near1 = area(inter(ink, inflate(p1s, TH['pin1_r'])))
        rec.update(mark_pin=p1n, ink_quadrants={'%+d%+d' % k: round(v, 4) for k, v in q.items()}, ink_near_pin1=round(near1, 4))
        def rx(P, a=ex_):
            d = (P[0] - c[0]) * a[0] + (P[1] - c[1]) * a[1]
            return (P[0] - 2 * d * a[0], P[1] - 2 * d * a[1])
        refls = [lambda P: rx(P, ex_), lambda P: rx(P, ey_), lambda P: rx(rx(P, ex_), ey_)]
        qreg = inter(halfplane(c, (ex_[0] * sx, ex_[1] * sx)), halfplane(c, (ey_[0] * sy, ey_[1] * sy)))
        mk = unpaired_markers(own_items(fp, side), refls, qreg, inflate(p1s, TH['pin1_r']))
        rec['markers'] = [m.get('shape', m.get('text')) + '@' + str(m['at']) for m in mk]
        if all(mine - v > max(TH['pin1_margin'], 0.1 * v) for v in rest) and near1 > 0:
            rec['verdict'] = 'ok'
        elif mk:
            rec['verdict'] = 'ok_marker'
        else:
            # 반평면(1번 패드가 더 치우친 축)
            ax = ex_ if abs(dv[0] * ex_[0] + dv[1] * ex_[1]) >= abs(dv[0] * ey_[0] + dv[1] * ey_[1]) else ey_
            sgn = 1 if dv[0] * ax[0] + dv[1] * ax[1] >= 0 else -1
            h1 = area(inter(ink, halfplane(c, (ax[0] * sgn, ax[1] * sgn))))
            h2 = area(inter(ink, halfplane(c, (-ax[0] * sgn, -ax[1] * sgn))))
            rec.update(ink_half_pin1=round(h1, 4), ink_half_other=round(h2, 4))
            if h1 - h2 > max(TH['pin1_margin'], 0.1 * h2) and near1 > 0:
                rec['verdict'] = 'ok_half'
            else:
                rec.update(verdict='missing', reason='1번 쪽에 치우친 실크 없음')
                S['S9_missing'].append(rec)
    cands.append(rec)

R = dict(board=A.pcb, kicad=pcbnew.Version(), thresholds=TH, mask_margin_board=mm(b.GetDesignSettings().m_SolderMaskExpansion),
         netlist=A.netlist, counts={s: dict(text=sum(1 for i in items if i['side'] == s and i['kind'] == 'text'),
                                            ref=sum(1 for i in refs if i['side'] == s),
                                            shape=sum(1 for i in items if i['side'] == s and i['kind'] == 'shape')) for s in SIDES},
         footprints=len(fps), footprints_without_silk_ref=[r for r in fps if not any(x['owner'] == r for x in refs)],
         orientation=orient, pin1_candidates=cands, findings=S)
R['summary'] = {k: len(v) for k, v in S.items()}
R['summary']['S9_verdicts'] = dict(collections.Counter(c['verdict'] for c in cands))
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(R['summary'], ensure_ascii=False))
