# M-008 CLA216-ICR 평면 방향 수정 + DF30 위치 (CAD 독립). 좌표 = 보조 원점 O (코어 중심 = 광축, +Y 위, 전면 보드 윗면 z 11.2).
# 근거: Commonlands CLA216-ICR 도면 (R-018·R-019 사본, 세션 임시 폴더 cla216_drawing.png sha256 1D652324…, R-019 표기 7827f26d…)
#   · 아랫면도: 구멍 간격 20.0 · 귀 (24.4) · 몸체 15.9 · 공동 14.1 이 한 축(구멍 축), 20.3(코일 하우징 포함)은 직각 축
#   · 픽셀 판독 (20.0 = 182.7 px → 9.135 px/mm): 공동 중심 → 코일 쪽 끝 11.7, 반대쪽 끝 8.65 (R-019 11.65 / 8.65)
#   · 윗면도(렌즈 쪽, IR-cut 필터 보임): 코일은 오른쪽, 리드는 코일 블록 아래 끝에서 구멍 축 방향(아래)으로 나감
#   · 보드에 회전만으로 맞춤 (구멍 축 = X, 구멍 (±10, 0) 유지): 윗면도 (h, v) → 보드 (x, y) = (−v, h) → 코일 +Y, 리드 +X
#     (−Y 코일은 DF30·FPC 경로와 겹쳐 버림)
CLA = {
    'hole_dx': 10.0,          # 구멍 (±10, 0) — 전면 MH1 그대로
    'body_x': 7.95,           # 몸체 반폭 (15.9 / 2) — 구멍 축 방향
    'y_coil': 11.65,          # 코일 쪽 끝 (+Y)
    'y_far': -8.65,           # 반대쪽 끝 (−Y)
    'ear_x': 12.2,            # 귀 끝 (24.4 / 2)
    'ear_w': 5.0,             # 귀 폭 (윗면도 (5.0))
    'ear_t': 3.4,             # 귀 두께 (R-007 판독, stack-reference ear_t)
    'h': 7.6,                 # 높이 (MBFL 기준면 → 윗면)
    'cav': 14.1,              # 공동 □
    'lead_y': 9.3,            # [판독] 리드 나오는 y (코일 블록 가운데쯤)
    'lead_z': 0.8,            # [가정] 리드 중심 높이 (홀더 바닥 위)
    'lead_d': 1.2,            # [가정] 리드 2가닥 묶음 지름
}
SPACER = {'t': 1.5, 'fpc_slot_x': 4.2, 'fpc_slot_top': 1.4}   # 스페이서 1.5 (M-001d), FPC 지나는 −Y 벽 홈 (x ±3.8, 바닥에서 1.4)
# O-84 / C-016: CLA216 리드는 2핀 2.54 mm 스루홀 납땜 패드 (리드를 잘라 납땜). 리드가 +X 로 나오므로 +X 쪽에 둔다.
ICR_PADS = [(16.0, 8.0), (16.0, 10.54)]   # 패드 중심 (보조 원점 기준), 지름 1.7 / 구멍 1.0 권장
# DF30 (R-019 #5): S401 뒷면 실크 원 (105.99, 115)·(123.99, 115) — 간격 18.0 = BXF4677 홀더 귀 간격, 중심 (114.99, 115) = 코어 중심 = 홀더 축.
#   S401 J2 DF30 중심 (114.98, 103.45) → 축에서 Y 11.55, X −0.01. 우리 모듈은 180° (O-40) → J3 중심 (0, −11.55), 회전 180° 그대로.
DF30 = {'x': 0.0, 'y': -11.55, 'rot': 180.0, 'w': 4.8, 'l': 7.6, 'h': 1.15}
FRONT_TOP = 11.2


def parts():
    """CSG (mechanical/m003/geom.py 와 같은 형식)"""
    c = CLA; z0 = FRONT_TOP + SPACER['t']; zt = z0 + c['h']
    def box(x0, x1, y0, y1, a, b):
        return ('box', x0, x1, y0, y1, a, b)
    body = ('u', box(-c['body_x'], c['body_x'], c['y_far'], c['y_coil'], z0, zt),
            box(-c['ear_x'], c['ear_x'], -c['ear_w'] / 2, c['ear_w'] / 2, z0, z0 + c['ear_t']))
    holes = [('cyl', (sx * c['hole_dx'], 0, z0 - 1), (sx * c['hole_dx'], 0, zt + 1), 0.85, 0.85) for sx in (-1, 1)]
    bore = box(-c['cav'] / 2, c['cav'] / 2, -c['cav'] / 2, c['cav'] / 2, z0 - 1, z0 + 1.2)   # 공동 깊이 1.2 (M-001d cav_d)
    thread = ('cyl', (0, 0, z0 - 1), (0, 0, zt + 1), 6.0, 6.0)   # M12 나사 구멍 관통 (렌즈가 들어감)
    P = {'CLA216_M008': ('d', body, bore, thread, *holes)}
    sp = ('u', box(-c['body_x'], c['body_x'], c['y_far'], c['y_coil'], FRONT_TOP, z0),
          box(-c['ear_x'], c['ear_x'], -c['ear_w'] / 2, c['ear_w'] / 2, FRONT_TOP, z0))
    P['SPACER_M008'] = ('d', sp, box(-c['cav'] / 2, c['cav'] / 2, -c['cav'] / 2, c['cav'] / 2, FRONT_TOP - 1, z0 + 1),
                        box(-SPACER['fpc_slot_x'], SPACER['fpc_slot_x'], c['y_far'] - 1, -c['cav'] / 2 + 0.01, FRONT_TOP - 1, FRONT_TOP + SPACER['fpc_slot_top']),
                        *holes)
    lz = z0 + c['lead_z']; r = c['lead_d'] / 2
    (px, py) = ICR_PADS[0]
    P['ICR_LEAD_M008'] = ('u', ('cyl', (c['body_x'], c['lead_y'], lz), (px - 2.0, c['lead_y'], lz), r, r),
                          ('cyl', (px - 2.0, c['lead_y'], lz), (px, (ICR_PADS[0][1] + ICR_PADS[1][1]) / 2, FRONT_TOP + 0.6), r, r))
    P['ICR_PADS_M008'] = ('u', *[('cyl', (x, y, FRONT_TOP), (x, y, FRONT_TOP + 0.5), 0.85, 0.85) for x, y in ICR_PADS])
    d = DF30
    P['DF30_M008'] = box(d['x'] - d['l'] / 2, d['x'] + d['l'] / 2, d['y'] - d['w'] / 2, d['y'] + d['w'] / 2, FRONT_TOP, FRONT_TOP + d['h'])
    # FPC: 센서 블록 −Y 끝 (−6.6) → DF30 중심, 받침 위 높이 (M-001d: 12.35…12.47)
    P['FPC_M008'] = box(-3.0, 3.0, d['y'], -6.6, 12.35, 12.47)
    return P
