# M-003 외함 매개변수 (단위 mm, 원점 O = 코어 보드 중심·아랫면, +Z = 광축 = 앞)
# 이 파일 하나가 형상의 기준이다. 값을 바꾸고 scripts/02_build.py 를 다시 돌리면 외함이 다시 만들어진다.
# 출처 표기: [pcb] = pcb 레인 6ecfa85 배치 / aebd293 STEP, [M001] = mechanical/stack-reference.md,
#            [DS] = 데이터시트(m003-enclosure.md §2), [가정] = 근거 없는 설계 선택
import math

P = {}
# ---- 적층 (M-001·M-002b) ----
P['btb_h'] = 8.0          # [M001] BTB 결합 높이
P['core_t'] = 1.6         # [M001]
P['brd_t'] = 1.6          # [pcb] 캐리어·전면 두께
P['optic_above_front'] = 29.485   # [M001] 전면 윗면 → 창 안쪽 면 (받침 0.75 + 상면 0.835 + TTL 27.4 + 0.5)
P['led_top_above_front'] = 2.445  # [M001] VSMA 높이
P['led_a_y'] = 16.0       # [pcb] D_IR_A1/A2 y
P['led_b_y'] = -16.5      # [pcb] D_IR_B1/B2 y (DNP)
# ---- 보드 외형·구멍 [pcb] ----
P['brd_x_min'] = -20.0
P['brd_x_max'] = 20.0
P['car_y_min'] = -34.0
P['brd_y_max'] = 20.0
P['fr_y_min'] = -20.0
P['holes'] = [(13.0, 13.0), (13.0, -13.0), (-13.0, 13.0), (-17.0, -17.0)]   # 캐리어·전면 공통 M1.6 NPTH
P['core_holes'] = [(13.0, 13.0), (13.0, -13.0), (-13.0, 13.0)]
# ---- 커넥터 (캐리어 뒷면, 판 아랫면 기준 아래로) ----
P['rj_x'] = (-10.475, 5.565); P['rj_y'] = (-33.455, -12.155); P['rj_h'] = 13.5        # [pcb] fab, [DS] HR911105A 21.30×16.04×13.50
P['rj_open_w'] = 16.54; P['rj_open_h'] = 14.00                                         # [DS] 권장 패널 개구 (PCB 면부터)
P['dc_x'] = (10.68, 19.68); P['dc_y'] = (-33.705, -19.705); P['dc_h'] = 11.0           # [pcb] fab, [DS] XKB 14×9×11
P['dc_axis_below'] = 6.5                                                                # [DS] 구멍 중심 PCB 아래 6.50
P['dc_open_d'] = 10.5                                                                   # [가정] 플러그 오버몰드 Ø≤10 통과
P['usb_x'] = (-19.455, -12.155); P['usb_y'] = (-4.47, 4.47); P['usb_h'] = 3.26        # [pcb] fab, [DS] HRO 7.35×8.94×3.26
P['usb_open_w'] = 12.8; P['usb_open_h'] = 7.0                                           # [가정] USB-C 오버몰드 12.35×6.5 + 여유
P['sd_x'] = (-6.96, 6.91); P['sd_y'] = (3.43, 19.6); P['sd_h'] = 1.78                  # [pcb] KiCad DM3AT 모델 측정
P['sd_slot_w'] = 13.0; P['sd_slot_z'] = (-2.4, 0.2)                                    # [가정] 카드 11×1 + 여유, 판 아랫면 기준
P['btn'] = [(14.5, -6.0), (14.5, 4.0)]                                                  # [pcb] SW1/SW2 PTS810 (뒷면)
P['stat_led'] = [(17.5, 9.0), (17.5, -14.5)]                                            # [pcb] D6/D3 0603 (뒷면)
# ---- 외함 ----
P['t_w'] = 2.0            # [가정] 옆벽 (0.4 노즐 5둘레)
P['t_back'] = 2.5         # [가정] 뒷벽
P['clr'] = 0.5            # [가정] 판–벽 틈
P['back_clr'] = 0.6       # [가정] RJ45 아래끝–뒷벽
P['x_in_min'] = -25.0     # [M002 K20] 하니스 통로 → 외함 −X 안쪽 벽 ≤ −25.0
P['al_gap'] = 0.75        # [M002b] 갭 패드 Tflex P340 1.0t 를 0.75 로 압축
P['al_t'] = 2.0           # [가정] 5052 판
P['led_out_deg'] = 32.0   # [M-003 2차] LED A 바깥쪽(+Y) 빛을 벽이 가리지 않는 각 — VFOV/2 28.5° + 주머니 테두리 여유 (30°면 주머니 위끝이 28.0°에서 자름)
P['step_z0'] = 8.0        # [가정] +Y 벽 45° 단 시작 높이 (microSD 쪽은 보드 가까이)
P['win_t'] = 3.0          # [M001] PMMA
P['ledge_t'] = 1.2        # [가정] 창 받침 턱 두께
P['lens_win_d'] = 20.6    # [가정] 렌즈 창 지름 (창 바깥 면 화각 반경 10.0 + 0.3)
P['lens_ap_d'] = 16.0     # [가정] 턱 개구 (창 안쪽 면 화각 반경 ≤ 6.7)
P['rib_y'] = 12.2         # [가정] 가운데 띠 반폭 (렌즈 창 반경 10.5 + 1.7)
P['b_pocket_y0'] = -28.4  # [가정] B 창 바깥 끝 (나사 자리 확보)
P['lens_tube'] = (9.6, 10.8, 36.8)   # [가정] 렌즈 관 안 반경·바깥 반경·아래 끝 z (머리 Ø18과 반경 0.6, 2.0 겹침)
P['lens_foam'] = (8.2, 9.5, 1.0)     # [가정] 폼 링 안·바깥 반경, 자유 두께 (0.7로 압축)
P['als_in'] = ((-18.5, -15.5), (-1.5, 5.5))   # [pcb] U3 LTR-329 (−17,0) + Q4 PT19 (−17,4.5) 덮는 관 안쪽
P['als_wall'] = 1.0
P['als_gap'] = 1.2        # [가정] 관 아래 끝 – 전면 윗면 (폼 개스킷 1.5t → 1.2)
P['ins_hole_d'] = 4.0; P['ins_len'] = 4.0; P['boss_d'] = 7.2   # [DS] CNC Kitchen M2.5 표준 인서트 (L4.0, 구멍 4.0, 최소 벽 1.6)
P['cov_screws'] = [(-21.4, -8.0), (18.4, 8.0), (-21.4, -32.9), (18.4, -32.9)]  # 덮개 M2.5×8
P['post_d'] = 4.6; P['post_hole'] = 1.9; P['post_cb_d'] = 3.8; P['post_cb_top'] = 3.0   # 적층 기둥 (M1.6×8 뒤에서)
P['tripod'] = (0.0, -4.0); P['tripod_boss_d'] = 14.0; P['tripod_boss_h'] = 6.7; P['tripod_hole_d'] = 8.0  # [가정·미확인] 1/4"-20 인서트
# [M-003 2차 K32] +X 바깥 방열판 (흑색 아노다이즈 Al 6061): 바닥판이 +X 면 바깥을 덮고, 받침대가 창을 지나 안쪽 x_al_in 까지, 세로(Y) 핀
P['hs_y'] = (-36.0, 22.0)          # 바닥판·핀 Y 범위 (중력 방향 길이 58)
P['hs_zpad'] = 0.5                 # 바닥판 z = 외형 z 범위 − 0.5
P['hs_tb'] = 3.0; P['hs_n'] = 9; P['hs_H'] = 20.0; P['hs_t'] = 1.5   # analysis2.py H3 (방열판→공기 5.6 K/W @25°C)
P['hs_ped_clr'] = 0.3              # 받침대 ↔ 벽 창 틈
P['print_tab_w'] = 1.0             # [M-003c] +X 창 가운데 출력용 희생 기둥 폭 (브리지 42 → 20.5 ×2), 조립 ② 전에 잘라냄. 0 이면 없음
P['win_r'] = 0.5                   # [M-003c] PMMA 사각 창 모서리 R (주머니 모서리는 직각 — 출력 모서리 R≈0.2 보다 큼)
P['al_win_y'] = (-28.0, 14.0); P['al_win_z'] = (-19.0, 24.0)  # +X 벽 창
P['al_holes_y'] = (-31.0, 17.0); P['al_holes_z_near'] = (-21.0, 21.0)  # M2.5 관통 + 안쪽 너트 — z 는 가장 가까운 핀 사이 중심으로 맞춤
P['flange'] = ((18.0, 20.0), (-19.5, 19.5), (-4.5, 2.9))       # 방열판 +X 플랜지 (방열판과 일체, 판 아래로) — 캐리어 C_1210 윗끝 z −5.48 위 0.98
P['spr_xy'] = ((-18.0, 20.0), (-19.5, 19.5)); P['spr_gap'] = 1.3; P['spr_t'] = 1.0   # [M002] 방열판 (AL_SPREADER_TAB_PX)
P['pillar_a'] = ((-9.5, 9.5), (16.5, 19.5))                     # [M002b] 기둥 A (일체 보스), 윗면 도피 홈 slot_w × 0.5
P['pillar_b'] = [((-12.0, -6.0), (-19.5, -13.5)), ((6.0, 12.0), (-19.5, -13.5))]
P['b2_notch'] = ((10.9, 12.5), (-15.1, -13.0))                  # [M-003] 기둥·패드 B2 모서리 따냄 — 스탠드오프 (13,−13) 맞모 반경 1.85 + 0.25
P['ins_t'] = 0.75; P['slot_w'] = 1.6; P['slot_d'] = 0.5         # [M002b]
P['ins_pads'] = [((-9.8, 9.8), (16.2, 19.8)), ((-12.3, -6.0), (-19.8, -13.2)), ((6.0, 12.3), (-19.8, -13.2))]
P['spr_j1_win'] = ((-10.0, 10.0), (8.0, 16.0))   # [M002] 방열판 J1(BTB) 창 — J1 짝 외형 x ±8.85, y 9.19…14.41
P['so_clear_d'] = 4.0     # [가정] 방열판 스탠드오프 관통 구멍 (육각 맞모 3.7 + 0.3)
P['so_d'] = 3.2           # M1.6 육각 스탠드오프 대각 근사


