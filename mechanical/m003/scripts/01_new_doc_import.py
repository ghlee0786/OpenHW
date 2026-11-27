"""M-003 01: new local design doc, import reference STEPs (pcb aebd293 boards + M-002b stack reference).
Coordinates: origin O = core board centre at its bottom face, +Z = optical axis (same as M-001).
KiCad STEPs: XY already in O, Z = each board's bottom = 0 -> carrier moved to z = -(btb_h+core_t)... see params."""
import adsk.core, adsk.fusion
LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
BOARDS = MAIN + r"\validation\runtime\vd001\boards"   # kicad-cli 보드 STEP (mechanical/m007/run_all.py)

def run(_c):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    design.attributes.add('openhw', 'doc', 'M003_enclosure')   # 02~06 이 확인
    root = design.rootComponent
    im = app.importManager
    out = {}
    for name, path in (("REF_STACK_M002b", LANE + r"\mechanical\step\stack-reference.step"), ("REF_CARRIER", BOARDS + r"\carrier.step"), ("REF_FRONT", BOARDS + r"\front.step")):
        n0 = root.occurrences.count
        opt = im.createSTEPImportOptions(path)
        im.importToTarget(opt, root)
        occ = root.occurrences.item(root.occurrences.count - 1)
        occ.component.name = name
        out[name] = (root.occurrences.count - n0)
    print("doc", doc.name, "imported", out)
