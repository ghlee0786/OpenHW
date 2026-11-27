"""REN-003 03 (Fusion, M007_assembly 문서) — 로컬 렌더 제품 샷 6장 2560×1440 → main validation/runtime/vd001/render/fusion/ren003_<보기>.png
[초안 · 미실행 — 첫 실행 전에 `fusion_cli.py docs RenderManager` / `docs startLocalRender` 로 이 판의 API 이름 확인]
· 클라우드 렌더·크레딧 금지: startLocalRender 만 쓴다. 로컬 렌더 API 가 없으면 예외로 멈춘다(뷰포트 캡처로 바꿔 「렌더」라 부르지 않음).
· 보기: front · back · threequarter · exploded · window(창 너머) · connectors — REN-002 Blender 보기와 같은 이름·방향.
· 판정용 덩어리(ENC_BLOCKS · KEEPIN · ENVELOPE · 통로 · 대체된 기준)와 REF_CARRIER/REF_FRONT 는 숨긴다(끝나면 되돌림).
실행: python -I -B mechanical/fusion_run.py mechanical/ren003/scripts/03_render.py"""
import adsk.core, adsk.fusion, os, time

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물 (O-100)
OUT = MAIN + r"\validation\runtime\vd001\render\fusion"
W, H = 2560, 1440
HIDE = ('ENC_BLOCKS', 'BLK_J4_CARD', 'PRINT_COUPON', 'KEEPIN', 'ENVELOPE', 'HARNESS_CORRIDOR', 'DF30_SITE', 'J_ICR', 'REF_CARRIER', 'REF_FRONT',
        'CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER_TAB_PX', 'THERMAL_PILLAR', 'INS_PAD_')
EXPLODE = {'FRONT_COVER': (0, 0, 45), 'LENS_WIN_PMMA': (0, 0, 70), 'WIN_A_PMMA': (0, 0, 70), 'WIN_B_PMMA': (0, 0, 70),
           'ALS_WIN_PMMA': (0, 0, 70), 'FOAM_LENS_RING': (0, 0, 22), 'FOAM_ALS_GASKET': (0, 0, 22), 'HS_EXTRUSION': (45, 0, 0),
           'HS_PEDESTAL': (22, 0, 0), 'GAP_PAD_PX': (25, 0, 0), 'HOUSING': (0, 0, -55)}   # m003 05_render.py 와 같음 (mm)
# (보기, 눈 mm, 목표 mm, 위) — 제품 좌표: +Z 광축(앞), +Y 위
VIEWS = [('front', (40, 25, 260), (0, -2, 8), (0, 1, 0)),
         ('back', (-60, 30, -240), (0, -2, 8), (0, 1, 0)),
         ('threequarter', (150, 110, 260), (0, -2, 8), (0, 1, 0)),
         ('exploded', (190, 140, 230), (0, 0, 10), (0, 1, 0)),
         ('window', (0, 6, 120), (0, 0, 12), (0, 1, 0)),
         ('connectors', (-60, -220, -40), (0, -20, -10), (0, 0, 1))]


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    rm = getattr(design, 'renderManager', None)     # [미확인] API 이름
    assert rm is not None, 'no local render API (renderManager) in this Fusion build'
    root = design.rootComponent
    os.makedirs(OUT, exist_ok=True)
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    hidden = []
    for o in root.allOccurrences:
        if any(h in o.component.name for h in HIDE) and o.isLightBulbOn:
            o.isLightBulbOn = False; hidden.append(o)
    rd = rm.rendering                               # [미확인]
    rd.resolution = adsk.fusion.RenderResolutions.CustomRenderResolution if hasattr(adsk.fusion, 'RenderResolutions') else rd.resolution
    if hasattr(rd, 'resolutionWidth'):
        rd.resolutionWidth, rd.resolutionHeight = W, H
    moved = []
    done = []
    try:
        for name, eye, tgt, up in VIEWS:
            if name == 'exploded':
                for o in root.occurrences:
                    v = EXPLODE.get(o.component.name)
                    if v:
                        m = adsk.core.Matrix3D.create(); m.translation = V3(*[x / 10 for x in v])
                        moved.append((o, o.transform2)); o.transform2 = m
            cam = app.activeViewport.camera
            cam.isSmoothTransition = False
            cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
            cam.eye, cam.target, cam.upVector = P3(*[v / 10 for v in eye]), P3(*[v / 10 for v in tgt]), V3(*up)
            app.activeViewport.camera = cam; app.activeViewport.fit()
            f = OUT + '\\ren003_%s.png' % name
            fut = rd.startLocalRender(f, cam)       # [미확인] 로컬 렌더 (클라우드 아님)
            t0 = time.time()
            while fut.renderState not in (adsk.fusion.LocalRenderStates.FinishedLocalRenderState, adsk.fusion.LocalRenderStates.FailedLocalRenderState):
                adsk.doEvents(); time.sleep(1)
                assert time.time() - t0 < 1800, 'render timeout ' + name
            done.append((name, str(fut.renderState), os.path.exists(f)))
            for o, t in moved:
                o.transform2 = t
            moved = []
    finally:
        for o, t in moved:
            o.transform2 = t
        if design.snapshots.hasPendingSnapshot:
            design.snapshots.revertPendingSnapshot()
        for o in hidden:
            o.isLightBulbOn = True
    print('RENDER', done)
