"""M-007 01: 대체 3D 모델 만들기 (Fusion) — models_spec.py 를 읽어 새 로컬 문서에 부품마다 몸체·리드 상자를 만들고 mechanical/models/*.step 으로 내보낸다."""
import adsk.core, adsk.fusion, re, math, os

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
BASE = LANE + r"\mechanical"


def fab_and_pads(path):
    t = open(path, encoding='utf-8').read()
    xs, ys = [], []
    for m in re.finditer(r'\n\t\((fp_line|fp_rect|fp_poly)(.*?)\n\t\)', t, re.S):   # 항목 하나씩 (KiCad 들여쓰기 기준)
        body = m.group(2)
        if '(layer "F.Fab")' not in body:
            continue
        for x, y in re.findall(r'\((?:start|end|xy) ([-\d.]+) ([-\d.]+)\)', body):
            xs.append(float(x)); ys.append(float(y))
    px, py = [], []
    for p in re.finditer(r'\(pad "[^"]*" smd \w+\s*\(at ([-\d.]+) ([-\d.]+)(?: ([-\d.]+))?\)\s*\(size ([-\d.]+) ([-\d.]+)\)', t):
        x, y, a, w, h = float(p.group(1)), float(p.group(2)), float(p.group(3) or 0), float(p.group(4)), float(p.group(5))
        if abs(a) % 180 == 90:
            w, h = h, w
        px += [x - w / 2, x + w / 2]; py += [y - h / 2, y + h / 2]
    return (min(xs), max(xs), min(ys), max(ys)), ((min(px), max(px), min(py), max(py)) if px else None)


def run(_c):
    g = {}
    exec(open(BASE + r"\m007\models_spec.py", encoding='utf-8').read(), g)
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    d = adsk.fusion.Design.cast(app.activeProduct)
    d.designType = adsk.fusion.DesignTypes.ParametricDesignType
    d.attributes.add('openhw', 'doc', 'M007_models')
    root = d.rootComponent
    tb = adsk.fusion.TemporaryBRepManager.get()
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    em = d.exportManager
    os.makedirs(BASE + r"\models", exist_ok=True)
    for name, fp, H, src, use in g['MODELS']:
        fab, pads = fab_and_pads(os.path.join(g['KICAD_FP'], fp + '.kicad_mod'))
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); c = occ.component; c.name = name
        bf = c.features.baseFeatures.add(); bf.startEdit()
        # KiCad 풋프린트 y 는 아래로 → 모델 y = −y
        def box(x0, x1, y0, y1, z0, z1):
            ob = adsk.core.OrientedBoundingBox3D.create(P3((x0 + x1) / 20, -(y0 + y1) / 20, (z0 + z1) / 20), V3(1, 0, 0), V3(0, 1, 0),
                                                       (x1 - x0) / 10, (y1 - y0) / 10, (z1 - z0) / 10)
            return tb.createBox(ob)
        c.bRepBodies.add(box(fab[0], fab[1], fab[2], fab[3], 0.0, H), bf)
        if pads:
            c.bRepBodies.add(box(pads[0], pads[1], pads[2], pads[3], 0.0, 0.15), bf)
        bf.finishEdit()
        c.bRepBodies.item(0).name = name + '_BODY'
        ok = em.execute(em.createSTEPExportOptions(BASE + r"\models\%s.step" % name, c))
        print('MODEL', name, 'fab', [round(v, 3) for v in fab], 'pads', [round(v, 3) for v in pads] if pads else None, 'H', H, 'export', ok)
