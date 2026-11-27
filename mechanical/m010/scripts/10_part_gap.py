"""M-010 10 (Fusion, M007_assembly 문서, 읽기만) — 보드 위 한 부품의 3D 모델 바디와 주변 기구 바디 사이 최소 틈 (O-124 「D5 이동」 재판정).
부품은 위치로 찾는다: 보드 바디 중 bbox 가운데가 (X, Y) 에서 TOL mm 안이고 보드 면 쪽에 있는 것. 결과 → main validation/runtime/vd001/m010_part_gap.json
실행: python -I -B mechanical/fusion_run.py mechanical/m010/scripts/10_part_gap.py --set "PART=front,D5,3.3,-2.55,B" --readonly"""
import adsk.core, adsk.fusion, json, os

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
PART = r"front,D5,3.3,-2.55,B"   # 보드, 참조, X, Y (기구 좌표 mm), 면 (F/B)
TOL = 1.2
SKIP = ('REF_', 'ENC_BLOCKS', 'BLK_', 'KEEPIN', 'ENVELOPE', 'HARNESS_CORRIDOR', 'PRINT_COUPON')


def run(_c):
    board, ref, x, y, side = PART.split(',')
    x, y = float(x), float(y)
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    top_name = 'REF_FRONT' if board == 'front' else 'REF_CARRIER'
    zb = {}
    exec(open(LANE + r"\mechanical\m003\params.py", encoding="utf-8").read(), zb)
    d = zb['derive'](zb['P'])
    z_bot = d['z_fr_bot'] if board == 'front' else d['z_car_bot']
    part, others = [], []
    for o in root.allOccurrences:
        t = o
        while t.assemblyContext:
            t = t.assemblyContext
        if not t.isLightBulbOn:
            continue
        for b in o.bRepBodies:
            if not b.isSolid or not b.isLightBulbOn:
                continue
            bb = b.boundingBox
            cx, cy, cz = [(getattr(bb.minPoint, k) + getattr(bb.maxPoint, k)) / 2 * 10 for k in 'xyz']
            if t.component.name == top_name:
                on_side = cz < z_bot if side == 'B' else cz > z_bot + 1.6
                if abs(cx - x) < TOL and abs(cy - y) < TOL and on_side:
                    part.append((b, o.component.name))
            elif not t.component.name.startswith(SKIP) and not o.component.name.startswith(SKIP):
                others.append((b, t.component.name if t.component.name != o.component.name else o.component.name))
    assert part, 'part body not found ' + PART
    mm = app.measureManager
    rows = []
    for b, n in others:
        dmin = min(mm.measureMinimumDistance(p, b).value * 10 for p, _ in part)
        rows.append({'body': n + '/' + b.name, 'min_mm': round(dmin, 3)})
    rows.sort(key=lambda r: r['min_mm'])
    pb = [p.boundingBox for p, _ in part]
    res = {'part': PART, 'model': sorted(set(n for _, n in part)), 'bodies': len(part),
           'z_mm': [round(min(b.minPoint.z for b in pb) * 10, 3), round(max(b.maxPoint.z for b in pb) * 10, 3)], 'nearest': rows[:8]}
    os.makedirs(MAIN + r"\validation\runtime\vd001", exist_ok=True)
    out = MAIN + r"\validation\runtime\vd001\m010_part_gap.json"
    allr = json.load(open(out, encoding='utf-8')) if os.path.exists(out) else {}
    allr[board + ':' + ref] = res
    json.dump(allr, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('PART_GAP', json.dumps(res, ensure_ascii=False))
