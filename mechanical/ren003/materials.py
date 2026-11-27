# REN-003 재질 표 (Fusion · Blender 공유) — CAD·렌더러 독립. 다른 스크립트는 exec(open(...).read(), g) 로 읽는다.
# 값: rgb = 선형 RGB 0..1 (Blender Principled 'Base Color' 그대로, Fusion 은 srgb255() 로 바꿔 씀) · metal · rough · trans · ior · coat
#     bump = (주기 mm, 세기) FDM 층 결 (Blender 만) · fusion = 복사할 Fusion 기본 외관 ID (fusion360 skill api-recipes 의 확인된 ID)
# 출처: REN-002 scene.py 값(외함·방열판·창·폼·패드 등은 그대로 옮김) + 보드·부품 재질 새로 (lead 지시 REN-003).

MATS = {
    # ---- 외함·기구 (REN-002 값 그대로) ----
    'petg':   dict(label='외함 흑색 PETG 무광 (설계 재질 PETG, lead 예시 ABS/PC 무광)', rgb=(0.013, 0.013, 0.014), rough=0.62, spec=0.4, bump=(0.2, 0.12), fusion='Prism-113'),
    'anod':   dict(label='방열판 알루미늄 흑색 아노다이즈 반광', rgb=(0.045, 0.046, 0.05), metal=1.0, rough=0.27, fusion='Prism-031'),
    'al':     dict(label='알루미늄 생지 (받침·확산판)', rgb=(0.78, 0.79, 0.8), metal=1.0, rough=0.28, fusion='Prism-028'),
    'pmma':   dict(label='PMMA 투명 창', rgb=(0.97, 0.98, 1.0), rough=0.02, trans=1.0, ior=1.49, fusion='Prism-169'),
    'foam':   dict(label='흑색 폼 (렌즈 링·ALS 가스킷)', rgb=(0.01, 0.01, 0.01), rough=0.95, spec=0.1, fusion='Prism-131'),
    'pad':    dict(label='열 패드 T-flex P340 보라', rgb=(0.32, 0.09, 0.42), rough=0.65, fusion='Prism-116'),
    'brass':  dict(label='황동 스탠드오프', rgb=(0.78, 0.6, 0.25), metal=1.0, rough=0.3, fusion='Prism-028'),
    'steel':  dict(label='강 나사·너트', rgb=(0.62, 0.63, 0.65), metal=1.0, rough=0.35, fusion='Prism-256'),
    'lens':   dict(label='렌즈 경통 흑색 금속', rgb=(0.03, 0.03, 0.03), metal=0.9, rough=0.35, fusion='Prism-626'),
    'glass':  dict(label='렌즈 유리', rgb=(0.9, 0.95, 1.0), rough=0.0, trans=1.0, ior=1.6, fusion='Prism-152'),
    'plastic': dict(label='흑색 플라스틱 (기타)', rgb=(0.025, 0.025, 0.028), rough=0.5, fusion='Prism-113'),
    'sensor': dict(label='센서 블록', rgb=(0.08, 0.08, 0.09), metal=0.6, rough=0.4, fusion='Prism-626'),
    'fpc':    dict(label='FPC 폴리이미드', rgb=(0.75, 0.42, 0.08), rough=0.4, fusion='Prism-119'),
    'core':   dict(label='코어 모듈 (덩어리)', rgb=(0.02, 0.14, 0.06), rough=0.45, fusion='Prism-112'),
    'wire_r': dict(label='전선 적', rgb=(0.6, 0.03, 0.02), rough=0.45, fusion='Prism-112'),
    'wire_k': dict(label='전선 흑', rgb=(0.02, 0.02, 0.02), rough=0.45, fusion='Prism-112'),
    'wire_y': dict(label='전선 황', rgb=(0.75, 0.6, 0.03), rough=0.45, fusion='Prism-112'),
    'cable_grey': dict(label='케이블 PVC 회색', rgb=(0.42, 0.44, 0.47), rough=0.55, fusion='Prism-116'),
    'cable_k': dict(label='케이블 PVC 흑', rgb=(0.02, 0.02, 0.022), rough=0.5, fusion='Prism-113'),
    'plug_clear': dict(label='RJ45 플러그 PC 투명', rgb=(0.9, 0.92, 0.95), rough=0.1, trans=0.85, ior=1.58, fusion='Prism-172'),
    'mount':  dict(label='받침대 알루미늄 흑', rgb=(0.12, 0.12, 0.13), metal=1.0, rough=0.4, fusion='Prism-031'),
    # ---- 보드 (REN-003 새로) ----
    'mask':   dict(label='PCB 녹색 솔더마스크 (LPI 반광)', rgb=(0.02, 0.18, 0.05), rough=0.25, coat=0.3, fusion='Prism-112'),
    'enig':   dict(label='ENIG 금 도금 패드', rgb=(0.95, 0.72, 0.35), metal=1.0, rough=0.25, fusion='Prism-028'),
    'silk':   dict(label='실크 흰색', rgb=(0.92, 0.92, 0.92), rough=0.6, fusion='Prism-127'),
    'fr4':    dict(label='FR-4 판 단면', rgb=(0.42, 0.40, 0.22), rough=0.7, fusion='Prism-3001'),
    'copper': dict(label='동박 (마스크 밑 배선·비아 — 마스크 너머로 비침)', rgb=(0.80, 0.42, 0.22), metal=1.0, rough=0.3, fusion='Prism-028'),
    # ---- 부품 ----
    'epoxy':  dict(label='IC 흑색 에폭시 몰드', rgb=(0.012, 0.012, 0.013), rough=0.55, fusion='Prism-113'),
    'tin':    dict(label='부품 리드 주석 도금', rgb=(0.72, 0.72, 0.70), metal=1.0, rough=0.3, fusion='Prism-073'),
    'gold':   dict(label='커넥터 접점 금 도금', rgb=(0.95, 0.72, 0.35), metal=1.0, rough=0.2, fusion='Prism-028'),
    'shield': dict(label='커넥터 금속 쉘 (니켈 도금)', rgb=(0.66, 0.66, 0.64), metal=1.0, rough=0.22, fusion='Prism-073'),
    'conn_white': dict(label='커넥터 하우징 백색 나일론 (JST)', rgb=(0.80, 0.77, 0.70), rough=0.5, fusion='Prism-127'),
    'conn_black': dict(label='커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD)', rgb=(0.02, 0.02, 0.022), rough=0.45, fusion='Prism-113'),
    'ceramic': dict(label='세라믹 커패시터 몸체', rgb=(0.36, 0.25, 0.13), rough=0.5, fusion='Prism-119'),
    'ferrite': dict(label='인덕터 페라이트·몰드 회색', rgb=(0.07, 0.07, 0.075), rough=0.6, fusion='Prism-116'),
    'led':    dict(label='IR LED 렌즈 몸체 (투명 실리콘)', rgb=(0.85, 0.85, 0.85), rough=0.15, trans=0.6, ior=1.41, fusion='Prism-172'),
    'led_smd': dict(label='상태 LED 녹색 확산 몰드 (0603)', rgb=(0.095, 0.42, 0.167), rough=0.2, trans=0.4, ior=1.5, fusion='Prism-172'),
    'holder': dict(label='M12 홀더 흑색 플라스틱', rgb=(0.02, 0.02, 0.022), rough=0.5, fusion='Prism-113'),
}

