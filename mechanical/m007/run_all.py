"""M-007 한 명령: pcb 커밋 → 보드 STEP(kicad-cli) → Fusion 조립(02) → 판정(03) → judge.md. 종료 코드 = 실패 수.
사용: python -I -B mechanical/m007/run_all.py [--pcb <커밋>] [--pcb-carrier <커밋>] [--pcb-front <커밋>] [--skip-build]
  --pcb: pcb 레인 커밋 (기본 HEAD), --pcb-carrier/--pcb-front 로 보드마다 따로 (M-010).
  보드 사본(git archive) 에 REN-002 apply_models 로 3D 모델을 연결한 뒤 kicad-cli STEP (--subst-models, --user-origin 100x100mm = 코어 중심).
  산출물은 main 체크아웃 validation/runtime/vd001/ (O-100). Fusion 스크립트는 mechanical/fusion_run.py 로 (LANE = 이 체크아웃)."""
import argparse, hashlib, json, os, subprocess, sys, tarfile, io, shutil

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
LANE = os.path.abspath(os.path.join(HERE, '..', '..'))
MAIN = os.path.abspath(os.environ.get('OPENHW_MAIN') or os.path.dirname(subprocess.run(['git', '-C', os.path.dirname(os.path.abspath(__file__)), 'rev-parse', '--path-format=absolute', '--git-common-dir'], capture_output=True, text=True).stdout.strip()))   # main 체크아웃 — 산출물 validation/runtime (O-100)
OUT = os.path.join(MAIN, 'validation', 'runtime', 'vd001')
PCB_LANE = MAIN   # pcb 커밋은 같은 저장소(pcb 레인 브랜치) — 레인 worktree 가 없어져도 커밋으로 읽힘
KICAD = os.path.join(os.environ['LOCALAPPDATA'], 'Programs', 'KiCad', '10.0', 'bin', 'kicad-cli.exe')
FRUN = os.path.join(HERE, '..', 'fusion_run.py')


