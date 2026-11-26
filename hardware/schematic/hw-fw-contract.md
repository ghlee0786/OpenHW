# C-001 HW/FW 계약 초안 — reCamera Core 2002 캐리어 기준

- 배정: orch t18r C-001 (2026-11-26) · 작성자: schematic (단독) · 레인 `t-20261126-155208-d030`
- 상태: **초안**. KiCad 회로도는 C-002에서 그린다. 부품 품번은 「후보」이며 재고와 정격은 C-002에서 데이터시트로 확정한다.
- 입력(읽기 전용):
  - D-001~D-003, product-brief (lead 레인 `t-20261126-144135-5470`)
  - R-001 `soc-sg2002.md`, R-002 `optics-ir.md`, R-003 `module-sg2002.md`
  - orch 확정 O-2(모듈 101991223), O-3(센서 GC2053 잠정), O-4(B301/S401은 참고만, 독자 설계)
- firmware 문서 `firmware/docs/sdk-facts.md`: 작성 시점에 아직 없다. 그래서 표마다 **「FW 확인 대기」** 열을 두었다.

## 근거 자료 (공개 저장소 Seeed-Studio/OSHW-reCamera-Series `main`, 2026-11-26 읽기 전용 내려받기, CC BY-SA 4.0)

| 약칭 | 파일 | sha256 | 읽은 방법 |
|---|---|---|---|
| 코어 SCH | `core/c1-2002/static/reCamera_Core_2002w_8GB_v1.2_SCH_PDF_241014.pdf` (표제란: Rev V1.0, 2024-04-25, KiCad 8) | 95fbc621d666f3c9db3df467e3d64d9fc67bd8b9fef037d9294c199add89358f | 시트 이미지로 렌더링해 판독. 아래 「시트」 번호는 표제란의 시트 이름 번호다(03 Power IN · 04 SG2002 PWR & XTAL · 05 SG2002 & EMMC · 06 SG2002 & WiFi · 07 BTB Connector) |
| 코어 STEP | `core/c1-2002/3D_Printed_Case/Recamera Core 2002.step` | (미계산) | 어셈블리 배치(AXIS2_PLACEMENT_3D)를 스크립트로 판독 |
| B101 | `base/b101-default/PCB/V1.2/reCamera B101 v1.2.kicad_sch` | 469a9927a5e541bd5982c6a7dacd56543aa534afab97ec6f34083f851745a325 | `kicad-cli 10.0.8 sch export netlist` (종료 코드 0)로 넷리스트를 뽑아 핀별 넷 추출 |
| S401 | `sensors/s401-gc2053/PCB/reCamera 2002 S4 GC2053 Sensor Board_V1.0_SCH&PCB_250905.kicad_sch` | 3da62d3bbdffc5ec534d0eaecf454a42428d96376bc9756c7aacaaff6a2174ba | 위와 같음 (종료 코드 0) |
| BTB 그림 | `core/c1-2002/static/BTB_Connector.png` | 7f7a0bc1d9a9f5909df8b2ed7d0768b26f4350ed32a82a62e016a0cac5477484 | 이미지 판독 (코어 SCH 07 시트와 같음) |
| README | `hardware/recamera-2002/README.md`, `core/c1-2002/README.md` | — | 본문 인용 |

- 코어 SCH는 **2002w(무선) BOM 기준**이다. 무선 없는 2002에 대해서는 README의 「C1-2002 | No wireless module; exposes additional SDIO/UART signals to the base」 문구만 있다. 그래서 2002w 회로도에서 DNP(✕)로 표시된 0Ω(SD1·UART1·R14)이 2002에 실장되는지는 **미확인**이다.
- 표기:
  - **확인됨**: 위 파일에서 직접 읽은 값
  - **추정**: 근거가 있지만 직접 확인하지 못한 값
  - **미확인**: 근거 없음
  - **가정**: 계약을 맺으려고 정한 값. 실측이나 데이터시트로 바꾼다.
- 라이선스(O-4): 이 문서는 커넥터 **인터페이스 사실**(핀 번호·넷·전압)만 인용한다. B101·S401의 회로 블록은 복제하지 않고 「참고 패턴」으로만 언급한다.

## 1. 결론 요약

1. **적층 구조 (확인됨):** 코어 J1(ST-BTB-058060-**A**, 플러그)은 SoC와 같은 **윗면**에 있고 센서 신호를 낸다. J2(ST-BTB-058060-**B**, 소켓)는 **아랫면**에 있고 베이스 신호를 낸다.
   - 따라서 구조는 「**캐리어(뒤) — 코어 — 전면(센서) 보드**」 3층 적층이다.
   - 캐리어 한 장이 CSI(J1)와 이더넷(J2)을 함께 받을 수는 없다. R-002 O1의 「센서 쪽 B2B → 캐리어 → 센서 보드」 경로는 물리적으로 성립하지 않아 **고쳐 적는다(분기 C1)**.
   - 전면 보드와 캐리어 사이의 FPC는 12V IR LED 전원과 예비 신호만 나른다.
2. **짝 커넥터 핀 번호는 홀짝이 뒤바뀐다 (확인됨):** 코어 핀 n은 짝 보드 핀 (n이 홀수면 n+1, 짝수면 n−1)에 닿는다. 예: 코어 J2-1 EPHY_TXP ↔ B101 J1-2 EPHY_TXP.
3. **전원 트리:** 12V DC 입력 → 보호 → ① 5V 벅(3A) → 모듈 VIN, ② 부하 스위치 → 12V_IR → FPC → 전면 보드 IR LED 정전류 벅.
   - 3.3V 주변 장치는 두 곳에서 받는다. microSD는 코어 +3V3을 스위칭해 쓰고(B101 패턴), ICR·조도센서는 전면 보드의 LDO(코어 VIN 5V 입력)로 쓴다.
   - 최대 입력 약 **17.4W(12V 1.45A, 가정)** → 어댑터는 12V 2A 이상.
4. **센서 쪽에 필요한 제어선이 이미 J1에 있다 (확인됨):** IR_PWM·WH_PWM·GPIO15/IR_CUT·LIGHT_SENSE(ADC1)·CAM_EN·CAM_I2C2·1V8·3V3·VIN.
   - 이 선들로 ICR 2선·IR PWM·조도센서를 모두 전면 보드에서 처리한다.
   - **센서 MCLK는 BTB에 없다.** 전면 보드에 24MHz 발진기가 꼭 있어야 한다(S401 X1 패턴).
