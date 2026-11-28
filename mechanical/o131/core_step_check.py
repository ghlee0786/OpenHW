"""O-131: 시안 A 조립(M007_assembly, case A — 02_assembly.py --set CASE=A 로 만든 문서)에 코어 자리 표시(덩어리) 대신
Seeed 코어 STEP 실형상을 넣어 간섭·최소 거리만 다시 잰다. 케이스 파일은 바꾸지 않는다(문서에 가져와 재기만, 저장 안 함).
  python -I -B mechanical/fusion_run.py mechanical/o131/core_step_check.py
- 코어 STEP: MAIN/validation/runtime/vd001/third_party/Recamera Core 2002.step (저장소에 넣지 않음, CC BY-SA 4.0 — 읽기·측정만)
- 위치: M-001 원점 O — STEP 좌표에서 PCB 외형 중심 (60, -65) -> (0, 0), PCB 아랫면 z 0 그대로
  (stack-reference.md §2: J1 (0,+12) 윗면 · J2 (+11.8,0) 아랫면 — 결과의 J1/J2 중심으로 확인)
- 무선 부품 제외(숨김): DZcc-U4(AP6212 — 12x12, 보드 위 1.5, stack-reference §2.2 의 1.58 과 높이로 맞춤) · U.FL-R-SMT-1 · ANT-SPRING
- 자리 표시 제외: CORE_ENVELOPE_30x30 · CORE_BOT_KEEPIN · CORE_TOP_KEEPIN · J1/J2_MATED_ENVELOPE (실형상과 겹치는 덩어리)
결과: MAIN/validation/runtime/vd001/o131/core_step_check.json"""
import adsk.core, adsk.fusion, os, json, hashlib, re

