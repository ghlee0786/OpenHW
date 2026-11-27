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
base = [(mm(t.GetPosition().x), mm(t.GetPosition().y), mm(t.GetWidth(pcbnew.F_Cu)) / 2) for t in b.Tracks()
        if t.GetClass() == 'PCB_VIA' and (mm(t.GetWidth(pcbnew.F_Cu)) < 0.65 - 1e-6 or mm(t.GetDrill()) < 0.30 - 1e-6)]
base_in = sum(1 for x, y, r in base if X0 <= x - r and x + r <= X1 and Y0 <= y - r and y + r <= Y1)
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


area('J1_ESC', X0, Y0, X1, Y1)
area('J1_FAR', X0 - 8.0, Y0, X0 - 6.0, Y0 + 2.0)                 # J1 에서 5 mm 넘게 떨어진 영역 → V5 불합격
sp = free_spots(6, X0, Y0, X1, Y1)
N = j1_nets[0]
A_ = via(sp[0][0], sp[0][1], 0.50, 0.20, N)                      # 정상
B_ = via(sp[1][0], sp[1][1], 0.45, 0.20, N)                      # 지름·링 미달
C_ = via(sp[2][0], sp[2][1], 0.50, 0.15, N)                      # 드릴 미달
D1 = via(sp[3][0], sp[3][1], 0.50, 0.20, N)                      # 구멍 간격 0.25 (중심 0.45)
D2 = via(sp[3][0] + 0.45, sp[3][1], 0.50, 0.20, N)
E_ = via(sp[4][0], sp[4][1], 0.50, 0.20, other_net)              # J1 넷 아님
G_ = via(X0, sp[5][1], 0.50, 0.20, N)                            # 영역 가장자리에 걸침
far = free_spots(2, X1 + 6.0, Y0, X1 + 14.0, Y1)
F_ = via(far[0][0], far[0][1], 0.50, 0.20, N)                    # 영역 밖 작은 비아
H_ = via(far[1][0], far[1][1], 0.60, 0.30, N)                    # 영역 밖 0.60/0.30 (#21 0.65 미달)
S_ = via(far[1][0], far[1][1] + 3.0, 0.65, 0.30, N)              # 표준 → 세지 않음
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


def cond2(dru):
    open(os.path.join(BD, 'carrier.kicad_dru'), 'w', encoding='utf-8').write(dru)
    json.dump(dict(violations=[], unconnected_items=[], schematic_parity=[]), open(os.path.join(RES, 'drc_carrier.json'), 'w'))
    o = os.path.join(RES, 'cond2.json')
    subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v006_cond2.py'), RES, 'test', o, '--snap', os.path.join(W, 'snap'), '--root', W],
                   capture_output=True, text=True, encoding='utf-8')
    return {i['id']: i for i in json.load(open(o, encoding='utf-8'))['items'] if i['board'] == 'carrier'}


C_ok = cond2('(version 1)\n(rule "j1_esc" (condition "A.Type == \'Via\' && A.enclosedByArea(\'J1_ESC\')") (constraint via_diameter (min 0.50mm)))\n')
C_bad = cond2('(version 1)\n(rule "j1_esc" (condition "A.Type == \'Via\' && A.intersectsArea(\'J1_ESC\')") (constraint via_diameter (min 0.50mm)))\n')
CASES = [
    ('영역 2개 인식, J1_ESC 는 J1 둘레 1.0 (통과) · J1_FAR 는 멀다 (불합격)', {a['name']: a['beyond_ok'] for a in E['areas']} == {'J1_ESC': True, 'J1_FAR': False}),
    ('A 정상 0.50/0.20 → 영역 안, 불합격 아님(음성)', at(E['inside'], A_) is not None and at(E['inside_fail'], A_) is None and at(E['non_j1_net'], A_) is None),
    ('B 0.45/0.20 → 지름·링 미달(양성)', '지름' in why(B_) and '링' in why(B_)),
    ('C 0.50/0.15 → 드릴 미달(양성)', '드릴' in why(C_)),
    ('D 구멍 간격 0.25 두 비아 모두(양성)', '구멍 간격' in why(D1) and '구멍 간격' in why(D2) and abs(at(E['inside'], D1)['hole_gap'] - 0.25) < 0.005),
    ('E J1 넷 아닌 작은 비아(양성)', at(E['non_j1_net'], E_) is not None),
    ('G 영역에 걸친 비아 → 밖으로 셈 + 걸침(양성)', at(E['outside_small'], G_) is not None and at(E['straddle_small'], G_) is not None),
    ('F 영역 밖 0.50/0.20(양성)', at(E['outside_small'], F_) is not None and at(E['straddle_small'], F_) is None),
    ('H 영역 밖 0.60/0.30 — #21 0.65 미달(양성)', at(E['outside_small'], H_) is not None),
    ('S 0.65/0.30 은 세지 않음(음성) — 원래 있던 작은 비아 %d(영역 안 %d) 더함' % (len(base), base_in),
     E['small_total'] == 9 + len(base) and len(E['outside_small']) == 3 + len(base) - base_in and len(E['inside']) == 6 + base_in),
    ('cond2 V1 영역 밖 3(+원래 것) 불합격', C_ok['2.V1']['value'] == 3 + len(base) - base_in and C_ok['2.V1']['pass'] is False),
    ('cond2 V2 enclosedByArea 통과 / intersectsArea 불합격', C_ok['2.V2']['pass'] is True and C_bad['2.V2']['pass'] is False),
    ('cond2 V3 영역 안 불합격 (B·C·D1·D2 포함)', C_ok['2.V3']['value'] == len(E['inside_fail']) >= 4 and C_ok['2.V3']['pass'] is False),
    ('cond2 V4 J1 넷 아님 (E 포함)', C_ok['2.V4']['value'] == len(E['non_j1_net']) >= 1 and C_ok['2.V4']['pass'] is False),
    ('cond2 V5 J1_FAR 때문에 불합격', C_ok['2.V5']['pass'] is False),
]
fail = 0
for n, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', n)); fail += 0 if ok else 1
if fail:
    print(json.dumps(E, ensure_ascii=False)[:4000])
print('사례 %d · 실패 %d · 폴더 %s' % (len(CASES), fail, W))
sys.exit(1 if fail else 0)
