# M-007 기계 판정 = VD-001 조건 5 (run_all.py 출력 — 종료 코드 = 불합격 항목 수 0: 03_judge 실패 0 + 3D 모델 빠짐 보드 0 + J3 삽입 0)

- 결과 파일 validation/runtime/vd001/results/cond5-mechanical.json (docs/review/vd001-format.md §1)
- carrier pcb 995b872: 원본 3D 모델 빠짐 0 · apply_models 사본 changed footprints 0
- kicad-cli carrier rc 0 (사본 감사 빠짐 0 , kicad-cli 경고 0 )
- front pcb 995b872: 원본 3D 모델 빠짐 0 · apply_models 사본 changed footprints 0
- kicad-cli front rc 0 (사본 감사 빠짐 0 , kicad-cli 경고 0 )
- pcb commit 995b872
- 커넥터 (pcb fab): {"rj_x": [-10.475, 5.565], "rj_y": [-33.455, -12.155], "dc_x": [10.68, 19.68], "dc_y": [-33.705, -19.705], "usb_x": [-20.455, -13.155], "usb_y": [-4.47, 4.47], "sd_x": [-6.955, 6.895], "sd_y": [3.44, 19.6], "sd_front": [19.6]}
- 02_assembly rc 0 CASE_A bodies 22
ASSEMBLY True 81c176c09e78482412b620b7faed40636e3a2bc9821e7087e75ff339d9000f97 harness path 24.72 slack 10.28
BOARDS {'carrier': '1ffaa95243bd6aed808604b8124904d5bb51abfedf846b2d1c5974491270640d', 'front': '2657c02ec6d086e74ac5bd59fc63b3bb8894bd2b52130f3526b7ff45280740d3'}
- 03_judge rc 0 JUDGE fail 0

- 판정에서 뺀 대체 블록 (그 보드 3D 모델 연결 사본 감사 빠짐 0 — asm_spec.SUBST_BLOCKS): BLK_J5_RJ45 BLK_J3_USBC BLK_L1_SRP7028A BLK_CAR_Q3 BLK_CAR_Q4 BLK_FR_X1 BLK_FR_Q3 BLK_FR_Q5 BLK_FR_Q7

## J1 바디 쌍 간섭 (바디 229개)

