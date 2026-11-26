# -*- coding: utf-8 -*-
"""V-006: VD-001 가상 설계 완료 보고 HTML 한 장 생성기 (표준 라이브러리). 입력 형식은 docs/review/vd001-format.md.

사용: python -I v006_vd001_html.py [--vd validation/runtime/vd001] [--sim hardware/sim/results] [--root .] [--out <html>]
종료 코드 = 기계 불합격 항목 수 + 결과 파일 없는 조건 수(1~5, 7). 사람 확인 항목은 세지 않는다.
"""
import sys, os, re, json, glob, html, argparse, datetime

sys.stdout.reconfigure(encoding='utf-8')
ap = argparse.ArgumentParser()
ap.add_argument('--vd', default='validation/runtime/vd001')
ap.add_argument('--sim', default='hardware/sim/results')
ap.add_argument('--root', default='.')
ap.add_argument('--out', default=None)
A = ap.parse_args()
ROOT = os.path.abspath(A.root)
VD = os.path.abspath(A.vd)
OUT = os.path.abspath(A.out or os.path.join(VD, 'index.html'))
E = html.escape
COND = {'1': '회로 — ERC 0 · netcompare 0 · 계약 일치', '2': 'PCB — DRC 0 · 미연결 0 · parity 0 · 완화는 D-003 기록분만 · V-005 최종',
        '3': '제조 산출물 — R-010 16항', '4': '전기 가상 검증 — 임피던스 · 길이/skew · 전류 용량(IPC-2152) · 전압 강하 · 열 연결',
        '5': '3D · 조립 — 모델 빠짐 0 · 간섭 0 · 최소 틈 · 플러그 삽입 · 광축 · LED 가림 · BTB 높이', '7': '회로 시뮬레이션 (SIM)'}
KINDS = [('pcb-front', 'PCB 앞'), ('pcb-back', 'PCB 뒤'), ('assembly', '조립'), ('section', '단면'), ('exploded', '분해'), ('enclosure', '외함 완성'),
         ('turntable', '턴테이블(영상)')]


def link(path):
    if not path:
        return ''
    if path.startswith('commit:'):
        return '<code>%s</code>' % E(path[7:15])
    if re.match(r'https?://', path):
        return '<a href="%s">%s</a>' % (E(path), E(path))
    p = path if os.path.isabs(path) else os.path.join(ROOT, path)
    rel = os.path.relpath(p, os.path.dirname(OUT)).replace('\\', '/')
    ok = os.path.exists(p.split('#')[0])
    return '<a href="%s"%s>%s</a>' % (E(rel), '' if ok else ' class="miss" title="파일 없음"', E(os.path.basename(path.split('#')[0]) or path))


# ---------- 입력 ----------
conds, errors = {}, []
for f in sorted(glob.glob(os.path.join(VD, 'results', 'cond*.json'))):
    try:
        d = json.load(open(f, encoding='utf-8'))
        c = str(d.get('cond') or re.match(r'cond(\d+)', os.path.basename(f)).group(1))
        conds.setdefault(c, []).append((os.path.relpath(f, ROOT), d))
    except Exception as e:
        errors.append('%s: %s' % (os.path.basename(f), e))
sims = []
for f in sorted(glob.glob(os.path.join(ROOT, A.sim, '*.json'))):
    try:
        sims.append((os.path.relpath(f, ROOT), json.load(open(f, encoding='utf-8'))))
    except Exception as e:
        errors.append('%s: %s' % (os.path.basename(f), e))
renders = []
mf = os.path.join(VD, 'render', 'manifest.json')
if os.path.exists(mf):
    try:
        renders = json.load(open(mf, encoding='utf-8'))
    except Exception as e:
        errors.append('render/manifest.json: %s' % e)
risks = []
rf = os.path.join(VD, 'risks.json')
if os.path.exists(rf):
    try:
        risks = json.load(open(rf, encoding='utf-8'))
    except Exception as e:
        errors.append('risks.json: %s' % e)