LANE = None
MAIN = None
OUT = MAIN + r"\validation\runtime\vd001"
CORE_STEP = OUT + r"\third_party\Recamera Core 2002.step"
SHIFT = (-60.0, 65.0, 0.0)   # mm, STEP -> O
WIRELESS = ('DZcc-U4', 'U.FL-R-SMT-1', 'ANT-SPRING')
PLACEHOLDERS = ('CORE_ENVELOPE_30x30', 'CORE_BOT_KEEPIN', 'CORE_TOP_KEEPIN', 'J1_MATED_ENVELOPE', 'J2_MATED_ENVELOPE')


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    ca = design.attributes.itemByName('openhw', 'case')
    assert ca and ca.value == 'A', 'case A 조립이 아님'
    root = design.rootComponent
    assert not any(o.component.name == 'CORE_STEP_2002' for o in root.occurrences), '이미 코어를 넣은 문서 — 02_assembly 로 새로 만들 것'
    res = {'core_step': os.path.basename(CORE_STEP), 'core_sha256': hashlib.sha256(open(CORE_STEP, 'rb').read()).hexdigest(),
           'shift_mm': SHIFT, 'wireless_hidden': WIRELESS, 'placeholders_excluded': PLACEHOLDERS}

    # 1) 코어 STEP 가져오기 · O 로 옮기기
    im = app.importManager
    im.importToTarget(im.createSTEPImportOptions(CORE_STEP), root)
    core = root.occurrences.item(root.occurrences.count - 1); core.component.name = 'CORE_STEP_2002'
    m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(*[v / 10 for v in SHIFT]); core.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
    hidden = 0
    for o in root.allOccurrences:   # 코어 부품은 중첩 occurrence
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        if top == core and o.component.name in WIRELESS:
            o.isLightBulbOn = False; hidden += 1
    res['wireless_occ_hidden'] = hidden

    def mmbox(b):
        bb = b.boundingBox
        return [v * 10 for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)]

    def solid(b):
        if not b.isSolid or not b.isLightBulbOn:
            return False
        try:
            return b.volume > 1e-9
        except RuntimeError:
            return False

    # 2) 바디 목록 (03_judge 와 같은 보임·이름 규칙)
    cores, others = [], []
    for o in root.allOccurrences:
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        tn = top.component.name
        if not o.isLightBulbOn or (top != o and not top.isLightBulbOn):
            continue
        for b in o.bRepBodies:
            if not solid(b):
                continue
            if tn == 'CORE_STEP_2002':
                cores.append((b, 'CORE:' + o.component.name))
                continue
            if tn in ('REF_CARRIER', 'REF_FRONT'):
                nm = 'BOARD_PART:' + re.sub(r' \(\d+\)$', '', o.component.name)
            else:
                nm = o.component.name if tn == 'REF_STACK' else (b.name if tn in ('ENC_BLOCKS', 'HARNESS_GH6P', 'CASE_A') else tn)
            if nm in PLACEHOLDERS:
                continue
            others.append((b, nm, tn))

    def centre_xy(bx):
        return [round((bx[0] + bx[1]) / 2, 2), round((bx[2] + bx[3]) / 2, 2)]
    byname = {n: mmbox(b) for b, n in cores}
    res['core_pcb_bbox_mm'] = [round(v, 3) for v in byname['CORE:Recamera Core w WiFi 8GB v1.2_PCB']]
    res['J1_plug_centre_xy'] = centre_xy(byname['CORE:SHANGQI_0_5BTB_60P_4_0H_PLUG'])
    res['J2_socket_centre_xy'] = centre_xy(byname['CORE:SHANGQI_0_5BTB_60P_4_0H_SOCKET'])
    boxes = [mmbox(b) for b, _ in cores]
    cb = [min(x[i] for x in boxes) if i % 2 == 0 else max(x[i] for x in boxes) for i in range(6)]
    res['core_bbox_mm'] = [round(v, 3) for v in cb]
    res['core_bodies'] = len(cores)

    def gap(a, b):   # 상자 사이 거리 (실제 거리의 하한)
        d2 = 0.0
        for i in range(0, 6, 2):
            g = max(a[i] - b[i + 1], b[i] - a[i + 1], 0.0); d2 += g * g
        return d2 ** 0.5

    near = [(b, n, tn) for b, n, tn in others if gap(cb, mmbox(b)) < 0.5]
    res['candidate_bodies'] = len(near)

    # 3) 간섭 (맞닿는 면 제외)
    coll = adsk.core.ObjectCollection.create()
    for b, _ in cores:
        coll.add(b)
    for b, _, _ in near:
        coll.add(b)
    inp = design.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
    r = design.analyzeInterference(inp)

    # 간섭 결과의 바디는 프록시가 아닐 수 있다(03_judge 와 같은 문제) → 같은 부피 + 겹친 곳 가운데를 품는 바디로 이름을 찾는다
    def vkey(b):
        try:
            return round(b.volume, 6)
        except RuntimeError:
            return None
    pool = {}
    for b, n in cores:
        pool.setdefault(vkey(b), []).append((b.boundingBox, n, True))
    for b, n, _ in near:
        pool.setdefault(vkey(b), []).append((b.boundingBox, n, False))

    def who(e, ic):
        for bb_, n, isc in pool.get(vkey(e), []):
            if bb_.contains(ic):
                return n, isc
        return '?', None
    inter, unknown = [], 0
    for i in range(0 if r is None else r.count):
        it = r.item(i)
        ib = it.interferenceBody
        bb = ib.boundingBox
        ic = adsk.core.Point3D.create((bb.minPoint.x + bb.maxPoint.x) / 2, (bb.minPoint.y + bb.maxPoint.y) / 2, (bb.minPoint.z + bb.maxPoint.z) / 2)
        (a, ac), (b, bc) = who(it.entityOne, ic), who(it.entityTwo, ic)
        if ac is None or bc is None:
            unknown += 1
        if ac is not None and ac == bc:
            continue   # 코어끼리 또는 코어 밖끼리 — 이번 판정 밖
        if ac is None and bc is None:
            continue
        c, o = (a, b) if ac else (b, a)
        inter.append({'core': c, 'other': o, 'mm3': round(ib.volume * 1000, 4), 'at': [round(v, 2) for v in mmbox(ib)],
                      'btb_mate': 'SHANGQI' in c and o.startswith('BOARD_PART:')})
    res['interference_results'] = 0 if r is None else r.count
    res['interference_unnamed'] = unknown
    res['interference'] = inter
    res['interference_mm3_total'] = round(sum(x['mm3'] for x in inter), 4)
    res['interference_non_mate_mm3'] = round(sum(x['mm3'] for x in inter if not x['btb_mate']), 4)

    # 4) 최소 거리 — 바디마다 상자 거리 순으로 재다가 하한이 현재 최소 이상이면 멈춤
    mm = app.measureManager
    cboxes = [(b, n, mmbox(b)) for b, n in cores]

    def mind(ob):
        obb = mmbox(ob); best = (1e9, None)
        for g, k in sorted((gap(obb, cbx), k) for k, (_, _, cbx) in enumerate(cboxes)):
            if g >= best[0]:
                break
            d = mm.measureMinimumDistance(cboxes[k][0], ob).value * 10
            if d < best[0]:
                best = (d, cboxes[k][1])
        return best
    case_rows = []
    for b, n, tn in others:
        if tn != 'CASE_A':
            continue
        d, cn = mind(b)
        case_rows.append({'case_body': n, 'min_mm': round(d, 3), 'core_body': cn})
    case_rows.sort(key=lambda x: x['min_mm'])
    res['case_min_distance'] = case_rows
    hit = {x['other'] for x in inter}
    ref_rows = []
    for b, n, tn in near:   # 케이스 밖 바디(간섭 쌍 제외) 중 가까운 것 — 참고
        if tn == 'CASE_A' or n in hit:
            continue
        d, cn = mind(b)
        ref_rows.append({'body': n, 'min_mm': round(d, 3), 'core_body': cn})
    ref_rows.sort(key=lambda x: x['min_mm'])
    res['other_min_distance_top10'] = ref_rows[:10]
    os.makedirs(OUT + r"\o131", exist_ok=True)
    json.dump(res, open(OUT + r"\o131\core_step_check.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('RESULT', json.dumps({k: res[k] for k in ('core_bodies', 'candidate_bodies', 'wireless_occ_hidden', 'J1_plug_centre_xy', 'J2_socket_centre_xy',
                                                    'core_bbox_mm', 'interference_results', 'interference_unnamed', 'interference_mm3_total', 'interference_non_mate_mm3')}, ensure_ascii=False))
    for x in inter:
        print('INTER', x)
    for x in case_rows[:8]:
        print('CASE', x)
    for x in ref_rows[:6]:
        print('REF', x)
