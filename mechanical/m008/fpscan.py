"""KiCad 보드의 풋프린트 목록 (기구 좌표: 보조 원점 = 코어 중심 (100,100), y 위). 면 필터와 fab/courtyard 외곽.
사용: python -I -B fpscan.py <board.kicad_pcb> [F.Cu|B.Cu]"""
import math, re, sys

sys.stdout.reconfigure(encoding='utf-8')
t = open(sys.argv[1], encoding='utf-8').read()
side = sys.argv[2] if len(sys.argv) > 2 else None
for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
    s = m.start() + 1
    e = t.find('\n\t(footprint', s)
    blk = t[s:e if e > 0 else len(t)]
    ref = re.search(r'\(property "Reference" "([^"]+)"', blk).group(1)
    lay = re.search(r'\(layer "([^"]+)"\)', blk).group(1)
    if side and lay != side:
        continue
    at = re.search(r'\n\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
    X0, Y0 = float(at.group(1)), float(at.group(2)); th = math.radians(float(at.group(3) or 0))
    box = {}
    for it in re.finditer(r'\n\t\t\((fp_line|fp_rect|fp_poly|fp_circle)(.*?)\n\t\t\)', blk, re.S):
        lm = re.search(r'\(layer "([^"]+)"\)', it.group(2))
        if not lm or not lm.group(1).endswith(('Fab', 'CrtYd')):
            continue
        for x, y in re.findall(r'\((?:start|end|xy|center) ([-\d.]+) ([-\d.]+)\)', it.group(2)):
            x, y = float(x), float(y)
            X = X0 + x * math.cos(th) + y * math.sin(th) - 100; Y = -(Y0 - x * math.sin(th) + y * math.cos(th) - 100)
            k = 'fab' if lm.group(1).endswith('Fab') else 'crt'
            b = box.setdefault(k, [1e9, -1e9, 1e9, -1e9])
            b[0] = min(b[0], X); b[1] = max(b[1], X); b[2] = min(b[2], Y); b[3] = max(b[3], Y)
    pads = len(re.findall(r'\(pad ', blk))
    print('%-10s %-55s %s at (%.3f, %.3f) rot %s pads %d crt %s' % (ref, m.group(1)[:55], lay, X0 - 100, -(Y0 - 100), at.group(3) or 0, pads,
                                                                   [round(v, 2) for v in box.get('crt', [])]))
