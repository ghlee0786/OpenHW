"""M-003 2차 계산 (CAD 독립): ① 방열 — 자연대류 상관식으로 방열판 크기 정하기·정상 상태 온도, ② IR 조명 범위 vs 시야 (HFOV 88°).
실행: python -I -B -X utf8 mechanical/m003/analysis2.py  → analysis2.md 를 쓴다. 모든 입력은 A{} 에 [가정]/[근거] 표기."""
import math, os, sys

sys.stdout.reconfigure(encoding='utf-8')   # cp949 콘솔에서 -X utf8 없이도 print 가 실패하지 않게

HERE = os.path.dirname(os.path.abspath(__file__))
g = {}
exec(open(os.path.join(HERE, 'params.py'), encoding='utf-8').read(), g)
d = g['derive'](g['P'])
out = []
w = out.append

# ------------------------------------------------------------------ ① 열
SIG = 5.670e-8
A = {
    'Q_core': 2.0,      # [가정] 코어 최악 평균 (SG2002 NPU·ISP + eMMC + Wi-Fi) — 문서 근거 없음, 실측 대상
    'Q_board': 1.0,     # [가정] 캐리어(PHY·DC-DC·USB) 0.7 + 전면(센서·AL8860 손실·ICR) 0.3
    'Q_led_elec': 1.55, # [근거 O-31] A 스트링 평균 (1 A 피크, 듀티 25%, Vf 3.1 × 2)
    'eta_opt': 1425 / 3100,  # [근거 R-006] 방사속 1.425 W / 전기 3.1 W
    'lost_frac': 0.25,  # [가정] 덮개 띠·벽에 막혀 안에서 흡수되는 빛 비율
    'eps_hs': 0.85,     # [가정] 흑색 아노다이즈 방사율 (맨 Al 은 약 0.1)
    'eps_petg': 0.90,   # [가정] 흑색 PETG
    'h_in': 4.0,        # [가정] 안쪽 공기 자연 대류 (밀폐 소형 공간)
    'k_petg': 0.2, 'k_al': 167.0,
    'R_flange': 0.9,    # [M002b 식] 옆 갭 패드 P340 (3.28 cm²)
    'R_ped': 0.25,      # [가정] 받침대 Al 6061 4 mm + 퍼짐
    'R_soc_spr': 4.0, 'R_led_pillar_A': 6.1, 'R_led_board': 5.0, 'R_led_js': 7.5,
    'T_amb': (25.0, 40.0),
}


def air(Tf):
    """공기 물성 (1 atm), 막 온도 Tf [°C] 선형 근사"""
    T = Tf + 273.15
    return 0.0241 + 7.3e-5 * Tf, 1.33e-5 + 9.0e-8 * Tf, 1.87e-5 + 1.3e-7 * Tf, 1.0 / T


def h_vplate(dT, L, Tf):
    """수직 평판 층류 자연대류 Churchill–Chu"""
    k, nu, al, be = air(Tf)
    Ra = 9.81 * be * max(dT, 0.1) * L ** 3 / (nu * al)
    Pr = nu / al
    Nu = 0.68 + 0.670 * Ra ** 0.25 / (1 + (0.492 / Pr) ** (9 / 16)) ** (4 / 9)
    return Nu * k / L


def h_rad(eps, Ts, Ta):
    Ts, Ta = Ts + 273.15, Ta + 273.15
    return eps * SIG * (Ts ** 2 + Ta ** 2) * (Ts + Ta)


def heatsink_G(hs, dT, Ta):
    """바깥 방열판 (바닥판 + 세로 핀) 컨덕턴스 W/K. 핀 채널: Elenbaas / Bar-Cohen–Rohsenow 대칭 등온 수직 평판."""
    n, H, tf, Lg, Wz, tb = hs['n'], hs['H'], hs['t'], hs['L'], hs['W'], hs['tb']   # mm, L = 중력 방향 길이
    Tf = Ta + dT / 2
    k, nu, al, be = air(Tf)
    if n >= 2:
        S = (Wz - n * tf) / (n - 1) * 1e-3
        L = Lg * 1e-3
        Ra = 9.81 * be * dT * S ** 3 / (nu * al)
        El = Ra * S / L
        Nu = (576 / El ** 2 + 2.873 / El ** 0.5) ** -0.5
        h = Nu * k / S
        m = math.sqrt(2 * h / (A['k_al'] * tf * 1e-3))
        eta = math.tanh(m * H * 1e-3) / (m * H * 1e-3)
        A_fin = 2 * n * H * Lg * 1e-6
        A_gap = (n - 1) * S * L
        G_conv = h * (eta * A_fin + A_gap) + h_vplate(dT, L, Tf) * (2 * (H + tb) * Lg * 1e-6)
        A_env = (Wz * Lg + 2 * (H + tb) * Lg + 2 * (H + tb) * Wz) * 1e-6
        Sm = S * 1e3
    else:
        h = h_vplate(dT, Lg * 1e-3, Tf)
        eta, Sm, A_fin = 1.0, 0.0, 0.0
        G_conv = h * Wz * Lg * 1e-6
        A_env = Wz * Lg * 1e-6
    G_rad = h_rad(A['eps_hs'], Ta + dT, Ta) * A_env
    return G_conv + G_rad, dict(h=h, eta=eta, S=Sm, G_conv=G_conv, G_rad=G_rad, A_fin=A_fin, A_env=A_env)


