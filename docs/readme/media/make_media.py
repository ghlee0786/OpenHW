"""README 회전 GIF · 정지 렌더 — kicad-cli pcb render 만 (Fusion·Blender·Docker 없음).
  FFMPEG=<ffmpeg 경로> python -I -B docs/readme/media/make_media.py --board front|carrier|stack --pcb <커밋>
        [--frames 40] [--fps 12] [--width 720] [--out <폴더>] [--renders <폴더>] [--pcb-front <커밋>]
순서: git archive <커밋> hardware → 사본 + mechanical/models → mechanical/ren002/apply_models.py (3D 모델 연결) → 모델 감사(빠짐 0 이어야 함)
      → --rotate 로 한 바퀴 프레임 → ffmpeg (palettegen/paletteuse, 무한 반복) GIF → 윗면·아랫면 정지 PNG (팔레트 축소)
  --board stack: 3층 적층(전면–코어–캐리어). 전면 보드 렌더 사본의 MH1(광축, (100,100)) 풋프린트에 3D 모델 두 개를 더 붙여 kicad-cli 한 번에 그림:
      캐리어 = 같은 커밋 캐리어 사본의 kicad-cli STEP(3D 모델 포함, --user-origin 100x100mm), 코어 = 단순 외형 VRML(30×30 판 + 부품 층 + 짝 BTB 플러그).
      높이는 기구 적층 그대로 (전면 윗면 기준: 코어 아랫면 −11.2, 캐리어 아랫면 −20.8 = 판 1.6 · BTB 결합 8.0, mechanical/m003/params.py).
      GIF 만 (stack_spin.gif). 코어는 구매 모듈이라 외형 덩어리로만 그린다.
  --renders <폴더>: 정지 렌더 4장 <보드>-top/-bottom/-iso/-iso-back.png (1600 요청 · 투명 · high, docs/renders/p005 와 같은 형식, 팔레트 256 ≤ 600KB)
  --out: GIF·PNG·media.json 을 쓸 곳 (기본 이 폴더). 시험은 저장소 밖 폴더로.
중간 파일: main 체크아웃 validation/runtime/vd001/ren004/ (gitignore). 종료 코드 = 기준(GIF ≤ 5MB · 폭 ≤ 720 · PNG ≤ 600KB · 모델 빠짐 0) 불합격 수."""
import argparse, hashlib, io, json, os, shutil, subprocess, sys, tarfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))   # main 체크아웃 — 산출물 validation/runtime (O-100)
W0 = os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'ren004')
KICAD = os.environ.get('KICAD_CLI') or shutil.which('kicad-cli') or os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
FFMPEG = os.environ.get('FFMPEG', 'ffmpeg')   # 격리 ffmpeg 경로는 환경 변수 FFMPEG 로 (공개 저장소에 로컬 경로를 적지 않음)
TILT = {'front': -40, 'carrier': -40, 'stack': -62}   # 보드를 눕혀 비스듬히 보는 각 (X 축, 도) — 적층은 옆면(층 사이)이 보이게 더 눕힘
ZOOM = {'front': 0.8, 'carrier': 0.8, 'stack': 0.45}
PIVOT = {'stack': ['--pivot', '0,0,-1']}   # 적층은 회전 중심을 적층 가운데(전면 윗면 아래 10 mm)로 — kicad-cli 단위 cm
GIF_MAX, PNG_MAX, W_MAX = 5 * 1024 * 1024, 600 * 1024, 720
# 적층 높이 (mm, 전면 보드 윗면 = 0, +Z = 광축 쪽). 판 1.6 · BTB 결합 8.0 (params.py brd_t/core_t · btb_h)
T, BTB = 1.6, 8.0
Z_CORE_TOP = -(T + BTB)                 # −9.6
Z_CORE_BOT = Z_CORE_TOP - T             # −11.2
Z_CARRIER_BOT = Z_CORE_BOT - BTB - T    # −20.8
# 코어 단순 외형 (기구 좌표 mm: x, y, z 중심 · 크기 · 색) — stack-reference: CORE_ENVELOPE 30×30, 부품 높이 윗면 0.92 · 아랫면 1.26,
#   짝 BTB 플러그 = J1_MATED(x ±8.85, y 9.6…14.0, 윗면) · J2_MATED(x 9.6…14.0, y ±8.85, 아랫면) 의 코어 쪽 절반 4.0
CORE = [((0, 0, Z_CORE_BOT + T / 2), (30, 30, T), (0.05, 0.30, 0.12)),
        ((0, 0, Z_CORE_TOP + 0.46), (27, 27, 0.92), (0.06, 0.06, 0.07)),
        ((0, 0, Z_CORE_BOT - 0.63), (27, 27, 1.26), (0.06, 0.06, 0.07)),
        ((0, 11.8, Z_CORE_TOP + 2.0), (17.7, 4.4, 4.0), (0.18, 0.18, 0.2)),
        ((11.8, 0, Z_CORE_BOT - 2.0), (4.4, 17.7, 4.0), (0.18, 0.18, 0.2))]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if r.returncode:
        print(' '.join(cmd)); print((r.stdout + r.stderr)[-1500:])
        raise SystemExit(r.returncode)
    return r.stdout + r.stderr


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def prep(b, rev):
    """그 커밋의 보드 사본 + 3D 모델 연결 → (보드 파일, 빠진 모델 참조 번호, apply 출력)"""
    src = os.path.join(W0, 'src_' + b)
    shutil.rmtree(src, ignore_errors=True)
    data = subprocess.run(['git', '-C', MAIN, 'archive', rev, 'hardware'], capture_output=True, check=True).stdout
    tarfile.open(fileobj=io.BytesIO(data)).extractall(src)
    shutil.copytree(os.path.join(LANE, 'mechanical', 'models'), os.path.join(src, 'mechanical', 'models'))
    pcb = os.path.join(src, 'hardware', 'schematic', b, b + '.kicad_pcb')
    applied = run([sys.executable, '-I', '-B', os.path.join(LANE, 'mechanical', 'ren002', 'apply_models.py'), pcb]).strip()
    aj = os.path.join(W0, 'audit_%s.json' % b)
    subprocess.run([sys.executable, '-I', '-B', os.path.join(LANE, 'mechanical', 'ren002', 'audit_models.py'), '--src', src, '--out-json', aj, '--no-md'],
                   capture_output=True)
    missing = sorted(r['ref'] for r in json.load(open(aj, encoding='utf-8'))['rows'] if r['board'] == b and r['missing'])
    return pcb, missing, applied


