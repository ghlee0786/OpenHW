"""C-004 (V-004 R6): XKB DC-005-5A-2.0 barrel jack footprint derived from KiCad BarrelJack_Horizontal.
V-004 R6 values (XKB drawing Rev A1, LCSC C381116): pin1-pin2 5.90, pin3 3.0 from pin1 and 4.70 perpendicular,
slots 1.0 x 3.5. Pads enlarged so annular ring >= 0.35 around the 3.5 slot.
usage: python c004_libfix.py <openhw.pretty> <kicad footprints dir>"""
import re, sys
L, OFF = sys.argv[1], sys.argv[2]
t = open(f'{OFF}/Connector_BarrelJack.pretty/BarrelJack_Horizontal.kicad_mod', encoding='utf-8').read()
name = 'BarrelJack_XKB_DC-005-5A-2.0_Horizontal'
t = t.replace('(footprint "BarrelJack_Horizontal"', f'(footprint "{name}"', 1)
t = re.sub(r'(\(property "Value" ")[^"]*(")', lambda m: m.group(1) + name + m.group(2), t, count=1)
t = re.sub(r'\(descr "[^"]*"\)', '(descr "XKB DC-005-5A-2.0 DC jack 5.5x2.1, THT right angle. Pin spacing per XKB drawing Rev A1 as read by V-004 R6: 1-2 5.90, pin 3 at 3.0 / 4.70, slots 1.0x3.5. Derived from KiCad Connector_BarrelJack:BarrelJack_Horizontal (body outline kept, verify vs XKB drawing).")', t, count=1)
def pad(num, at, size, drill):
    global t
    m = re.search(r'\(pad "%s" thru_hole \w+\s*\(at [^)]*\)\s*\(size [^)]*\)\s*\(drill [^)]*\)' % num, t)
    if not m: raise SystemExit(f'pad {num}')
    b = m.group(0)
    b = re.sub(r'\(at [^)]*\)', f'(at {at[0]} {at[1]})', b); b = re.sub(r'\(size [^)]*\)', f'(size {size[0]} {size[1]})', b)
    b = re.sub(r'\(drill [^)]*\)', f'(drill oval {drill[0]} {drill[1]})', b)
    t = t[:m.start()] + b + t[m.end():]
pad('1', (0, 0), (3.5, 4.2), (1.0, 3.5))
pad('2', (-5.9, 0), (3.0, 4.2), (1.0, 3.5))
pad('3', (-3.0, 4.7), (4.2, 3.5), (3.5, 1.0))
open(f'{L}/{name}.kicad_mod', 'w', encoding='utf-8', newline='\n').write(t)
print('ok')
