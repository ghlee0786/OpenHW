"""O-126 시안 A 상세 설계 (Fusion, 새 로컬 문서 O126_A). 사용자 선택 D-003 #67, 사양 orchestration/queues/O-126-design-A-final.md.
실행: python -I -B mechanical/fusion_run.py mechanical/design/o126_a.py
- 외형·핀 치수 mechanical/design/o126_dims.py, 커넥터 자리 = main validation/runtime/vd001/boards/connectors.json (run_all.py 가 pcb fab 에서 읽음),
  플러그·카드 삽입 공간 = mechanical/m003/geom.py BLK_*_PLUG 와 M-007 BLK_J4_CARD (같은 식).
- 바디: 뒤 Al 쉘(핀·숨은 나사 기둥·열 받침 리브·microSD 안내 통로) · 앞 플라스틱 쉘(턱 「OpenHW」 음각·인서트 보스) · 스모크 유리 · 렌즈/조도 투명 창 ·
  유리 안쪽 인쇄 마스크(GLASS_MASK) · 안쪽 검정 가림판(PCB·FPC 가림) · 분할면 가스킷 · 인서트(M2.5 ×4, 1/4"-20) · 광 파이프 · 케이블 그로밋 ·
  USB-C·microSD 정비 덮개 · 벽 브래킷(2축: 세로축 팬 + X축 틸트).
- 산출: main validation/runtime/vd001/case/A/ — A.step · A.f3d · A_<바디>.stl (곡면 오차 0.01 mm) · result.json · 뷰포트 3장 A_view_{front,back,section}.png"""
import adsk.core, adsk.fusion, json, math, os, hashlib

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움
U = 0.1       # mm → cm
SKIP = ('KEEPIN', 'ENVELOPE', 'CORRIDOR', 'CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER', 'THERMAL_PILLAR',
        'INS_PAD', 'J_ICR', 'GH6P_CARRIER_TOP', 'GH6P_FRONT_BOT', 'CLA216_ICR', 'HOLDER_SPACER_FRAME', 'ICR_LEAD_PATH', 'DF30_SITE', 'FPC_3mm')


