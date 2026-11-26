# M-007 전체 조립 틀 사양 (CAD 독립). 외함·방열판 형상은 mechanical/m003/params.py + geom.py 를 그대로 쓴다.
# 좌표: M-001 원점 O (코어 중심·아랫면, +Z 광축·앞, +Y 위). 단위 mm.
import math

# [M-007 J5 V4] B 창 가운데 연장은 O-94 로 M-003 원본(params.py b_ext · geom.py)에 옮김 — 조립은 원본을 그대로 쓴다.

# ---- GH 6P 하니스 (O-77b: 26AWG 자가 압착 35 mm, 하우징 뒤끝 사이) ----
HAR = {
    'len': 35.0,           # 하우징 뒤끝 사이 전선 길이 (M-002 K20)
    'od': 1.0,             # [가정] GH 핀 간격 1.25 에 나란히 들어가는 얇은 피복 26AWG (≤ 1.0). UL1007 26AWG(약 1.4–1.5)는 간격보다 굵어 GH 에 못 들어감 → 피복 외경 원문 확인 필요
    'pitch': 1.6,          # 모델 가닥 간격 (Y). GH 핀 간격은 1.25 이지만 대각선 구간(Y·Z 함께)에서 경로에 수직인 간격이 외경 1.0 이상이 되도록 퍼뜨림 — 하우징 쪽에서 1.25 로 모이는 부분은 단순화
    'n': 6,
    'R': 3.0,              # 굽힘 반경 (가닥 중심선) = 3 × 외경 — 플러그 뒤 ~ 벽 사이 3.2 안 [가정]
    'plug_back': 2.0,      # GHR 플러그 뒤끝이 리셉터클 입구 x −19.0 보다 −X 로 나온 거리 [가정]
    'x_leg': -24.2,        # 세로 다리 x (벽 −25 + 틈 0.3 + 반지름 0.5)
    'j7': (-25.05, -5.875),  # J7 (캐리어 윗면) 입구 y, 몸체 높이 가운데 z
    'j4': (-8.95, 7.475),    # J4 (전면 아랫면)
}

# ---- 플러그·카드 삽입 공간 블록 (geom.py BLK_*_PLUG 에 더해) ----
SD_CARD = (11.0, 15.0, 1.0)   # microSD 카드 폭 × 길이 × 두께 (SD 협회 규격 대표값)

# ---- 간섭에서 의도된 쌍 (이름 규칙, 앞쪽 포함 일치) ----
INTENDED = [
    ('CORE_BOT_KEEPIN', 'J2_MATED_ENVELOPE', '코어 아랫면 keep-in 이 짝 BTB 를 덮음 (M-001)'),
    ('CORE_TOP_KEEPIN', 'J1_MATED_ENVELOPE', '코어 윗면 keep-in 이 짝 BTB 를 덮음 (M-001)'),
    ('HW_STANDOFFS', 'CORE_BOT_KEEPIN', 'keep-in 덩어리가 코어 장착 구멍 자리를 덮음 (M-003 §7, M-006 스탠드오프 실제 모델 간섭 0)'),
    ('HW_STANDOFFS', 'CORE_TOP_KEEPIN', '위와 같음'),
    ('HARNESS_GH6P', 'HARNESS_CORRIDOR_MX', '하니스가 하니스 통로 안을 지남 (통로는 자리 표시)'),
    ('BLK_J3_PLUG', 'HARNESS_CORRIDOR_MX', 'z 0.02 맞닿음 수준 (M-003 §7)'),
    ('CLA216_M008', 'LENS_CIL093', '렌즈가 홀더 M12 나사에 물림'),
    ('FPC_M008', 'SENSOR_BLOCK_BXF4677', 'FPC 가 센서 블록에서 나옴'),
    ('ICR_LEAD_M008', 'ICR_PADS_M008', '리드 끝이 납땜 패드에 붙음'),
    ('DF30_M008', 'BOARD_PART', 'DF30 결합 외형 ↔ 전면 J3 모델 (같은 부품)', (-4.5, 4.5, -14.5, -9.0, 11.0, 13.0)),
    # (이름1, 이름2, 이유, 겹친 곳 가운데가 이 상자 안일 때만) — KiCad 일반 BarrelJack 모델과 XKB 대체 블록이 같은 잭을 두 번 그림
    ('BLK_J2_DC', 'BOARD_PART', 'DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품)', (8.0, 21.0, -35.0, -18.0, -22.0, -8.0)),
    ('BLK_J2_PLUG', 'BOARD_PART', 'DC 잭 일반 모델 앞면이 XKB 앞면보다 0.1 나옴 (같은 부품)', (8.0, 21.0, -35.0, -33.5, -22.0, -8.0)),
]
# 기준 STEP 중 이번 조립에서 대체된 바디 (숨기고 검사에서 뺌)
SUPERSEDED = ['CARRIER_40x54', 'FRONT_40x40', 'WINDOW_PMMA', 'LIGHT_COLLAR', 'AL_SPREADER_TAB_PX', 'THERMAL_PILLAR_A',
              'THERMAL_PILLAR_B', 'INS_PAD_A', 'INS_PAD_B1', 'INS_PAD_B2',
              'J_ICR_SITE', 'GH6P_CARRIER_TOP', 'GH6P_FRONT_BOT',   # 보드 STEP 에 실제 커넥터 모델이 있어 자리 표시를 뺌
              'CLA216_ICR', 'HOLDER_SPACER_FRAME', 'ICR_LEAD_PATH', 'DF30_SITE', 'FPC_3mm']   # M-008 로 고친 형상으로 대체
