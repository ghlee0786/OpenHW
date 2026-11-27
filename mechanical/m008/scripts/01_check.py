"""M-008 01 (Fusion, M007_assembly 문서): CLA216 새 방향·스페이서·리드·ICR 패드·DF30 (0,−11.55)·FPC 를 넣고
옛 자리 표시(CLA216_ICR, HOLDER_SPACER_FRAME, ICR_LEAD_PATH, DF30_SITE, FPC_3mm)를 숨긴 뒤, 새 바디마다
전면 보드 부품(참조 번호별)·LED·센서 블록·덮개·폼과 간섭·최소 틈을 잰다 → validation/runtime/vd001/m008_check.json"""
import adsk.core, adsk.fusion, json, math

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
OUT = MAIN + r"\validation\runtime\vd001"
OLD = ('CLA216_ICR', 'HOLDER_SPACER_FRAME', 'ICR_LEAD_PATH', 'DF30_SITE', 'FPC_3mm')


def run(_c):
    s = {}
    exec(open(LANE + r"\mechanical\m008\cla216_spec.py", encoding="utf-8").read(), s)
    fps = json.load(open(OUT + r"\m008_front_fp.json", encoding='utf-8'))
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
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
        op = {'u': adsk.fusion.BooleanTypes.UnionBooleanType, 'd': adsk.fusion.BooleanTypes.DifferenceBooleanType}[k]
        acc = ev(n[1])
        for sub in n[2:]:
            assert tb.booleanOperation(acc, ev(sub), op), 'boolean failed'
        return acc
    for o in [o for o in root.occurrences if o.component.name.endswith('_M008')]:
        o.deleteMe()
    new = {}
    for name, node in s['parts']().items():
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); occ.component.name = name
        bf = occ.component.features.baseFeatures.add(); bf.startEdit(); occ.component.bRepBodies.add(ev(node), bf); bf.finishEdit()
        b = occ.component.bRepBodies.item(0); b.name = name
        new[name] = occ.bRepBodies.item(0)
    for o in root.allOccurrences:
        if o.component.name in OLD:
            o.isLightBulbOn = False
    # 상대 바디: 기준 적층(보이는 것)·외함 생성물·전면 보드 부품 (참조 번호 = 코트야드 안에 바디 중심)
    others = []
    front_occ = [o for o in root.occurrences if o.component.name == 'REF_FRONT'][0]
    for o in root.allOccurrences:
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        if not o.isLightBulbOn or o.component.name.endswith('_M008') or top.component.name in ('REF_CARRIER',):
            continue
        for b in o.bRepBodies:
            if not b.isSolid or not b.isLightBulbOn:
                continue
            bb = b.boundingBox
            cx, cy, cz = (bb.minPoint.x + bb.maxPoint.x) * 5, (bb.minPoint.y + bb.maxPoint.y) * 5, (bb.minPoint.z + bb.maxPoint.z) * 5
            if top == front_occ:
                ref = None
                for r, crt, lay in fps:
                    if lay == 'F.Cu' and crt and crt[0] <= cx <= crt[1] and crt[2] <= cy <= crt[3] and cz > 11.15:
                        ref = r; break
                if ref is None:
                    if cz <= 11.15:
                        continue         # 보드 본체·뒷면 부품
                    ref = 'FRONT_TOP_PART@(%.1f,%.1f)' % (cx, cy)
                others.append((b, 'FRONT/' + ref))
            else:
                nm = o.component.name if top.component.name == 'REF_STACK' else top.component.name
                others.append((b, nm))
    mm = app.measureManager
    rows = []
    for nname, nb in new.items():
        for b, oname in others:
            dmin = mm.measureMinimumDistance(nb, b).value * 10
            if dmin < 3.0:
                rows.append({'new': nname, 'other': oname, 'min_mm': round(dmin, 3)})
    # 간섭 (부피)
    coll = adsk.core.ObjectCollection.create()
    for b in list(new.values()) + [b for b, _ in others]:
        coll.add(b)
    inp = design.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
    r = design.analyzeInterference(inp)
    hits = []
    for i in range(0 if r is None else r.count):
        ib = r.item(i).interferenceBody.boundingBox
        hits.append({'mm3': round(r.item(i).interferenceBody.volume * 1000, 3),
                     'at': [round(v * 10, 2) for v in (ib.minPoint.x, ib.maxPoint.x, ib.minPoint.y, ib.maxPoint.y, ib.minPoint.z, ib.maxPoint.z)]})
    json.dump({'near': sorted(rows, key=lambda x: x['min_mm']), 'hits_all': hits}, open(OUT + r"\m008_check.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('M008 near', len(rows), 'hits', len(hits))
