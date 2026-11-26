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

PAPERS = {'A1': (841, 594), 'A0': (1189, 841)}

class Sheet:
    """Single-sheet schematic laid out in functional blocks (frame + title + notes).
    Nets wholly inside one block (and not in `power`) are drawn as short orthogonal wires
    plus one name label; other nets use a local label on every pin."""
    def __init__(self, project, title, local_libs, paper='A1', power=()):
        self.project = project; self.title = title; self.local_libs = local_libs; self.paper = paper
        self.parts = []; self.blocks = []; self.cur = None; self.power = set(power)
        self.root = U()
    def block(self, key, title, notes=(), cols=4):
        self.blocks.append(dict(key=key, title=title, notes=list(notes), cols=cols)); self.cur = key
    def add(self, ref, lib_id, value, fp, nets, dnp=False, datasheet=None, fields=None, in_bom=True):
        pins = pins_of(lib_id, self.local_libs)
        nums = [p['num'] for p in pins]
        for k in nets:
            if k not in nums: raise SystemExit(f'{ref}: pin {k} not in {lib_id} {nums}')
        self.parts.append(dict(ref=ref, lib_id=lib_id, value=value, fp=fp, nets=nets, dnp=dnp, ds=datasheet,
                               fields=fields or {}, pins=pins, block=self.cur, in_bom=in_bom))

    # ---------------- layout
    def _layout(self):
        g = lambda v: round(v / 2.54) * 2.54
        boxes = []
        for b in self.blocks:
            parts = [p for p in self.parts if p['block'] == b['key']]
            x = 0.0; y = 0.0; rowh = 0.0; col = 0; maxw = 0.0
            for p in parts:
                bx0, by0, bx1, by1 = bbox(p['pins'])
                w = (bx1 - bx0) + 35.56; h = (by1 - by0) + 22.86
                if col >= b['cols']:
                    x = 0.0; y += rowh; rowh = 0.0; col = 0
                p['rel'] = (x - bx0 + 15.24, y + by1 + 11.43 + 7.62 * (1 + len(b['notes'])))
                x += w; rowh = max(rowh, h); col += 1; maxw = max(maxw, x)
            bw = max(maxw, 120.0) + 10.16; bh = y + rowh + 7.62 * (1 + len(b['notes'])) + 10.16
            boxes.append([b, parts, bw, bh])
        # shelf packing on the page
        for paper in ('A1', 'A0'):
            PW, PH = PAPERS[paper]
            x0, y0 = 25.4, 25.4; x, y, rowh = x0, y0, 0.0; ok = True
            for bx in boxes:
                if x + bx[2] > PW - 20:
                    x = x0; y += rowh + 7.62; rowh = 0.0
                bx.append((x, y)) if len(bx) == 4 else bx.__setitem__(4, (x, y))
                x += bx[2] + 7.62; rowh = max(rowh, bx[3])
            if y + rowh < PH - 45: break
        self.paper = paper
        for b, parts, bw, bh, (ox, oy) in boxes:
            b['frame'] = (g(ox), g(oy), g(ox + bw), g(oy + bh))
            for p in parts:
                p['at'] = (g(ox + p['rel'][0]), g(oy + p['rel'][1]))

    # ---------------- connectivity
    def build(self):
        netpins = {}
        for p in self.parts:
            for pin in p['pins']:
                n = p['nets'].get(pin['num'])
                if n: netpins.setdefault(n, []).append(pin['type'])
        flags = [n for n, ts in netpins.items() if 'power_in' in ts and 'power_out' not in ts]
        self.block('FLAGS', 'PWR_FLAG (ERC: 전원 입력 핀이 있는데 구동원이 없는 넷)', cols=6)
        for i, n in enumerate(sorted(flags)):
            self.add(f'#FLG{i+1:02d}', 'power:PWR_FLAG', 'PWR_FLAG', '', {'1': n})
        self.flags = sorted(flags)
        cnt = {}
        for p in self.parts:
            for pin in p['pins']:
                n = p['nets'].get(pin['num'])
                if n: cnt[n] = cnt.get(n, 0) + 1
        self.single = sorted(n for n, c in cnt.items() if c < 2)
        self._layout()
        pts = {}      # (x,y) -> set of nets ('' for NC/unconnected pin)
        netpts = {}   # net -> list of (pt, pin, part)
        ncs = []
        for p in self.parts:
            sx, sy = p['at']
            for pin in p['pins']:
                pt = (round(sx + pin['x'], 2), round(sy - pin['y'], 2))
                n = p['nets'].get(pin['num'])
                pts.setdefault(pt, set()).add(n or f'~{p["ref"]}.{pin["num"]}')
                if n: netpts.setdefault(n, []).append((pt, pin, p))
                elif pin['type'] != 'no_connect' and not p['ref'].startswith('#'): ncs.append(pt)
        segs = []     # (net, (x1,y1), (x2,y2))
        def on(pt, a, b):
            (x, y), (x1, y1), (x2, y2) = pt, a, b
            if x1 == x2 == x: return min(y1, y2) - 1e-6 <= y <= max(y1, y2) + 1e-6
            if y1 == y2 == y: return min(x1, x2) - 1e-6 <= x <= max(x1, x2) + 1e-6
            return False
        def clash(net, a, b):
            for pt, ns in pts.items():
                if on(pt, a, b) and (ns - {net}): return True
            for n2, c, d in segs:
                if n2 == net: continue
                if on(a, c, d) or on(b, c, d) or on(c, a, b) or on(d, a, b): return True
            return False
        labels = []; wired = []
        block_of = {}
        for n, lst in netpts.items():
            block_of[n] = {p['block'] for _, _, p in lst}
        for n in sorted(netpts):
            lst = netpts[n]
            route = []
            if n not in self.power and len(block_of[n]) == 1 and len(lst) >= 2:
                chain = sorted({pt for pt, _, _ in lst})
                okall = True; tmp = []
                for a, b in zip(chain, chain[1:]):
                    done = False
                    for c in ((b[0], a[1]), (a[0], b[1])):
                        path = [s for s in ((a, c), (c, b)) if s[0] != s[1]]
                        if all(not clash(n, s0, s1) for s0, s1 in path) and \
                           all(not clash(n, s0, s1) for s0, s1 in tmp if False):
                            tmp += path; segs.extend((n, s0, s1) for s0, s1 in path); done = True; break
                    if not done:
                        okall = False; break
                if okall:
                    route = tmp
                else:
                    segs[:] = [s for s in segs if s[0] != n]; route = []
            if route:
                wired.append(n)
                pt, pin, p = lst[0]
                labels.append(self._label(n, pt, pin))
                self.wires = getattr(self, 'wires', []) + route
            else:
                for pt, pin, p in lst:
                    labels.append(self._label(n, pt, pin))
        self.wired = wired
        if not hasattr(self, 'wires'): self.wires = []
        return labels, ncs

    def _label(self, n, pt, pin):
        ang = (pin['rot'] + 180) % 360
        just = {0: 'left bottom', 180: 'right bottom', 90: 'left bottom', 270: 'right bottom'}[int(ang)]
        return (n, pt[0], pt[1], ang, just)

    def write(self, path):
        labels, ncs = self.build()
        used = sorted(set(p['lib_id'] for p in self.parts))
        o = []
        o.append(f'(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n\t(uuid "{self.root}")\n\t(paper "{self.paper}")\n')
        o.append(f'\t(title_block\n\t\t(title "{self.title}")\n\t\t(date "2026-11-27")\n\t\t(rev "C-018")\n\t\t(company "OpenHW PoC")\n\t\t(comment 1 "Generated by tools/boards.py (C-002b block layout); contract hw-fw-contract.md")\n\t)\n')
        o.append('\t(lib_symbols\n')
        for lid in used:
            o.append('\t\t' + lib_block(lid, self.local_libs).replace('\n\t', '\n\t\t') + '\n')
        o.append('\t)\n')
        def text(t, x, y, size, bold=False):
            t = t.replace('"', '\\"')
            return f'\t(text "{t}"\n\t\t(exclude_from_sim no)\n\t\t(at {x:.2f} {y:.2f} 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(face "Malgun Gothic")\n\t\t\t\t(size {size} {size})\n' +('\t\t\t\t(thickness 0.4)\n\t\t\t\t(bold yes)\n' if bold else '') + f'\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{U()}")\n\t)\n'
        for b in self.blocks:
            x1, y1, x2, y2 = b['frame']
            o.append(f'\t(rectangle\n\t\t(start {x1:.2f} {y1:.2f})\n\t\t(end {x2:.2f} {y2:.2f})\n\t\t(stroke\n\t\t\t(width 0.3)\n\t\t\t(type dash)\n\t\t)\n\t\t(fill\n\t\t\t(type none)\n\t\t)\n\t\t(uuid "{U()}")\n\t)\n')
            o.append(text(b['title'], x1 + 2.54, y1 + 6.35, 2.5, True))
            for k, nline in enumerate(b['notes']):
                o.append(text(nline, x1 + 2.54, y1 + 6.35 + 6.35 * (k + 1), 1.6))
        for a, b2 in self.wires:
            o.append(f'\t(wire\n\t\t(pts\n\t\t\t(xy {a[0]:.2f} {a[1]:.2f}) (xy {b2[0]:.2f} {b2[1]:.2f})\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{U()}")\n\t)\n')
        for (n, px, py, ang, just) in labels:
            o.append(f'\t(label "{n}"\n\t\t(at {px:.2f} {py:.2f} {int(ang)})\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{U()}")\n\t)\n')
        for (px, py) in ncs:
            o.append(f'\t(no_connect\n\t\t(at {px:.2f} {py:.2f})\n\t\t(uuid "{U()}")\n\t)\n')
        for p in self.parts:
            sx, sy = p['at']
            bx0, by0, bx1, by1 = bbox(p['pins'])
            hide_ref = p['ref'].startswith('#')
            o.append(f'\t(symbol\n\t\t(lib_id "{p["lib_id"]}")\n\t\t(at {sx:.2f} {sy:.2f} 0)\n\t\t(unit 1)\n\t\t(exclude_from_sim no)\n\t\t(in_bom {"no" if hide_ref or not p.get("in_bom", True) else "yes"})\n\t\t(on_board {"no" if hide_ref else "yes"})\n\t\t(in_pos_files {"no" if hide_ref or not p.get("in_bom", True) else "yes"})\n\t\t(dnp {"yes" if p["dnp"] else "no"})\n\t\t(uuid "{U()}")\n')
            def prop(k, v, dx, dy, hide):
                v = v.replace('"', '\\"')
                return f'\t\t(property "{k}" "{v}"\n\t\t\t(at {sx+dx:.2f} {sy+dy:.2f} 0)\n' + ('\t\t\t(hide yes)\n' if hide else '') + '\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify left)\n\t\t\t)\n\t\t)\n'
            o.append(prop('Reference', p['ref'], bx1 + 1.27, -by1 - 5.08, hide_ref))  # C-013: one grid step higher, clears the top-pin label
            o.append(prop('Value', p['value'], bx1 + 1.27, -by1 - 2.54, hide_ref))
            o.append(prop('Footprint', p['fp'], 0, 0, True))
            o.append(prop('Datasheet', p['ds'] or '', 0, 0, True))
            for k, v in p['fields'].items():
                o.append(prop(k, v, 0, 0, True))
            for pin in p['pins']:
                o.append(f'\t\t(pin "{pin["num"]}"\n\t\t\t(uuid "{U()}")\n\t\t)\n')
            o.append(f'\t\t(instances\n\t\t\t(project "{self.project}"\n\t\t\t\t(path "/{self.root}"\n\t\t\t\t\t(reference "{p["ref"]}")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)\n')
        o.append('\t(sheet_instances\n\t\t(path "/"\n\t\t\t(page "1")\n\t\t)\n\t)\n\t(embedded_fonts no)\n)\n')
        open(path, 'w', encoding='utf-8', newline='\n').write(''.join(o))
        return dict(parts=len(self.parts), labels=len(labels), nc=len(ncs), wires=len(self.wires), wired_nets=len(self.wired),
                    flags=self.flags, single=self.single, paper=self.paper, blocks=len(self.blocks))

# ---------- helpers for netlists
def R(sh, ref, val, a, b, fp='Resistor_SMD:R_0402_1005Metric', dnp=False):
    sh.add(ref, 'Device:R', val, fp, {'1': a, '2': b}, dnp)
def C(sh, ref, val, a, b, fp='Capacitor_SMD:C_0402_1005Metric', dnp=False):
    sh.add(ref, 'Device:C', val, fp, {'1': a, '2': b}, dnp)
def TP(sh, ref, net):
    sh.add(ref, 'Connector:TestPoint', net, 'TestPoint:TestPoint_Pad_D1.0mm', {'1': net})
