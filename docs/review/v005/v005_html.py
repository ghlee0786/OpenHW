# -*- coding: utf-8 -*-
"""V-005 사람 확인용 HTML 한 장.
사용: python -I v005_html.py <out_dir> <commit> <res_dir>
  out_dir: <board>_{top,bottom}.png, <board>_{F,B}_silk.svg 가 있는 폴더 (index.html 을 여기에 쓴다)
  res_dir: rules_<board>.json, silk_<board>.json, drc_<board>.json 이 있는 폴더
SVG 좌표: kicad-cli export svg --page-size-mode 2 → x = 보드x − 80, y = 보드y − 80 (뒷면 --mirror: x = 120 − 보드x)
"""
import sys, os, re, json, html

out_dir, commit, res = sys.argv[1], sys.argv[2], sys.argv[3]
BOARDS = ['carrier', 'front']
X0, Y0, XM = 80.0, 80.0, 120.0


def load(n):
    return json.load(open(os.path.join(res, n), encoding='utf-8'))


def svg_inner(path, gid):
    s = open(path, encoding='utf-8').read()
    body = s[s.index('>', s.index('<svg')) + 1:s.rindex('</svg>')]
    body = re.sub(r'<title>.*?</title>|<desc>.*?</desc>', '', body, flags=re.S)
    return '<g id="%s">%s</g>' % (gid, body)


def tx(side, x, y):
    return ((XM - x) if side == 'B' else (x - X0)), y - Y0


def box_to_view(side, bb, pad=1.2):
    x0, y0 = tx(side, bb[0], bb[1]); x1, y1 = tx(side, bb[2], bb[3])
    xa, xb = sorted((x0, x1)); ya, yb = sorted((y0, y1))
    return xa - pad, ya - pad, (xb - xa) + 2 * pad, (yb - ya) + 2 * pad


E = html.escape
parts = []
defs = []
for bd in BOARDS:
    for side in 'FB':
        p = os.path.join(out_dir, '%s_%s_silk.svg' % (bd, side))
        if os.path.exists(p):
            defs.append(svg_inner(p, '%s_%s' % (bd, side)))

css = """
:root{--bg:#f7f7f5;--fg:#1d1d1b;--mut:#5d5d58;--card:#ffffff;--line:#d9d9d2;--bad:#c0392b;--warn:#b7791f;--ok:#2f855a;--hum:#2b6cb0;--pcb:#0f3d2a}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#141413;--fg:#ecebe6;--mut:#a3a29b;--card:#1f1f1d;--line:#3a3a36;--bad:#f07167;--warn:#f6c35b;--ok:#68d391;--hum:#7fb3f0;--pcb:#0f3d2a}}
:root[data-theme="dark"]{--bg:#141413;--fg:#ecebe6;--mut:#a3a29b;--card:#1f1f1d;--line:#3a3a36;--bad:#f07167;--warn:#f6c35b;--ok:#68d391;--hum:#7fb3f0}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.55 system-ui,-apple-system,"Segoe UI","Malgun Gothic",sans-serif}
main{max-width:1200px;margin:0 auto;padding:24px 16px 64px}h1{font-size:24px;margin:0 0 4px}h2{font-size:19px;margin:36px 0 10px;border-bottom:1px solid var(--line);padding-bottom:6px}h3{font-size:16px;margin:22px 0 8px}
.mut{color:var(--mut)}.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px;margin:10px 0}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}th{font-weight:600}
.tag{display:inline-block;border-radius:6px;padding:0 7px;font-size:12px;font-weight:600;border:1px solid currentColor}
.bad{color:var(--bad)}.warn{color:var(--warn)}.ok{color:var(--ok)}.hum{color:var(--hum)}
.imgs{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}.imgs figure{margin:0}.imgs img{width:100%;border-radius:8px;border:1px solid var(--line);background:#222}
figcaption{font-size:13px;color:var(--mut);margin-top:4px}
.silk{width:100%;background:var(--pcb);border-radius:8px;border:1px solid var(--line)}
.crops{display:grid;grid-template-columns:repeat(auto-fill,minmax(170px,1fr));gap:10px}.crop{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:6px}
.crop svg{width:100%;height:150px;background:var(--pcb);border-radius:6px}.crop .t{font-size:13px;margin-top:4px}
.chk{display:flex;gap:6px;align-items:center;font-size:13px;margin-top:4px}
.legend span{margin-right:14px;font-size:13px}.dot{display:inline-block;width:10px;height:10px;border-radius:50%;vertical-align:middle;margin-right:4px}
code{font-family:ui-monospace,Consolas,monospace;font-size:13px}
"""

