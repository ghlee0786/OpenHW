"""M-006 03: 코어 모델(Seeed 2002w STEP) ↔ 우리 보드 STEP(pcb 69ed962) 간섭, 결합 높이 8.0. 코어끼리·보드끼리 쌍은 뺀다.
결과: 쌍마다 겹친 부피. 코어 안테나 스프링(2002w 무선 모델 전용)은 따로 표시."""
import adsk.core, adsk.fusion

def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    assert d.attributes.itemByName('openhw', 'doc').value == 'M006_g1'
    root = d.rootComponent
    groups = {}
    coll = adsk.core.ObjectCollection.create()
    sig = {}
    for top in root.occurrences:
        if top.component.name == 'TEST_PLUG':
            continue
        occs = [top] + list(top.component.allOccurrences)
        for o in [top] + [x for x in root.allOccurrences if x.assemblyContext and (x.assemblyContext == top or x.fullPathName.startswith(top.name + '+'))]:
            for b in o.bRepBodies:
                if not b.isSolid:
                    continue
                coll.add(b)
                bb = b.boundingBox
                sig[(round(b.volume, 6), round(bb.minPoint.x, 4), round(bb.minPoint.y, 4), round(bb.minPoint.z, 4))] = (top.component.name, o.component.name)
    inp = d.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
    res = d.analyzeInterference(inp)

    tops = {o.name: o.component.name for o in root.occurrences}

    def who(b):
        ctx = b.assemblyContext
        if ctx is not None:
            path = ctx.fullPathName
            return (tops.get(path.split('+')[0], '?'), ctx.component.name)
        bb = b.boundingBox
        return sig.get((round(b.volume, 6), round(bb.minPoint.x, 4), round(bb.minPoint.y, 4), round(bb.minPoint.z, 4)), ('?', b.name))
    n = 0
    unk = 0
    print('RAW hits', 0 if res is None else res.count)
    for i in range(0 if res is None else res.count):
        it = res.item(i)
        a, b = who(it.entityOne), who(it.entityTwo)
        if a[0] == '?' or b[0] == '?':
            unk += 1
            ib = it.interferenceBody.boundingBox
            print('UNMATCHED', a[1], b[1], round(it.interferenceBody.volume * 1000, 3), 'at', [round(v * 10, 2) for v in (ib.minPoint.x, ib.maxPoint.x, ib.minPoint.y, ib.maxPoint.y, ib.minPoint.z, ib.maxPoint.z)])
            continue
        if a[0] == b[0]:
            continue
        n += 1
        print('HIT %s/%s <-> %s/%s : %.3f mm3' % (a[0], a[1], b[0], b[1], it.interferenceBody.volume * 1000))
    print('bodies', coll.count, 'signatures', len(sig), 'cross-group hits', n, 'unmatched', unk)
