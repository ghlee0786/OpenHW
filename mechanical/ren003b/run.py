"""REN-003b 한 명령 (O-125 2단계) — 메시 준비 → HDRI 확인 → Blender 컷 · 턴테이블 → 1600px 축소 · MP4 → 판정.

  python -I -B mechanical/ren003b/run.py [--case <외함 STEP/STL 폴더>] [--extra <STL 폴더>] [--boards-from <GLB 폴더> | --pcb <커밋>]
        [--final] [--hero-only] [--tag 이름] [--cuts a,b] [--frames N] [--res WxH] [--samples N] [--engine cycles|eevee] [--no-label]

- 메시 (기본값은 main 체크아웃 validation/runtime/vd001/ 의 M-010 최종 산출):
    --case        외함 STEP/STL 폴더. 기본 case/step (STEP → 곡면 오차 ≤ 0.01 mm 삼각화). 시안은 design/A 같은 폴더를 준다.
    --extra       외함 폴더에 없는 부품 STL (렌즈 · 나사 · 하니스 · 코어 등). 기본 render/mesh. 시안 폴더가 다 갖고 있으면 --extra none.
    --boards-from 보드 GLB 폴더. 기본 render/mesh. 없으면 --pcb <커밋> 으로 새로 내보낸다(prep.py).
- 기본 = 저해상도 시험(Cycles 960×540 · 48 샘플 · 턴테이블 24프레임 480×270).
  --final = 4K(3840×2160) · 256 샘플 · 턴테이블 200프레임(8 s @ 25) 1920×1080 + 대표본 복사.
  --hero-only = 히어로 컷 1장만(시안 비교용). --final 과 같이 쓰면 4K 1장.
- 출력: main 체크아웃 validation/runtime/vd001/render/blender-b/<tag>/ (O-100)
    stills/<컷>.png(원본) · web/<컷>.jpg(긴 변 1600px) · turntable/ · turntable.mp4 · scene_report.json · report.json
- 대표본(--final, 이 체크아웃): docs/renders/final/blender-product.png(히어로 1600px) · blender-turntable.mp4
- 도구: BLENDER(실행 파일) 또는 %ProgramFiles%/Blender Foundation/Blender 5.2, FFMPEG_BIN(폴더) 또는 ~/tools/ffmpeg 아래 격리 판,
        HDRI = fetch_hdri.py 가 받은 CC0 파일(assets.json 의 sha256 과 같아야 함). Fusion · Docker · 클라우드 렌더 · 유료 에셋은 쓰지 않는다.
종료 코드 = 불합격 항목 수 (기계 증거만: 단계 종료 코드 · 샘플 수 · 해상도 · 재질 빠짐 0 · 프레임 수 · HDRI sha256). 사실감 · 보기 품질은 판정하지 않는다."""
import argparse
import glob
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(
    ['git', '-C', HERE, 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))
V = os.path.join(MAIN, 'validation', 'runtime', 'vd001')
BASE = os.path.join(V, 'render', 'blender-b')
BLENDER = os.environ.get('BLENDER') or os.path.expandvars(r'%ProgramFiles%\Blender Foundation\Blender 5.2\blender.exe')
ALL_CUTS = ['hero', 'front', 'rear', 'exploded', 'section', 'inuse']
FPS = 25
PY = [sys.executable, '-I', '-B']


def ffbin(name):
    d = os.environ.get('FFMPEG_BIN')
    c = [os.path.join(d, name + '.exe')] if d else sorted(glob.glob(os.path.join(os.path.expanduser('~'), 'tools', 'ffmpeg', '*', 'ffmpeg-*', 'bin', name + '.exe')))
    return c[-1] if c and os.path.exists(c[-1]) else None


def rel(p):
    p = os.path.abspath(p)
    for root, tag in ((MAIN, ''), (LANE, '(이 체크아웃) ')):
        if p.lower().startswith(root.lower() + os.sep):
            return tag + os.path.relpath(p, root).replace('\\', '/')
    return '(저장소 밖) ' + os.path.basename(p)


def sh(title, cmd, log):
    t = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    open(log, 'w', encoding='utf-8').write(r.stdout + '\n---stderr---\n' + r.stderr)
    tail = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.startswith(('REN003B', 'PREP', 'HDRI', 'Traceback')) or 'Error:' in ln][-3:]
    print('[%s] rc %d · %.0f s %s' % (title, r.returncode, time.time() - t, ' | '.join(tail)), flush=True)
    return r.returncode


