# -*- coding: utf-8 -*-
"""O-114 / D-003 #60 J1 탈출 비아 판정 고장 주입 (v005_rules.py 7번 esc_vias + v006_cond2.py 2.V1~V5).

사용: KiCad python -I test_v006_esc.py <캐리어 보드.kicad_pcb> [작업 폴더]   종료 0 = 전부 통과
보드 사본에 J1 둘레 규칙 영역(J1_ESC)과 멀리 뻗은 영역(J1_FAR), 시험 비아를 넣고 판정기를 돌린다. 입력 보드는 고치지 않는다.
"""
import sys, os, json, math, shutil, subprocess, tempfile
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1]
W = sys.argv[2] if len(sys.argv) > 2 else tempfile.mkdtemp(prefix='v006e_')
if os.path.isdir(W):
    shutil.rmtree(W)
BD = os.path.join(W, 'snap', 'hardware', 'schematic', 'carrier')
os.makedirs(BD)
mm, FM = pcbnew.ToMM, pcbnew.FromMM
b = pcbnew.LoadBoard(SRC)
j1 = next(fp for fp in b.Footprints() if fp.GetReference() == 'J1')
bb = j1.GetBoundingBox(False)
X0, Y0, X1, Y1 = mm(bb.GetX()) - 1.0, mm(bb.GetY()) - 1.0, mm(bb.GetRight()) + 1.0, mm(bb.GetBottom()) + 1.0
j1_nets = sorted(set(p.GetNetname() for p in j1.Pads() if p.GetNetname()))
other_net = next(n.GetNetname() for c, n in b.GetNetInfo().NetsByNetcode().items() if n.GetNetname() and n.GetNetname() not in j1_nets)
# 이미 있는 0.65/0.30 미만 비아는 그대로 두고 수만 센다 (KiCad 10 SWIG 는 Remove 뒤 Tracks() 가 깨진다)
base = [(mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth(pcbnew.F_Cu)) / 2, t.GetNetname(), mm(t.GetDrill())) for t in b.Tracks()
        if t.GetClass() == 'PCB_VIA' and (mm(t.GetWidth(pcbnew.F_Cu)) < 0.65 - 1e-6 or mm(t.GetDrill()) < 0.30 - 1e-6)]
base_in = sum(1 for x, y, r, n, dr in base if X0 <= x - r and x + r <= X1 and Y0 <= y - r and y + r <= Y1)
# 영역 밖 원래 비아 중 #21 허용분(GND 0.60/0.30 이상)과 아닌 것
base_ok = sum(1 for x, y, r, n, dr in base if not (X0 <= x - r and x + r <= X1 and Y0 <= y - r and y + r <= Y1)
              and n in ('/GND', 'GND') and 2 * r >= 0.60 - 1e-6 and dr >= 0.30 - 1e-6)
base_bad = len(base) - base_in - base_ok
GND = '/GND' if b.FindNet('/GND') else 'GND'
holes = [(mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetDrill()) / 2) for t in b.Tracks() if t.GetClass() == 'PCB_VIA']
for fp in b.Footprints():
    for p in fp.Pads():
        if p.GetDrillSize().x > 0:
            holes.append((mm(p.GetPosition().x), mm(p.GetPosition().y), mm(max(p.GetDrillSize().x, p.GetDrillSize().y)) / 2))


def area(name, x0, y0, x1, y1):
    z = pcbnew.ZONE(b)
    z.SetIsRuleArea(True); z.SetZoneName(name); z.SetLayerSet(pcbnew.LSET.AllCuMask())
    o = z.Outline(); o.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        o.Append(FM(x), FM(y))
    b.Add(z)


def free_spots(n, x0, y0, x1, y1, clear=1.2):
    out, y = [], y0 + 1.0          # 가장자리에서 1.0 안쪽 (옆에 0.45 떨어진 짝 비아를 놓아도 영역에 걸치지 않게)
    while y < y1 - 1.0 and len(out) < n:
        x = x0 + 1.0
        while x < x1 - 1.0 and len(out) < n:
            if all(math.hypot(x - hx, y - hy) - hr >= clear for hx, hy, hr in holes) and all(math.hypot(x - ox, y - oy) >= 2 * clear for ox, oy in out):
                out.append((round(x, 3), round(y, 3)))
            x += 0.2
        y += 0.2
    assert len(out) == n, '빈자리 부족 %d/%d' % (len(out), n)
    return out


