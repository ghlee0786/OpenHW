"""M-005: 기성 압출 방열판 후보 판정 (CAD 독립). analysis2.py 의 식(Elenbaas/Bar-Cohen–Rohsenow 핀 채널, Churchill–Chu 평판,
핀 효율 tanh(mH)/mH, 복사)과 가정 A{} 를 그대로 가져와(소스 앞부분 exec) 후보마다 방열판→공기 R·안 공기 상승을 다시 계산한다.
실행: python -I -B mechanical/m003/analysis_m005.py → analysis_m005.md"""
import os, sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'analysis2.py'), encoding='utf-8').read()
ns = {'__file__': os.path.join(HERE, 'analysis2.py')}
exec(src[:src.index("HS_W = round(")], ns)          # 함수·가정·외함 치수까지만 (analysis2.md 는 건드리지 않음)
A, solve, led_heat, d = ns['A'], ns['solve'], ns['led_heat'], ns['d']

L_CUT = 58.0                                        # 압출 방향 절단 길이 = 핀 길이 (중력 방향, y −36…22)
W_MAX = round(d['z_bez_out'] - d['z_back_out'] - 1.0, 1)   # +X 면에 들어가는 최대 폭 (z 방향)
PED = (41.4, 42.4, 4.0)                             # 받침대 판 (창 통과) — 별도 Al 판
R_IF = 0.3 / (PED[0] * PED[1] / 100.0)              # [가정] 받침대 판 ↔ 압출 바닥 열 그리스 0.3 K·cm²/W
R_PED_PLATE = PED[2] * 1e-3 / (167.0 * PED[0] * PED[1] * 1e-6)

# 후보: 공개 카탈로그 값 (근거·URL 은 m003-enclosure.md §16 표). t = 핀 평균 두께, k = 재질 열전도율 [W/mK]
CANDIDATES = [
    # name, W(폭, 잘라 쓰는 경우 잘린 폭), n(그 폭 안 핀 수), H(핀 높이), t(핀 두께), tb(바닥), k, 메모
    # Fischer: 폭·높이·바닥·핀 수 = 공식 단면도(원문), 핀 두께 = 단면도 비율로 잰 추정, k = 6063 계열 200 [가정, 재질 미표기]
    ('REF H3 CNC (M-003 2차)', 68.9, 9, 20.0, 1.5, 3.0, 167.0, '비교 기준 — CNC 단품'),
    ('Fischer SK 444 75 SA', 62.5, 12, 16.5, 1.4, 3.5, 200.0, '흑색 아노다이즈 완제품, 길이만 절단'),
    ('Fischer SK 649 75 SA', 62.0, 12, 15.0, 1.4, 6.0, 200.0, '흑색 아노다이즈 완제품, 길이만 절단'),
    ('Fischer SK 594 75 SA, 폭 68.9 가공', 68.9, 22, 20.0, 0.9, 5.0, 200.0, '폭 가공(핀 2장 제거) — 절단면 무처리'),
    ('Fischer SK 648 75 SA', 68.9, 11, 5.0, 2.4, 4.0, 200.0, '짧은 핀(9 근접) 비교용, 폭 72→68.9 가공'),
    ('ATS-EXL74 (300 생지)', 68.9, 27, 12.0, 1.0, 3.0, 200.0, '단면 상세 미확인 — 바닥 3·핀 12·두께 1.0 가정, 2차 아노다이즈 필요'),
]
# 데이터시트 자연대류 열저항 (75 mm, 조건 미표기) → 58 mm 환산: R ∝ L^-0.67 (Fischer SK 594 50/75 mm 두 점에서 얻은 지수)
DS_75 = {'Fischer SK 444 75 SA': 3.7, 'Fischer SK 649 75 SA': 3.75, 'Fischer SK 594 75 SA, 폭 68.9 가공': 3.2,
         'Fischer SK 648 75 SA': 4.0}
DS_EXP = 0.67


def evaluate(c):
    name, W, n, H, t, tb, k, memo = c
    A['k_al'] = k
    A['R_ped'] = 0.25 + (R_IF + R_PED_PLATE if not name.startswith('REF') else 0.0)
    hs = dict(n=n, H=H, t=t, L=L_CUT, W=W, tb=tb)
    r = ns['solve'](hs, led_heat(0.25), A['Q_core'], 25.0, W * L_CUT * 1e-6)
    r40 = ns['solve'](hs, led_heat(0.25), A['Q_core'], 40.0, W * L_CUT * 1e-6)
    return r, r40


