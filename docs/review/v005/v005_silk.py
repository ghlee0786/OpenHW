# -*- coding: utf-8 -*-
"""V-005 B. 실크스크린 독립 검사 (KiCad 10 pcbnew, 읽기 전용). 면(F/B)마다:

  S1 패드·노출 동박(마스크 개구) 위 실크 잉크 면적 > 0 인 항목 (제조 시 잘림)
  S2 실크–마스크 개구 간격 < 0.15mm (프로젝트 DRU fab_silk_to_pad)
  S3 선폭 < 0.15mm (채움 없는 선·원·호·사각형)
  S4 글자 높이 < 1.0mm, 획 < 0.15mm, 획/높이 < 1/5 (PCBWay 「Character Width to Height Ratio 1:5」, 참고)
  S5 보드 외곽까지 < EDGE_MM (기본 0.30 — CNC 외형 공차 ±0.2 + 0.1) 또는 외곽 밖
  S6 참조 지정자가 같은 면 부품 courtyard 안(글자 중심이 안 = 숨음, 잉크가 걸침 = 걸침)
  S7 글자끼리 잉크 겹침, 글자와 다른 실크 선 겹침
  S8 읽는 방향(그려지는 회전각) 종류 수
  S9 1번 핀·극성 후보 부품(D·LED·U·J·전해 C): 자기 실크 항목 수, 1번 패드 쪽 표시 후보(1번 패드 가장자리 1.0mm 안, 다른 패드보다 1번 패드에 가까운 실크) — 사람 확인용
사용: python.exe -I v005_silk.py <board.kicad_pcb> <out.json> [EDGE_MM]
"""
import sys, json, math, collections
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
mm = pcbnew.ToMM
FM = pcbnew.FromMM
ERR = FM(0.005)
path, out = sys.argv[1], sys.argv[2]
EDGE_MM = float(sys.argv[3]) if len(sys.argv) > 3 else 0.30
b = pcbnew.LoadBoard(path)
ds = b.GetDesignSettings()
mask_margin_board = mm(ds.m_SolderMaskExpansion)

SIDES = {'F': (pcbnew.F_SilkS, pcbnew.F_Mask, pcbnew.F_Cu, pcbnew.F_CrtYd),
         'B': (pcbnew.B_SilkS, pcbnew.B_Mask, pcbnew.B_Cu, pcbnew.B_CrtYd)}


def area(s):
    return s.Area() / 1e12


def inter(a, c):
    x = pcbnew.SHAPE_POLY_SET(a)
    x.BooleanIntersection(c)
    return x


def bbox_of(s):
    bb = s.BBox()
    return [round(mm(bb.GetX()), 3), round(mm(bb.GetY()), 3), round(mm(bb.GetRight()), 3), round(mm(bb.GetBottom()), 3)]


def owner(it):
    fp = it.GetParentFootprint()
    return fp.GetReference() if fp else '(보드)'


# ---------- 실크 항목 모으기 ----------
items = []  # dict(kind, owner, side, ink(SHAPE_POLY_SET), obj, desc)
for fp in b.Footprints():
    texts = [fp.Reference(), fp.Value()] + [x for x in fp.GraphicalItems() if x.GetClass() in ('PCB_TEXT', 'PCB_FIELD')]
    try:
        texts += [f for f in fp.GetFields() if f not in (fp.Reference(), fp.Value())]
    except Exception:
        pass
    seen = set()
    for t in texts:
        if id(t) in seen:
            continue
        seen.add(id(t))
        for side, (silk, *_r) in SIDES.items():
            if t.GetLayer() != silk or not t.IsVisible():
                continue
            s = pcbnew.SHAPE_POLY_SET()
            t.TransformTextToPolySet(s, 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='text', owner=fp.GetReference(), side=side, ink=s, obj=t, text=t.GetShownText(True)))
    for g in fp.GraphicalItems():
        if g.GetClass() != 'PCB_SHAPE':
            continue
        for side, (silk, *_r) in SIDES.items():
            if g.GetLayer() != silk:
                continue
            s = pcbnew.SHAPE_POLY_SET()
            g.TransformShapeToPolygon(s, silk, 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='shape', owner=fp.GetReference(), side=side, ink=s, obj=g))