# 이름 규칙 1 — 외함·기구 바디 (Fusion 컴포넌트/바디 이름, Blender 객체 이름 = M007_assembly 의 이름). 앞쪽이 먼저. 부분 일치.
NAME_RULES = [('HOUSING', 'petg'), ('FRONT_COVER', 'petg'), ('HS_EXTRUSION', 'anod'), ('HS_PEDESTAL', 'al'), ('SPREADER_M003', 'al'),
              ('PMMA', 'pmma'), ('FOAM', 'foam'), ('INS_PADS', 'pad'), ('GAP_PAD', 'pad'), ('HW_STANDOFFS', 'brass'),
              ('HW_M16', 'steel'), ('HW_M25', 'steel'), ('LENS_CIL093', 'lens'), ('SENSOR', 'sensor'), ('PEDESTAL', 'al'), ('FPC', 'fpc'),
              ('CORE_MODULE', 'core'), ('CORE_ENVELOPE', 'core'), ('CLA216', 'holder'), ('SPACER_M008', 'holder')]

# 이름 규칙 1b — 보드 층 (KiCad 내보내기 메시/바디 이름 '<보드>_<층>', GLB 에서 확인 · Fusion STEP 은 미확인). 색 분류보다 먼저.
LAYER_RULES = [('_soldermask', 'mask'), ('_silkscreen', 'silk'), ('_pad', 'enig'), ('_copper', 'copper'), ('_via', 'copper'), ('_PCB', 'fr4')]

