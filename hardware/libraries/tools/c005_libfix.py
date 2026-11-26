"""C-005 library fixes (text-level, idempotent).
1 BarrelJack_XKB_DC-005-5A-2.0_Horizontal: body per XKB drawing A1 2025-04-22 (14.0 x 9.0, front -13.6, rear +0.4),
  courtyard covering body + pads, silk kept >= 0.2 from pads (V-004b R6, R-009 9)
2 silk clipping (silk >= 0.2 mm from any pad) for openhw DF30 and an openhw copy of KiCad L_Bourns_SRN6045TA
3 new Everlight_ALS-PT19_1.7x0.8mm (Everlight DLS-0000039 Rev.8: pads 0.8x0.8, pitch 1.5, body 1.7x0.8x0.6, pin1 collector)
usage: python c005_libfix.py <openhw.pretty> <kicad footprints dir>"""
import re, sys, uuid
L, OFF = sys.argv[1], sys.argv[2]
U = lambda: str(uuid.uuid4())
GAP = 0.2

def blocks(t, head):
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

def line(layer, a, b, w):
    return f'\t(fp_line\n\t\t(start {a[0]:.3f} {a[1]:.3f})\n\t\t(end {b[0]:.3f} {b[1]:.3f})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)\n'
def rect(layer, a, b, w):
    return f'\t(fp_rect\n\t\t(start {a[0]} {a[1]})\n\t\t(end {b[0]} {b[1]})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(fill no)\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)\n'
def circle(layer, c, r, w, fill='yes'):
    return f'\t(fp_circle\n\t\t(center {c[0]} {c[1]})\n\t\t(end {c[0] + r} {c[1]})\n\t\t(stroke\n\t\t\t(width {w})\n\t\t\t(type solid)\n\t\t)\n\t\t(fill {fill})\n\t\t(layer "{layer}")\n\t\t(uuid "{U()}")\n\t)\n'

def pads_bbox(t):
    out = []
    for s, e in blocks(t, 'pad '):
        b = t[s:e]
        if '"F.Cu"' not in b and '"*.Cu"' not in b: continue
        m = re.search(r'\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', b); z = re.search(r'\(size ([\d.]+) ([\d.]+)\)', b)
        x, y = float(m.group(1)), float(m.group(2)); rot = float(m.group(3) or 0)
        w, h = float(z.group(1)), float(z.group(2))
        if int(round(rot)) % 180 == 90: w, h = h, w
        out.append((x - w / 2, y - h / 2, x + w / 2, y + h / 2))
    return out

def clip_silk(t):
    """split axis-aligned F.SilkS fp_line/fp_rect so that every piece keeps GAP+width/2 from pads"""
    pads = pads_bbox(t); new = ''
    for head in ('fp_rect', 'fp_line'):
        for s, e in reversed(blocks(t, head)):
            b = t[s:e]
            if '"F.SilkS"' not in b and '"F.Silkscreen"' not in b: continue
            p1 = [float(v) for v in re.search(r'\(start ([-\d.]+) ([-\d.]+)\)', b).groups()]
            p2 = [float(v) for v in re.search(r'\(end ([-\d.]+) ([-\d.]+)\)', b).groups()]
            w = float(re.search(r'\(width ([\d.]+)\)', b).group(1))
            segs = [((p1[0], p1[1]), (p2[0], p1[1])), ((p2[0], p1[1]), (p2[0], p2[1])), ((p2[0], p2[1]), (p1[0], p2[1])), ((p1[0], p2[1]), (p1[0], p1[1]))] if head == 'fp_rect' else [(tuple(p1), tuple(p2))]
            ls = t.rfind('\n', 0, s) + 1
            t = t[:ls] + t[e:].lstrip(' \t').lstrip('\n')
            m = GAP + w / 2
            for a, c in segs:
                if a[0] == c[0]:   # vertical
                    x = a[0]; lo, hi = sorted((a[1], c[1])); keep = [(lo, hi)]
                    for (x0, y0, x1, y1) in pads:
                        if x0 - m < x < x1 + m:
                            keep = [k for iv in keep for k in ((iv[0], min(iv[1], y0 - m)), (max(iv[0], y1 + m), iv[1])) if k[1] - k[0] > 0.05]
                    new += ''.join(line('F.SilkS', (x, k0), (x, k1), w) for k0, k1 in keep)
                elif a[1] == c[1]:  # horizontal
                    y = a[1]; lo, hi = sorted((a[0], c[0])); keep = [(lo, hi)]
                    for (x0, y0, x1, y1) in pads:
                        if y0 - m < y < y1 + m:
                            keep = [k for iv in keep for k in ((iv[0], min(iv[1], x0 - m)), (max(iv[0], x1 + m), iv[1])) if k[1] - k[0] > 0.05]
                    new += ''.join(line('F.SilkS', (k0, y), (k1, y), w) for k0, k1 in keep)
                else:
                    new += line('F.SilkS', a, c, w)   # diagonal: kept (none in these footprints)
    i = t.find('\n\t(pad '); return t[:i + 1] + new + t[i + 1:]

