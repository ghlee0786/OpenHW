"""O-125 1단계 — 케이스 디자인 시안 A·B·C (Fusion, 덩어리 수준). 새 로컬 문서에 내부 적층을 가져오고 시안 외형을 만든 뒤 간섭을 숫자로 낸다.
실행: python -I -B mechanical/fusion_run.py mechanical/design/o125_design.py --set DESIGN=A   (B · C)
- 내부 적층(간섭 확인용): main 체크아웃 validation/runtime/vd001/boards/{carrier,front}.step (pcb 995b872, 3D 모델 포함, 코어 중심 원점)
  + 기준 적층 mechanical/step/stack-reference.step 중 코어·센서·렌즈 (keep-in·자리 표시·옛 외함은 뺌 — mechanical/m007/asm_spec.SUPERSEDED 등)
- 좌표: 코어 중심·아랫면 원점, +Z 광축(앞), +Y 위 (M-001). 단위 mm.
- 시안 공통: 나사는 바닥·뒷면에만, 상태 LED 광 파이프(Ø2), 케이블 출구 1곳(RJ45·DC 를 한 오목 자리에), 앞면 아래 「OpenHW」 음각 0.3.
- 산출: main validation/runtime/vd001/design/<시안>/<시안>.step · <시안>_<바디>.stl (곡면 오차 0.01 mm) · result.json (간섭 부피·바디·치수)
덩어리 시안이라 방열(#26)·나사 보스·가스킷은 3단계(고른 시안 상세 설계)에서 다시 본다."""
import adsk.core, adsk.fusion, json, math, os, hashlib

LANE = None   # 소스 체크아웃 — mechanical/fusion_run.py 가 채움
MAIN = None   # main 체크아웃 — mechanical/fusion_run.py 가 채움
DESIGN = r"A"
U = 0.1       # mm → cm
# 내부 적층 바깥 (mm) — 보드 STEP·기준 적층 실측 (o125_design.md §1): x, y, z 범위 + 커넥터 앞면
IN = {'x': (-21.0, 21.0), 'y': (-34.5, 21.0), 'z': (-24.0, 41.0)}
CONN = {'usb_x': -20.455, 'usb_y': (-4.47, 4.47), 'usb_z': (-13.0, -9.6),      # USB-C 앞면 −X (캐리어 아랫면, 플러그 오버몰드 12.35×6.5)
        'rj': (-10.475, 5.565), 'rj_z': (-23.1, -9.6), 'dc': (10.68, 19.68), 'dc_z': (-20.6, -9.6), 'y_bot': -33.7,   # RJ45·DC 앞면 −Y
        'sd': (-6.955, 6.895), 'sd_z': (-11.4, -9.6), 'sd_y': 19.6}             # microSD 슬롯 +Y
SKIP = ('KEEPIN', 'ENVELOPE', 'CORRIDOR', 'CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER', 'THERMAL_PILLAR',
        'INS_PAD', 'J_ICR', 'GH6P_CARRIER_TOP', 'GH6P_FRONT_BOT', 'CLA216_ICR', 'HOLDER_SPACER_FRAME', 'ICR_LEAD_PATH', 'DF30_SITE', 'FPC_3mm')


