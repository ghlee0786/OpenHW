# -*- coding: utf-8 -*-
"""v005_excl.py 고장 주입 시험 (KiCad 10 pcbnew). O-74 판정 E1~E4.

사용: <KiCad>/bin/python.exe -I test_v005_excl.py [작업 폴더]
합성 프로젝트(보드 · .kicad_pro 제외 목록 · .kicad_dru · fp-lib-table · openhw.pretty 사본 · pcb 문서)를 만들고
v005_excl.py 를 하위 프로세스로 돌려 위반은 잡히고 정상은 통과하는지 본다. 종료 0 = 전부 통과, 1 = 실패.
"""
import sys, os, re, json, shutil, subprocess, tempfile
import pcbnew

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = sys.argv[1] if len(sys.argv) > 1 else tempfile.mkdtemp(prefix='v005e_')
if os.path.isdir(WORK):
    shutil.rmtree(WORK)
os.makedirs(WORK)
KFP = os.path.join(os.path.dirname(os.path.dirname(sys.executable)), 'share', 'kicad', 'footprints')
FM = pcbnew.FromMM
SILK = (pcbnew.F_SilkS, pcbnew.B_SilkS)


def V(x, y):
    return pcbnew.VECTOR2I(FM(x), FM(y))


def load(lib, name):
    fp = pcbnew.FootprintLoad(os.path.join(KFP, lib + '.pretty'), name)
    assert fp is not None, (lib, name)
    return fp


def drop_silk(fp, keep_first=False):
    gs = [g for g in fp.GraphicalItems() if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() in SILK]
    for g in gs[1 if keep_first else 0:]:
        fp.Remove(g)


# ---- openhw.pretty 사본 ----
OH = os.path.join(WORK, 'openhw.pretty')
IO = pcbnew.PCB_IO_KICAD_SEXPR()  # FootprintLibCreate/FootprintSave 는 KiCad 10 파이썬에서 플러그인을 못 찾는다
IO.CreateLibrary(OH)
c1 = load('Resistor_SMD', 'R_0402_1005Metric'); drop_silk(c1, keep_first=True)          # 실크만 바뀐 사본(정상)
IO.FootprintSave(OH, c1)
c2 = load('Package_TO_SOT_SMD', 'SOT-23')                                                 # 패드를 0.1 옮긴 사본(불합격)
p = [x for x in c2.Pads() if x.GetNumber() == '1'][0]; p.SetPosition(p.GetPosition() + V(0.1, 0))
IO.FootprintSave(OH, c2)
c3 = load('Connector_PinHeader_2.54mm', 'PinHeader_1x02_P2.54mm_Vertical')               # 정상 THT 사본(드릴 비교 기준)
IO.FootprintSave(OH, c3)
c4 = load('Resistor_SMD', 'R_0603_1608Metric')                                            # Fab 선을 지운 사본(실크 밖 차이 → 불합격)
for g in [g for g in c4.GraphicalItems() if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() == pcbnew.F_Fab][:1]:
    c4.Remove(g)
IO.FootprintSave(OH, c4)
# ---- O-74b: 실크 사본 폴더(fp-lib-table 별칭을 돌림) + SOURCES.tsv ----
import hashlib


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def kfp(lib, name):
    return os.path.join(KFP, lib + '.pretty', name + '.kicad_mod')


SILK_DIR = os.path.join(WORK, 'hardware', 'pcb', 'lib', 'silk', 'front')
SR = os.path.join(SILK_DIR, 'Resistor_SMD.pretty')
SP = os.path.join(SILK_DIR, 'Package_TO_SOT_SMD.pretty')
OHR = os.path.join(WORK, 'hardware', 'libraries', 'openhw.pretty')     # 저장소 openhw 원본(별칭:이름 표기 시험)
for d in (SR, SP, OHR):
    os.makedirs(d)
# 사본은 .kicad_mod 텍스트를 직접 고쳐 만든다: KiCad 10 SWIG 는 같은 풋프린트를 여러 번 읽거나 복제하면 형 변환이 깨진다.


