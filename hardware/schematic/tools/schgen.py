"""KiCad 10 schematic generator: places library symbols, attaches a local label to every
connected pin end, no_connect flags on unused pins, PWR_FLAG on power nets without a driver."""
import re, uuid, math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import symlib as SL

KLIB = SL.S
U = lambda: str(uuid.uuid4())

def _balanced(txt, start):
    d = 0; j = start
    while True:
        c = txt[j]
        if c == '"':
            j += 1
            while txt[j] != '"':
                if txt[j] == chr(92): j += 1
                j += 1
        elif c == '(':
            d += 1
        elif c == ')':
            d -= 1
            if d == 0: return j + 1
        j += 1

def lib_block(lib_id, local_libs):
    lib, name = lib_id.split(':')
    path = local_libs.get(lib, f'{KLIB}/{lib}.kicad_sym')
    L = SL.lib(path)
    blk = L[name]
    m = re.search(r'\(extends "([^"]+)"\)', blk)
    if not m:
        out = blk
    else:
        base = L[m.group(1)]
        while re.search(r'\(extends "([^"]+)"\)', base):
            base = L[re.search(r'\(extends "([^"]+)"\)', base).group(1)]
        bname = re.search(r'\(symbol "([^"]+)"', base).group(1)
        # properties of derived override base
        out = base.replace(f'(symbol "{bname}"', f'(symbol "{name}"', 1)
        out = out.replace(f'(symbol "{bname}_', f'(symbol "{name}_')
        for pm in re.finditer(r'\(property "([^"]+)" "((?:[^"\\]|\\.)*)"', blk):
            k, v = pm.group(1), pm.group(2)
            out = re.sub(r'(\(property "%s" ")((?:[^"\\]|\\.)*)(")' % re.escape(k), lambda mm: mm.group(1) + v + mm.group(3), out, count=1)
    out = out.replace(f'(symbol "{name}"', f'(symbol "{lib_id}"', 1)
    return out

def pins_of(lib_id, local_libs):
    blk = lib_block(lib_id, local_libs)
    res = []
    for m in re.finditer(r'\(pin (\w+) (\w+)\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)\s*\(length ([-\d.]+)\)(.*?)\(name "([^"]*)".*?\(number "([^"]*)"', blk, re.S):
        res.append(dict(type=m.group(1), x=float(m.group(3)), y=float(m.group(4)), rot=float(m.group(5)), name=m.group(8), num=m.group(9)))
    return res

def bbox(pins):
    if not pins: return (-2.54, -2.54, 2.54, 2.54)
    xs = [p['x'] for p in pins]; ys = [p['y'] for p in pins]
    return (min(xs), min(ys), max(xs), max(ys))