def sh(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace', **kw)
    return r.returncode, r.stdout + r.stderr


def write_cond5(res, mm, hs):
    """VD-001 조건 5 결과 파일 (docs/review/vd001-format.md §1 형식). 반환 = 불합격 수 (3D 모델 빠짐 보드 + 03_judge 실패)."""
    import datetime
    ev = [{'label': 'm007_judge.json', 'path': 'validation/runtime/vd001/m007_judge.json'}, {'label': 'judge.md', 'path': 'mechanical/m007/judge.md'}]
    it = []
    for b in ('carrier', 'front'):
        m = mm['missing'].get(b, [])
        it.append({'cond': '5', 'id': '5.M-' + b, 'board': b, 'title': '3D 모델 빠짐 (kicad-cli STEP 내보내기)', 'verifiable': True,
                   'value': len(m), 'limit': 0, 'pass': not m,
                   'evidence': [{'label': 'models_missing.json', 'path': 'validation/runtime/vd001/boards/models_missing.json'}],
                   'note': (' '.join(m) + ' — 대체 모델 mechanical/models/*.step 연결 전 (pcb)') if m else ''})
    for k, x in enumerate(res['J1']['fail']):
        it.append({'cond': '5', 'id': '5.J1-%d' % (k + 1), 'board': '-', 'title': '조립 간섭 %s ↔ %s' % (x['a'], x['b']), 'verifiable': True,
                   'value': x['mm3'], 'limit': 0, 'pass': False, 'evidence': ev, 'note': '위치 x/y/z %s' % x['at']})
    if not res['J1']['fail']:
        it.append({'cond': '5', 'id': '5.J1', 'board': '-', 'title': '조립 간섭 (의도 %d건 제외)' % len(res['J1']['intended']), 'verifiable': True,
                   'value': 0, 'limit': 0, 'pass': True, 'evidence': ev})
    for k, x in enumerate(res['J2']):
        it.append({'cond': '5', 'id': '5.J2-%d' % (k + 1), 'board': '-', 'title': '최소 틈 %s ↔ %s' % (x['a'], x['b']), 'verifiable': True,
                   'value': x['min_mm'], 'limit': '>= %s' % x['need'], 'pass': x['ok'], 'evidence': ev})
    j4, j5, j6 = res['J4'], res['J5'], res['J6']
    it.append({'cond': '5', 'id': '5.J3', 'board': '-', 'title': '플러그·카드 삽입 공간 (블록 간섭 수)', 'verifiable': True, 'value': len(res['J3']),
               'limit': 0, 'pass': not res['J3'], 'evidence': ev, 'note': '5.J1 플러그·카드 블록 간섭을 삽입 관점으로 다시 센 것'})
    it.append({'cond': '5', 'id': '5.J4', 'board': '-', 'title': '광축 ↔ 렌즈 창 중심 어긋남 mm', 'verifiable': True, 'value': j4['offset_mm'],
               'limit': '<= 0.1', 'pass': j4['ok'], 'evidence': ev})
    it.append({'cond': '5', 'id': '5.J5', 'board': '-', 'title': 'LED A+B 직접광 방향 %% (시야 %d×%d)' % tuple(j5['grid']), 'verifiable': True,
               'value': j5['coverage_A_B'], 'limit': '>= 84 (analysis2 86)', 'pass': j5['ok'],
               'evidence': ev + [{'label': '개선안 비교', 'path': 'mechanical/m007/led_study.md'}]})
    it.append({'cond': '5', 'id': '5.J6', 'board': '-', 'title': '짝 BTB 결합 높이 mm', 'verifiable': True, 'value': j6['core_to_carrier_top'],
               'limit': j6['expected'], 'pass': j6['ok'], 'evidence': ev, 'note': j6['note']})
    n = sum(1 for x in it if x['pass'] is False)   # VD-001 생성기와 같은 셈 (pass false 항목 수, 5.J3 은 5.J1 플러그 간섭을 다시 셈)
    out = {'cond': '5', 'owner': 'mechanical', 'title': '3D 모델 빠짐 0 · 조립 간섭 0 · 최소 틈 · 플러그 삽입 · 광축 · LED 가림 · BTB 높이',
           'commit': mm['pcb'], 'generated': datetime.datetime.now().isoformat(timespec='seconds'),
           'command': mm.get('command', 'python -I -B mechanical/m007/run_all.py --pcb %s' % mm['pcb']), 'exit_code': n, 'items': it, 'inputs_sha256': hs}
    os.makedirs(os.path.join(OUT, 'results'), exist_ok=True)
    json.dump(out, open(os.path.join(OUT, 'results', 'cond5-mechanical.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pcb', default='HEAD')   # 결과 파일·judge.md 에 실제 커밋 해시를 적는다
    ap.add_argument('--pcb-carrier'); ap.add_argument('--pcb-front')
    ap.add_argument('--pcb-lane', default=PCB_LANE)
    ap.add_argument('--skip-build', action='store_true')
    ap.add_argument('--case', default='M003', choices=['M003', 'A'], help='O-126: A = 시안 A 케이스(case/A/A.step) 로 조립·판정')
    ap.add_argument('--no-fusion', action='store_true', help='O-107: 보드 사본·모델 감사·STEP·커넥터까지만 (Fusion 조립·판정·judge.md·조건 5 결과 파일 안 씀)')
    a = ap.parse_args()
    os.makedirs(os.path.join(OUT, 'boards'), exist_ok=True)
    log = []
    missing = {}
    import re
    if not a.skip_build:
        commits = {}
        aud = {}
        for b in ('carrier', 'front'):
            want = getattr(a, 'pcb_' + b) or a.pcb
            rc, c = sh(['git', '-C', a.pcb_lane, 'rev-parse', '--short', want])
            commits[b] = c.strip()
            if rc:
                print(c); return 99
            # 보드마다 그 커밋의 hardware/ 사본 + 모델 폴더 (${KIPRJMOD}/../../../mechanical/models 가 사본 안에서 풀리게)
            bs = os.path.join(OUT, 'pcbsrc', b)
            shutil.rmtree(bs, ignore_errors=True)
            data = subprocess.run(['git', '-C', a.pcb_lane, 'archive', want, 'hardware'], capture_output=True).stdout
            tarfile.open(fileobj=io.BytesIO(data)).extractall(bs)
            shutil.copytree(os.path.join(LANE, 'mechanical', 'models'), os.path.join(bs, 'mechanical', 'models'))
            # 3D 모델 빠짐(조건 5)은 pcb 원본으로 센다 — kicad-cli 는 모델 속성이 아예 없는 풋프린트를 경고하지 않으므로 REN-002 전수 감사
            aj = os.path.join(OUT, 'boards', 'model_audit_%s.json' % b)
            sh([sys.executable, '-I', '-B', os.path.join(HERE, '..', 'ren002', 'audit_models.py'), '--src', bs, '--out-json', aj, '--no-md'])
            missing[b] = sorted(r['ref'] for r in json.load(open(aj, encoding='utf-8'))['rows'] if r['board'] == b and r['missing'])
            pcbf = os.path.join(bs, 'hardware', 'schematic', b, b + '.kicad_pcb')
            rc, o = sh([sys.executable, '-I', '-B', os.path.join(HERE, '..', 'ren002', 'apply_models.py'), pcbf])
            log.append('%s pcb %s: 원본 3D 모델 빠짐 %d · apply_models 사본 %s' % (b, commits[b], len(missing[b]), ' '.join(o.split())))
            aj2 = os.path.join(OUT, 'boards', 'model_audit_%s_applied.json' % b)
            sh([sys.executable, '-I', '-B', os.path.join(HERE, '..', 'ren002', 'audit_models.py'), '--src', bs, '--out-json', aj2, '--no-md'])
            aud[b] = sorted(r['ref'] for r in json.load(open(aj2, encoding='utf-8'))['rows'] if r['board'] == b and r['missing'])
            rc, o = sh([KICAD, 'pcb', 'export', 'step', '--subst-models', '--user-origin', '100x100mm', '-f', '-o',
                        os.path.join(OUT, 'boards', b + '.step'), pcbf])
            miss = sorted(set(re.findall(r'Could not add 3D model for (\S+?)\.', o)))
            log.append('kicad-cli %s rc %d (사본 감사 빠짐 %d %s, kicad-cli 경고 %d %s)' % (b, rc, len(aud[b]), ' '.join(aud[b]), len(miss), ' '.join(miss)))
            if rc:
                print(o); return 99
        commit = commits['carrier'] if commits['carrier'] == commits['front'] else 'carrier %s · front %s' % (commits['carrier'], commits['front'])
        cmd = 'python -I -B mechanical/m007/run_all.py ' + ('--pcb %s' % commits['carrier'] if commits['carrier'] == commits['front']
                                                            else '--pcb-carrier %s --pcb-front %s' % (commits['carrier'], commits['front']))
        cmd += ' --case A' if a.case == 'A' else ''
        log.append('pcb commit ' + commit)
        json.dump({'pcb': commit, 'command': cmd, 'missing': missing, 'missing_after_apply': aud},
                  open(os.path.join(OUT, 'boards', 'models_missing.json'), 'w', encoding='utf-8'), indent=1)
        src = os.path.join(OUT, 'pcbsrc', 'carrier')
        # 캐리어 커넥터 fab 외곽 → 외함 개구·대체 블록 위치 (M-003 params 값을 덮어씀)
        import math, re
        t = open(os.path.join(src, 'hardware', 'schematic', 'carrier', 'carrier.kicad_pcb'), encoding='utf-8').read()
        conn = {}
        for ref, kx, ky in (('J5', 'rj_x', 'rj_y'), ('J2', 'dc_x', 'dc_y'), ('J3', 'usb_x', 'usb_y'), ('J4', 'sd_x', 'sd_y')):
            i = t.find('(property "Reference" "%s"' % ref); s0 = t.rfind('(footprint', 0, i); e0 = t.find('\n\t(footprint', i)
            blk = t[s0:e0]
            at = re.search(r'\n\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)', blk); X0, Y0 = float(at.group(1)), float(at.group(2)); th = math.radians(float(at.group(3) or 0))
            xs, ys = [], []
            for m in re.finditer(r'\n\t\t\((fp_line|fp_rect|fp_poly)(.*?)\n\t\t\)', blk, re.S):
                if '(layer "B.Fab")' not in m.group(2) and '(layer "F.Fab")' not in m.group(2):
                    continue
                for x, y in re.findall(r'\((?:start|end|xy) ([-\d.]+) ([-\d.]+)\)', m.group(2)):
                    x, y = float(x), float(y)
                    xs.append(X0 + x * math.cos(th) + y * math.sin(th) - 100.0); ys.append(-(Y0 - x * math.sin(th) + y * math.cos(th) - 100.0))
            conn[kx] = [round(min(xs), 3), round(max(xs), 3)]; conn[ky] = [round(min(ys), 3), round(max(ys), 3)]
        conn['sd_y'] = [conn['sd_y'][0], 19.6]          # DM3AT 몸체 앞면 (모델 측정, M-003) — fab 는 카드 튀어나온 자리까지 그림
        conn['sd_front'] = [19.6]
        json.dump(conn, open(os.path.join(OUT, 'boards', 'connectors.json'), 'w', encoding='utf-8'), indent=1)
        log.append('커넥터 (pcb fab): ' + json.dumps(conn))
        if a.no_fusion:
            print('\n'.join(log)); return 0
        rc, o = sh([sys.executable, '-I', '-B', FRUN, os.path.join(HERE, 'scripts', '02_assembly.py'), '--set', 'CASE=' + a.case]); log.append('02_assembly rc %d %s' % (rc, o.strip()[-300:]))
        if rc:
            print('\n'.join(log)); return 98
    rc, o = sh([sys.executable, '-I', '-B', FRUN, os.path.join(HERE, 'scripts', '03_judge.py')]); log.append('03_judge rc %d %s' % (rc, o.strip()[-200:]))
    if rc:
        print('\n'.join(log)); return 97
    res = json.load(open(os.path.join(OUT, 'm007_judge.json'), encoding='utf-8'))
    L = ['# M-007 기계 판정 (run_all.py 출력 — 종료 코드 = 실패 수 %d)' % res['fail'], '']
    L += ['- ' + x for x in log] + ['']
    L += ['- 판정에서 뺀 대체 블록 (그 보드 3D 모델 연결 사본 감사 빠짐 0 — asm_spec.SUBST_BLOCKS): %s' % (' '.join(res.get('dropped_blocks', [])) or '없음'), '']
    L += ['## J1 바디 쌍 간섭 (바디 %d개)' % res['J1']['bodies'], '', '| 쌍 | 부피 mm³ | 위치 x/y/z | 판정 |', '|---|---|---|---|']
    for x in res['J1']['fail']:
        L.append('| %s ↔ %s | %.3f | %s | **실패** |' % (x['a'], x['b'], x['mm3'], x['at']))
    for x in res['J1']['intended']:
        L.append('| %s ↔ %s | %.3f | %s | 의도 — %s |' % (x['a'], x['b'], x['mm3'], x['at'], x['why']))
    L += ['', '## J2 최소 틈', '', '| 쌍 | 최소 틈 mm | 기준 | 판정 |', '|---|---|---|---|']
    for x in res['J2']:
        L.append('| %s ↔ %s | %s | ≥ %s | %s |' % (x['a'], x['b'], x['min_mm'], x['need'], '통과' if x['ok'] else '**실패**'))
    L += ['', '## J3 플러그·카드 삽입 공간', '', '- 플러그/카드 블록이 낀 실패 간섭: %d건' % len(res['J3'])]
    j4 = res['J4']; L += ['', '## J4 광축 ↔ 렌즈 창 중심', '', '- 렌즈 %s · 창 %s · 어긋남 %.3f mm → %s' % (j4['lens_xy'], j4['window_xy'], j4['offset_mm'], '통과' if j4['ok'] else '**실패**')]
    j5 = res['J5']; L += ['', '## J5 LED 직접광 (광선 추적, LED A+B, 시야 %d × %d 방향)' % tuple(j5['grid']), '',
                          '- 직접광이 닿는 방향 %.1f %% (기준 86 %%, analysis2 · O-69) → %s' % (j5['coverage_A_B'], '통과' if j5['ok'] else '**실패**'),
                          '- 막은 바디(LED·방향 수): %s' % j5['blockers']]
    j6 = res['J6']; L += ['', '## J6 짝 BTB 결합 높이', '', '- 코어 ↔ 캐리어 윗면 %.3f · 전면 아랫면 ↔ 코어 윗면 %.3f (기대 8.0) → %s · %s' % (
        j6['core_to_carrier_top'], j6['front_bottom_to_core_top'], '통과' if j6['ok'] else '**실패**', j6['note'])]
    hs = {}
    for f in ('m007_assembly.step', 'boards/carrier.step', 'boards/front.step'):
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            hs[f] = hashlib.sha256(open(p, 'rb').read()).hexdigest()
    L += ['', '## 입력·산출 해시', ''] + ['- %s %s' % (k, v) for k, v in hs.items()]
    mm = json.load(open(os.path.join(OUT, 'boards', 'models_missing.json'), encoding='utf-8'))
    n_fail = write_cond5(res, mm, hs)
    L[0] = '# M-007 기계 판정 = VD-001 조건 5 (run_all.py 출력 — 종료 코드 = 불합격 항목 수 %d: 03_judge 실패 %d + 3D 모델 빠짐 보드 %d + J3 삽입 %d)' % (n_fail, res['fail'], sum(1 for b in mm['missing'].values() if b), len(res['J3']) > 0)
    L.insert(2, '- 결과 파일 validation/runtime/vd001/results/cond5-mechanical.json (docs/review/vd001-format.md §1)')
    open(os.path.join(HERE, 'judge.md'), 'w', encoding='utf-8').write('\n'.join(L) + '\n')
    print('\n'.join(L))
    return n_fail


if __name__ == '__main__':
    sys.exit(main())
