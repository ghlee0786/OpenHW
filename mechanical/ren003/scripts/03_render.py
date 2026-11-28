"""REN-003 03 (Fusion, M007_assembly 문서) — 로컬 렌더 한 장 시작 (보기 하나). 결과 → main validation/runtime/vd001/render/fusion/ren003_<보기>.png
· 로컬 렌더만: Rendering.startLocalRender(파일, 카메라). 파일 이름이 비면 Fusion 이 클라우드에 저장하므로 절대 경로 .png 를 꼭 넘긴다(아래 assert).
· 렌더는 Fusion 의 백그라운드 프로세스라 이 스크립트는 시작만 하고 돌아온다 — 끝났는지는 run_ren003.py 가 파일로 본다.
· VIEW=restore: 분해 위치·숨김을 되돌림 (숨긴 목록은 문서 속성 openhw/ren003_hidden).
· 보기: front · back · threequarter · exploded · window(창 너머) · connectors — REN-002 Blender 보기와 같은 이름·방향. 2560×1440, 품질 75(Final).
실행: python -I -B mechanical/fusion_run.py mechanical/ren003/scripts/03_render.py --set VIEW=<보기|restore>"""
import adsk.core, adsk.fusion, json, os

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
VIEW = r"front"
W, H, QUALITY = 2560, 1440, 75
HIDE = ('ENC_BLOCKS', 'BLK_J4_CARD', 'PRINT_COUPON', 'KEEPIN', 'ENVELOPE', 'HARNESS_CORRIDOR', 'DF30_SITE', 'J_ICR', 'REF_CARRIER', 'REF_FRONT',
        'CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER_TAB_PX', 'THERMAL_PILLAR', 'INS_PAD_')
EXPLODE = {'FRONT_COVER': (0, 0, 45), 'LENS_WIN_PMMA': (0, 0, 70), 'WIN_A_PMMA': (0, 0, 70), 'WIN_B_PMMA': (0, 0, 70),
           'ALS_WIN_PMMA': (0, 0, 70), 'FOAM_LENS_RING': (0, 0, 22), 'FOAM_ALS_GASKET': (0, 0, 22), 'HS_EXTRUSION': (45, 0, 0),
           'HS_PEDESTAL': (22, 0, 0), 'GAP_PAD_PX': (25, 0, 0), 'HOUSING': (0, 0, -55)}   # m003 05_render.py 와 같음 (mm)
# (눈 mm, 목표 mm, 위) — 제품 좌표: +Z 광축(앞), +Y 위
VIEWS = {'front': ((40, 25, 260), (0, -2, 8), (0, 1, 0)),
         'back': ((-60, 30, -240), (0, -2, 8), (0, 1, 0)),
         'threequarter': ((150, 110, 260), (0, -2, 8), (0, 1, 0)),
         'exploded': ((190, 140, 230), (0, 0, 10), (0, 1, 0)),
         'window': ((0, 6, 120), (0, 0, 12), (0, 1, 0)),
         'connectors': ((-60, -220, -40), (0, -20, -10), (0, 0, 1))}


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    att = design.attributes.itemByName('openhw', 'ren003_hidden')
    if VIEW == 'restore':
        if design.snapshots.hasPendingSnapshot:
            design.snapshots.revertPendingSnapshot()
        names = set(json.loads(att.value)) if att else set()
        n = 0
        for o in root.allOccurrences:
            if o.fullPathName in names:
                o.isLightBulbOn = True; n += 1
        if att:
            att.deleteMe()
        print('RESTORED', n)
        return
    eye, tgt, up = VIEWS[VIEW]
    hidden = set(json.loads(att.value)) if att else set()
    for o in root.allOccurrences:
        if any(h in o.component.name for h in HIDE) and o.isLightBulbOn:
            o.isLightBulbOn = False; hidden.add(o.fullPathName)
    design.attributes.add('openhw', 'ren003_hidden', json.dumps(sorted(hidden)))
    if design.snapshots.hasPendingSnapshot:          # 앞 보기(분해) 위치를 되돌림
        design.snapshots.revertPendingSnapshot()
    if VIEW == 'exploded':
        for o in root.occurrences:
            v = EXPLODE.get(o.component.name)
            if v:
                m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(*[x / 10 for x in v]); o.transform2 = m
    rd = design.renderManager.rendering
    rd.aspectRatio = adsk.fusion.RenderAspectRatios.CustomRenderAspectRatio
    rd.resolutionWidth, rd.resolutionHeight = W, H
    rd.renderQuality = QUALITY
    rd.isBackgroundTransparent = False
    vp = app.activeViewport
    cam = vp.camera
    cam.isSmoothTransition = False
    cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    cam.eye, cam.target, cam.upVector = P3(*[v / 10 for v in eye]), P3(*[v / 10 for v in tgt]), V3(*up)
    vp.camera = cam; vp.fit(); adsk.doEvents()
    out = MAIN + r"\validation\runtime\vd001\render\fusion"
    os.makedirs(out, exist_ok=True)
    f = out + '\\ren003_%s.png' % VIEW
    if os.path.exists(f):
        os.remove(f)
    assert os.path.isabs(f) and f.lower().endswith('.png'), 'local render needs an absolute file path (empty = cloud)'
    fut = rd.startLocalRender(f, vp.camera)
    print('STARTED', VIEW, f, str(fut.renderState))
