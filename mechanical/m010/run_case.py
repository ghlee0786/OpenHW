"""M-010 최종 케이스 경로 (O-102, D-003 #49) — 한 명령:
  pcb 커밋 보드 → (사본 + REN-002 apply_models) → kicad-cli STEP (--subst-models, --user-origin 100x100mm = 코어 중심)
  → main 체크아웃 validation/runtime/vd001/boards/ → Fusion M003 외함 문서에 가져오기·외함 다시 만들기·간섭 → STEP/STL/f3d 내보내기
  → M-007 조립·판정 J1~J6 (run_all.py, 조건 5) → Blender 최종 렌더 (REN-002) → 대표본 복사.
사용: python -I -B mechanical/m010/run_case.py --pcb-carrier <커밋> --pcb-front <커밋> [--docs <폴더>] [--skip-render]
  --docs: 대표 PNG(제품 10 · PCB 앞뒤 4)·MP4 를 복사할 곳 (기본 이 체크아웃 docs/renders — 커밋은 사람이/세션이 따로)
산출물: main 체크아웃 validation/runtime/vd001/{boards,case,render,results} (O-100). 기록: validation/runtime/vd001/m010_run.json + mechanical/m010/run.md
종료 코드 = 막힌 단계 수 (판정 불합격은 막힘이 아님 — 조건 5 불합격 수는 run.md·결과 파일에)."""
import argparse, datetime, glob, hashlib, json, os, shutil, subprocess, sys, time

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))   # main 체크아웃 — 산출물 validation/runtime (O-100)
V = os.path.join(MAIN, 'validation', 'runtime', 'vd001')
R = os.path.join(V, 'render')
M = os.path.join(LANE, 'mechanical')
PY = [sys.executable, '-I', '-B']
FRUN = PY + [os.path.join(M, 'fusion_run.py')]
KICAD = os.path.expandvars(r'%LOCALAPPDATA%\Programs\KiCad\10.0\bin\kicad-cli.exe')
BLENDER = r'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
CHUNKS = os.path.join(os.path.expanduser('~'), '.claude', 'skills', 'blender-render', 'scripts', 'render_chunks.py')
VIEWS = ['front', 'back', 'threequarter', 'exploded', 'section', 'window', 'connectors', 'microsd', 'inuse', 'dims']
steps = []


