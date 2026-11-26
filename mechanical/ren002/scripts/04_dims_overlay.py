"""REN-002 04: 외형 치수선 겹치기 — render/stills/ren002_dims_raw.png + ren002_dims.json (scene.py 가 외함·덮개·방열판 외형 상자 모서리를 화면 좌표로 투영)
→ render/stills/ren002_dims.png. 값은 Fusion STL 외형(제품 좌표 mm) 그대로, 소수 첫째 자리."""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

LANE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
S = os.path.join(LANE, 'validation', 'runtime', 'vd001', 'render', 'stills')
F = ImageFont.truetype(r'C:\Windows\Fonts\malgunbd.ttf', 46)
FS = ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf', 34)
INK, EXT = (20, 120, 230), (20, 120, 230, 150)
NAME = {'X': '폭 X (방열판 포함)', 'Y': '높이 Y', 'Z': '깊이 Z (덮개 앞면 ~ 뒷벽)'}


def arrow(dr, a, b, w=5):
    dr.line([tuple(a), tuple(b)], fill=INK, width=w)
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    for p, s in ((a, 1), (b, -1)):
        tip = [(p[0], p[1]),
               (p[0] + s * 30 * math.cos(ang) - 11 * math.sin(ang), p[1] + s * 30 * math.sin(ang) + 11 * math.cos(ang)),
               (p[0] + s * 30 * math.cos(ang) + 11 * math.sin(ang), p[1] + s * 30 * math.sin(ang) - 11 * math.cos(ang))]
        dr.polygon(tip, fill=INK)


def main():
    d = json.load(open(os.path.join(S, 'ren002_dims.json')))
    im = Image.open(os.path.join(S, 'ren002_dims_raw.png')).convert('RGBA')
    ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
    for key in ('X', 'Y', 'Z'):
        v = d[key]
        a, b = v['a'], v['b']
        for e, t in zip(v['ea'], (a, b)):                       # 보조선 (모서리 → 치수선)
            dr.line([tuple(e), tuple(t)], fill=EXT, width=3)
        arrow(dr, a, b)
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        nx, ny = -(b[1] - a[1]), b[0] - a[0]; L = math.hypot(nx, ny) or 1
        off = 58 if key != 'Y' else -70
        tx, ty = mx + nx / L * off, my + ny / L * off
        txt = '%.1f mm' % v['mm']
        dr.text((tx, ty), txt, font=F, fill=INK, anchor='mm', stroke_width=6, stroke_fill=(255, 255, 255))
        dr.text((tx, ty + 44), NAME[key], font=FS, fill=(40, 40, 40), anchor='mm', stroke_width=5, stroke_fill=(255, 255, 255))
    out = Image.alpha_composite(im, ov).convert('RGB')
    ImageDraw.Draw(out).text((40, 30), '외형 치수 (외함 HOUSING · 앞 덮개 · SK 444 방열판, Fusion 외형 기준, 단위 mm)', font=FS, fill=(30, 30, 30))
    out.save(os.path.join(S, 'ren002_dims.png'))
    print('DIMS', {k: round(d[k]['mm'], 2) for k in 'XYZ'})
    return 0


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.exit(main())