# ---------- 집계 ----------
summary, fail_total, human = [], 0, []
for c in ['1', '2', '3', '4', '5']:
    files = conds.get(c, [])
    its = [dict(i, _file=f) for f, d in files for i in d.get('items', [])]
    mach = [i for i in its if i.get('verifiable')]
    nf = sum(1 for i in mach if i.get('pass') is not True)
    hm = [i for i in its if not i.get('verifiable')]
    human += [(c, i) for i in hm]
    missing = not files
    fail_total += nf + (1 if missing else 0)
    summary.append(dict(c=c, files=files, items=its, n=len(mach), nf=nf, nh=len(hm), missing=missing))
sim_bad = [s for _, s in sims if s.get('verdict') != 'pass']
fail_total += len(sim_bad) + (0 if sims else 1)

# ---------- HTML ----------
css = """
:root{--bg:#f7f7f5;--fg:#1d1d1b;--mut:#5d5d58;--card:#fff;--line:#d9d9d2;--bad:#c0392b;--ok:#2f855a;--hum:#2b6cb0;--warn:#b7791f}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141413;--fg:#ecebe6;--mut:#a3a29b;--card:#1f1f1d;--line:#3a3a36;--bad:#f07167;--ok:#68d391;--hum:#7fb3f0;--warn:#f6c35b}}
:root[data-theme="dark"]{--bg:#141413;--fg:#ecebe6;--mut:#a3a29b;--card:#1f1f1d;--line:#3a3a36;--bad:#f07167;--ok:#68d391;--hum:#7fb3f0;--warn:#f6c35b}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,"Segoe UI","Malgun Gothic",sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px 64px}h1{font-size:24px;margin:0 0 4px}h2{font-size:19px;margin:34px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}
.mut{color:var(--mut)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px;margin:10px 0;overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
.tag{display:inline-block;border-radius:6px;padding:0 7px;font-size:12px;font-weight:600;border:1px solid currentColor;white-space:nowrap}
a{color:var(--hum)}.bad{color:var(--bad)}.ok{color:var(--ok)}.hum{color:var(--hum)}.warn{color:var(--warn)}a.miss{color:var(--warn);text-decoration:line-through}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}.slot{background:var(--card);border:1px dashed var(--line);border-radius:10px;padding:8px;min-height:120px}
.slot img,.slot video{width:100%;border-radius:6px}.thumb{max-width:220px;border-radius:6px;border:1px solid var(--line)}
details summary{cursor:pointer;font-weight:600}code{font-family:ui-monospace,Consolas,monospace;font-size:13px}
"""
P = []
P.append('<h1>VD-001 가상 설계 완료 보고</h1><p class="mut">생성 %s · 생성기 <code>docs/review/v005/v006_vd001_html.py</code> · 입력 형식 <code>docs/review/vd001-format.md</code>. '
         '기계 항목은 결과 파일의 판정을 그대로 보인다. <span class="hum tag">사람</span> 항목은 사용자가 체크하기 전까지 통과가 아니다(체크는 이 브라우저에만 남음). 견적·비용은 이 보고에 넣지 않는다(D-003 #39).</p>'
         % datetime.datetime.now().isoformat(timespec='minutes'))
if errors:
    P.append('<div class="card bad">입력 오류: %s</div>' % E('; '.join(errors)))
P.append('<h2>요약</h2><div class="card"><table><tr><th>조건</th><th>결과 파일 · 커밋</th><th>기계 항목</th><th>불합격</th><th>사람 확인</th><th>판정</th></tr>')
for s in summary:
    files = '<br>'.join('%s · <code>%s</code> · 종료 %s' % (link(f), E(str(d.get('commit', ''))[:8]), E(str(d.get('exit_code', '?')))) for f, d in s['files']) or '<span class="warn">결과 없음</span>'
    v = '<span class="bad tag">결과 없음</span>' if s['missing'] else ('<span class="bad tag">불합격 %d</span>' % s['nf'] if s['nf'] else
                                                                       ('<span class="hum tag">사람 확인 대기</span>' if s['nh'] else '<span class="ok tag">통과</span>'))
    P.append('<tr><td><a href="#c%s">%s. %s</a></td><td>%s</td><td>%d</td><td>%d</td><td>%d</td><td>%s</td></tr>' % (s['c'], s['c'], E(COND[s['c']]), files, s['n'], s['nf'], s['nh'], v))
