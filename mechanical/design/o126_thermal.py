"""O-126 시안 A — 뒤 알루미늄 쉘이 D-003 #26 열 경로(바깥 방열판)를 대신하는지 analysis2 방식으로 다시 계산 → o126_thermal.md
실행: python -I -B -X utf8 mechanical/design/o126_thermal.py
- 식·가정·노드 망은 mechanical/m003/analysis2.py 를 그대로 쓴다(정의 부분만 읽음): 노드 S 방열판(내부 확산판) · H 바깥 Al · I 안 공기 · W 플라스틱 벽.
- 바뀐 것: H = 뒤 알루미늄 쉘(바깥 면 전부가 방열 면, 흑색 아노다이즈 ε 0.85), 안쪽 Al 면도 안 공기와 맞닿음(G_HI 큼), 외형은 시안 A.
- 목표(#26 갱신, analysis2 와 같음): 방열판→공기 ≤ 8 K/W, 안 공기 상승 ≤ 25 K. analysis2 처럼 R ≤ 6 K/W(가정 많아 25 % 여유)를 고르는 기준으로 쓴다."""
import math, os, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
M3 = os.path.join(HERE, '..', 'm003', 'analysis2.py')
g = {'__file__': M3}
exec(open(M3, encoding='utf-8').read().split('\nHS_W = ')[0], g)   # 정의만 (air · h_vplate · h_rad · heatsink_G · A · led_heat)
air, h_vplate, h_rad, heatsink_G, A, led_heat = (g[k] for k in ('air', 'h_vplate', 'h_rad', 'heatsink_G', 'A', 'led_heat'))
sys.path.insert(0, HERE)
from o126_dims import CASE   # 시안 A 외형 (Fusion 스크립트와 같은 값)

X0, X1, Y0, Y1, Z0, ZS, Z1 = (CASE[k] for k in ('X0', 'X1', 'Y0', 'Y1', 'Z0', 'ZS', 'Z1'))
W, H, Lal, Lpl = X1 - X0, Y1 - Y0, ZS - Z0, Z1 - ZS          # mm: 폭 x · 높이 y(중력) · Al 길이 z · 플라스틱 길이 z


def h_hplate(dT, Lc, Tf, up):
    """수평 평판 자연대류 (위를 보는 뜨거운 면 0.54 Ra^¼, 아래 면 0.27 Ra^¼) — 교재식, Lc = 넓이/둘레"""
    k, nu, al, be = air(Tf)
    Ra = 9.81 * be * max(dT, 0.1) * (Lc * 1e-3) ** 3 / (nu * al)
    return (0.54 if up else 0.27) * Ra ** 0.25 * k / (Lc * 1e-3)


def shell_G(v, dT, Ta):
    """뒤 Al 쉘 바깥 → 공기 W/K. 옆 두 면(세로, 핀은 세로 방향) · 뒤 면(세로) · 윗면 · 아랫면."""
    Tf = Ta + dT / 2
    eps = A['eps_hs']
    G = 0.0
    side = dict(n=v['side_n'], H=v['side_H'], t=v['side_t'], L=H, W=Lal, tb=2.0)
    G += 2 * (heatsink_G(side, dT, Ta)[0] if v['side_n'] else (h_vplate(dT, H * 1e-3, Tf) + h_rad(eps, Ta + dT, Ta)) * H * Lal * 1e-6)
    back = dict(n=v['back_n'], H=v['back_H'], t=v['back_t'], L=H - 14.0, W=W, tb=4.0)   # 핀 길이 = 높이 − 14 (위·아래 모서리 숨은 나사 자리)
    G += heatsink_G(back, dT, Ta)[0] if v['back_n'] else (h_vplate(dT, H * 1e-3, Tf) + h_rad(eps, Ta + dT, Ta)) * W * H * 1e-6
    a_tb = W * Lal
    Lc = a_tb / (2 * (W + Lal))
    G += (h_hplate(dT, Lc, Tf, True) + h_rad(eps, Ta + dT, Ta)) * a_tb * 1e-6
    G += (h_hplate(dT, Lc, Tf, False) + h_rad(eps, Ta + dT, Ta)) * a_tb * 1e-6 * 0.7   # 아랫면 30 % 는 케이블 오목 자리·브래킷
    return G


A_pl_out = (2 * H * Lpl + 2 * W * Lpl + W * H) * 1e-6          # 플라스틱 앞 쉘 옆·위·아래 + 앞 유리
A_al_in = (2 * (H - 4) * (Lal - 4) + 2 * (W - 4) * (Lal - 4) + (W - 4) * (H - 4)) * 1e-6
A_pl_in = (2 * (H - 4) * Lpl + 2 * (W - 4) * Lpl + (W - 4) * (H - 4)) * 1e-6
A_joint = 2 * ((W - 2) + (H - 2)) * 2.0 * 1e-6                  # 분할면 (벽 두께 2) — PETG 쪽 전도
A_spr = 0.0035                                                  # analysis2 와 같음 (확산판 두 면 + 플랜지)


def solve(v, Q_led_heat, Q_core, Ta):
    dH, dW = 15.0, 10.0
    for _ in range(60):
        G_Ha = shell_G(v, max(dH, 0.5), Ta)
        h_w = h_vplate(max(dW, 0.5), H * 1e-3, Ta + dW / 2) + h_rad(A['eps_petg'], Ta + dW, Ta)
        G_Wa = h_w * A_pl_out
        G_SH = 1 / (A['R_flange'] + A['R_ped'])
        G_SI = A['h_in'] * A_spr
        G_HI = A['h_in'] * A_al_in
        G_HW = A['k_petg'] * A_joint / 0.002
        G_IW = A['h_in'] * A_pl_in
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
        S, Hh, I, Ww = [M[i][4] for i in range(4)]
        dH, dW = 0.5 * dH + 0.5 * Hh, 0.5 * dW + 0.5 * Ww
    return dict(S=S, H=Hh, I=I, W=Ww, R_hs=1 / G_Ha, G_Ha=G_Ha)


