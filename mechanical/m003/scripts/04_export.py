"""M-003 04: 내보내기 — 전체 F3D·STEP, 부품별 STL(출력 부품)·STEP(가공 부품). 출력 폴더 mechanical/m003/out."""
import adsk.core, adsk.fusion, os

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
OUT = LANE + r"\mechanical\m003\out"   # M-010 run_case.py 는 --set OUT=<main>\validation\runtime\vd001\case
STL = ['HOUSING', 'FRONT_COVER', 'PRINT_COUPON']                                     # FDM 출력
STEP = ['HOUSING', 'FRONT_COVER', 'HS_EXTRUSION', 'HS_PEDESTAL', 'SPREADER_M003', 'LENS_WIN_PMMA', 'WIN_A_PMMA', 'WIN_B_PMMA',
        'ALS_WIN_PMMA', 'FOAM_LENS_RING', 'FOAM_ALS_GASKET', 'INS_PADS_P340', 'GAP_PAD_PX']


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M003_enclosure', 'wrong document'
    root = design.rootComponent
    em = design.exportManager
    os.makedirs(OUT + r"\stl", exist_ok=True)
    os.makedirs(OUT + r"\step", exist_ok=True)
    res = []
    res.append(em.execute(em.createFusionArchiveExportOptions(OUT + r"\M003_enclosure.f3d")))
    # 외함 조립 STEP (기준 STEP 은 빼고 생성물만): 기준 부품을 잠시 숨기지 않고, 생성 부품만 하나씩 STEP
    tb = adsk.fusion.TemporaryBRepManager.get()
    for o in list(root.occurrences):
        n = o.component.name
        if n in STL:
            bodies = [b for b in o.component.bRepBodies]
            tmp_occ = None
            target = o
            if len(bodies) > 1:   # 출력용 희생 기둥 등 → 한 셸로 합쳐서 STL
                acc = tb.copy(bodies[0])
                for b in bodies[1:]:
                    tb.booleanOperation(acc, tb.copy(b), adsk.fusion.BooleanTypes.UnionBooleanType)
                tmp_occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
                bf = tmp_occ.component.features.baseFeatures.add()
                bf.startEdit()
                tmp_occ.component.bRepBodies.add(acc, bf)
                bf.finishEdit()
                target = tmp_occ.component.bRepBodies.item(0)
            so = em.createSTLExportOptions(target, OUT + r"\stl\%s.stl" % n)
            so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            res.append(em.execute(so))
            if tmp_occ:
                tmp_occ.deleteMe()
        if n in STEP:
            res.append(em.execute(em.createSTEPExportOptions(OUT + r"\step\%s.step" % n, o.component)))
    # 전체 조립 (기준 보드 포함) STEP
    res.append(em.execute(em.createSTEPExportOptions(OUT + r"\M003_assembly_with_refs.step", root)))
    print('EXPORT', res, sorted(os.listdir(OUT + r"\stl")), sorted(os.listdir(OUT + r"\step")))
