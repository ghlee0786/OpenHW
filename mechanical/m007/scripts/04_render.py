"""M-007 04: 조립 렌더 (Fusion 뷰포트) — 앞 등각·뒤 등각·단면 x=0·단면 y=0·분해 → validation/runtime/vd001/render_m007/*.png (2560×1440)
화면 위 = +Y, 광축 +Z = 앞. 대체된 바디·플러그 블록·하니스 통로는 숨긴다(끝나면 되돌림)."""
import adsk.core, adsk.fusion, os

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
OUT = MAIN + r"\validation\runtime\vd001\render_m007"
HIDE_PREFIX = ('ENC_BLOCKS', 'BLK_J4_CARD', 'HARNESS_CORRIDOR', 'KEEPIN', 'ENVELOPE', 'PRINT_COUPON')
EXPLODE = {'FRONT_COVER': (0, 0, 45), 'LENS_WIN_PMMA': (0, 0, 70), 'WIN_A_PMMA': (0, 0, 70), 'WIN_B_PMMA': (0, 0, 70),
           'ALS_WIN_PMMA': (0, 0, 70), 'FOAM_LENS_RING': (0, 0, 25), 'FOAM_ALS_GASKET': (0, 0, 25), 'HS_EXTRUSION': (45, 0, 0),
           'HS_PEDESTAL': (25, 0, 0), 'GAP_PAD_PX': (15, 0, 0), 'HOUSING': (0, 0, -60), 'REF_CARRIER': (0, 0, -30)}
W, H = 2560, 1440


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    os.makedirs(OUT, exist_ok=True)
    vp = app.activeViewport
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    hidden = []
    for o in root.allOccurrences:
        if any(o.component.name.startswith(h) or h in o.component.name for h in HIDE_PREFIX) and o.isLightBulbOn:
            o.isLightBulbOn = False; hidden.append(o)

    def shot(name, eye, target=(0, -2, 8), up=(0, 1, 0)):
        cam = vp.camera
        cam.isSmoothTransition = False
        cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
        cam.eye = P3(*[v / 10 for v in eye]); cam.target = P3(*[v / 10 for v in target]); cam.upVector = V3(*up)
        vp.camera = cam; vp.fit(); adsk.doEvents(); vp.refresh()
        vp.saveAsImageFile(OUT + '\\' + name, W, H)

    shot('m007_front_iso.png', (160, 120, 270))
    shot('m007_back_iso.png', (-170, -100, -240))
    sa = design.analyses.sectionAnalyses
    sec = sa.add(sa.createInput(root.yZConstructionPlane, 0.0))
    shot('m007_section_x0.png', (320, 0, 8))
    sec.deleteMe()
    sec = sa.add(sa.createInput(root.xZConstructionPlane, 0.0))
    shot('m007_section_y0.png', (0, 320, 8), target=(0, 0, 8), up=(1, 0, 0))
    sec.deleteMe()
    moved = []
    for o in root.occurrences:
        v = EXPLODE.get(o.component.name)
        if v:
            moved.append((o, o.transform2))
            m = adsk.core.Matrix3D.create(); m.translation = V3(*[x / 10 for x in v])
            t0 = o.transform2.copy(); t0.transformBy(m); o.transform2 = t0
    shot('m007_exploded.png', (210, 150, 250), target=(0, 0, 5))
    for o, t in moved:
        o.transform2 = t
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.revertPendingSnapshot()
    for o in hidden:
        o.isLightBulbOn = True
    print('RENDER', sorted(os.listdir(OUT)))
