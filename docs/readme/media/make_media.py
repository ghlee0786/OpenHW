"""README 회전 GIF · 정지 렌더 — kicad-cli pcb render 만 (Fusion·Blender·Docker 없음).
  FFMPEG=<ffmpeg 경로> python -I -B docs/readme/media/make_media.py --board front --pcb <커밋> [--frames 40] [--fps 12] [--width 720]
순서: git archive <커밋> hardware → 사본 + mechanical/models → mechanical/ren002/apply_models.py (3D 모델 연결) → 모델 감사(빠짐 0 이어야 함)
      → --rotate 로 한 바퀴 프레임 → ffmpeg (palettegen/paletteuse, 무한 반복) GIF → 윗면·아랫면 정지 PNG (팔레트 축소)
중간 파일: main 체크아웃 validation/runtime/vd001/ren004/ (gitignore). 산출: docs/readme/media/<보드>_spin.gif · <보드>_top.png · <보드>_bottom.png · media.json
종료 코드 = 기준(GIF ≤ 5MB · 폭 ≤ 720 · PNG ≤ 600KB · 모델 빠짐 0) 불합격 수."""
import argparse, glob, hashlib, io, json, os, shutil, subprocess, sys, tarfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))   # main 체크아웃 — 산출물 validation/runtime (O-100)
W0 = os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'ren004')
KICAD = os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')   # 격리 ffmpeg 경로는 환경 변수 FFMPEG 로 (공개 저장소에 로컬 경로를 적지 않음)
TILT = -40          # 보드를 눕혀 비스듬히 보는 각 (X 축, 도)
GIF_MAX, PNG_MAX, W_MAX = 5 * 1024 * 1024, 600 * 1024, 720


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        print(' '.join(cmd)); print((r.stdout + r.stderr)[-1500:])
        raise SystemExit(r.returncode)
    return r.stdout + r.stderr


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--board', default='front', choices=['front', 'carrier'])
    ap.add_argument('--pcb', required=True)
    ap.add_argument('--frames', type=int, default=40)
    ap.add_argument('--fps', type=int, default=12)
    ap.add_argument('--width', type=int, default=720)
    a = ap.parse_args()
    b = a.board
    commit = run(['git', '-C', MAIN, 'rev-parse', '--short', a.pcb]).strip()
    src = os.path.join(W0, 'src_' + b)
    shutil.rmtree(src, ignore_errors=True)
    data = subprocess.run(['git', '-C', MAIN, 'archive', a.pcb, 'hardware'], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(data)).extractall(src)
    shutil.copytree(os.path.join(LANE, 'mechanical', 'models'), os.path.join(src, 'mechanical', 'models'))
    pcb = os.path.join(src, 'hardware', 'schematic', b, b + '.kicad_pcb')
    applied = run([sys.executable, '-I', '-B', os.path.join(LANE, 'mechanical', 'ren002', 'apply_models.py'), pcb]).strip()
    aj = os.path.join(W0, 'audit_%s.json' % b)
    subprocess.run([sys.executable, '-I', '-B', os.path.join(LANE, 'mechanical', 'ren002', 'audit_models.py'), '--src', src, '--out-json', aj, '--no-md'],
                   capture_output=True)
    missing = sorted(r['ref'] for r in json.load(open(aj, encoding='utf-8'))['rows'] if r['board'] == b and r['missing'])
    # 프레임: 비스듬히 눕힌 보드를 Z 축으로 한 바퀴 (kicad-cli 는 요청보다 8~32 px 작게 저장 → 크게 그려 가운데를 자름)
    fr = os.path.join(W0, 'frames_' + b)
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    w, h = a.width, a.width * 3 // 4
    from PIL import Image
    for k in range(a.frames):
        ang = 360.0 * k / a.frames
        p = os.path.join(fr, 'f_%03d.png' % k)
        run([KICAD, 'pcb', 'render', '-o', p, '-w', str(w + 40), '-h', str(h + 40), '--side', 'top', '--background', 'opaque', '--quality', 'high',
             '--perspective', '--floor', '--zoom', '0.8', '--rotate', '%d,0,%.1f' % (TILT, ang), pcb])
        im = Image.open(p).convert('RGB')
        x0, y0 = (im.width - w) // 2, (im.height - h) // 2
        im.crop((x0, y0, x0 + w, y0 + h)).save(p)
        print('frame', k, ang, flush=True)
    os.makedirs(HERE, exist_ok=True)
    gif = os.path.join(HERE, '%s_spin.gif' % b)
    pal = os.path.join(W0, 'pal_%s.png' % b)
    run([FFMPEG, '-y', '-framerate', str(a.fps), '-i', os.path.join(fr, 'f_%03d.png'), '-vf', 'palettegen=max_colors=128:stats_mode=full', pal])
    run([FFMPEG, '-y', '-framerate', str(a.fps), '-i', os.path.join(fr, 'f_%03d.png'), '-i', pal, '-lavfi',
         'paletteuse=dither=bayer:bayer_scale=4', '-loop', '0', gif])
    # 정지: 윗면 · 아랫면 (정사영, 판 전체) → 팔레트 256 PNG
    stills = {}
    for side in ('top', 'bottom'):
        p = os.path.join(HERE, '%s_%s.png' % (b, side))
        t = os.path.join(W0, 'still_%s_%s.png' % (b, side))
        run([KICAD, 'pcb', 'render', '-o', t, '-w', '1000', '-h', '1000', '--side', side, '--background', 'transparent', '--quality', 'high', '--zoom', '0.95', pcb])
        im = Image.open(t).convert('RGBA')
        bb = im.getchannel('A').point(lambda v: 255 if v > 128 else 0).getbbox()   # 가장자리 반투명 빛번짐은 빼고 자름
        im = im.crop(bb)
        im.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(p, optimize=True)
        stills[side] = p
    # 기록 · 기준
    gi = Image.open(gif)
    rec = {'board': b, 'pcb': commit, 'models_applied': applied, 'models_missing': missing,
           'gif': {'path': os.path.relpath(gif, LANE).replace('\\', '/'), 'bytes': os.path.getsize(gif), 'size': list(gi.size),
                   'frames': getattr(gi, 'n_frames', 1), 'fps': a.fps, 'loop': gi.info.get('loop'), 'sha256': sha(gif),
                   'render': 'kicad-cli pcb render --quality high --perspective --floor --zoom 0.8 --rotate %d,0,<0..360>' % TILT},
           'png': {s: {'path': os.path.relpath(p, LANE).replace('\\', '/'), 'bytes': os.path.getsize(p), 'size': list(Image.open(p).size), 'sha256': sha(p)}
                   for s, p in stills.items()}}
    fails = []
    if missing:
        fails.append('3D 모델 빠짐 %s' % missing)
    if rec['gif']['bytes'] > GIF_MAX or rec['gif']['size'][0] > W_MAX or rec['gif']['loop'] != 0:
        fails.append('GIF 기준 %s' % rec['gif'])
    for s, v in rec['png'].items():
        if v['bytes'] > PNG_MAX:
            fails.append('PNG %s %d B' % (s, v['bytes']))
    rec['fails'] = fails
    mj = os.path.join(HERE, 'media.json')
    allrec = json.load(open(mj, encoding='utf-8')) if os.path.exists(mj) else {}
    allrec[b] = rec
    json.dump(allrec, open(mj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False, indent=1))
    return len(fails)


if __name__ == '__main__':
    sys.exit(main())