def via(x, y, d, dr, net):
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(FM(x), FM(y))); v.SetWidth(FM(d)); v.SetDrill(FM(dr)); v.SetNet(b.FindNet(net))
    b.Add(v)
    return [round(x, 3), round(y, 3)]


# 입력 보드에 이미 있는 J1_* 규칙 영역(pcb 의 진짜 J1_ESC)은 이름을 바꿔 판정에서 뺀다 — 이 시험이 넣은 영역만 보게 (Remove 는 SWIG 가 깨져 못 씀)
for z in b.Zones():
    if z.GetIsRuleArea() and z.GetZoneName().startswith('J1_'):
        z.SetZoneName('ORIG_' + z.GetZoneName())
area('J1_ESC', X0, Y0, X1, Y1)
area('J1_FAR', X0 - 8.0, Y0, X0 - 6.0, Y0 + 2.0)                 # J1 에서 5 mm 넘게 떨어진 영역 → V5 불합격
sp = free_spots(6, X0, Y0, X1, Y1)
N = next(n for n in j1_nets if n not in ('/GND', 'GND'))
A_ = via(sp[0][0], sp[0][1], 0.50, 0.20, N)                      # 정상
B_ = via(sp[1][0], sp[1][1], 0.45, 0.20, N)                      # 지름·링 미달
C_ = via(sp[2][0], sp[2][1], 0.50, 0.15, N)                      # 드릴 미달
D1 = via(sp[3][0], sp[3][1], 0.50, 0.20, N)                      # 구멍 간격 0.25 (중심 0.45)
D2 = via(sp[3][0] + 0.45, sp[3][1], 0.50, 0.20, N)
E_ = via(sp[4][0], sp[4][1], 0.50, 0.20, other_net)              # J1 넷 아님
G_ = via(X0, sp[5][1], 0.50, 0.20, N)                            # 영역 가장자리에 걸침
far = free_spots(6, X1 + 6.0, Y0, X1 + 14.0, Y1)
F_ = via(far[0][0], far[0][1], 0.50, 0.20, N)                    # 영역 밖 작은 비아
H_ = via(far[1][0], far[1][1], 0.60, 0.30, N)                    # 영역 밖 0.60/0.30 (#21 0.65 미달)
S_ = via(far[2][0], far[2][1], 0.65, 0.30, N)                    # 표준 → 세지 않음
I_ = via(far[3][0], far[3][1], 0.60, 0.30, GND)                  # GND 이음 비아 0.60/0.30 → #21 허용
K_ = via(far[4][0], far[4][1], 0.55, 0.30, GND)                  # GND 라도 0.60 미만 → 불합격
tz = pcbnew.ZONE(b); tz.SetZoneName('THERMAL_T'); tz.SetNet(b.FindNet(N)); tz.SetLayer(pcbnew.F_Cu)
to = tz.Outline(); to.NewOutline()
for x, y in ((far[5][0] - 1.0, far[5][1] - 1.0), (far[5][0] + 1.0, far[5][1] - 1.0), (far[5][0] + 1.0, far[5][1] + 1.0), (far[5][0] - 1.0, far[5][1] + 1.0)):
    to.Append(FM(x), FM(y))
b.Add(tz)
T_ = via(far[5][0] - 0.4, far[5][1], 0.60, 0.30, N)              # 같은 넷 THERMAL 구리 안 열 비아 → #21 허용
U_ = via(far[5][0] + 0.4, far[5][1], 0.60, 0.30, other_net)      # THERMAL 안이지만 다른 넷 → 불합격
pcb = os.path.join(BD, 'carrier.kicad_pcb')
pcbnew.SaveBoard(pcb, b)
RES = os.path.join(W, 'res'); os.makedirs(RES)
rj = os.path.join(RES, 'rules_carrier.json')
rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v005_rules.py'), pcb, rj], capture_output=True, text=True, encoding='utf-8')
if rc.returncode != 0:
    print('v005_rules.py 실패', rc.returncode, rc.stderr[-2500:]); sys.exit(1)
E = json.load(open(rj, encoding='utf-8'))['esc_vias']


def at(lst, p):
    return next((v for v in lst if abs(v['at'][0] - p[0]) < 2e-3 and abs(v['at'][1] - p[1]) < 2e-3), None)


def why(p):
    v = at(E['inside_fail'], p)
    return ' '.join(v['why']) if v else ''


