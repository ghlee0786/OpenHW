# -*- coding: utf-8 -*-
"""V-006 (VD-001 조건 2-①): 보드 규칙 완화·ignore 를 전부 뽑아 D-003 기록과 대조한다. 표준 라이브러리만 쓴다.

사용: python -I v006_relax.py <board.kicad_pcb> <out.json> --d003 <D-003 md> [--records relax-records.json] [--dru D] [--pro P]
종료 코드 = 불합격 수(기록 없는 완화 + 기록 문구 불일치). 입력 오류는 100.

완화로 보는 것 (기준값은 relax-records.json 의 baseline · original_limits):
  P1 .kicad_pro rules 최소값이 기준(P-001 제조 기준)보다 작다 (min_clearance 등)
  P2 .kicad_pro rule_severities 가 ignore
  D1 .kicad_dru 규칙의 min 제약이 기준보다 작다 (clearance·track_width·hole_size·annular_width·via_diameter·edge_clearance·
     hole_to_hole·silk_clearance·text_height·text_thickness)
  D2 .kicad_dru 규칙의 max 제약이 원래 한도보다 크다 (diff_pair_uncoupled = D-003 #28 이전 값, diff_pair_gap = 쌍 간격 상한, skew)
  D3 조건이 영역·부품에 묶인 규칙(intersectsArea·enclosedByArea·insideArea·memberOfFootprint)은 제약이 기준보다 느슨하거나
     같은 넷클래스의 영역 밖 규칙보다 느슨하면 「영역 예외」
  D4 (severity ignore|exclusion) 규칙
대조: relax-records.json 의 records — 완화 키(rule·constraint 또는 area 또는 severity)마다 D-003 행 번호와 그 행에 있어야 할 문구.
  문구의 {value} 는 지금 보드의 값으로 바꿔 찾는다(값이 바뀌면 D-003 도 바뀌어야 통과).
"""
import sys, os, re, json, argparse

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('pcb'); ap.add_argument('out')
ap.add_argument('--d003', required=True)
ap.add_argument('--records', default=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'relax-records.json'))
ap.add_argument('--dru'); ap.add_argument('--pro')
A = ap.parse_args()
base = os.path.splitext(A.pcb)[0]
DRU, PRO = A.dru or base + '.kicad_dru', A.pro or base + '.kicad_pro'
for f in (A.d003, A.records):
    if not os.path.exists(f):
        print('입력 없음', f); sys.exit(100)
REC = json.load(open(A.records, encoding='utf-8'))
BASE, ORIG = REC['baseline'], REC['original_limits']


