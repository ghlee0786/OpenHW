"""REN-002 02: kicad-cli 보드 렌더 (렌더용 사본 = pcb 보드 + 대체 3D 모델 연결, apply_models.py) → validation/runtime/vd001/render/pcb/
  <보드>_top / _bottom          : 정사영, 보드 전체 (2560×1440)
  <보드>_tilt                   : 원근·바닥 그림자, 기울임 (2560×1440)
  <보드>_<top|bottom>_zoom<n>   : 2배 크기로 그려 보드 영역을 2560×1440 조각으로 자름(배율 그대로) — 실크를 읽는 컷.
                                  부품 번호는 pcb 23fd8da 에서 실크에 없고 F/B.Fab 에만 있어, Fab 위치를 노란 글자로 겹쳐 적는다(주석 — 실크 아님).
보드 외곽 → 화면 좌표: 모델을 뺀 사본(<보드>_bare.kicad_pcb)을 같은 카메라·투명 배경으로 그려 알파로 외곽을 잡는다.
kicad-cli 10.0.8 은 요청보다 8~32 px 작게 저장한다 → 크게 요청한 뒤 가운데를 잘라 맞춘다.
사용: python -B mechanical/ren002/scripts/02_pcb_render.py [--src validation/runtime/vd001/ren002/rendersrc]"""
import argparse, math, os, re, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

LANE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
V = os.path.join(LANE, 'validation', 'runtime', 'vd001')
OUT = os.path.join(V, 'render', 'pcb')
KICAD = os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
W, H, PAD = 2560, 1440, 40
BG = (29, 32, 39)
EXT = {'carrier': (-20.0, 20.0, -34.0, 20.0), 'front': (-20.0, 20.0, -20.0, 20.0)}   # 보드 외곽 (기구 좌표, M-003 params)
FONT = ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf', 26)
FONT_S = ImageFont.truetype(r'C:\Windows\Fonts\malgun.ttf', 30)


def render(src, out, side, w, h, extra, bg='transparent'):
    cmd = [KICAD, 'pcb', 'render', '--quality', 'high', '--background', bg, '-w', str(w), '-h', str(h), '--side', side, '-o', out, src] + extra
    r = subprocess.run(cmd, capture_output=True, encoding='utf-8', errors='replace')
    if r.returncode:
        raise SystemExit('kicad-cli rc %d %s' % (r.returncode, r.stderr[-300:]))
    im = Image.open(out).convert('RGBA')
    return im


def flat(im):
    b = Image.new('RGBA', im.size, BG + (255,)); b.alpha_composite(im)
    return b.convert('RGB')


def crop_center(im, w, h):
    x0, y0 = (im.width - w) // 2, (im.height - h) // 2
    return im.crop((x0, y0, x0 + w, y0 + h))


def alpha_bbox(im):
    return im.getchannel('A').point(lambda a: 255 if a > 128 else 0).getbbox()


def refs(t, side):
    out = []
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"\s*\(layer "([FB])\.Cu"\)[\s\S]*?\n\t\t\(at ([-\d.]+) ([-\d.]+)', t):
        if m.group(2) != side:
            continue
        blk = t[m.start():t.find('\n\t(footprint', m.end())]
        ref = re.search(r'\(property "Reference" "([^"]*)"', blk).group(1)
        if re.match(r'(TP|H)\d', ref):
            continue
        out.append((ref, float(m.group(3)) - 100.0, -(float(m.group(4)) - 100.0)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=os.path.join(V, 'ren002', 'rendersrc'))
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.png'):
            os.remove(os.path.join(OUT, f))
    tmp = os.path.join(OUT, '_t.png')
    n = 0
    for b in ('carrier', 'front'):
        bd = os.path.join(a.src, 'hardware', 'schematic', b)
        src = os.path.join(bd, b + '.kicad_pcb')
        t = open(src, encoding='utf-8').read()
        bare = os.path.join(bd, b + '_bare.kicad_pcb')
        open(bare, 'w', encoding='utf-8', newline='\n').write(re.sub(r'\n\t\t\(model "[^"]*"[\s\S]*?\n\t\t\)', '', t))
        for side in ('top', 'bottom'):
            ext = ['--zoom', '0.95']
            flat(crop_center(render(src, tmp, side, W + PAD, H + PAD, ext), W, H)).save(os.path.join(OUT, '%s_%s.png' % (b, side))); n += 1
            big = render(src, tmp, side, 2 * W + PAD, 2 * H + PAD, ext)
            x0, y0, x1, y1 = alpha_bbox(render(bare, tmp, side, 2 * W + PAD, 2 * H + PAD, ext))
            big = flat(big)
            # 부품 번호 주석 (Fab 위치 → 화면)
            xa, xb, ya, yb = EXT[b]
            dr = ImageDraw.Draw(big)
            for ref, x, y in refs(t, 'F' if side == 'top' else 'B'):
                u = (x - xa) / (xb - xa) if side == 'top' else (xb - x) / (xb - xa)   # 아랫면은 좌우 반전
                px, py = x0 + u * (x1 - x0), y0 + (yb - y) / (yb - ya) * (y1 - y0)
                dr.text((px, py), ref, font=FONT, fill=(255, 214, 0), anchor='mm', stroke_width=3, stroke_fill=(0, 0, 0))
            nx, ny = math.ceil((x1 - x0) / W), math.ceil((y1 - y0) / H)
            cx0 = (x0 + x1) // 2 - nx * W // 2; cy0 = (y0 + y1) // 2 - ny * H // 2
            k = 0
            for j in range(ny):
                for i in range(nx):
                    k += 1
                    tile = big.crop((cx0 + i * W, cy0 + j * H, cx0 + (i + 1) * W, cy0 + (j + 1) * H))
                    ImageDraw.Draw(tile).text((24, 18), '%s %s 확대 %d/%d — 노란 글자 = 부품 번호 주석(F/B.Fab 위치, 실크 아님)' % (b, '윗면' if side == 'top' else '아랫면', k, nx * ny),
                                              font=FONT_S, fill=(235, 235, 235), stroke_width=3, stroke_fill=(0, 0, 0))
                    tile.save(os.path.join(OUT, '%s_%s_zoom%d.png' % (b, side, k))); n += 1
            print('PCB', b, side, 'board px', x1 - x0, y1 - y0, 'tiles', nx, 'x', ny)
        flat(crop_center(render(src, tmp, 'top', W + PAD, H + PAD, ['--floor', '--perspective', '--rotate', '-40,0,30', '--zoom', '0.8']), W, H)).save(
            os.path.join(OUT, '%s_tilt.png' % b)); n += 1
        os.remove(bare)
    os.remove(tmp)
    print('PCB images', n)
    return 0


if __name__ == '__main__':
    sys.exit(main())
