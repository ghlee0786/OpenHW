# -*- coding: utf-8 -*-
"""v005_excl.py 고장 주입 시험 (KiCad 10 pcbnew). O-74 판정 E1~E4.

사용: <KiCad>/bin/python.exe -I test_v005_excl.py [작업 폴더]
합성 프로젝트(보드 · .kicad_pro 제외 목록 · .kicad_dru · fp-lib-table · openhw.pretty 사본 · pcb 문서)를 만들고
v005_excl.py 를 하위 프로세스로 돌려 위반은 잡히고 정상은 통과하는지 본다. 종료 0 = 전부 통과, 1 = 실패.
"""
import sys, os, json, shutil, subprocess, tempfile
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
open(os.path.join(WORK, 'fp-lib-table'), 'w', encoding='utf-8').write(
    '(fp_lib_table\n  (version 7)\n  (lib (name "openhw")(type "KiCad")(uri "${KIPRJMOD}/openhw.pretty")(options "")(descr ""))\n)\n')

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
rc = subprocess.run([sys.executable, '-I', os.path.join(HERE, 'v005_excl.py'), pcb, out, '--doc', doc, '--board-name', 'front'],
                    capture_output=True, text=True, encoding='utf-8')
if rc.returncode != 0:
    print('v005_excl.py 실패', rc.returncode, rc.stderr[-2000:]); sys.exit(1)
R = json.load(open(out, encoding='utf-8'))
inst = {r['ref']: r for r in R['E4a_instances']}
libc = {r['name']: r for r in R['E4b_library_copies']}
E3 = R['E3']
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
]
fail = 0
for name, ok in CASES:
    print('%s  %s' % ('통과' if ok else '실패', name))
    fail += 0 if ok else 1
if fail:
    print('--- 진단', json.dumps(dict(E3=E3, inst=inst, lib=libc, v=R['verdict']), ensure_ascii=False)[:4000])
print('사례 %d · 실패 %d · 폴더 %s' % (len(CASES), fail, WORK))
sys.exit(1 if fail else 0)
