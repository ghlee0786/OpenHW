"""M-003 05: 렌더(뷰포트 캡처) — 앞 등각·뒤 등각·YZ 단면(x=0)·분해. 출력 mechanical/m003/render/*.png
화면 위쪽 = +Y (센서 세로), 광축 +Z = 앞. 기준 중복·대체된 바디와 플러그 블록은 숨긴다(끝나면 되돌림)."""
import adsk.core, adsk.fusion, os

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
OUT = LANE + r"\mechanical\m003\render"
HIDE = ('CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER_TAB_PX', 'THERMAL_PILLAR', 'INS_PAD_',
        'KEEPIN', 'HARNESS_CORRIDOR', 'ENVELOPE', 'DF30_SITE', 'J_ICR')
EXPLODE = {'FRONT_COVER': (0, 0, 45), 'LENS_WIN_PMMA': (0, 0, 70), 'WIN_A_PMMA': (0, 0, 70), 'WIN_B_PMMA': (0, 0, 70),
           'ALS_WIN_PMMA': (0, 0, 70), 'FOAM_LENS_RING': (0, 0, 22), 'FOAM_ALS_GASKET': (0, 0, 22), 'HS_EXTRUSION': (45, 0, 0), 'HS_PEDESTAL': (22, 0, 0),
           'GAP_PAD_PX': (25, 0, 0), 'HOUSING': (0, 0, -55)}


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M003_enclosure', 'wrong document'
    root = design.rootComponent
    os.makedirs(OUT, exist_ok=True)
    vp = app.activeViewport
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    hidden = []
    for o in root.allOccurrences:
        n = o.component.name
        if n in ('ENC_BLOCKS', 'PRINT_COUPON') or any(h in n for h in HIDE):
            if o.isLightBulbOn:
                o.isLightBulbOn = False
                hidden.append(o)

    def shot(name, eye, target=(0, -2, 8), up=(0, 1, 0)):
        cam = vp.camera
        cam.isSmoothTransition = False
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        cam.eye = P3(*[v / 10 for v in eye])
        cam.target = P3(*[v / 10 for v in target])
        cam.upVector = V3(*up)
        vp.camera = cam
        vp.fit()
        adsk.doEvents()
        vp.refresh()
        vp.saveAsImageFile(OUT + '\\' + name, 1600, 1200)

    shot('m003_front_iso.png', (150, 110, 260))
    shot('m003_back_iso.png', (-160, -90, -230))
    # 단면 x = 0 (YZ 평면), +X 쪽에서 봄
    sa = design.analyses.sectionAnalyses
    si = sa.createInput(root.yZConstructionPlane, 0.0)
    si.isHatchShown = True
    sec = sa.add(si)
    shot('m003_section_x0.png', (300, 0, 8), target=(0, -2, 8))
    sec.deleteMe()
    # 단면 y = 0 (XZ 평면), +Y 쪽에서 봄
    si = sa.createInput(root.xZConstructionPlane, 0.0)
    si.isHatchShown = True
    sec = sa.add(si)
    shot('m003_section_y0.png', (0, 300, 8), target=(0, 0, 8), up=(1, 0, 0))
    sec.deleteMe()
    # 분해 (임시 이동 → 캡처 → 되돌림)
    moved = []
    for o in root.occurrences:
        v = EXPLODE.get(o.component.name)
        if v:
            m = adsk.core.Matrix3D.create()
            m.translation = V3(*[x / 10 for x in v])
            moved.append((o, o.transform2))
            o.transform2 = m
    shot('m003_exploded.png', (190, 140, 230), target=(0, 0, 10))
    for o, t in moved:
        o.transform2 = t
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.revertPendingSnapshot()
    for o in hidden:
        o.isLightBulbOn = True
    print('RENDER', sorted(os.listdir(OUT)))
