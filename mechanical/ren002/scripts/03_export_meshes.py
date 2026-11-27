"""REN-002 03 (Fusion, M007_assembly 문서): 렌더용 메시 → validation/runtime/vd001/render/mesh/<이름>.stl (mm, 월드 좌표)
보드는 렌더용 사본 GLB(대체 3D 모델 연결)로 따로 넣으므로 빼고, GLB 안에 이미 들어간 부품(CLA216 홀더·스페이서·리드·ICR 패드, DF30, IR LED)과
숨김·판정 블록도 뺀다 (REN-001 01_export_meshes.py 와 차이는 EXCL_DUP 뿐)."""
import adsk.core, adsk.fusion, os, json

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
OUT = MAIN + r"\validation\runtime\vd001\render\mesh"
SKIP = ('REF_CARRIER', 'REF_FRONT', 'ENC_BLOCKS', 'BLK_J4_CARD', 'PRINT_COUPON')
SKIP_STACK = ('KEEPIN', 'ENVELOPE', 'HARNESS_CORRIDOR', 'DF30_SITE')
EXCL_DUP = ('CLA216_M008', 'SPACER_M008', 'ICR_LEAD_M008', 'ICR_PADS_M008', 'DF30_M008', 'LED_A1', 'LED_A2', 'LED_B1_DNP', 'LED_B2_DNP')


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    em = design.exportManager
    os.makedirs(OUT, exist_ok=True)
    for f in os.listdir(OUT):
        if f.endswith('.stl'):
            os.remove(os.path.join(OUT, f))
    done = []
    for o in root.allOccurrences:
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        tn = top.component.name
        name = o.component.name
        if tn in SKIP or not o.isLightBulbOn or name in EXCL_DUP:
            continue
        if tn == 'REF_STACK':
            if o == top or any(k in name for k in SKIP_STACK):
                continue
        elif o != top:
            continue
        bodies = [b for b in o.bRepBodies if b.isSolid and b.isLightBulbOn and not b.name.startswith('PRINT_TAB')]
        for i, b in enumerate(bodies):
            fn = '%s%s.stl' % (name, '' if len(bodies) == 1 else '__%d' % i)
            so = em.createSTLExportOptions(b, os.path.join(OUT, fn))
            so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
            so.isBinaryFormat = True
            em.execute(so)
            done.append(fn)
    for o in root.allOccurrences:
        if o.component.name == 'CORE_ENVELOPE_30x30':
            em.execute(em.createSTLExportOptions(o.bRepBodies.item(0), os.path.join(OUT, 'CORE_MODULE.stl')))
            done.append('CORE_MODULE.stl')
    json.dump(sorted(done), open(os.path.join(OUT, 'index.json'), 'w'), indent=0)
    print('MESH', len(done), sorted(done))
