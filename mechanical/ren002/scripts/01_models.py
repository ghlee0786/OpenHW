"""REN-002 01 (Fusion): openhw 풋프린트 대체 3D 모델 7종 → mechanical/models/*.step
몸체 = 풋프린트 F.Fab 외곽 × 높이(models_spec.NEW), 리드 = 패드 범위 두께 0.15. CLA216 홀더는 M-008 형상(스페이서·홀더·리드)을 보드 윗면 z 0 기준으로 옮김.
입력 풋프린트: validation/runtime/vd001/ren002/pcbsrc/hardware/libraries/openhw.pretty (audit_models.py 가 pcb 커밋에서 꺼냄)."""
import adsk.core, adsk.fusion, re, os

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
SRC = MAIN + r"\validation\runtime\vd001\ren002\pcbsrc"


def fab_and_pads(path):
    t = open(path, encoding='utf-8').read()
    xs, ys = [], []
    for m in re.finditer(r'\n\t\((fp_line|fp_rect|fp_poly)(.*?)\n\t\)', t, re.S):
        if '(layer "F.Fab")' not in m.group(2):
            continue
        for x, y in re.findall(r'\((?:start|end|xy) ([-\d.]+) ([-\d.]+)\)', m.group(2)):
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
    exec(open(LANE + r"\mechanical\ren002\models_spec.py", encoding='utf-8').read(), g)
    m8 = {}
    exec(open(LANE + r"\mechanical\m008\cla216_spec.py", encoding='utf-8').read(), m8)
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    d = adsk.fusion.Design.cast(app.activeProduct)
    d.designType = adsk.fusion.DesignTypes.ParametricDesignType
    d.attributes.add('openhw', 'doc', 'REN002_models')
    root = d.rootComponent
    tb = adsk.fusion.TemporaryBRepManager.get()
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    em = d.exportManager
    U = 0.1

    def ev(n, dz=0.0):
        k = n[0]
        if k == 'box':
            x0, x1, y0, y1, z0, z1 = n[1:]
            z0 += dz; z1 += dz
            return tb.createBox(adsk.core.OrientedBoundingBox3D.create(P3((x0 + x1) / 2 * U, (y0 + y1) / 2 * U, (z0 + z1) / 2 * U), V3(1, 0, 0), V3(0, 1, 0),
                                                                       (x1 - x0) * U, (y1 - y0) * U, (z1 - z0) * U))
        if k == 'cyl':
            a, b = n[1], n[2]
            return tb.createCylinderOrCone(P3(a[0] * U, a[1] * U, (a[2] + dz) * U), n[3] * U, P3(b[0] * U, b[1] * U, (b[2] + dz) * U), n[4] * U)
        op = {'u': adsk.fusion.BooleanTypes.UnionBooleanType, 'd': adsk.fusion.BooleanTypes.DifferenceBooleanType,
              'i': adsk.fusion.BooleanTypes.IntersectionBooleanType}[k]
        acc = ev(n[1], dz)
        for sub in n[2:]:
            assert tb.booleanOperation(acc, ev(sub, dz), op), 'boolean failed'
        return acc

    for name, fp, H, src, use in g['NEW']:
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); c = occ.component; c.name = name
        bf = c.features.baseFeatures.add(); bf.startEdit()
        if H is None:      # CLA216: 스페이서 + 홀더 + 리드 (기구 좌표, 앞 보드 윗면 11.2 → 0)
            P = m8['parts']()
            for part in ('SPACER_M008', 'CLA216_M008', 'ICR_LEAD_M008'):
                c.bRepBodies.add(ev(P[part], -m8['FRONT_TOP']), bf)
            info = 'cla216_spec'
        else:
            fab, pads = fab_and_pads(os.path.join(SRC, g['OPENHW_FP'].replace('/', '\\'), fp + '.kicad_mod'))
            # KiCad 풋프린트 y 는 아래로 → 모델 y = −y
            c.bRepBodies.add(ev(('box', fab[0], fab[1], -fab[3], -fab[2], 0.0, H)), bf)
            if pads:
                c.bRepBodies.add(ev(('box', pads[0], pads[1], -pads[3], -pads[2], 0.0, 0.15)), bf)
            info = 'fab %s pads %s H %s' % ([round(v, 3) for v in fab], [round(v, 3) for v in pads] if pads else None, H)
        bf.finishEdit()
        ok = em.execute(em.createSTEPExportOptions(LANE + r"\mechanical\models\%s.step" % name, c))
        print('MODEL', name, info, 'export', ok)
