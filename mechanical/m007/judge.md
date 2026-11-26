# M-007 기계 판정 = VD-001 조건 5 (run_all.py 출력 — 종료 코드 = 불합격 항목 수 7: 03_judge 실패 4 + 3D 모델 빠짐 보드 2 + J3 삽입 1)

- 결과 파일 validation/runtime/vd001/results/cond5-mechanical.json (docs/review/vd001-format.md §1)
- kicad-cli carrier rc 0, 3D 모델 빠짐 5 J3 J5 L1 Q3 Q4
- kicad-cli front rc 0, 3D 모델 빠짐 4 Q3 Q5 Q7 X1
- pcb commit 23fd8da
- 3D 모델 전수 감사 (mechanical/ren002/audit_models.py) 빠짐 캐리어 6 · 전면 13
- 커넥터 (pcb fab): {"rj_x": [-10.475, 5.565], "rj_y": [-33.455, -12.155], "dc_x": [10.68, 19.68], "dc_y": [-33.705, -19.705], "usb_x": [-19.455, -12.155], "usb_y": [-4.47, 4.47], "sd_x": [-6.955, 6.895], "sd_y": [3.44, 19.6], "sd_front": [19.6]}
- 02_assembly rc 0 ASSEMBLY True d2e4da4fc8f284c8ad4939679b0ccf7093b580244a8a864681784f316a05745f harness path 24.72 slack 10.28
BOARDS {'carrier': 'c5ebfefc22ed596f365c26623ef18683155d6cafd213d5ef8260d89b093a31fd', 'front': '5d284b82d6be93c30fc345bc999845148a2182d0f8fdf2955c8df4a488b448e8'}
- 03_judge rc 0 JUDGE fail 4

## J1 바디 쌍 간섭 (바디 180개)

