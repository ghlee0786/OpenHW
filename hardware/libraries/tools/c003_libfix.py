"""C-003 library fixes (V-003), text-level S-expression edits (idempotent).
1 BTB A/B: courtyard 18.3x6.4 around pads+locating holes, silk off copper, REF**
2 AL8860: Diodes suggested land (DS39014 Rev 8-2 p.17) derived from KiCad MSOP-8-1EP footprint
3 DRV8837: copy of official footprint with 3D path to installed WSON-8 2x2 STEP
4 M12 holder: CLA216-ICR/Commonlands properties, NPTH 1.8 at +-10.0
usage: python c003_libfix.py <openhw.pretty> <kicad footprints dir>"""
import re, sys, uuid
L, OFF = sys.argv[1], sys.argv[2]
U = lambda: str(uuid.uuid4())

def blocks(t, head):
    """yield (start, end) of top-level-in-footprint blocks beginning with '(head'"""
    out = []; i = 0
    while True:
        i = t.find('(' + head, i)
        if i < 0: return out
        d = 0; j = i
        while True:
            c = t[j]
            if c == '"':
                j += 1
                while t[j] != '"':
                    if t[j] == chr(92): j += 1
                    j += 1
            elif c == '(': d += 1
            elif c == ')':
                d -= 1
                if d == 0: break
            j += 1
        out.append((i, j + 1)); i = j + 1

def drop(t, head, pred):
    for s, e in reversed(blocks(t, head)):
        if pred(t[s:e]):
            ls = t.rfind('\n', 0, s) + 1
            t = t[:ls] + t[e:].lstrip(' \t').lstrip('\n') if t[ls:s].strip() == '' else t[:s] + t[e:]
    return t

def add_before_pads(t, txt):
    i = t.find('\n\t(pad ')
    return t[:i + 1] + txt + t[i + 1:]

def shape(kind, layer, w, *pts, fill='no'):
    if kind == 'rect':
        (x1, y1), (x2, y2) = pts
        return f'\t(fp_rect\n\t\t(start {x1} {y1})\n\t\t(end {x2} {y2})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)\n'
    if kind == 'line':
        (x1, y1), (x2, y2) = pts
        return f'\t(fp_line\n\t\t(start {x1} {y1})\n\t\t(end {x2} {y2})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)\n'
    if kind == 'circle':
        (cx, cy), r = pts
        return f'\t(fp_circle\n\t\t(center {cx} {cy})\n\t\t(end {cx + r} {cy})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(fill {fill})\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)\n'

def setprop(t, k, v):
    v = v.replace('"', '\\"')
    n, c = re.subn(r'(\(property "%s" ")((?:[^"\\]|\\.)*)(")' % re.escape(k), lambda m: m.group(1) + v + m.group(3), t, count=1)
    if not c: raise SystemExit(f'property {k} missing')
    return n

def setdescr(t, v):
    v = v.replace('"', '\\"')
    return re.sub(r'\(descr "((?:[^"\\]|\\.)*)"\)', lambda m: f'(descr "{v}")', t, count=1)

on_layer = lambda *ls: (lambda b: any(f'(layer "{l}")' in b for l in ls))

# 1) BTB
for n in ('BTB_ST-BTB-058060-A_2x30_P0.5mm', 'BTB_ST-BTB-058060-B_2x30_P0.5mm'):
    p = f'{L}/{n}.kicad_mod'; t = open(p, encoding='utf-8').read()
    for h in ('fp_line', 'fp_rect', 'fp_circle', 'fp_arc', 'fp_poly'):
        t = drop(t, h, on_layer('F.SilkS', 'F.Silkscreen', 'F.CrtYd', 'F.Courtyard'))
    t = setprop(t, 'Reference', 'REF**')
    t = add_before_pads(t, shape('rect', 'F.CrtYd', 0.05, (-9.15, -3.2), (9.15, 3.2))
                        + shape('line', 'F.SilkS', 0.12, (-8.9, -0.9), (-8.9, 0.9))
                        + shape('line', 'F.SilkS', 0.12, (8.9, -0.9), (8.9, 0.9))
                        + shape('circle', 'F.SilkS', 0.3, (-8.1, -2.6), 0.15, fill='yes'))
    open(p, 'w', encoding='utf-8', newline='\n').write(t)

