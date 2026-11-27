"""M-010 최종 케이스 경로 (O-102, D-003 #49) — 한 명령:
  pcb 커밋 보드 → (사본 + REN-002 apply_models) → kicad-cli STEP (--subst-models, --user-origin 100x100mm = 코어 중심)
  → main 체크아웃 validation/runtime/vd001/boards/ → Fusion M003 외함 문서에 가져오기·외함 다시 만들기·간섭 → STEP/STL/f3d 내보내기
  → M-007 조립·판정 J1~J6 (run_all.py, 조건 5) → Blender 최종 렌더 (REN-002) → 대표본 복사.
사용: python -I -B mechanical/m010/run_case.py --pcb-carrier <커밋> --pcb-front <커밋> [--docs <폴더>] [--skip-render] [--no-fusion]
  --no-fusion (O-107): 비-Fusion 부분만 WIP 사전 점검 — 사본·모델 감사·STEP·커넥터 대조·pcb 위치 대조·GLB·재질 건식 점검 → vd001/wip/m010_wip.json
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
    ap.add_argument('--no-fusion', action='store_true', help='O-107 WIP 사전 점검: Fusion·렌더 단계 건너뜀 (기록은 main validation/runtime/vd001/wip/)')
    a = ap.parse_args()
    if a.no_fusion:
        return wip(a)
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


# O-107: pcb 위치 기준 (기구 쪽 원본 값, 기구 좌표 mm: x = X − 100, y = −(Y − 100)). 허용 0.05
EXPECT = {
    'front': {'D_IR_A1': (-6.0, 16.0), 'D_IR_A2': (6.0, 16.0),       # params led_a_y 16.0 · 기준 적층 LED x ±6 (M-007 J5 광선 추적 근거)
              'D_IR_B1': (-7.5, -16.5), 'D_IR_B2': (7.5, -16.5),     # params led_b_y −16.5 · x ±7.5 (led_study V4)
              'MH1': (0.0, 0.0),                                    # 광축 = 코어 중심 (M-008)
              'J1': (0.0, 11.8),                                    # 짝 BTB 외형 중심 (stack-reference J1_MATED_ENVELOPE y 9.6…14.0)
              'J3': (0.0, -11.55),                                  # DF30 (m008/cla216_spec.py DF30)
              'J2': (16.0, 9.27)},                                  # ICR 납땜 패드 두 개 가운데 (cla216_spec ICR_PADS)
    'carrier': {'J1': (11.8, 0.0)},                                 # 짝 BTB 외형 중심 (stack-reference J2_MATED_ENVELOPE x 9.6…14.0)
}


def positions(b):
    """pcb 사본 보드의 풋프린트 위치 (기구 좌표). J2(전면 ICR) 는 패드 두 개 가운데, 나머지는 풋프린트 원점."""
    import re
    t = open(os.path.join(V, 'pcbsrc', b, 'hardware', 'schematic', b, b + '.kicad_pcb'), encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'\n\t\(footprint "([^"]+)"', t):
        e = t.find('\n\t)\n', m.start())
        blk = t[m.start():e]
        ref = re.search(r'\(property "Reference" "([^"]+)"', blk).group(1)
        at = re.search(r'\n\t\t\(at ([-\d.]+) ([-\d.]+)', blk)
        X, Y = float(at.group(1)), float(at.group(2))
        if b == 'front' and ref == 'J2':
            import math
            r = math.radians(float((re.search(r'\n\t\t\(at [-\d.]+ [-\d.]+ ([-\d.]+)', blk) or [0, 0])[1]))
            pads = [tuple(map(float, p)) for p in re.findall(r'\(pad "\d+" thru_hole \w+\s*\(at ([-\d.]+) ([-\d.]+)', blk)]
            if pads:
                px = sum(X + x * math.cos(r) + y * math.sin(r) for x, y in pads) / len(pads)
                py = sum(Y - x * math.sin(r) + y * math.cos(r) for x, y in pads) / len(pads)
                X, Y = px, py
        out[ref] = (round(X - 100.0, 3), round(-(Y - 100.0), 3))
        if ref.startswith('H') and 'MountingHole' in m.group(1):
            out.setdefault('_holes', []).append(out[ref])
    return out


def wip(a):
    """O-107: run_case 의 비-Fusion 부분만 (보드 사본·모델 감사·STEP·커넥터 → params 대조 → pcb 위치 대조 → GLB → 재질 건식 점검)."""
    W = os.path.join(V, 'wip')
    os.makedirs(W, exist_ok=True)
    rc, o = step('run_all --no-fusion (사본·apply_models·감사·STEP·커넥터)', PY + [os.path.join(M, 'm007', 'run_all.py'), '--no-fusion',
                                                                          '--pcb-carrier', a.pcb_carrier, '--pcb-front', a.pcb_front])
    if rc:
        return finish(a, None, wip=True)
    steps[-1]['tail'] = o[-900:]
    g = {}
    exec(open(os.path.join(M, 'm003', 'params.py'), encoding='utf-8').read(), g)
    conn = json.load(open(os.path.join(V, 'boards', 'connectors.json'), encoding='utf-8'))
    diff = {k: [list(g['P'][k]), v] for k, v in conn.items() if k in g['P'] and max(abs(p - q) for p, q in zip(g['P'][k], v)) > 0.05}
    steps.append({'step': '케이스 params.py ↔ pcb fab 커넥터 (허용 0.05)', 'rc': len(diff), 'blocked': False, 's': 0,
                  'tail': '다름 %d %s' % (len(diff), json.dumps(diff))})
    bad = {}
    for b, exp in EXPECT.items():
        pos = positions(b)
        for ref, xy in exp.items():
            got = pos.get(ref)
            if got is None or max(abs(p - q) for p, q in zip(got, xy)) > 0.05:
                bad['%s %s' % (b, ref)] = [xy, got]
        holes = pos.get('_holes', [])
        miss = [h for h in g['P']['holes'] if not any(max(abs(p - q) for p, q in zip(h, x)) <= 0.05 for x in holes)]
        if b == 'front' and miss:
            bad['front 장착 구멍'] = [g['P']['holes'], holes]
        if b == 'carrier':   # 캐리어 (+17, −17) 는 뺌 (stack-reference §5) — 나머지 4개는 같아야 함
            if miss:
                bad['carrier 장착 구멍'] = [g['P']['holes'], holes]
    steps.append({'step': 'pcb 위치 ↔ 기구 기준 (LED·MH1·BTB·DF30·ICR 패드·구멍, 허용 0.05)', 'rc': len(bad), 'blocked': False, 's': 0,
                  'tail': '다름 %d %s' % (len(bad), json.dumps(bad, ensure_ascii=False))})
    for b in ('carrier', 'front'):
        step('GLB %s (재질 건식 점검용)' % b, [KICAD, 'pcb', 'export', 'glb', '--user-origin', '100x100mm', '--subst-models', '--include-tracks',
                                          '--include-pads', '--include-zones', '--include-silkscreen', '--include-soldermask', '-f', '-o',
                                          os.path.join(W, 'board_%s.glb' % b), os.path.join(V, 'pcbsrc', b, 'hardware', 'schematic', b, b + '.kicad_pcb')])
    if not any(s['blocked'] for s in steps):
        step('재질 건식 점검 (ren003 dryrun_glb, 못 가른 색 수)', PY + [os.path.join(M, 'ren003', 'dryrun_glb.py'), W, os.path.join(W, 'assign_glb.md')], ok=None)
    return finish(a, None, wip=True)


def finish(a, rc5, wip=False):
    blocked = sum(1 for s in steps if s['blocked'])
    c5 = os.path.join(V, 'results', 'cond5-mechanical.json')
    cond5 = json.load(open(c5, encoding='utf-8')) if os.path.exists(c5) else {}
    rec = {'generated': datetime.datetime.now().isoformat(timespec='seconds'), 'pcb_carrier': a.pcb_carrier, 'pcb_front': a.pcb_front,
           'command': 'python -I -B mechanical/m010/run_case.py --pcb-carrier %s --pcb-front %s' % (a.pcb_carrier, a.pcb_front),
           'exit_code': blocked, 'cond5_exit': rc5, 'cond5_fail': [(x['id'], x['title'], x['value']) for x in cond5.get('items', []) if x['pass'] is False],
           'steps': steps}
    if wip:   # O-107 WIP 사전 점검 — 판정·외함 기록(run.md · m010_run.json)은 건드리지 않음
        rec['command'] += ' --no-fusion'
        json.dump(rec, open(os.path.join(V, 'wip', 'm010_wip.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        for s in steps:
            print('-', s['step'], 'rc', s['rc'], '막힘' if s['blocked'] else '', '|', s['tail'][-300:].replace('\n', ' '))
        return sum(1 for s in steps if s['blocked'])
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