# ---------- s-식 ----------
def sexp(t):
    toks = re.findall(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+', t)
    st = [[]]
    for k in toks:
        if k == '(':
            st.append([])
        elif k == ')':
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(k[1:-1] if k.startswith('"') else k)
    return st[0]


def num(v):
    m = re.fullmatch(r'([-\d.]+)(mm|mil)?', str(v))
    if not m:
        return None
    x = float(m.group(1))
    return x * 0.0254 if m.group(2) == 'mil' else x


def fmt(x):
    return ('%.3f' % x).rstrip('0').rstrip('.')


rules = []
if os.path.exists(DRU):
    txt = '\n'.join(l for l in open(DRU, encoding='utf-8').read().splitlines() if not l.lstrip().startswith('#'))
    for node in sexp(txt):
        if not (isinstance(node, list) and node and node[0] == 'rule'):
            continue
        r = dict(name=node[1], condition='', layer=None, constraints=[], severity=None)
        for it in node[2:]:
            if not isinstance(it, list) or not it:
                continue
            if it[0] == 'condition':
                r['condition'] = it[1]
            elif it[0] == 'layer':
                r['layer'] = it[1]
            elif it[0] == 'severity':
                r['severity'] = it[1]
            elif it[0] == 'constraint':
                c = dict(type=it[1])
                for kv in it[2:]:
                    if isinstance(kv, list) and kv and kv[0] in ('min', 'opt', 'max'):
                        c[kv[0]] = num(kv[1])
                    elif isinstance(kv, str):
                        c.setdefault('args', []).append(kv)
                r['constraints'].append(c)
        rules.append(r)

AREA_RE = re.compile(r"(intersectsArea|enclosedByArea|insideArea|memberOfFootprint)\('([^']+)'\)")
NC_RE = re.compile(r"hasNetclass\('([^']+)'\)")
relax = []


def add(kind, key, detail, value=None, rule=None):
    relax.append(dict(kind=kind, key=key, detail=detail, value=value, rule=rule))


# P1 · P2
pro = json.load(open(PRO, encoding='utf-8')) if os.path.exists(PRO) else {}
ds = pro.get('board', {}).get('design_settings', {})
for k, lim in BASE.get('pro_rules', {}).items():
    v = ds.get('rules', {}).get(k)
    if v is not None and v < lim - 1e-9:
        add('P1', 'pro:%s' % k, '.kicad_pro %s %s < 기준 %s' % (k, fmt(v), fmt(lim)), v)
for k, v in ds.get('rule_severities', {}).items():
    if v == 'ignore':
        add('P2', 'ignore:%s' % k, '.kicad_pro rule_severities %s = ignore' % k)

# 넷클래스별 영역 밖(기본) 규칙 값
plain = {}
for r in rules:
    if AREA_RE.search(r['condition']):
        continue
    for nc in NC_RE.findall(r['condition']) or ['*']:
        for c in r['constraints']:
            plain.setdefault((nc, c['type']), c)

for r in rules:
    areas = AREA_RE.findall(r['condition'])
    ncs = NC_RE.findall(r['condition']) or ['*']
    if r['severity'] in ('ignore', 'exclusion'):
        add('D4', 'severity:%s' % r['name'], '규칙 %s (severity %s)' % (r['name'], r['severity']), rule=r['name'])
    for c in r['constraints']:
        t = c['type']
        loose = []
        if 'min' in c and t in BASE['dru_min']:
            if c['min'] < BASE['dru_min'][t] - 1e-9:
                loose.append('min %s < 기준 %s' % (fmt(c['min']), fmt(BASE['dru_min'][t])))
        if 'max' in c and t in ORIG:
            for nc in ncs:
                lim = ORIG[t].get(nc, ORIG[t].get('*'))
                if lim is not None and c['max'] > lim + 1e-9:
                    loose.append('max %s > 원래 %s (%s)' % (fmt(c['max']), fmt(lim), nc))
        if areas:
            for nc in ncs:
                p = plain.get((nc, t)) or plain.get(('*', t))
                if p is None:
                    continue
                if 'max' in c and 'max' in p and c['max'] > p['max'] + 1e-9:
                    loose.append('영역 안 max %s > 영역 밖 %s (%s)' % (fmt(c['max']), fmt(p['max']), nc))
                if 'min' in c and 'min' in p and c['min'] < p['min'] - 1e-9:
                    loose.append('영역 안 min %s < 영역 밖 %s (%s)' % (fmt(c['min']), fmt(p['min']), nc))
        if loose:
            kind = 'D3' if areas else ('D2' if any(x.startswith('max') for x in loose) else 'D1')
            v = c.get('max') if any('max' in x for x in loose) else c.get('min')
            add(kind, 'rule:%s:%s' % (r['name'], t), '규칙 %s %s%s: %s' % (r['name'], t,
                (' [영역 %s]' % ','.join('%s(%s)' % a for a in areas)) if areas else '', '; '.join(sorted(set(loose)))), v, r['name'])

# ---------- D-003 대조 ----------
d003 = open(A.d003, encoding='utf-8').read()
rows = {}
for ln in d003.splitlines():
    m = re.match(r'\|\s*(\d+)\s*\|', ln)
    if m:
        rows[int(m.group(1))] = ln


def match(rec, rx):
    m = rec['match']
    if 'key' in m and m['key'] != rx['key']:
        return False
    if 'rule' in m and m['rule'] != rx['rule']:
        return False
    if 'constraint' in m and not rx['key'].endswith(':' + m['constraint']):
        return False
    if 'area' in m and ("(%s)" % m['area']) not in rx['detail'] and ("'%s'" % m['area']) not in rx['detail']:
        return False
    return True


fails = []
for rx in relax:
    recs = [r for r in REC['records'] if match(r, rx)]
    if not recs:
        rx.update(status='기록 없음', ok=False)
        fails.append(rx)
        continue
    rec = recs[0]
    row = rows.get(rec['d003'])
    need = [s.replace('{value}', fmt(rx['value']) if rx['value'] is not None else '') for s in rec.get('must_contain', [])]
    miss = [s for s in need if row is None or s not in row]
    rx.update(d003=rec['d003'], need=need, missing_text=miss, ok=(row is not None and not miss),
              status=('기록 일치' if row is not None and not miss else ('D-003 행 없음' if row is None else '기록 문구 불일치')))
    if not rx['ok']:
        fails.append(rx)

R = dict(board=A.pcb, dru=DRU, pro=PRO, d003=A.d003, records=A.records, rules=len(rules), relaxations=relax,
         fail=len(fails), pass_=(not fails))
json.dump(R, open(A.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for rx in relax:
    print('%s  %-4s %s — %s' % ('통과' if rx['ok'] else '불합격', rx['kind'], rx['detail'], rx['status']))
print('완화 %d · 불합격 %d' % (len(relax), len(fails)))
sys.exit(len(fails))
