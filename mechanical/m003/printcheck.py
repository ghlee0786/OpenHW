"""M-003c 출력 검사 (CAD 독립): STL 에서 출력 방향 기준 오버행(> 45°)·브리지(수평 아래면)를 찾아 표로.
실행: python -I -B mechanical/m003/printcheck.py → printcheck.md
판정 규칙: 면 법선 n, 출력 위 방향 u. n·u < −sin45° (= 수직에서 45° 넘게 기운 아래 향한 면) 이고 바닥(첫 층) 위에 있으면 오버행.
그중 n·u < −0.99 는 수평 아래면 = 브리지(양쪽이 받쳐지면) 또는 받침 필요 천장. 이웃 면을 꼭짓점 공유로 묶어 덩어리마다 크기를 낸다."""
import math, os, struct, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))


def read_stl(path):
    data = open(path, 'rb').read()
    n = struct.unpack('<I', data[80:84])[0]
    if 84 + n * 50 == len(data):
        tris = []
        for i in range(n):
            v = struct.unpack('<12f', data[84 + i * 50: 84 + i * 50 + 48])
            tris.append((v[3:6], v[6:9], v[9:12]))
        return tris
    tris, cur = [], []
    for line in data.decode('ascii', 'ignore').splitlines():
        s = line.split()
        if s and s[0] == 'vertex':
            cur.append(tuple(float(x) for x in s[1:4]))
            if len(cur) == 3:
                tris.append(tuple(cur)); cur = []
    return tris


def analyse(path, up, label):
    tris = read_stl(path)
    k = 10.0 if max(abs(c) for t in tris[:50] for p in t for c in p) < 10 else 1.0   # cm → mm 보정
    tris = [tuple(tuple(c * k for c in p) for p in t) for t in tris]
    hs = [sum(p[i] * up[i] for i in range(3)) for t in tris for p in t]
    h0 = min(hs)
    lim = -math.sin(math.radians(45))
    bad = []
    for t in tris:
        a, b, c = t
        ux, uy, uz = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
        vx, vy, vz = (c[0] - a[0], c[1] - a[1], c[2] - a[2])
        nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        L = math.sqrt(nx * nx + ny * ny + nz * nz)
        if L == 0:
            continue
        dot = (nx * up[0] + ny * up[1] + nz * up[2]) / L
        h = min(sum(p[i] * up[i] for i in range(3)) for p in t)
        if dot < lim and h > h0 + 0.05:
            bad.append((t, L / 2, dot))
    # 꼭짓점 공유로 묶기
    parent = list(range(len(bad)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    vmap = {}
    for i, (t, _, _) in enumerate(bad):
        for p in t:
            key = tuple(round(c, 3) for c in p)
            if key in vmap:
                ra, rb = find(i), find(vmap[key])
                if ra != rb:
                    parent[ra] = rb
            else:
                vmap[key] = i
    groups = {}
    for i in range(len(bad)):
        groups.setdefault(find(i), []).append(i)
    rows = []
    for idx in groups.values():
        pts = [p for i in idx for p in bad[i][0]]
        area = sum(bad[i][1] for i in idx)
        flat = all(bad[i][2] < -0.99 for i in idx)
        mn = [min(p[j] for p in pts) for j in range(3)]
        mx = [max(p[j] for p in pts) for j in range(3)]
        hgt = min(sum(p[j] * up[j] for j in range(3)) for p in pts) - h0
        dims = sorted([mx[j] - mn[j] for j in range(3) if abs(up[j]) < 0.5])
        rows.append((area, flat, mn, mx, hgt, dims))
    rows.sort(key=lambda r: -r[0])
    out = ['### %s — 출력 위 방향 %s, 삼각형 %d, 첫 층 높이 기준 %.2f' % (label, up, len(tris), h0),
           '', '| # | 종류 | 면적 mm² | 바닥에서 높이 | 범위 x / y / z (mm) | 짧은 변 / 긴 변 | 채움 | 모양 |', '|---|---|---|---|---|---|---|---|']
    for n, (area, flat, mn, mx, hgt, dims) in enumerate(rows[:25], 1):
        a_, b_ = (dims + [0, 0])[:2]
        fill = area / (a_ * b_) if a_ * b_ > 0 else 0
        kind = '수평 아래면' if flat else '경사 > 45°'
        shape = '꽉 찬 면' if fill > 0.6 else '고리·테두리 (내민 폭 ≈ %.1f)' % (area / (2 * (a_ + b_)) if a_ + b_ else 0)
        out.append('| %d | %s | %.1f | %.2f | %.1f…%.1f / %.1f…%.1f / %.1f…%.1f | %.1f / %.1f | %.2f | %s |' % (
            n, kind, area, hgt, mn[0], mx[0], mn[1], mx[1], mn[2], mx[2], a_, b_, fill, shape))
    out.append('\n- 덩어리 %d개 (표는 면적 큰 순 25개까지), 오버행 면적 합 %.1f mm².' % (len(rows), sum(r[0] for r in rows)))
    return out


lines = ['# M-003c 출력 검사 (printcheck.py 출력)', '',
         '- 기준: 오버행 = 수직에서 45° 넘게 기운 아래 향한 면 (첫 층 제외). 판정은 print-prep.md §3 에서 덩어리마다 한다 (벽 개구 윗변은 양 끝만 받쳐지므로 브리지 = 긴 변, 꽉 찬 천장은 짧은 변, 고리는 내민 폭).', '']
lines += analyse(os.path.join(HERE, 'out', 'stl', 'HOUSING.stl'), (0, 0, 1), 'HOUSING (뒷벽이 바닥)')
lines.append('')
lines += analyse(os.path.join(HERE, 'out', 'stl', 'FRONT_COVER.stl'), (0, 0, -1), 'FRONT_COVER (바깥 앞면이 바닥)')
open(os.path.join(HERE, 'printcheck.md'), 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