| 쌍 | 부피 mm³ | 위치 x/y/z | 판정 |
|---|---|---|---|
| CORE_BOT_KEEPIN ↔ J2_MATED_ENVELOPE | 115.970 | [9.2, 14.4, -8.85, 8.85, -1.26, 0.0] | 의도 — 코어 아랫면 keep-in 이 짝 BTB 를 덮음 (M-001) |
| CORE_BOT_KEEPIN ↔ HW_STANDOFFS | 30.401 | [-14.6, 14.6, -14.6, 14.6, -1.26, 0.0] | 의도 — keep-in 덩어리가 코어 장착 구멍 자리를 덮음 (M-003 §7, M-006 스탠드오프 실제 모델 간섭 0) |
| J2_MATED_ENVELOPE ↔ BOARD_PART:BTB_ST-BTB-058060-A_2x30_P0.5mm | 308.093 | [9.6, 14.0, -8.85, 8.85, -8.0, -4.04] | 의도 — 짝 BTB 외형 ↔ 캐리어 J1 플러그 모델 (같은 부품) |
| J2_MATED_ENVELOPE ↔ BOARD_PART:BTB_ST-BTB-058060-A_2x30_P0.5mm | 8.130 | [9.2, 14.4, -7.38, 7.38, -8.0, -7.89] | 의도 — 짝 BTB 외형 ↔ 캐리어 J1 플러그 모델 (같은 부품) |
| CORE_TOP_KEEPIN ↔ J1_MATED_ENVELOPE | 85.002 | [-8.85, 8.85, 9.19, 14.41, 1.6, 2.52] | 의도 — 코어 윗면 keep-in 이 짝 BTB 를 덮음 (M-001) |
| CORE_TOP_KEEPIN ↔ HW_STANDOFFS | 22.197 | [-14.6, 14.6, -14.6, 14.6, 1.6, 2.52] | 의도 — 위와 같음 |
| J1_MATED_ENVELOPE ↔ BOARD_PART:BTB_ST-BTB-058060-B_2x30_P0.5mm | 311.520 | [-8.85, 8.85, 9.6, 14.0, 5.51, 9.52] | 의도 — 짝 BTB 외형 ↔ 전면 J1 소켓 모델 (같은 부품) |
| J1_MATED_ENVELOPE ↔ BOARD_PART:BTB_ST-BTB-058060-B_2x30_P0.5mm | 11.549 | [-7.38, 7.38, 9.19, 14.41, 9.37, 9.52] | 의도 — 짝 BTB 외형 ↔ 전면 J1 소켓 모델 (같은 부품) |
| LED_A1 ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 27.756 | [-7.7, -4.3, 14.3, 17.7, 11.2, 13.6] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_A1 ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 1.225 | [-7.7, -4.3, 14.3, 17.7, 11.2, 11.31] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_A2 ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 27.756 | [4.3, 7.7, 14.3, 17.7, 11.2, 13.6] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_A2 ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 1.225 | [4.3, 7.7, 14.3, 17.7, 11.2, 11.31] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_B1_DNP ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 27.756 | [-9.2, -5.8, -18.2, -14.8, 11.2, 13.6] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_B1_DNP ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 1.225 | [-9.2, -5.8, -18.2, -14.8, 11.2, 11.31] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_B2_DNP ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 27.756 | [5.8, 9.2, -18.2, -14.8, 11.2, 13.6] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| LED_B2_DNP ↔ BOARD_PART:Vishay_VSMA1085600_3.4x3.4mm | 1.225 | [5.8, 9.2, -18.2, -14.8, 11.2, 11.31] | 의도 — IR LED 자리 표시 ↔ 전면 D_IR VSMA 모델 (같은 부품) |
| HARNESS_CORRIDOR_MX ↔ BLK_J3_PLUG | 0.255 | [-24.75, -20.46, -6.18, -3.2, -8.0, -7.98] | 의도 — z 0.02 맞닿음 수준 (M-003 §7) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W1 | 19.156 | [-24.7, -21.0, -29.55, -12.45, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W2 | 19.156 | [-24.7, -21.0, -27.95, -10.85, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W3 | 19.156 | [-24.7, -21.0, -26.35, -9.25, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W4 | 19.156 | [-24.7, -21.0, -24.75, -7.65, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W5 | 19.156 | [-24.7, -21.0, -23.15, -6.05, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W6 | 19.156 | [-24.7, -21.0, -21.55, -4.45, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| COVER_USBC ↔ BLK_J3_PLUG | 224.770 | [-27.8, -25.0, -6.18, 6.18, -14.48, -7.98] | 의도 — USB-C 정비 덮개는 플러그를 꽂을 때 뺌 (삽입 공간과 겹치는 것이 정상) |
| COVER_MICROSD ↔ BLK_J4_CARD | 30.800 | [-5.53, 5.47, 33.5, 36.3, -11.05, -10.05] | 의도 — microSD 정비 덮개는 카드를 넣을 때 뺌 |
| BLK_J2_DC ↔ BOARD_PART:BarrelJack_Horizontal | 620.815 | [10.68, 19.68, -33.7, -20.11, -20.38, -9.6] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_DC ↔ BOARD_PART:BarrelJack_Horizontal | 48.906 | [12.54, 17.82, -33.7, -19.7, -18.73, -9.6] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_DC ↔ BOARD_PART:BarrelJack_Horizontal | 17.164 | [12.68, 17.68, -32.58, -22.55, -13.22, -9.62] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_DC ↔ BOARD_PART:BarrelJack_Horizontal | 2.568 | [10.68, 17.1, -24.1, -22.1, -13.48, -13.29] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_PLUG ↔ BOARD_PART:BarrelJack_Horizontal | 3.744 | [10.68, 19.68, -33.8, -33.71, -20.38, -11.1] | 의도 — DC 잭 일반 모델 앞면이 XKB 앞면보다 0.1 나옴 (같은 부품) |
| BLK_J2_PLUG ↔ BOARD_PART:BarrelJack_Horizontal | 0.106 | [14.59, 15.77, -33.91, -33.71, -16.67, -15.5] | 의도 — DC 잭 일반 모델 앞면이 XKB 앞면보다 0.1 나옴 (같은 부품) |
| CLA216_M008 ↔ BOARD_PART:M12_Holder_20mm_CLA216-ICR | 1608.827 | [-12.2, 12.2, -8.65, 11.65, 12.7, 20.26] | 의도 — M-008 홀더 ↔ 전면 MH1 홀더 모델 (REN-002 모델 = 같은 M-008 형상) |
| SPACER_M008 ↔ BOARD_PART:M12_Holder_20mm_CLA216-ICR | 219.010 | [-12.2, 12.2, -8.65, 11.65, 11.2, 12.66] | 의도 — M-008 스페이서 ↔ MH1 모델 (같은 부품) |
| SPACER_M008 ↔ BOARD_PART:M12_Holder_20mm_CLA216-ICR | 7.124 | [-12.2, 12.2, -8.65, 11.65, 12.66, 12.7] | 의도 — M-008 스페이서 ↔ MH1 모델 (같은 부품) |
| ICR_LEAD_M008 ↔ ICR_PADS_M008 | 0.004 | [15.62, 15.92, 8.69, 9.86, 11.5, 11.7] | 의도 — 리드 끝이 납땜 패드에 붙음 |
| ICR_LEAD_M008 ↔ BOARD_PART:M12_Holder_20mm_CLA216-ICR | 9.265 | [7.95, 16.37, 8.67, 9.9, 11.34, 14.06] | 의도 — ICR 리드 ↔ MH1 모델의 리드 (같은 부품) |
| ICR_PADS_M008 ↔ BOARD_PART:M12_Holder_20mm_CLA216-ICR | 0.007 | [15.6, 15.96, 8.68, 9.87, 11.46, 11.7] | 의도 — 납땜 패드 ↔ MH1 모델 리드 끝 (같은 부품) |
| DF30_M008 ↔ BOARD_PART:Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm | 22.092 | [-3.48, 3.48, -13.4, -9.7, 11.2, 12.06] | 의도 — DF30 결합 외형 ↔ 전면 J3 모델 (같은 부품) |
| DF30_M008 ↔ BOARD_PART:Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm | 2.356 | [-2.32, 2.31, -13.95, -9.15, 11.2, 11.31] | 의도 — DF30 결합 외형 ↔ 전면 J3 모델 (같은 부품) |

## J2 최소 틈

| 쌍 | 최소 틈 mm | 기준 | 판정 |
|---|---|---|---|
| LENS_CIL093 ↔ LENS_WIN_CLEAR | 1.515 | ≥ 0.3 | 통과 |
| LENS_CIL093 ↔ GLASS_MASK | 3.101 | ≥ 0.3 | 통과 |
| LENS_CIL093 ↔ INNER_MASK_PLATE | 3.204 | ≥ 0.3 | 통과 |
| CLA216_M008 ↔ INNER_MASK_PLATE | 0.5 | ≥ 0.3 | 통과 |
| HW_M16_HEADS ↔ INNER_MASK_PLATE | 1.8 | ≥ 0.2 | 통과 |
| LED_A1 ↔ INNER_MASK_PLATE | 1.692 | ≥ 0.5 | 통과 |
| SPREADER_M003 ↔ SHELL_ALU | 0.75 | ≥ 0.3 | 통과 |
| HARNESS_GH6P ↔ SHELL | 0.3 | ≥ 0.1 | 통과 |
| HARNESS_GH6P ↔ SPREADER_M003 | 4.296 | ≥ 0.1 | 통과 |
| BLK_J3_PLUG ↔ SHELL | 0.3 | ≥ 0.0 | 통과 |
| BLK_J5_PLUG ↔ SHELL | 2.0 | ≥ 0.0 | 통과 |
| BLK_J2_PLUG ↔ SHELL | 0.1 | ≥ 0.0 | 통과 |
| BLK_J4_CARD ↔ SHELL | 0.25 | ≥ 0.0 | 통과 |
| BLK_J5_PLUG ↔ CABLE_GROMMET | 0.5 | ≥ 0.0 | 통과 |
| BLK_J2_PLUG ↔ CABLE_GROMMET | 0.5 | ≥ 0.0 | 통과 |
| BLK_J5_PLUG ↔ WALL_BRACKET | 12.745 | ≥ 0.0 | 통과 |
| BLK_J2_PLUG ↔ WALL_BRACKET | 13.526 | ≥ 0.0 | 통과 |
| CLA216_M008 ↔ LED_A1 | 2.65 | ≥ 1.0 | 통과 |
| CLA216_M008 ↔ LED_A2 | 2.65 | ≥ 1.0 | 통과 |
| DF30_M008 ↔ LED_B1 | 2.173 | ≥ 1.0 | 통과 |

## J3 플러그·카드 삽입 공간

- 플러그/카드 블록이 낀 실패 간섭: 0건

## J4 광축 ↔ 렌즈 창 중심

- 렌즈 [0.0, 0.0] · 창 [0.0, 0.0] · 어긋남 0.000 mm → 통과

## J5 LED 직접광 (광선 추적, LED A+B, 시야 19 × 13 방향)

- 직접광이 닿는 방향 100.0 % (기준 86 %, analysis2 · O-69) → 통과
- 막은 바디(LED·방향 수): {'SHELL_PLASTIC': 182, 'GLASS_MASK': 290, 'LENS_CIL093': 66}

## J6 짝 BTB 결합 높이

- 코어 ↔ 캐리어 윗면 8.000 · 전면 아랫면 ↔ 코어 윗면 8.000 (기대 8.0) → 통과 · M-006: 3D 모델은 단순화라 결합 높이 판정 불가 → 3사 높이표 8.00

## 입력·산출 해시

- m007_assembly.step 81c176c09e78482412b620b7faed40636e3a2bc9821e7087e75ff339d9000f97
- boards/carrier.step 1ffaa95243bd6aed808604b8124904d5bb51abfedf846b2d1c5974491270640d
- boards/front.step 2657c02ec6d086e74ac5bd59fc63b3bb8894bd2b52130f3526b7ff45280740d3