def cond2(dru, d003=None, tx=None):
    if tx is not None:   # O-119: 쌍 안 길이 차를 정해진 값으로 (TX 는 인자, RX 는 0.5)
        _r = json.load(open(rj, encoding='utf-8'))
        _r['pairs']['/EPHY_TX']['diff'] = tx; _r['pairs']['/EPHY_RX']['diff'] = 0.5
        json.dump(_r, open(rj, 'w', encoding='utf-8'), ensure_ascii=False)
    extra = []
    if d003 is not None:
        open(os.path.join(W, 'd003.md'), 'w', encoding='utf-8').write(d003)
        extra = ['--d003', os.path.join(W, 'd003.md')]
    open(os.path.join(BD, 'carrier.kicad_dru'), 'w', encoding='utf-8').write(dru)
    json.dump(dict(violations=[], unconnected_items=[], schematic_parity=[]), open(os.path.join(RES, 'drc_carrier.json'), 'w'))
    # O-115: 실크 참조 멂·모호(S6a)는 사람 확인 H4 — 불합격 수에 들지 않아야 한다
    json.dump(dict(summary={'S6a_ref_far': 2, 'S6a_ref_ambiguous': 1, 'S7_text_text': 1}, counts={'F': {'ref': 3}, 'B': {'ref': 0}}, pin1_candidates=[],
                   findings={'S6a_ref_far': [{'owner': 'R1'}, {'owner': 'R2'}], 'S6a_ref_ambiguous': [{'owner': 'R2'}]}),
              open(os.path.join(RES, 'silk_carrier.json'), 'w'))
    o = os.path.join(RES, 'cond2.json')
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v006_cond2.py'), RES, 'test', o, '--snap', os.path.join(W, 'snap'), '--root', W] + extra,
                   capture_output=True, text=True, encoding='utf-8')
    d = json.load(open(o, encoding='utf-8'))
    r = {i['id']: i for i in d['items'] if i['board'] == 'carrier'}
    r['_exit'] = d['exit_code']; r['_fails'] = sum(1 for i in d['items'] if i['verifiable'] and i['pass'] is False)
    r['_a8'] = {i['title'].split()[4]: i for i in d['items'] if i['id'] == '2.A8' and i['board'] == 'carrier'}   # 「쌍 안 길이 차 <넷>」
    return r