def png_size(p):
    d = open(p, 'rb').read(24)
    return struct.unpack('>II', d[16:24]) if d[:8] == b'\x89PNG\r\n\x1a\n' else (0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--case', default=os.path.join(V, 'case', 'step'))
    ap.add_argument('--extra', default=os.path.join(V, 'render', 'mesh'))
    ap.add_argument('--boards-from', default=os.path.join(V, 'render', 'mesh'))
    ap.add_argument('--pcb')
    ap.add_argument('--final', action='store_true')
    ap.add_argument('--hero-only', action='store_true')
    ap.add_argument('--cuts')
    ap.add_argument('--frames', type=int)
    ap.add_argument('--res')
    ap.add_argument('--samples', type=int)
    ap.add_argument('--engine', default='cycles')
    ap.add_argument('--tag')
    ap.add_argument('--no-label', action='store_true')
    a = ap.parse_args()
    cuts = a.cuts.split(',') if a.cuts else (['hero'] if a.hero_only else ALL_CUTS)
    res = a.res or ('3840x2160' if a.final else '960x540')
    tt_res = '1920x1080' if a.final else '480x270'
    frames = 0 if a.hero_only else (a.frames if a.frames is not None else (200 if a.final else 24))
    samples = a.samples or (256 if a.final else 48)
    out = os.path.join(BASE, a.tag or ('final' if a.final else 'preview'))
    os.makedirs(out, exist_ok=True)
    W, H = (int(v) for v in res.split('x'))
    TW, TH = (int(v) for v in tt_res.split('x'))
    checks = []

    def chk(name, value, ok, verifiable=True):
        checks.append({'check': name, 'value': value, 'pass': bool(ok), 'verifiable': verifiable})

    # ① 메시
    mesh = os.path.join(out, 'mesh')
    cmd = PY + [os.path.join(HERE, 'prep.py'), '--enclosure', os.path.abspath(a.case), '--out', mesh]
    if a.extra and a.extra != 'none':
        cmd += ['--extra', os.path.abspath(a.extra)]
    cmd += ['--pcb', a.pcb] if a.pcb else ['--boards-from', os.path.abspath(a.boards_from)]
    rc = sh('메시 준비', cmd, os.path.join(out, 'prep.log'))
    chk('메시 준비 종료 코드', rc, rc == 0)
    items = json.load(open(os.path.join(mesh, 'index.json'), encoding='utf-8'))['items'] if os.path.exists(os.path.join(mesh, 'index.json')) else []
    nb = sum(1 for i in items if i['kind'] == 'board')
    enc = [i for i in items if i['kind'] == 'enclosure']
    chk('보드 GLB 수', nb, nb == 2)
    chk('외함 · 부품 메시 수', len(enc), len(enc) > 0)
    step = [i for i in enc if i.get('deflection_mm') is not None]
    chk('STEP 삼각화 곡면 오차 mm (STEP 에서 온 %d개)' % len(step), sorted({i['deflection_mm'] for i in step}), bool(step) and all(i['deflection_mm'] <= 0.01 for i in step))

    # ② HDRI (CC0, 격리 폴더)
    rc = sh('HDRI 확인 (Poly Haven CC0)', PY + [os.path.join(HERE, 'fetch_hdri.py')], os.path.join(out, 'hdri.log'))
    rec = json.load(open(os.path.join(HERE, 'assets.json'), encoding='utf-8'))['hdri'][0]
    hdri = os.path.join(os.environ.get('OPENHW_HDRI_DIR') or os.path.join(os.path.expanduser('~'), 'tools', 'hdri', 'polyhaven'), rec['file'])
    chk('HDRI 받음 · sha256 이 assets.json 과 같음', rec['file'], rc == 0 and os.path.exists(hdri))

    # ③ Blender
    for f in glob.glob(os.path.join(out, 'stills', '*.png')) + glob.glob(os.path.join(out, 'web', '*')):
        os.remove(f)
    sig = hashlib.sha256(json.dumps([items, res, tt_res, samples, frames, a.engine, a.no_label], sort_keys=True).encode()).hexdigest()
    sp = os.path.join(out, 'scene_report.json')
    if not (os.path.exists(sp) and json.load(open(sp, encoding='utf-8')).get('sig') == sig):
        shutil.rmtree(os.path.join(out, 'turntable'), ignore_errors=True)       # 메시나 설정이 바뀌면 옛 프레임을 지운다
    if os.path.exists(sp):
        os.remove(sp)
    rc = sh('Blender 장면 · 렌더', [BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '--python', os.path.join(HERE, 'scene.py'), '--',
                                '--mesh', mesh, '--out', out, '--cuts', ','.join(cuts), '--turntable', str(frames), '--engine', a.engine, '--res', res,
                                '--tt-res', tt_res, '--samples', str(samples), '--hdri', hdri, '--label', '' if a.no_label else 'OpenHW'],
            os.path.join(out, 'blender.log')) if items else 1
    chk('Blender 종료 코드 (--python-exit-code 1)', rc, rc == 0)
    rep = json.load(open(sp, encoding='utf-8')) if rc == 0 and os.path.exists(sp) else {}
    if rep:
        rep['sig'] = sig
        json.dump(rep, open(sp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    g = {}
    exec(open(os.path.join(HERE, '..', 'ren003', 'materials.py'), encoding='utf-8').read(), g)
    chk('재질 정의 수 = materials.py MATS', '%s / %d (+확장 %s)' % (rep.get('mats_defined'), len(g['MATS']), rep.get('mats_ext')), rep.get('mats_defined') == len(g['MATS']))
    chk('재질 빠짐 (규칙에 없는 이름 · 못 가른 색)', rep.get('missing_count'), rep.get('missing_count') == 0)
    chk('엔진 · 장치 · 디노이저', '%s · %s · %s' % (rep.get('engine'), rep.get('device'), rep.get('denoiser')),
        rep.get('engine') == ('CYCLES' if a.engine == 'cycles' else 'BLENDER_EEVEE') and (a.engine != 'cycles' or bool(rep.get('denoiser'))))
    chk('샘플 수', rep.get('samples'), rep.get('samples') == samples)
    chk('HDRI 가 장면에 쓰임 (sha256 일치)', (rep.get('hdri') or {}).get('file'), (rep.get('hdri') or {}).get('sha256') == rec['sha256'])
    chk('색 관리 · 렌즈 · 조리개', '%s · %s mm · f/%s' % (rep.get('view_transform'), sorted({c['lens_mm'] for c in rep.get('cuts', {}).values()}), rep.get('fstop')),
        rep.get('view_transform') == 'AgX' and all(85 <= c['lens_mm'] <= 100 for c in rep.get('cuts', {}).values()) and 5.6 <= (rep.get('fstop') or 0) <= 8)
    chk('베벨 넣은 부품 수 (%.1f mm)' % (rep.get('bevel_mm') or 0), rep.get('beveled'), (rep.get('beveled') or 0) > 0 and 0.2 <= (rep.get('bevel_mm') or 0) <= 0.5)
    bb = rep.get('bbox_mm', {})
    hs = bb.get('HOUSING')
    if hs:      # 지금 외함처럼 HOUSING 이 있을 때만 (시안은 부품 이름이 다를 수 있다)
        for b in ('BOARD_CARRIER', 'BOARD_FRONT'):
            v = bb.get(b)
            chk('%s 가 외함 범위 안 (mm, 커넥터 돌출 여유 −3/+6)' % b, v,
                bool(v) and all(v[i] >= hs[i] - 3.0 for i in range(3)) and all(v[i + 3] <= hs[i + 3] + 6.0 for i in range(3)))
    stills = [os.path.join(out, 'stills', c + '.png') for c in cuts]
    chk('컷 수', '%d / %d %s' % (sum(os.path.exists(p) for p in stills), len(cuts), cuts), all(os.path.exists(p) for p in stills))
    chk('컷 해상도', sorted({png_size(p) for p in stills if os.path.exists(p)}), all(os.path.exists(p) and png_size(p) == (W, H) for p in stills))
    if 'section' in cuts:
        n = (rep.get('cuts', {}).get('section') or {}).get('section_objects')
        chk('단면 컷에서 잘린 객체 수', n, bool(n))

    # ④ 1600px 축소 (README 용)
    web = []
    try:
        from PIL import Image
        os.makedirs(os.path.join(out, 'web'), exist_ok=True)
        for p in stills:
            if os.path.exists(p):
                im = Image.open(p).convert('RGB')
                if max(im.size) > 1600:
                    im = im.resize((1600, round(1600 * im.size[1] / im.size[0])), Image.LANCZOS)
                q = os.path.join(out, 'web', os.path.basename(p)[:-4] + '.jpg')
                im.save(q, quality=92)
                web.append(q)
        chk('축소본 수 (긴 변 ≤ 1600)', len(web), len(web) == len(cuts))
    except ImportError:
        chk('축소본 (PIL 없음)', 0, False)

    # ⑤ 턴테이블 MP4 (격리 ffmpeg, libx264)
    mp4 = os.path.join(out, 'turntable.mp4')
    if frames:
        fr = sorted(glob.glob(os.path.join(out, 'turntable', 'frame_*.png')))
        chk('턴테이블 프레임 수', '%d / %d' % (len(fr), frames), len(fr) == frames)
        chk('턴테이블 프레임 해상도 · 빈 파일 없음', sorted({png_size(p) for p in fr}), bool(fr) and all(png_size(p) == (TW, TH) and os.path.getsize(p) > 1000 for p in fr))
        nd = len({hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in fr})
        chk('프레임이 서로 다름 (돌고 있음)', nd, nd == len(fr) > 1)
        ff, fp = ffbin('ffmpeg'), ffbin('ffprobe')
        chk('격리 ffmpeg 찾음', bool(ff and fp), bool(ff and fp))
        if ff and fp and len(fr) == frames:
            if os.path.exists(mp4):
                os.remove(mp4)
            rc = sh('ffmpeg MP4', [ff, '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(out, 'turntable', 'frame_%04d.png'),
                                   '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-movflags', '+faststart', mp4], os.path.join(out, 'ffmpeg.log'))
            chk('ffmpeg 종료 코드', rc, rc == 0)
            st = {}
            if rc == 0:
                r = subprocess.run([fp, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries',
                                    'stream=nb_read_frames,width,height,codec_name', '-of', 'json', mp4], capture_output=True, text=True)
                st = json.loads(r.stdout)['streams'][0] if r.returncode == 0 else {}
            n = int(st.get('nb_read_frames', 0))
            chk('MP4 프레임 수 · 길이 · 해상도 · 코덱', '%d · %.1f s · %sx%s · %s' % (n, n / FPS, st.get('width'), st.get('height'), st.get('codec_name')),
                n == frames and (st.get('width'), st.get('height')) == (TW, TH) and st.get('codec_name') == 'h264')
            if a.final:
                chk('MP4 길이 8~10 s · 1080p', '%.1f s · %dp' % (n / FPS, TH), 8 <= n / FPS <= 10 and TH == 1080)
        else:
            chk('MP4 만들기', '건너뜀 (프레임 수 또는 ffmpeg)', False)

    # ⑥ 대표본 (--final 이고 전부 통과일 때만) · 기록
    docs = []
    if a.final and not a.hero_only and all(c['pass'] for c in checks):
        d = os.path.join(LANE, 'docs', 'renders', 'final')
        os.makedirs(d, exist_ok=True)
        from PIL import Image
        Image.open(os.path.join(out, 'web', 'hero.jpg')).save(os.path.join(d, 'blender-product.png'))
        shutil.copy2(mp4, os.path.join(d, 'blender-turntable.mp4'))
        docs = ['docs/renders/final/blender-product.png', 'docs/renders/final/blender-turntable.mp4']
    chk('사실감 · 보기 품질 (재질 · 조명 · 구도)', '사람 확인 필요 — 컷 %d장%s' % (len(cuts), ' · MP4' if frames else ''), True, verifiable=False)
    fails = [c for c in checks if c['verifiable'] and not c['pass']]
    json.dump({'mode': ('final' if a.final else 'preview') + ('-hero' if a.hero_only else ''), 'engine': a.engine, 'res': [W, H], 'tt_res': [TW, TH],
               'samples': samples, 'frames': frames, 'fps': FPS, 'case': rel(a.case), 'out': rel(out), 'hdri': rec,
               'materials_used': rep.get('used'), 'looks': rep.get('looks'), 'objects': rep.get('objects'), 'cuts': rep.get('cuts'),
               'representative': docs, 'checks': checks, 'fail': len(fails)},
              open(os.path.join(out, 'report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for c in checks:
        print('  %s %s: %s' % ('—  ' if not c['verifiable'] else 'OK ' if c['pass'] else 'NG ', c['check'], c['value']))
    print('REN-003b %s: 불합격 %d · 출력 %s' % (('final' if a.final else 'preview') + ('-hero' if a.hero_only else ''), len(fails), rel(out)))
    return len(fails)


if __name__ == '__main__':
    sys.exit(main())
