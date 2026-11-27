"""O-125 시안 간섭 교차 확인 (Fusion, 읽기만) — 시안 바디마다 내부 적층(REF_*) 바디까지 최소 거리 mm. 0 이하면 닿음/겹침.
실행: python -I -B mechanical/fusion_run.py mechanical/design/o125_gap.py --readonly"""
import adsk.core, adsk.fusion, json, os

LANE = None
MAIN = None


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    tag = design.attributes.itemByName('openhw', 'doc').value
    assert tag.startswith('O125_'), 'wrong document'
    root = design.rootComponent
    comp = [o for o in root.occurrences if o.component.name.startswith('DESIGN_')][0]
    refs = []
    for o in root.allOccurrences:
        t = o
        while t.assemblyContext:
            t = t.assemblyContext
        if t.component.name.startswith('REF_'):
            refs += [b for b in o.bRepBodies if b.isSolid and o.isLightBulbOn]   # 숨김 기준 = 가져올 때 뺀 자리 표시 (불 켜짐 상태로 판정)
    mm = app.measureManager
    res = {}
    for b in comp.bRepBodies:
        best = min(((mm.measureMinimumDistance(b, r).value * 10, r.name) for r in refs), key=lambda x: x[0])
        res[b.name] = [round(best[0], 3), best[1]]
    out = os.path.join(MAIN, 'validation', 'runtime', 'vd001', 'design', tag[5:], 'gap.json')
    json.dump({'refs': len(refs), 'min_gap_mm': res}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('GAP', len(refs), json.dumps(res, ensure_ascii=False))