def step(name, cmd, ok=(0,), timeout=3600):
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=timeout)
    out = (r.stdout + r.stderr).strip()
    rc_ok = r.returncode in ok if ok is not None else True
    steps.append({'step': name, 'rc': r.returncode, 'blocked': not rc_ok, 's': round(time.time() - t0, 1), 'tail': out[-600:]})
    print('[%s] rc %d %s (%.0f s)' % (name, r.returncode, '' if rc_ok else '**막힘**', time.time() - t0), flush=True)
    if not rc_ok:
        print(out[-2000:])
    return r.returncode, out


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcb-carrier', required=True)
    ap.add_argument('--pcb-front', required=True)
    ap.add_argument('--docs', default=os.path.join(LANE, 'docs', 'renders'))
    ap.add_argument('--skip-render', action='store_true')
    a = ap.parse_args()
    case = os.path.join(V, 'case')
    os.makedirs(case, exist_ok=True)
    # 1) 보드 STEP + M-007 조립·판정 (조건 5) — 종료 코드 = 불합격 수, 97~99 = 막힘
    rc5, o5 = step('run_all (보드 STEP·M007 조립·J1~J6)', PY + [os.path.join(M, 'm007', 'run_all.py'), '--pcb-carrier', a.pcb_carrier, '--pcb-front', a.pcb_front],
                   ok=range(0, 97))
    if steps[-1]['blocked']:
        return finish(a, rc5)
    # 1b) 케이스 매개변수 ↔ pcb fab 커넥터 위치 (run_all.py 가 읽은 connectors.json). 다르면 「케이스 수정 필요」 — params.py 를 pcb 에 맞춘다
    g = {}
    exec(open(os.path.join(M, 'm003', 'params.py'), encoding='utf-8').read(), g)
    conn = json.load(open(os.path.join(V, 'boards', 'connectors.json'), encoding='utf-8'))
    diff = {k: [list(g['P'][k]), v] for k, v in conn.items() if k in g['P'] and max(abs(p - q) for p, q in zip(g['P'][k], v)) > 0.05}
    steps.append({'step': '케이스 params.py ↔ pcb fab 커넥터 (허용 0.05)', 'rc': len(diff), 'blocked': False, 's': 0,
                  'tail': '케이스 수정 필요 %d %s' % (len(diff), json.dumps(diff))})
    print('[params ↔ pcb] 다름 %d %s' % (len(diff), diff), flush=True)
    # 2) Fusion M003 외함 문서: 보드 STEP 가져오기 → 외함 다시 만들기 → 간섭 → STEP/STL/f3d
    step('M003 01 새 문서·보드 STEP 가져오기', FRUN + [os.path.join(M, 'm003', 'scripts', '01_new_doc_import.py')])
    step('M003 02 외함 만들기 (params.py·geom.py)', FRUN + [os.path.join(M, 'm003', 'scripts', '02_build.py')])
    step('M003 03 간섭', FRUN + [os.path.join(M, 'm003', 'scripts', '03_check.py'), '--set', 'TXT=' + os.path.join(case, 'interference.txt')])
    step('M003 04 STEP/STL/f3d 내보내기', FRUN + [os.path.join(M, 'm003', 'scripts', '04_export.py'), '--set', 'OUT=' + case])
    if any(s['blocked'] for s in steps) or a.skip_render:
        return finish(a, rc5)
    # 3) 렌더 (REN-002): PCB → 메시(M007 문서) → GLB → Blender 스틸·치수·턴테이블 → judge
    step('PCB 렌더 (kicad-cli, 모델 연결 사본)', PY + [os.path.join(M, 'ren002', 'scripts', '02_pcb_render.py')])
    step('M007 문서 활성', FRUN + [os.path.join(M, 'm010', 'scripts', '00_activate.py'), '--set', 'DOC=M007_assembly'])
    step('메시 내보내기 (Fusion)', FRUN + [os.path.join(M, 'ren002', 'scripts', '03_export_meshes.py')])
    for b in ('carrier', 'front'):
        step('GLB %s' % b, [KICAD, 'pcb', 'export', 'glb', '--user-origin', '100x100mm', '--subst-models', '--include-tracks', '--include-pads',
                            '--include-zones', '--include-silkscreen', '--include-soldermask', '-f', '-o', os.path.join(R, 'mesh', 'board_%s.glb' % b),
                            os.path.join(V, 'pcbsrc', b, 'hardware', 'schematic', b, b + '.kicad_pcb')])
    if any(s['blocked'] for s in steps):
        return finish(a, rc5)
    step('Blender 스틸 10', [BLENDER, '-b', '--factory-startup', '--python', os.path.join(M, 'ren002', 'scene.py'), '--', '--mode', 'stills'], timeout=7200)
    step('치수선 겹침', PY + [os.path.join(M, 'ren002', 'scripts', '04_dims_overlay.py')])
    step('턴테이블 .blend', [BLENDER, '-b', '--factory-startup', '--python', os.path.join(M, 'ren002', 'scene.py'), '--', '--mode', 'blend'])
    for p in glob.glob(os.path.join(R, 'blender', 'ren002_turntable.mp4')) + glob.glob(os.path.join(R, 'blender', 'turntable', '*.png')):   # 남은 프레임·MP4 는 render_chunks 가 건너뜀
        os.remove(p)
    step('턴테이블 렌더·MP4', [sys.executable, CHUNKS, '--blend', os.path.join(R, 'blender', 'turntable.blend'), '--out', os.path.join(R, 'blender', 'turntable'),
                           '--start', '1', '--end', '200', '--chunk', '40', '--fps', '25', '--mp4', os.path.join(R, 'blender', 'ren002_turntable.mp4')], timeout=7200)
    step('렌더 판정 (judge.py)', PY + [os.path.join(M, 'ren002', 'judge.py')])
    # 4) 대표본: 제품 10 · PCB 앞뒤 4 · MP4 → --docs (개당 < 20 MB)
    os.makedirs(a.docs, exist_ok=True)
    reps = [os.path.join(R, 'blender', 'stills', 'ren002_%s.png' % v) for v in VIEWS] + \
           [os.path.join(R, 'pcb', '%s_%s.png' % (b, s)) for b in ('carrier', 'front') for s in ('top', 'bottom')] + [os.path.join(R, 'blender', 'ren002_turntable.mp4')]
    big = [p for p in reps if not os.path.exists(p) or os.path.getsize(p) >= 20 * 1024 * 1024]
    for p in reps:
        if p not in big:
            shutil.copy2(p, os.path.join(a.docs, os.path.basename(p)))
    rel = os.path.relpath(os.path.abspath(a.docs), LANE).replace('\\', '/')   # 기록에는 저장소 상대 경로만 (공개 저장소)
    steps.append({'step': '대표본 복사 → %s' % (rel if not rel.startswith('..') else '(저장소 밖 폴더)'), 'rc': len(big), 'blocked': bool(big), 's': 0,
                  'tail': '복사 %d · 없음/20MB 이상 %s' % (len(reps) - len(big), [os.path.basename(p) for p in big]),
                  'files': {os.path.basename(p): [os.path.getsize(p), sha(p)] for p in reps if p not in big}})
    return finish(a, rc5)