| 쌍 | 부피 mm³ | 위치 x/y/z | 판정 |
|---|---|---|---|
| BLK_J3_PLUG ↔ BOARD_PART | 9.719 | [-20.0, -19.47, -6.18, 6.17, -9.6, -8.13] | **실패** |
| SPACER_M008 ↔ BOARD_PART | 0.152 | [-3.58, -2.58, 10.02, 10.52, 11.2, 11.51] | **실패** |
| SPACER_M008 ↔ BOARD_PART | 0.152 | [-6.57, -5.57, 10.07, 10.57, 11.2, 11.51] | **실패** |
| SPACER_M008 ↔ BOARD_PART | 0.152 | [-0.7, 0.3, 10.04, 10.54, 11.2, 11.51] | **실패** |
| CORE_BOT_KEEPIN ↔ J2_MATED_ENVELOPE | 115.970 | [9.2, 14.4, -8.85, 8.85, -1.26, 0.0] | 의도 — 코어 아랫면 keep-in 이 짝 BTB 를 덮음 (M-001) |
| CORE_BOT_KEEPIN ↔ HW_STANDOFFS | 30.401 | [-14.6, 14.6, -14.6, 14.6, -1.26, 0.0] | 의도 — keep-in 덩어리가 코어 장착 구멍 자리를 덮음 (M-003 §7, M-006 스탠드오프 실제 모델 간섭 0) |
| CORE_TOP_KEEPIN ↔ J1_MATED_ENVELOPE | 85.002 | [-8.85, 8.85, 9.19, 14.41, 1.6, 2.52] | 의도 — 코어 윗면 keep-in 이 짝 BTB 를 덮음 (M-001) |
| CORE_TOP_KEEPIN ↔ HW_STANDOFFS | 22.197 | [-14.6, 14.6, -14.6, 14.6, 1.6, 2.52] | 의도 — 위와 같음 |
| HARNESS_CORRIDOR_MX ↔ BLK_J3_PLUG | 0.314 | [-24.75, -19.47, -6.18, -3.2, -8.0, -7.98] | 의도 — z 0.02 맞닿음 수준 (M-003 §7) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W1 | 19.156 | [-24.7, -21.0, -29.55, -12.45, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W2 | 19.156 | [-24.7, -21.0, -27.95, -10.85, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W3 | 19.156 | [-24.7, -21.0, -26.35, -9.25, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W4 | 19.156 | [-24.7, -21.0, -24.75, -7.65, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W5 | 19.156 | [-24.7, -21.0, -23.15, -6.05, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| HARNESS_CORRIDOR_MX ↔ HARNESS_GH6P_W6 | 19.156 | [-24.7, -21.0, -21.55, -4.45, -6.38, 7.97] | 의도 — 하니스가 하니스 통로 안을 지남 (통로는 자리 표시) |
| BLK_J2_DC ↔ BOARD_PART | 620.815 | [10.68, 19.68, -33.7, -20.11, -20.38, -9.6] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_DC ↔ BOARD_PART | 48.906 | [12.54, 17.82, -33.7, -19.7, -18.73, -9.6] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_DC ↔ BOARD_PART | 17.164 | [12.68, 17.68, -32.58, -22.55, -13.22, -9.62] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_DC ↔ BOARD_PART | 2.568 | [10.68, 17.1, -24.1, -22.1, -13.48, -13.29] | 의도 — DC 잭: KiCad 일반 BarrelJack 모델 ↔ XKB 대체 블록 (같은 부품) |
| BLK_J2_PLUG ↔ BOARD_PART | 3.744 | [10.68, 19.68, -33.8, -33.71, -20.38, -11.1] | 의도 — DC 잭 일반 모델 앞면이 XKB 앞면보다 0.1 나옴 (같은 부품) |
| BLK_J2_PLUG ↔ BOARD_PART | 0.106 | [14.59, 15.77, -33.91, -33.71, -16.67, -15.5] | 의도 — DC 잭 일반 모델 앞면이 XKB 앞면보다 0.1 나옴 (같은 부품) |
| ICR_LEAD_M008 ↔ ICR_PADS_M008 | 0.004 | [15.62, 15.92, 8.69, 9.86, 11.5, 11.7] | 의도 — 리드 끝이 납땜 패드에 붙음 |

## J2 최소 틈

| 쌍 | 최소 틈 mm | 기준 | 판정 |
|---|---|---|---|
| LENS_CIL093 ↔ FRONT_COVER | 0.6 | ≥ 0.3 | 통과 |
| LENS_CIL093 ↔ LENS_WIN_PMMA | 0.5 | ≥ 0.3 | 통과 |
| HS_PEDESTAL ↔ HOUSING | 0.3 | ≥ 0.2 | 통과 |
| SPREADER_M003 ↔ HOUSING | 1.0 | ≥ 0.3 | 통과 |
| HARNESS_GH6P ↔ HOUSING | 0.3 | ≥ 0.1 | 통과 |
| HARNESS_GH6P ↔ SPREADER_M003 | 4.296 | ≥ 0.1 | 통과 |
| BLK_J3_PLUG ↔ HOUSING | 0.225 | ≥ 0.0 | 통과 |
| BLK_J5_PLUG ↔ HOUSING | 2.0 | ≥ 0.0 | 통과 |
| BLK_J2_PLUG ↔ HOUSING | 0.25 | ≥ 0.0 | 통과 |
| BLK_J4_CARD ↔ HOUSING | 0.65 | ≥ 0.0 | 통과 |
| FOAM_ALS_GASKET ↔ FRONT_COVER | 0.0 | ≥ -0.01 | 통과 |
| LED_A1 ↔ FRONT_COVER | 10.348 | ≥ 1.0 | 통과 |
| CLA216_M008 ↔ LED_A1 | 2.65 | ≥ 1.0 | 통과 |
| CLA216_M008 ↔ LED_A2 | 2.65 | ≥ 1.0 | 통과 |
| DF30_M008 ↔ LED_B1 | 2.173 | ≥ 1.0 | 통과 |

## J3 플러그·카드 삽입 공간

- 플러그/카드 블록이 낀 실패 간섭: 1건

## J4 광축 ↔ 렌즈 창 중심

- 렌즈 [0.0, 0.0] · 창 [0.0, 0.0] · 어긋남 0.000 mm → 통과

## J5 LED 직접광 (광선 추적, LED A+B, 시야 19 × 13 방향)

- 직접광이 닿는 방향 97.6 % (기준 86 %, analysis2 · O-69) → 통과
- 막은 바디(LED·방향 수): {'HOUSING': 200, 'FRONT_COVER': 254, 'LENS_CIL093': 66, 'FOAM_LENS_RING': 2}

## J6 짝 BTB 결합 높이

- 코어 ↔ 캐리어 윗면 8.000 · 전면 아랫면 ↔ 코어 윗면 8.000 (기대 8.0) → 통과 · M-006: 3D 모델은 단순화라 결합 높이 판정 불가 → 3사 높이표 8.00

## 입력·산출 해시

- m007_assembly.step d2e4da4fc8f284c8ad4939679b0ccf7093b580244a8a864681784f316a05745f
- boards/carrier.step c5ebfefc22ed596f365c26623ef18683155d6cafd213d5ef8260d89b093a31fd
- boards/front.step 5d284b82d6be93c30fc345bc999845148a2182d0f8fdf2955c8df4a488b448e8