area_out = (2 * (d['y_out_hi'] - d['y_out_min']) * (d['z_bez_out'] - d['z_back_out'])
            + 2 * (d['x_out_max'] - d['x_out_min']) * (d['z_bez_out'] - d['z_back_out'])
            + 2 * (d['x_out_max'] - d['x_out_min']) * (d['y_out_hi'] - d['y_out_min'])) * 1e-6
A_in = 0.019     # [계산 근사] 공동 안쪽 면 + 덮개 안쪽 면
A_spr = 0.0035   # 방열판 두 면 + 플랜지


def solve(hs, Q_led_heat, Q_core, Ta, A_hs_face):
    """노드 S 방열판(내부), H 바깥 방열판, I 안 공기, W 벽. h 는 온도 의존 → 반복."""
    dH, dW = 15.0, 10.0
    for _ in range(40):
        G_Ha, info = heatsink_G(hs, max(dH, 0.5), Ta)
        L_wall = (d['z_bez_out'] - d['z_back_out']) * 1e-3
        h_w = h_vplate(max(dW, 0.5), L_wall, Ta + dW / 2) + h_rad(A['eps_petg'], Ta + dW, Ta)
        G_Wa = h_w * (area_out - A_hs_face)
        G_SH = 1 / (A['R_flange'] + A['R_ped'])
        G_SI = A['h_in'] * A_spr
        G_HI = A['h_in'] * 0.0018
        G_HW = A['k_petg'] * 0.0012 / 0.002
        G_IW = A['h_in'] * A_in
        Q_S, Q_I = Q_core + Q_led_heat, A['Q_board']
        M = [[G_SH + G_SI, -G_SH, -G_SI, 0, Q_S],
             [-G_SH, G_SH + G_HI + G_HW + G_Ha, -G_HI, -G_HW, 0],
             [-G_SI, -G_HI, G_SI + G_HI + G_IW, -G_IW, Q_I],
             [0, -G_HW, -G_IW, G_HW + G_IW + G_Wa, 0]]
        for i in range(4):
            p = M[i][i]
            for j in range(i, 5):
                M[i][j] /= p
            for k2 in range(4):
                if k2 != i:
                    f = M[k2][i]
                    for j in range(i, 5):
                        M[k2][j] -= f * M[i][j]
        S, H, I, W = [M[i][4] for i in range(4)]
        dH, dW = 0.5 * dH + 0.5 * H, 0.5 * dW + 0.5 * W
    return dict(S=S, H=H, I=I, W=W, R_hs=1 / G_Ha, q_hs=G_Ha * H, q_wall=G_Wa * W, info=info)


def led_heat(duty, n_str=1):
    elec = A['Q_led_elec'] * duty / 0.25
    return n_str * elec * (1 - A['eta_opt'] * (1 - A['lost_frac']))