VARIANTS = [
    ('T0 매끈한 Al 쉘', dict(side_n=0, side_H=0, side_t=0, back_n=0, back_H=0, back_t=0)),
    ('T1 옆 홈 (O-125 덩어리: 폭 1.4 깊이 2.2)', dict(side_n=8, side_H=2.2, side_t=1.6, back_n=0, back_H=0, back_t=0)),
    ('T2 뒤 세로 핀 7×8', dict(side_n=0, side_H=0, side_t=0, back_n=7, back_H=8.0, back_t=2.0)),
    ('T3 뒤 세로 핀 7×12', dict(side_n=0, side_H=0, side_t=0, back_n=7, back_H=12.0, back_t=2.0)),
    ('T4 뒤 핀 7×12 + 옆 핀 4×5', dict(side_n=4, side_H=5.0, side_t=2.0, back_n=7, back_H=12.0, back_t=2.0)),
    ('T5 뒤 핀 7×16 + 옆 핀 4×6', dict(side_n=4, side_H=6.0, side_t=2.0, back_n=7, back_H=16.0, back_t=2.0)),
]


def main():
    out = []
    w = out.append
    w('# O-126 시안 A 방열 재계산 (o126_thermal.py 출력 — analysis2 방식)\n')
    w('- 외형 %.1f × %.1f × %.1f mm (x·y·z), 뒤 Al 쉘 z %.1f…%.1f (길이 %.1f), 앞 플라스틱 z %.1f…%.1f. +Y 위(세로 설치).' % (W, H, Z1 - Z0, Z0, ZS, Lal, ZS, Z1))
    w('- 열 경로: 코어 → 확산판 SPREADER_M003 → 옆 갭 패드 GAP_PAD_PX (R %.1f K/W) → **뒤 Al 쉘 안쪽 받침 리브** (R %.2f, analysis2 R_ped 그대로) → 쉘 바깥 → 공기.' % (A['R_flange'], A['R_ped']))
    w('  analysis2 의 바깥 방열판(HS_EXTRUSION·HS_PEDESTAL)·+X 벽 창은 없앤다 — Al 쉘이 방열판이다.')
    w('- 발열·물성·대류식은 analysis2.py 와 같은 값(코어 %.1f W [가정] · 보드 %.1f W [가정] · LED A 열 %.2f W @ 듀티 25 %%). 수평 면은 0.54/0.27 Ra^¼ (교재식).\n' % (A['Q_core'], A['Q_board'], led_heat(0.25)))
    w('| 변형 | Al 쉘→공기 R | 안 공기 상승 | 확산판 상승 | Al 쉘 상승 | 플라스틱 벽 상승 | 외형 증가 | 판정 (R ≤ 8 · 안 공기 ≤ 25) | R ≤ 6 (여유) |')
    w('|---|---|---|---|---|---|---|---|---|')
    pick = None
    for name, v in VARIANTS:
        r = solve(v, led_heat(0.25), A['Q_core'], 25.0)
        ok = r['R_hs'] <= 8.0 and r['I'] <= 25.0
        ok6 = ok and r['R_hs'] <= 6.0
        if ok6 and pick is None:
            pick = (name, v)
        grow = 'x +%.0f · z +%.0f' % (2 * v['side_H'] if v['side_n'] else 0, v['back_H'] if v['back_n'] else 0)
        w('| %s | **%.1f K/W** | **%.1f K** | %.1f K | %.1f K | %.1f K | %s | %s | %s |' % (name, r['R_hs'], r['I'], r['S'], r['H'], r['W'], grow,
                                                                                    '충족' if ok else '미달', '예' if ok6 else '아니오'))
    pick = pick or VARIANTS[-1]
    w('\n- 선택: **%s** — #26 목표 둘을 넘고 R ≤ 6 K/W(analysis2 와 같은 25 %% 여유)인 가장 작은 변형. o126_dims.py FINS 가 이 값.' % pick[0])
    w('\n### 선택안 정상 상태 온도 (°C)\n')
    w('| 조건 | T_amb | 확산판 | Al 쉘 | 안 공기 | 플라스틱 벽 | SoC 접합(추정) | LED 접합(추정) |')
    w('|---|---|---|---|---|---|---|---|')
    for label, duty, nstr in (('A 듀티 25%', 0.25, 1), ('A+B 듀티 25%', 0.25, 2), ('LED 끔', 0.0, 1)):
        for Ta in A['T_amb']:
            r = solve(pick[1], led_heat(duty, nstr), A['Q_core'], Ta)
            S = r['S'] + Ta
            q1 = led_heat(duty, 1)
            tj = S + q1 * (A['R_led_pillar_A'] + A['R_led_board']) + q1 / 2 * A['R_led_js']
            w('| %s | %.0f | %.1f | %.1f | %.1f | %.1f | %.1f | %.1f |' % (label, Ta, S, r['H'] + Ta, r['I'] + Ta, r['W'] + Ta, S + A['Q_core'] * A['R_soc_spr'], tj))
    w('\n- [가정] 그대로: 코어 발열 2 W 는 실측 대상(#26·#29 실측 판정). 핀 모서리 겹침(옆 핀 ↔ 뒤 핀 포락면 복사)은 따로 빼지 않음 — 작게 과대.')
    open(os.path.join(HERE, 'o126_thermal.md'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
    print('\n'.join(out))
    return pick


if __name__ == '__main__':
    main()