# 2) AL8860 Diodes suggested land
t = open(f'{OFF}/Package_SO.pretty/MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm.kicad_mod', encoding='utf-8').read()
name = 'Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860'
t = t.replace('(footprint "MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm"', f'(footprint "{name}"', 1)
t = setprop(t, 'Value', name)
t = setdescr(t, 'Diodes AL8860MP MSOP-8EP with Diodes Suggested Pad Layout (DS39014 Rev 8-2 p.17: C 0.65, X 0.45, Y 1.35, X1 2.0, Y1 1.7, Y2 5.3). Derived from KiCad library Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm (pads/EP/paste changed). EP paste 4 tiles ~66%.')
t = drop(t, 'pad ""', lambda b: True)                      # old EP paste tiles
def fix_pad(m):
    b = m.group(0); num = re.match(r'\(pad "(\d+)"', b).group(1)
    if num == '9':
        return re.sub(r'\(size [\d.]+ [\d.]+\)', '(size 1.7 2)', b, count=1)
    x = float(re.search(r'\(at ([-\d.]+) ', b).group(1))
    b = re.sub(r'\(at [-\d.]+ ', f'(at {1.975 if x > 0 else -1.975} ', b, count=1)
    return re.sub(r'\(size [\d.]+ [\d.]+\)', '(size 1.35 0.45)', b, count=1)
segs = blocks(t, 'pad "')
for s, e in reversed(segs):
    t = t[:s] + fix_pad(re.match(r'[\s\S]*', t[s:e])) + t[e:]
tiles = ''.join(f'\t(pad "" smd roundrect\n\t\t(at {x} {y})\n\t\t(size 0.68 0.82)\n\t\t(layers "F.Paste")\n\t\t(roundrect_rratio 0.25)\n\t\t(uuid "{U()}")\n\t)\n'
                for x in (-0.425, 0.425) for y in (-0.5, 0.5))
i = t.find('\n\t(pad '); t = t[:i + 1] + tiles + t[i + 1:]
open(f'{L}/{name}.kicad_mod', 'w', encoding='utf-8', newline='\n').write(t)

# 3) DRV8837 3D path
src = 'Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm'
t = open(f'{OFF}/Package_SON.pretty/{src}.kicad_mod', encoding='utf-8').read()
t = re.sub(r'\(model "[^"]*"', '(model "${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.step"', t, count=1)
t = re.sub(r'\(descr "((?:[^"\\]|\\.)*)"\)', lambda m: '(descr "' + m.group(1) + ' | openhw copy: land unchanged; 3D set to installed WSON-8-1EP_2x2mm STEP (official Texas_DSG0008A STEP missing in KiCad 10.0.8, V-003 1)")', t, count=1)
open(f'{L}/{src}.kicad_mod', 'w', encoding='utf-8', newline='\n').write(t)

# 4) M12 holder
p = f'{L}/M12_Holder_20mm_CLA216-ICR.kicad_mod'; t = open(p, encoding='utf-8').read()
t = setprop(t, 'MPN', 'CLA216-ICR'); t = setprop(t, 'Manufacturer', 'Commonlands')
t = setprop(t, 'Datasheet', 'https://commonlands.com/products/ir-cut-off-filter-switcher-m12-cla216')
t = setprop(t, 'Description', 'Commonlands CLA216-ICR M12 holder with IR-cut switcher; mounting holes 20.0 apart (R-007, holder hole ref dia 1.7); PCB NPTH 1.8 = ISO 273 medium clearance for M1.6')
t = setdescr(t, 'Commonlands CLA216-ICR M12 holder: 2x NPTH 1.8 at 20.0 spacing (R-007: spacing 20.0, hole ref 1.7; screw M1.6, ISO 273 medium clearance 1.8). Derived from Antmicro ov9281-camera-board antmicro-footprints:Camera_Lens_20mm (ea69666, Apache-2.0); artwork removed; Arducam properties replaced (V-003 8).')
for s, e in reversed(blocks(t, 'pad ""')):
    b = t[s:e]
    x = float(re.search(r'\(at ([-\d.]+) ', b).group(1))
    b = re.sub(r'\(at [-\d.]+ [-\d.]+', f'(at {10.0 if x > 0 else -10.0} 0', b, count=1)
    b = re.sub(r'\(size [\d.]+ [\d.]+\)', '(size 1.8 1.8)', b, count=1)
    b = re.sub(r'\(drill [\d.]+\)', '(drill 1.8)', b, count=1)
    t = t[:s] + b + t[e:]
open(p, 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
