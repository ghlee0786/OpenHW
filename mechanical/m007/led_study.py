"""M-007 J5 보충: LED 직접광 개선안 비교 (CAD 없이 CSG 광선 추적) — python -I -B mechanical/m007/led_study.py
- 판정식은 03_judge.py J5 와 같다: 시야 HFOV 88° × 16:9, 19 × 13 방향, LED 윗면 + 0.05 에서 쏜 광선이 처음 닿는 것이 PMMA 창이면(또는 아무것도 없으면) 비춤.
- 형상: mechanical/m003/geom.py 의 FRONT_COVER · HOUSING · FOAM_LENS_RING (CSG 그대로) + 렌즈 CIL093 4단 (stack-reference.md §2 표 값).
- 기준선(V0)이 Fusion 판정 84.6 % 와 같은지 먼저 맞춘 뒤 개선안을 비교한다. 결과 → led_study.md 표 (stdout)."""
import math, os, sys, json

HERE = os.path.dirname(os.path.abspath(__file__))
M003 = os.path.join(HERE, '..', 'm003')
sys.path.insert(0, M003)
import params, geom  # noqa: E402

LEDS = {'A1': (-6.0, 16.0), 'A2': (6.0, 16.0), 'B1': (-7.5, -16.5), 'B2': (7.5, -16.5)}   # stack-reference §3.4 / M-001e
HFOV, NH, NV = 88.0, 19, 13
STEP = 0.05


def lens_parts(z_head_front=38.785, dome_r=5.0):
    """CIL093: 나사 Ø12 × 13.2 · 단 Ø14 × 4.2 · 머리 Ø18 × 5.4 · 돔 1.4 (stack-reference §2)."""
    zh = z_head_front
    return ('u', geom.zcyl(0, 0, zh - 5.4 - 4.2 - 13.2, zh - 5.4 - 4.2, 6.0), geom.zcyl(0, 0, zh - 5.4 - 4.2, zh - 5.4, 7.0),
            geom.zcyl(0, 0, zh - 5.4, zh, 9.0), geom.zcyl(0, 0, zh, zh + 1.4, dome_r))


def bbox(n):
    t = n[0]
    if t == 'box':
        return n[1:7]
    if t == 'cyl':
        (x0, y0, z0), (x1, y1, z1), r0, r1 = n[1:]
        r = max(r0, r1)
        return (min(x0, x1) - r, max(x0, x1) + r, min(y0, y1) - r, max(y0, y1) + r, min(z0, z1) - r, max(z0, z1) + r)
    if t == 'hs45':
        return (-1e9, 1e9, -1e9, 1e9, -1e9, 1e9)
    if t in ('d',):
        return bbox(n[1])
    bs = [bbox(c) for c in n[1:]]
    if t == 'i':
        return (max(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), min(b[3] for b in bs), max(b[4] for b in bs), min(b[5] for b in bs))
    return (min(b[0] for b in bs), max(b[1] for b in bs), min(b[2] for b in bs), max(b[3] for b in bs), min(b[4] for b in bs), max(b[5] for b in bs))


def inside(n, p):
    t = n[0]
    x, y, z = p
    if t == 'box':
        return n[1] <= x <= n[2] and n[3] <= y <= n[4] and n[5] <= z <= n[6]
    if t == 'cyl':
        (x0, y0, z0), (x1, y1, z1), r0, r1 = n[1:]
        ax = (x1 - x0, y1 - y0, z1 - z0); L2 = ax[0] ** 2 + ax[1] ** 2 + ax[2] ** 2
        s = ((x - x0) * ax[0] + (y - y0) * ax[1] + (z - z0) * ax[2]) / L2
        if s < 0 or s > 1:
            return False
        q = (x0 + ax[0] * s - x, y0 + ax[1] * s - y, z0 + ax[2] * s - z)
        r = r0 + (r1 - r0) * s
        return q[0] ** 2 + q[1] ** 2 + q[2] ** 2 <= r * r
    if t == 'hs45':
        return z - n[2] < y - n[1]
    if t == 'u':
        return any(inside(c, p) for c in n[1:])
    if t == 'i':
        return all(inside(c, p) for c in n[1:])
    if t == 'd':
        return inside(n[1], p) and not any(inside(c, p) for c in n[2:])
    raise ValueError(t)


