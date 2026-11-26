# REN-002 3D 모델 전수 감사 (audit_models.py — pcb 23fd8da, 빠짐 19 / 풋프린트 192)

- 풀림 규칙: `${KICAD10_3DMODEL_DIR}` = KiCad 10.0 설치 `share/kicad/3dmodels`, `${KIPRJMOD}` = 보드 폴더, .wrl → 같은 이름 .step.
- 상태: ok · 경로 없음(풋프린트에 model 속성 없음) · file not found · unset variable · 숨김 · 모델 불필요(board_only, 구멍·테스트 점·기점)

| 보드 | 참조 | 값 | 풋프린트 | 면 | 모델 경로 | 상태 |
|---|---|---|---|---|---|---|
| carrier | J1 | HC-PBB05-2-60-M-H4.0 (ST-BTB-058060-A) | openhw:BTB_ST-BTB-058060-A_2x30_P0.5mm | F | — | **경로 없음** |
| carrier | J3 | USB-C 16P | Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12 | B | `${KICAD10_3DMODEL_DIR}/Connector_USB.3dshapes/USB_C_Receptacle_HRO_TYPE-C-31-M-12.step` | **file not found** |
| carrier | J5 | HR911105A | Connector_RJ:RJ45_Hanrun_HR911105A_Horizontal | B | `${KICAD10_3DMODEL_DIR}/Connector_RJ.3dshapes/RJ45_Hanrun_HR911105A_Horizontal.step` | **file not found** |
| carrier | L1 | 10uH Isat>=6A | Inductor_SMD:L_Bourns_SRP7028A_7.3x6.6mm | F | `${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_Bourns_SRP7028A_7.3x6.6mm.step` | **file not found** |
| carrier | Q3 | DMG1012T | Package_TO_SOT_SMD:SOT-523 | F | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-523.step` | **file not found** |
| carrier | Q4 | DMG1012T | Package_TO_SOT_SMD:SOT-523 | F | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-523.step` | **file not found** |
| front | D_IR_A1 | VSMA1085400 | openhw:Vishay_VSMA1085600_3.4x3.4mm | F | — | **경로 없음** |
| front | D_IR_A2 | VSMA1085400 | openhw:Vishay_VSMA1085600_3.4x3.4mm | F | — | **경로 없음** |
| front | D_IR_B1 | VSMA1085400 | openhw:Vishay_VSMA1085600_3.4x3.4mm | F | — | **경로 없음** |
| front | D_IR_B2 | VSMA1085400 | openhw:Vishay_VSMA1085600_3.4x3.4mm | F | — | **경로 없음** |
| front | J1 | HC-PBB05-2-60-F-H4.0 (ST-BTB-058060-B) | openhw:BTB_ST-BTB-058060-B_2x30_P0.5mm | B | — | **경로 없음** |
| front | J3 | DF30FC-24DS-0.4V(81) | openhw:Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm | F | — | **경로 없음** |
| front | MH1 | CLA216-ICR M12 holder | openhw:M12_Holder_20mm_CLA216-ICR | F | — | **경로 없음** |
| front | Q3 | DMG1012T | Package_TO_SOT_SMD:SOT-523 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-523.step` | **file not found** |
| front | Q4 | ALS-PT19 (alt) | openhw:Everlight_ALS-PT19_1.7x0.8mm | F | — | **경로 없음** |
| front | Q5 | DMG1012T | Package_TO_SOT_SMD:SOT-523 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-523.step` | **file not found** |
| front | Q7 | DMG1012T | Package_TO_SOT_SMD:SOT-523 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-523.step` | **file not found** |
| front | U3 | LTR-329ALS-01 | openhw:Lite-On_LTR-329ALS-01_2x2mm_P1.2mm | F | — | **경로 없음** |
| front | X1 | OT7EL89CJI-111YLC-24M | Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm | B | `${KICAD10_3DMODEL_DIR}/Oscillator.3dshapes/Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm.step` | **file not found** |
| carrier | C1 | 47uF/35V | Capacitor_SMD:CP_Elec_6.3x5.4 | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/CP_Elec_6.3x5.4.step` | ok |
| carrier | C10 | 1uF/25V | Capacitor_SMD:C_0603_1608Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0603_1608Metric.step` | ok |
| carrier | C11 | 10uF/25V | Capacitor_SMD:C_1206_3216Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| carrier | C12 | 1uF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C13 | 1uF | Capacitor_SMD:C_0603_1608Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0603_1608Metric.step` | ok |
| carrier | C14 | 100nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C15 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C16 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C17 | 1nF/2kV | Capacitor_SMD:C_1206_3216Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| carrier | C18 | 10nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C19 | 75pF C0G 50V | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C2 | 10uF/25V | Capacitor_SMD:C_1206_3216Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| carrier | C20 | 22uF/25V X7R | Capacitor_SMD:C_1210_3225Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1210_3225Metric.step` | ok |
| carrier | C21 | 100nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C22 | 10nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C23 | 22uF/25V X7R | Capacitor_SMD:C_1210_3225Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1210_3225Metric.step` | ok |
| carrier | C3 | 10uF/25V | Capacitor_SMD:C_1206_3216Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| carrier | C4 | 10uF/25V | Capacitor_SMD:C_1206_3216Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| carrier | C5 | 100nF/50V | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C6 | 100nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | C7 | 22uF/25V X7R | Capacitor_SMD:C_1210_3225Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1210_3225Metric.step` | ok |
| carrier | C8 | 22uF/25V X7R | Capacitor_SMD:C_1210_3225Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1210_3225Metric.step` | ok |
| carrier | C9 | 22nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| carrier | D1 | BZT52C12 | Diode_SMD:D_SOD-123 | F | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SOD-123.step` | ok |
| carrier | D2 | SMBJ15A | Diode_SMD:D_SMB | F | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SMB.step` | ok |
| carrier | D3 | PWR green | LED_SMD:LED_0603_1608Metric | B | `${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_0603_1608Metric.step` | ok |
| carrier | D4 | UDD32C03L01 | Diode_SMD:D_SOD-323 | F | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SOD-323.step` | ok |
| carrier | D5 | UDD32C03L01 | Diode_SMD:D_SOD-323 | F | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SOD-323.step` | ok |
| carrier | D6 | STATUS blue | LED_SMD:LED_0603_1608Metric | B | `${KICAD10_3DMODEL_DIR}/LED_SMD.3dshapes/LED_0603_1608Metric.step` | ok |
| carrier | D7 | SMBJ6.0A | Diode_SMD:D_SMB | F | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SMB.step` | ok |
| carrier | F1 | 3A slow-blow 63V | Fuse:Fuse_1206_3216Metric | F | `${KICAD10_3DMODEL_DIR}/Fuse.3dshapes/Fuse_1206_3216Metric.step` | ok |
| carrier | H1 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| carrier | H2 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| carrier | H3 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| carrier | H4 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| carrier | J2 | DC-005-5A-2.0 | openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal | B | `${KICAD10_3DMODEL_DIR}/Connector_BarrelJack.3dshapes/BarrelJack_Horizontal.step` | ok |
| carrier | J4 | DM3AT-SF-PEJM5 | Connector_Card:microSD_HC_Hirose_DM3AT-SF-PEJM5 | B | `${KICAD10_3DMODEL_DIR}/Connector_Card.3dshapes/microSD_HC_Hirose_DM3AT-SF-PEJM5.step` | ok |
| carrier | J6 | DEBUG UART | Connector_JST:JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal | B | `${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_SH_SM03B-SRSS-TB_1x03-1MP_P1.00mm_Horizontal.step` | ok |
| carrier | J7 | JST GH 6P (board link) | Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal | F | `${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal.step` | ok |
| carrier | Q1 | AO4407A | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm | F | `${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/SOIC-8_3.9x4.9mm_P1.27mm.step` | ok |
| carrier | Q2 | AO3401A | Package_TO_SOT_SMD:SOT-23 | F | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23.step` | ok |
| carrier | R1 | 100k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R10 | 100k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R11 | 100k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R12 | 100k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R13 | 47k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R14 | 47k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R15 | 47k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R16 | 47k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R17 | 47k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R18 | 1M | Resistor_SMD:R_0603_1608Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0603_1608Metric.step` | ok |
| carrier | R19 | 1k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R2 | 100k 1% | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R20 | 100k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R21 | 1.5k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R22 | 47k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R23 | 100k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R3 | 13.3k 1% | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R4 | 2.2k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R5 | 10k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R6 | 8.06k 1% | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R7 | 5.1k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R8 | 5.1k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | R9 | 200k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| carrier | SW1 | RESET | Button_Switch_SMD:SW_SPST_PTS810 | B | `${KICAD10_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_SPST_PTS810.step` | ok |
| carrier | SW2 | UPGRADE | Button_Switch_SMD:SW_SPST_PTS810 | B | `${KICAD10_3DMODEL_DIR}/Button_Switch_SMD.3dshapes/SW_SPST_PTS810.step` | ok |
| carrier | TP1 | 12V_IN | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP10 | USB_DET | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP11 | nRESET | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP12 | UPGRAD_KEY | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP13 | STATUS_LED | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP14 | IR_LED_EN | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP15 | SPARE1 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP16 | I2C1_SDA | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP17 | I2C1_SCL | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP18 | RESERVE1 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP19 | RESERVE2 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP2 | 5V_SYS | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP20 | UART1_RX | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP21 | UART1_TX | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP22 | UART1_CTS | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP23 | UART1_RTS | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP24 | DEBUG_UART0_TX | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP25 | DEBUG_UART0_RX | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP26 | ALS_INT_RSV | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP3 | 12V_IR | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP4 | CORE_3V3 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP5 | SD_PWR_3V3 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP6 | GND | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP7 | GND | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| carrier | TP8 | USB_DP | TestPoint:TestPoint_Pad_D1.0mm | F | — | 모델 불필요 |
| carrier | TP9 | USB_DN | TestPoint:TestPoint_Pad_D1.0mm | F | — | 모델 불필요 |
| carrier | U1 | TPS54302DDCR | Package_TO_SOT_SMD:SOT-23-6 | F | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-6.step` | ok |
| carrier | U2 | TPS26600PWPR | Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm_ThermalVias | F | `${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm.step` | ok |
| carrier | U3 | USBLC6-2SC6 | Package_TO_SOT_SMD:SOT-23-6 | F | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-6.step` | ok |
| carrier | U4 | TPD4E05U06DQA | Package_SON:USON-10_2.5x1.0mm_P0.5mm | F | `${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/USON-10_2.5x1.0mm_P0.5mm.step` | ok |
| carrier | U5 | TPD4E05U06DQA | Package_SON:USON-10_2.5x1.0mm_P0.5mm | F | `${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/USON-10_2.5x1.0mm_P0.5mm.step` | ok |
| front | C1 | 1uF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C10 | 100nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C11 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C12 | 1uF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C13 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C14 | 10uF/50V X7R | Capacitor_SMD:C_1206_3216Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| front | C15 | 100nF/50V | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C16 | 10uF/50V X7R | Capacitor_SMD:C_1206_3216Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_1206_3216Metric.step` | ok |
| front | C17 | 100nF/50V | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C18 | 1uF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C2 | 1uF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C3 | 10uF | Capacitor_SMD:C_0603_1608Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0603_1608Metric.step` | ok |
| front | C4 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C5 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C6 | 100nF | Capacitor_SMD:C_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C7 | 1uF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C8 | 1uF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | C9 | 100nF | Capacitor_SMD:C_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Capacitor_SMD.3dshapes/C_0402_1005Metric.step` | ok |
| front | D1 | SS24 (40V 2A, SMA) | Diode_SMD:D_SMA | B | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SMA.step` | ok |
| front | D2 | SS24 (40V 2A, SMA) | Diode_SMD:D_SMA | B | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SMA.step` | ok |
| front | D3 | BAT54WS | Diode_SMD:D_SOD-323 | B | `${KICAD10_3DMODEL_DIR}/Diode_SMD.3dshapes/D_SOD-323.step` | ok |
| front | H1 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| front | H2 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| front | H3 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| front | H4 | M1.6 | OpenHW_Mech:MountingHole_M1.6_NPTH | F | — | 모델 불필요 |
| front | J2 | PicoBlade 53261-0271 (CLA216 lead) | Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal | F | `${KICAD10_3DMODEL_DIR}/Connector_Molex.3dshapes/Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal.step` | ok |
| front | J4 | JST GH 6P (board link) | Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal | B | `${KICAD10_3DMODEL_DIR}/Connector_JST.3dshapes/JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal.step` | ok |
| front | L1 | 47uH Irms>=1.3A Isat>=2A | openhw:L_Bourns_SRN6045TA | B | `${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_Bourns_SRN6045TA.step` | ok |
| front | L2 | 47uH Irms>=1.3A Isat>=2A | openhw:L_Bourns_SRN6045TA | B | `${KICAD10_3DMODEL_DIR}/Inductor_SMD.3dshapes/L_Bourns_SRN6045TA.step` | ok |
| front | Q1 | AO3401A | Package_TO_SOT_SMD:SOT-23 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23.step` | ok |
| front | Q2 | AO3401A | Package_TO_SOT_SMD:SOT-23 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23.step` | ok |
| front | Q6 | DMG2305UX | Package_TO_SOT_SMD:SOT-23 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23.step` | ok |
| front | R1 | 10k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R10 | 4.7k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R11 | 10k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R12 | 100k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R13 | 0.1R 1% 0.25W | Resistor_SMD:R_1206_3216Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_1206_3216Metric.step` | ok |
| front | R14 | 0.1R 1% 0.25W | Resistor_SMD:R_1206_3216Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_1206_3216Metric.step` | ok |
| front | R15 | 10k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R16 | 10k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R17 | 10k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R2 | 100k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R3 | 100k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R4 | 100k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R5 | 10k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R6 | 100k | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R7 | 10k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R8 | 22R | Resistor_SMD:R_0402_1005Metric | B | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | R9 | 4.7k | Resistor_SMD:R_0402_1005Metric | F | `${KICAD10_3DMODEL_DIR}/Resistor_SMD.3dshapes/R_0402_1005Metric.step` | ok |
| front | TP1 | VIN | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP10 | ICR_A | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP11 | ICR_B | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP12 | IRA_SW | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP13 | IRA_SET | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP14 | IR_PWM | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP15 | IR_CTRL | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP16 | LIGHT_SENSE | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP17 | CAM_I2C2_SDA | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP18 | CAM_I2C2_SCL | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP19 | 12V_IR | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP2 | FRONT_2V8 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP20 | GND | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP21 | GND | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP22 | SPARE1 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP23 | CAM_1V8 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP3 | CORE_1V8 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP4 | CORE_3V3 | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP5 | CAM_AVDD | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP6 | CAM_IOVDD | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP7 | CAM_MCLK | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP8 | CAM_EN | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | TP9 | CAM_RESET | TestPoint:TestPoint_Pad_D1.0mm | B | — | 모델 불필요 |
| front | U1 | RT9013-28GB | Package_TO_SOT_SMD:SOT-23-5 | B | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-5.step` | ok |
| front | U2 | DRV8837DSGR | openhw:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm | B | `${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.step` | ok |
| front | U4 | AL8860MP-13 | openhw:Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860 | B | `${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm.step` | ok |
| front | U5 | AL8860MP-13 | openhw:Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860 | B | `${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm.step` | ok |