def model_block(path, z):
    p = path.replace('\\', '/')
    return ('\t\t(model "%s"\n\t\t\t(offset\n\t\t\t\t(xyz 0 0 %.3f)\n\t\t\t)\n\t\t\t(scale\n\t\t\t\t(xyz 1 1 1)\n\t\t\t)\n'
            '\t\t\t(rotate\n\t\t\t\t(xyz 0 0 0)\n\t\t\t)\n\t\t)\n' % (p, z))


def make_stack(rev, rev_front):
    """전면 사본에 캐리어 STEP + 코어 VRML 을 MH1 모델로 덧붙인 렌더 사본 → (보드 파일, 빠짐)"""
    cpcb, cmiss, _ = prep('carrier', rev)
    cstep = os.path.join(W0, 'stack_carrier.step')
    run([KICAD, 'pcb', 'export', 'step', '--subst-models', '--user-origin', '100x100mm', '-f', '-o', cstep, cpcb])
    core = os.path.join(W0, 'stack_core.wrl')
    k = 1 / 2.54     # KiCad VRML 단위 = 0.1 inch
    with open(core, 'w', encoding='utf-8') as f:
        f.write('#VRML V2.0 utf8\n')
        for (x, y, z), (sx, sy, sz), (r, g, b) in CORE:
            f.write('Transform { translation %.4f %.4f %.4f children [ Shape { appearance Appearance { material Material { diffuseColor %.3f %.3f %.3f '
                    'specularColor 0.2 0.2 0.2 shininess 0.3 } } geometry Box { size %.4f %.4f %.4f } } ] }\n'
                    % (x * k, y * k, z * k, r, g, b, sx * k, sy * k, sz * k))
    fpcb, fmiss, _ = prep('front', rev_front)
    t = open(fpcb, encoding='utf-8').read()
    i = t.index('(property "Reference" "MH1"')
    s0 = t.rfind('\n\t(footprint ', 0, i)
    e0 = t.index('\n\t)\n', i)          # MH1 풋프린트 끝
    t = t[:e0] + '\n' + model_block(cstep, Z_CARRIER_BOT).rstrip('\n') + '\n' + model_block(core, 0.0).rstrip('\n') + t[e0:]
    assert s0 > 0
    spcb = os.path.join(os.path.dirname(fpcb), 'stack.kicad_pcb')
    open(spcb, 'w', encoding='utf-8', newline='\n').write(t)
    shutil.copy2(os.path.join(os.path.dirname(fpcb), 'front.kicad_pro'), os.path.join(os.path.dirname(fpcb), 'stack.kicad_pro'))
    return spcb, sorted(set(['carrier:' + m for m in cmiss] + ['front:' + m for m in fmiss]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--board', default='front', choices=['front', 'carrier', 'stack'])
    ap.add_argument('--pcb', required=True)
    ap.add_argument('--frames', type=int, default=40)
    ap.add_argument('--fps', type=int, default=12)
    ap.add_argument('--width', type=int, default=720)
    ap.add_argument('--out', default=HERE)
    ap.add_argument('--renders')
    ap.add_argument('--pcb-front', help='--board stack: 전면 보드 커밋 (기본 --pcb)')
    a = ap.parse_args()
    b = a.board
    commit = run(['git', '-C', MAIN, 'rev-parse', '--short', a.pcb]).strip()
    os.makedirs(W0, exist_ok=True)
    if b == 'stack':
        pcb, missing = make_stack(a.pcb, a.pcb_front or a.pcb); applied = '전면·캐리어 사본 apply_models'
    else:
        pcb, missing, applied = prep(b, a.pcb)
    from PIL import Image
    # 프레임: 비스듬히 눕힌 보드를 Z 축으로 한 바퀴 (kicad-cli 는 요청보다 8~32 px 작게 저장 → 크게 그려 가운데를 자름)
    fr = os.path.join(W0, 'frames_' + b)
    shutil.rmtree(fr, ignore_errors=True); os.makedirs(fr)
    w, h = a.width, a.width * 3 // 4
    for k in range(a.frames):
        ang = 360.0 * k / a.frames
        p = os.path.join(fr, 'f_%03d.png' % k)
        run([KICAD, 'pcb', 'render', '-o', p, '-w', str(w + 40), '-h', str(h + 40), '--side', 'top', '--background', 'opaque', '--quality', 'high',
             '--perspective', '--floor', '--zoom', str(ZOOM[b]), '--rotate', '%d,0,%.1f' % (TILT[b], ang)] + PIVOT.get(b, []) + [pcb])
        im = Image.open(p).convert('RGB')
        x0, y0 = (im.width - w) // 2, (im.height - h) // 2
        im.crop((x0, y0, x0 + w, y0 + h)).save(p)
        print('frame', k, ang, flush=True)
    os.makedirs(a.out, exist_ok=True)
    gif = os.path.join(a.out, '%s_spin.gif' % b)
    pal = os.path.join(W0, 'pal_%s.png' % b)
    run([FFMPEG, '-y', '-framerate', str(a.fps), '-i', os.path.join(fr, 'f_%03d.png'), '-vf', 'palettegen=max_colors=128:stats_mode=full', pal])
    run([FFMPEG, '-y', '-framerate', str(a.fps), '-i', os.path.join(fr, 'f_%03d.png'), '-i', pal, '-lavfi',
         'paletteuse=dither=bayer:bayer_scale=4', '-loop', '0', gif])
    # 정지: 윗면 · 아랫면 (정사영, 판 전체) → 팔레트 256 PNG (적층은 GIF 만)
    stills = {}
    for side in (('top', 'bottom') if b != 'stack' else ()):
        p = os.path.join(a.out, '%s_%s.png' % (b, side))
        t = os.path.join(W0, 'still_%s_%s.png' % (b, side))
        run([KICAD, 'pcb', 'render', '-o', t, '-w', '1000', '-h', '1000', '--side', side, '--background', 'transparent', '--quality', 'high', '--zoom', '0.95', pcb])
        im = Image.open(t).convert('RGBA')
        bb = im.getchannel('A').point(lambda v: 255 if v > 128 else 0).getbbox()   # 가장자리 반투명 빛번짐은 빼고 자름
        im = im.crop(bb)
        im.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(p, optimize=True)
        stills[side] = p
    # 정지 렌더 4장 (docs/renders/<보드>/, p005 형식)
    renders = {}
    if a.renders and b != 'stack':
        os.makedirs(a.renders, exist_ok=True)
        for name, side, extra in (('top', 'top', []), ('bottom', 'bottom', []), ('iso', 'top', ['--perspective', '--zoom', '0.8', '--rotate', '-45,0,45']),
                                  ('iso-back', 'bottom', ['--perspective', '--zoom', '0.7', '--rotate', '-45,0,45'])):
            p = os.path.join(a.renders, '%s-%s.png' % (b, name))
            run([KICAD, 'pcb', 'render', '-o', p, '-w', '1600', '-h', '1600', '--side', side, '--background', 'transparent', '--quality', 'high'] + extra + [pcb])
            im = Image.open(p).convert('RGBA')
            im.putalpha(im.getchannel('A').point(lambda v: 255 if v > 128 else 0))   # 가장자리 반투명 빛번짐 제거
            im.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(p, optimize=True)   # 투명 유지 팔레트 (≤ 600 KB)
            renders[name] = {'path': os.path.relpath(p, LANE).replace('\\', '/'), 'bytes': os.path.getsize(p), 'size': list(Image.open(p).size), 'sha256': sha(p)}
    # 기록 · 기준
    gi = Image.open(gif)
    rec = {'board': b, 'pcb': commit if b != 'stack' else 'carrier %s · front %s' % (commit, run(['git', '-C', MAIN, 'rev-parse', '--short', a.pcb_front or a.pcb]).strip()), 'models_applied': applied, 'models_missing': missing,
           'gif': {'path': os.path.relpath(gif, LANE).replace('\\', '/'), 'bytes': os.path.getsize(gif), 'size': list(gi.size),
                   'frames': getattr(gi, 'n_frames', 1), 'fps': a.fps, 'loop': gi.info.get('loop'), 'sha256': sha(gif),
                   'render': 'kicad-cli pcb render --quality high --perspective --floor --zoom %s --rotate %d,0,<0..360> %s' % (ZOOM[b], TILT[b], ' '.join(PIVOT.get(b, [])))},
           'png': {s: {'path': os.path.relpath(p, LANE).replace('\\', '/'), 'bytes': os.path.getsize(p), 'size': list(Image.open(p).size), 'sha256': sha(p)}
                   for s, p in stills.items()},
           'renders': renders}
    fails = []
    if missing:
        fails.append('3D 모델 빠짐 %s' % missing)
    if rec['gif']['bytes'] > GIF_MAX or rec['gif']['size'][0] > W_MAX or rec['gif']['loop'] != 0:
        fails.append('GIF 기준 %s' % rec['gif'])
    for s, v in list(rec['png'].items()) + list(rec['renders'].items()):
        if v['bytes'] > PNG_MAX:
            fails.append('PNG %s %d B' % (s, v['bytes']))
    rec['fails'] = fails
    mj = os.path.join(a.out, 'media.json')
    allrec = json.load(open(mj, encoding='utf-8')) if os.path.exists(mj) else {}
    allrec[b] = rec
    json.dump(allrec, open(mj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps(rec, ensure_ascii=False, indent=1))
    return len(fails)


if __name__ == '__main__':
    sys.exit(main())
