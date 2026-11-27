# -*- coding: utf-8 -*-
"""v006_relax.py 고장 주입 시험 (표준 라이브러리). 합성 .kicad_dru·.kicad_pro·D-003 으로 판정이 맞는지 본다.
사용: python -I test_v006_relax.py [작업 폴더]   종료 0 = 전부 통과
"""
import sys, os, json, subprocess, tempfile, shutil

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
W = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='v006r_')
if os.path.isdir(W):
    shutil.rmtree(W)
os.makedirs(W)

DRU = '''(version 1)
# 주석 줄 (rule "commented" (constraint clearance (min 0.01mm)))
(rule "fab_copper_clearance"
  (constraint clearance (min 0.16mm)))
(rule "csi_100_pair"
  (condition "A.hasNetclass('CSI_100')")
  (constraint track_width (min 0.15mm) (opt 0.15mm) (max 0.16mm))
  (constraint diff_pair_gap (min 0.15mm) (opt 0.16mm) (max 0.18mm))
  (constraint diff_pair_uncoupled (max 4mm)))
(rule "mdi_100_pair"
  (condition "A.hasNetclass('MDI_100')")
  (constraint diff_pair_uncoupled (max 7mm)))
(rule "hs_track_spacing"
  (condition "A.hasNetclass('CSI_100') && A.Type == 'Track'")
  (constraint clearance (min 0.30mm)))
(rule "new_area_exception"
  (condition "A.hasNetclass('CSI_100') && A.intersectsArea('NEW_ZONE')")
  (constraint clearance (min 0.16mm)))
(rule "twist"
  (condition "A.hasNetclass('MDI_100') && A.enclosedByArea('DP_TWIST')")
  (constraint diff_pair_uncoupled (max 20mm)))
(rule "thin_track"
  (constraint track_width (min 0.10mm)))
(rule "quiet"
  (layer "?.Silkscreen")
  (severity ignore)
  (constraint silk_clearance (min 0.15mm)))
'''
PRO = {'board': {'design_settings': {'rules': {'min_clearance': 0.12, 'min_track_width': 0.15},
                                     'rule_severities': {'silk_overlap': 'ignore', 'clearance': 'error', 'track_dangling': 'warning'}}}}
D3 = '''| # | 항목 | 기본값 | 이유 | 차선 |
|---|---|---|---|---|
| 28 | 차동쌍 비결합 길이 한도 | CSI 3→4mm · MDI 5→6mm · USB 5→12mm로 완화 | 근거 | 차선 |
| 31 | 꼬임 | PCB에서 ESD→RJ45 구간만 교차 — 그 구간 한정 규칙 예외 | 근거 | 차선 |
| 40 | ignore | silk_overlap ignore 기록 | 근거 | 차선 |
'''
REC = json.load(open(os.path.join(HERE, 'relax-records.json'), encoding='utf-8'))
REC['records'].append({'match': {'key': 'ignore:silk_overlap'}, 'd003': 40, 'must_contain': ['silk_overlap ignore']})
for n, t in (('t.kicad_dru', DRU), ('d003.md', D3)):
    open(os.path.join(W, n), 'w', encoding='utf-8').write(t)
json.dump(PRO, open(os.path.join(W, 't.kicad_pro'), 'w', encoding='utf-8'))
json.dump(REC, open(os.path.join(W, 'rec.json'), 'w', encoding='utf-8'), ensure_ascii=False)
out = os.path.join(W, 'relax.json')
rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v006_relax.py'), os.path.join(W, 't.kicad_pcb'), out,
                     '--d003', os.path.join(W, 'd003.md'), '--records', os.path.join(W, 'rec.json')], capture_output=True, text=True, encoding='utf-8')
R = json.load(open(out, encoding='utf-8'))
by = {r['key']: r for r in R['relaxations']}


def st(k):
    return by.get(k, {}).get('status')