def drop_layers(t, layers):
    for head in ('fp_line', 'fp_rect', 'fp_circle', 'fp_arc', 'fp_poly'):
        for s, e in reversed(blocks(t, head)):
            if any(f'(layer "{l}")' in t[s:e] for l in layers):
                ls = t.rfind('\n', 0, s) + 1; t = t[:ls] + t[e:].lstrip(' \t').lstrip('\n')
    return t

def add(t, txt):
    i = t.find('\n\t(pad '); return t[:i + 1] + txt + t[i + 1:]

# 1) DC jack
p = f'{L}/BarrelJack_XKB_DC-005-5A-2.0_Horizontal.kicad_mod'; t = open(p, encoding='utf-8').read()
t = drop_layers(t, ('F.SilkS', 'F.Silkscreen', 'F.CrtYd', 'F.Courtyard', 'F.Fab'))
x0, x1, y0, y1 = -13.6, 0.4, -4.5, 4.5
t = add(t, rect('F.Fab', (x0, y0), (x1, y1), 0.1)
          + rect('F.SilkS', (x0 - 0.11, y0 - 0.11), (x1 + 0.11, y1 + 0.11), 0.12)
          + rect('F.CrtYd', (-13.85, -4.75), (2.0, 6.7), 0.05))
t = clip_silk(t)
t = re.sub(r'\(descr "((?:[^"\\]|\\.)*)"\)', lambda m: '(descr "' + m.group(1).split(' Body ')[0] + ' Body per XKB X-DC-005-5A-2.0 Rev A1 2025-04-22: 14.0 x 9.0, front -13.6, rear +0.4 (R-009). 3D model is the KiCad generic 6.0-pitch jack (substitute).")', t, count=1)
open(p, 'w', encoding='utf-8', newline='\n').write(t)

# 2a) DF30 silk
p = f'{L}/Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm.kicad_mod'; t = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8', newline='\n').write(clip_silk(t))
# 2b) SRN6045 openhw copy
t = open(f'{OFF}/Inductor_SMD.pretty/L_Bourns_SRN6045TA.kicad_mod', encoding='utf-8').read()
t = clip_silk(t)
t = re.sub(r'\(descr "((?:[^"\\]|\\.)*)"\)', lambda m: '(descr "' + m.group(1) + ' | openhw copy: silk clipped to keep 0.2 mm from pads (C-005); land unchanged")', t, count=1)
open(f'{L}/L_Bourns_SRN6045TA.kicad_mod', 'w', encoding='utf-8', newline='\n').write(t)

# 3) ALS-PT19
name = 'Everlight_ALS-PT19_1.7x0.8mm'
pad = lambda n, x: f'\t(pad "{n}" smd rect\n\t\t(at {x} 0)\n\t\t(size 0.8 0.8)\n\t\t(layers "F.Cu" "F.Paste" "F.Mask")\n\t\t(uuid "{U()}")\n\t)\n'
prop = lambda k, v, y, hide: f'\t(property "{k}" "{v}"\n\t\t(at 0 {y} 0)\n\t\t(layer "{"F.SilkS" if k == "Reference" else "F.Fab"}")\n' + ('\t\t(hide yes)\n' if hide else '') + f'\t\t(uuid "{U()}")\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1 1)\n\t\t\t\t(thickness 0.15)\n\t\t\t)\n\t\t)\n\t)\n'
t = (f'(footprint "{name}"\n\t(version 20260206)\n\t(generator "openhw-c005")\n\t(layer "F.Cu")\n'
     f'\t(descr "Everlight ALS-PT19-315C/L177/TR8 ambient light phototransistor 1.7x0.8x0.6mm. Land 0.8x0.8 at pitch 1.5 per Everlight DLS-0000039 Rev.8 (R-009 9). Pad 1 = collector, pad 2 = emitter.")\n'
     f'\t(tags "ALS-PT19 phototransistor light sensor")\n'
     + prop('Reference', 'REF**', -1.5, False) + prop('Value', name, 1.5, False) + prop('Datasheet', 'https://en.everlight.com/wp-content/plugins/ItemRelationship/product_files/pdf/ALS-PT19-315C-L177-TR8_V8.pdf', 0, True)
     + '\t(attr smd)\n'
     + rect('F.Fab', (-0.85, -0.4), (0.85, 0.4), 0.1)
     + rect('F.CrtYd', (-1.4, -0.65), (1.4, 0.65), 0.05)
     + circle('F.SilkS', (-1.45, 0), 0.1, 0.12)
     + pad('1', -0.75) + pad('2', 0.75) + '\t(embedded_fonts no)\n)\n')
open(f'{L}/{name}.kicad_mod', 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