for d in b.GetDrawings():
    for side, (silk, *_r) in SIDES.items():
        if d.GetLayer() != silk:
            continue
        s = pcbnew.SHAPE_POLY_SET()
        if d.GetClass() in ('PCB_TEXT', 'PCB_TEXTBOX'):
            d.TransformTextToPolySet(s, 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='text', owner='(보드)', side=side, ink=s, obj=d, text=d.GetShownText(True)))
        else:
            d.TransformShapeToPolygon(s, silk, 0, ERR, pcbnew.ERROR_INSIDE)
            items.append(dict(kind='shape', owner='(보드)', side=side, ink=s, obj=d))

# ---------- 마스크 개구 ----------
mask_open = {}
for side, (silk, mlayer, cu, cy) in SIDES.items():
    s = pcbnew.SHAPE_POLY_SET()
    for fp in b.Footprints():
        for p in fp.Pads():
            if not p.IsOnLayer(mlayer):
                continue
            # 마스크 개구 = 패드 + 실효 마스크 확장(패드·부품·보드 설정 순, KiCad 계산값)
            p.TransformShapeToPolygon(s, mlayer, max(0, p.GetSolderMaskExpansion(mlayer)), ERR, pcbnew.ERROR_OUTSIDE)
        for g in fp.GraphicalItems():
            if g.GetLayer() == mlayer and g.GetClass() == 'PCB_SHAPE':
                g.TransformShapeToPolygon(s, mlayer, 0, ERR, pcbnew.ERROR_OUTSIDE)
    for t in b.Tracks():
        if t.GetClass() == 'PCB_VIA':
            tented = True
            try:
                tented = t.IsTented(mlayer)
            except Exception:
                pass
            if not tented:
                t.TransformShapeToPolygon(s, mlayer, 0, ERR, pcbnew.ERROR_OUTSIDE)
    for d in b.GetDrawings():
        if d.GetLayer() == mlayer and d.GetClass() == 'PCB_SHAPE':
            d.TransformShapeToPolygon(s, mlayer, 0, ERR, pcbnew.ERROR_OUTSIDE)
    for z in b.Zones():
        if not z.GetIsRuleArea() and z.GetLayerSet().Contains(mlayer):
            s.BooleanAdd(z.Outline())
    s.Simplify()
    mask_open[side] = s

edge = pcbnew.SHAPE_POLY_SET()
b.GetBoardPolygonOutlines(edge, False)
edge_in = pcbnew.SHAPE_POLY_SET(edge)
edge_in.Inflate(-FM(EDGE_MM), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)

for fp in b.Footprints():
    fp.BuildCourtyardCaches()


def min_dist(a, c, hi=1.0):
    x = pcbnew.SHAPE_POLY_SET(a); x.BooleanIntersection(c)
    if x.Area() > 0:
        return 0.0
    lo = 0.0
    for _ in range(12):
        m = (lo + hi) / 2
        t = pcbnew.SHAPE_POLY_SET(a); t.Inflate(FM(m), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR); t.BooleanIntersection(c)
        if t.Area() > 0:
            hi = m
        else:
            lo = m
    return round(hi, 3)