5. **조도센서 LTR-329ALS-01에는 INT 핀이 없다 (R-002 표의 인터페이스 「I2C, CH0+CH1(IR)」와 패키지 VDFN-4 기준, 데이터시트는 미열람).** 그래서 폴링으로 읽는다. INT는 FPC 예비선(→ PWR_WAKEUP1)으로 남긴다(분기 C6).

## 2. J1/J2 판정 근거

| 항목 | 코어 J1 | 코어 J2 | 근거 | 확인 |
|---|---|---|---|---|
| 커넥터 | ST-BTB-058060-A, 3D 모델 「320210641_Sungtech_ST-BTB-058060-A_3D」 → 「SHANGQI_0_5BTB_60P_4_0H_PLUG」 | ST-BTB-058060-B, 「320210642_Sungtech_ST-BTB-058060-B_3D」 → 「…_4_0H_SOCKET」 | 코어 SCH 07, 코어 STEP PRODUCT 이름 | 확인됨. 제조사 Sungtech(STEP 모델명). 짝 높이 4.0mm는 모델명 「4_0H」에서 나온 **추정** |
| 실장 면 | 윗면: 배치 z = +1.6467mm, 법선 +Z (SoC QFN88·eMMC와 같은 면) | 아랫면: z ≈ 0, 법선 −Z | 코어 STEP 어셈블리 배치 | 확인됨 |
| STEP 좌표 (참고) | 중심 (60.0, −53.0) | (71.8, −65.0) | 같은 STEP 파일 | 확인됨. 1번 핀 방향·회전은 기구 담당이 STEP으로 다시 확인 |
| 신호 | CAM_RX0(4레인+CLK), CAM_I2C2, CAM_EN, IR_PWM, WH_PWM, GPIO15/IR_CUT, LIGHT_SENSE, AUD, 1V8, 3V3, VIN | EPHY MDI, USB2, USB_DET, SDIO0, SD1, UART0·UART1, MIPI_TX(GPIO/I2C/PWM 겸용), nRESET, UPGRAD_KEY, PWR_WAKEUP1, +3V3, VIN | 코어 SCH 07 | 확인됨 |
| 짝 보드 | S401(센서)이 ST-BTB-058060-**B**로 짝 | B101(베이스)이 ST-BTB-058060-**A**로 짝 | 두 보드 넷리스트의 넷 이름이 홀짝 반전 규칙으로 코어와 일치 | 확인됨 |
| 우리 보드 | **전면 보드: ST-BTB-058060-B 실장** | **캐리어: ST-BTB-058060-A 실장** | 위 결과 | 원품번(제조사 P/N)·조달처는 **미확인** |
| 3층 구조 | — | — | README 「built from three interchangeable layers: a C1 core board, an S-series sensor board, and a B-series base board」 | 확인됨 |

## 3. 전원 트리와 전력 예산

### 3.1 트리

```
12V DC 잭 ─ 퓨즈/PTC ─ 역접 P-MOSFET ─ TVS ─┬─ 5V 벅 (≥3A) ── 5V_SYS ─┬─ 캐리어 BTB VIN (29·31·33·35) ─▶ 코어 VIN
  (D-003 #10)                                 │                         │      코어 안: VDDC 0.96V(1.3A) · VDDQ 1.344V(1A) · +3V3(1A) · +1V8 LDO(0.3A) · VDD_RTC 1.8V(0.1A)
                                              │                         │      코어 VIN ─▶ 코어 J1 VIN(38·40·42·44) ─▶ 전면 보드 3.3V LDO (ICR 드라이버·LTR-329)
                                              │                         │      코어 +3V3 ─▶ 캐리어 BTB 27 ─ P-FET 스위치(SD0_PWR_EN) ─▶ microSD
                                              │                         │      코어 +3V3/+1V8 ─▶ 전면 보드 센서 전원 스위치(CAM_EN)
                                              │                         └─ 전원 LED, STATUS_LED
                                              └─ 부하 스위치(IR_LED_EN) ── 12V_IR ─▶ FPC ─▶ 전면 보드 AL8860 정전류 벅 ─▶ 850nm IR LED 직렬
```

| 레일 | 출처 | 정격/제한 | 근거 | 확인 |
|---|---|---|---|---|
| 모듈 VIN | 캐리어 5V 벅 | 5V. 하한은 VBAT_DET 분압(30k/15k)과 「VBAT_DET<1.0V shutdown」 주석에서 **3.0V 이하면 꺼짐**(계산). 상한은 코어 벅 SY80004·LDO SGM2036 정격 미열람이라 **미확인** → 5V ±5%로 계약 | 코어 SCH 04 (R8/R9 주석), 03 | 하한 확인됨(계산) · 상한 미확인 |
| 코어 +3V3 (BTB 출력) | 코어 SY80004 | Imax 1A (코어 SoC·eMMC·센서와 공유) | 코어 SCH 03 「Imax=1A」 | 확인됨 (실제 여유는 미확인) |
| 코어 +1V8 (J1 출력) | 코어 SGM2036 LDO, 입력 VIN | Imax 300mA (공유) | 코어 SCH 03 | 확인됨 |
| 5V_SYS | 캐리어 벅 | 출력 5.0V, 3A급(필요 1.25A의 2배 이상) · 입력 정격 ≥28V | 아래 예산 | 가정 |
| 12V_IR | 캐리어 부하 스위치 | 1.0A 연속 (가정) | 아래 예산 | 가정 |
| 전면 3V3 | 전면 LDO, 입력 코어 VIN 5V | ≥300mA | ICR 코일 165mA(3.3V, 20Ω) 펄스 + ALS | 가정 |

### 3.2 전력 예산 (최악, 야간)

| 부하 | 레일 | 전류 | 전력 | 근거 | 확인 |
|---|---|---|---|---|---|
| 코어 모듈 + 센서 | 5V VIN | 1.0A | 5.0W | Seeed 시리즈 「5V 1A」 (R-003) | 확인됨(공식 표기) · 실측 필요 |
| microSD | 코어 +3V3 | ≤0.2A | ≤0.66W | SD 카드 일반값 | 가정 (코어 3V3 1A 안에서 공유) |
| ICR 코일 (CLA216) | 전면 3V3 | 0.165A, 100~500ms 펄스 | 피크 0.55W, 평균 ≈0 | R-002 2.2절 | 확인됨(데이터 값) |
| 전면 3V3 LDO 손실 | 코어 VIN | ≤0.2A | 피크 ≤0.34W | 계산 | 가정 |
| LTR-329 · 24MHz 발진기 · LED 2개 | — | <25mA | <0.1W | 일반값 | 가정 |
| **5V_SYS 합계** | | **≈1.25A** | **6.25W** | | 가정 |
| 5V 벅 입력 (효율 88%) | 12V | 0.59A | 7.1W | | 가정 |
| IR LED: VSMA1085600 ×3 직렬, 1.0A | 12V_IR | — | LED 9.3W (Vf 3.1V×3) | R-002 O6 (개수·전류는 O6-미정) | 가정 |
| AL8860 입력 (효율 90%) | 12V | 0.86A | 10.3W | | 가정 |
| **12V 입력 합계 (야간 최악)** | | **≈1.45A** | **≈17.4W** | | 가정 → **어댑터 12V 2A(24W) 이상** |
| 주간 (IR 꺼짐) | | ≈0.6A | ≈7.1W | | 가정 |

