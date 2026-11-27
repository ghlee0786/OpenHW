# F5·F6 (pcb 전면 5a20d44 DRC) 판단용 계산. 보드 파일은 읽기만 한다.
# 사용: python -I -B mechanical/m008/f5f6_drc.py <front.kicad_pcb>
# F5: J2(CLA216 리드 납땜 패드) courtyard ↔ H1 / F6: MH1 courtyard ↔ 뒷면 J1 BTB 고정 핀 NPTH
import math
import re
import sys

from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

sys.stdout.reconfigure(encoding='utf-8')
s = open(sys.argv[1], encoding='utf-8').read()


def blocks(t, key):
    for m in re.finditer(r'\(' + key + r'\s', t):
        i = m.start()
        d = 0
        for j in range(i, len(t)):
            if t[j] == '(':
                d += 1
            elif t[j] == ')':
                d -= 1
                if d == 0:
                    yield t[i:j + 1]
                    break


def xf(at, lx, ly):
    x, y, r = at
    a = math.radians(r)
    return (x + lx * math.cos(a) + ly * math.sin(a), y - lx * math.sin(a) + ly * math.cos(a))


def nums(t, key):
    return [float(v) for v in re.search(r'\(' + key + r' ([-\d.]+) ([-\d.]+)', t).groups()]


FP = {}
for fp in blocks(s, 'footprint'):
    ref = re.search(r'\(property "Reference" "([^"]+)"', fp).group(1)
    a = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', fp).groups()
    at = (float(a[0]), float(a[1]), float(a[2] or 0))
    cy = {'F': [], 'B': []}
    body = fp.split('(pad ', 1)[0]
    for kind in ('fp_rect', 'fp_poly', 'fp_circle'):
        for g in blocks(body, kind):
            m = re.search(r'\(layer "(F|B)\.CrtYd"\)', g)
            if not m:
                continue
            if kind == 'fp_rect':
                (x0, y0), (x1, y1) = nums(g, 'start'), nums(g, 'end')
                pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                cy[m.group(1)].append(Polygon([xf(at, *p) for p in pts]))
            elif kind == 'fp_poly':
                pts = [tuple(map(float, p)) for p in re.findall(r'\(xy ([-\d.]+) ([-\d.]+)\)', g)]
                cy[m.group(1)].append(Polygon([xf(at, *p) for p in pts]))
            else:
                c, e = nums(g, 'center'), nums(g, 'end')
                cy[m.group(1)].append(Point(*xf(at, *c)).buffer(math.dist(c, e), 256))
    holes = []
    for p in blocks(fp, 'pad'):
        if 'np_thru_hole' in p:
            px, py = nums(p, 'at')
            holes.append((xf(at, px, py), float(re.search(r'\(drill ([-\d.]+)', p).group(1))))
    pads = {}
    for p in blocks(fp, 'pad'):
        m = re.match(r'\(pad "(\w+)" thru_hole', p)
        if m:
            px, py = nums(p, 'at')
            pads[m.group(1)] = (xf(at, px, py), nums(p, 'size'))
    FP[ref] = dict(at=at, cy={k: unary_union(v) if v else None for k, v in cy.items()}, holes=holes, pads=pads)


def others(side, skip):
    return [(r, f['cy'][side]) for r, f in FP.items() if r not in skip and f['cy'][side] is not None]


def fmt(v):
    return f'{v:.3f}'


