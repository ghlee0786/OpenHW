"""REN-001 01 (Fusion, M007_assembly 문서): 렌더용 메시 내보내기 → validation/runtime/vd001/render/mesh/<이름>.stl (mm, 월드 좌표)
보드(REF_CARRIER/REF_FRONT)는 KiCad GLB 로 따로 만들므로 빼고, 숨김(대체된) 바디·판정 블록도 뺀다."""
import adsk.core, adsk.fusion, os, json

LANE = r"C:\workspace_python\OpenHW"   # 소스 체크아웃 — mechanical/fusion_run.py 가 실행하는 스크립트의 체크아웃으로 바꿈
MAIN = r"C:\workspace_python\OpenHW"   # 산출물(validation/runtime) — main 체크아웃 (O-100)
OUT = MAIN + r"\validation\runtime\vd001\render\mesh"
SKIP = ('REF_CARRIER', 'REF_FRONT', 'ENC_BLOCKS', 'BLK_J4_CARD', 'PRINT_COUPON')
SKIP_STACK = ('KEEPIN', 'ENVELOPE', 'HARNESS_CORRIDOR', 'DF30_SITE')


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    em = design.exportManager
    os.makedirs(OUT, exist_ok=True)
    done = []
    for o in root.allOccurrences:
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        tn = top.component.name
        if tn in SKIP or not o.isLightBulbOn:
            continue
        name = o.component.name
        if tn == 'REF_STACK':
            if o == top or any(k in name for k in SKIP_STACK) or name == 'CORE_ENVELOPE_30x30' and False:
                continue
        elif o != top:
            continue
        bodies = [b for b in o.bRepBodies if b.isSolid and b.isLightBulbOn and not b.name.startswith('PRINT_TAB')]
        if not bodies:
            continue
        for i, b in enumerate(bodies):
            fn = '%s%s.stl' % (name, '' if len(bodies) == 1 else '__%d' % i)
            so = em.createSTLExportOptions(b, os.path.join(OUT, fn))
            so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            so.isBinaryFormat = True
            em.execute(so)
            done.append(fn)
    # 코어 외형은 KEEPIN/ENVELOPE 걸러짐 → 따로 (렌더용 코어 덩어리)
    for o in root.allOccurrences:
        if o.component.name == 'CORE_ENVELOPE_30x30':
            em.execute(em.createSTLExportOptions(o.bRepBodies.item(0), os.path.join(OUT, 'CORE_MODULE.stl')))
            done.append('CORE_MODULE.stl')
    json.dump(sorted(done), open(os.path.join(OUT, 'index.json'), 'w'), indent=0)
    print('MESH', len(done))