C_ok = cond2('(version 1)\n(rule "j1_esc" (condition "A.Type == \'Via\' && A.enclosedByArea(\'J1_ESC\')") (constraint via_diameter (min 0.50mm)))\n')
C_bad = cond2('(version 1)\n(rule "j1_esc" (condition "A.Type == \'Via\' && A.intersectsArea(\'J1_ESC\')") (constraint via_diameter (min 0.50mm)))\n')
DRU_OK = '(version 1)\n(rule "j1_esc" (condition "A.Type == \'Via\' && A.enclosedByArea(\'J1_ESC\')") (constraint via_diameter (min 0.50mm)))\n'
ROW62 = '| 62 | MDI TX 쌍 길이 차 예외(O-119, #28 예외) | (가) MDI TX 쌍만 쌍 안 길이 차 ≤1.7mm 허용, 비결합 길이는 그대로 | 근거 | 차선 |\n'
X_ok = cond2(DRU_OK, d003='| # | 항목 |\n|---|---|\n' + ROW62, tx=1.677)
X_over = cond2(DRU_OK, d003='| # | 항목 |\n|---|---|\n' + ROW62, tx=1.75)
X_norow = cond2(DRU_OK, d003='| # | 항목 |\n|---|---|\n| 28 | 차동쌍 | 쌍 안 길이 차 0 | 근거 | 차선 |\n', tx=1.677)
X_noarg = cond2(DRU_OK, tx=1.677)
CASES = [
    ('영역 2개 인식, J1_ESC 는 J1 둘레 1.0 (통과) · J1_FAR 는 멀다 (불합격)', {a['name']: a['beyond_ok'] for a in E['areas']} == {'J1_ESC': True, 'J1_FAR': False}),
    ('A 정상 0.50/0.20 → 영역 안, 불합격 아님(음성)', at(E['inside'], A_) is not None and at(E['inside_fail'], A_) is None and at(E['non_j1_net'], A_) is None),
    ('B 0.45/0.20 → 지름·링 미달(양성)', '지름' in why(B_) and '링' in why(B_)),
    ('C 0.50/0.15 → 드릴 미달(양성)', '드릴' in why(C_)),
    ('D 구멍 간격 0.25 두 비아 모두(양성)', '구멍 간격' in why(D1) and '구멍 간격' in why(D2) and abs(at(E['inside'], D1)['hole_gap'] - 0.25) < 0.005),
    ('E J1 넷 아닌 작은 비아(양성)', at(E['non_j1_net'], E_) is not None),
    ('G 영역에 걸친 비아 → 밖으로 셈 + 걸침(양성)', at(E['outside_small'], G_) is not None and at(E['straddle_small'], G_) is not None),
    ('F 영역 밖 0.50/0.20(양성)', at(E['outside_small'], F_) is not None and at(E['straddle_small'], F_) is None),
    ('H 영역 밖 신호 비아 0.60/0.30 — #21 신호 0.65 미달(양성)', at(E['outside_small'], H_) is not None),
    ('I GND 이음 비아 0.60/0.30 → #21 허용(음성)', at(E['allowed_060'], I_) is not None and at(E['outside_small'], I_) is None),
    ('K GND 라도 0.55/0.30 → 불합격(양성)', at(E['outside_small'], K_) is not None),
    ('T 같은 넷 THERMAL 구리 안 열 비아 0.60/0.30 → 허용(음성)', (at(E['allowed_060'], T_) or {}).get('kind') == '열'),
    ('U THERMAL 안 다른 넷 0.60/0.30 → 불합격(양성)', at(E['outside_small'], U_) is not None),
    ('S 0.65/0.30 은 세지 않음(음성) — 원래 있던 작은 비아 %d(영역 안 %d · #21 허용 %d) 더함' % (len(base), base_in, base_ok),
     E['small_total'] == 13 + len(base) and len(E['outside_small']) == 5 + base_bad and len(E['inside']) == 6 + base_in and len(E['allowed_060']) == 2 + base_ok),
    ('cond2 V1 영역 밖 5(+원래 것 중 허용 아닌 것) 불합격', C_ok['2.V1']['value'] == 5 + base_bad and C_ok['2.V1']['pass'] is False),
    ('cond2 V2 enclosedByArea 통과 / intersectsArea 불합격', C_ok['2.V2']['pass'] is True and C_bad['2.V2']['pass'] is False),
    ('cond2 V3 영역 안 불합격 (B·C·D1·D2 포함)', C_ok['2.V3']['value'] == len(E['inside_fail']) >= 4 and C_ok['2.V3']['pass'] is False),
    ('cond2 V4 J1 넷 아님 (E 포함)', C_ok['2.V4']['value'] == len(E['non_j1_net']) >= 1 and C_ok['2.V4']['pass'] is False),
    ('cond2 V5 J1_FAR 때문에 불합격', C_ok['2.V5']['pass'] is False),
    ('#62 MDI TX 쌍 안 길이 차 1.677 ≤ 1.7 통과(음성)', X_ok['_a8']['/EPHY_TX']['pass'] is True and '#62' in X_ok['_a8']['/EPHY_TX']['limit']),
    ('#62 MDI TX 1.75 > 1.7 불합격(양성)', X_over['_a8']['/EPHY_TX']['pass'] is False),
    ('#62 는 TX 한정 — MDI RX 0.5 는 #28 「0」 그대로 불합격(양성)', X_ok['_a8']['/EPHY_RX']['pass'] is False and '#28' in X_ok['_a8']['/EPHY_RX']['limit']),
    ('D-003 에 #62 행이 없으면 예외 없음 — TX 1.677 불합격(양성)', X_norow['_a8']['/EPHY_TX']['pass'] is False),
    ('--d003 을 안 주면 예외 없음 — TX 1.677 불합격(양성)', X_noarg['_a8']['/EPHY_TX']['pass'] is False),
    ('cond2 S6a 는 기계 항목에서 빠짐 (O-115)', '2.S6a' not in C_ok),
    ('cond2 H4 사람 확인: verifiable 아니오 · pass 없음 · 멂 2(R1, R2) / 모호 1(R2)', C_ok.get('2.H4', {}).get('verifiable') is False and C_ok['2.H4']['pass'] is None
     and C_ok['2.H4']['value'] == '2 / 1' and 'R1, R2' in C_ok['2.H4']['title']),
    ('cond2 종료 코드는 기계 불합격만 셈 (H4 제외, 글자 겹침 S7 은 그대로 불합격)', C_ok['_exit'] == C_ok['_fails'] and C_ok['2.S7']['pass'] is False),
]
fail = 0
for n, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', n)); fail += 0 if ok else 1
if fail:
    print(json.dumps(E, ensure_ascii=False)[:4000])
print('사례 %d · 실패 %d · 폴더 %s' % (len(CASES), fail, W))
sys.exit(1 if fail else 0)
