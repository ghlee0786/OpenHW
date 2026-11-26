# M-003 외함 형상 정의 (CAD 독립 CSG). params.derive() 결과 d 를 받아 부품별 CSG 트리를 돌려준다.
# 기본 입체:  ('box', x0, x1, y0, y1, z0, z1)
#            ('cyl', (x,y,z) 시작, (x,y,z) 끝, r 시작, r 끝)      — r 이 다르면 원뿔
#            ('hs45', y_a, z_a)  — z − z_a < y − y_a 인 반공간(+Y 벽 45° 단 아래쪽), x 방향 무한
# 연산:      ('u', a, b, ...) 합 / ('d', a, b, ...) a 에서 b… 빼기 / ('i', a, b) 교집합
# Fusion 빌더(scripts/02_build.py)와 차선 CadQuery 모두 이 트리만 읽는다.
import math


def box(x0, x1, y0, y1, z0, z1):
    return ('box', min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1))


def zcyl(x, y, z0, z1, r, r1=None):
    return ('cyl', (x, y, z0), (x, y, z1), r, r if r1 is None else r1)


def xcyl(y, z, x0, x1, r):
    return ('cyl', (x0, y, z), (x1, y, z), r, r)


def ycyl(x, z, y0, y1, r):
    return ('cyl', (x, y0, z), (x, y1, z), r, r)


def rbox_z(x0, x1, y0, y1, z0, z1, r):
    if r <= 0:
        return box(x0, x1, y0, y1, z0, z1)
    return ('u', box(x0 + r, x1 - r, y0, y1, z0, z1), box(x0, x1, y0 + r, y1 - r, z0, z1),
            *[zcyl(x, y, z0, z1, r) for x in (x0 + r, x1 - r) for y in (y0 + r, y1 - r)])