- **BTB 핀 전류 정격은 미확인이다.** J2 VIN 4핀으로 1.25A가 흐르면 핀당 약 0.31A다. B101도 같은 4핀으로 USB 5V(퓨즈 2A)를 공급하는 것을 확인했다. 정격은 커넥터 데이터시트로 C-002에서 확인한다.
- **AL8860 헤드룸:** 12V×0.95 = 11.4V에서 LED 3직렬 9.3V면 듀티가 약 82%다. 동작 여부는 데이터시트 확인이 필요하고, 안 되면 2직렬로 줄인다.

## 4. 캐리어 BTB 핀맵 (캐리어 커넥터 = ST-BTB-058060-A, 코어 J2와 짝)

- 「캐리어 핀」은 B101 J1 넷리스트에서 읽은 번호다(kicad-cli 추출). 「코어 J2 핀」은 홀짝 반전 규칙으로 구했다.
- SoC 패드와 전압은 코어 SCH에서 읽었다.
- 「시트」 열은 코어 SCH 시트 번호다.

| 캐리어 핀 | 코어 J2 핀 | 넷 | SoC 패드 (코어 SCH) | 전압 도메인 | 캐리어 용도 | FW 확인 대기 | 시트 |
|---|---|---|---|---|---|---|---|
| 1 | 2 | USB_DN | 70 USB_DM (R90 2.2Ω) | USB2 HS | USB-C 디바이스 D− | — | 05 |
| 2 | 1 | EPHY_TXP | 65 PAD_ETH_RXM_EPHY_TXP (R85 2.2Ω) | 아날로그 MDI | MDI → 트랜스/RJ45 | — | 05 |
| 3 | 4 | USB_DP | 69 USB_DP (R89 2.2Ω) | USB2 HS | USB-C 디바이스 D+ | — | 05 |
| 4 | 3 | EPHY_TXN | 64 PAD_ETH_RXP_EPHY_TXN (R86 2.2Ω) | 아날로그 MDI | MDI → 트랜스/RJ45 | — | 05 |
| 5 | 6 | GND | GND | — | GND | — | — |
| 6 | 5 | GND | GND | — | GND | — | — |
| 7 | 8 | RESERVE1 | SoC 미연결 — 코어 J1-4 ↔ J2-8 관통 | — | 미사용 (NC, 시험점) | — | 07 |
| 8 | 7 | EPHY_RXP | 63 PAD_ETH_TXM_EPHY_RXP (R87 2.2Ω) | 아날로그 MDI | MDI → 트랜스/RJ45 | — | 05 |
| 9 | 10 | RESERVE2 | SoC 미연결 — 코어 J1-2 ↔ J2-10 관통 | — | 미사용 (NC, 시험점) | — | 07 |
| 10 | 9 | EPHY_RXN | 62 PAD_ETH_TXP_EPHY_RXN (R88 2.2Ω) | 아날로그 MDI | MDI → 트랜스/RJ45 | — | 05 |
| 11 | 12 | SD1_CLK | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | 2002 실장 여부 | 07 |
| 12 | 11 | GND | GND | — | GND | — | — |
| 13 | 14 | GND | GND | — | GND | — | — |
| 14 | 13 | USB_DET | 60 USB_VBUS_DET | 분압 입력 (B101: VIN 20k/10k) | USB-C VBUS 20k/10k 분압 | VBUS 검출 임계 대기 | 05 |
| 15 | 16 | SD1_CMD | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | 2002 실장 여부 | 07 |
| 16 | 15 | MIPI_TXM2/IIC1_SDA/PWM | 83 PAD_MIPI_TXM2 | 1.8V 추정(VDD18A_MIPI) | FPC SPARE1 (예비 GPIO) | GPIO 번호·핀먹스 | 05 |
| 17 | 18 | SD1_D0 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | 2002 실장 여부 | 07 |
| 18 | 17 | MIPI_TXP2/IIC1_SCL/PWM | 84 PAD_MIPI_TXP2 | 1.8V 추정 | IR_LED_EN (12V_IR 부하 스위치) | GPIO 번호·핀먹스 | 05 |
| 19 | 20 | SD1_D1 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | 2002 실장 여부 | 07 |
| 20 | 19 | MIPI_TXM1/IIC2_SDA/PWM | 85 PAD_MIPI_TXM1 | 1.8V 추정 | 예비 (시험점) | IIC2가 PWR_GPIO1/2와 겹치는지 | 05 |
| 21 | 22 | SD1_D2 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | 2002 실장 여부 | 07 |
| 22 | 21 | MIPI_TXP1/IIC2_SCL/PWM | 86 PAD_MIPI_TXP1 | 1.8V 추정 | 예비 (시험점) | IIC2 핀먹스 | 05 |
| 23 | 24 | SD1_D3 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | 2002 실장 여부 | 07 |
| 24 | 23 | MIPI_TXM0/GPIO12/PWM | 87 PAD_MIPI_TXM0 | 1.8V 추정 | STATUS_LED (N-MOSFET 구동) | GPIO 번호 | 05 |
| 25 | 26 | GND | GND | — | GND | — | — |
| 26 | 25 | MIPI_TXM0/WL_BT_EN/GPIO13 | 88 PAD_MIPI_TXP0 (R14 0Ω, 2002w 회로도 DNP) | 1.8V 추정 | 미사용 (2002 R14 실장 미확인) | 2002 실장 여부 | 05·07 |
| 27 | 28 | +3V3 | 코어 SY80004 3.3V 출력 (Imax 1A, 코어와 공유) | 3.3V 출력 | microSD 전원 스위치 입력 (B101 방식) | — | 03·07 |
| 28 | 27 | GND | GND | — | GND | — | — |
| 29 | 30 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 30 | 29 | GND | GND | — | GND | — | — |
| 31 | 32 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 32 | 31 | PWR_WAKEUP1 | 44 PWR_BUTTON1 (2002w: BT_HOST_WAKE 겸용) | 1.8V (VDDIO_RTC) | FPC ALS_INT_RSV (예비 인터럽트) | GPIO/IRQ 번호 | 04·06 |
| 33 | 34 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 34 | 33 | nRESET | 39 PWR_RSTN/1V8 (10k PU→VDD_RTC, 100nF) | 1.8V | 리셋 버튼 (GND로) | — | 04 |
| 35 | 36 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 36 | 35 | UPGRAD_KEY | 30 AUX0 (4.7k PU→VDDIO_EMMC) | 3.3V | 업그레이드 버튼 (GND로) | 부트 시 동작 | 05 |
| 37 | 38 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 38 | 37 | SD0_PWR_EN | 15 SD0_PWR_EN | 3.3V | microSD 전원 스위치 제어 | 극성·기본값 | 05 |
| 39 | 40 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 40 | 39 | SDIO_D3/3V3 | 12 SD0_D3 | 3.3V | microSD | — | 05 |
| 41 | 42 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 42 | 41 | SDIO_D2/3V3 | 11 SD0_D2 | 3.3V | microSD | — | 05 |
| 43 | 44 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 44 | 43 | SDIO_D1/3V3 | 10 SD0_D1 | 3.3V | microSD | — | 05 |
| 45 | 46 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 46 | 45 | SDIO_D0/3V3 | 8 SD0_D0 | 3.3V | microSD | — | 05 |
| 47 | 48 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 48 | 47 | SDIO_CMD/3V3 | 7 SD0_CMD | 3.3V | microSD | — | 05 |
| 49 | 50 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 50 | 49 | GND | GND | — | GND | — | — |
| 51 | 52 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 52 | 51 | SDIO_CLK/3V3 | 6 SD0_CLK (R36 0Ω) | 3.3V | microSD | — | 05 |
| 53 | 54 | BT_UART1_RX | 29 IIC0_SDA (R68 0Ω, 2002w DNP) | 3.3V (VDDIO_EMMC) | 예비 헤더 (NC 허용) | 2002 실장 여부·핀먹스 | 05·07 |
| 54 | 53 | GND | GND | — | GND | — | — |
| 55 | 56 | BT_UART1_TX | 28 IIC0_SCL (R67 0Ω, 2002w DNP) | 3.3V | 예비 헤더 | 2002 실장 여부 | 05·07 |
| 56 | 55 | SDIO_CD/3V3 | 14 SD0_CD (R39 33Ω + C53 100nF) | 3.3V | microSD 카드 감지 | 극성 | 05 |
| 57 | 58 | BT_UART1_CTS | 27 JTAG_CPU_TCK (R70 0Ω, 2002w DNP) | 3.3V | 예비 헤더 | 2002 실장 여부 | 05·07 |
| 58 | 57 | DEBUG_UART0_TX | 18 UART0_TX (R4 100Ω, R32 4.7k PU = 부트 스트랩) | 3.3V | 디버그 헤더 TX (부하·풀다운 금지) | 콘솔 설정 | 05 |
| 59 | 60 | BT_UART1_RTS | 26 JTAG_CPU_TMS (R69 0Ω, 2002w DNP) | 3.3V | 예비 헤더 | 2002 실장 여부 | 05·07 |
| 60 | 59 | DEBUG_UART0_RX | 19 UART0_RX (R5 100Ω, R30 4.7k PU) | 3.3V | 디버그 헤더 RX | — | 05 |

