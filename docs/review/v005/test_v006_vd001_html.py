# -*- coding: utf-8 -*-
"""v006_vd001_html.py 시험 — 가짜 입력(조건 결과·SIM·렌더·위험)으로 HTML 과 종료 코드를 본다. 사용: python -I test_v006_vd001_html.py [작업 폴더]"""
import sys, os, json, shutil, subprocess, tempfile

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
W = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='v006h_')
if os.path.isdir(W):
    shutil.rmtree(W)
VD = os.path.join(W, 'validation', 'runtime', 'vd001')
for d in ('results', 'render'):
    os.makedirs(os.path.join(VD, d))
os.makedirs(os.path.join(W, 'hardware', 'sim', 'results'))
os.makedirs(os.path.join(W, 'hardware', 'sim', 'png'))


def it(c, i, ok, v=True, board='carrier'):
    return dict(cond=c, id=i, board=board, title='항목 %s' % i, verifiable=v, value=0, limit=0, pass_=None, evidence=[{'label': 'x', 'path': 'commit:abcdef1234'}])


def dump(name, cond, items, rc):
    for x in items:
        x['pass'] = x.pop('pass_')
    json.dump(dict(cond=cond, owner='t', commit='abc12345', command='cmd', exit_code=rc, items=items), open(os.path.join(VD, 'results', name), 'w', encoding='utf-8'), ensure_ascii=False)


a = [it('1', '1.1', True)]; a[0]['pass_'] = True
dump('cond1-schematic.json', '1', a, 0)
b = [it('2', '2.A1', True), it('2', '2.A2', False), it('2', '2.H1', None, v=False)]
b[0]['pass_'] = True; b[1]['pass_'] = False
dump('cond2-review.json', '2', b, 1)
c1 = [it('3', '3.01', True)]; c1[0]['pass_'] = True
c2 = [it('3', '3.01', False, board='front')]; c2[0]['pass_'] = False
dump('cond3-review-carrier.json', '3', c1, 0)
dump('cond3-review-front.json', '3', c2, 1)
e = [it('5', '5.H', None, v=False)]
dump('cond5-mechanical.json', '5', e, 0)
open(os.path.join(W, 'hardware', 'sim', 'png', 'a.png'), 'wb').write(b'\x89PNG\r\n\x1a\n')
for sid, v in (('SIM-A1', 'pass'), ('SIM-B1', 'error')):
    json.dump(dict(id=sid, title=sid, owner='schematic', circuit={'board': 'carrier', 'refs': ['U1']}, model={'source': 'm', 'behavioral': True},
                   checks=[{'name': 'peak', 'op': 'between', 'limit': [0, 1.5], 'unit': 'A', 'value': 0.8, 'corner': 'worst', 'pass': True}],
                   verdict=v, waveforms=['hardware/sim/png/a.png'], tool={'name': 'ngspice', 'version': '45'}, notes='가정'),
              open(os.path.join(W, 'hardware', 'sim', 'results', sid + '.json'), 'w', encoding='utf-8'))
json.dump([{'kind': 'pcb-front', 'board': 'carrier', 'title': '앞', 'path': 'validation/runtime/vd001/render/a.png', 'sha256': '00', 'source': 'kicad-cli'},
           {'kind': 'turntable', 'title': '턴', 'path': 'validation/runtime/vd001/render/t.mp4', 'sha256': '11', 'source': 'blender'}],
          open(os.path.join(VD, 'render', 'manifest.json'), 'w', encoding='utf-8'))
json.dump([{'id': 'RISK-01', 'title': 'MDI 극성', 'source': 'D-003 #31', 'owner': 'firmware', 'bringup': 'F-005 7절', 'status': 'open'}],
          open(os.path.join(VD, 'risks.json'), 'w', encoding='utf-8'), ensure_ascii=False)
r = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v006_vd001_html.py'), '--root', W, '--vd', VD, '--sim', 'hardware/sim/results'],
                   capture_output=True, text=True, encoding='utf-8')
h = open(os.path.join(VD, 'index.html'), encoding='utf-8').read() if os.path.exists(os.path.join(VD, 'index.html')) else ''
CASES = [
    ('종료 코드 4 = 조건2 불합격 1 + 조건3 front 불합격 1 + 조건4 결과 없음 1 + SIM error 1', r.returncode == 4),
    ('조건 4 「결과 파일 없음」 표시', '결과 파일 없음' in h and 'cond4-*.json' in h),
    ('조건 3 보드 두 파일 합침(불합격 1)', h.count('cond3-review-') >= 2 and '불합격 1' in h),
    ('사람 확인 2건(조건 2·5) 모음 + 체크 상자', '사람 확인 모음 (verifiable 아니오 2건)' in h and h.count('data-k="c') == 2),
    ('SIM 2건, error 는 불합격 표시 · 파형 그림', 'SIM-B1' in h and '>error<' in h and 'a.png' in h),
    ('렌더 자리: 없는 kind 5개 「아직 없음」, mp4 는 video', h.count('아직 없음') == 5 and '<video' in h),
    ('남은 위험 표', 'RISK-01' in h and 'F-005 7절' in h),
    ('견적·비용 항목 없음', '견적' not in h.replace('견적·비용은 이 보고에 넣지 않는다', '') and '비용' not in h.replace('견적·비용은 이 보고에 넣지 않는다', '')),
    ('커밋 근거 표시', 'abcdef12' in h),
]
fail = 0
for n, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', n)); fail += 0 if ok else 1
if fail:
    print(r.stdout[-1500:], r.stderr[-1500:])
print('사례 %d · 실패 %d' % (len(CASES), fail))
sys.exit(1 if fail else 0)