# 최소 틈 표 (쌍, 기준 mm — 0 이하이면 실패)
CLEARANCE_PAIRS = [
    ('LENS_CIL093', 'FRONT_COVER', 0.3), ('LENS_CIL093', 'LENS_WIN_PMMA', 0.3),
    ('HS_PEDESTAL', 'HOUSING', 0.2), ('SPREADER_M003', 'HOUSING', 0.3),
    ('HARNESS_GH6P', 'HOUSING', 0.1), ('HARNESS_GH6P', 'SPREADER_M003', 0.1),
    ('BLK_J3_PLUG', 'HOUSING', 0.0), ('BLK_J5_PLUG', 'HOUSING', 0.0), ('BLK_J2_PLUG', 'HOUSING', 0.0), ('BLK_J4_CARD', 'HOUSING', 0.0),
    ('FOAM_ALS_GASKET', 'FRONT_COVER', -0.01), ('LED_A1', 'FRONT_COVER', 1.0),
    ('CLA216_M008', 'LED_A1', 1.0), ('CLA216_M008', 'LED_A2', 1.0), ('DF30_M008', 'LED_B1', 1.0),
]


def fillet_path(pts, R, nseg=8):
    out = [pts[0]]
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        u = [b[i] - a[i] for i in range(3)]; v = [c[i] - b[i] for i in range(3)]
        lu = math.sqrt(sum(x * x for x in u)); lv = math.sqrt(sum(x * x for x in v))
        u = [x / lu for x in u]; v = [x / lv for x in v]
        th = math.acos(max(-1.0, min(1.0, sum(u[i] * v[i] for i in range(3)))))
        if th < 1e-6:
            out.append(b); continue
        t = R * math.tan(th / 2)
        if t > min(lu, lv) / (1.0 if b in (pts[1], pts[-2]) else 2.0) + 1e-9:
            raise ValueError('fillet does not fit at %s (t %.2f, seg %.2f/%.2f)' % (b, t, lu, lv))
        p1 = [b[i] - u[i] * t for i in range(3)]; p2 = [b[i] + v[i] * t for i in range(3)]
        w = [v[i] - u[i] for i in range(3)]; lw = math.sqrt(sum(x * x for x in w)); w = [x / lw for x in w]
        ctr = [b[i] + w[i] * (R / math.cos(th / 2)) for i in range(3)]
        r1 = [p1[i] - ctr[i] for i in range(3)]; r2 = [p2[i] - ctr[i] for i in range(3)]
        for k in range(nseg + 1):
            s = k / nseg
            sa, sb = math.sin((1 - s) * th) / math.sin(th), math.sin(s * th) / math.sin(th)
            out.append(tuple(ctr[i] + sa * r1[i] + sb * r2[i] for i in range(3)))
    out.append(pts[-1])
    return out


def path_len(p):
    return sum(math.dist(a, b) for a, b in zip(p, p[1:]))


def harness_paths(h=HAR):
    """가닥마다 최단 경로: 플러그 뒤 → −X → 대각선(Y·Z 함께) → +X. 모서리 2개 (각 90°). 남는 길이 = len − 경로 길이 는
    −X 하니스 통로(HARNESS_CORRIDOR_MX, 자리 표시) 안에서 느슨하게 휜다고 보고 모델에는 넣지 않는다."""
    x0 = -19.0 - h['plug_back']
    (y7, z7), (y4, z4) = h['j7'], h['j4']
    out = []
    for k in range(h['n']):
        dy = (k - (h['n'] - 1) / 2) * h['pitch']
        pts = [(x0, y7 + dy, z7), (h['x_leg'], y7 + dy, z7), (h['x_leg'], y4 + dy, z4), (x0, y4 + dy, z4)]
        out.append(fillet_path(pts, h['R']))
    L = path_len(out[0])
    return L, h['len'] - L, out