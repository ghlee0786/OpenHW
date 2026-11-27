"""KiCad .kicad_pcb 에서 BTB 풋프린트(1·2·59·60 패드 절대 좌표), 장착 구멍, 외곽 bbox 를 뽑는다. 좌표는 KiCad 원값(mm, y 아래).
사용: python -I -B btbscan.py <file.kicad_pcb> [...]"""
import math, re, sys

sys.stdout.reconfigure(encoding='utf-8')


def blocks(t, key):
    for m in re.finditer(r'\(' + key + r'[\s"]', t):
        s = m.start(); dpt = 0; i = s
        while True:
            c = t[i]
            if c == '(':
                dpt += 1
            elif c == ')':
                dpt -= 1
                if dpt == 0:
                    break
            i += 1
        yield t[s:i + 1]


for path in sys.argv[1:]:
    t = open(path, encoding='utf-8', errors='replace').read()
    print('=====', path.split('/')[-1].split('\\')[-1])
    xs, ys = [], []
    for m in re.finditer(r'\(gr_(?:line|rect|arc)\s*\(start ([-\d.]+) ([-\d.]+)\)(?:\s*\(mid [-\d.]+ [-\d.]+\))?\s*\(end ([-\d.]+) ([-\d.]+)\).*?\(layer "Edge.Cuts"\)', t, re.S):
        xs += [float(m.group(1)), float(m.group(3))]; ys += [float(m.group(2)), float(m.group(4))]
    for m in re.finditer(r'\(gr_circle\s*\(center ([-\d.]+) ([-\d.]+)\)\s*\(end ([-\d.]+) ([-\d.]+)\).*?\(layer "Edge.Cuts"\)', t, re.S):
        cx, cy, ex, ey = map(float, m.groups()); r = math.hypot(ex - cx, ey - cy)
        xs += [cx - r, cx + r]; ys += [cy - r, cy + r]
    if xs:
        print('EDGE bbox x %.3f..%.3f y %.3f..%.3f  centre (%.3f, %.3f)' % (min(xs), max(xs), min(ys), max(ys), (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2))
    for blk in blocks(t, 'footprint'):
        name = blk.split('"')[1]
        refm = re.search(r'\(property "Reference" "([^"]+)"', blk) or re.search(r'\(fp_text reference "([^"]+)"', blk)
        ref = refm.group(1) if refm else '?'
        at = re.search(r'\n\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk)
        X0, Y0 = float(at.group(1)), float(at.group(2)); rot = float(at.group(3) or 0); th = math.radians(rot)
        layer = re.search(r'\(layer "([^"]+)"\)', blk).group(1)
        is_btb = 'BTB' in name.upper() or 'ST-BTB' in blk or 'HC-PBB' in blk
        is_hole = 'hole' in name.lower() or re.search(r'\(pad "[^"]*" np_thru_hole', blk) and len(re.findall(r'\(pad ', blk)) <= 2
        if not (is_btb or is_hole):
            continue

        def tr(x, y):
            return (X0 + x * math.cos(th) + y * math.sin(th), Y0 - x * math.sin(th) + y * math.cos(th))
        pads = {}
        for p in re.finditer(r'\(pad "([^"]*)" (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+)[^)]*\)\s*\(size ([-\d.]+) ([-\d.]+)\)(?:\s*\(drill ([-\d.]+))?', blk):
            pads.setdefault(p.group(1), []).append((tr(float(p.group(4)), float(p.group(5))), p.group(2), float(p.group(6)), float(p.group(7)), p.group(8)))
        mpn = re.search(r'\(property "(?:MPN|Manufacturer Part|Value)" "([^"]*)"', blk)
        if is_btb:
            sel = {k: [round(c, 3) for c in pads[k][0][0]] for k in ('1', '2', '59', '60') if k in pads}
            print('BTB %s %s layer %s at (%.3f, %.3f) rot %g value %s pads %s n_pads %d' % (ref, name, layer, X0, Y0, rot, mpn.group(1) if mpn else '?', sel, len(pads)))
        else:
            dr = [pp for v in pads.values() for pp in v]
            print('HOLE %s %s at (%.3f, %.3f) drill %s' % (ref, name, X0, Y0, dr[0][4] if dr else '?'))