parts.append('<h1>V-005 PCB 독립 감수 — 사람 확인용</h1>')
parts.append('<p class="mut">기준 커밋 <code>%s</code> (pcb 레인 t-20261126-171922-251f) · 생성: <code>v005_html.py</code> · KiCad 10.0.8 kicad-cli 렌더·SVG. '
             '이 장의 <span class="hum tag">사람</span> 항목은 사용자가 보고 체크하기 전까지 통과가 아니다. 체크 상태는 이 브라우저에만 남는다(저장소·검토자에게 전달되지 않음 — 결과는 orch에 직접 알려 주세요).</p>' % E(commit))

# 요약 표
parts.append('<h2>1. 기계 판정 요약 (verifiable 예)</h2><div class="card"><table><tr><th>항목</th><th>캐리어</th><th>전면</th></tr>')
rows = []
D = {bd: load('drc_%s.json' % bd) for bd in BOARDS}
RU = {bd: load('rules_%s.json' % bd) for bd in BOARDS}
SI = {bd: load('silk_%s.json' % bd) for bd in BOARDS}


def cell(v, good):
    return '<td class="%s">%s</td>' % ('ok' if good else 'bad', E(str(v)))


rows.append(('DRC 위반 (kicad-cli pcb drc --severity-all --schematic-parity)', [(len(D[b]['violations']), len(D[b]['violations']) == 0) for b in BOARDS]))
rows.append(('미연결', [(len(D[b]['unconnected_items']), len(D[b]['unconnected_items']) == 0) for b in BOARDS]))
rows.append(('회로도 일치 문제', [(len(D[b].get('schematic_parity', [])), len(D[b].get('schematic_parity', [])) == 0) for b in BOARDS]))
for k, lab in (('S1_on_mask_open', '패드·노출 동박 위 실크(잘림)'), ('S2_clear_lt_0p15', '실크–마스크 개구 < 0.15mm'), ('S3_line_lt_0p15', '실크 선폭 < 0.15mm'),
               ('S4_text', '글자 높이 < 1.0 · 획 < 0.15'), ('S5_edge', '보드 외곽까지 < 0.30mm'), ('S6_ref_hidden', '부품 아래 숨는 참조 지정자'), ('S7_text_text', '겹치는 글자')):
    rows.append((lab, [(SI[b]['summary'][k], SI[b]['summary'][k] == 0) for b in BOARDS]))
rows.append(('실크 글자 수(앞/뒤)', [('%d / %d' % (SI[b]['counts']['F']['text'], SI[b]['counts']['B']['text']), True) for b in BOARDS]))
for lab, vals in rows:
    parts.append('<tr><td>%s</td>%s</tr>' % (E(lab), ''.join(cell(v, g) for v, g in vals)))
parts.append('</table><p class="mut">수치 판정 근거와 수정 요청은 <code>docs/review/v005-pcb-review.md</code>.</p></div>')

# 렌더
parts.append('<h2>2. 3D 렌더 (kicad-cli pcb render, quality high)</h2>')
for bd in BOARDS:
    parts.append('<h3>%s</h3><div class="imgs">' % ('캐리어' if bd == 'carrier' else '전면'))
    for side, lab in (('top', '앞면(top)'), ('bottom', '뒷면(bottom)')):
        parts.append('<figure><img src="%s_%s.png" alt="%s %s 렌더" loading="lazy"><figcaption>%s</figcaption></figure>' % (bd, side, bd, side, lab))
    parts.append('</div>')

# 실크 SVG + 표시
parts.append('<h2>3. 실크 레이어 (노랑 = 실크, 보라 = 마스크 개구, 회색 = 외곽)</h2>'
             '<p class="legend"><span><i class="dot" style="background:#ff4d4d"></i>실크–마스크 &lt;0.15</span><span><i class="dot" style="background:#ffb000"></i>외곽 &lt;0.30</span>'
             '<span><i class="dot" style="background:#4da3ff"></i>1번 핀·극성 확인 대상</span></p><p class="mut">뒷면은 뒤에서 본 모습(좌우 반전)이다.</p>')
for bd in BOARDS:
    for side in 'FB':
        gid = '%s_%s' % (bd, side)
        H = 54.0 if bd == 'carrier' else 40.0
        marks = []
        for f in SI[bd]['findings']['S2_clear_lt_0p15']:
            if f['side'] != side:
                continue
            x, y = tx(side, *f['at'])
            marks.append('<circle cx="%.3f" cy="%.3f" r="0.45" fill="none" stroke="#ff4d4d" stroke-width="0.12"/>' % (x, y))
        for f in SI[bd]['findings']['S5_edge']:
            if f['side'] != side:
                continue
            x, y = tx(side, *f['at'])
            marks.append('<circle cx="%.3f" cy="%.3f" r="0.8" fill="none" stroke="#ffb000" stroke-width="0.18"/>' % (x, y))
        for c in SI[bd]['pin1_candidates']:
            if c['side'] != side:
                continue
            vx, vy, vw, vh = box_to_view(side, c['bbox'], 0.15)
            marks.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="none" stroke="#4da3ff" stroke-width="0.1" stroke-dasharray="0.4 0.3"/>'
                         '<text x="%.3f" y="%.3f" font-size="0.9" fill="#4da3ff">%s</text>' % (vx, vy, vw, vh, vx, vy - 0.15, E(c['ref'])))
        parts.append('<h3>%s · %s</h3><svg class="silk" viewBox="-1 -1 42 %.1f"><use href="#%s"/>%s</svg>'
                     % ('캐리어' if bd == 'carrier' else '전면', '앞면 실크' if side == 'F' else '뒷면 실크', H + 2, gid, ''.join(marks)))

