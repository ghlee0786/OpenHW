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
parts.append('<p class="mut">기준 커밋 <code>%s</code> (pcb 레인 t-20261126-171922-251f) · 생성: <code>v005_html.py</code> (V-005b) · KiCad 10.0.8 kicad-cli 렌더·SVG. '
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
for k, lab in (('S1_on_mask_open', 'S1 패드·노출 동박 위 실크(잘림)'), ('S1v_over_via', 'S1v 비아 위 실크'), ('S1h_over_hole', 'S1h 구멍 위 실크'),
               ('S2_clear_lt_0p15', 'S2 실크–마스크 개구 < 0.15mm'), ('S3_line_lt_0p15', 'S3 실크 선폭 < 0.15mm'),
               ('S4_text', 'S4 글자 높이 < 1.0 · 획 < 0.15'), ('S4r_ratio_lt_1to5', 'S4r 획/높이 < 1:5 (획 0.2)'), ('S5_edge', 'S5 보드 외곽까지 < 0.30mm'),
               ('S6_ref_hidden', 'S6 부품 아래 숨는 참조'), ('S6a_ref_far', 'S6a 자기 부품에서 먼 참조(>2mm)'), ('S6a_ref_ambiguous', 'S6a 다른 부품이 더 가까운 참조'),
               ('S7_text_text', 'S7 글자–글자 겹침'), ('S7l_text_line', 'S7l 글자–선 겹침'), ('S7s_text_space', 'S7s 글자–실크 간격 < 0.127'),
               ('S8_orient_gt2', 'S8 읽는 방향 > 2종(면 수)'), ('S8m_mirror', 'S8m 거울상 오류'), ('S9_missing', 'S9 1번 핀·극성 표시 없음'), ('S9_wrong_side', 'S9 표시가 반대쪽')):
    rows.append((lab, [(SI[b]['summary'].get(k, 0), SI[b]['summary'].get(k, 0) == 0) for b in BOARDS]))
rows.append(('실크 글자 수 / 참조 수 (앞·뒤)', [('%d·%d / %d·%d' % (SI[b]['counts']['F']['text'], SI[b]['counts']['B']['text'], SI[b]['counts']['F'].get('ref', 0), SI[b]['counts']['B'].get('ref', 0)), True) for b in BOARDS]))
rows.append(('읽는 방향 (앞 / 뒤, 각도:개수)', [('%s / %s' % (SI[b].get('orientation', {}).get('F', {}), SI[b].get('orientation', {}).get('B', {})), True) for b in BOARDS]))
EX = {bd: (load('excl_%s.json' % bd) if os.path.exists(os.path.join(res, 'excl_%s.json' % bd)) else None) for bd in BOARDS}
if all(EX.values()):
    rows.append(('O-74 DRC 제외 수 / ignore 심각도 / DRU severity 규칙', [('%d / %d / %d' % (EX[b]['verdict']['exclusions'], EX[b]['verdict']['ignored_severities'], EX[b]['verdict']['dru_severity_rules']), True) for b in BOARDS]))
    rows.append(('O-74 E2 lib_footprint_mismatch 외 종류 제외', [(len(EX[b]['E2_disallowed']), EX[b]['verdict']['E2_pass']) for b in BOARDS]))
    rows.append(('O-74 E3 제외 참조 = pcb 문서 목록', [(EX[b]['E3']['status'], EX[b]['E3']['status'] != '불일치') for b in BOARDS]))
    rows.append(('O-74b E2b DRC 제외 0', [(EX[b]['verdict']['exclusions'], EX[b]['verdict'].get('E2b_exclusions_zero', True)) for b in BOARDS]))
    rows.append(('O-74b 실크 사본 별칭 / 사본 수', [('%s / %d' % (', '.join(EX[b]['verdict'].get('silk_redirects', [])) or '없음', EX[b]['verdict'].get('E4c_copies', 0)), True) for b in BOARDS]))
    rows.append(('O-74b E4c 사본↔원본(패드·구멍·실크 밖·sha256) 불합격', [(', '.join(EX[b]['verdict'].get('E4c_fail', [])) or '0', not EX[b]['verdict'].get('E4c_fail')) for b in BOARDS]))
    rows.append(('O-74 E4 사본·인스턴스 패드·구멍·실크 밖 다름', [(', '.join(EX[b]['verdict']['E4a_fail'] + EX[b]['verdict']['E4b_fail']) or '0', not (EX[b]['verdict']['E4a_fail'] or EX[b]['verdict']['E4b_fail'])) for b in BOARDS]))
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
             '<span><i class="dot" style="background:#4da3ff"></i>1번 핀·극성 판정 대상</span><span><i class="dot" style="background:#d63bff"></i>S9 표시 없음·반대</span></p><p class="mut">뒷면은 뒤에서 본 모습(좌우 반전)이다.</p>')
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
            if c.get('verdict') in ('missing', 'wrong_side'):
                vx, vy, vw, vh = box_to_view(side, c['bbox'], 0.3)
                marks.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="none" stroke="#d63bff" stroke-width="0.25"/>' % (vx, vy, vw, vh))
            vx, vy, vw, vh = box_to_view(side, c['bbox'], 0.15)
            marks.append('<rect x="%.3f" y="%.3f" width="%.3f" height="%.3f" fill="none" stroke="#4da3ff" stroke-width="0.1" stroke-dasharray="0.4 0.3"/>'
                         '<text x="%.3f" y="%.3f" font-size="0.9" fill="#4da3ff">%s</text>' % (vx, vy, vw, vh, vx, vy - 0.15, E(c['ref'])))
        parts.append('<h3>%s · %s</h3><svg class="silk" viewBox="-1 -1 42 %.1f"><use href="#%s"/>%s</svg>'
                     % ('캐리어' if bd == 'carrier' else '전면', '앞면 실크' if side == 'F' else '뒷면 실크', H + 2, gid, ''.join(marks)))

