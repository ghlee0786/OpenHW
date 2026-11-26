"""Count overlapping text on a generated KiCad schematic (C-013).
Text = net labels, free text (block titles/notes) and visible symbol fields (Reference/Value).
Box = estimated text bounding box (char advance 0.8 x size for ASCII, 1.0 x size otherwise; height = size).
Two texts overlap when their boxes intersect by more than 0.05 mm in both axes.
usage: python overlaps.py <file.kicad_sch> [-v]   -> prints total, visible and stacked counts (and the pairs with -v)"""
import re, sys

def width(s, size):
    return sum((0.8 if ord(c) < 128 else 1.0) * size for c in s)

def box(x, y, ang, just, s, size):
    w, h = width(s, size), size
    ang = int(ang) % 360
    right = 'right' in just
    if ang in (0, 180):
        x0 = x - w if (right or ang == 180 and 'left' not in just) else x
        if ang == 180 and right: x0 = x - w
        return (x0, y - h, x0 + w, y)
    # vertical: reads upward (90) or the text is placed below the anchor (270, right-justified)
    return (x - h, y - w, x, y) if ang == 90 else (x - h, y, x, y + w)

def texts(t):
    out = []
    for m in re.finditer(r'\n\t\(label "((?:[^"\\]|\\.)*)"\n\t\t\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)(.*?)\(justify ([^)]*)\)', t, re.S):
        s, x, y, a, _, j = m.groups(); out.append(('label', s, box(float(x), float(y), a, j, s, 1.27)))
    for m in re.finditer(r'\n\t\(text "((?:[^"\\]|\\.)*)"\n.*?\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\).*?\(size ([\d.]+) [\d.]+\)', t, re.S):
        s, x, y, a, sz = m.groups(); out.append(('text', s, box(float(x), float(y), a, 'left bottom', s, float(sz))))
    for sm in re.finditer(r'\n\t\(symbol\n\t\t\(lib_id .*?\n\t\)(?=\n)', t, re.S):
        b = sm.group(0); ref = re.search(r'\(property "Reference" "([^"]+)"', b).group(1)
        for pm in re.finditer(r'\(property "(Reference|Value)" "((?:[^"\\]|\\.)*)"\n\t\t\t\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\n(\t\t\t\(hide yes\)\n)?', b):
            k, s, x, y, a, hide = pm.groups()
            if hide: continue
            # field text is centred vertically on its anchor (justify left)
            x0, y0 = float(x), float(y)
            out.append((f'{ref}.{k}', s, (x0, y0 - 0.635, x0 + width(s, 1.27), y0 + 0.635)))
    return out

def overlaps(items):
    res = []
    for i in range(len(items)):
        a = items[i][2]
        for j in range(i + 1, len(items)):
            b = items[j][2]
            if min(a[2], b[2]) - max(a[0], b[0]) > 0.05 and min(a[3], b[3]) - max(a[1], b[1]) > 0.05:
                res.append((items[i], items[j]))
    return res

if __name__ == '__main__':
    t = open(sys.argv[1], encoding='utf-8').read()
    r = overlaps(texts(t))
    # same label text drawn twice at the same spot (stacked pins of one net) renders as one label
    stacked = [(a, b) for a, b in r if a[0] == b[0] == 'label' and a[1] == b[1] and a[2] == b[2]]
    print(f'{len(r)} total, {len(r) - len(stacked)} visible (different text), {len(stacked)} stacked same-name labels')
    if '-v' in sys.argv:
        for a, b in r:
            print(f'  {a[0]} "{a[1][:40]}" {tuple(round(v, 2) for v in a[2])}  x  {b[0]} "{b[1][:40]}" {tuple(round(v, 2) for v in b[2])}')