def run(_c):
    app = adsk.core.Application.get()
    g = {}
    exec(open(LANE + r"\mechanical\m003\params.py", encoding="utf-8").read(), g)
    exec(open(LANE + r"\mechanical\m003\geom.py", encoding="utf-8").read(), g)
    dm = {}
    exec(open(LANE + r"\mechanical\design\o126_dims.py", encoding="utf-8").read(), dm)
    C, F = dm['CASE'], dm['FINS']
    conn = json.load(open(MAIN + r"\validation\runtime\vd001\boards\connectors.json", encoding='utf-8'))
    for k, v in conn.items():
        g['P'][k] = tuple(v)
    d = g['derive'](g['P'])
    _, blocks = g['parts'](d)

    def bbox(n):   # geom 노드 바깥 상자 (box · cyl · 합집합 · 차집합은 첫 항)
        k = n[0]
        if k == 'box':
            return list(n[1:7])
        if k == 'cyl':
            a, b, r = n[1], n[2], max(n[3], n[4])
            return [min(a[0], b[0]) - r, max(a[0], b[0]) + r, min(a[1], b[1]) - r, max(a[1], b[1]) + r, min(a[2], b[2]) - r, max(a[2], b[2]) + r]
        bs = [bbox(x) for x in (n[1:] if k == 'u' else n[1:2])]
        return [f(x[i] for x in bs) for i, f in zip(range(6), [min, max] * 3)]
    PL = {k: bbox(blocks[k]) for k in ('BLK_J5_PLUG', 'BLK_J2_PLUG', 'BLK_J3_PLUG')}
    sx = sum(d['sd_x']) / 2; zc = d['z_car_bot'] - 0.95
    PL['BLK_J4_CARD'] = [sx - 5.5, sx + 5.5, conn['sd_front'][0], 99.0, zc - 0.5, zc + 0.5]

    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.attributes.add('openhw', 'doc', 'O126_A')
    root = design.rootComponent
    tb = adsk.fusion.TemporaryBRepManager.get()
    P3, V3 = adsk.core.Point3D.create, adsk.core.Vector3D.create
    im = app.importManager

    def box(x0, x1, y0, y1, z0, z1):
        return tb.createBox(adsk.core.OrientedBoundingBox3D.create(P3((x0 + x1) / 2 * U, (y0 + y1) / 2 * U, (z0 + z1) / 2 * U), V3(1, 0, 0), V3(0, 1, 0),
                                                                   (x1 - x0) * U, (y1 - y0) * U, (z1 - z0) * U))

    def cyl(a, b, r):
        return tb.createCylinderOrCone(P3(*[v * U for v in a]), r * U, P3(*[v * U for v in b]), r * U)

    def op(a, b, k):
        assert tb.booleanOperation(a, b, {'u': adsk.fusion.BooleanTypes.UnionBooleanType, 'd': adsk.fusion.BooleanTypes.DifferenceBooleanType,
                                          'i': adsk.fusion.BooleanTypes.IntersectionBooleanType}[k]), 'boolean ' + k
        return a

    def rounded(x0, x1, y0, y1, z0, z1, r, r2=None):
        """세로(Z) 모서리 r, 앞뒤 둘레 r2 모깎은 상자 (r2=0 이면 세로 모서리만 — 판·고리용). Fusion 모깎기 → BRep 복사."""
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()); comp = occ.component
        sk = comp.sketches.add(root.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(x0 * U, y0 * U, 0), P3(x1 * U, y1 * U, 0))
        body = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal((z1 - z0) * U),
                                                       adsk.fusion.FeatureOperations.NewBodyFeatureOperation).bodies.item(0)
        r = min(r, (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1)
        vert = adsk.core.ObjectCollection.create()
        for e in body.edges:
            sp, ep = e.startVertex.geometry, e.endVertex.geometry
            if abs(sp.x - ep.x) < 1e-6 and abs(sp.y - ep.y) < 1e-6:
                vert.add(e)
        fi = comp.features.filletFeatures.createInput()
        fi.edgeSetInputs.addConstantRadiusEdgeSet(vert, adsk.core.ValueInput.createByReal(r * U), True)
        comp.features.filletFeatures.add(fi)
        r2 = min(r * 0.6, (z1 - z0) / 2 - 0.1) if r2 is None else r2
        if r2 > 0.05:
            body = comp.bRepBodies.item(0)
            rest = adsk.core.ObjectCollection.create()
            for f in body.faces:
                if isinstance(f.geometry, adsk.core.Plane) and abs(abs(f.geometry.normal.z) - 1) < 1e-6:
                    for e in f.edges:
                        rest.add(e)
            fi = comp.features.filletFeatures.createInput()
            fi.edgeSetInputs.addConstantRadiusEdgeSet(rest, adsk.core.ValueInput.createByReal(r2 * U), True)
            comp.features.filletFeatures.add(fi)
        out = tb.copy(comp.bRepBodies.item(0))
        occ.deleteMe()
        m = adsk.core.Matrix3D.create(); m.translation = V3(0, 0, z0 * U)
        tb.transform(out, m)
        return out

    # ---------- 내부 적층 (간섭 확인용, o125 와 같음) ----------
    for name, path, z in (('REF_STACK', LANE + r"\mechanical\step\stack-reference.step", 0.0),
                          ('REF_CARRIER', MAIN + r"\validation\runtime\vd001\boards\carrier.step", d['z_car_bot']),
                          ('REF_FRONT', MAIN + r"\validation\runtime\vd001\boards\front.step", d['z_fr_bot'])):
        im.importToTarget(im.createSTEPImportOptions(path), root)
        occ = root.occurrences.item(root.occurrences.count - 1); occ.component.name = name
        if z:
            m = adsk.core.Matrix3D.create(); m.translation = V3(0, 0, z * U); occ.transform2 = m
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()
    for o in root.allOccurrences:
        if any(s in o.component.name for s in SKIP):
            o.isLightBulbOn = False

    def ref_bb(name):
        for o in root.allOccurrences:
            if o.component.name == name and o.bRepBodies.count:
                bb = o.bRepBodies.item(0).boundingBox
                return [bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10, bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10]
        raise AssertionError('no ref ' + name)

    X0, X1, Y0, Y1, Z0, ZS, Z1 = (C[k] for k in ('X0', 'X1', 'Y0', 'Y1', 'Z0', 'ZS', 'Z1'))
    w, wb, R = C['wall'], C['back'], C['R']
    zg = Z1 - C['glass_t']            # 유리 안쪽 면 41.7
    zm = zg - C['mask_t']             # 인쇄 마스크 안쪽 면 41.6
    xi0, xi1, yi0, yi1 = X0 + w, X1 - w, Y0 + w, Y1 - w
    rec = {}

    # ---------- 쉘 ----------
    outer = rounded(X0, X1, Y0, Y1, Z0, Z1, R, 3.0)
    inner = rounded(xi0, xi1, yi0, yi1, Z0 + wb, Z1 + 5, 3.0, 1.8)
    shell = op(tb.copy(outer), inner, 'd')
    op(shell, box(X0 - 5, X1 + 5, C['chin_top'], Y1 + 5, zm, Z1 + 1), 'd')            # 턱 위는 유리 자리 (벽 끝 → 인쇄 마스크 → 유리)
    op(shell, op(tb.copy(outer), box(X0 - 5, X1 + 5, Y0 - 5, C['chin_top'], zm, Z1), 'i'), 'u')   # 앞 턱 (「OpenHW」 음각 자리)
    rear = op(tb.copy(shell), box(X0 - 5, X1 + 5, Y0 - 5, Y1 + 5, Z0 - 5, ZS), 'i')
    front = op(tb.copy(shell), box(X0 - 5, X1 + 5, Y0 - 5, Y1 + 5, ZS, Z1 + 1), 'i')
    # 분할선 홈 0.6 × 0.6 (바깥 둘레, 분할면 가운데)
    sg = C['split_groove']
    ring = op(rounded(X0 - 1, X1 + 1, Y0 - 1, Y1 + 1, ZS - sg / 2, ZS + sg / 2, R + 1, 0.0),
              rounded(X0 + sg, X1 - sg, Y0 + sg, Y1 - sg, ZS - sg, ZS + sg, R - sg, 0.0), 'd')
    op(rear, tb.copy(ring), 'd'); op(front, ring, 'd')
    # 가스킷 홈 (Al 분할면, 폭 0.8 깊이 0.8, 벽 가운데) + 가스킷 (EPDM, 홈을 채운 모양)
    gk = op(rounded(X0 + 0.8, X1 - 0.8, Y0 + 0.8, Y1 - 0.8, ZS - 0.8, ZS, R - 0.8, 0.0),
            rounded(X0 + 1.6, X1 - 1.6, Y0 + 1.6, Y1 - 1.6, ZS - 1.0, ZS + 0.2, R - 1.6, 0.0), 'd')
    op(rear, tb.copy(gk), 'd')
    gasket = gk
    # 뒷면 세로 방열 핀 (o126_thermal.md 선택안) — 위·아래 모서리는 숨은 나사 자리
    fy0, fy1 = Y0 + 10.0, Y1 - 10.5
    xs = [-(F['back_n'] - 1) / 2 * 8.0 + k * 8.0 for k in range(F['back_n'])]
    for xc in xs:
        op(rear, box(xc - F['back_t'] / 2, xc + F['back_t'] / 2, fy0, fy1, Z0 - F['back_H'], Z0 + 0.5), 'u')
    # 열 받침 리브: 확산판 플랜지 → 갭 패드 GAP_PAD_PX(x 20…20.75) → Al 옆벽 (analysis2 HS_PEDESTAL 대신)
    gp = [20.75, xi1 + 0.5, -19.5, 19.5, -4.5, 3.9]
    op(rear, box(*gp), 'u')
    # 숨은 나사: Al 기둥(뒤에서 M2.5 관통·묻힌 머리) ↔ 앞 쉘 보스 + 열 압입 인서트
    SCR = [(sxx * 22.7, yy) for sxx in (-1, 1) for yy in (31.0, -35.8)]
    inserts = []
    for k, (px, py) in enumerate(SCR):
        op(rear, cyl((px, py, Z0 + 1), (px, py, ZS), 2.2), 'u')
        op(rear, cyl((px, py, Z0 - 1), (px, py, ZS + 1), 1.35), 'd')                   # M2.5 관통 Ø2.7
        op(rear, cyl((px, py, Z0 - 1), (px, py, Z0 + 2.6), 2.3), 'd')                  # 머리 묻힘 Ø4.6 깊이 2.6
        op(front, cyl((px, py, ZS), (px, py, ZS + 8.0), 3.0), 'u')                      # 보스 Ø6 (옆벽에 붙음)
        op(front, cyl((px, py, ZS - 1), (px, py, ZS + 5.7), 1.75), 'd')                 # 인서트 구멍 Ø3.5
        inserts.append(('INSERT_M25_%d' % (k + 1), op(cyl((px, py, ZS), (px, py, ZS + 5.7), 1.75), cyl((px, py, ZS - 1), (px, py, ZS + 7), 1.1), 'd')))
    op(rear, tb.copy(gk), 'd')                                                         # 리브·기둥 뒤에 가스킷 홈 다시 (리브가 홈을 메우지 않게)
    # ---------- 커넥터 개구 (보드 실제 위치 · 삽입 공간 블록 + 틈) ----------
    j5, j2, j3, j4 = PL['BLK_J5_PLUG'], PL['BLK_J2_PLUG'], PL['BLK_J3_PLUG'], PL['BLK_J4_CARD']
    cav = [min(j5[0], j2[0]) - 3.0, max(j5[1], j2[1]) + 0.1, Y0 - 1, min(conn['rj_y'][0], conn['dc_y'][0]) - 0.2,
           min(j5[4], j2[4]) - 2.0, max(j5[5], j2[5]) + 0.9]                              # 아랫면 케이블 오목 자리 (RJ45 · DC 한 곳)
    usb = [X0 - 1, xi0 + 0.01, j3[2] - 0.3, j3[3] + 0.3, j3[4] - 0.3, j3[5] + 0.3]          # 옆(−X) USB-C
    sd = [j4[0] - 0.5, j4[1] + 0.5, yi1 - 0.01, Y1 + 1, j4[4] - 0.25, j4[5] + 0.25]         # 위 microSD 슬롯
    for c in (cav, usb, sd):
        op(rear, box(*c), 'd')
    rec['openings_mm'] = {'cable_recess': [round(v, 2) for v in cav], 'usbc': [round(v, 2) for v in usb], 'microsd': [round(v, 2) for v in sd]}
    # microSD 안내 통로 (소켓 앞 y 19.6 → 윗벽): Al 쉘과 한 몸, 카드 단면 + 0.25
    gd = op(box(sd[0] - 1.2, sd[1] + 1.2, conn['sd_front'][0] + 0.5, yi1 + 0.5, sd[4] - 1.2, sd[5] + 1.2), box(sd[0], sd[1], 0, Y1 + 2, sd[4], sd[5]), 'd')
    op(rear, gd, 'u')
    # 정비 덮개 (실리콘 마개: 개구를 채우는 몸통 + 바깥 테 0.8) — 꽂을 때 뺌 (asm_spec CASE_A INTENDED)
    cov_usb = op(box(usb[0] + 1, xi0, usb[2] + 0.05, usb[3] - 0.05, usb[4] + 0.05, usb[5] - 0.05),
                 box(X0 - 0.8, X0, usb[2] - 1.5, usb[3] + 1.5, usb[4] - 1.5, usb[5] + 1.5), 'u')
    cov_sd = op(box(sd[0] + 0.05, sd[1] - 0.05, yi1, Y1 + 0.01, sd[4] + 0.05, sd[5] - 0.05),
                box(sd[0] - 1.5, sd[1] + 1.5, Y1, Y1 + 0.8, sd[4] - 1.5, sd[5] + 1.5), 'u')
    # 케이블 그로밋: 오목 자리 입구(아랫벽 두께)의 고무 테 — 플러그 단면 + 0.5 구멍
    grom = box(cav[0] + 0.05, cav[1] - 0.05, Y0 + 0.3, yi0, cav[4] + 0.05, cav[5] - 0.05)
    for p in (j5, j2):
        op(grom, box(p[0] - 0.5, p[1] + 0.5, Y0 - 2, yi0 + 2, p[4] - 0.5, p[5] + 0.5), 'd')
    # ---------- 앞면: 유리 · 투명 창 · 인쇄 마스크 · 안쪽 가림판 ----------
    glass = op(tb.copy(outer), box(X0 - 5, X1 + 5, C['chin_top'], Y1 + 5, zg, Z1 + 1), 'i')
    lr = g['P']['lens_win_d'] / 2
    lw = cyl((0, 0, zg), (0, 0, Z1), lr)
    als = [(a + b) / 2 for a, b in d['als_in']]
    aw = cyl((als[0], als[1], zg), (als[0], als[1], Z1), 2.0)
    op(glass, cyl((0, 0, zg - 1), (0, 0, Z1 + 1), lr), 'd'); op(glass, cyl((als[0], als[1], zg - 1), (als[0], als[1], Z1 + 1), 2.0), 'd')
    op(lw, tb.copy(outer), 'i'); op(aw, tb.copy(outer), 'i')
    # 유리 안쪽 검정 인쇄 마스크 (렌더: 이름에 MASK → 무광 검정). 남기는 구멍 = 렌즈 창 · 조도 창 · IR LED 창 2띠 —
    #   LED 창: LED A(y 16) 위쪽 빛·LED B(y −16.5) 아래쪽 빛이 유리 안쪽 면 z 41.6 을 지나는 띠(시야 VFOV, 32°/30.2° 여유) — 그 뒤는 안쪽 가림판(검정)만 보임
    mask = op(tb.copy(outer), box(X0 - 5, X1 + 5, C['chin_top'], Y1 + 5, zm, zg), 'i')
    rise = zm - d['z_led_top']
    ya1 = min(yi1 - 1.0, g['P']['led_a_y'] + rise * math.tan(math.radians(g['P']['led_out_deg'])))
    yb0 = max(C['chin_top'] + 1.0, g['P']['led_b_y'] - rise * math.tan(math.radians(30.2)))
    led_win = {'A': [xi0 + 1.0, xi1 - 1.0, g['P']['led_a_y'] - 1.5, ya1], 'B': [xi0 + 1.0, xi1 - 1.0, yb0, g['P']['led_b_y'] + 1.5]}
    for k2, (wx0, wx1, wy0, wy1) in led_win.items():
        op(mask, rounded(wx0, wx1, wy0, wy1, zm - 1, zg + 1, 2.0, 0.0), 'd')
    op(mask, cyl((0, 0, zm - 1), (0, 0, zg + 1), lr), 'd')
    op(mask, cyl((als[0], als[1], zm - 1), (als[0], als[1], zg + 1), 2.0), 'd')
    rec['glass_mask_led_windows_mm'] = {k2: [round(v, 2) for v in vv] for k2, vv in led_win.items()}
    # 안쪽 가림판 (흑색 PC 0.8): 전면 보드 위 부품·FPC·나사 머리를 가림. 구멍 = 렌즈 홀더 · LED 4 (화각 원뿔) · 조도 센서
    zp0, zp1 = 14.6, 15.4
    plate = rounded(xi0, xi1, yi0, yi1, zp0, zp1, 3.0, 0.0)
    m8 = {}
    exec(open(LANE + r"\mechanical\m008\cla216_spec.py", encoding="utf-8").read(), m8)
    hb = bbox(m8['parts']()['CLA216_M008'])   # M-008 홀더 (조립에서 CLA216_M008)
    op(plate, box(hb[0] - 0.5, hb[1] + 0.5, hb[2] - 0.5, hb[3] + 0.5, zp0 - 1, zp1 + 1), 'd')
    holes = {}
    tH = math.tan(math.radians(44.0)); tV = math.tan(math.radians(g['P']['led_out_deg']))
    for n in ('LED_A1', 'LED_A2', 'LED_B1_DNP', 'LED_B2_DNP'):
        lb = ref_bb(n)
        cx, cy = (lb[0] + lb[1]) / 2, (lb[2] + lb[3]) / 2
        hx, hy = (lb[1] - lb[0]) / 2 + (zp1 - d['z_led_top']) * tH + 0.3, (lb[3] - lb[2]) / 2 + (zp1 - d['z_led_top']) * tV + 0.3
        op(plate, box(cx - hx, cx + hx, cy - hy, cy + hy, zp0 - 1, zp1 + 1), 'd')
        holes[n] = [round(cx - hx, 2), round(cx + hx, 2), round(cy - hy, 2), round(cy + hy, 2)]
    (ax0, ax1), (ay0, ay1) = d['als_in']
    op(plate, box(ax0 - 0.5, ax1 + 0.5, ay0 - 0.5, ay1 + 0.5, zp0 - 1, zp1 + 1), 'd')
    rec['inner_plate_holes_mm'] = holes
    # ---------- 광 파이프 (상태 LED D6 뒷면 → 아래로 2.4 → +Y 윗벽까지, Ø2 PC) ----------
    sl = g['P']['stat_led'][0]
    zl = d['z_car_bot'] - 1.5; zt = zl - 2.4       # LED 몸체 아래끝 z −10.79 (보드 모델) + 0.3
    pipe = op(op(cyl((sl[0], sl[1], zl), (sl[0], sl[1], zt), 1.0), cyl((sl[0], sl[1], zt), (sl[0], Y1 + 0.2, zt), 1.0), 'u'),
              tb.createSphere(P3(sl[0] * U, sl[1] * U, zt * U), 0.1), 'u')
    op(rear, cyl((sl[0], yi1 - 1, zt), (sl[0], Y1 + 1, zt), 1.05), 'd')
    # ---------- 바닥 1/4"-20 인서트 (앞 쉘, 바닥 가운데) ----------
    tz = (ZS + Z1) / 2
    op(front, op(cyl((0, Y0 + 0.5, tz), (0, Y0 + 10.0, tz), 6.0), cyl((0, Y0 - 1, tz), (0, Y0 + 8.0, tz), 4.0), 'd'), 'u')
    op(front, cyl((0, Y0 - 1, tz), (0, Y0 + 8.0, tz), 4.0), 'd')
    ins14 = op(cyl((0, Y0, tz), (0, Y0 + 8.0, tz), 4.0), cyl((0, Y0 - 1, tz), (0, Y0 + 9, tz), 3.175), 'd')
    # ---------- 벽 브래킷 (2축: 세로 기둥 팬 · X축 틸트, 벽 z −80) ----------
    zw = Z0 - F['back_H'] - 44.0
    yb = Y0 - 0.2
    b_tilt = op(op(box(-10, 10, yb - 3.0, yb, tz - 10, tz + 10), box(-4, 4, yb - 6.5, yb - 2.99, tz - 4, tz + 4), 'u'),
                cyl((-6, yb - 6.5, tz), (6, yb - 6.5, tz), 4.0), 'u')
    op(b_tilt, cyl((-7, yb - 6.5, tz), (7, yb - 6.5, tz), 1.5), 'd')
    op(b_tilt, cyl((0, yb + 1, tz), (0, yb - 3.5, tz), 3.4), 'd')                          # 1/4"-20 나사 자리
    b_pin = cyl((-7, yb - 6.5, tz), (7, yb - 6.5, tz), 1.5)
    b_pan = op(cyl((0, yb - 11.0, tz), (0, yb - 14.0, tz), 6.0), cyl((0, yb - 14.0, tz), (0, yb - 36.0, tz), 4.0), 'u')
    op(b_tilt, cyl((0, yb - 10.0, tz), (0, yb - 11.0, tz), 4.0), 'u')                       # 틸트 머리 ↔ 팬 받침 (맞닿음)
    b_wall = op(box(-5, 5, yb - 44.0, yb - 36.0, zw + 4, tz + 5), box(-20, 20, yb - 60.0, yb - 20.0, zw, zw + 4), 'u')
    for yy in (yb - 52.0, yb - 28.0):
        op(b_wall, cyl((0, yy, zw - 1), (0, yy, zw + 5), 2.5), 'd')
    b_screw = cyl((0, yb - 3.0, tz), (0, Y0 + 7.5, tz), 3.175)
    # ---------- 바디로 넣기 ----------
    comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    comp.name = 'CASE_A'
    named = [('SHELL_ALU', rear), ('SHELL_PLASTIC', front), ('FRONT_GLASS_IR', glass), ('LENS_WIN_CLEAR', lw), ('ALS_WIN_CLEAR', aw),
             ('GLASS_MASK', mask), ('INNER_MASK_PLATE', plate), ('GASKET_SPLIT', gasket), ('LIGHT_PIPE', pipe)] + inserts + \
            [('INSERT_1_4_20', ins14), ('CABLE_GROMMET', grom), ('COVER_USBC', cov_usb), ('COVER_MICROSD', cov_sd),
             ('WALL_BRACKET_ARM', b_wall), ('WALL_BRACKET_PAN', b_pan), ('WALL_BRACKET_TILT', b_tilt), ('WALL_BRACKET_PIN', b_pin), ('WALL_BRACKET_SCREW', b_screw)]
    bf = comp.features.baseFeatures.add(); bf.startEdit()
    for nm, b in named:
        comp.bRepBodies.add(b, bf)
    bf.finishEdit()
    for i, (nm, _) in enumerate(named):
        comp.bRepBodies.item(i).name = nm
    # 개구 바깥 모서리 모깎기 0.6 (USB-C · microSD · 케이블 오목 자리) — 실패하면 기록
    rear_b = comp.bRepBodies.itemByName('SHELL_ALU')
    fil = {}
    for key, c, axis, val in (('usbc', usb, 'x', X0), ('microsd', sd, 'y', Y1), ('cable_recess', cav, 'y', Y0)):
        es = adsk.core.ObjectCollection.create()
        for e in rear_b.edges:
            bb = e.boundingBox
            lo, hi = getattr(bb.minPoint, axis) * 10, getattr(bb.maxPoint, axis) * 10
            if abs(lo - val) < 0.05 and abs(hi - val) < 0.05:
                mx, my, mz = [(getattr(bb.minPoint, a) + getattr(bb.maxPoint, a)) * 5 for a in 'xyz']
                if c[0] - 0.1 <= mx <= c[1] + 0.1 and c[2] - 0.1 <= my <= c[3] + 0.1 and c[4] - 0.1 <= mz <= c[5] + 0.1:
                    es.add(e)
        ok = False
        if es.count:
            fi = comp.features.filletFeatures.createInput()
            fi.edgeSetInputs.addConstantRadiusEdgeSet(es, adsk.core.ValueInput.createByReal(0.06), True)
            try:
                comp.features.filletFeatures.add(fi); ok = True
            except RuntimeError as ex:
                ok = 'fail: ' + str(ex)[:80]
        fil[key] = [es.count, ok]
    rec['fillet_0p6'] = fil
    # 앞 턱 「OpenHW」 음각 0.3
    sh = comp.bRepBodies.itemByName('SHELL_PLASTIC')
    ytxt = (Y0 + 3.0 + C['chin_top']) / 2
    cand = [f for f in sh.faces if isinstance(f.geometry, adsk.core.Plane) and abs(abs(f.geometry.normal.z) - 1) < 1e-6
            and f.boundingBox.minPoint.x * 10 <= -2.0 and f.boundingBox.maxPoint.x * 10 >= 2.0
            and f.boundingBox.minPoint.y * 10 <= ytxt - 1.0 and f.boundingBox.maxPoint.y * 10 >= ytxt + 1.0]
    face = max(cand, key=lambda f: f.boundingBox.maxPoint.z, default=None)
    rec['engraved_OpenHW_z'] = None
    if face is not None:
        sk = comp.sketches.add(face)
        zf = face.boundingBox.maxPoint.z
        pt = sk.modelToSketchSpace(P3(0, ytxt * U, zf))
        ti = sk.sketchTexts.createInput2('OpenHW', 0.28)
        ti.setAsMultiLine(P3(pt.x - 1.2, pt.y - 0.2, 0), P3(pt.x + 1.2, pt.y + 0.2, 0),
                          adsk.core.HorizontalAlignments.CenterHorizontalAlignment, adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
        ei = comp.features.extrudeFeatures.createInput(sk.sketchTexts.add(ti), adsk.fusion.FeatureOperations.CutFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-0.03))
        ei.participantBodies = [sh]
        comp.features.extrudeFeatures.add(ei); rec['engraved_OpenHW_z'] = round(zf * 10, 2)
    # ---------- 간섭: 케이스 바디 ↔ 내부 적층 (빠른 확인 — 판정은 M-007 조립 03_judge) ----------
    coll = adsk.core.ObjectCollection.create()
    for b in comp.bRepBodies:
        coll.add(b)
    nref = 0
    for o in root.allOccurrences:
        t = o
        while t.assemblyContext:
            t = t.assemblyContext
        if t.component.name.startswith('REF_') and o.isLightBulbOn and t.isLightBulbOn:
            for b in o.bRepBodies:
                if b.isSolid and b.isLightBulbOn:
                    coll.add(b); nref += 1
    inp = design.createInterferenceInput(coll); inp.areCoincidentFacesIncluded = False
    r = design.analyzeInterference(inp)
    hits, self_hits = [], []
    for i in range(0 if r is None else r.count):
        it = r.item(i)
        a, b2 = it.entityOne, it.entityTwo
        da, db = a.parentComponent == comp, b2.parentComponent == comp
        ib = it.interferenceBody.boundingBox
        at = [round(v * 10, 2) for v in (ib.minPoint.x, ib.maxPoint.x, ib.minPoint.y, ib.maxPoint.y, ib.minPoint.z, ib.maxPoint.z)]
        h = {'a': a.name, 'b': b2.name, 'mm3': round(it.interferenceBody.volume * 1000, 4), 'at': at}
        if da != db:
            hits.append(h)
        elif da and db:
            self_hits.append(h)
    rec.update({'interference_ref': hits, 'interference_ref_mm3': round(sum(h['mm3'] for h in hits), 4), 'interference_self': self_hits, 'ref_bodies': nref})
    # ---------- 내보내기 ----------
    out = MAIN + r"\validation\runtime\vd001\case\A"
    os.makedirs(out, exist_ok=True)
    em = design.exportManager
    files = []
    stp = os.path.join(out, 'A.step')
    em.execute(em.createSTEPExportOptions(stp, comp)); files.append(stp)
    for b in comp.bRepBodies:
        so = em.createSTLExportOptions(b, os.path.join(out, 'A_%s.stl' % b.name))
        so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementCustom
        so.surfaceDeviation = 0.001; so.normalDeviation = math.radians(5); so.maximumEdgeLength = 0.2; so.aspectRatio = 10
        so.isBinaryFormat = True
        em.execute(so); files.append(so.filename)
    f3d = os.path.join(out, 'A.f3d')
    em.execute(em.createFusionArchiveExportOptions(f3d, comp)); files.append(f3d)
    bbs = [b.boundingBox for b in comp.bRepBodies if not b.name.startswith('WALL_BRACKET')]
    rec['outer_mm_xyz'] = [round((max(getattr(b.maxPoint, k) for b in bbs) - min(getattr(b.minPoint, k) for b in bbs)) * 10, 2) for k in 'xyz']
    rec['bodies'] = [b.name for b in comp.bRepBodies]
    rec['volume_cm3'] = {b.name: round(b.volume, 3) for b in comp.bRepBodies}
    # 뷰포트 3장 (앞 ¾ · 뒤 ¾ · 단면 x=0 — 단면은 임시 반쪽 바디)
    vp = app.activeViewport
    cam = vp.camera; cam.isSmoothTransition = False; cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType

    def shot(fn, eye, tgt=(0, -2, 0.8)):
        c = vp.camera; c.isSmoothTransition = False
        c.eye, c.target, c.upVector = P3(*eye), P3(*tgt), V3(0, 1, 0)
        vp.camera = c; vp.fit(); adsk.doEvents(); vp.refresh()
        vp.saveAsImageFile(os.path.join(out, fn), 1920, 1200); files.append(os.path.join(out, fn))
    tops = [o for o in root.occurrences if o.component.name.startswith('REF_')]
    for o in tops:
        o.isLightBulbOn = False
    shot('A_view_front.png', (18, 12, 30))
    shot('A_view_back.png', (-20, 10, -26))
    sec = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    sec.name = 'SECTION_X0'
    bf2 = sec.features.baseFeatures.add(); bf2.startEdit()
    for b in comp.bRepBodies:
        if b.name.startswith('WALL_BRACKET'):
            continue
        t = tb.copy(b)
        if tb.booleanOperation(t, box(0, 200, -200, 200, -200, 200), adsk.fusion.BooleanTypes.DifferenceBooleanType) and t.volume > 0:
            sec.bRepBodies.add(t, bf2)
    bf2.finishEdit()
    root.occurrences.item(root.occurrences.count - 2).isLightBulbOn = False   # CASE_A 숨김 → 반쪽 + 적층
    for o in tops:
        o.isLightBulbOn = True
    for o in root.allOccurrences:
        if any(s in o.component.name for s in SKIP):
            o.isLightBulbOn = False
    shot('A_view_section.png', (40, 6, 12), (0, -2, 0.8))
    for o in root.occurrences:
        if o.component.name == 'CASE_A':
            o.isLightBulbOn = True
        if o.component.name == 'SECTION_X0':
            o.isLightBulbOn = False
    rec['files'] = {os.path.basename(p): {'bytes': os.path.getsize(p), 'sha256': hashlib.sha256(open(p, 'rb').read()).hexdigest()} for p in files}
    json.dump(rec, open(os.path.join(out, 'result.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('CASE_A', json.dumps({k: rec[k] for k in ('outer_mm_xyz', 'interference_ref_mm3', 'engraved_OpenHW_z', 'fillet_0p6', 'ref_bodies')}))
    print('HITS', json.dumps(hits[:12]), 'SELF', json.dumps(self_hits[:12]))