def parts(d):
    P = {}
    BIG = 200.0
    zt = d['z_bez_in']
    # ---------- 본체 (뒤·옆벽, 앞이 열림) ----------
    xo0, xo1 = d['x_out_min'], d['x_out_max']
    xi0, xi1 = d['x_in_min'], d['x_in_max']
    # +Y 벽: z < step_z0 는 y_in_lo, 45° 로 올라가 y_in_hi
    zs = d['step_z0']
    outer_notch = ('i', box(xo0 - 1, xo1 + 1, d['y_out_lo'], d['y_out_hi'] + 1, d['z_back_out'] - 1, zt + 1),
                   ('hs45', d['y_out_lo'], zs - d['t_w'] * (math.sqrt(2) - 1)))
    outer = ('d', box(xo0, xo1, d['y_out_min'], d['y_out_hi'], d['z_back_out'], zt), outer_notch)
    inner_notch = ('i', box(xi0 - 1, xi1 + 1, d['y_in_lo'], d['y_in_hi'] + 1, d['z_back_in'] - 1, zt + 2),
                   ('hs45', d['y_in_lo'], zs))
    cavity = ('d', box(xi0, xi1, d['y_in_min'], d['y_in_hi'], d['z_back_in'], zt + 1), inner_notch)
    zc = d['z_car_bot']
    adds = []
    cuts = []
    # 적층 기둥 (캐리어 구멍 4곳) — 뒤에서 M1.6×8, 카운터보어
    for (x, y) in d['holes']:
        adds.append(zcyl(x, y, d['z_back_in'] - 0.1, zc, d['post_d'] / 2))
        cuts.append(zcyl(x, y, d['z_back_out'] - 1, zc + 1, d['post_hole'] / 2))
        cuts.append(zcyl(x, y, d['z_back_out'] - 1, zc - d['post_cb_top'], d['post_cb_d'] / 2))
    # 덮개 나사 보스 (M2.5 인서트) — 위쪽만, 45° 원뿔로 받침 없이 출력
    bz1 = zt
    bz0 = zt - 8.5
    for (x, y) in d['cov_screws']:
        r = d['boss_d'] / 2
        adds.append(zcyl(x, y, bz0, bz1, r))
        adds.append(zcyl(x, y, bz0 - r, bz0, 0.05, r))
        cuts.append(zcyl(x, y, bz1 - d['ins_len'] - 1.0, bz1 + 1, d['ins_hole_d'] / 2))
    # 삼각대 1/4"-20 보스
    tx, ty = d['tripod']
    adds.append(zcyl(tx, ty, d['z_back_in'] - 0.1, d['z_back_in'] + d['tripod_boss_h'], d['tripod_boss_d'] / 2))
    cuts.append(zcyl(tx, ty, d['z_back_out'] - 1, d['z_back_in'] + d['tripod_boss_h'] - 1.0, d['tripod_hole_d'] / 2))
    # ---- 개구 ----
    # −Y 벽: RJ45 (권장 패널 개구, PCB 면부터 아래로)
    rjc = (d['rj_x'][0] + d['rj_x'][1]) / 2
    cuts.append(box(rjc - d['rj_open_w'] / 2, rjc + d['rj_open_w'] / 2, d['y_out_min'] - 1, d['y_in_min'] + 1,
                    zc - d['rj_open_h'], zc + 0.01))
    # −Y 벽: DC 잭 (원)
    dcx = (d['dc_x'][0] + d['dc_x'][1]) / 2
    dcz = zc - d['dc_axis_below']
    cuts.append(ycyl(dcx, dcz, d['y_out_min'] - 1, d['y_in_min'] + 1, d['dc_open_d'] / 2))
    # −X 벽: USB-C (긴 원형, y 방향 길이 usb_open_w, 높이 usb_open_h)
    uyc = (d['usb_y'][0] + d['usb_y'][1]) / 2
    uzc = zc - d['usb_h'] / 2
    rr = d['usb_open_h'] / 2
    cuts.append(box(xo0 - 1, xi0 + 1, uyc - d['usb_open_w'] / 2, uyc + d['usb_open_w'] / 2, uzc - rr, uzc + rr))
    # +Y 벽: microSD 슬롯 + 손가락 홈
    sxc = (d['sd_x'][0] + d['sd_x'][1]) / 2
    cuts.append(box(sxc - d['sd_slot_w'] / 2, sxc + d['sd_slot_w'] / 2, d['y_in_lo'] - 1, d['y_out_lo'] + 1,
                    zc + d['sd_slot_z'][0], zc + d['sd_slot_z'][1]))
    cuts.append(box(sxc - 9.0, sxc + 9.0, d['y_out_lo'] - 1.2, d['y_out_lo'] + 1, zc - 4.6, zc + 2.4))
    # 뒷벽: 버튼 핀 구멍, 상태 LED 구멍
    for (x, y) in d['btn']:
        cuts.append(zcyl(x, y, d['z_back_out'] - 1, d['z_back_in'] + 0.5, 1.1))
    for (x, y) in d['stat_led']:
        cuts.append(zcyl(x, y, d['z_back_out'] - 1, d['z_back_in'] + 0.5, 1.0))
    # +X 벽: 알루미늄 옆판 창 + 나사 구멍
    cuts.append(box(d['x_in_max'] - 1, xo1 + 1, d['al_win_y'][0], d['al_win_y'][1], d['al_win_z'][0], d['al_win_z'][1]))
    for (y, z) in d['al_holes']:
        cuts.append(xcyl(y, z, d['x_in_max'] - 1, xo1 + 1, 1.4))
    P['HOUSING'] = ('d', ('u', ('d', outer, cavity), *adds), *cuts)
    if d['print_tab_w'] > 0:   # 같은 부품 안 두 번째 바디 — STL 에는 들어가고 간섭 검사에서는 뺀다 (이름 PRINT_TAB_*)
        yc = (d['al_win_y'][0] + d['al_win_y'][1]) / 2
        P['HOUSING'] = [('HOUSING', P['HOUSING']),
                        ('PRINT_TAB_PX_WIN', box(d['x_in_max'], xo1, yc - d['print_tab_w'] / 2, yc + d['print_tab_w'] / 2,
                                                 d['al_win_z'][0] - 0.01, d['al_win_z'][1] + 0.01))]

    # ---------- 바깥 방열판 (+X): 압출재(바닥 + 세로 핀) + 창을 지나는 받침대 판 ----------
    #   압출재: 외함 안쪽에서 M2.5 나사 4개 (벽 Ø2.8 → 바닥 탭 M2.5) / 받침대 판: 접시머리 M2.5 2개 (판 쪽 → 바닥 탭)
    (hb0, hb1), (hy0, hy1), (hz0, hz1) = d['x_hs_base'], d['hs_y'], d['hs_z']
    c = d['hs_ped_clr']
    hs = [box(hb0, hb1, hy0, hy1, hz0, hz1)]
    for zc_ in d['hs_fin_zc']:
        hs.append(box(hb1 - 0.01, d['x_hs_tip'], hy0, hy1, zc_ - d['hs_t'] / 2, zc_ + d['hs_t'] / 2))
    taps = [xcyl(y, z, hb0 - 1, hb1 + 0.01, 1.025) for (y, z) in d['al_holes'] + d['hs_ped_screws']]   # M2.5 탭 밑구멍 Ø2.05 (바닥 관통)
    P['HS_EXTRUSION'] = ('d', ('u', *hs), *taps)
    ped = box(d['x_al_in'], hb0, d['al_win_y'][0] + c, d['al_win_y'][1] - c, d['al_win_z'][0] + c, d['al_win_z'][1] - c)
    csk = []
    for (y, z) in d['hs_ped_screws']:
        csk.append(xcyl(y, z, d['x_al_in'] - 1, hb0 + 1, 1.4))                       # Ø2.8 틈새
        csk.append(('cyl', (d['x_al_in'] - 0.01, y, z), (d['x_al_in'] + 1.6, y, z), 2.45, 1.4))   # 90° 접시 Ø4.9
    P['HS_PEDESTAL'] = ('d', ped, *csk)

    # ---------- 앞 덮개 (창 받침 + 렌즈 관 + ALS 관) ----------
    zw, zo = d['z_win_in'], d['z_bez_out']
    bez = box(xo0, xo1, d['y_out_min'], d['y_out_hi'], zt, zo)
    ccuts = []
    # 렌즈 창 주머니 + 턱 개구
    ccuts.append(zcyl(0, 0, zw, zo + 1, d['lens_win_d'] / 2 + d['win_clr']))
    ccuts.append(zcyl(0, 0, zt - 1, zw + 0.01, d['lens_ap_d'] / 2))
    # LED A 창 (+Y), B 창 (−Y)
    ry = d['rib_y']
    ccuts.append(box(xi0, xi1, ry, d['y_in_hi'] + 1.0, zw, zo + 1))
    ccuts.append(box(xi0 + 1, xi1 - 1, ry, d['y_in_hi'], zt - 1, zw + 0.01))
    ccuts.append(box(xi0, xi1, d['b_pocket_y0'], -ry, zw, zo + 1))
    ccuts.append(box(xi0 + 1, xi1 - 1, d['b_pocket_y0'] + 1, -ry, zt - 1, zw + 0.01))
    # ALS 창 (1.5 깊이) + 관 안쪽
    (ax0, ax1), (ay0, ay1) = d['als_in']
    ccuts.append(box(ax0 - 1.1, ax1 + 1.1, ay0 - 1.1, ay1 + 1.6, zo - 1.5, zo + 1))   # ALS 주머니 (창은 win_clr 만큼 작게)
    ccuts.append(box(ax0, ax1, ay0, ay1, d['z_fr_top'], zo - 1.49))
    # 덮개 나사 구멍 Ø2.8
    for (x, y) in d['cov_screws']:
        ccuts.append(zcyl(x, y, zt - 1, zo + 1, 1.4))
    ri, ro, zb = d['lens_tube']
    tube = ('d', zcyl(0, 0, zb, zt + 0.1, ro), zcyl(0, 0, zb - 1, zt + 1, ri))
    w = d['als_wall']
    als_tube = box(ax0 - w, ax1 + w, ay0 - w, ay1 + w, d['z_fr_top'] + d['als_gap'], zt + 0.1)
    P['FRONT_COVER'] = ('d', ('u', bez, tube, als_tube), *ccuts)

    # ---------- 맞춤 시험 쿠폰 (FDM, 외함 옆 x +100 — 간섭 검사 제외) ----------
    cx, cz = 100.0, d['z_back_out']
    cp = [box(cx, cx + 80, -15, 15, cz, cz + 4.0)]
    cc = []
    cp.append(zcyl(cx + 8, 0, cz + 3.9, cz + 4.0 + 6.0, d['boss_d'] / 2))                      # M2.5 인서트 보스
    cc.append(zcyl(cx + 8, 0, cz + 10.0 - d['ins_len'] - 1.0, cz + 11, d['ins_hole_d'] / 2))
    cp.append(zcyl(cx + 24, 0, cz + 3.9, cz + 4.0 + 6.0, d['tripod_boss_d'] / 2))              # 1/4"-20 인서트 보스
    cc.append(zcyl(cx + 24, 0, cz + 10.0 - 7.4, cz + 11, d['tripod_hole_d'] / 2))
    cc.append(zcyl(cx + 38, -6, cz - 1, cz + 5, d['post_hole'] / 2))                         # M1.6 기둥 구멍
    cc.append(zcyl(cx + 38, 6, cz - 1, cz + 5, 1.4))                                         # M2.5 틈새 Ø2.8
    cc.append(zcyl(cx + 46, -6, cz - 1, cz + 1.0, d['post_cb_d'] / 2))                       # 카운터보어 Ø3.8
    cc.append(zcyl(cx + 46, -6, cz - 1, cz + 5, d['post_hole'] / 2))
    cc.append(zcyl(cx + 63, 0, cz + 1.0, cz + 5, d['lens_win_d'] / 2 + d['win_clr']))         # 렌즈 창 주머니 (깊이 3)
    cc.append(zcyl(cx + 63, 0, cz - 1, cz + 1.01, d['lens_ap_d'] / 2))
    P['PRINT_COUPON'] = ('d', ('u', *cp), *cc)

    # ---------- 창 (PMMA, 투명) ----------
    P['LENS_WIN_PMMA'] = zcyl(0, 0, zw, zo, d['lens_win_d'] / 2)
    wr = d['win_r']
    k = d['win_clr']
    P['WIN_A_PMMA'] = rbox_z(xi0 + k, xi1 - k, ry + k, d['y_in_hi'] + 1.0 - k, zw, zo, wr)
    P['WIN_B_PMMA'] = rbox_z(xi0 + k, xi1 - k, d['b_pocket_y0'] + k, -ry - k, zw, zo, wr)
    P['ALS_WIN_PMMA'] = rbox_z(ax0 - 1.1 + k, ax1 + 1.1 - k, ay0 - 1.1 + k, ay1 + 1.6 - k, zo - 1.5, zo, wr)
    # ---------- 흑색 폼 ----------
    fi, fo, ft = d['lens_foam']
    zh = d['z_win_in'] - 0.5 - 1.4   # 렌즈 머리 앞면 = 돔 바닥 (M001: 38.785)
    P['FOAM_LENS_RING'] = ('d', zcyl(0, 0, zh, zt, fo), zcyl(0, 0, zh - 1, zt + 1, fi))
    P['FOAM_ALS_GASKET'] = ('d', box(ax0 - w, ax1 + w, ay0 - w, ay1 + w, d['z_fr_top'], d['z_fr_top'] + d['als_gap']),   # 압축 상태 (자유 als_gasket_t)
                            box(ax0, ax1, ay0, ay1, d['z_fr_top'] - 1, d['z_fr_top'] + d['als_gap'] + 1))
    # ---------- 방열판 (판 + 일체 기둥 A/B + +X 플랜지) + 절연 패드 + 옆 갭 패드 ----------
    (fx0, fx1), (fy0, fy1), (fz0, fz1) = d['flange']
    (sx0, sx1), (sy0, sy1) = d['spr_xy']
    zs0 = d['core_t'] + d['spr_gap']
    zs1 = zs0 + d['spr_t']
    zp1 = d['z_fr_bot'] - d['ins_t']
    (ax0_, ax1_), (ay0_, ay1_) = d['pillar_a']
    spr = [box(sx0, sx1, sy0, sy1, zs0, zs1), box(fx0, fx1, fy0, fy1, fz0, zs0 + 0.01), box(ax0_, ax1_, ay0_, ay1_, zs1 - 0.01, zp1)]
    for (bx, by) in d['pillar_b']:
        spr.append(box(bx[0], bx[1], by[0], by[1], zs1 - 0.01, zp1))
    (nx0, nx1), (ny0, ny1) = d['b2_notch']
    scut = [box(-d['slot_w'] / 2, d['slot_w'] / 2, ay0_ - 1, ay1_ + 1, zp1 - d['slot_d'], zp1 + 1),
            box(nx0, nx1, ny0, ny1, zs1, zp1 + 1)]
    for (x, y) in d['holes']:
        scut.append(zcyl(x, y, zs0 - 1, zs1 + 1, d['so_clear_d'] / 2))
    (wx, wy) = d['spr_j1_win']
    scut.append(box(wx[0], wx[1], wy[0], wy[1], zs0 - 1, zs1 + 1))
    P['SPREADER_M003'] = ('d', ('u', *spr), *scut)
    pads = [box(px[0], px[1], py[0], py[1], zp1, d['z_fr_bot']) for (px, py) in d['ins_pads']]
    P['INS_PADS_P340'] = ('d', ('u', *pads), box(nx0, nx1 + 0.5, ny0, ny1 + 1, zp1 - 1, d['z_fr_bot'] + 1))
    P['GAP_PAD_PX'] = box(fx1, d['x_al_in'], fy0, fy1, fz0, zs1)
    # ---------- 적층 체결 (M1.6 스탠드오프·나사) ----------
    so = []
    for (x, y) in d['core_holes']:
        so.append(zcyl(x, y, d['core_t'], d['z_fr_bot'], d['so_d'] / 2))     # 전면–코어
        so.append(zcyl(x, y, d['z_car_top'], 0.0, d['so_d'] / 2))           # 코어–캐리어
    x, y = d['holes'][3]
    so.append(zcyl(x, y, d['z_car_top'], d['z_fr_bot'], d['so_d'] / 2))    # 전면–캐리어 직결 (맞춤 17.6)
    P['HW_STANDOFFS'] = ('u', *so)
    heads = []
    for (x, y) in d['holes']:
        heads.append(zcyl(x, y, d['z_fr_top'], d['z_fr_top'] + 1.6, 1.5))           # 전면 M1.6 머리
        heads.append(zcyl(x, y, zc - d['post_cb_top'] - 1.6, zc - d['post_cb_top'], 1.5))  # 뒤 M1.6×8 머리
    P['HW_M16_HEADS'] = ('u', *heads)
    nuts = [box(d['x_in_max'] - 2.0, d['x_in_max'], y - 2.5, y + 2.5, z - 2.5, z + 2.5) for (y, z) in d['al_holes']]   # M2.5 너트 (안쪽)
    P['HW_M25_NUTS'] = ('u', *nuts)   # M-005: 안쪽 나사 머리 자리 (같은 상자로 보수적 확인)
    # ---------- 3D 모델 없는 부품 대체 블록 (간섭 검사용) ----------
    B = {}
    B['BLK_J5_RJ45'] = box(d['rj_x'][0], d['rj_x'][1], d['rj_y'][0], d['rj_y'][1], zc - d['rj_h'], zc)
    B['BLK_J5_PLUG'] = box(rjc - 11.7 / 2, rjc + 11.7 / 2, d['rj_y'][0] - 30, d['rj_y'][0] - 0.01, zc - 12.0, zc - 3.0)
    B['BLK_J2_DC'] = box(d['dc_x'][0], d['dc_x'][1], d['dc_y'][0], d['dc_y'][1], zc - d['dc_h'], zc)
    B['BLK_J2_PLUG'] = ycyl(dcx, dcz, d['dc_y'][0] - 30, d['dc_y'][0] - 0.01, 10.0 / 2)
    B['BLK_J3_USBC'] = box(d['usb_x'][0], d['usb_x'][1], d['usb_y'][0], d['usb_y'][1], zc - d['usb_h'], zc)
    B['BLK_J3_PLUG'] = box(d['usb_x'][0] - 30, d['usb_x'][0] - 0.01, uyc - 12.35 / 2, uyc + 12.35 / 2, uzc - 6.5 / 2, uzc + 6.5 / 2)
    zct = d['z_car_top']
    B['BLK_L1_SRP7028A'] = box(-2.191, 4.509, -1.523, 5.077, zct, zct + 2.8)
    B['BLK_CAR_Q3'] = box(-11.59, -9.29, -7.358, -5.258, zct, zct + 0.8)
    B['BLK_CAR_Q4'] = box(3.038, 5.338, 11.447, 13.547, zct, zct + 0.8)
    zfb = d['z_fr_bot']
    B['BLK_FR_X1'] = box(0.95, 3.55, -13.5, -10.5, zfb - 0.9, zfb)
    B['BLK_FR_Q3'] = box(-8.345, -6.245, -8.893, -6.593, zfb - 0.8, zfb)
    B['BLK_FR_Q5'] = box(6.45, 8.55, -9.15, -6.85, zfb - 0.8, zfb)
    B['BLK_FR_Q7'] = box(-5.736, -3.636, -16.336, -14.036, zfb - 0.8, zfb)
    return P, B
