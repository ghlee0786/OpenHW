"""M-003 04: 내보내기 — 전체 F3D·STEP, 부품별 STL(출력 부품)·STEP(가공 부품). 출력 폴더 mechanical/m003/out."""
import adsk.core, adsk.fusion, os

OUT = r"C:\workspace_python\OpenHW\.harness-worktrees\t-20261127-013549-8089\mechanical\m003\out"
STL = ['HOUSING', 'FRONT_COVER']                                     # FDM 출력
STEP = ['HOUSING', 'FRONT_COVER', 'AL_HEATSINK_PX', 'SPREADER_M003', 'LENS_WIN_PMMA', 'WIN_A_PMMA', 'WIN_B_PMMA',
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
    for o in root.occurrences:
        n = o.component.name
        if n in STL:
            so = em.createSTLExportOptions(o, OUT + r"\stl\%s.stl" % n)
            so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            res.append(em.execute(so))
        if n in STEP:
            res.append(em.execute(em.createSTEPExportOptions(OUT + r"\step\%s.step" % n, o.component)))
    # 전체 조립 (기준 보드 포함) STEP
    res.append(em.execute(em.createSTEPExportOptions(OUT + r"\M003_assembly_with_refs.step", root)))
    print('EXPORT', res, sorted(os.listdir(OUT + r"\stl")), sorted(os.listdir(OUT + r"\step")))