def spans(t, heads):
    """최상위 풋프린트 안의 (head …) 블록 [시작, 끝) 목록"""
    out, i = [], 0
    while True:
        k = min([x for x in (t.find('(' + h, i) for h in heads) if x >= 0] or [-1])
        if k < 0:
            return out
        d, j = 0, k
        while True:
            if t[j] == '(':
                d += 1
            elif t[j] == ')':
                d -= 1
                if d == 0:
                    break
            j += 1
        out.append((k, j + 1))
        i = j + 1


GR = ('fp_line', 'fp_arc', 'fp_circle', 'fp_poly', 'fp_rect')


def txt(lib, name):
    return open(kfp(lib, name), encoding='utf-8').read()


def cut(t, sp):
    for a_, b_ in sorted(sp, reverse=True):
        t = t[:a_] + t[b_:]
    return t


def t_drop_silk(t, keep_first=True):
    sp = [x for x in spans(t, GR) if '(layer "F.SilkS")' in t[x[0]:x[1]]]
    return cut(t, sp[1 if keep_first else 0:])


def t_drop_fab(t):
    sp = [x for x in spans(t, GR) if '(layer "F.Fab")' in t[x[0]:x[1]]]
    return cut(t, sp[:1])


def t_move_pad(t, num, dy):
    for a_, b_ in spans(t, ('pad ',)):
        blk = t[a_:b_]
        if blk.startswith('(pad "%s"' % num):
            m = re.search(r'\(at ([-\d.]+) ([-\d.]+)', blk)
            nb = blk[:m.start()] + '(at %s %s' % (m.group(1), repr(round(float(m.group(2)) + dy, 4))) + blk[m.end():]
            return t[:a_] + nb + t[b_:]
    raise AssertionError('pad')


def t_rename(t, new):
    return re.sub(r'^\(footprint "[^"]+"', '(footprint "%s"' % new, t, count=1)


def put(d, name, t):
    open(os.path.join(d, name + '.kicad_mod'), 'w', encoding='utf-8').write(t)