sv = '<span class="bad tag">결과 없음</span>' if not sims else ('<span class="bad tag">불합격 %d</span>' % len(sim_bad) if sim_bad else '<span class="ok tag">통과</span>')
P.append('<tr><td><a href="#c7">7. %s</a></td><td>%s</td><td>%d</td><td>%d</td><td>-</td><td>%s</td></tr>' % (E(COND['7']), E(A.sim), len(sims), len(sim_bad), sv))
P.append('<tr><td>6. 이 HTML · 원장</td><td colspan="4">사람 확인 %d건 · 남은 위험 %d건</td><td>%s</td></tr></table>'
         '<p>기계 불합격 + 결과 없음 합계: <b class="%s">%d</b> (생성기 종료 코드)</p></div>' % (len(human), len(risks), '<span class="hum tag">사람 확인</span>' if human else '', 'bad' if fail_total else 'ok', fail_total))

for s in summary:
    P.append('<h2 id="c%s">%s. %s</h2>' % (s['c'], s['c'], E(COND[s['c']])))
    if s['missing']:
        P.append('<div class="card warn">결과 파일 없음 — <code>%s/results/cond%s-*.json</code></div>' % (E(os.path.relpath(VD, ROOT)), s['c']))
        continue
    for f, d in s['files']:
        P.append('<p class="mut">%s · 명령 <code>%s</code> · 생성 %s</p>' % (link(f), E(d.get('command', '')), E(d.get('generated', ''))))
    P.append('<div class="card"><table><tr><th>id</th><th>보드</th><th>항목</th><th>verifiable</th><th>값</th><th>기준</th><th>결과</th><th>근거</th></tr>')
    for i in sorted(s['items'], key=lambda i: (i.get('pass') is not False, not i.get('verifiable'), str(i.get('id')))):
        if i.get('verifiable'):
            r = '<span class="ok tag">통과</span>' if i.get('pass') is True else '<span class="bad tag">불합격</span>'
        else:
            k = 'c%s:%s:%s' % (s['c'], i.get('id'), i.get('board'))
            r = '<label class="hum"><input type="checkbox" data-k="%s"> 사람 확인</label>' % E(k)
        ev = ' '.join(link(e.get('path', '')) for e in i.get('evidence', []))
        note = ('<div class="mut">%s</div>' % E(str(i['note']))) if i.get('note') else ''
        P.append('<tr><td><code>%s</code></td><td>%s</td><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                 % (E(str(i.get('id'))), E(str(i.get('board', '-'))), E(str(i.get('title'))), note, '예' if i.get('verifiable') else '<b class="hum">아니오</b>',
                    E(str(i.get('value', ''))), E(str(i.get('limit', ''))), r, ev))
    P.append('</table></div>')

P.append('<h2 id="c7">7. %s</h2>' % E(COND['7']))
if not sims:
    P.append('<div class="card warn">결과 없음 — <code>%s/*.json</code> (orch O-81 형식)</div>' % E(A.sim))
for f, s in sims:
    v = s.get('verdict')
    P.append('<div class="card"><b>%s</b> %s <span class="%s tag">%s</span> <span class="mut">%s · 보드 %s · 참조 %s · 모델 %s%s · 도구 %s %s</span>'
             % (E(str(s.get('id'))), E(str(s.get('title'))), 'ok' if v == 'pass' else 'bad', E(str(v)), link(f), E(str(s.get('circuit', {}).get('board', ''))),
                E(', '.join(s.get('circuit', {}).get('refs', []))), E(str(s.get('model', {}).get('source', ''))),
                ' (동작 모델)' if s.get('model', {}).get('behavioral') else '', E(str(s.get('tool', {}).get('name', ''))), E(str(s.get('tool', {}).get('version', '')))))
    P.append('<table><tr><th>검사</th><th>값</th><th>기준</th><th>코너</th><th>결과</th></tr>')
    for c in s.get('checks', []):
        lim = c.get('limit')
        lim = '%s %s' % (c.get('op'), lim if not isinstance(lim, list) else '%s~%s' % tuple(lim))
        P.append('<tr><td>%s</td><td>%s %s</td><td>%s %s</td><td>%s</td><td>%s</td></tr>' % (E(str(c.get('name'))), E(str(c.get('value'))), E(str(c.get('unit', ''))), E(lim),
                 E(str(c.get('unit', ''))), E(str(c.get('corner', ''))), '<span class="ok tag">통과</span>' if c.get('pass') else '<span class="bad tag">불합격</span>'))
    P.append('</table>')
    for w in s.get('waveforms', []):
        P.append('<a href="%s"><img class="thumb" src="%s" alt="%s" loading="lazy"></a> ' % ((os.path.relpath(os.path.join(ROOT, w), os.path.dirname(OUT)).replace('\\', '/'),) * 2 + (E(w),)))
    if s.get('notes'):
        P.append('<p class="mut">%s</p>' % E(str(s['notes'])))
    P.append('</div>')