def derive(p=P):
    d = dict(p)
    d['z_car_bot'] = -(p['btb_h'] + p['brd_t'])
    d['z_car_top'] = -p['btb_h']
    d['z_fr_bot'] = p['core_t'] + p['btb_h']
    d['z_fr_top'] = d['z_fr_bot'] + p['brd_t']
    d['z_win_in'] = d['z_fr_top'] + p['optic_above_front']
    d['z_bez_in'] = d['z_win_in'] - p['ledge_t']
    d['z_bez_out'] = d['z_win_in'] + p['win_t']
    d['z_led_top'] = d['z_fr_top'] + p['led_top_above_front']
    d['z_back_in'] = d['z_car_bot'] - p['rj_h'] - p['back_clr']
    d['z_back_out'] = d['z_back_in'] - p['t_back']
    d['x_out_min'] = p['x_in_min'] - p['t_w']
    d['x_al_in'] = p['brd_x_max'] + p['al_gap']
    d['x_in_max'] = d['x_al_in'] + p['al_t']
    d['x_out_max'] = d['x_in_max'] + p['t_w']
    d['y_in_min'] = p['car_y_min'] - p['clr']
    d['y_out_min'] = d['y_in_min'] - p['t_w']
    d['y_in_lo'] = p['brd_y_max'] + p['clr']
    d['y_out_lo'] = d['y_in_lo'] + p['t_w']
    rise = d['z_bez_in'] - d['z_led_top']
    d['y_in_hi'] = math.ceil((p['led_a_y'] + rise * math.tan(math.radians(p['led_out_deg']))) * 2) / 2
    d['y_out_hi'] = d['y_in_hi'] + p['t_w']
    # 바깥 방열판
    d['hs_z'] = (d['z_back_out'] + p['hs_zpad'], d['z_bez_out'] - p['hs_zpad'])
    W = d['hs_z'][1] - d['hs_z'][0]
    pitch = (W - p['hs_t']) / (p['hs_n'] - 1)
    d['hs_fin_zc'] = [d['hs_z'][0] + p['hs_t'] / 2 + k * pitch for k in range(p['hs_n'])]
    gaps = [(a + b) / 2 for a, b in zip(d['hs_fin_zc'], d['hs_fin_zc'][1:])]
    d['al_holes'] = [(y, min(gaps, key=lambda gz: abs(gz - z))) for z in p['al_holes_z_near'] for y in p['al_holes_y']]
    d['x_hs_base'] = (d['x_out_max'], d['x_out_max'] + p['hs_tb'])
    d['x_hs_tip'] = d['x_hs_base'][1] + p['hs_H']
    return d