def run(_c):
    app = adsk.core.Application.get()
    app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    design.designType = adsk.fusion.DesignTypes.ParametricDesignType
    design.attributes.add('openhw', 'doc', 'O125_' + DESIGN)
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

    def rounded(x0, x1, y0, y1, z0, z1, r, axis='z'):
        """모서리 12개를 r 로 모깎은 상자 (Fusion 모깎기 기능 → BRep 복사)"""
        comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        sk = comp.sketches.add(root.xYConstructionPlane)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(x0 * U, y0 * U, 0), P3(x1 * U, y1 * U, 0))
        ext = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal((z1 - z0) * U),
                                                      adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        body = ext.bodies.item(0)
        # 1) 세로(Z) 모서리 4개 = r  2) 앞뒤 둘레 = r2 (두께의 절반보다 작게, r 보다 작게 — 같은 반지름 구석은 계산 실패)
        r = min(r, (x1 - x0) / 2 - 0.1, (y1 - y0) / 2 - 0.1)
        vert = adsk.core.ObjectCollection.create()
        for e in body.edges:
            sp, ep = e.startVertex.geometry, e.endVertex.geometry
            if abs(sp.x - ep.x) < 1e-6 and abs(sp.y - ep.y) < 1e-6:
                vert.add(e)
        fi = comp.features.filletFeatures.createInput()
        fi.edgeSetInputs.addConstantRadiusEdgeSet(vert, adsk.core.ValueInput.createByReal(r * U), True)
        comp.features.filletFeatures.add(fi)
        body = comp.bRepBodies.item(0)
        r2 = min(r * 0.6, (z1 - z0) / 2 - 0.1)
        if r2 > 0.05:
            rest = adsk.core.ObjectCollection.create()
            for f in body.faces:
                if isinstance(f.geometry, adsk.core.Plane) and abs(abs(f.geometry.normal.z) - 1) < 1e-6:
                    for e in f.edges:
                        rest.add(e)
            fi = comp.features.filletFeatures.createInput()
            fi.edgeSetInputs.addConstantRadiusEdgeSet(rest, adsk.core.ValueInput.createByReal(r2 * U), True)
            comp.features.filletFeatures.add(fi)
        out = tb.copy(comp.bRepBodies.item(0))
        root.occurrences.item(root.occurrences.count - 1).deleteMe()
        m = adsk.core.Matrix3D.create(); m.translation = V3(0, 0, z0 * U)
        tb.transform(out, m)
        return out

    def rounded_cyl(z0, z1, rad, r, cy=0.0):
        """Z 축 원통, 앞뒤 모서리 r 모깎기"""
        comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
        sk = comp.sketches.add(root.xYConstructionPlane)
        sk.sketchCurves.sketchCircles.addByCenterRadius(P3(0, cy * U, 0), rad * U)
        ext = comp.features.extrudeFeatures.addSimple(sk.profiles.item(0), adsk.core.ValueInput.createByReal((z1 - z0) * U),
                                                      adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        body = ext.bodies.item(0)
        edges = adsk.core.ObjectCollection.create()
        for e in body.edges:
            edges.add(e)
        fi = comp.features.filletFeatures.createInput()
        fi.edgeSetInputs.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(r * U), True)
        comp.features.filletFeatures.add(fi)
        out = tb.copy(comp.bRepBodies.item(0))
        root.occurrences.item(root.occurrences.count - 1).deleteMe()
        m = adsk.core.Matrix3D.create(); m.translation = V3(0, 0, z0 * U)
        tb.transform(out, m)
        return out

    # ---------- 내부 적층 가져오기 ----------
    g = {}
    exec(open(LANE + r"\mechanical\m003\params.py", encoding="utf-8").read(), g)
    d = g['derive'](g['P'])
    refs = []
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
    x0, x1 = IN['x']; y0, y1 = IN['y']; z0, z1 = IN['z']
    parts = {}
    if DESIGN == 'A':
        # 둥근 박스 R5. 뒤 1/3 알루미늄 쉘(두께 4, 바깥 홈 = 통합 핀) · 앞 2/3 무광 흑색 플라스틱(두께 2) · 분할선 0.6 · 앞면 IR 투과 검정 유리 한 장
        w = 2.0; wa = 4.0
        X0, X1, Y0, Y1, Z0, Z1 = x0 - w - 1, x1 + w + 1, y0 - w - 1, y1 + w + 1, z0 - wa, z1 + 2.5
        outer = rounded(X0, X1, Y0, Y1, Z0, Z1, 5.0)
        inner = rounded(X0 + w, X1 - w, Y0 + w, Y1 - w, Z0 + wa, Z1 + 5, 3.0)
        shell = op(tb.copy(outer), inner, 'd')
        zs = Z0 + (Z1 - Z0) / 3.0                       # 재질 경계 (뒤 1/3)
        rear = op(tb.copy(shell), box(X0 - 5, X1 + 5, Y0 - 5, Y1 + 5, Z0 - 5, zs - 0.3), 'i')
        front = op(tb.copy(shell), box(X0 - 5, X1 + 5, Y0 - 5, Y1 + 5, zs + 0.3, Z1 - 2.0), 'i')
        for k in range(int((zs - Z0 - 4) // 3)):        # 통합 핀: 위·양옆 바깥 홈 폭 1.4 깊이 2.2, 간격 3
            zc = Z0 + 3.0 + k * 3.0
            for cut in (box(X0 - 1, X1 + 1, Y1 - 2.2, Y1 + 1, zc, zc + 1.4), box(X0 - 1, X0 + 2.2, Y0 + 6, Y1 - 6, zc, zc + 1.4),
                        box(X1 - 2.2, X1 + 1, Y0 + 6, Y1 - 6, zc, zc + 1.4)):
                op(rear, cut, 'd')
        glass = op(rounded(X0, X1, Y0, Y1, Z1 - 2.0 - 3, Z1, 5.0), box(X0 - 5, X1 + 5, Y0 + 7.0, Y1 + 5, Z1 - 2.0, Z1 + 1), 'i')   # 앞 유리 (아래 7 mm 는 플라스틱 턱)
        chin = op(rounded(X0, X1, Y0, Y1, Z1 - 2.0 - 3, Z1, 5.0), box(X0 - 5, X1 + 5, Y0 - 5, Y0 + 7.0, Z1 - 2.0, Z1 + 1), 'i')
        op(front, chin, 'u')
        tripod = (0.0, Y0, (zs + Z1) / 2)
        ring = None
        body_main, body_al = front, rear
    elif DESIGN == 'B':
        # 퍽/큐브: 거의 정육면체 R6, 윗판 알루미늄 핀(세로 핀 7장), 앞면 원형 렌즈 링 강조
        w = 2.2
        X0, X1, Y0, Y1, Z0, Z1 = x0 - w - 1, x1 + w + 1, y0 - w - 1, y1 + w + 1 + 6, z0 - w, z1 + 2.5
        outer = rounded(X0, X1, Y0, Y1, Z0, Z1, 6.0)
        inner = rounded(X0 + w, X1 - w, Y0 + w, Y1 - w - 6, Z0 + w, Z1 - 2.0, 3.5)          # 앞벽 2 (유리 자리만 뚫음)
        body_main = op(tb.copy(outer), inner, 'd')
        op(body_main, box(X0 - 5, X1 + 5, Y0 + 9.0, Y1 + 5, Z1 - 2.0, Z1 + 5), 'd')        # 앞면 유리 자리 (아래 9 mm 는 플라스틱 턱 — 음각 자리)
        body_al = box(X0 + 4, X1 - 4, Y1 - 6.0, Y1 - 4.5, Z0 + 4, Z1 - 6)                   # 윗판 받침 (알루미늄)
        n = 7; pitch = (X1 - X0 - 12) / (n - 1)
        for k in range(n):
            xc = X0 + 6 + k * pitch
            op(body_al, box(xc - 0.8, xc + 0.8, Y1 - 4.6, Y1 + 3.0, Z0 + 6, Z1 - 8), 'u')
        op(body_main, box(X0 + 3.5, X1 - 3.5, Y1 - 6.5, Y1 + 5, Z0 + 3.5, Z1 - 5.5), 'd')   # 윗판 자리
        glass = op(rounded(X0, X1, Y0, Y1, Z1 - 2.0 - 3, Z1, 6.0), box(X0 - 5, X1 + 5, Y0 + 9.0, Y1 + 5, Z1 - 2.0, Z1 + 1), 'i')
        ring = op(cyl((0, 0, Z1 - 0.01), (0, 0, Z1 + 2.5), 11.0), cyl((0, 0, Z1 - 1), (0, 0, Z1 + 3), 8.0), 'd')   # 렌즈 링 (유리 앞, 알루미늄)
        # 렌즈 링은 따로 (렌더에서 다른 재질) — LENS_RING 바디
        tripod = (0.0, Y0, (Z0 + Z1) / 2)
    else:
        ring = None
        # 원통 불릿: 축 = 광축, 지름 = 내부 단면을 감싸는 원 + 벽, 앞 차양(위 반원통), 뒤 케이블 글랜드
        cy = (y0 + y1) / 2
        rad = math.hypot(max(abs(x0), abs(x1)), (y1 - y0) / 2) + 1.0 + 2.2
        Z0, Z1 = z0 - 2.5, z1 + 2.5
        outer = rounded_cyl(Z0, Z1, rad, 4.0, cy)
        inner = rounded_cyl(Z0 + 2.5, Z1 - 2.0, rad - 2.2, 2.0, cy)                          # 앞벽 2 (유리 자리만 뚫음)
        body_main = op(tb.copy(outer), inner, 'd')
        op(body_main, cyl((0, cy, Z1 - 2.0), (0, cy, Z1 + 5), rad - 8.0), 'd')                 # 앞 베젤 링 폭 8 (모깎기 4 안쪽 평평한 4 mm = 음각 자리) 안쪽에 유리
        glass = cyl((0, cy, Z1 - 2.0), (0, cy, Z1), rad - 8.01)
        hood = op(op(cyl((0, cy, Z1 - 12), (0, cy, Z1 + 22), rad + 1.6), cyl((0, cy, Z1 - 13), (0, cy, Z1 + 23), rad - 0.5), 'd'),   # 쉘 벽에 0.5 겹쳐 한 몸
                  box(-rad - 5, rad + 5, cy + 2.0, cy + rad + 5, Z1 - 12, Z1 + 22), 'i')        # 위쪽 차양
        op(body_main, hood, 'u')
        body_al = cyl((0, cy, Z0 - 10), (0, cy, Z0 + 0.01), 7.0)                                # 뒤 케이블 글랜드 (M16 급)
        op(body_al, cyl((0, cy, Z0 - 11), (0, cy, Z0 + 1), 3.5), 'd')
        X0, X1, Y0, Y1 = -rad, rad, cy - rad, cy + rad
        tripod = (0.0, cy - rad, (Z0 + Z1) / 2)
    # ---------- 공통: 커넥터 구멍 · 케이블 출구 · 삼각대 · 광 파이프 · 나사 ----------
    cuts = []
    if DESIGN != 'C':
        # 케이블 출구 1곳: 바닥 오목 자리 안에 RJ45 · DC (−Y 면) — 오목 깊이 6
        cuts.append(box(CONN['rj'][0] - 1.0, CONN['dc'][1] + 1.0, Y0 - 1, CONN['y_bot'] - 0.2, CONN['rj_z'][0] - 1.0, CONN['dc_z'][1] - 0.6))
    else:
        cuts.append(cyl((0, cy, Z0 - 12), (0, cy, Z0 + 3), 3.5))   # 글랜드 구멍
    cuts.append(box(X0 - 1, CONN['usb_x'] - 0.2, CONN['usb_y'][0] - 2.0, CONN['usb_y'][1] + 2.0, CONN['usb_z'][0] - 1.6, CONN['usb_z'][1] + 0.4))   # USB-C (옆, 서비스용 고무 마개)
    cuts.append(box(CONN['sd'][0] - 1.0, CONN['sd'][1] + 1.0, CONN['sd_y'] + 0.2, Y1 + 1, CONN['sd_z'][0] - 0.8, CONN['sd_z'][1] + 0.6))       # microSD (위, 서비스용 마개)
    lp = (x1 - 4.0, Y1, z1 - 6.0)
    cuts.append(cyl((lp[0], lp[1] - 4, lp[2]), (lp[0], lp[1] + 1, lp[2]), 1.0))                                              # 상태 LED 광 파이프 구멍
    for cut in cuts:
        for b in (body_main, body_al):
            op(b, cut, 'd')
    pipe = cyl((lp[0], lp[1] - 3.5, lp[2]), (lp[0], lp[1] + 0.2, lp[2]), 0.95)                                               # 광 파이프 (투명)
    tx, ty, tz = tripod
    boss = op(cyl((tx, ty + 0.01, tz), (tx, ty + 9.0, tz), 5.5), cyl((tx, ty - 1, tz), (tx, ty + 8.0, tz), 3.2), 'd')         # 1/4"-20 인서트 보스 (Ø6.4 구멍)
    op(body_main, boss, 'u')
    op(body_main, cyl((tx, ty - 1, tz), (tx, ty + 8.0, tz), 3.2), 'd')
    screws = []
    zback = (Z0 if DESIGN != 'C' else Z0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            pt = (sx * (X1 - 6.0) if DESIGN != 'C' else sx * (rad - 6) * 0.7, (cy if DESIGN == 'C' else (Y0 + Y1) / 2) + sy * ((Y1 - Y0) / 2 - 6.0) * (0.7 if DESIGN == 'C' else 1), zback)
            screws.append(pt)
            hole = cyl((pt[0], pt[1], zback - 1), (pt[0], pt[1], zback + 6), 1.25)                                          # 뒷면 숨은 나사 (M2.5, 접시 자리)
            op(body_al if DESIGN == 'A' else body_main, hole, 'd')
    bracket = None
    if DESIGN == 'A':                                   # 벽 브래킷: 벽판 + 팔 (삼각대 나사로 체결)
        bracket = box(tx - 20, tx + 20, ty - 40, ty - 37, tz - 25, tz + 25)
        op(bracket, box(tx - 6, tx + 6, ty - 37.01, ty - 0.2, tz - 6, tz + 6), 'u')
        op(bracket, cyl((tx, ty - 45, tz), (tx, ty + 1, tz), 3.2), 'd')
    # ---------- 바디로 넣기 ----------
    comp = root.occurrences.addNewComponent(adsk.core.Matrix3D.create()).component
    comp.name = 'DESIGN_' + DESIGN
    bf = comp.features.baseFeatures.add(); bf.startEdit()
    named = [('SHELL_PLASTIC', body_main), ('SHELL_ALU', body_al), ('FRONT_GLASS_IR', glass), ('LIGHT_PIPE', pipe)] + ([('WALL_BRACKET', bracket)] if bracket else []) + ([('LENS_RING', ring)] if DESIGN == 'B' else [])
    for nm, b in named:
        comp.bRepBodies.add(b, bf)
    bf.finishEdit()
    for i, (nm, _) in enumerate(named):
        comp.bRepBodies.item(i).name = nm
    # 앞면 아래 「OpenHW」 음각 0.3 (플라스틱 턱 / 앞 테두리)
    sh = comp.bRepBodies.itemByName('SHELL_PLASTIC')
    ytxt = {'A': Y0 + 5.0, 'B': Y0 + 6.0, 'C': Y0 + 6.0}[DESIGN]   # 앞 모서리 모깎기 안쪽 평평한 띠 가운데
    cand = []
    for f in sh.faces:   # 음각 자리 (x=0, ytxt) 를 품는 +Z 평면 중 가장 앞쪽 (안쪽 뒷벽·차양 끝 말고 앞 테두리)
        if isinstance(f.geometry, adsk.core.Plane) and abs(abs(f.geometry.normal.z) - 1) < 1e-6:   # 평면 법선은 바깥 방향 보장 없음 → 절댓값
            bb = f.boundingBox
            if bb.minPoint.x * 10 <= -2.0 and bb.maxPoint.x * 10 >= 2.0 and bb.minPoint.y * 10 <= ytxt - 1.0 and bb.maxPoint.y * 10 >= ytxt + 1.0:
                cand.append(f)
    face = max(cand, key=lambda f: f.boundingBox.maxPoint.z, default=None)
    engraved = False
    if face is not None:
        sk = comp.sketches.add(face)
        zf = face.boundingBox.maxPoint.z
        ptxt = sk.modelToSketchSpace(P3(0, ytxt * U, zf))
        ti = sk.sketchTexts.createInput2('OpenHW', 0.28)
        ti.setAsMultiLine(P3(ptxt.x - 1.2, ptxt.y - 0.2, 0), P3(ptxt.x + 1.2, ptxt.y + 0.2, 0),
                          adsk.core.HorizontalAlignments.CenterHorizontalAlignment, adsk.core.VerticalAlignments.MiddleVerticalAlignment, 0)
        txt = sk.sketchTexts.add(ti)
        ei = comp.features.extrudeFeatures.createInput(txt, adsk.fusion.FeatureOperations.CutFeatureOperation)
        ei.setDistanceExtent(False, adsk.core.ValueInput.createByReal(-0.03))
        ei.participantBodies = [sh]
        comp.features.extrudeFeatures.add(ei); engraved = round(zf * 10, 2)   # 음각한 면의 z (mm) — 바깥 앞면이어야 함
    # ---------- 간섭: 시안 바디 ↔ 내부 적층 ----------
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
    names = {b.entityToken: b.name for b in comp.bRepBodies}
    hits = []
    for i in range(0 if r is None else r.count):
        it = r.item(i)
        a, b2 = it.entityOne, it.entityTwo
        da = a.parentComponent == comp if hasattr(a, 'parentComponent') else False
        db = b2.parentComponent == comp if hasattr(b2, 'parentComponent') else False
        if da != db:   # 시안 바디 ↔ 내부 (시안끼리·내부끼리는 판정 밖)
            hits.append({'design_body': (a if da else b2).name, 'ref': (b2 if da else a).name, 'mm3': round(it.interferenceBody.volume * 1000, 3)})
    # ---------- 내보내기 ----------
    out = MAIN + r"\validation\runtime\vd001\design" + '\\' + DESIGN
    os.makedirs(out, exist_ok=True)
    em = design.exportManager
    files = {}
    stp = out + '\\%s.step' % DESIGN
    em.execute(em.createSTEPExportOptions(stp, comp))
    files[os.path.basename(stp)] = stp
    for b in comp.bRepBodies:
        so = em.createSTLExportOptions(b, out + '\\%s_%s.stl' % (DESIGN, b.name))
        so.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementCustom
        so.surfaceDeviation = 0.001          # cm = 0.01 mm
        so.normalDeviation = math.radians(5)
        so.maximumEdgeLength = 0.2
        so.aspectRatio = 10
        so.isBinaryFormat = True
        em.execute(so)
        files[os.path.basename(so.filename)] = so.filename
    bb = [comp.bRepBodies.itemByName(n).boundingBox for n in ('SHELL_PLASTIC', 'SHELL_ALU', 'FRONT_GLASS_IR')]
    ext = [round((max(getattr(b.maxPoint, k) for b in bb) - min(getattr(b.minPoint, k) for b in bb)) * 10, 2) for k in 'xyz']
    res = {'design': DESIGN, 'outer_mm_xyz': ext, 'bodies': [b.name for b in comp.bRepBodies], 'ref_bodies': nref,
           'interference': hits, 'interference_mm3': round(sum(h['mm3'] for h in hits), 3), 'engraved_OpenHW': engraved,
           'tripod_mm': [round(v, 2) for v in tripod], 'screws_back_mm': [[round(v, 2) for v in s] for s in screws],
           'files': {k: {'bytes': os.path.getsize(v), 'sha256': hashlib.sha256(open(v, 'rb').read()).hexdigest()} for k, v in files.items()}}
    json.dump(res, open(out + '\\result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    vp = app.activeViewport
    for o in root.allOccurrences:
        t = o
        while t.assemblyContext:
            t = t.assemblyContext
        if t.component.name.startswith('REF_'):
            t.isLightBulbOn = False
    cam = vp.camera; cam.isSmoothTransition = False; cam.cameraType = adsk.core.CameraTypes.PerspectiveCameraType
    cam.eye, cam.target, cam.upVector = P3(16, 11, 26), P3(0, -0.5, 0.8), V3(0, 1, 0)
    vp.camera = cam; vp.fit(); adsk.doEvents(); vp.refresh()
    vp.saveAsImageFile(out + '\\%s_iso.png' % DESIGN, 1600, 1000)
    print('DESIGN', json.dumps({k: res[k] for k in ('design', 'outer_mm_xyz', 'bodies', 'ref_bodies', 'interference_mm3', 'engraved_OpenHW')}), 'hits', hits[:6])
