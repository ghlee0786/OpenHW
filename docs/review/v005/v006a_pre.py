# -*- coding: utf-8 -*-
"""V-006a(O-107): WIP 보드 사전 감수 — 배선과 무관한 항목만 모아 수정 요청 목록을 만든다.

사용: python -I v006a_pre.py <run_v005 결과 폴더> <pcb 커밋> <out.json> <out.md> [--snap <스냅샷>] [--root <저장소 루트>]
읽는 것: cond2.json(V-006 조건 2 집계) · drc_<b>.json · ev.json(R-020 ev_check) · models.json(REN-002 audit_models) · refs_<b>.json(v006a_refs)
        · <스냅샷>/hardware/pcb/route/<b>-silk-refs.json 의 refs_fab_only(pcb 가 기록한 「자리 없어 Fab 에만」 목록, O-65)
배선 무관 = 배치·실크·규칙 완화 기록·라이브러리 사본·열 비아·노출(절연) 패드·전원 트랙 폭/비아·3D 모델·참조 지정자.
배선이 끝나야 정해지는 것(미연결·간격·차동쌍 길이/결합·기준층 교차)은 세지 않는다.
종료 코드 = 수정 요청 수 (입력 오류 100)
"""
import sys, os, json, argparse, collections

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('res'); ap.add_argument('commit'); ap.add_argument('out'); ap.add_argument('md')
ap.add_argument('--snap', default=None); ap.add_argument('--root', default='.')
A = ap.parse_args()
SNAP = A.snap or os.path.join(A.res, 'snap')
BOARDS = ['carrier', 'front']
# cond2 항목 중 배선 무관 (v006_cond2.py id)
COND2_PRE = {'2.PAR', '2.RLX', '2.E2b', '2.E4', '2.A12', '2.A13', '2.A13g', '2.A13x', '2.TXT', '2.V1', '2.V2', '2.V3', '2.V4', '2.V5', '2.V6', '2.A14'}
# DRC 종류 중 배치·실크·라이브러리 (배선과 무관)
DRC_PRE = {'courtyards_overlap', 'malformed_courtyard', 'missing_courtyard', 'npth_inside_courtyard', 'pth_inside_courtyard',
           'silk_overlap', 'silk_over_copper', 'silk_edge_clearance', 'text_height', 'text_thickness', 'text_on_edge_cuts',
           'lib_footprint_issues', 'lib_footprint_mismatch', 'footprint_type_mismatch', 'footprint_filters_mismatch', 'footprint',
           'extra_footprint', 'missing_footprint', 'duplicate_footprints', 'net_conflict', 'item_on_disabled_layer', 'invalid_outline',
           'nonmirrored_text_on_back_layer', 'mirrored_text_on_front_layer', 'footprint_symbol_mismatch'}
req = []


def J(p):
    p = os.path.join(A.res, p) if not os.path.isabs(p) else p
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else None


def ev(name):
    p = os.path.join(A.res, name)
    return os.path.relpath(p, A.root).replace(os.sep, '/') if os.path.exists(p) else name


def add(area, board, what, detail, to, src):
    req.append(dict(n=len(req) + 1, area=area, board=board, what=what, detail=detail, to=to, evidence=ev(src)))


missing_inputs = []
c2 = J('cond2.json')
if c2 is None:
    missing_inputs.append('cond2.json')
else:
    for i in c2['items']:
        base = i['id'] if i['id'] in COND2_PRE else ('2.S' if i['id'].startswith('2.S') else None)
        if base and i['verifiable'] and i['pass'] is False:
            ev_ = i['evidence'][0]['label'] if i['evidence'] else 'cond2.json'
            add('조건2 ' + i['id'], i['board'], i['title'], '값 %s · 기준 %s%s' % (i['value'], i['limit'], (' · ' + i['note']) if i.get('note') else ''), 'pcb', ev_)
for b in BOARDS:
    d = J('drc_%s.json' % b)
    if d is None:
        missing_inputs.append('drc_%s.json' % b); continue
    cnt = collections.defaultdict(list)
    for v in d['violations']:
        if v['type'] in DRC_PRE:
            cnt[v['type']].append('; '.join(x.get('description', '') for x in v.get('items', []))[:160])
    for t, L in sorted(cnt.items()):
        add('DRC 배치', b, 'DRC %s %d건' % (t, len(L)), ' | '.join(L[:6]) + (' …' if len(L) > 6 else ''), 'pcb', 'drc_%s.json' % b)
