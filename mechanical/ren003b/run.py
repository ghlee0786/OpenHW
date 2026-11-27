"""REN-003b 한 명령 — 메시 준비 → Blender 스틸 3장 · 턴테이블 프레임 → MP4 → 판정.

  python -I -B mechanical/ren003b/run.py [--mesh-from <메시 폴더>] [--enclosure <STEP/STL 폴더>] [--pcb <커밋>]
        [--final] [--frames N] [--res WxH] [--samples N] [--engine eevee|cycles] [--tag 이름]

- 메시 고르기 (셋 중 하나):
    --mesh-from <폴더>   : 이미 있는 메시 폴더(board_*.glb + *.stl)를 그대로 쓴다. 예: main 체크아웃 validation/runtime/vd001/render/mesh (M-010 최종)
    --enclosure <폴더>   : 외함 STEP/STL 폴더 + --pcb 커밋의 보드를 새로 내보낸다 (prep.py)
    (둘 다 없음)         : mechanical/m003/out/step + --pcb 기본 커밋
- 기본 = 저해상도 미리보기(EEVEE 960×540 · 48프레임). --final = Cycles 2560×1440 · 200프레임 + 대표본 복사.
- 출력: main 체크아웃 validation/runtime/vd001/render/blender-b/<tag>/ (O-100) — stills/ · turntable/ · turntable.mp4 · scene_report.json · report.json
- 대표본(--final 일 때만, 이 체크아웃): docs/renders/final/blender-product.png (hero 스틸) · blender-turntable.mp4
- 도구: BLENDER(실행 파일) 또는 %ProgramFiles%/Blender Foundation/Blender 5.2, FFMPEG_BIN(폴더) 또는 %USERPROFILE%/tools/ffmpeg 아래 격리 판,
        KICAD_BIN(폴더, prep.py). Fusion · Docker · 클라우드 렌더는 쓰지 않는다.
종료 코드 = 불합격 항목 수 (기계 증거만: 단계 종료 코드 · 프레임 수 · 해상도 · 재질 빠짐 0 · MP4 프레임 수 · 보드가 외함 안). 보기 품질은 판정하지 않는다."""
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
BASE = os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'render', 'blender-b')
BLENDER = os.environ.get('BLENDER') or os.path.expandvars(r'%ProgramFiles%\Blender Foundation\Blender 5.2\blender.exe')
CAMS = ['hero', 'rear', 'window']
FPS = 25


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
    tail = [ln for ln in (r.stdout + r.stderr).splitlines() if ln.startswith(('REN003B', 'PREP', 'Error', 'Traceback')) or 'Error:' in ln][-3:]
    print('[%s] rc %d · %.0f s %s' % (title, r.returncode, time.time() - t, ' | '.join(tail)), flush=True)
    return r.returncode