- **전압 도메인:**
  - PWR_* 패드: VDDIO_RTC = +VDD_RTC = XC6206P182(1.8V) → **1.8V**. 확인됨 (시트 03·04)
  - SD0·UART0·AUX0 그룹: VDDIO_SD0_EMMC가 R83(0Ω)으로 3.3V에 연결됐다고 **추정**. R84(DNP)가 1.8V 쪽이다. B101 넷 이름 「SDIO_*/3V3」이 이를 뒷받침한다.
  - MIPI_TX 패드: VDD18A_MIPI = +1V8이라 1.8V로 **추정**
- **캐리어에서 쓰지 않는 핀:** RESERVE1/2, SD1, UART1, MIPI_TXP0, IIC2. 이 핀들은 비워 두거나 시험점으로만 낸다. 2002에서 실장되는지는 FW/실물로 확인한다.

## 5. 전면(센서) 보드 BTB 핀맵 (전면 커넥터 = ST-BTB-058060-B, 코어 J1과 짝)

「전면 핀」은 S401 J1 넷리스트에서 읽었다.

| 전면 핀 | 코어 J1 핀 | 넷 | SoC 패드 (코어 SCH) | 전압 도메인 | 전면 보드 용도 | FW 확인 대기 | 시트 |
|---|---|---|---|---|---|---|---|
| 1 | 2 | RESERVE2 | SoC 미연결 — 코어 J1-2 ↔ J2-10 관통 | — | 미사용 (NC) | — | 07 |
| 2 | 1 | GND | GND | — | GND | — | — |
| 3 | 4 | RESERVE1 | SoC 미연결 — 코어 J1-4 ↔ J2-8 관통 | — | 미사용 (NC) | — | 07 |
| 4 | 3 | CAM_RX0_4N | 72 PAD_MIPIRX4N | MIPI CSI | 미사용 | — | 05 |
| 5 | 6 | WH_PWM | 47 PWR_GPIO0 | 1.8V | ICR_INB (AP1511B 입력 B) | GPIO 번호 | 04 |
| 6 | 5 | CAM_RX0_4P | 73 PAD_MIPIRX4P | MIPI CSI | 미사용 | — | 05 |
| 7 | 8 | GND | GND | — | GND | — | — |
| 8 | 7 | GND | GND | — | GND | — | — |
| 9 | 10 | CAM_I2C2_SCL | 48 PWR_GPIO1 | 1.8V (VDDIO_RTC) | 센서 + LTR-329 SCL | 버스 번호 | 04 |
| 10 | 9 | CAM_RX0_CLKN | 76 PAD_MIPIRX2N | MIPI CSI | 센서 CLK− (DF30-9) | lane 매핑 | 05 |
| 11 | 12 | CAM_I2C2_SDA | 49 PWR_GPIO2 | 1.8V | 센서 + LTR-329 SDA | 버스 번호 | 04 |
| 12 | 11 | CAM_RX0_CLKP | 77 PAD_MIPIRX2P | MIPI CSI | 센서 CLK+ (DF30-11) | lane 매핑 | 05 |
| 13 | 14 | GND | GND | — | GND | — | — |
| 14 | 13 | GND | GND | — | GND | — | — |
| 15 | 16 | IR_PWM | 35 PAD_ZQ | 미확인 | IR_LED_PWM (AL8860 CTRL, N-MOSFET 경유) | PWM 채널·PAD_ZQ 기능 | 04 |
| 16 | 15 | CAM_RX0_0N | 80 PAD_MIPIRX0N | MIPI CSI | 센서 D0− (DF30-5) | lane 매핑 | 05 |
| 17 | 18 | LIGHT_SENSE | 59 ADC1 | 아날로그 (입력 범위 미확인) | 예비 (아날로그 조도 차선용 패드) | ADC 채널·범위 | 05 |
| 18 | 17 | CAM_RX0_0P | 81 PAD_MIPIRX0P | MIPI CSI | 센서 D0+ (DF30-7) | lane 매핑 | 05 |
| 19 | 20 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 20 | 19 | GND | GND | — | GND | — | — |
| 21 | 22 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 22 | 21 | CAM_RX0_1N | 74 PAD_MIPIRX3N | MIPI CSI | 센서 D1− (DF30-13) | lane 매핑 | 05 |
| 23 | 24 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 24 | 23 | CAM_RX0_1P | 75 PAD_MIPIRX3P | MIPI CSI | 센서 D1+ (DF30-15) | lane 매핑 | 05 |
| 25 | 26 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 26 | 25 | GND | GND | — | GND | — | — |
| 27 | 28 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 28 | 27 | CAM_RX0_3N | 78 PAD_MIPIRX1N | MIPI CSI | 미사용 (GC2053 2레인) | — | 05 |
| 29 | 30 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 30 | 29 | CAM_RX0_3P | 79 PAD_MIPIRX1P | MIPI CSI | 미사용 | — | 05 |
| 31 | 32 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 32 | 31 | GND | GND | — | GND | — | — |
| 33 | 34 | GND | GND | — | GND | — | — |
| 34 | 33 | GPIO15/IR_CUT | 17 SPK_EN | 미확인 (SD0/EMMC 그룹 3.3V 추정) | ICR_INA (AP1511B 입력 A) | GPIO 번호·전압 도메인 | 05 |
| 35 | 36 | GND | GND | — | GND | — | — |
| 36 | 35 | GND | GND | — | GND | — | — |
| 37 | 38 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 전면 보드 3.3V LDO 입력 (ICR·ALS) | — | 03·07 |
| 38 | 37 | GND | GND | — | GND | — | — |
| 39 | 40 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 전면 보드 3.3V LDO 입력 (ICR·ALS) | — | 03·07 |
| 40 | 39 | AUD_MIC | 2 PAD_AUD_AINL_MIC (R97 0Ω) | 아날로그 | 미사용 (NC) | — | 05 |
| 41 | 42 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 전면 보드 3.3V LDO 입력 (ICR·ALS) | — | 03·07 |
| 42 | 41 | GND | GND | — | GND | — | — |
| 43 | 44 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 전면 보드 3.3V LDO 입력 (ICR·ALS) | — | 03·07 |
| 44 | 43 | AUD_AOUTR | 4 PAD_AUD_AOUTR | 아날로그 | 미사용 (NC) | — | 05 |
| 45 | 46 | GND | GND | — | GND | — | — |
| 46 | 45 | GND | GND | — | GND | — | — |
| 47 | 48 | GND | GND | — | GND | — | — |
| 48 | 47 | CAM_EN | 43 PWR_WAKEUP0 | 1.8V | 센서 전원 스위치·24MHz 발진기 EN·센서 리셋 | GPIO 번호·극성 | 04 |
| 49 | 50 | 1V8 | 코어 SGM2036 1.8V LDO 출력 (Imax 300mA, 공유) | 1.8V 출력 | 센서 1.8V·I2C 풀업 | — | 03·07 |
| 50 | 49 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 51 | 52 | 1V8 | 코어 SGM2036 1.8V LDO 출력 (Imax 300mA, 공유) | 1.8V 출력 | 센서 1.8V·I2C 풀업 | — | 03·07 |
| 52 | 51 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 53 | 54 | GND | GND | — | GND | — | — |
| 54 | 53 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 55 | 56 | GND | GND | — | GND | — | — |
| 56 | 55 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 57 | 58 | 3V3 | 코어 SY80004 3.3V 출력 (Imax 1A, 코어와 공유) | 3.3V 출력 | 센서 AVDD/IOVDD 스위치 입력 (S401 방식) | — | 03·07 |
| 58 | 57 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 59 | 60 | 3V3 | 코어 SY80004 3.3V 출력 (Imax 1A, 코어와 공유) | 3.3V 출력 | 센서 AVDD/IOVDD 스위치 입력 (S401 방식) | — | 03·07 |
| 60 | 59 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |

