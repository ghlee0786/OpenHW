"""M-003 03: 간섭 검사. 외함 생성물(부품·대체 블록) ↔ 기준(KiCad 보드 STEP·M-002b 적층) 과 생성물끼리.
맞닿는 면은 빼고(areCoincidentFacesIncluded=False) 부피가 있는 겹침만 센다. 결과를 m003/interference.txt 로 쓴다."""
import adsk.core, adsk.fusion

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 이 스크립트의 체크아웃 경로로 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움 (산출물 validation/runtime, O-100)
BASE = LANE + r"\mechanical\m003"
TXT = BASE + r"\interference.txt"   # M-010 run_case.py 는 --set TXT=<main>\validation\runtime\vd001\case\interference.txt
# 기준 중 이번 외함으로 대체된 것 (같은 자리 중복 또는 M-003에서 바뀐 것)
SUPERSEDED = {'CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER_TAB_PX',
              'THERMAL_PILLAR_A', 'THERMAL_PILLAR_B', 'INS_PAD_A', 'INS_PAD_B1', 'INS_PAD_B2'}
GEN_COMPS = None


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M003_enclosure', 'wrong document'
    root = design.rootComponent
    # M-010: 3D 모델이 모두 연결된 보드의 「모델 없는 부품 대체 블록」은 뺀다 (mechanical/m007/asm_spec.py SUBST_BLOCKS, run_all.py models_missing.json)
    import json, os
    s = {}
    exec(open(LANE + r"\mechanical\m007\asm_spec.py", encoding="utf-8").read(), s)
    mmj = MAIN + r"\validation\runtime\vd001\boards\models_missing.json"
    after = json.load(open(mmj, encoding='utf-8')).get('missing_after_apply', {}) if os.path.exists(mmj) else {}
    drop = {n for bd, ns in s['SUBST_BLOCKS'].items() if bd in after and not after[bd] for n in ns}
    gen, ref = [], []
    for o in root.allOccurrences:
        top = o
        while top.assemblyContext:
            top = top.assemblyContext
        tn = top.component.name
        for b in o.bRepBodies:
            if not b.isSolid or b.name.startswith(('PRINT_TAB_', 'PRINT_COUPON')):   # 출력용 희생 기둥은 조립 전 잘라냄
                continue
            if tn.startswith('REF_'):
                # KiCad 일반 DC 잭 모델은 XKB 블록으로 대체
                if 'BarrelJack' in o.component.name or b.name in SUPERSEDED or o.component.name in SUPERSEDED:
                    continue
                ref.append((b, tn + '/' + (o.component.name if o.component.name != tn else b.name)))
            else:
                if tn == 'ENC_BLOCKS' and b.name in drop:
                    continue
                gen.append((b, tn if tn != 'ENC_BLOCKS' else b.name))
    coll = adsk.core.ObjectCollection.create()
    for b, n in gen + ref:
        coll.add(b)
    inp = design.createInterferenceInput(coll)
    inp.areCoincidentFacesIncluded = False
    res = design.analyzeInterference(inp)

    def sig(b):
        bb = b.boundingBox
        return (b.name, round(b.volume, 6), round(bb.minPoint.x, 4), round(bb.minPoint.y, 4), round(bb.minPoint.z, 4),
                round(bb.maxPoint.x, 4), round(bb.maxPoint.y, 4), round(bb.maxPoint.z, 4))
    table = {}
    for b, n in ref:
        table[sig(b)] = (n, False)
    for b, n in gen:
        table[sig(b)] = (n, True)

    vol = {}
    for b, n in ref:
        vol.setdefault(round(b.volume, 6), []).append((b.boundingBox, n))

    def find(e, c=None):   # 보드 STEP 안 바디는 간섭 결과가 프록시가 아니라 sig 가 다름 → 같은 부피 + 겹친 곳 가운데를 품는 기준 바디
        if sig(e) in table:
            return table[sig(e)]
        for bb, n in vol.get(round(e.volume, 6), []):
            if c is not None and bb.contains(c):
                return (n, False)
        return (e.name + '?', False)
    lines = []
    for i in range(res.count):
        it = res.item(i)
        ib = it.interferenceBody.boundingBox
        c = adsk.core.Point3D.create((ib.minPoint.x + ib.maxPoint.x) / 2, (ib.minPoint.y + ib.maxPoint.y) / 2, (ib.minPoint.z + ib.maxPoint.z) / 2)
        n1, g1 = find(it.entityOne, c)
        n2, g2 = find(it.entityTwo, c)
        if not (g1 or g2):
            continue
        lines.append('%s <-> %s : %.3f mm3' % (n1, n2, it.interferenceBody.volume * 1000))
    txt = 'gen %d / ref %d bodies, hits involving generated: %d\n' % (len(gen), len(ref), len(lines)) + '\n'.join(sorted(lines))
    txt += '\ndropped substitute blocks (board 3D models linked): ' + (' '.join(sorted(drop)) or '-')
    open(TXT, 'w', encoding='utf-8').write(txt + '\n')
    print(txt)
