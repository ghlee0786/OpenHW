"""M-003c 06: 조립 단계 렌더 ①~⑨ (assembly-procedure.md 용). 단계마다 보일 부품만 켜고 캡처 → render/steps/step_N.png
끝나면 보이기 상태를 되돌린다."""
import adsk.core, adsk.fusion, os

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
OUT = LANE + r"\mechanical\m003\render\steps"
HOUSE = ['HOUSING', 'HS_EXTRUSION', 'HS_PEDESTAL', 'HW_M25_NUTS']
CORE = ['REF_CARRIER', 'HW_STANDOFFS', 'CORE_ENVELOPE', 'J1_MATED', 'J2_MATED']
SPR = ['SPREADER_M003', 'INS_PADS_P340', 'GAP_PAD_PX']
FRONT = ['REF_FRONT', 'PEDESTAL', 'SENSOR_BLOCK', 'FPC_3mm', 'HOLDER_SPACER', 'CLA216', 'LENS_THREAD', 'LENS_STEP', 'LENS_HEAD',
         'LENS_DOME', 'ICR_LEAD', 'LED_', 'HW_M16_HEADS']
HARN = ['GH6P_', 'HARNESS_CORRIDOR', 'FOAM_ALS_GASKET']
COVER = ['FRONT_COVER', 'LENS_WIN_PMMA', 'WIN_A_PMMA', 'WIN_B_PMMA', 'ALS_WIN_PMMA']
STEPS = [
    (1, HOUSE[:1]),
    (2, HOUSE),
    (3, CORE),
    (4, CORE + SPR),
    (5, CORE + SPR + FRONT),
    (6, CORE + SPR + FRONT + HARN),
    (7, HOUSE + CORE + SPR + FRONT + HARN),
    (8, HOUSE + CORE + SPR + FRONT + HARN + ['FOAM_LENS_RING']),
    (9, HOUSE + CORE + SPR + FRONT + HARN + ['FOAM_LENS_RING'] + COVER),
]


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M003_enclosure', 'wrong document'
    root = design.rootComponent
    os.makedirs(OUT, exist_ok=True)
    vp = app.activeViewport
    occs = list(root.allOccurrences)
    saved = [(o, o.isLightBulbOn) for o in occs]
    stack = [o for o in root.occurrences if o.component.name.startswith('REF_STACK')][0]

    def show(keys):
        for o in root.occurrences:
            n = o.component.name
            if n.startswith('REF_STACK'):
                o.isLightBulbOn = True
                for ch in o.childOccurrences:
                    ch.isLightBulbOn = any(ch.component.name.startswith(k) for k in keys)
            else:
                o.isLightBulbOn = any(n.startswith(k) for k in keys) and n != 'PRINT_COUPON'
    cam = vp.camera
    for n, keys in STEPS:
        show(keys)
        cam = vp.camera
        cam.isSmoothTransition = False
        cam.eye = adsk.core.Point3D.create(17, 9, 24)
        cam.target = adsk.core.Point3D.create(0.4, -0.2, 0.8)
        cam.upVector = adsk.core.Vector3D.create(0, 1, 0)
        vp.camera = cam
        vp.fit()
        adsk.doEvents()
        vp.refresh()
        vp.saveAsImageFile(OUT + '\\step_%d.png' % n, 1200, 900)
    for o, s in saved:
        o.isLightBulbOn = s
    print('STEPS', sorted(os.listdir(OUT)))