### 5.1 센서 모듈 커넥터 (S401 J2 = Hirose DF30FC-24DS-0.4V, 24P 0.4mm) — S401 넷리스트에서 확인됨

| 핀 | 넷 | 핀 | 넷 |
|---|---|---|---|
| 1 | CAM_I2C2_SDA | 2 | GND |
| 3 | CAM_I2C2_SCL | 4 | MCLK 24MHz (X1 → R18 0Ω) |
| 5 | CAM_RX0_0N (D0−) | 6 | GND |
| 7 | CAM_RX0_0P (D0+) | 8 | GND |
| 9 | CAM_RX0_CLKN | 10 | GND |
| 11 | CAM_RX0_CLKP | 12 | AVDD (코어 3V3 → Q8 스위치, CAM_EN 제어) |
| 13 | CAM_RX0_1N (D1−) | 14 | IOVDD (코어 3V3 → Q3 스위치) |
| 15 | CAM_RX0_1P (D1+) | 16 | AVDD |
| 17~23 | GND | 24 | 센서 리셋/PWDN 추정 (R8 10k로 CAM_EN, R7 10k) |

- **GC2053은 2레인으로 쓴다:** D0·D1·CLK만 사용한다. SoC 패드 기준으로는 D0 = MIPIRX0, CLK = MIPIRX2, D1 = MIPIRX3이다. reCamera SDK의 lane_id·pn_swap 설정과 대조해야 한다(**FW 확인 대기**).
- **AVDD·IOVDD 전압 미확인:** S401은 둘 다 3.3V를 스위칭해 모듈에 준다. 센서 모듈 안에 LDO가 있는지는 모른다. 24P 센서 모듈의 품번과 판매처도 **미확인**이다(O-3 위험).
- **I2C 풀업:** S401은 4.7k(R6/R11)를 CAM_1V8에 연결한다. CAM_1V8은 코어 1V8을 Q6로 스위칭한 것이고, Q6는 CAM_EN이 제어한다.