def png_size(p):
    d = open(p, 'rb').read(24)
    return struct.unpack('>II', d[16:24]) if d[:8] == b'\x89PNG\r\n\x1a\n' else (0, 0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--mesh-from')
    ap.add_argument('--enclosure')
    ap.add_argument('--pcb', default='995b872')
    ap.add_argument('--final', action='store_true')
    ap.add_argument('--frames', type=int)
    ap.add_argument('--res')
    ap.add_argument('--samples', type=int)
    ap.add_argument('--engine')
    ap.add_argument('--tag')
    a = ap.parse_args()
    eng = a.engine or ('cycles' if a.final else 'eevee')
    res = a.res or ('2560x1440' if a.final else '960x540')
    frames = a.frames or (200 if a.final else 48)
    samples = a.samples or ((256 if eng == 'cycles' else 64) if a.final else 16)
    out = os.path.join(BASE, a.tag or ('final' if a.final else 'preview'))
    os.makedirs(out, exist_ok=True)
    W, H = (int(v) for v in res.split('x'))
    checks = []

    def chk(name, value, ok, verifiable=True):
        checks.append({'check': name, 'value': value, 'pass': bool(ok), 'verifiable': verifiable})

    # ① 메시
    if a.mesh_from:
        mesh = os.path.abspath(a.mesh_from)
        idx = os.path.join(mesh, 'index.json')
        raw = json.load(open(idx, encoding='utf-8')) if os.path.exists(idx) else None
        if not isinstance(raw, dict):       # 다른 도구가 만든 폴더(목록만 있거나 index 없음) → 이 파이프라인 형식의 사본 폴더를 만든다
            rc = sh('메시 준비 (있는 폴더 복사)', [sys.executable, '-I', '-B', os.path.join(HERE, 'prep.py'), '--enclosure', mesh, '--boards-from', mesh,
                                           '--out', os.path.join(BASE, 'mesh')], os.path.join(out, 'prep.log'))
            mesh = os.path.join(BASE, 'mesh')
        else:
            rc = 0
    else:
        mesh = os.path.join(BASE, 'mesh')
        cmd = [sys.executable, '-I', '-B', os.path.join(HERE, 'prep.py'), '--pcb', a.pcb, '--out', mesh]
        rc = sh('메시 준비 (보드 내보내기 · STEP→STL)', cmd + (['--enclosure', os.path.abspath(a.enclosure)] if a.enclosure else []), os.path.join(out, 'prep.log'))
    chk('메시 준비 종료 코드', rc, rc == 0)
    items = json.load(open(os.path.join(mesh, 'index.json'), encoding='utf-8'))['items'] if rc == 0 else []
    chk('보드 GLB 수', sum(1 for i in items if i['kind'] == 'board'), sum(1 for i in items if i['kind'] == 'board') == 2)
    chk('외함 메시 수', sum(1 for i in items if i['kind'] == 'enclosure'), any(i['kind'] == 'enclosure' for i in items))

    # ② Blender (스틸 + 턴테이블 프레임, 끝난 프레임은 건너뜀)
    for f in glob.glob(os.path.join(out, 'stills', '*.png')):
        os.remove(f)
    old = os.path.join(out, 'scene_report.json')
    stale = True
    if os.path.exists(old):     # 메시나 설정이 바뀌었으면 옛 프레임을 지운다
        o = json.load(open(old, encoding='utf-8'))
        stale = o.get('mesh_sha') != hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest() or o.get('res') != [W, H] \
            or o.get('samples') != samples or o.get('frames_requested') != frames
    if stale:
        shutil.rmtree(os.path.join(out, 'turntable'), ignore_errors=True)
    rc = sh('Blender 장면 · 렌더', [BLENDER, '-b', '--factory-startup', '--python-exit-code', '1', '--python', os.path.join(HERE, 'scene.py'), '--',
                                '--mesh', mesh, '--out', out, '--mode', 'both', '--engine', eng, '--res', res, '--samples', str(samples),
                                '--frames', str(frames)], os.path.join(out, 'blender.log')) if items else 1
    chk('Blender 종료 코드', rc, rc == 0)
    rep = json.load(open(old, encoding='utf-8')) if rc == 0 and os.path.exists(old) else {}
    if rep:
        rep['mesh_sha'] = hashlib.sha256(json.dumps(items, sort_keys=True).encode()).hexdigest()
        json.dump(rep, open(old, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    g = {}
    exec(open(os.path.join(HERE, '..', 'ren003', 'materials.py'), encoding='utf-8').read(), g)
    chk('재질 정의 수 = materials.py MATS', '%s / %d' % (rep.get('mats_defined'), len(g['MATS'])), rep.get('mats_defined') == len(g['MATS']))
    chk('재질 빠짐 (규칙에 없는 이름 · 못 가른 색)', rep.get('missing_count'), rep.get('missing_count') == 0)
    bb = rep.get('bbox_mm', {})
    hs = bb.get('HOUSING')
    for b in ('BOARD_CARRIER', 'BOARD_FRONT'):
        v = bb.get(b)
        inside = bool(hs and v) and all(v[i] >= hs[i] - 3.0 for i in range(3)) and all(v[i + 3] <= hs[i + 3] + 6.0 for i in range(3))
        chk('%s 가 외함 범위 안 (mm, 커넥터 돌출 여유 −3/+6)' % b, v, inside)
    stills = [os.path.join(out, 'stills', c + '.png') for c in CAMS]
    chk('스틸 수 (카메라 3개)', sum(os.path.exists(p) for p in stills), all(os.path.exists(p) for p in stills))
    chk('스틸 해상도', sorted({png_size(p) for p in stills if os.path.exists(p)}), all(os.path.exists(p) and png_size(p) == (W, H) for p in stills))
    fr = sorted(glob.glob(os.path.join(out, 'turntable', 'frame_*.png')))
    chk('턴테이블 프레임 수', '%d / %d' % (len(fr), frames), len(fr) == frames)
    chk('턴테이블 프레임 해상도 · 빈 파일 없음', sorted({png_size(p) for p in fr}), bool(fr) and all(png_size(p) == (W, H) and os.path.getsize(p) > 1000 for p in fr))
    chk('프레임이 서로 다름 (돌고 있음)', len({hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in fr}), len({hashlib.sha256(open(p, 'rb').read()).hexdigest() for p in fr}) == len(fr) > 1)

    # ③ MP4 (격리 ffmpeg, libx264)
    mp4 = os.path.join(out, 'turntable.mp4')
    ff, fp = ffbin('ffmpeg'), ffbin('ffprobe')
    chk('격리 ffmpeg 찾음', bool(ff and fp), bool(ff and fp))
    n = 0
    if ff and fp and len(fr) == frames:
        if os.path.exists(mp4):
            os.remove(mp4)
        rc = sh('ffmpeg MP4', [ff, '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(out, 'turntable', 'frame_%04d.png'),
                               '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-movflags', '+faststart', mp4], os.path.join(out, 'ffmpeg.log'))
        chk('ffmpeg 종료 코드', rc, rc == 0)
        if rc == 0:
            r = subprocess.run([fp, '-v', 'error', '-select_streams', 'v:0', '-count_frames', '-show_entries', 'stream=nb_read_frames,width,height,codec_name',
                                '-of', 'json', mp4], capture_output=True, text=True)
            st = json.loads(r.stdout)['streams'][0] if r.returncode == 0 else {}
            n = int(st.get('nb_read_frames', 0))
            chk('MP4 프레임 수 · 해상도 · 코덱', '%d · %sx%s · %s' % (n, st.get('width'), st.get('height'), st.get('codec_name')),
                n == frames and (st.get('width'), st.get('height')) == (W, H) and st.get('codec_name') == 'h264')
    else:
        chk('MP4 만들기', '건너뜀 (프레임 수 또는 ffmpeg)', False)

    # ④ 대표본 (--final 만) · 기록
    docs = []
    if a.final and all(c['pass'] for c in checks):
        d = os.path.join(LANE, 'docs', 'renders', 'final')
        os.makedirs(d, exist_ok=True)
        for src, name in ((stills[0], 'blender-product.png'), (mp4, 'blender-turntable.mp4')):
            shutil.copy2(src, os.path.join(d, name))
            docs.append('docs/renders/final/' + name)
    chk('보기 품질 (재질 · 조명 · 구도가 보기에 맞는가)', '사람 확인 필요 — 스틸 3장 · MP4', True, verifiable=False)
    fails = [c for c in checks if c['verifiable'] and not c['pass']]
    json.dump({'mode': 'final' if a.final else 'preview', 'engine': eng, 'res': [W, H], 'samples': samples, 'frames': frames, 'fps': FPS,
               'mesh': rel(mesh), 'out': rel(out), 'pcb': a.pcb if not a.mesh_from else None, 'materials_used': rep.get('used'),
               'objects': rep.get('objects'), 'representative': docs, 'checks': checks, 'fail': len(fails)},
              open(os.path.join(out, 'report.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for c in checks:
        print('  %s %s: %s' % ('—  ' if not c['verifiable'] else 'OK ' if c['pass'] else 'NG ', c['check'], c['value']))
    print('REN-003b %s: 불합격 %d · 출력 %s' % ('final' if a.final else 'preview', len(fails), rel(out)))
    return len(fails)


if __name__ == '__main__':
    sys.exit(main())