HS_W = round(d['z_bez_out'] - d['z_back_out'] - 1.0, 1)   # 핀이 늘어서는 폭 (z 방향)
HS_L = 58.0                                               # 중력 방향 길이 (y −36…22)
w('# M-003 2차 계산 (analysis2.py 출력)\n')
w('## ① 방열 — 목표 (D-003 #26 갱신): 방열판→공기 ≤ 8 K/W, 안 공기 상승 ≤ 25 K\n')
w('### 계산 근거\n')
w('| 항목 | 값·식 | 근거 |')
w('|---|---|---|')
w('| 핀 채널 대류 | Nu_S = [576/El² + 2.873/El^0.5]^−0.5, El = Ra_S·S/L, h = Nu·k/S | Elenbaas / Bar-Cohen–Rohsenow (대칭 등온 수직 평판) |')
w('| 평판·벽 대류 | 수직 평판 Churchill–Chu: Nu = 0.68 + 0.670 Ra^¼ / [1+(0.492/Pr)^(9/16)]^(4/9) | 교재식 |')
w('| 핀 효율 | η = tanh(mH)/(mH), m = √(2h/(k·t)), Al 6061 k = 167 | 교재식 |')
w('| 복사 | **포함**. 방열판 외곽 포락면 × ε %.2f (흑색 아노다이즈 **가정** — 맨 Al ε≈0.1 이면 복사 몫이 거의 사라짐), 벽 ε %.2f | h_r = εσ(T²+Ta²)(T+Ta) |' % (A['eps_hs'], A['eps_petg']))
w('| 공기 물성 | 막 온도 선형 근사 (k, ν, α, β = 1/T) | 표값 근사 |')
w('| 설치 자세 | **+Y 위 (세로 핀이 중력 방향)** — 옆으로 누이면 핀 대류가 크게 준다 | 가정 |')
w('| 발열 | 코어 %.1f W 최악 평균 [가정, 실측 대상] · 보드 기타 %.1f W [가정] · LED A 전기 %.2f W (듀티 25%%) 중 창 밖으로 나가는 빛 %.0f%% × (1 − 막혀 흡수 %.0f%%) → 열 %.2f W | O-31, R-006 |' % (
    A['Q_core'], A['Q_board'], A['Q_led_elec'], A['eta_opt'] * 100, A['lost_frac'] * 100, led_heat(0.25)))
w('| 내부 경로 | 갭 패드 %.1f + 받침대 %.2f K/W, 안 공기 h %.0f W/m²K, 벽 PETG k %.1f | M-002b, 가정 |' % (A['R_flange'], A['R_ped'], A['h_in'], A['k_petg']))
w('')
w('### 방열판 변형 비교 (T_amb 25 °C, ΔT 반복 수렴, R 은 그 ΔT 에서)\n')
w('| 변형 | 핀 수×높이×두께 | 핀 간격 | 외형 X | 방열판→공기 R | 대류/복사 W/K | 안 공기 상승 | 방열판(내부) 상승 | 벽 상승 | 판정 |')
w('|---|---|---|---|---|---|---|---|---|---|')
cases = [('H0 안쪽 평판 (1차, 창 18 cm²)', dict(n=0, H=0, t=0, L=42, W=43, tb=2), 0.0018, 0.0),
         ('H1 바깥 바닥판만 (58×%.0f, 3t)' % HS_W, dict(n=0, H=0, t=0, L=HS_L, W=HS_W, tb=3), HS_L * HS_W * 1e-6, 3.0),
         ('H2 바깥 핀 9×12', dict(n=9, H=12, t=1.5, L=HS_L, W=HS_W, tb=3), HS_L * HS_W * 1e-6, 15.0),
         ('H3 바깥 핀 9×20', dict(n=9, H=20, t=1.5, L=HS_L, W=HS_W, tb=3), HS_L * HS_W * 1e-6, 23.0),
         ('H4 바깥 핀 10×25', dict(n=10, H=25, t=1.5, L=HS_L, W=HS_W, tb=3), HS_L * HS_W * 1e-6, 28.0),
         ('H5 바깥 핀 8×30', dict(n=8, H=30, t=1.5, L=HS_L, W=HS_W, tb=3), HS_L * HS_W * 1e-6, 33.0)]
best = None
for name, hs, Af, grow in cases:
    r = solve(hs, led_heat(0.25), A['Q_core'], 25.0, Af)
    i = r['info']
    ok = r['R_hs'] <= 8.0 and r['I'] <= 25.0
    if ok and best is None and r['R_hs'] <= 6.0:
        best = (name, hs, Af, grow)
    w('| %s | %s | %.1f | %.2f (+%.0f) | **%.1f K/W** | %.3f / %.3f | **%.1f K** | %.1f K | %.1f K | %s |' % (
        name, ('%d×%.0f×%.1f' % (hs['n'], hs['H'], hs['t'])) if hs['n'] else '-', i['S'],
        d['x_out_max'] - d['x_out_min'] + grow, grow, r['R_hs'], i['G_conv'], i['G_rad'], r['I'], r['S'], r['W'],
        '충족' if ok else '미달'))
