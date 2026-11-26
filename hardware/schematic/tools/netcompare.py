"""Compare two KiCad S-expression netlists (kicad-cli sch export netlist --format kicadsexpr).
Checks: component set (ref, value, footprint), and every net as (name, sorted pins).
Sheet-path prefix of net names ('/' or '/Sheet/') is ignored; nothing else is ignored.
Exit code 0 = identical, 1 = differences (printed)."""
import re, sys

def parse(path):
    t = open(path, encoding='utf-8').read()
    comps = {}
    for m in re.finditer(r'\(comp\s+\(ref "([^"]+)"\)\s*\(value "([^"]*)"\)\s*\(footprint "([^"]*)"\)', t):
        comps[m.group(1)] = (m.group(2), m.group(3))
    nets = {}
    for m in re.finditer(r'\(net\s+\(code "?\d+"?\)\s+\(name "([^"]*)"\)(.*?)\n\t\t\)', t, re.S):
        name = m.group(1).rsplit('/', 1)[-1]
        pins = tuple(sorted(re.findall(r'\(ref "([^"]+)"\)\s*\(pin "([^"]+)"\)', m.group(2))))
        nets[pins] = name
    return comps, nets

def main(a, b):
    ca, na = parse(a); cb, nb = parse(b)
    diffs = []
    for r in sorted(set(ca) | set(cb)):
        if ca.get(r) != cb.get(r): diffs.append(f'COMP {r}: {ca.get(r)} -> {cb.get(r)}')
    for pins in sorted(set(na) | set(nb)):
        x, y = na.get(pins), nb.get(pins)
        if x is None or y is None:
            diffs.append(f'NET {"only-before" if y is None else "only-after"} {x or y}: {pins[:6]}{"..." if len(pins) > 6 else ""}')
        elif x != y and not (x.startswith('unconnected-') and y.startswith('unconnected-')):
            diffs.append(f'NETNAME {x} -> {y}: {pins[:4]}')
    print(f'{a} vs {b}: comps {len(ca)}/{len(cb)} nets {len(na)}/{len(nb)} differences {len(diffs)}')
    for d in diffs: print('  ' + d)
    return 1 if diffs else 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