put(SR, 'R_0402_1005Metric', t_drop_silk(txt('Resistor_SMD', 'R_0402_1005Metric')))            # 실크만 → 통과
put(SR, 'R_0603_1608Metric', txt('Resistor_SMD', 'R_0603_1608Metric'))                           # 기록 sha 틀림 → 불합격
put(SR, 'R_0805_2012Metric', txt('Resistor_SMD', 'R_0805_2012Metric'))                           # SOURCES 행 없음 → 불합격
put(SP, 'SOT-23', t_move_pad(txt('Package_TO_SOT_SMD', 'SOT-23'), '2', 0.05))                     # 패드 → 불합격
put(SP, 'SOT-23-5', t_drop_fab(txt('Package_TO_SOT_SMD', 'SOT-23-5')))                            # Fab → 불합격
put(OHR, 'SOT-23_OH', t_rename(txt('Package_TO_SOT_SMD', 'SOT-23'), 'SOT-23_OH'))
put(SP, 'SOT-23_OH', t_drop_silk(t_rename(txt('Package_TO_SOT_SMD', 'SOT-23'), 'SOT-23_OH')))     # openhw 원본, 실크만 → 통과
oh_file = os.path.join(OHR, 'SOT-23_OH.kicad_mod')
# V-006a: 프로젝트 라이브러리 별칭(OpenHW_Mech → hardware/pcb/lib/OpenHW_Mech.pretty) 원본
PMR = os.path.join(WORK, 'hardware', 'pcb', 'lib', 'OpenHW_Mech.pretty'); os.makedirs(PMR)
put(PMR, 'SOT-23_PM', t_rename(txt('Package_TO_SOT_SMD', 'SOT-23'), 'SOT-23_PM'))
put(SP, 'SOT-23_PM', t_drop_silk(t_rename(txt('Package_TO_SOT_SMD', 'SOT-23'), 'SOT-23_PM')))     # 프로젝트 원본, 실크만 → 통과
pm_file = os.path.join(PMR, 'SOT-23_PM.kicad_mod')
open(os.path.join(OHR, 'SOT-23_OH2.kicad_mod'), 'w', encoding='utf-8', newline='\n').write(t_rename(txt('Package_TO_SOT_SMD', 'SOT-23'), 'SOT-23_OH2'))  # 원본은 LF (put 은 윈도우에서 CRLF)
put(SP, 'SOT-23_OH2', t_drop_silk(t_rename(txt('Package_TO_SOT_SMD', 'SOT-23'), 'SOT-23_OH2')))
oh2_file = os.path.join(OHR, 'SOT-23_OH2.kicad_mod')
rows = [
    ('Resistor_SMD.pretty/R_0402_1005Metric.kicad_mod', '${KICAD10_FOOTPRINT_DIR}/Resistor_SMD.pretty/R_0402_1005Metric.kicad_mod', sha(kfp('Resistor_SMD', 'R_0402_1005Metric'))),
    ('Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod', '${KICAD10_FOOTPRINT_DIR}/Resistor_SMD.pretty/R_0603_1608Metric.kicad_mod', '0' * 64),
    ('Resistor_SMD.pretty/R_1206_3216Metric.kicad_mod', '${KICAD10_FOOTPRINT_DIR}/Resistor_SMD.pretty/R_1206_3216Metric.kicad_mod', sha(kfp('Resistor_SMD', 'R_1206_3216Metric'))),  # 사본 파일 없음
    ('Package_TO_SOT_SMD.pretty/SOT-23.kicad_mod', kfp('Package_TO_SOT_SMD', 'SOT-23').replace('\\', '/'), sha(kfp('Package_TO_SOT_SMD', 'SOT-23'))),  # 절대 경로
    ('Package_TO_SOT_SMD.pretty/SOT-23-5.kicad_mod', '/opt/kicad/share/kicad/footprints/Package_TO_SOT_SMD.pretty/SOT-23-5.kicad_mod', sha(kfp('Package_TO_SOT_SMD', 'SOT-23-5'))),  # 다른 PC 절대 경로 → 이 PC KiCad
    ('Package_TO_SOT_SMD.pretty/SOT-23_OH.kicad_mod', 'openhw:SOT-23_OH', sha(oh_file)),
    # V-006e: 이름이 이 라이브러리 이름으로 시작하는 다른 라이브러리의 행 — Resistor_SMD 의 「사본 파일 없음」으로 잡히면 안 된다
    ('Resistor_SMDX.pretty/R_ZZZ.kicad_mod', '${KICAD10_FOOTPRINT_DIR}/Resistor_SMD.pretty/R_0402_1005Metric.kicad_mod', sha(kfp('Resistor_SMD', 'R_0402_1005Metric'))),
    ('Package_TO_SOT_SMD.pretty/SOT-23_PM.kicad_mod', 'OpenHW_Mech:SOT-23_PM', sha(pm_file)),
    # V-006a: 기록 sha 가 CRLF 형태(autocrlf worktree 에서 잼) — 같은 원본으로 통과
    ('Package_TO_SOT_SMD.pretty/SOT-23_OH2.kicad_mod', 'openhw:SOT-23_OH2', hashlib.sha256(open(oh2_file, 'rb').read().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')).hexdigest()),
]
open(os.path.join(SILK_DIR, 'SOURCES.tsv'), 'w', encoding='utf-8').write('copy\tsource\tsha256\n' + ''.join('%s\t%s\t%s\n' % r for r in rows))
open(os.path.join(WORK, 'fp-lib-table'), 'w', encoding='utf-8').write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "openhw")(type "KiCad")(uri "${KIPRJMOD}/openhw.pretty")(options "")(descr ""))\n'
    '  (lib (name "Resistor_SMD") (type "KiCad") (uri "${KIPRJMOD}/hardware/pcb/lib/silk/front/Resistor_SMD.pretty") (options "") (descr "O-74b"))\n'
    '  (lib (name "Package_TO_SOT_SMD")(type "KiCad")(uri "${KIPRJMOD}/hardware/pcb/lib/silk/front/Package_TO_SOT_SMD.pretty")(options "")(descr "O-74b"))\n)\n')