# 사람 확인 항목
parts.append('<h2>4. 사람 확인 항목 (verifiable 아니오 — V-005b에서 줄인 뒤 남은 것)</h2>')
parts.append('<div class="card"><table><tr><th>#</th><th>볼 것</th><th>왜 기계로 못 정하나</th><th>확인</th></tr>'
             '<tr><td>H1</td><td>1번 핀 판정이 <b>exempt(기구 키)</b>인 커넥터에 정말 방향 표시가 필요 없는가</td><td>부품 몸체가 방향을 정하는지는 실물·데이터시트 판단</td><td>아래 4.1의 exempt 칸 체크</td></tr>'
             '<tr><td>H2</td><td>판정 <b>ok_half</b>(1번 쪽 반에만 치우친 약한 표시)를 조립자가 알아보는가</td><td>표시 모양이 관례적인지는 사람 판단</td><td>아래 4.1의 ok_half 칸 체크</td></tr>'
             '<tr><td>H3</td><td>첫 보드 실물에서 0.15 선·1.0 글자가 읽히는가(인쇄 번짐·잘림)</td><td>제조 결과물이 필요 — 지금은 볼 수 없음</td><td><label class="chk"><input type="checkbox" data-k="H3">실물 확인</label></td></tr>'
             '</table><p class="mut">V-005 1차의 H2(실크 글자 0)는 O-65로, H5(외곽 문턱)는 O-66으로, 읽는 방향 개수·숨는 참조·겹침·1번 핀 ok/missing/wrong_side는 기계 판정(S6~S9)으로 옮겼다.</p></div>')
parts.append('<h3>4.1 1번 핀·극성 확대 — 기계 판정(S9)</h3><p class="mut">ok = 1번(캐소드·+) 쪽 사분면·반쪽에 실크가 더 많음 · ok_marker = 1번 쪽 2mm 안에 대칭 짝 없는 작은 표시(점·삼각·+) · ok_half = 반쪽에만 약하게 치우침(사람 H2) · missing = 치우친 실크 없음 · wrong_side = 반대쪽에 치우침 · exempt = 기구 키(사람 H1). 규칙·한계는 보고서 B9.</p><div class="crops">')
for bd in BOARDS:
    for c in SI[bd]['pin1_candidates']:
        side = c['side']
        vx, vy, vw, vh = box_to_view(side, c['bbox'], 1.0)
        # 1번 패드 위치 표시용: 부품 중심
        key = '%s:%s' % (bd, c['ref'])
        v = c.get('verdict', '?')
        cls = {'ok': 'ok', 'ok_marker': 'ok', 'ok_half': 'hum', 'exempt': 'hum', 'missing': 'bad', 'wrong_side': 'bad'}.get(v, 'warn')
        human = v in ('ok_half', 'exempt')
        chk = ('<label class="chk"><input type="checkbox" data-k="%s">%s</label>' % (E(key), '방향 표시 불필요 확인' if v == 'exempt' else '표시 알아봄')) if human else ''
        parts.append('<div class="crop"><svg viewBox="%.3f %.3f %.3f %.3f"><use href="#%s_%s"/></svg>'
                     '<div class="t"><b>%s</b> %s · %s%s · <span class="%s tag">%s</span></div>'
                     '<div class="t mut">%s %s</div>%s</div>'
                     % (vx, vy, vw, vh, bd, side, E(c['ref']), '캐리어' if bd == 'carrier' else '전면', '앞' if side == 'F' else '뒤',
                        ' · DNP' if c['dnp'] else '', cls, E(v), E(c['fpid'].split(':')[-1][:40]), E(c.get('reason', '')), chk))
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