P.append('<h2 id="render">렌더 (PCB 앞뒤 · 조립 · 단면 · 분해 · 외함 완성) — 사람 확인</h2><div class="grid">')
for k, lab in KINDS:
    rs = [r for r in renders if r.get('kind') == k]
    if not rs:
        P.append('<div class="slot"><b>%s</b><p class="warn">자리 — 아직 없음 (render/manifest.json kind=%s)</p></div>' % (E(lab), k))
    for r in rs:
        src = os.path.relpath(os.path.join(ROOT, r.get('path', '')), os.path.dirname(OUT)).replace('\\', '/')
        media = ('<video src="%s" controls muted></video>' % E(src)) if src.lower().endswith('.mp4') else ('<a href="%s"><img src="%s" alt="%s" loading="lazy"></a>' % (E(src), E(src), E(r.get('title', ''))))
        P.append('<div class="slot"><b>%s</b> %s %s<div class="mut">%s · sha256 %s… · 입력 %s…</div><label class="hum"><input type="checkbox" data-k="render:%s"> 봄</label></div>'
                 % (E(lab), E(r.get('title', '')), media, E(r.get('source', '')), E(str(r.get('sha256', ''))[:12]), E(str(r.get('input_sha256', ''))[:12]), E(r.get('path', ''))))
P.append('</div>')

P.append('<h2 id="human">사람 확인 모음 (verifiable 아니오 %d건)</h2><div class="card"><table><tr><th>조건</th><th>id</th><th>보드</th><th>볼 것</th><th>근거</th></tr>' % len(human))
for c, i in human:
    P.append('<tr><td>%s</td><td><code>%s</code></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (c, E(str(i.get('id'))), E(str(i.get('board', '-'))), E(str(i.get('title'))),
             ' '.join(link(e.get('path', '')) for e in i.get('evidence', []))))
P.append('</table></div>')
P.append('<h2 id="risks">bring-up 으로 넘기는 남은 위험 (%d)</h2><div class="card"><table><tr><th>id</th><th>위험</th><th>출처</th><th>담당</th><th>bring-up 확인</th><th>상태</th></tr>' % len(risks))
for r in risks:
    P.append('<tr><td>%s</td><td>%s%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (E(str(r.get('id'))), E(str(r.get('title'))), ('<div class="mut">%s</div>' % E(r['note'])) if r.get('note') else '',
             E(str(r.get('source', ''))), E(str(r.get('owner', ''))), E(str(r.get('bringup', ''))), E(str(r.get('status', '')))))
if not risks:
    P.append('<tr><td colspan="6" class="warn">risks.json 없음 — orch가 원장 대기 목록에서 만든다</td></tr>')
P.append('</table></div>')
js = """(function(){var K='vd001-checks',s={};try{s=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
document.querySelectorAll('input[data-k]').forEach(function(c){c.checked=!!s[c.dataset.k];c.addEventListener('change',function(){s[c.dataset.k]=c.checked;try{localStorage.setItem(K,JSON.stringify(s))}catch(e){}})})})();"""
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
                                       '<title>VD-001 완료 보고</title><style>%s</style></head><body><main>%s</main><script>%s</script></body></html>' % (css, ''.join(P), js))
print('VD-001 HTML %s · 기계 불합격+결과 없음 %d · 사람 확인 %d · 위험 %d' % (OUT, fail_total, len(human), len(risks)))
sys.exit(fail_total)