def model(over=None, lens=True, tube_chamfer=0.0):   # over 에 b_ext 가 없으면 M-003 원형(None) 으로 비교
    """over: params 덮어쓰기. b_ext: (x0, x1, y0) — B 창 주머니를 가운데 x 구간만 y0 까지 늘림(덮개 나사 보스 피함), 턱 1.0 유지."""
    p = dict(params.P); p['b_ext'] = None; p.update(over or {})
    d = params.derive(p)
    P, _ = geom.parts(d)
    cov = P['FRONT_COVER']
    if tube_chamfer > 0:   # 렌즈 관 아래 끝 바깥 모서리 45° 모따기 (관 바깥 반경 → 안 반경)
        ri, ro, zb = d['lens_tube']
        c = min(tube_chamfer, ro - ri)
        cov = ('d', cov, ('d', geom.zcyl(0, 0, zb - 0.01, zb + c, ro + 0.01, ro + 0.01), geom.zcyl(0, 0, zb - 0.02, zb + c + 0.01, ro - c, ro + 0.01)))
    bodies = [('FRONT_COVER', cov), ('HOUSING', P['HOUSING'] if not isinstance(P['HOUSING'], list) else P['HOUSING'][0][1]),
              ('FOAM_LENS_RING', P['FOAM_LENS_RING'])]
    if lens:
        bodies.append(('LENS_CIL093', lens_parts(d['z_win_in'] - 0.5 - 1.4)))
    return d, [(n, b, bbox(b)) for n, b in bodies]


def trace(d, bodies, leds=LEDS):
    vf = 2 * math.degrees(math.atan(math.tan(math.radians(HFOV / 2)) * 1080 / 1920))
    tH, tV = math.tan(math.radians(HFOV / 2)), math.tan(math.radians(vf / 2))
    z0 = d['z_led_top'] + 0.05
    zend = d['z_win_in']          # 창 안쪽 면 — 여기까지 막히지 않으면 처음 닿는 것은 창(또는 바깥)
    lit_ab = lit_a = 0
    blk = {}; miss = []
    for i in range(NH):
        for j in range(NV):
            tx = -tH + 2 * tH * i / (NH - 1); ty = -tV + 2 * tV * j / (NV - 1)
            ok = {}
            for ln, (x, y) in leds.items():
                hit = None
                s = 0.0
                while True:
                    z = z0 + s
                    if z > zend:
                        break
                    q = (x + tx * s, y + ty * s, z)
                    for n, b, bb in bodies:
                        if bb[0] <= q[0] <= bb[1] and bb[2] <= q[1] <= bb[3] and bb[4] <= q[2] <= bb[5] and inside(b, q):
                            hit = n; break
                    if hit:
                        break
                    s += STEP
                ok[ln] = hit is None
                if hit:
                    blk[hit] = blk.get(hit, 0) + 1
            lit_ab += any(ok.values()); lit_a += ok['A1'] or ok['A2']
            if not any(ok.values()):
                miss.append((i, j))
    n = NH * NV
    return {'AB': round(100 * lit_ab / n, 1), 'A': round(100 * lit_a / n, 1), 'blockers': blk, 'miss': miss}


def ang(t):
    return round(math.degrees(math.atan(t)), 1)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    VAR = [
        ('V0 기준 (현재)', {}, {}),
        ('V0-렌즈 없음 (렌즈 가림 상한)', {}, {'lens': False}),
        ('V1 렌즈 관 LED 쪽 모따기 1.2', {}, {'tube_chamfer': 1.2}),
        ('V2 가운데 띠 rib_y 12.2→11.2 (렌즈 창 벽 0.55)', {'rib_y': 11.2}, {}),
        ('V3 B 창 바깥 끝 −28.4→−30.4 (나사 보스 겹침)', {'b_pocket_y0': -30.4}, {}),
        ('V4 B 창 가운데만 y −33.2 까지 (x −17.3…14.3, 보스 0.5 비킴) — 선택, M-003 params.b_ext', {'b_ext': params.P['b_ext']}, {}),
        ('V5 LED B y −16.5→−12.7 (pcb 이동)', {'led_b_y': -12.7}, {'leds': {**LEDS, 'B1': (-7.5, -12.7), 'B2': (7.5, -12.7)}}),
        ('V6 LED 띄움 K13 (윗면 z 13.645→30)', {'led_top_above_front': 30 - 11.2}, {}),
    ]
    rows = []
    for name, over, kw in VAR:
        leds = kw.pop('leds', LEDS)
        d, bodies = model(over, **kw)
        r = trace(d, bodies, leds)
        rows.append((name, r))
        print('| %s | %.1f | %.1f | %s | %d |' % (name, r['AB'], r['A'], json.dumps(r['blockers'], ensure_ascii=False), len(r['miss'])), flush=True)
    d = params.derive(params.P)
    vt = math.tan(math.radians(HFOV / 2)) * 1080 / 1920
    print('VFOV/2', ang(vt), 'z_led_top', d['z_led_top'], 'z_win_in', d['z_win_in'], 'z_bez_in', d['z_bez_in'], 'y_in_hi', d['y_in_hi'])
    print('V0 miss', rows[0][1]['miss'])