## 6. I2C 버스와 주소

| 버스 | SoC 패드 | 전압 | 장치 | 7비트 주소 | 풀업 | 근거 | FW 확인 대기 |
|---|---|---|---|---|---|---|---|
| CAM_I2C2 | 48 PWR_GPIO1(SCL) · 49 PWR_GPIO2(SDA) | 1.8V | GC2053 | 0x37 (**미확인** — 일반 지식. R-003의 Milk-V GC2083 cfg 「주소 37」과 같은 계열) | 4.7k → CAM_1V8 (전면 보드) | 코어 SCH 04, S401 | 버스 번호(i2c-2?), 센서 주소 |
| 〃 | 〃 | 〃 | LTR-329ALS-01 (조도) | 0x29 (**미확인** — 데이터시트 미열람) | 같은 풀업 공유 | R-002 O8 | 드라이버 유무(사용자 공간 i2c-dev 폴링 가능) |
| IIC1 (MIPI_TXM2/TXP2) | 83/84 | 1.8V 추정 | 없음 (예비) | — | — | 코어 SCH 05 | 핀먹스 가능 여부 |

- **충돌:** 0x37과 0x29는 겹치지 않는다(주소 값은 둘 다 미확인).
- **LTR-329 로직 전압 (미확인):** VDD는 전면 3V3을 쓴다. 1.8V I2C(VIH)를 받는지는 데이터시트로 확인해야 한다. 받지 못하면 레벨시프터를 넣거나 차선 센서로 바꾼다.
- **FW 제약:** 풀업이 CAM_EN으로 켜지는 CAM_1V8에 걸려 있다. 그래서 **조도센서는 CAM_EN=1일 때만 읽는다.** 센서 IOVDD가 꺼진 상태에서 버스를 쓰면 센서 쪽 보호 다이오드가 버스를 눌러 둘 수 있다(추정).

## 7. GPIO 배정

| 기능 | 신호 (넷) | SoC 패드 | 커넥터 | 도메인 | 방향 / 기본 상태 | 연결 | FW 확인 대기 |
|---|---|---|---|---|---|---|---|
| ICR 정방향 (낮) | GPIO15/IR_CUT | 17 SPK_EN | 코어 J1-33 / 전면 34 | 미확인 (3.3V 추정) | 출력, 기본 Low | AP1511B INA (O4) | GPIO 번호, 도메인, 부팅 중 상태 |
| ICR 역방향 (밤) | WH_PWM | 47 PWR_GPIO0 | 코어 J1-6 / 전면 5 | 1.8V | 출력, 기본 Low | AP1511B INB. 1.8V에서 VIH가 부족하면 N-MOSFET 레벨 변환 | GPIO 번호, PWM 기능 끄기 |
| IR LED 밝기 | IR_PWM | 35 PAD_ZQ | 코어 J1-16 / 전면 15 | 미확인 | PWM 출력, 기본 Low = 끔 | N-MOSFET → AL8860 CTRL 끌어내림 (논리 반전 — CTRL 임계값은 데이터시트로 확정) | **PAD_ZQ가 PWM으로 쓰이는지**, 채널 번호 |
| IR LED 전원 | IR_LED_EN | 84 PAD_MIPI_TXP2 | 코어 J2-17 / 캐리어 18 | 1.8V 추정 | 출력, 기본 Low = 12V_IR 끊김 (하드웨어 풀다운) | 캐리어 12V 부하 스위치 | GPIO 번호, 핀먹스 |
| 조도 INT | (없음 — 폴링) | — | — | — | — | LTR-329에는 INT가 없다 | — |
| 조도 INT 예비 | ALS_INT_RSV | 44 PWR_BUTTON1 (PWR_WAKEUP1) | 코어 J2-31 / 캐리어 32 → FPC 7 | 1.8V | 입력 | 차선 센서(LTR-303·VEML6030) INT | IRQ 사용 가능 여부 |
| 예비 GPIO | SPARE1 | 83 PAD_MIPI_TXM2 | 코어 J2-15 / 캐리어 16 → FPC 8 | 1.8V 추정 | 미정 | FPC 예비 | 핀먹스 |
| 상태 LED | STATUS_LED | 87 PAD_MIPI_TXM0 | 코어 J2-23 / 캐리어 24 | 1.8V 추정 | 출력, High = 켬 | N-MOSFET + LED (5V 또는 3V3) | GPIO 번호 |
| 센서 전원·리셋 | CAM_EN | 43 PWR_WAKEUP0 | 코어 J1-47 / 전면 48 | 1.8V | 출력 | 전면 보드 전원 스위치·발진기 EN·센서 리셋 (S401 패턴) | 극성, 드라이버가 제어하는지 |
| 아날로그 조도 예비 | LIGHT_SENSE | 59 ADC1 | 코어 J1-18 / 전면 17 | 아날로그 | 입력 | 미실장 패드(ALS-PT19 차선) | ADC 채널·입력 범위 |
| microSD 전원 | SD0_PWR_EN | 15 | 코어 J2-37 / 캐리어 38 | 3.3V | 출력 | NPN + P-FET 스위치 (B101 패턴) | 극성 |

- **1.8V GPIO로 3.3V/5V/12V 쪽을 구동할 때**는 N-MOSFET(오픈 드레인)이나 레벨시프터를 쓴다. 직접 연결은 하지 않는다.
- **풀다운과 기본 상태:** 모든 출력은 부팅 중 상태가 미확인이라, 하드웨어 풀다운으로 「꺼짐」을 기본으로 둔다(ICR 양쪽 Low = 코일 무전류).

## 8. 클록

| 클록 | 위치 | 값 | 근거 | 캐리어/전면 할 일 |
|---|---|---|---|---|
| SoC 주 클록 | 코어 X1 | 25MHz, 10ppm | 코어 SCH 04 | 없음 |
| 센서 MCLK | **전면 보드** | 24MHz 발진기 (S401 X1 「9C24000004」, EN = CAM_EN 경유, 전원 CAM_1V8) | S401 넷리스트 — BTB에 MCLK 핀이 없음 | 발진기 실장 **필수**. 센서 쪽 MCLK 정격은 미확인 |
| 32.768kHz | 코어 시트 06 X3 (Wi-Fi 쪽) | 32.768kHz | 코어 SCH 06 | SoC RTC 클록원인지 **미확인**. 캐리어 영향 없음 |
| 이더넷 | SoC 내장 EPHY | — | 코어 SCH 05 | 캐리어에 클록 없음 (추정) |
| USB | SoC 내장 | — | — | 없음 |