def finish(a, rc5):
    blocked = sum(1 for s in steps if s['blocked'])
    c5 = os.path.join(V, 'results', 'cond5-mechanical.json')
    cond5 = json.load(open(c5, encoding='utf-8')) if os.path.exists(c5) else {}
    rec = {'generated': datetime.datetime.now().isoformat(timespec='seconds'), 'pcb_carrier': a.pcb_carrier, 'pcb_front': a.pcb_front,
           'command': 'python -I -B mechanical/m010/run_case.py --pcb-carrier %s --pcb-front %s' % (a.pcb_carrier, a.pcb_front),
           'exit_code': blocked, 'cond5_exit': rc5, 'cond5_fail': [(x['id'], x['title'], x['value']) for x in cond5.get('items', []) if x['pass'] is False],
           'steps': steps}
    json.dump(rec, open(os.path.join(V, 'm010_run.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    L = ['# M-010 실행 기록 (run_case.py 출력 — 종료 코드 = 막힌 단계 수 %d)' % blocked, '',
         '- 명령: `%s`' % rec['command'], '- 시각: %s' % rec['generated'],
         '- 조건 5 (run_all.py) 종료 코드 %d = 불합격 항목 수 — 막힘 아님' % rc5, '',
         '| 단계 | 종료 코드 | 막힘 | 초 |', '|---|---|---|---|']
    L += ['| %s | %d | %s | %s |' % (s['step'], s['rc'], '**예**' if s['blocked'] else '아니오', s['s']) for s in steps]
    L += ['', '## 조건 5 불합격 항목', ''] + ['- %s %s = %s' % x for x in rec['cond5_fail']]
    case = os.path.join(V, 'case')
    if os.path.exists(os.path.join(case, 'interference.txt')):
        L += ['', '## M003 외함 문서 간섭 (validation/runtime/vd001/case/interference.txt)', '', '```'] + \
             open(os.path.join(case, 'interference.txt'), encoding='utf-8').read().strip().split('\n') + ['```']
    L += ['', '## 산출 해시 (main 체크아웃 validation/runtime/vd001/)', '']
    for p in sorted(glob.glob(os.path.join(V, 'boards', '*.step')) + glob.glob(os.path.join(case, '*.*')) + glob.glob(os.path.join(case, '*', '*.*'))
                    + [os.path.join(R, 'blender', 'ren002_turntable.mp4'), os.path.join(R, 'manifest.json')]):
        if os.path.isfile(p):
            L.append('- %s %s' % (os.path.relpath(p, V).replace('\\', '/'), sha(p)))
    open(os.path.join(HERE, 'run.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L[:8 + len(steps)]))
    return blocked


if __name__ == '__main__':
    sys.exit(main())
