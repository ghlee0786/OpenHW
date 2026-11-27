# -*- coding: utf-8 -*-
"""D-003 #63 비결합 셈법 ②·비아 높이 계산 고장 주입 (v005_rules.py).

사용: KiCad python -I test_v006_unc.py <캐리어 보드.kicad_pcb> [작업 폴더]   종료 0 = 전부 통과
보드 사본에서 규칙 영역 이름만 바꿔(영역을 「없앤」 것과 같음) 판정기가 그 영역에만 반응하는지 본다. 입력 보드는 고치지 않는다.
  A 원본                         : ② 값 ≤ ① 값, 영역 표의 「영역 덕에 결합으로 센 길이」 합 = ① − ②
  B DP_BRK · DP_TUNE 이름 바꿈   : ② 값 = ① 값 (탈출·보정 영역이 없으면 봐주는 것이 없다), 영역 표 비어 있음
  C DP_TWIST 이름 바꿈           : 꼬임 예외로 빼던 비아 높이가 그대로 판정에 들어온다 (뺀 높이 0, 넷별 합은 보존)
"""
import sys, os, json, shutil, subprocess, tempfile
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
W = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix='v006u_')
if os.path.isdir(W):
    shutil.rmtree(W)
os.makedirs(W)


def run(tag, rename):
    b = pcbnew.LoadBoard(SRC)
    for z in b.Zones():
        if z.GetIsRuleArea() and z.GetZoneName() in rename:
            z.SetZoneName('X_' + z.GetZoneName())
    pcb = os.path.join(W, tag + '.kicad_pcb')
    pcbnew.SaveBoard(pcb, b)
    out = os.path.join(W, tag + '.json')
    rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v005_rules.py'), pcb, out], capture_output=True, text=True, encoding='utf-8')
    if rc.returncode != 0:
        print('v005_rules.py 실패', tag, rc.stderr[-2000:]); sys.exit(1)
    return json.load(open(out, encoding='utf-8'))


A, B, C = run('a', ()), run('b', ('DP_BRK', 'DP_TUNE')), run('c', ('DP_TWIST',))


def strict(p):   # ① 꼬임 밖 (MDI) 또는 전체 (그 밖)
    if 'uncoupled_outside_twist' in p:
        return p['uncoupled_outside_twist']
    return {'P': p['strict_0.18']['uncoupledP'], 'N': p['strict_0.18']['uncoupledN']}


def near(x, y, tol=0.06):
    return abs(x - y) <= tol


def vsum(p, side):
    return p['via'][side]['h'] + p['via'][side]['twist_excluded']


CASES = []
for k, p in A['pairs'].items():
    s, ar = strict(p), p['uncoupled_area_rule']
    extra = {x: sum(r['pairs'][k]['extra' + x] for r in A['area_table'] if k in r['pairs']) for x in 'PN'}
    CASES.append(('A %s: ② ≤ ① (P %g ≤ %g, N %g ≤ %g)' % (k, ar['P'], s['P'], ar['N'], s['N']), ar['P'] <= s['P'] + 1e-6 and ar['N'] <= s['N'] + 1e-6))
    CASES.append(('A %s: ① − ② ≤ 영역 표의 「결합으로 센 길이」 합 (P %g ≤ %g, N %g ≤ %g)' % (k, round(s['P'] - ar['P'], 3), extra['P'], round(s['N'] - ar['N'], 3), extra['N']),
                  s['P'] - ar['P'] <= extra['P'] + 0.06 and s['N'] - ar['N'] <= extra['N'] + 0.06))
    pb = B['pairs'][k]; sb, arb = strict(pb), pb['uncoupled_area_rule']
    CASES.append(('B %s: 탈출·보정 영역이 없으면 ② = ① (P %g = %g, N %g = %g)' % (k, arb['P'], sb['P'], arb['N'], sb['N']), near(arb['P'], sb['P']) and near(arb['N'], sb['N'])))
    pc = C['pairs'][k]
    CASES.append(('C %s: 꼬임 영역이 없으면 뺀 비아 높이 0, 넷별 높이 합 보존' % k,
                  pc['via']['P']['twist_excluded'] == 0 and pc['via']['N']['twist_excluded'] == 0 and near(vsum(pc, 'P'), vsum(p, 'P'), 1e-3) and near(vsum(pc, 'N'), vsum(p, 'N'), 1e-3)))
CASES.append(('A: 탈출·보정 영역 덕에 줄어든 쌍이 하나 이상 (영역이 실제로 쓰이는 보드)', any(strict(p)['P'] - p['uncoupled_area_rule']['P'] > 0.5 for p in A['pairs'].values())))
CASES.append(('B: 영역 표가 비어 있음', B['area_table'] == []))
tw = [k for k, p in A['pairs'].items() if p['via']['P']['twist_excluded'] + p['via']['N']['twist_excluded'] > 0]
CASES.append(('A: 꼬임 예외로 뺀 비아가 있는 쌍이 있음 (%s)' % ', '.join(tw), bool(tw)))
CASES.append(('C: 그 쌍은 꼬임 영역이 없으면 +비아 길이 차가 달라짐(예외가 판정을 바꾼다)', bool(tw) and all(
    not near(C['pairs'][k]['via']['diff_with_via'], A['pairs'][k]['via']['diff_with_via'], 1e-3) for k in tw)))
fail = 0
for n, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', n)); fail += 0 if ok else 1
print('사례 %d · 실패 %d · 폴더 %s' % (len(CASES), fail, W))
sys.exit(1 if fail else 0)
