"""REN-001 00: kicad-cli 보드 렌더 6장 (캐리어·전면 × 윗면·아랫면·기울임) → validation/runtime/vd001/render/pcb/<보드>_<보기>.png 2560×1440
kicad-cli 10.0.8 pcb render 는 요청보다 8~32 px 작게 저장한다(요청 2560×1440 → 2552×1432) → 40 px 크게 그린 뒤 가운데를 잘라 맞춘다(배율 변경 없음).
입력: validation/runtime/vd001/pcbsrc (run_all.py 가 pcb 커밋에서 꺼냄)."""
import os, subprocess, sys
from PIL import Image

LANE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
V = os.path.join(LANE, 'validation', 'runtime', 'vd001')
OUT = os.path.join(V, 'render', 'pcb')
KICAD = os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
W, H, PAD = 2560, 1440, 40
VIEWS = {'top': ('top', None), 'bottom': ('bottom', None), 'tilt': ('top', '-40,0,30')}   # 기울임은 zoom 0.8 (1.0 이면 보드 아래가 잘림)


def main():
    os.makedirs(OUT, exist_ok=True)
    bad = 0
    for b in ('carrier', 'front'):
        src = os.path.join(V, 'pcbsrc', 'hardware', 'schematic', b, b + '.kicad_pcb')
        for v, (side, rot) in VIEWS.items():
            out = os.path.join(OUT, '%s_%s.png' % (b, v))
            cmd = [KICAD, 'pcb', 'render', '--quality', 'high', '--floor', '--perspective', '-w', str(W + PAD), '-h', str(H + PAD),
                   '--side', side, '-o', out, src] + (['--rotate', rot, '--zoom', '0.8'] if rot else [])
            rc = subprocess.run(cmd, capture_output=True).returncode
            im = Image.open(out)
            w, h = im.size
            if rc or w < W or h < H:
                print('FAIL', b, v, rc, w, h); bad += 1; continue
            x0, y0 = (w - W) // 2, (h - H) // 2
            im.crop((x0, y0, x0 + W, y0 + H)).save(out)
            print('PCB', b, v, '%dx%d -> %dx%d' % (w, h, W, H))
    return bad


if __name__ == '__main__':
    sys.exit(main())
