# REN-003 재질 배정 건식 점검 (보드 GLB, `dryrun_glb.py` 출력 — 종료 코드 = 못 가른 색 0)

- 입력: `C:/workspace_python/OpenHW/validation/runtime/vd001/render/mesh` (board_carrier.glb · board_front.glb)
- 규칙: `mechanical/ren003/materials.py` `classify()` → `body` 이면 `PART_RULES`(모델 이름 → 참조 번호)

| 보드 | 모델 (GLB 메시 이름) | 파일 색 (선형) | 재질 | 바디 수 |
|---|---|---|---|---|
| carrier | BTB_ST-BTB-058060-A_2x30_P0.5mm | 0.352 0.352 0.352 a1.00 mNone | conn_black 커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD) | 12 |
| carrier | BarrelJack_Horizontal | 0.019 0.018 0.018 a1.00 mNone | conn_black 커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD) | 33 |
| carrier | BarrelJack_Horizontal | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 42 |
| carrier | CP_Elec_63x54 | 0.019 0.018 0.018 a1.00 mNone | plastic 흑색 플라스틱 (기타) | 20 |
| carrier | CP_Elec_63x54 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 21 |
| carrier | C_0402_1005Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 88 |
| carrier | C_0402_1005Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 220 |
| carrier | C_0603_1608Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 16 |
| carrier | C_0603_1608Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 40 |
| carrier | C_1206_3216Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 40 |
| carrier | C_1206_3216Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 100 |
| carrier | C_1210_3225Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 32 |
| carrier | C_1210_3225Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 80 |
| carrier | D_SMB | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 32 |
| carrier | D_SMB | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 10 |
| carrier | D_SMB | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 40 |
| carrier | D_SOD-123 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 30 |
| carrier | D_SOD-123 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 5 |
| carrier | D_SOD-123 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 24 |
| carrier | D_SOD-323 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 60 |
| carrier | D_SOD-323 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 10 |
| carrier | D_SOD-323 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 48 |
| carrier | Fuse_1206_3216Metric | 0.007 0.008 0.009 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 5 |
| carrier | Fuse_1206_3216Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 18 |
| carrier | Fuse_1206_3216Metric | 0.778 0.770 0.626 a1.00 mNone | tin 부품 리드 주석 도금 | 3 |
| carrier | HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 46 |
| carrier | HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 1 |
| carrier | HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 213 |
| carrier | JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 43 |
| carrier | JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal | 0.778 0.770 0.626 a1.00 mNone | conn_white 커넥터 하우징 백색 나일론 (JST) | 37 |
| carrier | JST_SM06B_GHS_TB | 0.644 0.638 0.571 a1.00 mNone | tin 부품 리드 주석 도금 | 140 |
| carrier | JST_SM06B_GHS_TB | 0.776 0.768 0.624 a1.00 mNone | conn_white 커넥터 하우징 백색 나일론 (JST) | 125 |
| carrier | LED_0603_1608Metric | 0.095 0.420 0.167 a1.00 mNone | led_smd 상태 LED 녹색 확산 몰드 (0603) | 8 |
| carrier | LED_0603_1608Metric | 0.709 0.504 0.210 a1.00 mNone | gold 커넥터 접점 금 도금 | 68 |
| carrier | LED_0603_1608Metric | 0.778 0.770 0.626 a1.00 mNone | tin 부품 리드 주석 도금 | 24 |
| carrier | L_Bourns_SRP7028A_7.3x6.6mm | 0.352 0.352 0.352 a1.00 mNone | ferrite 인덕터 페라이트·몰드 회색 | 12 |
| carrier | RJ45_Hanrun_HR911105A_Horizontal | 0.352 0.352 0.352 a1.00 mNone | shield 커넥터 금속 쉘 (니켈 도금) | 6 |
| carrier | R_0402_1005Metric | 0.007 0.008 0.009 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 110 |
| carrier | R_0402_1005Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 396 |
| carrier | R_0402_1005Metric | 0.778 0.770 0.626 a1.00 mNone | tin 부품 리드 주석 도금 | 66 |
| carrier | R_0603_1608Metric | 0.007 0.008 0.009 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 5 |
| carrier | R_0603_1608Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 18 |
| carrier | R_0603_1608Metric | 0.778 0.770 0.626 a1.00 mNone | tin 부품 리드 주석 도금 | 3 |
| carrier | SOIC-8_3.9x4.9mm_P1.27mm | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 42 |
| carrier | SOIC-8_3.9x4.9mm_P1.27mm | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 1 |
| carrier | SOIC-8_3.9x4.9mm_P1.27mm | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 104 |
| carrier | SOT-23 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 32 |
| carrier | SOT-23 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 1 |
| carrier | SOT-23 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 36 |
| carrier | SOT-23-6 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 76 |
| carrier | SOT-23-6 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 2 |
| carrier | SOT-23-6 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 156 |
| carrier | SOT-523 | 0.352 0.352 0.352 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 24 |
| carrier | SW_SPST_PTS810 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 78 |
| carrier | SW_SPST_PTS810 | 0.221 0.221 0.221 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 18 |
| carrier | SW_SPST_PTS810 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 56 |
| carrier | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | 0.352 0.352 0.352 a1.00 mNone | shield 커넥터 금속 쉘 (니켈 도금) | 12 |
| carrier | USON_10_25x10mm_Pitch05mm | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 12 |
| carrier | USON_10_25x10mm_Pitch05mm | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 4 |
| carrier | USON_10_25x10mm_Pitch05mm | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 120 |
| carrier | carrier_PCB | 0.420 0.450 0.290 a1.00 m0.0 | fr4 FR-4 판 단면 | 58 |
| carrier | carrier_copper | 0.700 0.610 0.000 a1.00 m1.0 | copper 동박 (마스크 밑 배선·비아 — 마스크 너머로 비침) | 7404 |
| carrier | carrier_pad | 0.500 0.500 0.500 a1.00 m1.0 | enig ENIG 금 도금 패드 | 3294 |
| carrier | carrier_silkscreen | 1.000 1.000 1.000 a0.90 m0.0 | silk 실크 흰색 | 268 |
| carrier | carrier_soldermask | 0.063 0.160 0.113 a0.83 m0.0 | mask PCB 녹색 솔더마스크 (LPI 반광) | 2 |
| carrier | carrier_via | 0.700 0.610 0.000 a1.00 m1.0 | copper 동박 (마스크 밑 배선·비아 — 마스크 너머로 비침) | 1016 |
| carrier | microSD_HC_Hirose_DM3AT-SF-PEJM5 | 0.019 0.018 0.018 a1.00 mNone | conn_black 커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD) | 301 |
| carrier | microSD_HC_Hirose_DM3AT-SF-PEJM5 | 0.221 0.221 0.221 a1.00 mNone | shield 커넥터 금속 쉘 (니켈 도금) | 526 |
| carrier | microSD_HC_Hirose_DM3AT-SF-PEJM5 | 0.709 0.504 0.210 a1.00 mNone | gold 커넥터 접점 금 도금 | 110 |
| front | BTB_ST-BTB-058060-B_2x30_P0.5mm | 0.352 0.352 0.352 a1.00 mNone | conn_black 커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD) | 12 |
| front | C_0402_1005Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 144 |
| front | C_0402_1005Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 360 |
| front | C_0603_1608Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 8 |
| front | C_0603_1608Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 20 |
| front | C_1206_3216Metric | 0.119 0.059 0.038 a1.00 mNone | ceramic 세라믹 커패시터 몸체 | 16 |
| front | C_1206_3216Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 40 |
| front | D_SMA | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 32 |
| front | D_SMA | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 10 |
| front | D_SMA | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 40 |
| front | D_SOD-323 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 90 |
| front | D_SOD-323 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 15 |
| front | D_SOD-323 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 72 |
| front | Everlight_ALS-PT19_1.7x0.8mm | 0.352 0.352 0.352 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 12 |
| front | Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm | 0.352 0.352 0.352 a1.00 mNone | conn_black 커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD) | 12 |
| front | JST_SM06B_GHS_TB | 0.644 0.638 0.571 a1.00 mNone | tin 부품 리드 주석 도금 | 140 |
| front | JST_SM06B_GHS_TB | 0.776 0.768 0.624 a1.00 mNone | conn_white 커넥터 하우징 백색 나일론 (JST) | 125 |
| front | L_Bourns_SRN6045TA | 0.061 0.061 0.061 a1.00 mNone | ferrite 인덕터 페라이트·몰드 회색 | 62 |
| front | L_Bourns_SRN6045TA | 0.468 0.154 0.028 a1.00 mNone | copper 동박 (마스크 밑 배선·비아 — 마스크 너머로 비침) | 38 |
| front | L_Bourns_SRN6045TA | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 20 |
| front | Lite-On_LTR-329ALS-01_2x2mm_P1.2mm | 0.352 0.352 0.352 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 12 |
| front | M12_Holder_20mm_CLA216-ICR | 0.352 0.352 0.352 a1.00 mNone | holder M12 홀더 흑색 플라스틱 | 53 |
| front | MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 60 |
| front | MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 2 |
| front | MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 218 |
| front | Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm | 0.352 0.352 0.352 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 12 |
| front | PinHeader_1x02_P254mm_Vertical | 0.019 0.018 0.018 a1.00 mNone | conn_black 커넥터 하우징 흑색 LCP (BTB·DF30·RJ45·microSD) | 16 |
| front | PinHeader_1x02_P254mm_Vertical | 0.709 0.504 0.210 a1.00 mNone | gold 커넥터 접점 금 도금 | 36 |
| front | R_0402_1005Metric | 0.007 0.008 0.009 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 100 |
| front | R_0402_1005Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 360 |
| front | R_0402_1005Metric | 0.778 0.770 0.626 a1.00 mNone | tin 부품 리드 주석 도금 | 60 |
| front | R_1206_3216Metric | 0.007 0.008 0.009 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 10 |
| front | R_1206_3216Metric | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 36 |
| front | R_1206_3216Metric | 0.778 0.770 0.626 a1.00 mNone | tin 부품 리드 주석 도금 | 6 |
| front | SOT-23 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 96 |
| front | SOT-23 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 3 |
| front | SOT-23 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 108 |
| front | SOT-23-5 | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 36 |
| front | SOT-23-5 | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 1 |
| front | SOT-23-5 | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 65 |
| front | SOT-523 | 0.352 0.352 0.352 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 36 |
| front | Vishay_VSMA1085600_3.4x3.4mm | 0.352 0.352 0.352 a1.00 mNone | led IR LED 렌즈 몸체 (투명 실리콘) | 48 |
| front | WSON_8_1EP_2x2mm_P05mm_EP09x16mm | 0.019 0.018 0.018 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 6 |
| front | WSON_8_1EP_2x2mm_P05mm_EP09x16mm | 0.435 0.398 0.316 a1.00 mNone | epoxy IC 흑색 에폭시 몰드 | 2 |
| front | WSON_8_1EP_2x2mm_P05mm_EP09x16mm | 0.645 0.638 0.572 a1.00 mNone | tin 부품 리드 주석 도금 | 54 |
| front | front_PCB | 0.420 0.450 0.290 a1.00 m0.0 | fr4 FR-4 판 단면 | 16 |
| front | front_copper | 0.700 0.610 0.000 a1.00 m1.0 | copper 동박 (마스크 밑 배선·비아 — 마스크 너머로 비침) | 7827 |
| front | front_pad | 0.500 0.500 0.500 a1.00 m1.0 | enig ENIG 금 도금 패드 | 2762 |
| front | front_silkscreen | 1.000 1.000 1.000 a0.90 m0.0 | silk 실크 흰색 | 199 |
| front | front_soldermask | 0.063 0.160 0.113 a0.83 m0.0 | mask PCB 녹색 솔더마스크 (LPI 반광) | 2 |
| front | front_via | 0.700 0.610 0.000 a1.00 m1.0 | copper 동박 (마스크 밑 배선·비아 — 마스크 너머로 비침) | 660 |