CH = best or cases[-1]
w('\n- 선택: **%s** — 목표 두 개를 넘고 R 이 목표의 75 %% (6 K/W) 이하인 가장 작은 변형 — 가정이 많아 25 %% 여유. H2 (7.5 K/W) 는 외형 −8 mm 차선. params.py hs_* 가 이 값.' % CH[0])
w('\n### 선택안 정상 상태 온도 (°C)\n')
w('| 조건 | T_amb | 방열판(내부) | 바깥 방열판 | 안 공기 | 벽 | SoC 접합(추정) | LED 접합(추정) |')
w('|---|---|---|---|---|---|---|---|')
for label, duty, nstr in (('A 듀티 25%', 0.25, 1), ('A+B 듀티 25%', 0.25, 2), ('LED 끔', 0.0, 1)):
    for Ta in A['T_amb']:
        r = solve(CH[1], led_heat(duty, nstr), A['Q_core'], Ta, CH[2])
        S = r['S'] + Ta
        q1 = led_heat(duty, 1)
        tj = S + q1 * (A['R_led_pillar_A'] + A['R_led_board']) + q1 / 2 * A['R_led_js']
        w('| %s | %.0f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |' % (label, Ta, S, r['H'] + Ta, r['I'] + Ta, r['W'] + Ta,
                                                                    S + A['Q_core'] * A['R_soc_spr'], tj))
w('\n### 차선 순서 (orch): 방열판 확대/핀 → 듀티 상한 → 0.3 A 연속\n')
H0 = cases[0]
r0 = solve(H0[1], led_heat(0.25), A['Q_core'], 25.0, H0[2])
roff = solve(H0[1], 0.0, A['Q_core'], 25.0, H0[2])


def duty_cap(case):
    lo, hi = 0.0, 1.0
    if solve(case[1], 0.0, A['Q_core'], 25.0, case[2])['I'] > 25.0:
        return None
    for _ in range(40):
        mid = (lo + hi) / 2
        if solve(case[1], led_heat(mid), A['Q_core'], 25.0, case[2])['I'] <= 25.0:
            lo = mid
        else:
            hi = mid
    return lo


c0 = duty_cap(H0)
w('- 1차 평판(H0) 유지: 안 공기 상승 %.1f K (LED 끔 %.1f K), 방열판→공기 %.0f K/W — R 목표는 형상 값이라 듀티로 못 맞춤. 안 공기 25 K 를 지키는 A 듀티 상한 = **%s**.' % (
    r0['I'], roff['I'], r0['R_hs'], ('%.1f%%' % (c0 * 100)) if c0 is not None else 'LED 를 꺼도 넘음 → 듀티로 해결 불가'))
c1 = duty_cap(CH)
w('- 선택안: 안 공기 25 K 를 지키는 A 듀티 계산 상한 = **%.0f%%** (실제 상한은 O-31 1.6 W·LED 정격이 먼저).' % (min(c1 or 0, 1.0) * 100))
w('- 0.3 A 연속 (차선 3): Vf ≈ 2.7 V [가정] × 2 × 0.3 A ≈ 1.62 W 전기 — 듀티 25 % × 1 A 와 열이 거의 같고 정면 세기는 약 0.3 배 [R-006 선형 근사] → 열 이득 없이 조사만 준다.')

# ------------------------------------------------------------------ ② 조명
HFOV = 88.0
VFOV = 2 * math.degrees(math.atan(math.tan(math.radians(HFOV / 2)) * 1080 / 1920))
REL = [(0, 1.0), (30, 0.69), (45, 0.38), (60, 0.13), (90, 0.0)]   # [R-006] VSMA1085400 상대강도


def rel(th):
    for (a0, r0_), (a1, r1) in zip(REL, REL[1:]):
        if th <= a1:
            return r0_ + (r1 - r0_) * (th - a0) / (a1 - a0)
    return 0.0


zt, zw, zo = d['z_bez_in'], d['z_win_in'], d['z_bez_out']
xi0, xi1, ry = d['x_in_min'], d['x_in_max'], d['rib_y']
apA = ((xi0 + 1, xi1 - 1), (ry, d['y_in_hi']))
pkA = ((xi0, xi1), (ry, d['y_in_hi'] + 1.0))
apB = ((xi0 + 1, xi1 - 1), (d['b_pocket_y0'] + 1, -ry))
pkB = ((xi0, xi1), (d['b_pocket_y0'], -ry))
if d.get('b_ext'):   # M-007 J5 V4: B 창 가운데 연장 → 개구는 직사각형 둘의 합
    ex0, ex1, ey0 = d['b_ext']
    apB = [apB, ((ex0 + 1, ex1 - 1), (ey0 + 1, d['b_pocket_y0'] + 1))]
    pkB = [pkB, ((ex0, ex1), (ey0, d['b_pocket_y0']))]


def inside(p, r):
    if isinstance(r, list):
        return any(inside(p, q) for q in r)
    return r[0][0] <= p[0] <= r[0][1] and r[1][0] <= p[1] <= r[1][1]


