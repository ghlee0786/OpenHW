# -*- coding: utf-8 -*-
"""v005_silk.py 고장 주입 시험 (KiCad 10 pcbnew).

사용: <KiCad>/bin/python.exe -I test_v005_silk.py [작업 폴더]
합성 보드(.kicad_pcb)를 만들어 판정마다 일부러 위반 하나와 정상 대조 하나를 넣고, v005_silk.py 를 하위 프로세스로 돌려
위반은 잡히고(양성) 대조는 안 잡히는지(음성) 확인한다. 종료 코드 0 = 모든 사례 통과, 1 = 하나라도 실패.
"""
import sys, os, json, subprocess, tempfile
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='v005t_')
os.makedirs(WORK, exist_ok=True)
KBIN = os.path.dirname(sys.executable)
LIB = os.path.join(os.path.dirname(KBIN), 'share', 'kicad', 'footprints')
FM = pcbnew.FromMM


def V(x, y):
    return pcbnew.VECTOR2I(FM(x), FM(y))


b = pcbnew.BOARD()
b.GetDesignSettings().m_SolderMaskExpansion = FM(0.05)
pts = [(100, 100), (160, 100), (160, 140), (100, 140)]
for i in range(4):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(*pts[i])); s.SetEnd(V(*pts[(i + 1) % 4]))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(FM(0.1))
    b.Add(s)


def fp_add(lib, name, ref, x, y, rot=0.0, ref_at=None, ref_layer=pcbnew.F_SilkS):
    fp = pcbnew.FootprintLoad(os.path.join(LIB, lib + '.pretty'), name)
    assert fp is not None, (lib, name)
    fp.SetReference(ref)
    b.Add(fp)
    fp.SetPosition(V(x, y))
    fp.SetOrientationDegrees(rot)
    r = fp.Reference()
    r.SetLayer(ref_layer)
    r.SetVisible(True)
    r.SetTextSize(pcbnew.VECTOR2I(FM(1.0), FM(1.0)))
    r.SetTextThickness(FM(0.2))
    r.SetTextAngleDegrees(0)
    r.SetPosition(V(*(ref_at or (x, y - 2.0))))
    # 라이브러리 안의 ${REFERENCE} 사용자 글자는 Fab 에 그대로 둔다
    return fp


def line(x0, y0, x1, y1, w=0.15, layer=pcbnew.F_SilkS):
    s = pcbnew.PCB_SHAPE(b)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(V(x0, y0)); s.SetEnd(V(x1, y1))
    s.SetLayer(layer); s.SetWidth(FM(w))
    b.Add(s)


def text(t, x, y, h=1.0, th=0.2, ang=0.0, layer=pcbnew.F_SilkS, mirror=False):
    o = pcbnew.PCB_TEXT(b)
    o.SetText(t)
    o.SetLayer(layer)
    o.SetTextSize(pcbnew.VECTOR2I(FM(h), FM(h)))
    o.SetTextThickness(FM(th))
    o.SetPosition(V(x, y))
    o.SetTextAngleDegrees(ang)
    o.SetMirrored(mirror)
    b.Add(o)


def set_fn(fp, m):
    for p in fp.Pads():
        if p.GetNumber() in m:
            p.SetPinFunction(m[p.GetNumber()])


def strip_silk(fp, only_filled=False):
    for g in list(fp.GraphicalItems()):
        if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS):
            if not only_filled or g.IsSolidFill() or g.GetShape() == pcbnew.SHAPE_T_POLY:
                fp.Remove(g)


# ---- 부품 ----
R1 = fp_add('Resistor_SMD', 'R_0402_1005Metric', 'R1', 110, 110)             # 정상 참조(음성)
R2 = fp_add('Resistor_SMD', 'R_0402_1005Metric', 'R2', 120, 110)             # S2 대상 패드
U1 = fp_add('Package_SO', 'SOIC-8_3.9x4.9mm_P1.27mm', 'U1', 128, 122)        # S6 courtyard
R3 = fp_add('Resistor_SMD', 'R_0402_1005Metric', 'R3', 140, 112, ref_at=(128, 122))   # 참조가 U1 아래 → S6 숨음
R4 = fp_add('Resistor_SMD', 'R_0402_1005Metric', 'R4', 105, 130, ref_at=(105, 125.5))  # 참조가 멀다 → S6a far
R5 = fp_add('Resistor_SMD', 'R_0402_1005Metric', 'R5', 112, 130, ref_at=(116.2, 128.8))  # R6 쪽에 붙음 → S6a 모호
R6 = fp_add('Resistor_SMD', 'R_0402_1005Metric', 'R6', 116.2, 130, ref_at=(116.2, 132.2))
D10 = fp_add('Diode_SMD', 'D_SOD-323', 'D10', 108, 104); set_fn(D10, {'1': 'K', '2': 'A'})       # S9 ok
D11 = fp_add('Diode_SMD', 'D_SOD-323', 'D11', 116, 104); set_fn(D11, {'1': 'A', '2': 'K'})       # S9 wrong_side
D12 = fp_add('LED_SMD', 'LED_0603_1608Metric', 'D12', 124, 104); set_fn(D12, {'1': 'K', '2': 'A'}); strip_silk(D12)  # S9 missing
Q10 = fp_add('Package_TO_SOT_SMD', 'SOT-23', 'Q10', 134, 104)                # S9 ok
Q11 = fp_add('Package_TO_SOT_SMD', 'SOT-23', 'Q11', 142, 104); strip_silk(Q11, only_filled=True)  # 삼각 표시 제거 → missing
Q12 = fp_add('Package_TO_SOT_SMD', 'SOT-23', 'Q12', 150, 104, rot=90)        # 회전해도 ok
J10 = fp_add('Connector_USB', 'USB_C_Receptacle_HRO_TYPE-C-31-M-12', 'J10', 150, 128, rot=90)  # 면제

