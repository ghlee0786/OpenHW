"""Render before/after schematic SVGs to PNG (full page + crops in schematic mm) with PyMuPDF."""
import fitz, sys, os
src, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
# crops (board, name, x0, y0, x1, y1) in schematic mm
CROPS = [('carrier', 'J2_12V_IN_RAW', 165, 40, 215, 75), ('carrier', 'D3_PWR_LED', 495, 105, 540, 135),
         ('carrier', 'J1_part_number', 40, 45, 110, 75), ('carrier', 'J3_USB_VBUS', 765, 45, 805, 75),
         ('front', 'J1_part_number', 40, 45, 110, 75), ('front', 'IR_A_VSMA', 380, 270, 450, 300)]
for state in ('before', 'after'):
    for b in ('carrier', 'front'):
        p = os.path.join(src, state, f'{b}.svg'); doc = fitz.open(p); pg = doc[0]
        import re
        wmm = float(re.search(r'width="([\d.]+)mm"', open(p, encoding='utf-8').read(2000)).group(1))
        sx = pg.rect.width / wmm  # page points per mm
        pg.get_pixmap(matrix=fitz.Matrix(0.5, 0.5)).save(os.path.join(out, f'{b}-{state}-page.png'))
        for bb, name, x0, y0, x1, y1 in CROPS:
            if bb != b: continue
            clip = fitz.Rect(x0 * sx, y0 * sx, x1 * sx, y1 * sx)
            pg.get_pixmap(matrix=fitz.Matrix(6, 6), clip=clip).save(os.path.join(out, f'{b}-{name}-{state}.png'))
print(sorted(os.listdir(out)))
