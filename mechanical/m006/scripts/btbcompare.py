"""BTB 짝 대조: 우리 보드 vs Seeed 보드 (같은 코어 커넥터에 결합). 코어 좌표(코어 중심, y 위)로 옮겨 패드별 위치·넷을 나란히 둔다.
코어 중심 = Seeed 보드는 장착 구멍 4개(±13) 중심, 우리 보드는 (100,100). 출력: btb_pads.csv + 요약."""
import csv, math, re, sys

sys.stdout.reconfigure(encoding='utf-8')


def fp_block(t, ref):
    i = t.find('(property "Reference" "%s"' % ref)
    s = t.rfind('(footprint', 0, i)
    dpt = 0; k = s
    while True:
        c = t[k]
        if c == '(':
            dpt += 1
        elif c == ')':
            dpt -= 1
            if dpt == 0:
                break
        k += 1
    return t[s:k + 1]


def pads(path, ref, centre):
    t = open(path, encoding='utf-8', errors='replace').read()
    blk = fp_block(t, ref)
    at = re.search(r'\n\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
    X0, Y0 = float(at.group(1)), float(at.group(2)); th = math.radians(float(at.group(3) or 0))
    out = {}
    for p in re.finditer(r'\(pad "([^"]*)" (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)(.*?)\n\t\t\)', blk, re.S):
        x, y = float(p.group(4)), float(p.group(5))
        X = X0 + x * math.cos(th) + y * math.sin(th); Y = Y0 - x * math.sin(th) + y * math.cos(th)
        net = re.search(r'\(net (?:\d+ )?"([^"]*)"\)', p.group(6))
        cx, cy = centre
        out.setdefault(p.group(1), []).append((round(X - cx, 3), round(-(Y - cy), 3), net.group(1) if net else ''))
    return out


SE = r"C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\decb4398-40a5-4677-aeb1-556f1d7e2c56\scratchpad\m006"
pairs = [
    ('core J1 (윗면) ↔ 전면 J1', (SE + r"\ours\front.kicad_pcb", 'J1', (100.0, 100.0)), (SE + r"\seeed\s401.kicad_pcb", 'J1', (114.989, 115.0)), 'S401'),
    ('core J2 (아랫면) ↔ 캐리어 J1', (SE + r"\ours\carrier.kicad_pcb", 'J1', (100.0, 100.0)), (SE + r"\seeed\b301.kicad_pcb", 'J1', (115.0, 115.001)), 'B301'),
    ('core J2 (아랫면) ↔ 캐리어 J1', (SE + r"\ours\carrier.kicad_pcb", 'J1', (100.0, 100.0)), (SE + r"\seeed\b101.kicad_pcb", 'J1', (113.544, 98.48)), 'B101'),
]
rows = []
PWR = re.compile(r'GND|VIN|VSYS|5V|3V3|VBUS|VCC|1V8|12V', re.I)
for title, ours, seeed, sname in pairs:
    a = pads(*ours); b = pads(*seeed)
    dmax = 0.0; npw = 0; mism = []
    for k in sorted(set(a) | set(b), key=lambda s: (len(s), s)):
        for i in range(max(len(a.get(k, [])), len(b.get(k, [])))):
            pa = a.get(k, [None])[i] if i < len(a.get(k, [])) else None
            pb = b.get(k, [None])[i] if i < len(b.get(k, [])) else None
            dd = math.hypot(pa[0] - pb[0], pa[1] - pb[1]) if pa and pb else None
            if dd is not None:
                dmax = max(dmax, dd)
            ga = bool(pa and re.search(r'GND', pa[2], re.I)); gb = bool(pb and re.search(r'GND', pb[2], re.I))
            if pa and pb and (ga != gb):
                mism.append(k)
            rows.append([title, sname, k, pa[0] if pa else '', pa[1] if pa else '', pa[2] if pa else '', pb[0] if pb else '', pb[1] if pb else '',
                         pb[2] if pb else '', '%.3f' % dd if dd is not None else ''])
    print('%s vs %s: 패드 %d/%d, 위치 최대 차 %.3f mm, GND 여부가 다른 패드 %s' % (title, sname, len(a), len(b), dmax, mism or '없음'))
with open(SE + r"\btb_pads.csv", 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['pair', 'seeed_board', 'pad', 'ours_x', 'ours_y', 'ours_net', 'seeed_x', 'seeed_y', 'seeed_net', 'pos_diff_mm'])
    w.writerows(rows)
print('rows', len(rows))
# S401 J3 (GH 2P) 넷
t = open(SE + r"\seeed\s401.kicad_pcb", encoding='utf-8', errors='replace').read()
blk = fp_block(t, 'J3')
print('S401 J3', re.search(r'\(footprint "([^"]+)"', blk).group(1), re.findall(r'\(pad "([^"]*)".*?\(net (?:\d+ )?"([^"]*)"\)', blk, re.S))