# ---- 실크 위반 ----
line(109.0, 110.0, 109.6, 110.0)                 # S1: R1 패드 1(x 109.49) 위로 지남
line(120.3, 109.455, 120.7, 109.455)              # S2: R2 패드 2 위 모서리(y 109.68) + 확장 0.05 → 잉크 아래 가장자리 109.53, 간격 0.10
line(120.3, 108.0, 120.7, 108.0)                 # S2 음성: 1.6 떨어짐
line(130.0, 113.0, 134.0, 113.0, w=0.10)         # S3 양성
line(130.0, 115.0, 134.0, 115.0, w=0.15)         # S3 음성
text('H08', 104, 116, h=0.8, th=0.16)            # S4 높이
text('T12', 110, 116, h=1.0, th=0.12)            # S4 획
text('R15', 116, 116, h=1.0, th=0.15)            # S4r 비율만
text('OKT', 104, 120, h=1.0, th=0.2)             # 음성
text('EDGE', 130, 100.3, h=1.0, th=0.2)          # S5 외곽
text('AAA', 140, 118, h=1.0, th=0.2); text('BBB', 140.3, 118.2, h=1.0, th=0.2)   # S7 글자 겹침
text('LIN', 146, 118, h=1.0, th=0.2); line(144.5, 118, 147.5, 118)              # S7l 글자–선
text('SPA', 140, 124, h=1.0, th=0.2); line(138.0, 124.72, 142.0, 124.72)         # S7s 간격 < 0.127 (글자 잉크 아래 약 124.6, 선 위 가장자리 124.645)
text('A90', 104, 136, ang=90); text('A180', 110, 136, ang=180)                  # S8 앞면 각도 0·90·180 → 3종
text('BNM', 120, 136, layer=pcbnew.B_SilkS, mirror=False)                        # S8m 뒷면 비거울
via = pcbnew.PCB_VIA(b); via.SetPosition(V(135, 132)); via.SetWidth(FM(0.6)); via.SetDrill(FM(0.3)); b.Add(via)
via.SetFrontTentingMode(pcbnew.TENTING_MODE_NOT_TENTED); via.SetBackTentingMode(pcbnew.TENTING_MODE_NOT_TENTED)
line(134.0, 132.0, 136.0, 132.0)                 # S1v·S1h 안 덮인 비아 위 → 불합격
via2 = pcbnew.PCB_VIA(b); via2.SetPosition(V(141, 132)); via2.SetWidth(FM(0.6)); via2.SetDrill(FM(0.3)); b.Add(via2)
via2.SetFrontTentingMode(pcbnew.TENTING_MODE_TENTED); via2.SetBackTentingMode(pcbnew.TENTING_MODE_TENTED)
line(140.0, 132.0, 142.0, 132.0)                 # 덮인 비아 위 → 허용 (D-003 #58)

pcb = os.path.join(WORK, 'inject.kicad_pcb')
pcbnew.SaveBoard(pcb, b)
out = os.path.join(WORK, 'inject.json')
rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v005_silk.py'), pcb, out], capture_output=True, text=True, encoding='utf-8')
if rc.returncode != 0:
    print('v005_silk.py 실패', rc.returncode, rc.stderr[-2000:])
    sys.exit(1)
R = json.load(open(out, encoding='utf-8'))
F = R['findings']
P1 = {c['ref']: c for c in R['pin1_candidates']}


def has(key, pred):
    return any(pred(x) for x in F[key])


def near(at, x, y, tol=0.6):
    return abs(at[0] - x) < tol and abs(at[1] - y) < tol


def S2dist():
    xs = [x['dist'] for x in F['S2_clear_lt_0p15'] if x['owner'] == '(보드)' and near(x['at'], 120.5, 109.455)]
    return xs[0] if xs else None