## 9. 부트·복구

| 항목 | 내용 | 근거 | 확인 |
|---|---|---|---|
| 부트 매체 | 코어 eMMC (회로도 U3 KLM8G1GETF-B041, 8GB) | 코어 SCH 05 | 확인됨(2002w 8GB 회로도 기준) |
| microSD | SD0 → 캐리어 microSD 슬롯 (D-003 #8). **SD 부팅 가능 여부와 우선순위**는 미확인 | 캐리어 표 4 | FW 확인 대기 |
| 스트랩 UART0_TX | PU = Normal, PD = 「ROM Fail Mode」 (코어 R32 4.7k PU) → **캐리어는 DEBUG_UART0_TX에 풀다운·LED·저임피던스 부하를 두지 않는다** | 코어 SCH 05 주석 | 확인됨 |
| 스트랩 EPHY_RTX | PD = CA53, PU = C906 (코어 R10 4.7k PU, R16 DNP) → RISC-V C906 부팅. BTB에 나오지 않음 | 코어 SCH 05 | 확인됨 |
| RESET 버튼 | nRESET(코어 J2-33 / 캐리어 34) → 택트 스위치 → GND. 코어 안에 10k PU(VDD_RTC)와 100nF가 있음 | 코어 SCH 04, B101 K1 | 확인됨 |
| UPGRADE 버튼 | UPGRAD_KEY(AUX0, 코어 J2-35 / 캐리어 36) → 스위치 → GND. 코어 안에 4.7k PU. B101은 10pF를 병렬로 둔다 | 코어 SCH 05, B101 K2 | 연결은 확인됨 · **누른 채 켰을 때의 동작(USB 다운로드/복구 모드 여부)은 FW 확인 대기** |
| 복구 경로 | ① USB-C(디바이스)로 펌웨어 갱신 ② 디버그 UART 콘솔 ③ microSD (②·③ 보조) | — | FW 확인 대기 |
| 저전압 차단 | VIN < 3.0V면 코어 꺼짐 (VBAT_DET) | 코어 SCH 04 | 확인됨(계산) |

## 10. 디버그 UART와 시험점

- **디버그 UART:** DEBUG_UART0_TX/RX(캐리어 58/60)를 3핀 헤더(GND·TX·RX)로 낸다. 3.3V 레벨(추정)이고 코어 안에 직렬 100Ω이 있다. 시험점도 함께 둔다(B101 TP1/TP2 패턴). 보드율과 콘솔 설정은 FW 확인 대기다.
- **시험점(캐리어):**
  - 전원: 12V_IN(보호 후), 5V_SYS, 12V_IR, 코어 +3V3(캐리어 27), SD_PWR_3V3, GND 2곳 이상
  - 신호: USB D+/D−, USB_DET, nRESET, UPGRAD_KEY, STATUS_LED, IR_LED_EN, 예비 MIPI_TX1 쌍, RESERVE1/2
- **시험점(전면):** 전면 3V3, CAM_1V8, AVDD, IOVDD, MCLK, CAM_EN, ICR 코일 양단, AL8860 SW·LED+, IR_PWM, LIGHT_SENSE

## 11. 보호회로

| 위치 | 위협 | 대책 (후보 — 정격·재고는 C-002에서 확정) | 근거 |
|---|---|---|---|
| 12V 입력 | 역접 | P-MOSFET 역접 보호 (Vds ≥30V, 게이트 제너 클램프) | 일반 설계 |
| 〃 | 과전압·서지 | TVS SMBJ15A급(동작전압 15V, 클램프 약 24V) + 5V 벅·부하 스위치·AL8860 입력 정격 ≥28V(AL8860 4.5~40V는 R-002에서 확인) | R-002 3.4절 |
| 〃 | 과전류·단락 | 리셋형 PTC 또는 퓨즈 3A급 (예산 1.45A의 약 2배) | 3.2절 |
| 5V_SYS | 벅 고장 시 과전압 | 5V 출력 TVS(5.6~6V급). 코어 상한이 미확인이라 보수적으로 둔다 | 3.1절 |
| USB-C | ESD | D+/D− 저용량 ESD, VBUS TVS, CC 5.1k 풀다운(디바이스) | B101 D1~D3 패턴 |
| microSD | ESD | 7선 ESD (B101 D4~D9 ESDPSA0402V05 패턴) | B101 |
| RJ45 | 서지·ESD | 칩 쪽 쌍마다 저용량 TVS (B101 UDD32C03L01). 칩 쪽 센터탭은 100nF로 GND (B101 C3/C4). 라인 쪽 센터탭은 75Ω + 1nF(2kV) → 실드/GNDPWR (Bob Smith). GNDPWR–GND는 1M + 1nF (B101 R6/C5/C10) | B101 넷리스트 |
| 12V_IR | LED 단선·단락 | 부하 스위치에 전류 제한이 있는 형, AL8860의 개방/단락 동작은 데이터시트로 확인 | — |
| 버튼 | ESD·채터링 | 코어 쪽 RC 외에 10pF~100nF (B101 C9 패턴) | B101 |

## 12. 전면 보드 – 캐리어 FPC 핀배치 안

- **규격 (가정):** 1.0mm 피치 10P FFC, 양쪽 ZIF 커넥터. 접점당 약 1A 가정이며 커넥터 데이터시트로 확인한다.
- **경로:** 캐리어에서 코어 옆을 돌아 전면 보드로 간다. 길이는 기구에서 정한다.

| 핀 | 신호 | 방향 (캐리어 기준) | 전압 | 캐리어 쪽 | 전면 쪽 | 비고 |
|---|---|---|---|---|---|---|
| 1 | 12V_IR | 출력 | 12V | 부하 스위치 출력 | AL8860 VIN | 3접점으로 1.0A |
| 2 | 12V_IR | 출력 | 12V | 〃 | 〃 | |
| 3 | 12V_IR | 출력 | 12V | 〃 | 〃 | |
| 4 | GND | — | — | GND | GND | IR 귀환 |
| 5 | GND | — | — | 〃 | 〃 | |
| 6 | GND | — | — | 〃 | 〃 | |
| 7 | ALS_INT_RSV | 입력 | 1.8V | 캐리어 32 (PWR_WAKEUP1) | 차선 조도센서 INT (기본 미실장, 10k 풀업은 전면 1.8V) | 예비 |
| 8 | SPARE1 | 양방향 | 1.8V | 캐리어 16 (MIPI_TXM2) | 예비 패드 | 예비 |
| 9 | GND | — | — | 〃 | 〃 | 신호 차폐 |
| 10 | GND | — | — | 〃 | 〃 | |

- 센서 쪽 제어선(ICR·IR_PWM·I2C·CAM_EN)은 FPC로 보내지 않는다. 모두 코어 J1을 통해 전면 보드에 직접 닿는다.
- **접지:** 전면 보드 접지는 코어 J1의 GND 핀들과 FPC GND로 이어진다. IR 전류(최대 1A)는 FPC GND로 돌아오게 하고, 코어 BTB GND로 흐르지 않게 전면 보드에서 배치한다(C-002 배치 규칙).

## 13. 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C1 | 보드 구성 | 캐리어(뒤)–코어–전면 보드 3층 적층. 전면 보드가 코어 J1에 직접 짝 | 코어 J1·J2가 반대면(STEP 확인)이라 캐리어 한 장이 둘 다 받을 수 없다. Seeed 3층 구조와 같아 위험이 낮다. R-002 O1 경로는 이에 맞게 고친다 | 코어 J1에 작은 어댑터를 꽂고 FPC로 CSI를 원격 센서 보드까지 보냄 (MIPI FPC 길이·임피던스 위험) |
| C2 | 센서 실장 | S401과 핀 호환되는 DF30 24P GC2053 센서 모듈 + 전면 보드 24MHz 발진기 | reCamera SDK에 GC2053 IQ가 있다 (O-3) | GC2053 칩 직접 실장 → O-3 차선(GC4653, CAM-GC2083 기성 모듈) |
| C3 | IR LED 드라이버 위치 | 전면 보드 (FPC로 12V 공급) | 스위칭 루프를 LED 옆에 둔다. FPC에는 DC만 흐름 | 캐리어에 드라이버, FPC로 LED 전류 |
| C4 | 전원 입력 | 12V 단독. USB-C는 데이터 + VBUS 검출(USB_DET)만, VIN에 연결하지 않음 | 전원 경로가 하나라 단순하다. 역류 문제가 없다 | 이상적 다이오드 OR로 USB 5V 급전 |
| C5 | microSD | SD0(3.3V) + 코어 +3V3 스위칭 (B101 패턴) | B101에서 검증된 경로이고, 2002의 SD1 실장 여부가 미확인 | SD1 (1.8V 추정, 2002 실장 확인 후) |
| C6 | 조도 INT | LTR-329(INT 없음) → 폴링. INT 예비선 확보 | R-002 O8 선택 유지 | LTR-303 / VEML6030 + FPC 7 |
| C7 | ICR 제어선 | GPIO15/IR_CUT(A) + WH_PWM(B) | 두 신호가 이미 센서 쪽 BTB에 있다 (S401은 LED에 썼음) | FPC SPARE1을 한쪽 선으로 |
| C8 | IR 밝기 제어 | IR_PWM → N-MOSFET → AL8860 CTRL. 12V_IR 하드웨어 스위치는 IR_LED_EN | 1.8V PWM은 CTRL을 직접 올리기에 부족할 수 있다. 꺼짐을 두 겹으로 보장한다 | UMW PT4115 (R-002 O7 차선) |
| C9 | 이더넷 자기부품 | 통합 마그넷 RJ45 (칩 쪽 센터탭이 따로 나오는 형) | 부품 수와 면적이 적다 | B101처럼 개별 트랜스 + 비자기 RJ45 |
| C10 | 전면 3.3V | 코어 VIN(5V) → 전면 LDO | 코어 3V3(1A 공유)을 센서에 남겨 둔다 | 코어 +3V3을 그대로 사용 |
| C11 | 보드 간 링크 | 1.0mm 10P FFC | 12V 1A를 3접점으로 나눠 흘릴 수 있다 | JST-GH 케이블 |
| C12 | BTB 짝 커넥터 | 캐리어 ST-BTB-058060-A, 전면 ST-BTB-058060-B (Sungtech) | 코어와 같은 시리즈 | 같은 피치·핀 배열의 호환품 (조달 확인 후) |

## 14. 미확인과 FW 확인 대기 목록

**하드웨어 (데이터시트 또는 실물 필요):**
1. 2002(무선 없음)에서 R48~R53(SD1)·R67~R70(UART1)·R14(GPIO13) 실장 여부. README는 「exposes additional SDIO/UART」라고만 쓴다.
2. 코어 VIN 상한 (SY80004·SGM2036 정격)
3. BTB 핀당 전류 정격, 원품번과 조달처, 짝 높이 4.0mm
4. SPK_EN(GPIO15)과 PAD_ZQ(IR_PWM)의 전압 도메인
5. SD1 패드 번호와 전압
6. LTR-329 주소와 1.8V I2C 호환, AP1511B·AL8860의 입력 임계값
7. GC2053 24P 센서 모듈 품번·조달처, 센서 모듈 안의 AVDD/IOVDD 레귤레이터 유무
8. 코어 단독 외형과 BTB 1번 핀 방향 (기구 담당이 STEP으로 확인)

**FW 확인 대기 (`firmware/docs/sdk-facts.md`와 대조):**
1. GPIO 번호와 핀먹스: GPIO15(SPK_EN), PWR_GPIO0, PAD_ZQ의 PWM 가능 여부, MIPI_TXM0/TXP2/TXM2, PWR_BUTTON1의 IRQ
2. I2C 버스 번호 (CAM_I2C2 = i2c-2?), IIC1·IIC2 핀먹스 충돌
3. GC2053 sensor_cfg: lane_id, pn_swap, MCLK 설정 (외부 발진기 사용)
4. 부팅 순서 (eMMC/SD), UPGRAD_KEY 동작, USB 업그레이드 절차, 디버그 콘솔 보드율
5. USB_VBUS_DET 임계값 (분압비 20k/10k 유지 여부)
6. ICR 펄스 폭(100~500ms)과 sophapp `app_ipcam_IRCut_Switch`의 매핑

## 15. C-002(회로도)로 넘길 규칙

- 캐리어와 전면 보드 각각에 이 문서의 표 4와 표 5를 그대로 심벌 핀으로 쓴다. **홀짝 반전 규칙을 다시 확인한다.**
- B101/S401 회로를 복사하지 않는다. 인터페이스 사실만 쓴다(O-4).
- 「미확인」 항목이 풀리기 전에는 해당 핀을 시험점이나 0Ω 옵션으로 둔다.