# 사람 확인 항목
parts.append('<h2>4. 사람 확인 항목 (verifiable 아니오)</h2>')
parts.append('<div class="card"><table><tr><th>#</th><th>볼 것</th><th>어디를</th><th>확인</th></tr>'
             '<tr><td>H1</td><td>1번 핀·극성 표시를 조립자가 알아볼 수 있는가 (다이오드·LED·IC·커넥터·전해)</td><td>아래 4.1 확대 그림, 3절 파란 점선</td><td>각 그림 체크</td></tr>'
             '<tr><td>H2</td><td>실크에 참조 지정자·라벨 글자가 0개다(배치 스크립트가 참조를 조립도 Fab 층으로 옮김). 조립도(R-010 S6)로 대신하는 것을 받아들이는가, 시험점·커넥터 이름 정도는 실크에 둘 것인가</td><td>2절 렌더 전체</td><td><label class="chk"><input type="checkbox" data-k="H2">확인</label></td></tr>'
             '<tr><td>H3</td><td>읽는 방향 — 실크 글자가 없어 판정 대상 없음. 글자를 넣기로 하면 다시 본다</td><td>—</td><td><label class="chk"><input type="checkbox" data-k="H3">확인</label></td></tr>'
             '<tr><td>H4</td><td>표시가 잘려 보기 흉한 곳(빨간 원: 마스크 개구에서 0.05~0.149mm, PCBWay가 개구 둘레를 깎을 수 있음)</td><td>3절 빨간 원</td><td><label class="chk"><input type="checkbox" data-k="H4">확인</label></td></tr>'
             '<tr><td>H5</td><td>보드 끝 커넥터(USB-C J3·microSD J4·DC 잭 J2) 실크가 외곽 0.15~0.30mm — 외형 가공 공차(±0.2)로 일부 깎여도 되는가</td><td>3절 주황 원(캐리어 뒷면)</td><td><label class="chk"><input type="checkbox" data-k="H5">확인</label></td></tr>'
             '</table></div>')
parts.append('<h3>4.1 1번 핀·극성 확대 (H1)</h3><p class="mut">파란 숫자 = 기계 힌트(1번 패드 1mm 안, 다른 패드보다 1번 패드에 가까운 실크 항목 수). 0이라도 표시가 있을 수 있고(예: 모서리 점), 1 이상이어도 알아보기 어려울 수 있다 — 판정은 사람이 한다.</p><div class="crops">')
for bd in BOARDS:
    for c in SI[bd]['pin1_candidates']:
        side = c['side']
        vx, vy, vw, vh = box_to_view(side, c['bbox'], 1.0)
        # 1번 패드 위치 표시용: 부품 중심
        key = '%s:%s' % (bd, c['ref'])
        parts.append('<div class="crop"><svg viewBox="%.3f %.3f %.3f %.3f"><use href="#%s_%s"/></svg>'
                     '<div class="t"><b>%s</b> %s · %s%s · <span class="hum">힌트 %d</span></div>'
                     '<div class="t mut">%s</div><label class="chk"><input type="checkbox" data-k="%s">표시 알아봄</label></div>'
                     % (vx, vy, vw, vh, bd, side, E(c['ref']), '캐리어' if bd == 'carrier' else '전면', '앞' if side == 'F' else '뒤',
                        ' · DNP' if c['dnp'] else '', c['pin1_hint_items'], E(c['fpid'].split(':')[-1][:40]), E(key)))
parts.append('</div>')

js = """
(function(){var K='v005-checks';var st={};try{st=JSON.parse(localStorage.getItem(K)||'{}')}catch(e){}
document.querySelectorAll('input[data-k]').forEach(function(c){c.checked=!!st[c.dataset.k];c.addEventListener('change',function(){st[c.dataset.k]=c.checked;try{localStorage.setItem(K,JSON.stringify(st))}catch(e){}})})})();
"""
doc = ('<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
       '<title>V-005 PCB 감수</title><style>%s</style></head><body><svg width="0" height="0" style="position:absolute"><defs>%s</defs></svg><main>%s</main><script>%s</script></body></html>'
       % (css, ''.join(defs), ''.join(parts), js))
open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(doc)
print('ok', os.path.join(out_dir, 'index.html'), len(doc))