class Sheet:
    def __init__(self, project, title, local_libs, paper='A1'):
        self.project = project; self.title = title; self.local_libs = local_libs; self.paper = paper
        self.parts = []   # dict(ref, lib_id, value, fp, nets{pinnum:net or None}, dnp, fields)
        self.root = U()
    def add(self, ref, lib_id, value, fp, nets, dnp=False, datasheet=None, fields=None):
        pins = pins_of(lib_id, self.local_libs)
        nums = [p['num'] for p in pins]
        for k in nets:
            if k not in nums: raise SystemExit(f'{ref}: pin {k} not in {lib_id} {nums}')
        self.parts.append(dict(ref=ref, lib_id=lib_id, value=value, fp=fp, nets=nets, dnp=dnp, ds=datasheet, fields=fields or {}, pins=pins))

    def build(self):
        # power flags: nets having power_in but no power_out
        netpins = {}
        for p in self.parts:
            for pin in p['pins']:
                n = p['nets'].get(pin['num'])
                if n: netpins.setdefault(n, []).append(pin['type'])
        flags = [n for n, ts in netpins.items() if 'power_in' in ts and 'power_out' not in ts]
        for i, n in enumerate(sorted(flags)):
            self.add(f'#FLG{i+1:02d}', 'power:PWR_FLAG', 'PWR_FLAG', '', {'1': n})
        self.flags = sorted(flags)
        # single-pin net check
        cnt = {}
        for p in self.parts:
            for pin in p['pins']:
                n = p['nets'].get(pin['num'])
                if n: cnt[n] = cnt.get(n, 0) + 1
        self.single = sorted(n for n, c in cnt.items() if c < 2)
        # layout: grid placement
        out_syms = []; labels = []; ncs = []
        x0, y0 = 30.48, 30.48; x, y = x0, y0; rowh = 0; maxw = {'A1': 800, 'A2': 560, 'A3': 390}[self.paper]
        for p in self.parts:
            bx0, by0, bx1, by1 = bbox(p['pins'])
            w = (bx1 - bx0) + 45.72; h = (by1 - by0) + 25.4
            if x + w > maxw:
                x = x0; y += rowh; rowh = 0
            sx = round((x - bx0 + 20.32) / 2.54) * 2.54; sy = round((y + by1 + 12.7) / 2.54) * 2.54
            p['at'] = (sx, sy)
            x += w; rowh = max(rowh, h)
            for pin in p['pins']:
                px, py = sx + pin['x'], sy - pin['y']
                n = p['nets'].get(pin['num'], None)
                if n:
                    ang = (pin['rot'] + 180) % 360
                    just = {0: 'left bottom', 180: 'right bottom', 90: 'left bottom', 270: 'right bottom'}[int(ang)]
                    labels.append((n, px, py, ang, just))
                elif pin['type'] != 'no_connect' and not p['ref'].startswith('#'):
                    ncs.append((px, py))
        self.height = y + rowh
        return labels, ncs

    def write(self, path):
        labels, ncs = self.build()
        used = sorted(set(p['lib_id'] for p in self.parts))
        o = []
        o.append(f'(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n\t(uuid "{self.root}")\n\t(paper "{self.paper}")\n')
        o.append(f'\t(title_block\n\t\t(title "{self.title}")\n\t\t(date "2026-11-26")\n\t\t(rev "C-002 draft")\n\t\t(company "OpenHW PoC")\n\t\t(comment 1 "Generated by C-002 schgen.py; contract hw-fw-contract.md v1.2")\n\t)\n')
        o.append('\t(lib_symbols\n')
        for lid in used:
            blk = lib_block(lid, self.local_libs)
            o.append('\t\t' + blk.replace('\n\t', '\n\t\t') + '\n')
        o.append('\t)\n')
        for (n, px, py, ang, just) in labels:
            o.append(f'\t(label "{n}"\n\t\t(at {px:.2f} {py:.2f} {int(ang)})\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{U()}")\n\t)\n')
        for (px, py) in ncs:
            o.append(f'\t(no_connect\n\t\t(at {px:.2f} {py:.2f})\n\t\t(uuid "{U()}")\n\t)\n')
        for p in self.parts:
            sx, sy = p['at']
            bx0, by0, bx1, by1 = bbox(p['pins'])
            hide_ref = p['ref'].startswith('#')
            o.append(f'\t(symbol\n\t\t(lib_id "{p["lib_id"]}")\n\t\t(at {sx:.2f} {sy:.2f} 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom {"no" if hide_ref else "yes"})\n\t\t(on_board {"no" if hide_ref else "yes"})\n\t\t(in_pos_files {"no" if hide_ref else "yes"})\n\t\t(dnp {"yes" if p["dnp"] else "no"})\n\t\t(uuid "{U()}")\n')
            def prop(k, v, dx, dy, hide):
                v = v.replace('"', '\\"')
                return f'\t\t(property "{k}" "{v}"\n\t\t\t(at {sx+dx:.2f} {sy+dy:.2f} 0)\n' + ('\t\t\t(hide yes)\n' if hide else '') + '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left)\n\t\t\t)\n\t\t)\n'
            o.append(prop('Reference', p['ref'], bx1 + 1.27, -by1 - 3.81, hide_ref))
            o.append(prop('Value', p['value'], bx1 + 1.27, -by1 - 1.27, hide_ref))
            o.append(prop('Footprint', p['fp'], 0, 0, True))
            o.append(prop('Datasheet', p['ds'] or '', 0, 0, True))
            for k, v in p['fields'].items():
                o.append(prop(k, v, 0, 0, True))
            for pin in p['pins']:
                o.append(f'\t\t(pin "{pin["num"]}"\n\t\t\t(uuid "{U()}")\n\t\t)\n')
            o.append(f'\t\t(instances\n\t\t\t(project "{self.project}"\n\t\t\t\t(path "/{self.root}"\n\t\t\t\t\t(reference "{p["ref"]}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
        o.append(f'\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
        open(path, 'w', encoding='utf-8', newline='\n').write(''.join(o))
        return dict(parts=len(self.parts), labels=len(labels), nc=len(ncs), flags=self.flags, single=self.single)

# ---------- helpers for netlists
def R(sh, ref, val, a, b, fp='Resistor_SMD:R_0402_1005Metric', dnp=False):
    sh.add(ref, 'Device:R', val, fp, {'1': a, '2': b}, dnp)
def C(sh, ref, val, a, b, fp='Capacitor_SMD:C_0402_1005Metric', dnp=False):
    sh.add(ref, 'Device:C', val, fp, {'1': a, '2': b}, dnp)
def TP(sh, ref, net):
    sh.add(ref, 'Connector:TestPoint', net, 'TestPoint:TestPoint_Pad_D1.0mm', {'1': net})
