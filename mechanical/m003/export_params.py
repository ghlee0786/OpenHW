"""params.py → params.csv / params.md (CAD 독립 매개변수 표). 실행: python -I -B -X utf8 mechanical/m003/export_params.py"""
import csv, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
g = {}
exec(open(os.path.join(HERE, 'params.py'), encoding='utf-8').read(), g)
P, d = g['P'], g['derive'](g['P'])
src = open(os.path.join(HERE, 'params.py'), encoding='utf-8').read()
notes = {}
for line in src.splitlines():
    for k in re.findall(r"P\['(\w+)'\]", line):
        if '#' in line:
            notes.setdefault(k, line.split('#', 1)[1].strip())
rows = []
for k, v in P.items():
    rows.append((k, 'input', repr(v), notes.get(k, '')))
for k, v in d.items():
    if k not in P:
        rows.append((k, 'derived', repr(round(v, 3) if isinstance(v, float) else v), 'params.derive()'))
with open(os.path.join(HERE, 'params.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['name', 'kind', 'value_mm', 'source_note'])
    w.writerows(rows)
with open(os.path.join(HERE, 'params.md'), 'w', encoding='utf-8') as f:
    f.write('# M-003 외함 매개변수 표 (params.py 에서 생성, 단위 mm, 원점 O = 코어 중심·아랫면, +Z = 광축)\n\n')
    f.write('| 이름 | 종류 | 값 | 출처·메모 |\n|---|---|---|---|\n')
    for r in rows:
        f.write('| %s | %s | `%s` | %s |\n' % (r[0], '입력' if r[1] == 'input' else '유도', r[2], r[3].replace('|', '/')))
print('rows', len(rows))
