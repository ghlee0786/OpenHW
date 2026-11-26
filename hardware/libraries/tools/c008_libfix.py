"""C-008 library fixes (pcb P-003 9355bd1 request, text-level, idempotent).
1 BarrelJack_XKB_DC-005-5A-2.0_Horizontal: the board edge sits at the body front (x = -13.6).
  Drop the front silk line and start the side silk lines at x = -13.3 (edge + 0.2 + half of the 0.12 stroke).
2 M12_Holder_20mm_CLA216-ICR: F.CrtYd x = +-12.45 (holder ears +-12.2 per R-007, 24.4 overall, + 0.25); y kept +-9.5.
3 M12_Holder_20mm_CLA216-ICR: sensor pedestal 13.2 x 13.2 (M-001d K11, height 0.75) as an F.Fab outline plus a
  footprint keepout rule area "SENSOR_PEDESTAL" (footprints not allowed; tracks, vias, pads and copper pour allowed).
  The pedestal is a bonded part, so it gets no copper (O-39 default; alternative: copper reference plane).
usage: python c008_libfix.py <openhw.pretty>"""
import re, sys, uuid
L = sys.argv[1]
U = lambda: str(uuid.uuid4())
EDGE_SILK_X = -13.3
P = 6.6  # pedestal half size

def rw(name, fn):
    p = f'{L}/{name}.kicad_mod'; t = open(p, encoding='utf-8').read(); n = fn(t)
    open(p, 'w', encoding='utf-8', newline='\n').write(n)

def jack(t):
    def fix(m):
        b = m.group(0)
        if '"F.SilkS"' not in b: return b
        (x1, y1), (x2, y2) = [tuple(map(float, re.search(rf'\({k} ([-\d.]+) ([-\d.]+)\)', b).groups())) for k in ('start', 'end')]
        if x1 == x2 and x1 < EDGE_SILK_X: return None          # front line on the board edge
        if y1 == y2 and min(x1, x2) < EDGE_SILK_X:
            b = b.replace(f'(start {x1:.3f} ', f'(start {max(x1, EDGE_SILK_X):.3f} ').replace(f'(end {x2:.3f} ', f'(end {max(x2, EDGE_SILK_X):.3f} ')
        return b
    out = []; pos = 0
    for m in re.finditer(r'\t\(fp_line\n.*?\n\t\)\n', t, re.S):
        out.append(t[pos:m.start()]); r = fix(m); out.append(r or ''); pos = m.end()
    out.append(t[pos:]); t = ''.join(out)
    if 'board edge at body front' not in t:
        t = re.sub(r'\(descr "((?:[^"\\]|\\.)*)"\)', lambda m: '(descr "' + m.group(1) + ' Silk keeps 0.2 inside a board edge at body front x=-13.6 (C-008).")', t, count=1)
    return t

def holder(t):
    t = re.sub(r'(\(fp_rect\s*\(start )-13\.5 (-9\.5\)\s*\(end )13\.5 (9\.5\)(?:(?!\(fp_).)*?\(layer "F\.CrtYd"\))', r'\g<1>-12.45 \g<2>12.45 \3', t, count=1, flags=re.S)
    assert '(start -12.45 -9.5)' in t, 'courtyard not updated'
    if 'SENSOR_PEDESTAL' not in t:
        fab = (f'\t(fp_rect\n\t\t(start {-P} {-P})\n\t\t(end {P} {P})\n\t\t(stroke\n\t\t\t(width 0.1)\n\t\t\t(type dash)\n\t\t)\n'
               f'\t\t(fill no)\n\t\t(layer "F.Fab")\n\t\t(uuid "{U()}")\n\t)\n')
        zone = (f'\t(zone\n\t\t(layers "F.Cu")\n\t\t(uuid "{U()}")\n\t\t(name "SENSOR_PEDESTAL")\n\t\t(hatch edge 0.5)\n'
                '\t\t(connect_pads\n\t\t\t(clearance 0)\n\t\t)\n\t\t(min_thickness 0.25)\n'
                '\t\t(keepout\n\t\t\t(tracks allowed)\n\t\t\t(vias allowed)\n\t\t\t(pads allowed)\n\t\t\t(copperpour allowed)\n\t\t\t(footprints not_allowed)\n\t\t)\n'
                '\t\t(placement\n\t\t\t(enabled no)\n\t\t\t(sheetname "")\n\t\t)\n'
                '\t\t(fill\n\t\t\t(thermal_gap 0.5)\n\t\t\t(thermal_bridge_width 0.5)\n\t\t\t(island_removal_mode 0)\n\t\t)\n'
                f'\t\t(polygon\n\t\t\t(pts\n\t\t\t\t(xy {-P} {-P}) (xy {P} {-P}) (xy {P} {P}) (xy {-P} {P})\n\t\t\t)\n\t\t)\n\t)\n')
        i = t.find('\n\t(pad '); t = t[:i + 1] + fab + t[i + 1:]
        i = t.find('\t(embedded_fonts'); i = i if i >= 0 else t.rfind(')')
        t = t[:i] + zone + t[i:]
        t = re.sub(r'\(descr "((?:[^"\\]|\\.)*)"\)', lambda m: '(descr "' + m.group(1) + ' C-008: courtyard x +-12.45 (ears +-12.2 + 0.25, R-007); sensor pedestal 13.2 sq (M-001d K11, h 0.75, bonded, no copper - O-39) as F.Fab + footprint keepout SENSOR_PEDESTAL.")', t, count=1)
    return t

rw('BarrelJack_XKB_DC-005-5A-2.0_Horizontal', jack)
rw('M12_Holder_20mm_CLA216-ICR', holder)
print('ok')
