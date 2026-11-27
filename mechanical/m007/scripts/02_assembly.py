"""M-007 02: 전체 조립 틀 (Fusion) — 새 로컬 문서 M007_assembly 에
  · 기준 적층 STEP (mechanical/step/stack-reference.step: 코어 외형·센서 블록·CLA216·렌즈·LED·GH 커넥터·하니스 통로) — 대체된 바디는 숨김
  · 보드 STEP 2장 (validation/runtime/vd001/boards/{carrier,front}.step — run_all.py 가 pcb 커밋에서 kicad-cli 로 만듦)
  · 외함·방열판·창·폼·패드·대체 블록 (mechanical/m003/params.py + geom.py)
  · microSD 카드 삽입 블록, GH 6P 하니스 26AWG 35 mm 6가닥 (mechanical/m007/asm_spec.py)
을 놓고 조립 STEP 을 validation/runtime/vd001/m007_assembly.step 으로 내보낸다. Seeed 형상은 넣지 않는다(코어는 우리 외형 덩어리)."""
import adsk.core, adsk.fusion, math, os, hashlib

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
OUT = MAIN + r"\validation\runtime\vd001"


def run(_c):
    g = {}
    exec(open(LANE + r"\mechanical\m003\params.py", encoding="utf-8").read(), g)
    exec(open(LANE + r"\mechanical\m003\geom.py", encoding="utf-8").read(), g)
    s = {}
    exec(open(LANE + r"\mechanical\m007\asm_spec.py", encoding="utf-8").read(), s)
    import json
    conn = json.load(open(OUT + r"\boards\connectors.json", encoding='utf-8'))   # run_all.py 가 pcb 커밋에서 읽은 커넥터 fab 외곽
    for k, v in conn.items():
        g['P'][k] = tuple(v)
    d = g['derive'](g['P'])
    parts, blocks = g['parts'](d)
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.attributes.add('openhw', 'doc', 'M007_assembly')
    root = design.rootComponent
    im = app.importManager
    tb = adsk.fusion.TemporaryBRepManager.get()
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    U = 0.1

    def ev(n):
        k = n[0]
        if k == 'box':
            x0, x1, y0, y1, z0, z1 = [v * U for v in n[1:]]
            return tb.createBox(adsk.core.OrientedBoundingBox3D.create(P3((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), V3(1, 0, 0), V3(0, 1, 0), x1 - x0, y1 - y0, z1 - z0))
        if k == 'cyl':
            return tb.createCylinderOrCone(P3(*[v * U for v in n[1]]), n[3] * U, P3(*[v * U for v in n[2]]), n[4] * U)
        if k == 'hs45':
            ya, za = n[1] * U, n[2] * U; H = 40.0; q = 1 / math.sqrt(2)
            return tb.createBox(adsk.core.OrientedBoundingBox3D.create(P3(0, ya + q * H / 2, za - q * H / 2), V3(1, 0, 0), V3(0, q, q), H, H, H))
        op = {'u': adsk.fusion.BooleanTypes.UnionBooleanType, 'd': adsk.fusion.BooleanTypes.DifferenceBooleanType,
              'i': adsk.fusion.BooleanTypes.IntersectionBooleanType}[k]
        acc = ev(n[1])
        for sub in n[2:]:
            assert tb.booleanOperation(acc, ev(sub), op), 'boolean failed'
        return acc

    def add_comp(name, bodies):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); occ.component.name = name
        bf = occ.component.features.baseFeatures.add(); bf.startEdit()
        for bname, body in bodies:
            occ.component.bRepBodies.add(body, bf)
        bf.finishEdit()
        for i, (bname, _) in enumerate(bodies):
            occ.component.bRepBodies.item(i).name = bname
        return occ

    # 1) 기준 STEP
    refs = [('REF_STACK', LANE + r"\mechanical\step\stack-reference.step", 0.0),
            ('REF_CARRIER', OUT + r"\boards\carrier.step", d['z_car_bot']),
            ('REF_FRONT', OUT + r"\boards\front.step", d['z_fr_bot'])]
    for name, path, z in refs:
        im.importToTarget(im.createSTEPImportOptions(path), root)
        occ = root.occurrences.item(root.occurrences.count - 1); occ.component.name = name
        if z:
            m = adsk.core.Matrix3D.create(); m.translation = V3(0, 0, z * U); occ.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
    for o in root.allOccurrences:
        if o.component.name in s['SUPERSEDED']:
            o.isLightBulbOn = False
    # 2) 외함·방열판 등 (M-003 형상 정의)
    for name, node in parts.items():
        if name == 'PRINT_COUPON':
            continue
        lst = node if isinstance(node, list) else [(name, node)]
        add_comp(name, [(bn, ev(bnode)) for bn, bnode in lst if not bn.startswith('PRINT_TAB')])
    add_comp('ENC_BLOCKS', [(bn, ev(bnode)) for bn, bnode in blocks.items()])
    # 2b) M-008 CLA216 방향·스페이서·리드·ICR 패드·DF30·FPC (mechanical/m008/cla216_spec.py)
    m8 = {}
    exec(open(LANE + r"\mechanical\m008\cla216_spec.py", encoding="utf-8").read(), m8)
    for name, node in m8['parts']().items():
        add_comp(name, [(name, ev(node))])
    # 3) microSD 카드 삽입 경로 블록 (카드 11 × 1, 소켓 앞면부터 바깥 +20 까지 — 소켓 안은 소켓 모델 몫)
    cw, cl, ct = s['SD_CARD']
    sx = sum(d['sd_x']) / 2
    zc = d['z_car_bot'] - 0.95
    add_comp('BLK_J4_CARD', [('BLK_J4_CARD', ev(('box', sx - cw / 2, sx + cw / 2, conn.get('sd_front', [d['sd_y'][1]])[0], d['y_out_lo'] + 20.0, zc - ct / 2, zc + ct / 2)))])
    # 4) 하니스 6가닥
    L, slack, paths = s['harness_paths']()
    r = s['HAR']['od'] / 2
    wires = []
    for k, pth in enumerate(paths):
        acc = None
        for a, b in zip(pth, pth[1:]):
            if math.dist(a, b) < 1e-4:
                continue
            seg = tb.createCylinderOrCone(P3(*[v * U for v in a]), r * U, P3(*[v * U for v in b]), r * U)
            if acc is None:
                acc = seg
            else:
                tb.booleanOperation(acc, seg, adsk.fusion.BooleanTypes.UnionBooleanType)
        wires.append(('HARNESS_GH6P_W%d' % (k + 1), acc))
    add_comp('HARNESS_GH6P', wires)
    # 5) 조립 STEP
    os.makedirs(OUT, exist_ok=True)
    em = design.exportManager
    ok = em.execute(em.createSTEPExportOptions(OUT + r"\m007_assembly.step", root))
    h = hashlib.sha256(open(OUT + r"\m007_assembly.step", 'rb').read()).hexdigest()
    print('ASSEMBLY', ok, h, 'harness path %.2f slack %.2f' % (L, slack))
    print('BOARDS', {n: hashlib.sha256(open(OUT + r"\boards\%s.step" % n, 'rb').read()).hexdigest() for n in ('carrier', 'front')})
