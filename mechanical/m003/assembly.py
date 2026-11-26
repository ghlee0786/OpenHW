"""M-003 조립도(분해·순서 번호)와 부품표 — params.py 기준 (CAD 독립). 구매하지 않는다(수량·치수 정리만).
실행: python -I -B -X utf8 mechanical/m003/assembly.py → drawing/m003-assembly.pdf·png, bom.csv, bom.md"""
import csv, os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon, FancyArrow

HERE = os.path.dirname(os.path.abspath(__file__))
g = {}
exec(open(os.path.join(HERE, 'params.py'), encoding='utf-8').read(), g)
d = g['derive'](g['P'])
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False
OUT = os.path.join(HERE, 'drawing')
os.makedirs(OUT, exist_ok=True)

# ---------------- 부품표 ----------------
ry = d['rib_y']
xi0, xi1 = d['x_in_min'], d['x_in_max']
winA = ((xi1 - xi0) - 2 * d['win_clr'], (d['y_in_hi'] + 1.0 - ry) - 2 * d['win_clr'])
winB = ((xi1 - xi0) - 2 * d['win_clr'], (-ry - d['b_pocket_y0']) - 2 * d['win_clr'])
(ax0, ax1), (ay0, ay1) = d['als_in']
BOM = [
    # 번호, 이름, 수량, 사양·치수, 공정/재질, 근거·비고
    (1, 'HOUSING 본체', 1, '%.2f × %.1f × %.1f (X×Y×Z), 벽 %.1f / 뒷벽 %.1f' % (d['x_out_max'] - d['x_out_min'], d['y_out_hi'] - d['y_out_min'], d['z_bez_in'] - d['z_back_out'], d['t_w'], d['t_back']), 'FDM 흑색 PETG (차선 ASA)', 'out/stl/HOUSING.stl'),
    (2, 'FRONT_COVER 앞 덮개', 1, '%.2f × %.1f × %.1f, 렌즈 관·ALS 관 일체' % (d['x_out_max'] - d['x_out_min'], d['y_out_hi'] - d['y_out_min'], d['z_bez_out'] - d['z_bez_in']), 'FDM 흑색 PETG', 'out/stl/FRONT_COVER.stl'),
    (3, 'HS_EXTRUSION 바깥 방열판 (기성 압출)', 1, 'Fischer SK 444 75 SA (흑색 아노다이즈, 폭 62.5 · 바닥 3.5 · 핀 12 × 16.5) 을 %.0f 로 절단, M2.5 탭 6' % (d['hs_y'][1] - d['hs_y'][0]), '압출 완제품 + 절단·탭 2차가공', 'US$4.29/개 (75 mm, 최소 5개, Digi-Key 마켓플레이스, 확인 2026-11-27) — 차선 CNC H3'),
    (26, 'HS_PEDESTAL 받침대 판', 1, '%.1f × %.1f × %.1f, 접시 구멍 2' % (d['al_win_y'][1] - d['al_win_y'][0] - 2 * d['hs_ped_clr'], d['al_win_z'][1] - d['al_win_z'][0] - 2 * d['hs_ped_clr'], d['hs_ped_t']), 'Al 6061-T6 판 절단·드릴', '가격 미확인 (판재)'),
    (27, 'M2.5 × 6 접시머리 (받침대 판)', 2, 'ISO 10642 / A2', '스테인리스', '+ 열 그리스'),
    (4, 'SPREADER_M003 방열판', 1, '판 38 × 39 × 1.0 + 기둥 A/B1/B2 + +X 플랜지 2 × 39 × 7.4, 구멍 Ø4.0 × 4', 'Al 6061 가공', 'M-002b + M-003'),
    (5, 'LENS_WIN_PMMA 렌즈 창', 1, 'Ø%.1f × %.1f' % (d['lens_win_d'], d['win_t']), '투명 PMMA 레이저 컷', ''),
    (6, 'WIN_A_PMMA LED A 창', 1, '%.2f × %.2f × %.1f' % (winA[0], winA[1], d['win_t']), '투명 PMMA', ''),
    (7, 'WIN_B_PMMA LED B 창', 1, '%.2f × %.2f × %.1f' % (winB[0], winB[1], d['win_t']), '투명 PMMA', ''),
    (8, 'ALS_WIN_PMMA ALS 창', 1, '%.1f × %.1f × 1.5' % (ax1 - ax0 + 2.2 - 2 * d['win_clr'], ay1 - ay0 + 2.7 - 2 * d['win_clr']), '투명 PMMA', ''),
    (9, 'FOAM_LENS_RING 렌즈 폼 링', 1, 'ID %.1f / OD %.1f × %.1f (0.7로 압축)' % (2 * d['lens_foam'][0], 2 * d['lens_foam'][1], d['lens_foam'][2]), '흑색 셀 폼 (PORON 4701-30 등, 1.0t 가용 미확인)', '30 % 압축 (3M·Rogers 권장 25–35 %)'),
    (10, 'FOAM_ALS_GASKET ALS 개스킷', 1, '바깥 %.1f × %.1f / 안 %.1f × %.1f × %.1f (%.1f로 압축)' % (ax1 - ax0 + 2 * d['als_wall'], ay1 - ay0 + 2 * d['als_wall'], ax1 - ax0, ay1 - ay0, d['als_gasket_t'], d['als_gap']), '흑색 PVC 폼 (3M 4516 1.6t 대표)', '25 % 압축'),
    (11, '절연 패드 (기둥 위) Tflex P340', 3, 'A 19.6 × 3.6 · B1 6.3 × 6.6 · B2 6.3 × 6.6 (모서리 따냄), 1.0t', 'Laird Tflex P340', 'M-002b K25'),
    (12, '옆 갭 패드 (플랜지 ↔ 방열판 받침대) Tflex P340', 1, '39.0 × 8.4 × 1.0t', 'Laird Tflex P340', 'GND끼리라 절연 불필요, 같은 재료로 통일'),
    (13, 'SoC 열 패드 (코어 ↔ 방열판)', 1, '두께 1.5 (spr_gap 1.3 압축), 크기 SoC 덮개 영역 — 미정', '갭 패드', 'M-001 spr_gap'),
    (14, 'M2.5 열압입 인서트', 4, 'CNC Kitchen 표준 M2.5 × 4.0, 바깥 4.6, 구멍 Ø%.1f × 깊이 5.0, 벽 ≥1.6, 인두 245 °C (PETG)' % d['ins_hole_d'], '황동', '덮개 고정 — CNC Kitchen 블로그 표'),
    (15, '1/4"-20 열압입 인서트', 1, 'CNC Kitchen 1/4"-20 짧은 판 L 6.4, 바깥 8.7, 구멍 Ø%.1f, 벽 ≥3.3' % d['tripod_hole_d'], '황동', '삼각대 — 3DJake 표 (2차 출처)'),
    (16, 'M2.5 × 8 나사 (덮개)', 4, '냄비머리 ISO 14583 / A2', '스테인리스', ''),
    (17, 'M2.5 × 5 냄비머리 (방열판 → 외함, 안쪽에서)', 4, '벽 2 + 바닥 탭 3 물림, 0.30 N·m', '스테인리스', '핀 간격 4.15 < 머리 Ø4.5 → 바깥에서 못 넣음'),
    (18, 'M1.6 × 4 나사 (전면 보드 위)', 4, 'ISO 7045 / A2', '스테인리스', ''),
    (19, 'M1.6 × 8 나사 + 와셔 Ø3.5 (뒤 → 캐리어)', 4, 'ISO 7045 / A2, 카운터보어 Ø%.1f, 0.05 N·m' % d['post_cb_d'], '스테인리스', ''),
    (20, 'M1.6 육각 스탠드오프 M-F 8.0', 3, '전면–코어', '황동', ''),
    (21, 'M1.6 육각 스탠드오프 F-F 8.0', 3, '코어–캐리어', '황동', ''),
    (22, 'M1.6 스탠드오프 F-F 17.6 (맞춤)', 1, '(-17, -17) 전면–캐리어 직결 (차선: 8 + 9.6)', '황동', '표준 길이 아님'),
    (23, 'GH 6P 하니스 35mm', 1, 'GHR-06V-S × 2 + 압착 단자 12 + 28AWG', '—', 'M-002 K20 (핀 순서 K23 미결)'),
    (24, '창 접착 (투명 양면 테이프 또는 UV 접착)', 1, '창 4장 둘레', '—', '미정'),
    (25, '나사 고정제 (렌즈)', 1, '저강도', '—', '초점 맞춘 뒤'),
]
with open(os.path.join(HERE, 'bom.csv'), 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(['no', 'name', 'qty', 'spec_mm', 'material_process', 'note'])
    wr.writerows(BOM)
with open(os.path.join(HERE, 'bom.md'), 'w', encoding='utf-8') as f:
    f.write('# M-003 부품표 (params.py 에서 생성, 단위 mm) — 구매하지 않음, 수량·치수 정리\n\n| 번호 | 부품 | 수량 | 사양·치수 | 재질·공정 | 근거·비고 |\n|---|---|---|---|---|---|\n')
    for r in BOM:
        f.write('| %d | %s | %d | %s | %s | %s |\n' % r)

# ---------------- 조립도 (-Y 에서 본 분해도, x 가로 / z 세로) ----------------
fig, ax = plt.subplots(figsize=(16.5, 11.7))
ax.set_aspect('equal')
ax.axis('off')
K = dict(fill=False, lw=1.0, ec='k')


def part(x0, x1, z0, z1, dz=0.0, dx=0.0, **kw):
    st = dict(K)
    st.update(kw)
    ax.add_patch(Rectangle((x0 + dx, z0 + dz), x1 - x0, z1 - z0, **st))


def balloon(x, y, n, txt):
    ax.add_patch(Circle((x, y), 2.6, fc='white', ec='#c0392b', lw=1.0, zorder=5))
    ax.text(x, y, str(n), ha='center', va='center', fontsize=8, color='#c0392b', zorder=6)
    ax.text(x + 3.6, y, txt, ha='left', va='center', fontsize=6.5)


zb, zt, zo = d['z_back_out'], d['z_bez_in'], d['z_bez_out']
xo0, xo1 = d['x_out_min'], d['x_out_max']
# 본체 (고정 위치)
part(xo0, xo1, zb, zt, fc='#dddddd', fill=True)
part(xo0 + d['t_w'], d['x_in_max'], d['z_back_in'], zt, fc='white', fill=True)
for (x, y) in d['holes']:
    part(x - d['post_d'] / 2, x + d['post_d'] / 2, d['z_back_in'], d['z_car_bot'], fc='#bbbbbb', fill=True)
# 방열판 (오른쪽으로 분해)
DX = 40
(hb0, hb1) = d['x_hs_base']
part(hb0, hb1, d['hs_z'][0], d['hs_z'][1], dx=DX, fc='#555555', fill=True)
part(d['x_al_in'], hb0, d['al_win_z'][0] + 0.3, d['al_win_z'][1] - 0.3, dx=DX, fc='#555555', fill=True)
for zc_ in d['hs_fin_zc']:
    part(hb1, d['x_hs_tip'], zc_ - d['hs_t'] / 2, zc_ + d['hs_t'] / 2, dx=DX, fc='#555555', fill=True)
ax.add_patch(FancyArrow(hb0 + DX - 2, 0, -DX + 6, 0, width=0.3, head_width=2, color='#2c7fb8'))
# 적층 (위로 분해)
DZ_STACK = 55
zc0 = d['z_car_bot']
part(-20, 20, zc0, zc0 + 1.6, dz=DZ_STACK, fc='#7fbf7f', fill=True)                    # 캐리어
part(-15, 15, 0, 1.6, dz=DZ_STACK + 12, fc='#4f8f4f', fill=True)                        # 코어
part(-18, 20, 2.9, 3.9, dz=DZ_STACK + 24, fc='#aaaaaa', fill=True)                      # 방열판 판
part(18, 20, -4.5, 2.9, dz=DZ_STACK + 24, fc='#aaaaaa', fill=True)                      # 플랜지
part(-20, 20, d['z_fr_bot'], d['z_fr_top'], dz=DZ_STACK + 36, fc='#7fbf7f', fill=True)  # 전면
part(-9, 9, 33.385, 38.785, dz=DZ_STACK + 36, fc='#e0a070', fill=True)                  # 렌즈 머리
part(-6, 6, 15.985, 33.385, dz=DZ_STACK + 36, fc='#e0a070', fill=True)
# 덮개·창·폼
DZ_COV = 120
part(xo0, xo1, zt, zo, dz=DZ_COV, fc='#444444', fill=True)
part(-d['lens_tube'][1], d['lens_tube'][1], d['lens_tube'][2], zt, dz=DZ_COV, fc='#444444', fill=True)
part(-d['lens_win_d'] / 2, d['lens_win_d'] / 2, d['z_win_in'], zo, dz=DZ_COV + 16, fc='#cfe6ff', fill=True)
part(xi0, xi1, d['z_win_in'], zo, dz=DZ_COV + 24, fc='#cfe6ff', fill=True)
part(-d['lens_foam'][1], d['lens_foam'][1], 38.785, 39.485, dz=DZ_STACK + 44, fc='#111111', fill=True)
# 화살표 (조립 방향)
for z0, z1 in ((DZ_STACK + zc0 - 2, d['z_car_bot'] + 3), (DZ_COV + zt - 2, zt + 3)):
    ax.add_patch(FancyArrow(-32, z0, 0, z1 - z0, width=0.3, head_width=2, color='#2c7fb8'))
bx = xo1 + DX + 30
balloon(bx, d['z_back_in'] + 4, 1, '본체: M2.5 인서트 4·1/4" 인서트 압입 (BOM 14·15)')
balloon(bx, 20, 2, '받침대 판(26)을 압출재(3)에 접시머리 2 (27) → +X 창에 끼우고 안쪽에서 M2.5×5 ×4 (17)')
balloon(bx, DZ_STACK + zc0 + 1, 3, '캐리어 + F-F 8.0 ×3 (21) + F-F 17.6 (22), 코어 BTB 꽂기')
balloon(bx, DZ_STACK + 27, 4, '방열판(4): SoC 패드(13)·절연 패드(11)·옆 갭 패드(12) 붙이고 얹기')
balloon(bx, DZ_STACK + 47, 5, 'M-F 8.0 ×3 (20) → 전면 BTB 꽂기 → M1.6×4 ×4 (18)')
balloon(bx, DZ_STACK + 58, 6, 'GH 6P 하니스(23) J7↔J4 (-X 통로), ALS 개스킷(10)')
balloon(bx, DZ_STACK + 69, 7, '적층을 본체에 넣고 뒤에서 M1.6×8 ×4 (19)')
balloon(bx, DZ_STACK + 80, 8, '렌즈 초점 → 고정제(25) → 렌즈 폼 링(9)')
balloon(bx, DZ_COV + 30, 9, '창 4장(5–8) 덮개에 접착(24) → 덮개 M2.5×8 ×4 (16)')
ax.text(xo0, zb - 8, 'M-003 조립도 (-Y 에서 본 분해 — 가로 x, 세로 z, 단위 mm). 번호 = 조립 순서, 괄호 = 부품표 번호 (bom.md). 본체·방열판·덮개는 실제 치수, 보드·렌즈는 외곽 단순화.', fontsize=8)
ax.set_xlim(xo0 - 40, bx + 95)
ax.set_ylim(zb - 12, DZ_COV + zo + 30)
fig.tight_layout()
fig.savefig(os.path.join(OUT, 'm003-assembly.png'), dpi=150)
fig.savefig(os.path.join(OUT, 'm003-assembly.pdf'))
print('ok bom', len(BOM))