CASES = [
    ('CSI 비결합 4 = D-003 「CSI 3→4mm」 기록 일치(음성)', st('rule:csi_100_pair:diff_pair_uncoupled') == '기록 일치'),
    ('MDI 비결합 7 ≠ D-003 「MDI 5→6mm」 → 문구 불일치(양성)', st('rule:mdi_100_pair:diff_pair_uncoupled') == '기록 문구 불일치'),
    ('기록 없는 영역 예외 NEW_ZONE(양성)', st('rule:new_area_exception:clearance') == '기록 없음' and by['rule:new_area_exception:clearance']['kind'] == 'D3'),
    ('DP_TWIST 예외 #31 기록 일치(음성)', st('rule:twist:diff_pair_uncoupled') == '기록 일치'),
    ('전역 트랙 0.10 < 0.15(양성 D1)', st('rule:thin_track:track_width') == '기록 없음'),
    ('severity ignore 규칙(양성 D4)', st('severity:quiet') == '기록 없음'),
    ('.kicad_pro min_clearance 0.12(양성 P1)', st('pro:min_clearance') == '기록 없음'),
    ('ignore silk_overlap + 기록 #40(음성)', st('ignore:silk_overlap') == '기록 일치'),
    ('warning 심각도는 완화 아님(음성)', 'ignore:track_dangling' not in by),
    ('더 엄격한 규칙(hs 0.30·fab 0.16·CSI 선폭 0.15)은 완화 아님(음성)',
     not any(k in by for k in ('rule:hs_track_spacing:clearance', 'rule:fab_copper_clearance:clearance', 'rule:csi_100_pair:track_width'))),
    ('주석 처리된 규칙 무시(음성)', not any('commented' in k for k in by)),
    ('종료 코드 = 불합격 수(5: P1·MDI 문구·NEW_ZONE·선폭 0.10·severity)', rc.returncode == R['fail'] == 5),
]
# ---- O-114 / D-003 #60: J1 탈출 비아 0.50/0.20 (enclosedByArea J1_*) ----
DRU2 = '''(version 1)
(rule "fab_via_diameter" (constraint via_diameter (min 0.60mm)))
(rule "fab_min_drill" (constraint hole_size (min 0.30mm)))
(rule "j1_esc_via"
  (condition "A.Type == 'Via' && A.enclosedByArea('J1_ESC')")
  (constraint via_diameter (min 0.50mm))
  (constraint hole_size (min 0.20mm))
  (constraint annular_width (min 0.15mm)))
(rule "j1_bad_inter"
  (condition "A.Type == 'Via' && A.intersectsArea('J1_ESC')")
  (constraint via_diameter (min 0.50mm)))
(rule "j1_small"
  (condition "A.Type == 'Via' && A.enclosedByArea('J1_ESC2')")
  (constraint via_diameter (min 0.45mm)))
(rule "j1_h2h"
  (condition "A.enclosedByArea('J1_ESC')")
  (constraint hole_to_hole (min 0.28mm)))
'''
D3b = D3 + '| 60 | J1 탈출 비아 | J1 탈출 비아만 0.50/0.20(링 0.15)을 J1 둘레 규칙 영역(enclosedByArea) 안에서 허용 | 근거 | 차선 |\n'
W2 = os.path.join(W, 'esc'); os.makedirs(W2)
open(os.path.join(W2, 't.kicad_dru'), 'w', encoding='utf-8').write(DRU2)
open(os.path.join(W2, 'd003.md'), 'w', encoding='utf-8').write(D3b)
json.dump({'board': {'design_settings': {}}}, open(os.path.join(W2, 't.kicad_pro'), 'w', encoding='utf-8'))
out2 = os.path.join(W2, 'relax.json')
rc2 = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v006_relax.py'), os.path.join(W2, 't.kicad_pcb'), out2,
                      '--d003', os.path.join(W2, 'd003.md')], capture_output=True, text=True, encoding='utf-8')
R2 = json.load(open(out2, encoding='utf-8'))
by2 = {r['key']: r for r in R2['relaxations']}


def st2(k):
    return by2.get(k, {}).get('status')


CASES += [
    ('#60 J1 탈출 비아 지름 0.50 · 드릴 0.20 (enclosedByArea) 기록 일치(음성)', st2('rule:j1_esc_via:via_diameter') == '기록 일치' and st2('rule:j1_esc_via:hole_size') == '기록 일치'),
    ('#60 링 0.15 는 기준과 같아 완화 아님(음성)', 'rule:j1_esc_via:annular_width' not in by2),
    ('#60 intersectsArea 로 쓴 같은 완화 → 기록 없음(양성)', st2('rule:j1_bad_inter:via_diameter') == '기록 없음'),
    ('#60 지름 0.45 는 기록 값 0.50 과 다름 → 문구 불일치(양성)', st2('rule:j1_small:via_diameter') == '기록 문구 불일치'
     and any('보드 값 0.45' in x for x in by2['rule:j1_small:via_diameter']['missing_text'])),
    ('#60 구멍 간격 0.28 은 D-003 에 값 없음 → 문구 불일치(양성)', st2('rule:j1_h2h:hole_to_hole') == '기록 문구 불일치'),
    ('#60 종료 코드 = 불합격 3', rc2.returncode == R2['fail'] == 3),
]
fail = 0
for n, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', n)); fail += 0 if ok else 1
if fail:
    print(rc.stdout[-3000:]); print(rc2.stdout[-3000:], rc2.stderr[-1500:])
print('사례 %d · 실패 %d' % (len(CASES), fail))
sys.exit(1 if fail else 0)