# ---- 보드: openhw 사본 인스턴스 ----
b = pcbnew.BOARD()


BASE = {}


def place(name, ref, x, y, rot=0, flip=False, mutate=None):
    if name not in BASE:
        BASE[name] = IO.FootprintLoad(OH, name)
    fp = pcbnew.FOOTPRINT(BASE[name])  # 같은 이름을 다시 불러오면 KiCad 10 SWIG 가 FOOTPRINT 로 못 바꾼다 → 한 번 읽어 복제
    fp.ResetUuidDirect()  # 복제는 UUID 를 그대로 가져가 제외 목록 매핑이 겹친다 → 새 UUID
    fp.SetFPID(pcbnew.LIB_ID('openhw', name))
    fp.SetReference(ref)
    b.Add(fp)
    fp.SetPosition(V(x, y))
    if flip:
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(rot)
    if mutate:
        mutate(fp)
    return fp


def silk_cut(fp):  # 위치별 실크 자름(O-74 의도): 인스턴스 실크 선 하나 지움
    gs = [g for g in fp.GraphicalItems() if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() in SILK]
    if gs:
        fp.Remove(gs[0])


def pad_grow(fp):  # 패드 크기 변경(불합격)
    p = [x for x in fp.Pads() if x.GetNumber() == '1'][0]
    p.SetSize(pcbnew.F_Cu, pcbnew.VECTOR2I(p.GetSize(pcbnew.F_Cu).x + FM(0.1), p.GetSize(pcbnew.F_Cu).y))


def drill_grow(fp):  # 구멍 변경(불합격)
    p = [x for x in fp.Pads() if x.GetNumber() == '1'][0]
    p.SetDrillSize(pcbnew.VECTOR2I(FM(1.2), FM(1.2)))


def fab_move(fp):  # Fab 선 이동(실크 밖 차이 → 불합격)
    g = [g for g in fp.GraphicalItems() if g.GetClass() == 'PCB_SHAPE' and g.GetLayer() in (pcbnew.F_Fab, pcbnew.B_Fab)][0]
    g.Move(V(0.2, 0))


R1 = place('R_0402_1005Metric', 'R1', 110, 110)                         # 그대로(정상)
R2 = place('R_0402_1005Metric', 'R2', 115, 110, rot=90, mutate=silk_cut)  # 실크만 자름(정상, 제외 대상)
R3 = place('R_0402_1005Metric', 'R3', 120, 110, mutate=pad_grow)         # 패드 바뀜(불합격, 제외 대상)
R4 = place('R_0402_1005Metric', 'R4', 125, 110, rot=180, flip=True, mutate=silk_cut)  # 뒷면 + 실크만(정상)
R5 = place('R_0402_1005Metric', 'R5', 130, 110, mutate=fab_move)         # Fab 바뀜(불합격)
J1 = place('PinHeader_1x02_P2.54mm_Vertical', 'J1', 140, 110, mutate=drill_grow)  # 구멍 바뀜(불합격)
J2 = place('PinHeader_1x02_P2.54mm_Vertical', 'J2', 145, 110, rot=90)    # THT 그대로(정상)
pcb = os.path.join(WORK, 't.kicad_pcb')
pcbnew.SaveBoard(pcb, b)
b2 = pcbnew.LoadBoard(pcb)
U = {fp.GetReference(): fp.m_Uuid.AsString() for fp in b2.Footprints()}
Z = '00000000-0000-0000-0000-000000000000'

