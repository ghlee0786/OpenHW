"""M-006 02: 짝 BTB 결합 형상 시험 — 코어 J1 플러그 모델(4.0H PLUG)을 복사해(부품 TEST_PLUG) 코어 J2 소켓(4.0H SOCKET)에 끼운다.
플러그 어깨(몸체 윗면)를 소켓 결합면에 맞춘 높이 = 결합 높이 4.0 + 4.0. 그 위치와 들어 올린 위치에서 Fusion analyzeInterference 로 겹침을 잰다.
회전 +90° / −90° 둘 다 (극성 키 확인). 캐리어 쪽 플러그도 혀가 위(코어 쪽)라 뒤집지 않는다. 끝나면 TEST_PLUG 를 지운다."""
import adsk.core, adsk.fusion, math

def run(_c):
    d = adsk.fusion.Design.cast(adsk.core.Application.get().activeProduct)
    assert d.attributes.itemByName('openhw', 'doc').value == 'M006_g1'
    root = d.rootComponent
    tb = adsk.fusion.TemporaryBRepManager.get()
    bodies = {}
    for o in root.allOccurrences:
        if o.component.name in ('SHANGQI_0_5BTB_60P_4_0H_SOCKET', 'SHANGQI_0_5BTB_60P_4_0H_PLUG'):
            bodies[o.component.name] = o.bRepBodies.item(0)
    plug, sock = bodies['SHANGQI_0_5BTB_60P_4_0H_PLUG'], bodies['SHANGQI_0_5BTB_60P_4_0H_SOCKET']
    pbb, sbb = plug.boundingBox, sock.boundingBox
    pcx, pcy = (pbb.minPoint.x + pbb.maxPoint.x) / 2, (pbb.minPoint.y + pbb.maxPoint.y) / 2
    scx, scy = (sbb.minPoint.x + sbb.maxPoint.x) / 2, (sbb.minPoint.y + sbb.maxPoint.y) / 2
    SHOULDER, MATE = 0.5647, -0.405
    b = tb.copy(plug)
    m = adsk.core.Matrix3D.create(); m.translation = adsk.core.Vector3D.create(-pcx, -pcy, -SHOULDER); tb.transform(b, m)
    occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
    occ.component.name = 'TEST_PLUG'
    bf = occ.component.features.baseFeatures.add(); bf.startEdit(); occ.component.bRepBodies.add(b, bf); bf.finishEdit()
    tbody = occ.bRepBodies.item(0)

    def place(ang, lift):
        mm = adsk.core.Matrix3D.create()
        r2 = adsk.core.Matrix3D.create(); r2.setToRotation(math.radians(ang), adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))
        mm.transformBy(r2)
        t = adsk.core.Matrix3D.create(); t.translation = adsk.core.Vector3D.create(scx, scy, MATE - lift / 10.0)   # 혀는 위(+Z, 코어 쪽)
        mm.transformBy(t)
        occ.transform2 = mm

    def ov():
        coll = adsk.core.ObjectCollection.create(); coll.add(occ.bRepBodies.item(0)); coll.add(sock)
        inp = d.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
        res = d.analyzeInterference(inp)
        return 0.0 if res is None else sum(res.item(i).interferenceBody.volume for i in range(res.count)) * 1000

    for ang in (90, -90):
        place(ang, 0.0)
        v0 = ov()
        lift = None
        if v0 > 1e-4:
            for k in range(1, 41):
                place(ang, k * 0.05)
                if ov() < 1e-4:
                    lift = k * 0.05; break
        else:
            lift = 0.0
        print('ANGLE %+d: overlap at mated 8.0 = %.4f mm3 ; first zero-overlap lift = %s mm -> mated height %s' % (
            ang, v0, lift, None if lift is None else round(8.0 + lift, 2)))
    occ.deleteMe()
    if d.snapshots.hasPendingSnapshot:
        d.snapshots.revertPendingSnapshot()
    print('PLUG z', round(pbb.minPoint.z * 10, 3), round(pbb.maxPoint.z * 10, 3), 'SOCKET z', round(sbb.minPoint.z * 10, 3), round(sbb.maxPoint.z * 10, 3))