def passes(led, tx, ty, ap, pk, z_led):
    x, y = led
    for z, rect in ((zt, ap), (zw, ap), (zw, pk), (zo, pk)):
        if z <= z_led:
            continue
        dz = z - z_led
        if not inside((x + tx * dz, y + ty * dz), rect):
            return False
    return True


LA = [(-6.0, 16.0), (6.0, 16.0)]
LB = [(-7.5, -16.5), (7.5, -16.5)]


def coverage(cases_, z_led, simple=None):
    N = 121
    tH, tV = math.tan(math.radians(HFOV / 2)), math.tan(math.radians(VFOV / 2))
    lit = tot = 0
    edge = {}
    keys = {'중앙': (N // 2, N // 2), '위 끝(+Y)': (N // 2, N - 1), '아래 끝(-Y)': (N // 2, 0), '좌우 끝': (0, N // 2), '아래 모서리': (0, 0)}
    for i in range(N):
        for j in range(N):
            tx = -tH + 2 * tH * i / (N - 1)
            ty = -tV + 2 * tV * j / (N - 1)
            th = math.degrees(math.atan(math.hypot(tx, ty)))
            irr = 0.0
            for leds, ap, pk in cases_:
                for L in leds:
                    ok = simple(L, tx, ty) if simple else passes(L, tx, ty, ap, pk, z_led)
                    if ok:
                        irr += rel(th)
            tot += 1
            lit += irr > 0
            for key, ij in keys.items():
                if (i, j) == ij:
                    edge[key] = irr
    return lit / tot, edge


def m001e_simple(inward_deg):
    def f(L, tx, ty):
        toward = -ty if L[1] > 0 else ty
        return math.degrees(math.atan(toward)) <= inward_deg if toward > 0 else True
    return f


w('\n## ② IR 조명 범위 vs 시야 (HFOV %.0f° × VFOV %.1f° — 1920×1080 rectilinear, 화소 균등 격자 121²)\n' % (HFOV, VFOV))
w('- 직접광이 덮개 띠·창 주머니 벽에 가리지 않는 화소 비율과 끝 화소의 상대 조도 합 (LED 하나 정면 = 1, R-006 배광; 거리·cos⁴ 는 경우마다 같아 뺌).')
w('- LED 윗면 z %.3f, 덮개 턱 z %.3f…%.3f, 창 주머니 z %.3f…%.3f. +Y 바깥은 45° 단으로 y %.1f 까지 (led_out_deg %.0f°).\n' % (
    d['z_led_top'], zt, zw, zw, zo, d['y_in_hi'], d['led_out_deg']))
w('| 경우 | 조명 닿는 화소 | 중앙 | 위 끝(+Y) | 아래 끝(-Y) | 좌우 끝 | 아래 모서리 | 비고 |')
w('|---|---|---|---|---|---|---|---|')
rows = [('M-003 덮개, A만 (B DNP)', [(LA, apA, pkA)], d['z_led_top'], None, '렌즈 쪽 7.2° 에서 잘림'),
        ('M-003 덮개, A+B', [(LA, apA, pkA), (LB, apB, pkB)], d['z_led_top'], None, 'B 렌즈 쪽 8.1°'),
        ('M-001e 기준 (덮개 띠 없음), A만', [(LA, None, None)], d['z_led_top'], m001e_simple(14.7), '칼라 그림자 14.7°, 바깥 제한 없음 근사'),
        ('K13 LED 띄움 보드 (LED 윗면 z %.3f), A만' % (d['z_win_in'] - 0.3), [(LA, apA, pkA)], d['z_win_in'] - 0.3, None, '창 주머니 벽만 남음'),
        ('K13, A+B', [(LA, apA, pkA), (LB, apB, pkB)], d['z_win_in'] - 0.3, None, '')]
for name, cs, zl, simple, note in rows:
    f, e = coverage(cs, zl, simple)
    w('| %s | **%.0f%%** | %.2f | %.2f | %.2f | %.2f | %.2f | %s |' % (name, f * 100, e['중앙'], e['위 끝(+Y)'], e['아래 끝(-Y)'], e['좌우 끝'], e['아래 모서리'], note))
w('\n- 해석: 렌즈 쪽 띠가 LED A 빛을 −Y 로 7.2° 넘게 보내지 못한다 → 화면 아래쪽(센서 −Y)은 B 없이는 직접광 0. 좌우(HFOV 끝)는 A1·A2 가 서로 반대쪽을 덮어 살아 있다.')
open(os.path.join(HERE, 'analysis2.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('\n'.join(out))
