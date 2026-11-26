"""M-003 02: params.py + geom.py 로 외함 부품을 (다시) 만든다. 앞서 만든 같은 이름 부품은 지우고 새로 만든다.
실행: python ~/.claude/skills/fusion360/scripts/fusion_cli.py run mechanical/m003/scripts/02_build.py
활성 문서에 openhw/doc = M003_enclosure 속성이 있어야 한다 (01_new_doc_import.py 가 만든 문서)."""
import adsk.core, adsk.fusion, math

BASE = r"C:\workspace_python\OpenHW\.harness-worktrees\t-20261127-013549-8089\mechanical\m003"
COLORS = {  # 부품 → (R,G,B,불투명도)
    'HOUSING': (30, 30, 30, 255), 'FRONT_COVER': (45, 45, 45, 255), 'AL_HEATSINK_PX': (40, 40, 45, 255),
    'LENS_WIN_PMMA': (200, 230, 255, 90), 'WIN_A_PMMA': (200, 230, 255, 90), 'WIN_B_PMMA': (200, 230, 255, 90),
    'ALS_WIN_PMMA': (200, 230, 255, 90), 'FOAM_LENS_RING': (10, 10, 10, 255), 'FOAM_ALS_GASKET': (10, 10, 10, 255),
    'SPREADER_M003': (170, 175, 180, 255), 'INS_PADS_P340': (150, 60, 160, 255), 'GAP_PAD_PX': (150, 60, 160, 255),
    'HW_STANDOFFS': (200, 170, 60, 255), 'HW_SCREW_HEADS': (120, 120, 120, 255),
}


def run(_c):
    g = {}
    exec(open(BASE + r"\params.py", encoding="utf-8").read(), g)
    exec(open(BASE + r"\geom.py", encoding="utf-8").read(), g)
    d = g['derive'](g['P'])
    parts, blocks = g['parts'](d)

    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M003_enclosure', 'wrong document'
    root = design.rootComponent
    tb = adsk.fusion.TemporaryBRepManager.get()
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    U = 0.1  # mm -> cm

    def ev(n):
        k = n[0]
        if k == 'box':
            x0, x1, y0, y1, z0, z1 = [v * U for v in n[1:]]
            ob = adsk.core.OrientedBoundingBox3D.create(P3((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), V3(1, 0, 0), V3(0, 1, 0),
                                                       x1 - x0, y1 - y0, z1 - z0)
            return tb.createBox(ob)
        if k == 'cyl':
            a, b, r0, r1 = n[1], n[2], n[3], n[4]
            return tb.createCylinderOrCone(P3(*[v * U for v in a]), r0 * U, P3(*[v * U for v in b]), r1 * U)
        if k == 'hs45':
            ya, za = n[1] * U, n[2] * U
            H = 40.0
            s = 1 / math.sqrt(2)
            c = P3(0, ya + s * H / 2, za - s * H / 2)
            ob = adsk.core.OrientedBoundingBox3D.create(c, V3(1, 0, 0), V3(0, s, s), H, H, H)
            return tb.createBox(ob)
        op = {'u': adsk.fusion.BooleanTypes.UnionBooleanType, 'd': adsk.fusion.BooleanTypes.DifferenceBooleanType,
              'i': adsk.fusion.BooleanTypes.IntersectionBooleanType}[k]
        acc = ev(n[1])
        for sub in n[2:]:
            assert tb.booleanOperation(acc, ev(sub), op), 'boolean failed'
        return acc

    # 기준 보드 위치 (KiCad STEP: 판 아랫면 z=0)
    for o in root.occurrences:
        nm = o.component.name
        if nm.startswith('REF_CARRIER') or nm.startswith('REF_FRONT'):
            m = adsk.core.Matrix3D.create()
            m.translation = V3(0, 0, (d['z_car_bot'] if nm.startswith('REF_CARRIER') else d['z_fr_bot']) * U)
            o.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()

    # 이전 생성물 지우기
    names = set(parts) | set(blocks) | {'ENC_BLOCKS', 'SPREADER_FLANGE_PX', 'AL_SIDE_PLATE'}
    for o in [o for o in root.occurrences if o.component.name in names]:
        o.deleteMe()

    lib = None

    def color(body, rgba):
        a = design.appearances.itemByName('m003_%d_%d_%d_%d' % rgba)
        if a is None:
            base = app.materialLibraries.itemById('BA5EE55E-9982-449B-9D66-9F036540E140').appearances.itemById('Prism-093')  # 단색 플라스틱 계열
            if base is None:
                return
            a = design.appearances.addByCopy(base, 'm003_%d_%d_%d_%d' % rgba)
            for i in range(a.appearanceProperties.count):
                pr = a.appearanceProperties.item(i)
                if isinstance(pr, adsk.core.ColorProperty) and pr.value is not None:
                    pr.value = adsk.core.Color.create(*rgba)
                    break
        body.appearance = a

    def add_part(comp, name, node):
        body = ev(node)
        bf = comp.features.baseFeatures.add()
        bf.startEdit()
        b = comp.bRepBodies.add(body, bf)
        bf.finishEdit()
        b = comp.bRepBodies.item(comp.bRepBodies.count - 1)
        b.name = name
        return b

    out = []
    for name, node in parts.items():
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = name
        b = add_part(occ.component, name, node)
        if name in COLORS:
            color(b, COLORS[name])
        out.append((name, round(b.volume * 1000, 1)))
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = 'ENC_BLOCKS'
    for name, node in blocks.items():
        add_part(occ.component, name, node).opacity = 0.5
    print('BUILT', out, 'blocks', len(blocks))
    print('DERIVED', {k: round(v, 3) for k, v in d.items() if isinstance(v, float) and k.startswith(('z_', 'x_', 'y_'))})