# 이름 규칙 2 — 보드 부품 (KiCad 모델 이름 = Fusion 컴포넌트 이름, 참조 번호 = Blender GLB 노드 이름). 그 부품의 「몸체」 색 분류에 씀.
#   (모델 이름 정규식, 참조 번호 정규식, 몸체 재질). 리드·쉘 등 금속 색 바디는 아래 색 분류(tin·gold)가 먼저.
PART_RULES = [
    (r'RJ45', r'^J5$', 'shield'), (r'USB_C', r'^J3$', 'shield'), (r'microSD|DM3AT', r'^J4$', 'shield'),
    (r'BarrelJack|DC_Jack', r'^J2$', 'conn_black'),
    (r'JST_', r'^J6$|^J7$', 'conn_white'), (r'BTB_', r'^J1$', 'conn_black'), (r'Hirose_DF30', r'^J3$', 'conn_black'),
    (r'M12_Holder', r'^MH1$', 'holder'), (r'Vishay_VSMA', r'^D_IR', 'led'),
    (r'PinHeader', r'^J2$', 'conn_black'), (r'^LED_\d{4}', r'^LED\d|^D\d', 'led_smd'), (r'CP_Elec', r'^C\d', 'plastic'),
    (r'^C_\d{4}', r'^C\d', 'ceramic'), (r'^L_|SRP|SRN', r'^L\d', 'ferrite'),
    (r'SOIC|SOT|TSSOP|SSOP|USON|WSON|MSOP|QFN|DFN|Oscillator|LTR-329|ALS-PT19|^D_S|^R_|Fuse', r'^(U|Q|D|R|F|X|Y)\d', 'epoxy'),
]
# 모델 + 색 덮어쓰기 (같은 모델 안에서 색으로 부분을 가름 — 색 분류·PART_RULES 보다 먼저). (모델 정규식, 파일 색, 재질)
COLOR_OVERRIDES = [(r'JST_', (0.777, 0.769, 0.625), 'conn_white'),          # JST GH/SH 하우징 (자연색 나일론) — 리드는 0.645 주석
                   (r'microSD|DM3AT', (0.221, 0.221, 0.221), 'shield'),     # DM3AT 금속 쉘 (0.019 은 절연체 → conn_black)
                   (r'microSD|DM3AT', (0.019, 0.018, 0.018), 'conn_black'),
                   (r'SRN|SRP', (0.468, 0.154, 0.028), 'copper')]           # 인덕터 권선 동선
# 참조 번호 규칙은 보드마다 J 번호가 다르므로 보드 이름을 붙여 쓸 때만 맞음 — 모델 이름이 먼저, 참조 번호는 GLB 에 모델 이름이 없을 때의 차선.
BOARD_REF_ONLY = {'carrier': {'J5': 'shield', 'J3': 'shield', 'J4': 'shield', 'J2': 'conn_black', 'J1': 'conn_black'},
                  'front': {'J1': 'conn_black', 'J3': 'conn_black', 'MH1': 'holder', 'J2': 'tin'}}