CASES = [
    ('S1 패드 위 실크(양성)', has('S1_on_mask_open', lambda x: x['owner'] == '(보드)' and near(x['at'], 109.3, 110.0))),
    ('S2 간격 0.10 잡음(양성)', S2dist() is not None and abs(S2dist() - 0.10) <= 0.012),
    ('S2 1.6 떨어진 선(음성)', not has('S2_clear_lt_0p15', lambda x: x['owner'] == '(보드)' and near(x['at'], 120.5, 108.0))),
    ('S3 선폭 0.10(양성)', has('S3_line_lt_0p15', lambda x: near(x['at'], 132, 113))),
    ('S3 선폭 0.15(음성)', not has('S3_line_lt_0p15', lambda x: near(x['at'], 132, 115))),
    ('S4 높이 0.8(양성)', has('S4_text', lambda x: x.get('text') == 'H08')),
    ('S4 획 0.12(양성)', has('S4_text', lambda x: x.get('text') == 'T12')),
    ('S4r 1:5 미만(양성)', has('S4r_ratio_lt_1to5', lambda x: x.get('text') == 'R15') and not has('S4_text', lambda x: x.get('text') == 'R15')),
    ('S4 1.0/0.2(음성)', not has('S4_text', lambda x: x.get('text') == 'OKT') and not has('S4r_ratio_lt_1to5', lambda x: x.get('text') == 'OKT')),
    ('S5 외곽(양성)', has('S5_edge', lambda x: x.get('text') == 'EDGE' and x['area_outside_board'] > 0)),
    ('S5 안쪽 글자(음성)', not has('S5_edge', lambda x: x.get('text') == 'OKT')),
    ('S6 부품 아래 참조(양성)', has('S6_ref_hidden', lambda x: x.get('text') == 'R3' and x['under'] == 'U1')),
    ('S6 정상 참조(음성)', not has('S6_ref_hidden', lambda x: x.get('text') == 'R1') and not has('S6a_ref_far', lambda x: x.get('text') == 'R1')
     and not has('S6a_ref_ambiguous', lambda x: x.get('text') == 'R1')),
    ('S6a 먼 참조(양성)', has('S6a_ref_far', lambda x: x.get('text') == 'R4')),
    ('S6a 모호한 참조(양성)', has('S6a_ref_ambiguous', lambda x: x.get('text') == 'R5' and x['nearer'] == 'R6')),
    ('S7 글자 겹침(양성)', has('S7_text_text', lambda x: {x['text'].get('text'), x['other'].get('text')} == {'AAA', 'BBB'})),
    ('S7l 글자–선(양성)', has('S7l_text_line', lambda x: x['text'].get('text') == 'LIN')),
    ('S7s 간격 < 0.127(양성)', has('S7s_text_space', lambda x: x['text'].get('text') == 'SPA')),
    ('S7 떨어진 글자(음성)', not has('S7_text_text', lambda x: 'OKT' in (x['text'].get('text'), x['other'].get('text')))),
    ('S8 앞면 3방향(양성)', has('S8_orient_gt2', lambda x: x['side'] == 'F')),
    ('S8m 뒷면 비거울(양성)', has('S8m_mirror', lambda x: x.get('text') == 'BNM')),
    ('S1v 안 덮인 비아 위 실크(양성)', has('S1v_over_via', lambda x: near(x['at'], 135, 132))),
    ('S1h 안 덮인 비아 구멍 위 실크(양성)', has('S1h_over_hole', lambda x: near(x['at'], 135, 132))),
    ('S1v·S1h·S1 덮인(tented) 비아 위 실크 허용(음성, D-003 #58)', not any(has(k, lambda x: near(x['at'], 141, 132)) for k in ('S1v_over_via', 'S1h_over_hole', 'S1_on_mask_open'))),
    ('S9 다이오드 캐소드 쪽 표시 ok(음성)', P1.get('D10', {}).get('verdict') in ('ok', 'ok_marker')),
    ('S9 캐소드 반대쪽 표시 wrong_side(양성)', P1.get('D11', {}).get('verdict') == 'wrong_side'),
    ('S9 LED 표시 없음 missing(양성)', P1.get('D12', {}).get('verdict') == 'missing'),
    ('S9 SOT-23 삼각 ok(음성)', P1.get('Q10', {}).get('verdict') in ('ok', 'ok_marker')),
    ('S9 SOT-23 삼각 지움 missing(양성)', P1.get('Q11', {}).get('verdict') == 'missing'),
    ('S9 SOT-23 90° 회전 ok(음성)', P1.get('Q12', {}).get('verdict') in ('ok', 'ok_marker')),
    ('S9 USB-C 면제', P1.get('J10', {}).get('verdict') == 'exempt'),
    # V-006a: 참조 필드는 Reference()·GetFields() 두 길로 나옴 — 한 번만 센다 (부품 14개 모두 앞면 실크 참조)
    ('참조 한 번만 셈 (앞면 실크 참조 14)', R['counts']['F']['ref'] == 14),
    ('S7 자기 참조끼리 겹침 없음(음성)', not has('S7_text_text', lambda x: x['text'].get('owner') == x['other'].get('owner') and x['text'].get('at') == x['other'].get('at'))),
]
fail = 0
for name, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', name))
    fail += 0 if ok else 1
if fail:
    print('--- 진단', json.dumps({k: P1[k] for k in ('D10', 'D11', 'D12', 'Q10', 'Q11', 'Q12') if k in P1}, ensure_ascii=False)[:3000])
    print('S2', [(x['owner'], x['at'], x['dist']) for x in F['S2_clear_lt_0p15'] if x['owner'] == '(보드)'])
print('사례 %d · 실패 %d · 보드 %s' % (len(CASES), fail, pcb))
sys.exit(1 if fail else 0)