e = J('ev.json')
if e is None:
    missing_inputs.append('ev.json')
else:
    for i in e['items']:
        if i['area'].startswith('③') and i['result'] == '불합격':
            add('전원(R-020)', i['target'].split(':')[0], '%s — %s' % (i['target'], i['metric']), '값 %s · 기준 %s' % (i['value'], i['limit']), 'pcb', 'ev.json')
m = J('models.json')
if m is None:
    missing_inputs.append('models.json')
else:
    for b in BOARDS:
        miss = [r for r in m['rows'] if r['board'] == b and r['missing']]
        if miss:
            add('3D 모델', b, '3D 모델 빠짐 %d (pcb 원본 기준, REN-002 audit_models)' % len(miss),
                ', '.join('%s %s(%s)' % (r['ref'], r['footprint'], r['state']) for r in miss), 'pcb(라이브러리 모델 연결) 또는 mechanical(apply_models 대체 표)', 'models.json')
counts = {}
for b in BOARDS:
    r = J('refs_%s.json' % b)
    if r is None:
        missing_inputs.append('refs_%s.json' % b); continue
    sr = os.path.join(SNAP, 'hardware', 'pcb', 'route', '%s-silk-refs.json' % b)
    fab_only = set(json.load(open(sr, encoding='utf-8')).get('refs_fab_only', [])) if os.path.exists(sr) else None
    counts[b] = dict(footprints=r['footprints'], need=r['need'], silk=r['silk'], fab=r['fab'], no_silk=len(r['no_silk']), no_fab=len(r['no_fab']),
                     fab_only_list=None if fab_only is None else len(fab_only))
    if r['no_fab']:
        add('참조 지정자', b, 'Fab(조립도)에 참조 지정자 없음 %d' % len(r['no_fab']), ', '.join(r['no_fab']), 'pcb', 'refs_%s.json' % b)
    if fab_only is None:
        add('참조 지정자', b, '실크에 없는 참조 %d 인데 「Fab 에만」 기록 목록 없음 (O-65)' % len(r['no_silk']), sr, 'pcb', 'refs_%s.json' % b)
    else:
        unrec = sorted(set(r['no_silk']) - fab_only)
        if unrec:
            add('참조 지정자', b, '실크에 없는데 「자리 없어 Fab 에만」 기록에도 없음 %d (O-65)' % len(unrec), ', '.join(unrec), 'pcb', 'refs_%s.json' % b)
        stale = sorted(x for x in fab_only - set(r['no_silk']) if any(rw['ref'] == x and rw['silk'] for rw in r['rows']))
        if stale:
            add('참조 지정자', b, '「Fab 에만」 기록인데 실크에 참조 있음 %d (기록 갱신)' % len(stale), ', '.join(stale), 'pcb', 'refs_%s.json' % b)
for x in missing_inputs:
    add('입력', '-', '결과 파일 없음: ' + x, '실행 로그 확인', 'review', x)

R = dict(task='V-006a', commit=A.commit, requests=req, ref_counts=counts, missing_inputs=missing_inputs, exit_code=len(req))
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
L = ['# V-006a 사전 감수 수정 요청 (pcb %s, 배선 무관 항목) — %d건' % (A.commit, len(req)), '',
     '| # | 분야 | 보드 | 요청 | 근거 값 | 받는 칸 | 근거 파일 |', '|---|---|---|---|---|---|---|']
for q in req:
    L.append('| %d | %s | %s | %s | %s | %s | `%s` |' % (q['n'], q['area'], q['board'], q['what'], q['detail'].replace('|', '/'), q['to'], q['evidence']))
L += ['', '## 참조 지정자 수 (실장 부품 기준)', '', '| 보드 | 풋프린트 | 실장 대상 | 실크 참조 | Fab 참조 | 실크 없음 | Fab 없음 | pcb 「Fab 에만」 기록 |', '|---|---|---|---|---|---|---|---|']
for b, c in counts.items():
    L.append('| %s | %d | %d | %d | %d | %d | %d | %s |' % (b, c['footprints'], c['need'], c['silk'], c['fab'], c['no_silk'], c['no_fab'], c['fab_only_list']))
open(A.md, 'w', encoding='utf-8', newline='\n').write('\n'.join(L) + '\n')
print('수정 요청 %d건 · 입력 없음 %d' % (len(req), len(missing_inputs)))
sys.exit(len(req))