def classify(rgb, metal=None, alpha=1.0):
    """KiCad 가 STEP/GLB 에 넣는 색으로 보드·부품 바디의 재질 무리를 가름 (rgb 0..1, 파일에 적힌 값).
    반환: 'mask' · 'silk' · 'enig' · 'fr4' · 'gold' · 'tin' · 'body' (몸체 → PART_RULES 로), 'keep' (모르면 원래 색)"""
    r, g, b = rgb[:3]
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    sat = max(rgb[:3]) - min(rgb[:3])
    if alpha < 0.95 and g > r and g > b:
        return 'mask'                        # KiCad 솔더마스크 (0.063, 0.16, 0.113, α 0.83)
    if alpha < 0.95 and lum > 0.8:
        return 'silk'                        # KiCad 실크 (1, 1, 1, α 0.9)
    if metal is not None and metal >= 0.5:
        return 'enig'                        # KiCad 동박 노출 (금 0.7/0.61/0 · 회 0.5) — ENIG 로 통일 [가정: 회색 금속도 노출 동박]
    if abs(r - 0.42) < 0.03 and abs(g - 0.45) < 0.03 and abs(b - 0.29) < 0.03:
        return 'fr4'                         # KiCad 판 몸체
    if r > 0.6 and 0.4 < g < 0.65 and b < 0.3:
        return 'gold'                        # 부품 모델 금 도금 접점 (0.709, 0.504, 0.21)
    if lum > 0.5 and sat < 0.2:
        return 'tin'                         # 부품 모델 리드 주석·은색 (0.645/0.638/0.572 등)
    if lum < 0.45:
        return 'body'                        # 흑·회·갈색 몸체 (0.435/0.398/0.316 = IC 1번 핀 표시 등도 몸체로)
    return 'keep'


def part_key(model='', ref='', board=''):
    import re
    for mp, rp, k in PART_RULES:
        if model and re.search(mp, model):
            return k
    if ref and board in BOARD_REF_ONLY and ref in BOARD_REF_ONLY[board]:
        return BOARD_REF_ONLY[board][ref]
    for mp, rp, k in PART_RULES:
        if ref and re.search(rp, ref) and not rp.startswith('^J'):
            return k
    return 'epoxy'


def body_key(rgb, metal=None, alpha=1.0, model='', ref='', board=''):
    import re
    for suf, k in LAYER_RULES:
        if model.endswith(suf) and model[:-len(suf)] in ('carrier', 'front', board):
            return k
    for mp, col, k in COLOR_OVERRIDES:
        if model and re.search(mp, model) and max(abs(a - b) for a, b in zip(rgb[:3], col)) < 0.01:
            return k
    c = classify(rgb, metal, alpha)
    if c == 'body':
        return part_key(model, ref, board)
    return c   # mask · silk · enig · fr4 · gold · tin · keep


def name_key(name, default='plastic'):
    return next((k for key, k in NAME_RULES if key in name), default)


def srgb255(rgb):
    def f(c):
        return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055
    return tuple(max(0, min(255, round(f(c) * 255))) for c in rgb)


def glb_materials(path):
    """보드 GLB 의 재질 원값 {재질 이름: (rgb, metallicFactor 또는 None, alpha)} — glTF 기본값(금속 1)으로 읽는 Blender 대신 파일 값 그대로."""
    import json, struct
    d = open(path, 'rb').read()
    n = struct.unpack('<I', d[12:16])[0]
    j = json.loads(d[20:20 + n])
    out = {}
    for i, m in enumerate(j.get('materials', [])):
        p = m.get('pbrMetallicRoughness', {})
        c = p.get('baseColorFactor', [1, 1, 1, 1])
        out[m.get('name', 'mat_%d' % i)] = (tuple(c[:3]), p.get('metallicFactor'), c[3])
    return out
