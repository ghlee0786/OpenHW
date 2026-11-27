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
# O-121 / D-003 #64: SD ESD 어레이(U4·U5) 영역 — 두 부품 외곽 상자를 합쳐 0.6 넓힌 사각형
sd_fps = [fp for fp in b.Footprints() if fp.GetReference() in ('U4', 'U5')]
sd_bbs = [fp.GetBoundingBox(False) for fp in sd_fps]
SX0, SY0 = mm(min(q.GetX() for q in sd_bbs)) - 0.6, mm(min(q.GetY() for q in sd_bbs)) - 0.6
SX1, SY1 = mm(max(q.GetRight() for q in sd_bbs)) + 0.6, mm(max(q.GetBottom() for q in sd_bbs)) + 0.6
sd_nets = set(p.GetNetname() for fp in sd_fps for p in fp.Pads())
sd_sig = [(fp, p) for fp in sd_fps for p in fp.Pads() if p.GetNetname() and p.GetNetname() not in ('/GND', 'GND')]
sd_gnd = [(fp, p) for fp in sd_fps for p in fp.Pads() if p.GetNetname() in ('/GND', 'GND')]
not_sd_net = next(n for n in j1_nets if n not in sd_nets and n not in ('/GND', 'GND'))
# 이미 있는 0.65/0.30 미만 비아는 그대로 두고 수만 센다 (KiCad 10 SWIG 는 Remove 뒤 Tracks() 가 깨진다)
base = [(mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth(pcbnew.F_Cu)) / 2, t.GetNetname(), mm(t.GetDrill())) for t in b.Tracks()
        if t.GetClass() == 'PCB_VIA' and (mm(t.GetWidth(pcbnew.F_Cu)) < 0.65 - 1e-6 or mm(t.GetDrill()) < 0.30 - 1e-6)]
def in_rects(x, y, r):
    return (X0 <= x - r and x + r <= X1 and Y0 <= y - r and y + r <= Y1) or (SX0 <= x - r and x + r <= SX1 and SY0 <= y - r and y + r <= SY1)


