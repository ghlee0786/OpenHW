"""README 갤러리 그림 — PCB 층(pcb/) · 회로도 첫 장(sch/) · 케이스 1차 초안(mech/) (kicad-cli + PyMuPDF + Pillow, CAD·렌더러 없음).
  python -I -B docs/readme/gallery/make_gallery.py
- PCB 층: kicad-cli pcb export svg (전면 보드, 층마다 + 외곽선, 보드 영역만) → PyMuPDF 로 PNG → 어두운 배경을 칠함 (밝은·어두운 README 테마 모두에서 보이게)
- 회로도: kicad-cli sch export svg (전면·캐리어 첫 장 = 최상위 시트) → 원본 SVG 복사 + 미리보기 PNG
- 케이스 1차 초안: 저장소의 원본 PNG 를 폭을 줄인 사본 (원본은 그대로, gallery.json 에 원본 경로)
기준: PCB 층 PNG 폭 ≤ 900 · ≤ 400 KB, 그 밖 PNG ≤ 600 KB. 결과 gallery.json, 종료 코드 = 기준 불합격 수.
경로는 모두 저장소 기준 (로컬 경로 없음). KiCad 10 kicad-cli 는 환경 변수 KICAD_CLI 또는 PATH 또는 기본 설치 위치."""
import glob, hashlib, io, json, os, shutil, subprocess, sys, tempfile

import fitz
from PIL import Image, ImageChops

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
KICAD = os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
BG = (16, 20, 28)                     # 어두운 남색 바탕 (KiCad 기본 테마 층 색이 잘 보임)
LAYERS = [('fcu', 'F.Cu'), ('in1', 'In1.Cu'), ('in2', 'In2.Cu'), ('bcu', 'B.Cu'), ('silk', 'F.Silkscreen')]   # → pcb/front-<이름>.png
CASE = [('case-front-iso', 'mechanical/m003/render/m003_front_iso.png'), ('case-exploded', 'mechanical/m003/render/m003_exploded.png'),
        ('case-section', 'mechanical/m003/render/m003_section_x0.png')]   # → mech/<이름>.png (케이스 1차 초안)
PCB_W, PCB_MAX, PNG_MAX, COPY_W = 900, 400 * 1024, 600 * 1024, 900


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        print(' '.join(cmd)); print((r.stdout + r.stderr)[-1500:])
        raise SystemExit(r.returncode)


def rel(p):
    return os.path.relpath(p, ROOT).replace('\\', '/')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def svg_to_image(svg, width):
    doc = fitz.open(svg)
    page = doc[0]
    z = width / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=True)
    return Image.open(io.BytesIO(pix.tobytes('png'))).convert('RGBA')


def save_png(im, path, limit):
    """팔레트로 줄여 저장 — 한도를 넘으면 색 수를 줄임."""
    for colors in (256, 128, 64):
        im.convert('RGB').quantize(colors=colors, method=Image.Quantize.MEDIANCUT).save(path, optimize=True)
        if os.path.getsize(path) <= limit:
            break
    return os.path.getsize(path)


def main():
    rec, fails = {}, []
    for d in ('pcb', 'sch', 'mech'):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='gallery_')
    pcb = os.path.join(ROOT, 'hardware', 'schematic', 'front', 'front.kicad_pcb')
    # ④ PCB 층
    for name, layer in LAYERS:
        svg = os.path.join(tmp, name + '.svg')
        run([KICAD, 'pcb', 'export', 'svg', '--mode-single', '-o', svg, '-l', layer, '--cl', 'Edge.Cuts', '--page-size-mode', '2',
             '--exclude-drawing-sheet', '--drill-shape-opt', '2', pcb])
        im = svg_to_image(svg, PCB_W - 40)
        out = Image.new('RGBA', (im.width + 40, im.height + 40), BG + (255,))
        out.alpha_composite(im, (20, 20))
        p = os.path.join(HERE, 'pcb', 'front-%s.png' % name)
        n = save_png(out, p, PCB_MAX)
        rec[rel(p)[len('docs/readme/gallery/'):]] = {'bytes': n, 'size': list(out.size), 'source': rel(pcb) + ' · ' + layer + ' + Edge.Cuts', 'sha256': sha(p)}
        if n > PCB_MAX or out.width > PCB_W:
            fails.append(rel(p))
    # ⑤ 회로도 첫 장 (최상위 시트)
    for b in ('front', 'carrier'):
        d = os.path.join(tmp, 'sch_' + b)
        sch = os.path.join(ROOT, 'hardware', 'schematic', b, b + '.kicad_sch')
        run([KICAD, 'sch', 'export', 'svg', '-o', d, '--exclude-drawing-sheet', sch])
        first = os.path.join(d, b + '.svg')
        if not os.path.exists(first):
            first = sorted(glob.glob(os.path.join(d, '*.svg')))[0]
        dst = os.path.join(HERE, 'sch', '%s-sch.svg' % b)
        shutil.copy2(first, dst)
        im = svg_to_image(first, 4000)
        out = Image.new('RGBA', im.size, (255, 255, 255, 255))
        out.alpha_composite(im)
        out = out.convert('RGB')
        bg = max(out.getcolors(1 << 24), key=lambda c: c[0])[1]   # 도면 바탕색(가장 많은 색) — 내용(시트 상자·부품) 영역만 잘라 키움
        diff = ImageChops.difference(out, Image.new('RGB', out.size, bg)).convert('L').point(lambda v: 255 if v > 24 else 0)
        x0, y0, x1, y1 = diff.getbbox()
        m = 20
        out = out.crop((max(0, x0 - m), max(0, y0 - m), min(out.width, x1 + m), min(out.height, y1 + m)))
        out.thumbnail((1400, 1400), Image.LANCZOS)
        p = os.path.join(HERE, 'sch', '%s-sch.png' % b)
        n = save_png(out, p, PNG_MAX)
        rec[rel(dst)[len('docs/readme/gallery/'):]] = {'bytes': os.path.getsize(dst), 'source': rel(sch) + ' (첫 장)', 'sha256': sha(dst)}
        rec[rel(p)[len('docs/readme/gallery/'):]] = {'bytes': n, 'size': list(out.size), 'source': rel(sch) + ' (첫 장 미리보기)', 'sha256': sha(p)}
        if n > PNG_MAX:
            fails.append(rel(p))
    # ⑦ 케이스 초안: 폭 줄인 사본 (시뮬레이션 파형은 README 가 hardware/sim/png 원본을 직접 씀)
    for name, src in CASE:
        im = Image.open(os.path.join(ROOT, src)).convert('RGB')
        if im.width > COPY_W:
            im = im.resize((COPY_W, round(im.height * COPY_W / im.width)), Image.LANCZOS)
        p = os.path.join(HERE, 'mech', name + '.png')
        n = save_png(im, p, PNG_MAX)
        rec[rel(p)[len('docs/readme/gallery/'):]] = {'bytes': n, 'size': list(im.size), 'source': src, 'sha256': sha(p)}
        if n > PNG_MAX:
            fails.append(rel(p))
    shutil.rmtree(tmp, ignore_errors=True)
    json.dump({'files': rec, 'fails': fails}, open(os.path.join(HERE, 'gallery.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for k, v in rec.items():
        print(k, v.get('size'), v['bytes'])
    print('fails', fails)
    return len(fails)


if __name__ == '__main__':
    sys.exit(main())
