"""M-006 01: G1 STEP 결합 — 새 로컬 문서에 Seeed 코어 STEP(읽기·측정만, CC BY-SA 4.0 — 저장소에 넣지 않음)과
우리 보드 STEP(pcb 69ed962 kicad-cli)을 적층 높이에 놓는다. 좌표: M-001 원점 O (코어 중심·아랫면, +Z 광축)."""
import adsk.core, adsk.fusion
SCR = r"C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\decb4398-40a5-4677-aeb1-556f1d7e2c56\scratchpad"
BTB_H = 8.0

def run(_c):
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.attributes.add('openhw', 'doc', 'M006_g1')
    root = design.rootComponent
    im = app.importManager
    V3 = adsk.core.Vector3D.create
    places = [('SEEED_CORE2002', SCR + r"\seeed_step\core2002.step", (-60.0, 65.0, 0.0)),
              ('OURS_CARRIER_69ed962', SCR + r"\m006\step\carrier-69ed962.step", (0, 0, -(BTB_H + 1.6))),
              ('OURS_FRONT_69ed962', SCR + r"\m006\step\front-69ed962.step", (0, 0, 1.6 + BTB_H))]
    for name, path, t in places:
        im.importToTarget(im.createSTEPImportOptions(path), root)
        occ = root.occurrences.item(root.occurrences.count - 1)
        occ.component.name = name
        m = adsk.core.Matrix3D.create(); m.translation = V3(*[v / 10 for v in t]); occ.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
    for o in root.occurrences:
        bb = o.boundingBox
        print('OCC', o.component.name, [round(v * 10, 2) for v in (bb.minPoint.x, bb.maxPoint.x, bb.minPoint.y, bb.maxPoint.y, bb.minPoint.z, bb.maxPoint.z)])