edge_ring = pcbnew.SHAPE_POLY_SET(edge)
_big = pcbnew.SHAPE_POLY_SET(edge); _big.Inflate(FM(5), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
_big.BooleanSubtract(edge)
edge_ring = _big  # 보드 밖 띠: 실크가 여기까지의 거리 = 외곽까지 거리


def desc(it):
    o = it['obj']
    bb = it['ink'].BBox() if it['ink'].OutlineCount() else o.GetBoundingBox()
    d = dict(owner=it['owner'], side=it['side'], kind=it['kind'],
             at=[round(mm(bb.Centre().x), 2), round(mm(bb.Centre().y), 2)], bbox=[round(mm(bb.GetX()), 2), round(mm(bb.GetY()), 2), round(mm(bb.GetRight()), 2), round(mm(bb.GetBottom()), 2)])
    if it['kind'] == 'text':
        d['text'] = it['text']
    else:
        d['shape'] = o.ShowShape() if hasattr(o, 'ShowShape') else o.GetClass()
    return d


R = dict(board=path, kicad=pcbnew.Version(), edge_mm=EDGE_MM, mask_margin_board=mask_margin_board,
         counts={s: dict(text=sum(1 for i in items if i['side'] == s and i['kind'] == 'text'),
                         shape=sum(1 for i in items if i['side'] == s and i['kind'] == 'shape')) for s in SIDES})
S = {k: [] for k in ('S1_on_mask_open', 'S2_clear_lt_0p15', 'S3_line_lt_0p15', 'S4_text', 'S4_ratio_lt_1to5', 'S5_edge', 'S6_ref_hidden', 'S6_ref_touch', 'S7_text_text', 'S7_text_line')}
for it in items:
    side = it['side']
    ink = it['ink']
    if ink.OutlineCount() == 0:
        continue
    a = area(inter(ink, mask_open[side]))
    if a > 1e-5:
        S['S1_on_mask_open'].append(dict(desc(it), area=round(a, 4)))
    else:
        inf = pcbnew.SHAPE_POLY_SET(ink)
        inf.Inflate(FM(0.15) - 1, pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
        a2 = area(inter(inf, mask_open[side]))
        if a2 > 1e-5:
            S['S2_clear_lt_0p15'].append(dict(desc(it), dist=min_dist(ink, mask_open[side], 0.2)))
    o = it['obj']
    if it['kind'] == 'shape':
        filled = o.IsSolidFill() if hasattr(o, 'IsSolidFill') else o.IsFilled()
        w = mm(o.GetWidth())
        if not filled and w < 0.15 - 1e-6:
            S['S3_line_lt_0p15'].append(dict(desc(it), width=round(w, 3)))
    else:
        h, th = mm(o.GetTextHeight()), mm(o.GetEffectiveTextPenWidth())
        if h < 1.0 - 1e-6 or th < 0.15 - 1e-6:
            S['S4_text'].append(dict(desc(it), height=round(h, 3), stroke=round(th, 3)))
        if th / h < 0.2 - 1e-6:
            S['S4_ratio_lt_1to5'].append(dict(desc(it), height=round(h, 3), stroke=round(th, 3)))
    out_edge = pcbnew.SHAPE_POLY_SET(ink)
    out_edge.BooleanSubtract(edge_in)
    a3 = area(out_edge)
    if a3 > 1e-5:
        outside = pcbnew.SHAPE_POLY_SET(ink); outside.BooleanSubtract(edge)
        S['S5_edge'].append(dict(desc(it), dist_edge=min_dist(ink, edge_ring, 1.0), area_outside_board=round(area(outside), 4)))

# S6 참조 지정자 숨음
refs = [i for i in items if i['kind'] == 'text' and i['owner'] != '(보드)' and i['text'] == i['owner']]
for it in refs:
    side = it['side']
    cyl = SIDES[side][3]
    c = it['ink'].BBox().Centre()
    for fp in b.Footprints():
        cy = fp.GetCourtyard(cyl)
        if cy.OutlineCount() == 0:
            continue
        if cy.Contains(c):
            S['S6_ref_hidden'].append(dict(desc(it), under=fp.GetReference(), dnp_under=fp.IsDNP()))
        else:
            a = area(inter(it['ink'], cy))
            if a > 1e-5:
                S['S6_ref_touch'].append(dict(desc(it), under=fp.GetReference(), area=round(a, 4)))
R['refs_on_silk'] = {s: len([r for r in refs if r['side'] == s]) for s in SIDES}
fps_no_silk_ref = [fp.GetReference() for fp in b.Footprints() if not any(r['owner'] == fp.GetReference() for r in refs)]
R['footprints_without_silk_ref'] = fps_no_silk_ref

# S7 겹침
texts = [i for i in items if i['kind'] == 'text' and i['ink'].OutlineCount()]
shapes = [i for i in items if i['kind'] == 'shape' and i['ink'].OutlineCount()]
for i in range(len(texts)):
    for j in range(i + 1, len(texts)):
        A, B_ = texts[i], texts[j]
        if A['side'] != B_['side'] or not A['ink'].BBox().Intersects(B_['ink'].BBox()):
            continue
        a = area(inter(A['ink'], B_['ink']))
        if a > 1e-5:
            S['S7_text_text'].append(dict(a=desc(A), b=desc(B_), area=round(a, 4)))
    for sh in shapes:
        A = texts[i]
        if A['side'] != sh['side'] or not A['ink'].BBox().Intersects(sh['ink'].BBox()):
            continue
        a = area(inter(A['ink'], sh['ink']))
        if a > 1e-5:
            S['S7_text_line'].append(dict(text=desc(A), line=desc(sh), area=round(a, 4)))

# S8 방향
orient = {}
for side in SIDES:
    c = collections.Counter()
    for it in texts:
        if it['side'] != side:
            continue
        ang = it['obj'].GetDrawRotation().AsDegrees() % 360
        c[round(ang) % 360] += 1
    orient[side] = dict(c)
R['orientation'] = orient
R['mirrored_check'] = {s: dict(mirrored=sum(1 for t in texts if t['side'] == s and t['obj'].IsMirrored()),
                               total=sum(1 for t in texts if t['side'] == s)) for s in SIDES}

# S9 1번 핀·극성 후보
cands = []
for fp in b.Footprints():
    ref = fp.GetReference()
    fpid = fp.GetFPIDAsString()
    is_pol = (ref[0] in 'DUJ' and not ref.startswith('DNP')) or ref.startswith('LED') or (ref.startswith('C') and ('CP_' in fpid or 'Elec' in fpid)) or ref.startswith('X') or ref.startswith('Q')
    if not is_pol or ref.startswith('H') or ref.startswith('TP'):
        continue
    side = 'B' if fp.IsFlipped() else 'F'
    own = [i for i in items if i['owner'] == ref and i['side'] == side and not (i['kind'] == 'text' and i['text'] in (ref, fp.GetValue()))]
    pads = [p for p in fp.Pads() if p.GetNumber() not in ('', 'MP')]
    p1 = [p for p in pads if p.GetNumber() in ('1', 'A1', 'K')]
    hint = 0
    if p1:
        p1s = pcbnew.SHAPE_POLY_SET()
        p1[0].TransformShapeToPolygon(p1s, SIDES[side][2], 0, ERR, pcbnew.ERROR_OUTSIDE)
        p1i = pcbnew.SHAPE_POLY_SET(p1s); p1i.Inflate(FM(1.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
        others = [p for p in pads if p.GetNumber() != p1[0].GetNumber()]
        for i in own:
            if area(inter(i['ink'], p1i)) <= 1e-5:
                continue
            c = i['ink'].BBox().Centre()
            d1 = mm((c - p1[0].GetPosition()).EuclideanNorm())
            do = min([mm((c - p.GetPosition()).EuclideanNorm()) for p in others] or [1e9])
            if d1 < do:
                hint += 1
    cands.append(dict(ref=ref, side=side, value=fp.GetValue(), fpid=fpid, dnp=fp.IsDNP(),
                      pos=[round(mm(fp.GetPosition().x), 2), round(mm(fp.GetPosition().y), 2)],
                      bbox=[round(mm(q), 2) for q in (fp.GetBoundingBox(False).GetX(), fp.GetBoundingBox(False).GetY(), fp.GetBoundingBox(False).GetRight(), fp.GetBoundingBox(False).GetBottom())],
                      own_silk_items=len(own), pin1_hint_items=hint, has_pin1=bool(p1)))
R['pin1_candidates'] = cands
R['findings'] = S
R['summary'] = {k: len(v) for k, v in S.items()}
R['summary']['pin1_no_own_silk'] = [c['ref'] for c in cands if c['own_silk_items'] == 0]
R['summary']['pin1_no_hint'] = [c['ref'] for c in cands if c['own_silk_items'] and c['pin1_hint_items'] == 0]
json.dump(R, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1, default=str)
print(json.dumps(R['summary'], ensure_ascii=False))
print('orientation', json.dumps(orient), 'mirror', json.dumps(R['mirrored_check']))