base_in = sum(1 for x, y, r, n, dr in base if in_rects(x, y, r))
# 영역 밖 원래 비아 중 #21 허용분(GND 0.60/0.30 이상)과 아닌 것
base_ok = sum(1 for x, y, r, n, dr in base if not in_rects(x, y, r)
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
    if z.GetIsRuleArea() and (z.GetZoneName().startswith('J1_') or z.GetZoneName().startswith('SD_')):
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
# ---- O-121: SD_ESC 영역, 영역 안 작은 비아 2개, ESD GND 패드 4개의 비아·트랙 ----
area('SD_ESC', SX0, SY0, SX1, SY1)


def pxy(p):
    return mm(p.GetPosition().x), mm(p.GetPosition().y)


SDok = via(pxy(sd_sig[0][1])[0], pxy(sd_sig[0][1])[1], 0.50, 0.20, sd_sig[0][1].GetNetname())     # U4·U5 핀 넷 → 통과
SDbad = via(pxy(sd_sig[1][1])[0], pxy(sd_sig[1][1])[1], 0.50, 0.20, not_sd_net)                   # J1 넷이지만 U4·U5 넷 아님 → 불합격


def gnd_stub(fp, p, length, width):
    """GND 패드 중심에서 부품 바깥쪽으로 length 만큼 트랙(폭 width)을 내고 끝에 0.65/0.30 비아. length 0 이면 패드 안 비아."""
    x, y = pxy(p)
    # 네 방향 중 끝점이 기존 GND 비아·GND 트랙 끝에서 가장 먼 쪽 — 보드에 이미 있는 GND 트랙을 타고 시험 비아에 닿으면 안 된다
    ux, uy = max(((0.0, 1.0), (0.0, -1.0), (1.0, 0.0), (-1.0, 0.0)),
                 key=lambda u: min([math.hypot(x + u[0] * max(length, 0.7) - gx, y + u[1] * max(length, 0.7) - gy) for gx, gy in gnd_pts] or [9.0]))
    ex, ey = x + ux * length, y + uy * length
    gnd_pts.append((ex, ey))
    if length > 0:
        t = pcbnew.PCB_TRACK(b)
        t.SetStart(pcbnew.VECTOR2I(FM(x), FM(y))); t.SetEnd(pcbnew.VECTOR2I(FM(ex), FM(ey))); t.SetWidth(FM(width))
        t.SetLayer(pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu); t.SetNet(b.FindNet(p.GetNetname()))
        b.Add(t)
    return via(ex, ey, 0.65, 0.30, p.GetNetname())


assert len(sd_gnd) >= 4, 'U4·U5 GND 패드 %d' % len(sd_gnd)
# 입력 보드에 이미 있는 U4·U5 둘레 GND 트랙은 다른 넷으로 돌려 놓는다 — 시험이 넣은 트랙만 패드에서 비아로 이어지게 (지우면 SWIG 가 깨져 넷만 바꾼다)
_gp = [pxy(p) for _f, p in sd_gnd]
for t in b.Tracks():
    if t.GetClass() == 'PCB_TRACK' and t.GetNetname() in ('/GND', 'GND') and any(
            math.hypot(mm(e.x) - gx, mm(e.y) - gy) < 4.0 for e in (t.GetStart(), t.GetEnd()) for gx, gy in _gp):
        t.SetNet(b.FindNet(other_net))
gnd_pts = []   # 기존 GND 비아 중심과 GND 트랙 끝점
for t in b.Tracks():
    if t.GetNetname() in ('/GND', 'GND'):
        if t.GetClass() == 'PCB_VIA':
            gnd_pts.append((mm(t.GetPosition().x), mm(t.GetPosition().y)))
        else:
            gnd_pts += [(mm(t.GetStart().x), mm(t.GetStart().y)), (mm(t.GetEnd().x), mm(t.GetEnd().y))]
G_in = gnd_stub(sd_gnd[0][0], sd_gnd[0][1], 0.0, 0.25)      # 패드 안 비아 → 조건 맞음
G_ok = gnd_stub(sd_gnd[1][0], sd_gnd[1][1], 0.7, 0.25)      # 0.7 mm · 폭 0.25 → 조건 맞음
G_thin = gnd_stub(sd_gnd[2][0], sd_gnd[2][1], 0.7, 0.15)    # 폭 0.15 → 조건 안 맞음
G_long = gnd_stub(sd_gnd[3][0], sd_gnd[3][1], 1.4, 0.25)    # 1.4 mm → 조건 안 맞음
# O-123: 같은 부품의 두 GND 패드(sd_gnd[0] ↔ sd_gnd[1])를 0.25 트랙으로 잇는다 — sd_gnd[0] 에서 G_ok 로 가는 경로는 sd_gnd[1] 을 거친다
assert sd_gnd[0][0].GetReference() == sd_gnd[1][0].GetReference()
_t = pcbnew.PCB_TRACK(b)
_t.SetStart(pcbnew.VECTOR2I(FM(pxy(sd_gnd[0][1])[0]), FM(pxy(sd_gnd[0][1])[1]))); _t.SetEnd(pcbnew.VECTOR2I(FM(pxy(sd_gnd[1][1])[0]), FM(pxy(sd_gnd[1][1])[1])))
_t.SetWidth(FM(0.25)); _t.SetLayer(pcbnew.F_Cu if sd_gnd[0][1].IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu); _t.SetNet(b.FindNet(sd_gnd[0][1].GetNetname())); b.Add(_t)
PAD0 = (sd_gnd[0][0].GetReference(), sd_gnd[0][1].GetNumber()); PAD1 = (sd_gnd[1][0].GetReference(), sd_gnd[1][1].GetNumber())
PAD2 = (sd_gnd[2][0].GetReference(), sd_gnd[2][1].GetNumber()); PAD3 = (sd_gnd[3][0].GetReference(), sd_gnd[3][1].GetNumber())
D01 = math.hypot(pxy(sd_gnd[0][1])[0] - pxy(sd_gnd[1][1])[0], pxy(sd_gnd[0][1])[1] - pxy(sd_gnd[1][1])[1])
pcb = os.path.join(BD, 'carrier.kicad_pcb')
pcbnew.SaveBoard(pcb, b)
RES = os.path.join(W, 'res'); os.makedirs(RES)
rj = os.path.join(RES, 'rules_carrier.json')
rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v005_rules.py'), pcb, rj], capture_output=True, text=True, encoding='utf-8')
if rc.returncode != 0:
    print('v005_rules.py 실패', rc.returncode, rc.stderr[-2500:]); sys.exit(1)
E = json.load(open(rj, encoding='utf-8'))['esc_vias']
EG = json.load(open(rj, encoding='utf-8'))['esd_gnd']['pads']


def esd_via(pos, pad=None):
    """pad = (부품, 패드 번호) 를 주면 그 패드의 기록에서만 찾는다"""
    for x_ in EG:
        if pad is not None and (x_['ref'], x_['pad']) != pad:
            continue
        for v_ in x_['vias']:
            if abs(v_['at'][0] - pos[0]) < 2e-3 and abs(v_['at'][1] - pos[1]) < 2e-3:
                return v_
    return None


def at(lst, p):
    return next((v for v in lst if abs(v['at'][0] - p[0]) < 2e-3 and abs(v['at'][1] - p[1]) < 2e-3), None)


def why(p):
    v = at(E['inside_fail'], p)
    return ' '.join(v['why']) if v else ''


def cond2(dru, d003=None, tx=None, unc=None, unc_ar=None, base=None, nopairs=False, esd=None):
    if esd is not None:   # ESD GND 핀 목록을 정해진 값으로 (원본은 뒤에 되돌림)
        _keep2 = open(rj, encoding='utf-8').read()
        _r2 = json.loads(_keep2); _r2['esd_gnd']['pads'] = esd
        json.dump(_r2, open(rj, 'w', encoding='utf-8'), ensure_ascii=False)
    if nopairs:   # 넷클래스를 못 읽은 것처럼 쌍을 비움 (원본은 뒤에 되돌림)
        _keep = open(rj, encoding='utf-8').read()
        _r0 = json.loads(_keep); _r0['pairs'] = {}
        json.dump(_r0, open(rj, 'w', encoding='utf-8'), ensure_ascii=False)
    if tx is not None:   # O-119: 쌍 안 길이 차를 정해진 값으로 (TX 는 인자, RX 는 0.5)
        _r = json.load(open(rj, encoding='utf-8'))
        _r['pairs']['/EPHY_TX']['diff'] = tx; _r['pairs']['/EPHY_RX']['diff'] = 0.5
        for _k, _d in (('/EPHY_TX', tx), ('/EPHY_RX', 0.5)):   # 판정값(max(트랙, +비아))도 같은 값으로
            _r['pairs'][_k]['via'] = dict(P={}, N={}, diff_with_via=_d, diff_judged=_d, uncoupled_area_rule_with_via={'P': unc_ar or 0.0, 'N': 0.0})
            _r['pairs'][_k]['uncoupled_area_rule'] = {'P': unc_ar or 0.0, 'N': 0.0, 'in_twist_P': 0.0, 'in_twist_N': 0.0}
        if unc is not None:   # 꼬임 밖 비결합(쌍 간격 0.18 셈법)을 TX·RX 같은 값으로
            for _k in ('/EPHY_TX', '/EPHY_RX'):
                _r['pairs'][_k]['uncoupled_outside_twist'] = {'P': unc, 'N': 0.0}
        json.dump(_r, open(rj, 'w', encoding='utf-8'), ensure_ascii=False)
    extra = []
    if base is not None:
        json.dump(base, open(os.path.join(W, 'abase.json'), 'w', encoding='utf-8'))
        extra += ['--area-baseline', os.path.join(W, 'abase.json')]
    if d003 is not None:
        open(os.path.join(W, 'd003.md'), 'w', encoding='utf-8').write(d003)
        extra += ['--d003', os.path.join(W, 'd003.md')]
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
    r['_all'] = {i['id']: i for i in d['items'] if i['board'] == 'carrier'}
    if nopairs:
        open(rj, 'w', encoding='utf-8').write(_keep)
    if esd is not None:
        open(rj, 'w', encoding='utf-8').write(_keep2)
    r['_a10'] = {('/EPHY_TX' if '/EPHY_TX' in i['title'] else '/EPHY_RX'): i for i in d['items'] if i['id'] == '2.A10' and i['board'] == 'carrier' and '/EPHY_' in i['title']}
    return r


RULE = '(rule "%s" (condition "A.Type == \'Via\' && A.%s(\'%s\')") (constraint via_diameter (min 0.50mm)))\n'
DRU_ALL = '(version 1)\n' + RULE % ('j1_esc', 'enclosedByArea', 'J1_ESC') + RULE % ('j1_far', 'enclosedByArea', 'J1_FAR') + RULE % ('sd_esc', 'enclosedByArea', 'SD_ESC')
C_ok = cond2(DRU_ALL)
C_norule = cond2('(version 1)\n' + RULE % ('j1_esc', 'enclosedByArea', 'J1_ESC') + RULE % ('j1_far', 'enclosedByArea', 'J1_FAR'))   # SD_ESC 영역은 있는데 규칙 없음
C_sdinter = cond2('(version 1)\n' + RULE % ('j1_esc', 'enclosedByArea', 'J1_ESC') + RULE % ('j1_far', 'enclosedByArea', 'J1_FAR') + RULE % ('sd_esc', 'intersectsArea', 'SD_ESC'))
C_bad = cond2('(version 1)\n(rule "j1_esc" (condition "A.Type == \'Via\' && A.intersectsArea(\'J1_ESC\')") (constraint via_diameter (min 0.50mm)))\n')
DRU_OK = DRU_ALL
ROW62 = '| 62 | MDI TX 쌍 길이 차·비결합 예외(O-119, #28 예외) | (다) MDI TX 쌍만: 쌍 안 길이 차 ≤1.27mm, 비결합 길이 ≤7mm(mdi_100_pair 6 → MDI TX 한정 7). 처음 (가)(차 ≤1.7·비결합 6)였으나 갱신 | 근거 | 차선 |\n'
HD = '| # | 항목 |\n|---|---|\n'
X_ok = cond2(DRU_OK, d003=HD + ROW62, tx=1.2, unc=6.5)
X_over = cond2(DRU_OK, d003=HD + ROW62, tx=1.3, unc=7.2)
X_norow = cond2(DRU_OK, d003=HD + '| 28 | 차동쌍 | 쌍 안 길이 차 0 | 근거 | 차선 |\n', tx=1.2, unc=6.5)
X_noarg = cond2(DRU_OK, tx=1.2, unc=6.5)
# D-003 #63: 비결합 셈법 ② + 영역 감시
ROW63 = '| 63 | 고속 쌍 비결합 길이 셈법 | ② #46에서 승인한 탈출·보정 영역(DP_BRK·DP_TUNE, enclosedByArea) 안 구간은 결합으로 셈, 꼬임 영역(DP_TWIST) 제외는 그대로 | 근거 | 차선 |\n'
_at = json.load(open(rj, encoding='utf-8'))['area_table']
BASE = {'carrier': {}}
for _a in _at + E['areas']:   # 0.50/0.20 영역(J1_ · SD_)도 같은 기준으로 감시한다
    _c = BASE['carrier'].setdefault(_a['name'], dict(count=0, area_mm2=0.0)); _c['count'] += 1; _c['area_mm2'] = round(_c['area_mm2'] + _a['area_mm2'], 3)
SMALL = {'carrier': {n: dict(count=c['count'], area_mm2=round(c['area_mm2'] - 0.5, 3)) for n, c in BASE['carrier'].items()}}
FEWER = {'carrier': {n: dict(count=c['count'] - 1, area_mm2=c['area_mm2']) for n, c in BASE['carrier'].items()}}
Y_63 = cond2(DRU_OK, d003=HD + ROW62 + ROW63, tx=1.2, unc=7.5, unc_ar=6.5, base=BASE)
Y_63over = cond2(DRU_OK, d003=HD + ROW62 + ROW63, tx=1.2, unc=7.5, unc_ar=7.2, base=SMALL)
Y_no63 = cond2(DRU_OK, d003=HD + ROW62, tx=1.2, unc=7.5, unc_ar=6.5, base=FEWER)
Y_nobase = cond2(DRU_OK, d003=HD + ROW62 + ROW63, tx=1.2, unc=7.5, unc_ar=6.5, base={})
Y_nopairs = cond2(DRU_OK, d003=HD + ROW62 + ROW63, nopairs=True)
Z_esd_bad = cond2(DRU_OK, esd=[dict(ref='U4', pad='3', n_ok=2, vias=[]), dict(ref='U4', pad='8', n_ok=1, vias=[]), dict(ref='U5', pad='3', n_ok=0, vias=[])])
Z_esd_ok = cond2(DRU_OK, esd=[dict(ref='U4', pad='3', n_ok=2, vias=[]), dict(ref='U4', pad='8', n_ok=1, vias=[])])
# O-123 / D-003 #64 보완: 핀 8 은 핀 3 을 거쳐 ≤1.8 mm 허용
ROW64 = '| 64 | 캐리어 SD ESD 어레이 GND | SD_ESC 에만 0.50/0.20 비아 허용. ESD GND는 핀마다 가능하면 비아 2개, 패드→비아 ≤1mm·폭 ≥0.25. O-123 보완(가): GND 핀 8(U4.8 1.776mm·U5.8 1.421mm)은 같은 GND 핀 3을 거쳐 비아에 닿는 ≤1.8mm 허용, 핀 3 비아는 1개 | 근거 | 차선 |\n'
ROW64_OLD = '| 64 | 캐리어 SD ESD 어레이 GND | SD_ESC 에만 0.50/0.20 비아 허용. ESD GND는 핀마다 가능하면 비아 2개, 패드→비아 ≤1mm·폭 ≥0.25 | 근거 | 차선 |\n'


def P(pad, ln, w=0.25, th=()):
    return dict(ref='U4', pad=pad, n_ok=0, vias=[dict(at=[0, 0], len=ln, min_w=w, ok=ln <= 1.0 and w >= 0.25, through=list(th))])


V6 = lambda r_: r_['_all']['2.V6']
W_ok = cond2(DRU_OK, d003=HD + ROW64, esd=[P('3', 1.0), P('8', 1.776, th=['3'])])
W_old = cond2(DRU_OK, d003=HD + ROW64_OLD, esd=[P('3', 1.0), P('8', 1.776, th=['3'])])
W_long = cond2(DRU_OK, d003=HD + ROW64, esd=[P('3', 1.0), P('8', 1.9, th=['3'])])
W_direct = cond2(DRU_OK, d003=HD + ROW64, esd=[P('3', 1.0), P('8', 1.5)])
W_pin3 = cond2(DRU_OK, d003=HD + ROW64, esd=[P('3', 1.5, th=['8']), P('8', 0.5)])
W_thin = cond2(DRU_OK, d003=HD + ROW64, esd=[P('3', 1.0), P('8', 1.776, w=0.2, th=['3'])])
CASES = [
    ('영역 3개 인식, J1_ESC 는 J1 둘레 1.0 (통과) · J1_FAR 는 멀다 (불합격) · SD_ESC 는 U4·U5 둘레 0.6 (통과)',
     {a['name']: a['beyond_ok'] for a in E['areas']} == {'J1_ESC': True, 'J1_FAR': False, 'SD_ESC': True} and {a['name']: a['group'] for a in E['areas']}['SD_ESC'] == 'SD_'),
    ('#64 SD_ESC 안 0.50/0.20, U4·U5 핀 넷 → 영역 안·넷 통과(음성)', (at(E['inside'], SDok) or {}).get('area') == 'SD_ESC' and at(E['non_j1_net'], SDok) is None),
    ('#64 SD_ESC 안 0.50/0.20, J1 넷이지만 U4·U5 넷 아님 → 불합격(양성)', (at(E['non_j1_net'], SDbad) or {}).get('area') == 'SD_ESC'),
    ('#64 ESD GND: 패드 안 비아 → 조건 맞음(음성)', (esd_via(G_in, PAD0) or {}).get('ok') is True and esd_via(G_in, PAD0)['len'] == 0),
    ('#64 ESD GND: 0.7 mm · 폭 0.25 → 조건 맞음(음성), 다른 패드를 거치지 않음', (esd_via(G_ok, PAD1) or {}).get('ok') is True and abs(esd_via(G_ok, PAD1)['len'] - 0.7) < 0.02
     and esd_via(G_ok, PAD1)['through'] == []),
    ('#64 ESD GND: 폭 0.15 → 조건 안 맞음(양성)', (esd_via(G_thin, PAD2) or {}).get('ok') is False and abs(esd_via(G_thin, PAD2)['min_w'] - 0.15) < 1e-3),
    ('#64 ESD GND: 1.4 mm → 조건 안 맞음(양성)', (esd_via(G_long, PAD3) or {}).get('ok') is False and abs(esd_via(G_long, PAD3)['len'] - 1.4) < 0.02),
    ('O-123 경로가 같은 부품의 다른 GND 패드를 거치면 그 패드 번호와 합친 길이를 기록', (esd_via(G_ok, PAD0) or {}).get('through') == [PAD1[1]]
     and abs(esd_via(G_ok, PAD0)['len'] - (D01 + 0.7)) < 0.03 and esd_via(G_ok, PAD0)['ok'] is False),
    ('#64 cond2 V6: 비아 0 인 핀 1 → 불합격, 1개뿐인 핀은 참고란에(양성)', Z_esd_bad['_all']['2.V6']['pass'] is False and Z_esd_bad['_all']['2.V6']['value'] == 1
     and 'U5.3' in Z_esd_bad['_all']['2.V6']['note'] and 'U4.8' in Z_esd_bad['_all']['2.V6']['note']),
    ('#64 cond2 V6: 모든 핀에 1개 이상 → 통과(음성)', Z_esd_ok['_all']['2.V6']['pass'] is True),
    ('O-123 핀 8 이 핀 3 을 거쳐 1.776 ≤ 1.8 → 통과(음성), 참고란에 경유 길이', V6(W_ok)['pass'] is True and '1.776' in V6(W_ok)['note'] and '1.8' in V6(W_ok)['title']),
    ('O-123 D-003 #64 에 보완 문구가 없으면 1.776 은 불합격(양성)', V6(W_old)['pass'] is False and 'U4.8' in V6(W_old)['note']),
    ('O-123 핀 3 경유라도 1.9 > 1.8 불합격(양성)', V6(W_long)['pass'] is False),
    ('O-123 핀 3 을 거치지 않은 1.5 는 불합격(양성) — 예외는 핀 3 경유만', V6(W_direct)['pass'] is False),
    ('O-123 예외는 핀 8 만 — 핀 3 이 핀 8 을 거쳐 1.5 는 불합격(양성)', V6(W_pin3)['pass'] is False and 'U4.3' in V6(W_pin3)['note']),
    ('O-123 핀 3 경유 1.776 이라도 폭 0.2 는 불합격(양성)', V6(W_thin)['pass'] is False),
    ('#64 cond2 V2: SD_ESC 영역은 있는데 규칙 없음 → 불합격(양성)', C_norule['2.V2']['pass'] is False and 'SD_ESC' in C_norule['2.V2']['note']),
    ('#64 cond2 V2: SD_ESC 규칙이 intersectsArea → 불합격(양성)', C_sdinter['2.V2']['pass'] is False),
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
     E['small_total'] == 15 + len(base) and len(E['outside_small']) == 5 + base_bad and len(E['inside']) == 8 + base_in and len(E['allowed_060']) == 2 + base_ok),
    ('cond2 V1 영역 밖 5(+원래 것 중 허용 아닌 것) 불합격', C_ok['2.V1']['value'] == 5 + base_bad and C_ok['2.V1']['pass'] is False),
    ('cond2 V2 enclosedByArea 통과 / intersectsArea 불합격', C_ok['2.V2']['pass'] is True and C_bad['2.V2']['pass'] is False),
    ('cond2 V3 영역 안 불합격 (B·C·D1·D2 포함)', C_ok['2.V3']['value'] == len(E['inside_fail']) >= 4 and C_ok['2.V3']['pass'] is False),
    ('cond2 V4 J1 넷 아님 (E 포함)', C_ok['2.V4']['value'] == len(E['non_j1_net']) >= 1 and C_ok['2.V4']['pass'] is False),
    ('cond2 V5 J1_FAR 때문에 불합격', C_ok['2.V5']['pass'] is False),
    ('#62 MDI TX 쌍 안 길이 차 1.2 ≤ 1.27 통과(음성) — 옛 문구 속 「≤1.7」은 읽지 않음', X_ok['_a8']['/EPHY_TX']['pass'] is True and '≤1.27 (D-003 #62' in X_ok['_a8']['/EPHY_TX']['limit']),
    ('#62 MDI TX 1.3 > 1.27 불합격(양성)', X_over['_a8']['/EPHY_TX']['pass'] is False),
    ('#62 MDI TX 비결합 6.5 ≤ 7 통과(음성)', X_ok['_a10']['/EPHY_TX']['pass'] is True and '≤7 (D-003 #62' in X_ok['_a10']['/EPHY_TX']['limit']),
    ('#62 MDI TX 비결합 7.2 > 7 불합격(양성)', X_over['_a10']['/EPHY_TX']['pass'] is False),
    ('#62 는 TX 한정 — MDI RX 비결합 6.5 는 ≤6 그대로 불합격(양성)', X_ok['_a10']['/EPHY_RX']['pass'] is False and X_ok['_a10']['/EPHY_RX']['limit'] == '≤6'),
    ('#62 행 없으면 TX 비결합 6.5 도 ≤6 으로 불합격(양성)', X_norow['_a10']['/EPHY_TX']['pass'] is False),
    ('#62 는 TX 한정 — MDI RX 0.5 는 #28 「0」 그대로 불합격(양성)', X_ok['_a8']['/EPHY_RX']['pass'] is False and '#28' in X_ok['_a8']['/EPHY_RX']['limit']),
    ('D-003 에 #62 행이 없으면 예외 없음 — TX 1.2 불합격(양성)', X_norow['_a8']['/EPHY_TX']['pass'] is False),
    ('--d003 을 안 주면 예외 없음 — TX 1.2 불합격(양성)', X_noarg['_a8']['/EPHY_TX']['pass'] is False),
    ('#63 있음: 비결합을 ② 값(6.5)으로 — TX ≤7 통과, ① 값 7.5 는 참고(음성)', Y_63['_a10']['/EPHY_TX']['pass'] is True and Y_63['_a10']['/EPHY_TX']['value'] == 6.5 and '#63' in Y_63['_a10']['/EPHY_TX']['title']
     and '7.5' in Y_63['_a10']['/EPHY_TX']['note']),
    ('#63 있음: RX 는 ② 값 6.5 > 6 불합격(양성)', Y_63['_a10']['/EPHY_RX']['pass'] is False),
    ('#63 있음: TX ② 값 7.2 > 7 불합격(양성)', Y_63over['_a10']['/EPHY_TX']['pass'] is False),
    ('#63 행 없음: ① 값 7.5 로 판정 — TX 불합격(양성)', Y_no63['_a10']['/EPHY_TX']['pass'] is False and Y_no63['_a10']['/EPHY_TX']['value'] == 7.5),
    ('A14 영역 수·면적이 기준과 같으면 통과(음성)', Y_63['_all']['2.A14']['pass'] is True),
    ('A14 기준보다 면적이 큼 → 불합격(양성)', Y_63over['_all']['2.A14']['pass'] is False),
    ('A14 기준보다 영역 수가 많음 → 불합격(양성)', Y_no63['_all']['2.A14']['pass'] is False),
    ('A14 기준 파일에 그 보드가 없음 → 불합격(양성)', Y_nobase['_all']['2.A14']['pass'] is False),
    ('A0 쌍 인식 3 통과(음성) / 쌍 0 이면 불합격(양성)', Y_63['_all']['2.A0']['pass'] is True and Y_63['_all']['2.A0']['value'] >= 3 and Y_nopairs['_all']['2.A0']['pass'] is False),
    ('영역 표 areas.md 가 결과 폴더에 생김', os.path.exists(os.path.join(RES, 'areas.md')) and 'DP_BRK' in open(os.path.join(RES, 'areas.md'), encoding='utf-8').read()),
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
