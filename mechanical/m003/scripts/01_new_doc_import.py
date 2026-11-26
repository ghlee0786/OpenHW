"""M-003 01: new local design doc, import reference STEPs (pcb aebd293 boards + M-002b stack reference).
Coordinates: origin O = core board centre at its bottom face, +Z = optical axis (same as M-001).
KiCad STEPs: XY already in O, Z = each board's bottom = 0 -> carrier moved to z = -(btb_h+core_t)... see params."""
import adsk.core, adsk.fusion
SCR = r"C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\decb4398-40a5-4677-aeb1-556f1d7e2c56\scratchpad\m003\ref"
LANE = r"C:\workspace_python\OpenHW\.harness-worktrees\t-20261127-013549-8089\mechanical\step\stack-reference.step"

def run(_c):
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.fusionUnitsManager.distanceDisplayUnits = adsk.fusion.DistanceUnits.MillimeterDistanceUnits
    root = design.rootComponent
    im = app.importManager
    out = {}
    for name, path in (("REF_STACK_M002b", LANE), ("REF_CARRIER_aebd293", SCR + r"\carrier.step"), ("REF_FRONT_aebd293", SCR + r"\front.step")):
        n0 = root.occurrences.count
        opt = im.createSTEPImportOptions(path)
        im.importToTarget(opt, root)
        occ = root.occurrences.item(root.occurrences.count - 1)
        occ.component.name = name
        out[name] = (root.occurrences.count - n0)
    print("doc", doc.name, "imported", out)
