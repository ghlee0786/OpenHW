"""M-007 03: 기계 판정 (Fusion, M007_assembly 문서) → validation/runtime/vd001/m007_judge.json
J1 바디 쌍 간섭 (의도된 쌍은 asm_spec.INTENDED 이름 규칙으로 제외·목록) · J2 최소 틈 표 · J3 플러그·카드 삽입 공간 ·
J4 광축 ↔ 렌즈 창 중심 어긋남 · J5 LED 직접광 광선 추적 (시야 방향마다 처음 맞는 바디가 PMMA 창인지) · J6 짝 BTB 결합 높이."""
import adsk.core, adsk.fusion, re, json, math, os

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
OUT = MAIN + r"\validation\runtime\vd001"


def run(_c):
    g = {}
    exec(open(LANE + r"\mechanical\m003\params.py", encoding="utf-8").read(), g)
    s = {}
    exec(open(LANE + r"\mechanical\m007\asm_spec.py", encoding="utf-8").read(), s)
    d = g['derive'](g['P'])
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M007_assembly', 'wrong document'
    root = design.rootComponent
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    res = {'fail': 0}

    # ---- 바디 목록: 이름 있는 것(생성물·기준 적층) / 보드 ----
    named, boards = [], []
    for o in root.allOccurrences:
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        tn = top.component.name
        if not o.isLightBulbOn or (top != o and not top.isLightBulbOn):
            continue
        for b in o.bRepBodies:
            if not b.isSolid or not b.isLightBulbOn:
                continue
            if tn in ('REF_CARRIER', 'REF_FRONT'):   # 보드 바디는 KiCad 모델 이름으로 (M-010: pcb 가 실제 모델을 연결 → 같은 부품 대체 블록과 구분)
                boards.append((b, 'BOARD_PART:' + re.sub(r' \(\d+\)$', '', o.component.name)))
            else:
                nm = o.component.name if tn == 'REF_STACK' else (b.name if tn in ('ENC_BLOCKS', 'HARNESS_GH6P') else tn)
                if tn.endswith('_M008') and tn != 'DF30_M008':
                    nm = tn
                named.append((b, nm))

    # M-010: 3D 모델이 모두 연결된 보드의 대체 블록은 뺀다 (asm_spec.SUBST_BLOCKS, run_all.py 의 models_missing.json)
    mmj = os.path.join(OUT, 'boards', 'models_missing.json')
    after = json.load(open(mmj, encoding='utf-8')).get('missing_after_apply', {}) if os.path.exists(mmj) else {}
    drop = [n for bd, ns in s['SUBST_BLOCKS'].items() if bd in after and not after[bd] for n in ns]
    named = [(b, n) for b, n in named if n not in drop]
    res['dropped_blocks'] = drop

    def sig(b):
        bb = b.boundingBox
        return (round(b.volume, 6), round(bb.minPoint.x, 4), round(bb.minPoint.y, 4), round(bb.minPoint.z, 4), round(bb.maxPoint.z, 4))
    table = {sig(b): n for b, n in named}
    btable = {sig(b): n for b, n in boards}
    bvol = {}
    for b, n in boards:
        bvol.setdefault(round(b.volume, 6), []).append((b.boundingBox, n))

    def intended(a, b, where):
        cx, cy, cz = (where[0] + where[1]) / 2, (where[2] + where[3]) / 2, (where[4] + where[5]) / 2
        for e in s['INTENDED']:
            p, q, why = e[0], e[1], e[2]
            if (a.startswith(p) and b.startswith(q)) or (a.startswith(q) and b.startswith(p)):
                if len(e) > 3:
                    x0, x1, y0, y1, z0, z1 = e[3]
                    if not (x0 <= cx <= x1 and y0 <= cy <= y1 and z0 <= cz <= z1):
                        continue
                return why
        return None

    # ---- J1 간섭 ----
    coll = adsk.core.ObjectCollection.create()
    for b, _ in named + boards:
        coll.add(b)
    inp = design.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
    r = design.analyzeInterference(inp)
    j1 = {'bodies': coll.count, 'intended': [], 'fail': []}
    for i in range(0 if r is None else r.count):
        it = r.item(i)
        a, b = table.get(sig(it.entityOne)), table.get(sig(it.entityTwo))
        ib = it.interferenceBody.boundingBox
        ic = ib.minPoint.copy(); ic.x = (ib.minPoint.x + ib.maxPoint.x) / 2; ic.y = (ib.minPoint.y + ib.maxPoint.y) / 2; ic.z = (ib.minPoint.z + ib.maxPoint.z) / 2

        def bname(e):   # 간섭 결과의 보드 바디는 프록시가 아닐 수 있어 sig 가 다름 → 같은 부피 + 겹친 곳 가운데를 품는 보드 바디
            n = btable.get(sig(e))
            if n:
                return n
            for bb_, nm_ in bvol.get(round(e.volume, 6), []):
                if bb_.contains(ic):
                    return nm_
            return None
        ba_, bb2 = bname(it.entityOne), bname(it.entityTwo)
        where = [round(v * 10, 2) for v in (ib.minPoint.x, ib.maxPoint.x, ib.minPoint.y, ib.maxPoint.y, ib.minPoint.z, ib.maxPoint.z)]
        vol = round(it.interferenceBody.volume * 1000, 3)
        if a is None and b is None:
            continue                     # 보드 안 (KiCad 부품 모델 ↔ 자기 보드) — 판정 밖
        a = a or ba_ or 'BOARD_PART'; b = b or bb2 or 'BOARD_PART'
        why = intended(a, b, where)
        (j1['intended'] if why else j1['fail']).append({'a': a, 'b': b, 'mm3': vol, 'at': where, 'why': why})
    res['J1'] = j1; res['fail'] += len(j1['fail'])

    # ---- J2 최소 틈 ----
    mm = app.measureManager

    def bodies_of(name):
        return [b for b, n in named if n.startswith(name)]
    j2 = []
    for a, b, need in s['CLEARANCE_PAIRS']:
        ba, bb_ = bodies_of(a), bodies_of(b)
        if not ba or not bb_:
            j2.append({'a': a, 'b': b, 'min_mm': None, 'need': need, 'ok': False, 'note': '바디 없음'}); res['fail'] += 1; continue
        dmin = min(mm.measureMinimumDistance(x, y).value * 10 for x in ba for y in bb_)
        ok = dmin >= need - 1e-6
        j2.append({'a': a, 'b': b, 'min_mm': round(dmin, 3), 'need': need, 'ok': ok})
        res['fail'] += 0 if ok else 1
    res['J2'] = j2

    # ---- J3 삽입 공간 (J1 에서 BLK_*_PLUG/CARD 가 낀 실패만 모아 다시 표시) ----
    res['J3'] = [x for x in j1['fail'] if x['a'].startswith('BLK_') and ('PLUG' in x['a'] or 'CARD' in x['a'])
                 or x['b'].startswith('BLK_') and ('PLUG' in x['b'] or 'CARD' in x['b'])]

    # ---- J4 광축 ↔ 렌즈 창 ----
    def centre(name):
        bs = bodies_of(name)
        bb = bs[0].boundingBox
        return ((bb.minPoint.x + bb.maxPoint.x) * 5, (bb.minPoint.y + bb.maxPoint.y) * 5)
    lx, ly = centre('LENS_CIL093'); wx, wy = centre('LENS_WIN_PMMA')
    off = math.hypot(lx - wx, ly - wy)
    res['J4'] = {'lens_xy': [round(lx, 3), round(ly, 3)], 'window_xy': [round(wx, 3), round(wy, 3)], 'offset_mm': round(off, 3), 'ok': off <= 0.1}
    res['fail'] += 0 if off <= 0.1 else 1

    # ---- J5 LED 직접광 광선 추적 ----
    HFOV, NV, NH = 88.0, 13, 19
    VFOV = 2 * math.degrees(math.atan(math.tan(math.radians(HFOV / 2)) * 1080 / 1920))
    tH, tV = math.tan(math.radians(HFOV / 2)), math.tan(math.radians(VFOV / 2))
    leds = [(n, centre(n)) for n in ('LED_A1', 'LED_A2', 'LED_B1_DNP', 'LED_B2_DNP')]
    ztop = d['z_led_top'] + 0.05
    windows = ('LENS_WIN_PMMA', 'WIN_A_PMMA', 'WIN_B_PMMA', 'ALS_WIN_PMMA')
    lit = 0; blockers = {}
    for i in range(NH):
        for j in range(NV):
            tx = -tH + 2 * tH * i / (NH - 1); ty = -tV + 2 * tV * j / (NV - 1)
            n = math.sqrt(tx * tx + ty * ty + 1)
            any_ok = False
            for nm, (x, y) in leds:
                hp = adsk.core.ObjectCollection.create()
                hits = root.findBRepUsingRay(P3(x / 10, y / 10, ztop / 10), V3(tx / n, ty / n, 1 / n),
                                             adsk.fusion.BRepEntityTypes.BRepBodyEntityType, 0.0001, True, hp)
                best, bd = None, 1e9
                for k in range(hits.count):
                    p = hp.item(k)
                    dd = math.dist((p.x, p.y, p.z), (x / 10, y / 10, ztop / 10))
                    if dd < bd:
                        bd, best = dd, hits.item(k)
                name = table.get(sig(best), 'BOARD_PART') if best else None
                if name is None or name.startswith(windows):
                    any_ok = True
                else:
                    blockers[name] = blockers.get(name, 0) + 1
            lit += any_ok
    cov = lit / (NH * NV)
    res['J5'] = {'grid': [NH, NV], 'coverage_A_B': round(cov * 100, 1), 'baseline_pct': 86.0, 'blockers': blockers, 'ok': cov * 100 >= 84.0}
    res['fail'] += 0 if res['J5']['ok'] else 1

    # ---- J6 짝 BTB 결합 높이 ----
    zc = {o.component.name: o.transform2.translation.z * 10 for o in root.occurrences if o.component.name in ('REF_CARRIER', 'REF_FRONT')}
    h_bot = 0.0 - (zc['REF_CARRIER'] + 1.6); h_top = zc['REF_FRONT'] - 1.6
    res['J6'] = {'core_to_carrier_top': round(h_bot, 3), 'front_bottom_to_core_top': round(h_top, 3), 'expected': 8.0,
                 'ok': abs(h_bot - 8.0) < 1e-3 and abs(h_top - 8.0) < 1e-3, 'note': 'M-006: 3D 모델은 단순화라 결합 높이 판정 불가 → 3사 높이표 8.00'}
    res['fail'] += 0 if res['J6']['ok'] else 1
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(OUT + r"\m007_judge.json", 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('JUDGE fail', res['fail'])