# ---- .kicad_pro 제외 · ignore, .kicad_dru, 문서 ----
pro = json.load(open(os.path.join(WORK, 't.kicad_pro'), encoding='utf-8')) if os.path.exists(os.path.join(WORK, 't.kicad_pro')) else {}
pro.setdefault('board', {}).setdefault('design_settings', {})
pro['board']['design_settings']['drc_exclusions'] = [
    ['lib_footprint_mismatch|115000000|110000000|%s|%s' % (U['R2'], Z), 'O-74 R2 실크 자름'],
    ['lib_footprint_mismatch|120000000|110000000|%s|%s' % (U['R3'], Z), 'O-74 R3'],
    'lib_footprint_mismatch|125000000|110000000|%s|%s' % (U['R4'], Z),                 # 주석 없음 → 경고
    ['clearance|130000000|110000000|%s|%s' % (U['R5'], U['R1']), 'O-74 잘못 쓴 종류'],  # 허용 밖 종류 → 불합격
]
pro['board']['design_settings']['rule_severities'] = {'silk_overlap': 'ignore', 'clearance': 'error'}
json.dump(pro, open(os.path.join(WORK, 't.kicad_pro'), 'w', encoding='utf-8'), indent=1)
open(os.path.join(WORK, 't.kicad_dru'), 'w', encoding='utf-8').write(
    '(version 1)\n(rule "keep"\n  (constraint clearance (min 0.16mm)))\n\n(rule "hide_silk"\n  (layer "?.Silkscreen")\n  (severity ignore)\n  (constraint silk_clearance (min 0.15mm)))\n')
doc = os.path.join(WORK, 'pcb-notes.md')
open(doc, 'w', encoding='utf-8').write('# 메모\n- O-74 실크 자름 제외 (front): R2, R4, R9\n- 다른 줄 R7 (관계없는 메모)\n- O-74 carrier: R3\n')

out = os.path.join(WORK, 'excl.json')
rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v005_excl.py'), pcb, out, '--doc', doc, '--board-name', 'front', '--repo-root', WORK],
                    capture_output=True, text=True, encoding='utf-8')
if rc.returncode != 0:
    print('v005_excl.py 실패', rc.returncode, rc.stderr[-2000:]); sys.exit(1)