def model_vs_ds(c):
    """같은 식을 데이터시트 조건(길이 75, 방열판만, 온도차 75 K 가정)으로 돌린 값 → 데이터시트와의 비 (보수성)"""
    name, W, n, H, t, tb, k, memo = c
    A['k_al'] = k
    g_, _ = ns['heatsink_G'](dict(n=n, H=H, t=t, L=75.0, W=W, tb=tb), 75.0, 25.0)
    return (1 / g_) / DS_75[name] if name in DS_75 else None


if __name__ == '__main__':
    L_SEL = d['hs_y'][1] - d['hs_y'][0]
    out = ['# M-005 압출 방열판 후보 판정 (analysis_m005.py 출력)', '',
           '- 식·가정: analysis2.py 와 같음 (코어 %.1f W, 보드 %.1f W, LED A 열 %.2f W, ε %.2f 흑색 아노다이즈, +Y 위 세로 핀, T_amb 25 °C).' % (
               A['Q_core'], A['Q_board'], led_heat(0.25), A['eps_hs']),
           '- 압출재는 받침대를 별도 Al 판(%.1f × %.1f × %.1f)으로 붙임 → 직렬 저항 + 계면 %.3f K/W (그리스 0.3 K·cm²/W 가정) + 판 전도 %.3f K/W.' % (
               PED[0], PED[1], PED[2], R_IF, R_PED_PLATE),
           '- +X 면 최대 폭 %.1f mm. 절단 길이(핀 길이)는 58 (아래쪽 +X 면 높이) 과 %.0f (외함 Y 전체, 선택) 두 가지.' % (W_MAX, L_SEL),
           '- 「보수성」 = 같은 식을 데이터시트 조건(75 mm, 온도차 75 K 가정)으로 돌린 R ÷ 데이터시트 R. 「보정 R」 = 계산 R ÷ 보수성 (참고).', '',
           '| 후보 | 길이 | 폭 × 핀 수 × 핀 높이 × 두께 / 바닥 | k | 핀 간격 | 방열판→공기 R (계산) | 보수성 | 보정 R | 데이터시트 길이 환산 | 안 공기 상승 | 내부 방열판 상승 | 40 °C 안 공기 | 목표 (≤ 8 K/W, ≤ 25 K, 계산 R 기준) | 외형 X | 메모 |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for Lc in (58.0, L_SEL):
        globals()['L_CUT'] = Lc
        for c in CANDIDATES:
            r, r40 = evaluate(c)
            name, W, n, H, t, tb, k, memo = c
            ok = r['R_hs'] <= 8.0 and r['I'] <= 25.0
            cons = model_vs_ds(c)
            ds = ('%.1f K/W' % (DS_75[name] * (75.0 / Lc) ** DS_EXP)) if name in DS_75 else '—'
            out.append('| %s | %.0f | %.1f × %d × %.1f × %.2f / %.1f | %.0f | %.2f | **%.1f K/W** | %s | %s | %s | **%.1f K** | %.1f K | %.1f °C | %s | %.2f | %s |' % (
                name, Lc, W, n, H, t, tb, k, r['info']['S'], r['R_hs'], ('%.2f' % cons) if cons else '—',
                ('%.1f K/W' % (r['R_hs'] / cons)) if cons else '—', ds, r['I'], r['S'], r40['I'] + 40.0, '충족' if ok else '미달',
                d['x_out_max'] - d['x_out_min'] + tb + H, memo))
    out.append('')
    out.append('- 선택 (params.py hs_*): Fischer SK 444 75 SA 를 %.0f 로 절단. 계산 R 은 목표 8 을 조금 넘고(미달), 데이터시트 보정 R 은 충족. 안 공기 상승은 목표 안. 차선 = CNC H3.' % L_SEL)
    open(os.path.join(HERE, 'analysis_m005.md'), 'w', encoding='utf-8').write(chr(10).join(out) + chr(10))
    print(chr(10).join(out))