print('== F5  J2 ↔ H1')
j2, h1 = FP['J2'], FP['H1']
(p1, sz), (p2, _) = j2['pads']['1'], j2['pads']['2']
hx, hy = h1['at'][:2]
print('J2 패드1', p1, '패드2', p2, '크기', sz, '/ H1', (hx, hy), 'courtyard r', fmt(h1['cy']['F'].exterior.distance(Point(hx, hy))))
ov = j2['cy']['F'].intersection(h1['cy']['F'])
print('현재 courtyard 겹침 면적', fmt(ov.area), 'mm²  bbox', [fmt(v) for v in ov.bounds])
HEAD_R = 1.5   # M1.6 나사 머리 Ø3.0 (DIN 912 dk 3.0) — 1.53 여유가 나오는 값
gap = math.dist(p2, (hx, hy)) - sz[0] / 2 - HEAD_R
print('패드2 가장자리 ↔ H1 나사 머리 Ø3.0 여유', fmt(gap))
# (b) 헤더 몸체 없는 2패드: courtyard = 패드 외형 + 0.25 (사각 감싸기)
half = sz[0] / 2 + 0.25
cb = box(min(p1[0], p2[0]) - half, min(p1[1], p2[1]) - half, max(p1[0], p2[0]) + half, max(p1[1], p2[1]) + half)
print('(b) 새 courtyard 전역', [fmt(v) for v in cb.bounds], '/ 국소 (패드1 기준, 0°)', (-half, -half), (half, abs(p2[1] - p1[1]) + half))
print('(b) ↔ H1 courtyard 거리', fmt(cb.distance(h1['cy']['F'])))
worst = min(((cb.distance(g), r) for r, g in others('F', ('J2',))))
print('(b) ↔ 가장 가까운 다른 F.CrtYd', worst[1], fmt(worst[0]))
for r, g in others('F', ('J2',)):
    if cb.intersects(g):
        print('  (b) 겹침!', r)
# (a) 헤더 courtyard 그대로 패드 이동: H1 원(r 2) 에서 벗어나는 최소 이동
for name, (dx, dy) in (('+x', (1, 0)), ('+y', (0, 1))):
    lo, hi = 0.0, 5.0
    for _ in range(60):
        mid = (lo + hi) / 2
        from shapely.affinity import translate
        moved = translate(j2['cy']['F'], dx * mid, dy * mid)
        if moved.intersects(h1['cy']['F']) and moved.intersection(h1['cy']['F']).area > 1e-9:
            lo = mid
        else:
            hi = mid
    moved = translate(j2['cy']['F'], dx * hi, dy * hi)
    hit = [r for r, g in others('F', ('J2',)) if moved.intersection(g).area > 1e-9]
    print(f'(a) 이동 {name} 최소', fmt(hi), '→ 그 자리 다른 겹침', hit)

print('== F6  MH1 ↔ J1 NPTH')
mh, j1 = FP['MH1'], FP['J1']
mx, my = mh['at'][:2]
print('MH1 at', mh['at'], 'F.CrtYd bbox', [fmt(v) for v in mh['cy']['F'].bounds])
for (c, d) in j1['holes']:
    hole = Point(*c).buffer(d / 2, 256)
    print('J1 NPTH', c, 'Ø', d, '국소', (fmt(c[0] - mx), fmt(c[1] - my)), '현재 courtyard 와 겹침', fmt(hole.intersection(mh['cy']['F']).area))
    # 스페이서·홀더 몸체 바닥 (cla216_spec: X ±7.95, 기계 Y −8.65…+11.65 → KiCad y = −Y)
    sp = box(mx - 7.95, my - 11.65, mx + 7.95, my + 8.65)
    peg = Point(*c).buffer(0.25, 256)   # HCTL 소켓 보스 Ø0.50
    print('   구멍 ∩ 스페이서 바닥', fmt(hole.intersection(sp).area), 'mm²  보스 Ø0.50 ∩ 스페이서', fmt(peg.intersection(sp).area), 'mm²')
# 새 MH1 F.CrtYd (국소 좌표, 0°): 두 구멍 둘레 노치 x ±7.80, y −10.10
NEW = [(-7.8, -11.9), (7.8, -11.9), (7.8, -10.1), (8.2, -10.1), (8.2, -2.75), (12.45, -2.75), (12.45, 2.75), (8.2, 2.75), (8.2, 8.9),
       (-8.2, 8.9), (-8.2, 2.75), (-12.45, 2.75), (-12.45, -2.75), (-8.2, -2.75), (-8.2, -10.1), (-7.8, -10.1)]
newp = Polygon([xf(mh['at'], *p) for p in NEW])
print('새 F.CrtYd 국소 꼭짓점', NEW)
for (c, d) in j1['holes']:
    hole = Point(*c).buffer(d / 2, 256)
    print('   새 courtyard ↔ 구멍', c, '겹침', fmt(hole.intersection(newp).area), '거리', fmt(newp.exterior.distance(hole)))
print('   줄어든 면적', fmt(mh['cy']['F'].area - newp.area), 'mm² · 새 외형이 옛 외형 안', newp.buffer(-1e-6).within(mh['cy']['F']))