R = json.load(open(out, encoding='utf-8'))
inst = {r['ref']: r for r in R['E4a_instances']}
libc = {r['name']: r for r in R['E4b_library_copies']}
E3 = R['E3']
cp = {r['name']: r for r in R.get('E4c_silk_copies', [])}
CASES = [
    ('E1 제외 4건 나열', len(R['exclusions']) == 4 and {x['type'] for x in R['exclusions']} == {'lib_footprint_mismatch', 'clearance'}),
    ('E1 제외 → 참조 매핑(R2·R3·R4)', sorted(r for x in R['exclusions'] if x['type'] == 'lib_footprint_mismatch' for r in x['refs']) == ['R2', 'R3', 'R4']),
    ('E1 ignore 심각도 나열(silk_overlap)', R['ignored_severities'] == {'silk_overlap': 'ignore'}),
    ('E1 DRU severity 규칙 나열(hide_silk)', [x['rule'] for x in R['dru_severity_rules']] == ['hide_silk']),
    ('E2 허용 밖 종류(clearance) 불합격', (not R['verdict']['E2_pass']) and [x['type'] for x in R['E2_disallowed']] == ['clearance']),
    ('E2 O-74 주석 없음 경고 1', R['verdict']['E2_warn_no_comment'] == 1),
    ('E3 불일치 판정', E3['status'] == '불일치'),
    ('E3 문서에 없는 제외 R3', E3['missing_in_doc'] == ['R3']),
    ('E3 제외에 없는 문서 참조(보드에 없는 R9는 따로)', E3['missing_in_exclusions'] == [] and E3['doc_tokens_not_on_board'] == ['R9']),
    ('E3 다른 보드 줄(carrier) 무시', 'R3' not in E3['doc_refs']),
    ('E4a 그대로(R1) 통과', inst.get('R1', {}).get('ok') is True),
    ('E4a 실크만 자름(R2, 90°) 통과', inst.get('R2', {}).get('ok') is True and inst['R2']['silk_equal'] is False),
    ('E4a 패드 바뀜(R3) 불합격', inst.get('R3', {}).get('ok') is False and inst['R3']['pads_equal'] is False),
    ('E4a 뒷면·180°·실크만(R4) 통과', inst.get('R4', {}).get('ok') is True),
    ('E4a Fab 바뀜(R5) 불합격', inst.get('R5', {}).get('ok') is False and inst['R5']['nonsilk_equal'] is False and inst['R5']['pads_equal'] is True),
    ('E4a 구멍 바뀜(J1) 불합격', inst.get('J1', {}).get('ok') is False and inst['J1']['holes_equal'] is False),
    ('E4a THT 그대로(J2, 90°) 통과', inst.get('J2', {}).get('ok') is True),
    ('E4b 실크만 바뀐 사본 통과', libc.get('R_0402_1005Metric', {}).get('ok') is True and libc['R_0402_1005Metric']['silk_equal'] is False),
    ('E4b 패드 옮긴 사본 불합격', libc.get('SOT-23', {}).get('ok') is False and libc['SOT-23']['pads_equal'] is False),
    ('E4b Fab 지운 사본 불합격', libc.get('R_0603_1608Metric', {}).get('ok') is False and libc['R_0603_1608Metric']['pads_equal'] is True),
    ('E4b THT 사본 통과', libc.get('PinHeader_1x02_P2.54mm_Vertical', {}).get('ok') is True),
    ('E2b 제외가 있으면 0 아님 표시', R['verdict']['E2b_exclusions_zero'] is False),
    ('E4c 실크 사본 별칭 2개 인식', R['verdict']['silk_redirects'] == ['Package_TO_SOT_SMD', 'Resistor_SMD']),
    ('E4c R_0402 실크만·sha 맞음 통과', cp.get('R_0402_1005Metric', {}).get('ok') is True and cp['R_0402_1005Metric']['silk_equal'] is False),
    ('E4c R_0603 기록 sha 틀림 불합격', cp.get('R_0603_1608Metric', {}).get('ok') is False and cp['R_0603_1608Metric'].get('sha_ok') is False and cp['R_0603_1608Metric'].get('pads_equal') is True),
    ('E4c R_0805 SOURCES 행 없음 불합격', cp.get('R_0805_2012Metric', {}).get('ok') is False and 'SOURCES' in cp['R_0805_2012Metric'].get('error', '')),
    ('E4c R_1206 사본 파일 없음 불합격', cp.get('R_1206_3216Metric', {}).get('ok') is False),
    ('E4c SOT-23 패드 0.05 이동 불합격(절대 경로 원본)', cp.get('SOT-23', {}).get('ok') is False and cp['SOT-23'].get('pads_equal') is False and cp['SOT-23'].get('sha_ok') is True),
    ('E4c SOT-23-5 Fab 지움 불합격(다른 PC 경로 → 이 PC KiCad)', cp.get('SOT-23-5', {}).get('ok') is False and cp['SOT-23-5'].get('sha_ok') is True and cp['SOT-23-5'].get('nonsilk_equal') is False),
    ('E4c openhw:이름 원본·실크만 통과', cp.get('SOT-23_OH', {}).get('ok') is True),
    ('E4c 프로젝트 라이브러리 별칭:이름 원본(hardware/pcb/lib) 통과', cp.get('SOT-23_PM', {}).get('ok') is True),
    ('E4c 기록 sha 가 CRLF 형태 — 줄바꿈만 다름 통과', cp.get('SOT-23_OH2', {}).get('ok') is True and cp['SOT-23_OH2'].get('sha_form') == 'crlf'),
    ('E4c 기록 sha 0 은 여전히 불합격(줄바꿈 허용이 틀린 sha 를 통과시키지 않음)', cp.get('R_0603_1608Metric', {}).get('sha_ok') is False),
    ('E4c 불합격 목록 5', len(R['verdict']['E4c_fail']) == 5),
    ('E4c 이름이 앞부분만 같은 다른 라이브러리(Resistor_SMDX)의 행은 이 라이브러리 것으로 치지 않음(음성)', not any(r.get('name') == 'R_ZZZ' for r in R.get('E4c_silk_copies', []))),
]
fail = 0
for name, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', name))
    fail += 0 if ok else 1
if fail:
    print('--- 진단', json.dumps(dict(v=R['verdict'], cp=cp, E3=E3, inst=inst, lib=libc), ensure_ascii=False)[:5000])
print('사례 %d · 실패 %d · 폴더 %s' % (len(CASES), fail, WORK))
sys.exit(1 if fail else 0)
