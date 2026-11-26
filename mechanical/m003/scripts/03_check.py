"""M-003 03: 간섭 검사. 외함 생성물(부품·대체 블록) ↔ 기준(KiCad 보드 STEP·M-002b 적층) 과 생성물끼리.
맞닿는 면은 빼고(areCoincidentFacesIncluded=False) 부피가 있는 겹침만 센다. 결과를 m003/interference.txt 로 쓴다."""
import adsk.core, adsk.fusion

BASE = r"C:\workspace_python\OpenHW\.harness-worktrees\t-20261127-040816-30c6\mechanical\m003"
# 기준 중 이번 외함으로 대체된 것 (같은 자리 중복 또는 M-003에서 바뀐 것)
SUPERSEDED = {'CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER_TAB_PX',
              'THERMAL_PILLAR_A', 'THERMAL_PILLAR_B', 'INS_PAD_A', 'INS_PAD_B1', 'INS_PAD_B2'}
GEN_COMPS = None


def run(_c):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    assert design.attributes.itemByName('openhw', 'doc').value == 'M003_enclosure', 'wrong document'
    root = design.rootComponent
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

    def find(e):
        return table.get(sig(e), (e.name + '?', False))
    lines = []
    for i in range(res.count):
        it = res.item(i)
        n1, g1 = find(it.entityOne)
        n2, g2 = find(it.entityTwo)
        if not (g1 or g2):
            continue
        lines.append('%s <-> %s : %.3f mm3' % (n1, n2, it.interferenceBody.volume * 1000))
    txt = 'gen %d / ref %d bodies, hits involving generated: %d\n' % (len(gen), len(ref), len(lines)) + '\n'.join(sorted(lines))
    open(BASE + r"\interference.txt", 'w', encoding='utf-8').write(txt + '\n')
    print(txt)
