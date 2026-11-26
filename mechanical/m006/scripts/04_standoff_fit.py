"""M-006 04: 스탠드오프 정렬 — 코어 구멍 (13,13)(13,−13)(−13,13) 에 M1.6 육각 스탠드오프 외곽(맞모 Ø3.7)을 코어 위(1.6…9.6)·아래(−8…0)로 세우고
Seeed 코어 모델 부품과 간섭을 잰다(코어 PCB 본체는 구멍이 뚫려 있어 제외 대상 아님 — 구멍과 겹치면 0). 임시 부품은 끝나면 지운다.
또 코어 PCB 의 원통 구멍 중심을 찾아 우리 구멍 좌표와 비교한다."""
import adsk.core, adsk.fusion, math

HOLES = [(13.0, 13.0), (13.0, -13.0), (-13.0, 13.0)]

def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    assert d.attributes.itemByName('openhw', 'doc').value == 'M006_g1'
    root = d.rootComponent
    core = [o for o in root.occurrences if o.component.name == 'SEEED_CORE2002'][0]
    pcb = [o for o in core.childOccurrences if o.component.name.startswith('Recamera Core')][0]
    pb = pcb.bRepBodies.item(0)
    found = []
    for f in pb.faces:
        g = f.geometry
        if g.surfaceType == adsk.core.SurfaceTypes.CylinderSurfaceType:
            r = g.radius * 10
            if 0.7 < r < 1.5:
                c = g.origin
                found.append((round(c.x * 10, 2), round(c.y * 10, 2), round(2 * r, 2)))
    print('CORE PCB holes (x, y, dia):', sorted(set(found)))
    tb = adsk.fusion.TemporaryBRepManager.get()
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); occ.component.name = 'TEST_STANDOFFS'
    bf = occ.component.features.baseFeatures.add(); bf.startEdit()
    for (x, y) in HOLES:
        for z0, z1 in ((0.16, 0.96), (-0.8, 0.0)):
            cyl = tb.createCylinderOrCone(adsk.core.Point3D.create(x / 10, y / 10, z0), 0.185, adsk.core.Point3D.create(x / 10, y / 10, z1), 0.185)
            occ.component.bRepBodies.add(cyl, bf)
    bf.finishEdit()
    coll = adsk.core.ObjectCollection.create()
    for b in occ.bRepBodies:
        coll.add(b)
    for o in [core] + list(core.childOccurrences):
        for b in o.bRepBodies:
            coll.add(b)
    for o in root.allOccurrences:
        if o.assemblyContext and o.assemblyContext.name == core.name:
            for b in o.bRepBodies:
                coll.add(b)
    inp = d.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
    res = d.analyzeInterference(inp)
    hits = []
    for i in range(0 if res is None else res.count):
        ib = res.item(i).interferenceBody.boundingBox
        cx, cy = (ib.minPoint.x + ib.maxPoint.x) * 5, (ib.minPoint.y + ib.maxPoint.y) * 5
        near = [h for h in HOLES if math.hypot(cx - h[0], cy - h[1]) < 2.5]
        if near:
            hits.append((near[0], round(res.item(i).interferenceBody.volume * 1000, 3),
                         [round(v * 10, 2) for v in (ib.minPoint.x, ib.maxPoint.x, ib.minPoint.y, ib.maxPoint.y, ib.minPoint.z, ib.maxPoint.z)]))
    print('STANDOFF hits near holes:', hits if hits else 0)
    occ.deleteMe()
