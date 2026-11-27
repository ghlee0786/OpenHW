"""REN-003 01 (Fusion, M007_assembly 문서) — 렌더용 보드 STEP(층 포함) 가져오기. [초안 · 미실행: KiCad 완료 알림 뒤 첫 실행 (D-003 #53)]
입력: main 체크아웃 validation/runtime/vd001/render/fusion/boards/<보드>_render.step
  (run_ren003.py 가 pcbsrc/<보드> 사본에서 kicad-cli export step --include-tracks/pads/zones/silkscreen/soldermask --user-origin 100x100mm 로 만듦)
동작: REN_CARRIER · REN_FRONT 로 가져와 판 아랫면 z 에 놓고, 판정용 REF_CARRIER · REF_FRONT(층 없음)는 숨긴다(지우지 않음 — 판정 03_judge 는 run_all 이 새 문서로 다시 돎).
실행: python -I -B mechanical/fusion_run.py mechanical/ren003/scripts/01_render_boards.py"""
import adsk.core, adsk.fusion

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물 (O-100)
B = MAIN + r"\validation\runtime\vd001\render\fusion\boards"


def run(_c):
    g = {}
    exec(open(LANE + r"\mechanical\m003\params.py", encoding="utf-8").read(), g)
    d = g['derive'](g['P'])
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    im = app.importManager
    for o in list(root.occurrences):
        if o.component.name in ('REN_CARRIER', 'REN_FRONT'):
            o.deleteMe()
    for name, f, z in (('REN_CARRIER', 'carrier', d['z_car_bot']), ('REN_FRONT', 'front', d['z_fr_bot'])):
        im.importToTarget(im.createSTEPImportOptions(B + '\\%s_render.step' % f), root)
        occ = root.occurrences.item(root.occurrences.count - 1); occ.component.name = name
        m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(0, 0, z * 0.1); occ.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
    for o in root.occurrences:
        if o.component.name in ('REF_CARRIER', 'REF_FRONT'):
            o.isLightBulbOn = False
    print('BOARDS', [(o.component.name, o.component.allOccurrences.count) for o in root.occurrences if o.component.name.startswith('REN_')])
