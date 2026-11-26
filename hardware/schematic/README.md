# C-002 회로도 — 캐리어 보드 · 전면(센서) 보드

- 배정: orch t18r C-002 (README 단계 4) + G-001(GUI) · 작성: schematic · 레인 `t-20261126-165741-b193` (L-001 `t-20261126-161205-dcb9`에서 이어 받음) · 2026-11-26
- 상태: **회로도 초안 — ERC 0**. PCB(`*.kicad_pcb`)는 P-003에서 pcb 역할이 이 폴더로 가져온다(O-20).
- **계약:** `hw-fw-contract.md` v1.2 (C-001 레인 `t-20261126-155208-d030`, 커밋 `fd12ba4`). 이 회로도에 맞춰 v1.2로 함께 고쳤다(13절).
- **입력:**
  - L-001 라이브러리 (`hardware/libraries`, 이 레인에 포함)
  - P-002 넷클래스 (`022c364`)
  - M-001b/c 높이·배치 (`fd9ed82`·`4dc801d`)
  - R-004 BOM (`7a9923c`), V-002 (`51489c5`), R-006 (`67e9959`)
  - orch O-16~O-26

## 1. 파일

| 파일 | 내용 |
|---|---|
| `carrier/carrier.kicad_pro` · `carrier.kicad_sch` | 캐리어(뒤, 코어 J2 짝) 프로젝트와 회로도 |
| `front/front.kicad_pro` · `front.kicad_sch` | 전면(센서, 코어 J1 짝) 프로젝트와 회로도 |
| `*/sym-lib-table` · `*/fp-lib-table` | 프로젝트 라이브러리 `openhw` → `../../libraries/` |
| `carrier/carrier.net` · `front/front.net` | `kicad-cli sch export netlist` 결과 (KiCad S-expression) |
| `carrier/carrier-erc.json` · `front/front-erc.json` | `kicad-cli sch erc` 결과 |
| `tools/schgen.py` · `boards.py` · `symlib.py` | 회로도 생성기 (2절) |

- `*.kicad_prl`(로컬 화면 상태)은 커밋하지 않는다.

## 2. 작성 방법

- **방식:**
  - `tools/boards.py`에 부품·핀·넷을 적었다. `tools/schgen.py`가 KiCad 10 공식/프로젝트 라이브러리 심벌을 회로도에 넣는다.
  - 연결 방식: 각 핀 끝에 **넷 라벨**을 붙이고, 쓰지 않는 핀에는 **NC 표시**를 한다.
  - 전원 입력 핀이 있는데 구동원이 없는 넷에는 **PWR_FLAG**를 자동으로 단다.
    - 캐리어: 12V_IN · GND · SD_PWR_3V3
    - 전면: 12V_IR · CORE_1V8 · GND · VIN
  - 선(wire)은 쓰지 않는다. 그래서 그림은 부품 격자 배치이고, 연결은 라벨 이름으로 읽는다.
- **BTB 60핀 넷:** Seeed B101/S401 넷리스트(인터페이스 사실, Apache-2.0)를 읽어 계약 4·5절 이름 규칙으로 바꿔 만들었다. 손으로 옮겨 적지 않았다. 대조 결과는 6절에 있다.
- **GUI(G-001):** KiCad 10.0.8 회로도 편집기로 두 프로젝트를 열어 확인했고, GUI에서 ERC도 돌렸다(9절 스크린샷).
  - 편집은 「파일 생성 → GUI로 불러 확인」 방식이다. GUI에서 저장하지 않았다.
  - 실험적 MCP 회로도 편집은 쓰지 않았다(KICAD_MCP_ENABLE_SCH_EDIT=0).
- **다음 편집:** 사람이 GUI에서 고치면 그 파일이 원본이 된다. 생성기를 다시 돌리면 GUI 편집을 덮어쓰므로, 그 뒤에는 생성기를 쓰지 않는다.

## 3. 넷 이름 규칙 (P-002 넷클래스 패턴 · 계약 이름)

| 규칙 | 내용 | 넷클래스 |
|---|---|---|
| N1 | 코어 넷 이름을 기능 이름으로 바꾼다 (계약 4·5·7절 「용도」 열):<br>MIPI_TXM2/TXP2 → `I2C1_SDA/SCL`<br>MIPI_TXM1 → `SPARE1`<br>MIPI_TXP1 → `IR_LED_EN`<br>MIPI_TXM0 → `STATUS_LED`<br>PWR_WAKEUP1 → `ALS_INT_RSV`<br>BT_UART1_* → `UART1_*`<br>GPIO15/IR_CUT → `IR_CUT`<br>+3V3/3V3 → `CORE_3V3`<br>1V8 → `CORE_1V8`<br>캐리어 VIN → `5V_SYS` | `*3V3`·`*1V8` → PWR_LOGIC, `*5V_SYS` → PWR_5V |
| N2 | 고속선은 계약 이름 그대로: `CAM_RX0_*`, `EPHY_TX*/RX*`, `USB_DP/DN` | CSI_100 · MDI_100 · USB_90 |
| N3 | 12V 계열:<br>`12V_IN_RAW`(잭) → `12V_IN_F`(퓨즈 뒤) → `12V_IN`(역접 FET 뒤)<br>`12V_IR`(eFuse 출력, FPC) | 모두 `*12V_IN*` / `*12V_IR` 패턴 |
| N4 | 전면 VIN은 `VIN`(BTB 37~43 = 코어 VIN = 캐리어 5V_SYS) | PWR_5V (`VIN`) |

## 4. 캐리어 보드 블록

| 블록 | 부품 (레퍼런스) | 연결 핵심 | 근거 |
|---|---|---|---|
| 코어 짝 BTB | J1 `Conn_02x30_Odd_Even` / `openhw:BTB_ST-BTB-058060-A` | 6절 표 | 계약 4절, O-17·O-23(패드 0.25 원품 유지) |
| 12V 입력 | J2 DC 잭(XKB DC-005-5A-2.0), F1 3A, Q1 AO4407A(역접, 게이트 R1 100k·D1 12V 제너), D2 SMBJ15A, C1 47µ/25V, C2 10µ | 잭 → 퓨즈 → P-FET(D=입력, S=12V_IN) → TVS | 계약 12절 |
| 5V 벅 | U1 TPS54302 / L1 10µH / R2 100k / R3 13.3k / C3·C4 10µ, C5 100n, C6 BOOT 100n, C7·C8 22µ | EN 개방(내부 풀업), Vout = 0.596×(1+100/13.3) = 5.08V | TI SLVSDG6C §7.2 설계 예 (R2=100k, R3=13.3k, 10µH) |
| 전원 LED | D3 + R4 2.2k (5V_SYS) | — | — |
| 12V_IR eFuse | U2 TPS26600PWP | **SHDN ← IR_LED_EN + R5 10k 풀다운**, UVLO → IN, OVP·MODE·RTN·GND → GND, **ILIM R6 8.06k (≈1.49A)**, dVdT C9 22nF, FLT·IMON 개방 | O-21, V-002 ⑥, SLVSDG2G (「UVLO terminal must be connected to the IN terminal」, 「Designs that do not need reverse input polarity protection can have RTN, GND and PowerPAD connected together」, FLT·IMON 「If unused, leave floating」) |
| USB-C | J3 USB-C 16P(HRO TYPE-C-31-M-12), R7·R8 5.1k(CC), U3 USBLC6-2SC6, R9 20k / R10 10k → USB_DET | VBUS는 5V_SYS에 잇지 않음(C4), USB_DET = VBUS/3 | 계약 C4, B101과 같은 분압비 |
| microSD | J4 Hirose DM3AT, Q2 AO3401A + Q3 DMG1012T 스위치(SD0_PWR_EN High = 켬), R11·R12 100k, C13·C14, R13~R17 47k 풀업 **DNP**, U4·U5 TPD4E05U06 ESD | SD 3.3V 전용(DTS `no-1-8-v`), CD = gpio493 | 계약 5·7절, F-001 |
| 이더넷 | J5 HR911105A, C15·C16 센터탭 100n **DNP**, D4·D5 쌍별 TVS, R18 1M + C17 1nF/2kV (CHASSIS–GND) | EPHY_TXP/N → TD+/−, EPHY_RXP/N → RD+/−, 핀 8 → GND, 실드 → CHASSIS, LED 9~12 미사용 | R-004 P6-주의(센터탭 DNP), 계약 12절 |
| 디버그 UART | J6 JST SH 3P (GND·TX·RX) | TX에 풀다운·LED 없음(부트 스트랩) | 계약 10·11절 |
| 버튼 | SW1 RESET (nRESET→GND), SW2 UPGRADE (UPGRAD_KEY → R19 1k → 스위치), C18 10n | — | 계약 C16 |
| 상태 LED | Q4 DMG1012T(게이트 STATUS_LED, R20 100k) + D6 + R21 1.5k | 1.8V GPIO라 저문턱 NMOS | 계약 7절 |
| FPC | J7 TE 1-84952-0 (10P, 접점 1A) | 계약 12A절 핀배치(대칭) | R-004 P3, 계약 12A절 v1.2 |
| 시험점 | TP1~TP26 | 계약 11절 목록 + UART1·RESERVE·I2C1 | 계약 11절 |

## 5. 전면 보드 블록

| 블록 | 부품 | 연결 핵심 | 근거 |
|---|---|---|---|
| 코어 짝 BTB | J1 `Conn_02x30_Odd_Even` / `openhw:BTB_ST-BTB-058060-B` | 6절 표 | 계약 5절 |
| 3.3V LDO | U1 RT9013-33GB (심벌 `AP2112K-3.3` — SOT-23-5 핀 같음, 4번 BP 개방), C1·C2 1µ | VIN(5V) → FRONT_3V3 | R-004 U_3V3F |
| ICR | U2 DRV8837 (VM = VIN, VCC = FRONT_3V3, IN1 = IR_CUT, IN2 = WH_PWM, nSLEEP R1 10k → VCC), J2 JST 1.25mm 2P (CLA216), R2·R3 100k 풀다운 | 기본 IN1=IN2=0 (코스트) | 계약 C13 |
| 렌즈 홀더 | MH1 `openhw:M12_Holder_20mm_CLA216-ICR` (구멍 ±10, X축) | — | M-001c, R-006 O-26 |
| 센서 커넥터 | J3 DF30FC-24DS-0.4V(81) / `openhw:Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm`(S401 파생) | 7절 표 | O-18, O-22, V-002 ④ |
| 카메라 전원 | Q1 AO3401A(IOVDD), Q2 AO3401A(AVDD, R5 10k + C6 100n **DNP** 지연), Q3 DMG1012T(게이트 CAM_EN), R4 100k, R6 100k, C7~C9 | CAM_EN=1 → CORE_3V3 → CAM_IOVDD·CAM_AVDD (모듈 3전원 모두 3.3V 입력, DVDD = J3-16 = AVDD 레일) | O-22, V-002 ④ (IOVDD 3.3V 전원 입력) |
| 센서 리셋 | R7 10k (CAM_EN → CAM_RESET), C10 100n **DNP** | RC 자리 | O-22 |
| MCLK | X1 OT7EL89 24MHz (OE = CAM_EN, VDD = CORE_1V8 상시), R8 22Ω, C11 | BTB에 MCLK 없음 → 발진기가 유일 경로 | 계약 9절, R-004 X_MCLK |
| I2C2 풀업 | R9·R10 4.7k → **CORE_1V8 (상시)** | LTR-329 폴링이 CAM_EN과 무관 | O-22 (14절 분기 C2-6) |
| 조도 | U3 LTR-329ALS-01 (VDD FRONT_3V3, SDA/SCL 1.8V 직결), C12 1µ·C13 100n | 주소 0x29 ≠ GC2053 0x3f | 계약 C15, DS86-2014-0006 Rev C (VIO 1.7~3.6V) |
| 아날로그 조도 차선 | Q4 포토트랜지스터 **DNP** (CORE_1V8 → LIGHT_SENSE), R11 10k **DNP** | ADC1 | 계약 C15 차선 |
| IR PWM | Q5 DMG1012T (게이트 IR_PWM, R12 100k) → IR_CTRL (두 AL8860 CTRL 공통) | CTRL 「open-drain PWM」 | 계약 C8, DS39014 |
| IR 스트링 A | U4 AL8860MP, R13 0.1Ω (1.0A), D_IR_A1·A2 VSMA1085400 직렬, L1 68µH, D1 SS24, C14 10µ·C15 100n | 12V_IR → Rs → SET/LED+ → LED×2 → L → SW | O-25, V-001 ⑥, DS39014 (MSOP Rs 0.1 L 68µH 예) |
| IR 스트링 B | U5·R14·D_IR_B1·B2·L2·D2·C16·C17 — **전부 DNP** | 스트링 A와 같음, CTRL 공통 | O-25 |
| FPC | J4 TE 1-84952-0, R15 10k (ALS_INT_RSV → CORE_1V8 풀업) | 계약 12A절 핀배치 | 계약 12절 |
| 시험점 | TP1~TP22 | — | 계약 11절 |

- **LED 배치 (M-001c, 코어 중심 원점):** A1(−6,+16)·A2(+6,+16) 실장, B1(−9,−16.5)·B2(+9,−16.5) DNP. DF30 중심 (0,−12.0).
- **높이 제한:** 캐리어 윗면 ≤6.2, 전면 아랫면 ≤5.2, 광차단 링 그림자 안 ≤7.6, LED 둘레 5mm 안은 LED 높이 이하. FPC 통로와 홀더 공동에는 부품을 두지 않는다. → P-003 배치에서 적용한다.
- **VSMA1085400 풋프린트:** VSMA1085600과 권장 풋프린트 도면(6.550-5366.9-3)이 같고 아랫면 패드도 같아 `openhw:Vishay_VSMA1085600_3.4x3.4mm`를 그대로 쓴다. 높이만 2.445mm로 다르다(1085600은 1.795).
  - 근거: Vishay 문서 80294 Rev 1.4, https://www.vishay.com/docs/80294/vsma1085400.pdf, sha256 642c5635…92b3, 패키지 도면 6.550-5367.01-4

## 6. 핀 ↔ 계약 대조표 (자동, 넷리스트 기준)

- 대조 방법: `carrier.net`·`front.net`의 J1 핀별 넷을 계약 v1.1 4·5절 표의 「넷」·「용도」 열과 기계로 비교했다.
- 「일치 (이름 규칙 N1)」은 3절 N1 규칙으로 바꾼 이름이다.
- 집계: 캐리어 60핀 = 일치 38 + 이름 규칙 22, 전면 60핀 = 일치 55 + 이름 규칙 5. **불일치 0.**

### 캐리어 J1 (ST-BTB-058060-A) ↔ 계약 4절

| 핀 | 코어 핀 | 계약 넷 | 계약 용도 | 회로도 넷 | 판정 |
|---|---|---|---|---|---|
| 1 | 2 | USB_DN | USB-C 디바이스 D− | USB_DN | 일치 |
| 2 | 1 | EPHY_TXP | MDI → 마그네틱/RJ45 | EPHY_TXP | 일치 |
| 3 | 4 | USB_DP | USB-C 디바이스 D+ | USB_DP | 일치 |
| 4 | 3 | EPHY_TXN | MDI → 마그네틱/RJ45 | EPHY_TXN | 일치 |
| 5 | 6 | GND | GND | GND | 일치 |
| 6 | 5 | GND | GND | GND | 일치 |
| 7 | 8 | RESERVE1 | 미사용 (NC, 시험점) | RESERVE1 | 일치 |
| 8 | 7 | EPHY_RXP | MDI → 마그네틱/RJ45 | EPHY_RXP | 일치 |
| 9 | 10 | RESERVE2 | 미사용 (NC, 시험점) | RESERVE2 | 일치 |
| 10 | 9 | EPHY_RXN | MDI → 마그네틱/RJ45 | EPHY_RXN | 일치 |
| 11 | 12 | SD1_CLK | 미사용 (NC) | (NC) | 일치 |
| 12 | 11 | GND | GND | GND | 일치 |
| 13 | 14 | GND | GND | GND | 일치 |
| 14 | 13 | USB_DET | USB-C VBUS 20k/10k 분압 (B101과 같은 비) | USB_DET | 일치 |
| 15 | 16 | SD1_CMD | 미사용 (NC) | (NC) | 일치 |
| 16 | 15 | MIPI_TXM2/IIC1_SDA/PWM | IIC1_SDA → 캐리어 예비 I2C 패드 | I2C1_SDA | 일치 (이름 규칙 N1) |
| 17 | 18 | SD1_D0 | 미사용 (NC) | (NC) | 일치 |
| 18 | 17 | MIPI_TXP2/IIC1_SCL/PWM | IIC1_SCL → 캐리어 예비 I2C 패드 | I2C1_SCL | 일치 (이름 규칙 N1) |
| 19 | 20 | SD1_D1 | 미사용 (NC) | (NC) | 일치 |
| 20 | 19 | MIPI_TXM1/IIC2_SDA/PWM | SPARE1 → FPC 8 | SPARE1 | 일치 (이름 규칙 N1) |
| 21 | 22 | SD1_D2 | 미사용 (NC) | (NC) | 일치 |
| 22 | 21 | MIPI_TXP1/IIC2_SCL/PWM | IR_LED_EN → 12V_IR 부하 스위치 | IR_LED_EN | 일치 (이름 규칙 N1) |
| 23 | 24 | SD1_D3 | 미사용 (NC) | (NC) | 일치 |
| 24 | 23 | MIPI_TXM0/GPIO12/PWM | STATUS_LED (N-MOSFET) | STATUS_LED | 일치 (이름 규칙 N1) |
| 25 | 26 | GND | GND | GND | 일치 |
| 26 | 25 | MIPI_TXM0/WL_BT_EN/GPIO13 | 미사용 (2002 R14 실장 미확인) | (NC) | 일치 |
| 27 | 28 | +3V3 | microSD 전원 스위치 입력 (B101 방식) | CORE_3V3 | 일치 (이름 규칙 N1) |
| 28 | 27 | GND | GND | GND | 일치 |
| 29 | 30 | VIN | 5V_SYS 공급 | 5V_SYS | 일치 (이름 규칙 N1) |
| 30 | 29 | GND | GND | GND | 일치 |
| 31 | 32 | VIN | 5V_SYS 공급 | 5V_SYS | 일치 (이름 규칙 N1) |
| 32 | 31 | PWR_WAKEUP1 | ALS_INT_RSV → FPC 7 | ALS_INT_RSV | 일치 (이름 규칙 N1) |
| 33 | 34 | VIN | 5V_SYS 공급 | 5V_SYS | 일치 (이름 규칙 N1) |
| 34 | 33 | nRESET | 리셋 버튼 (GND로) | nRESET | 일치 |
| 35 | 36 | VIN | 5V_SYS 공급 | 5V_SYS | 일치 (이름 규칙 N1) |
| 36 | 35 | UPGRAD_KEY | 업그레이드 버튼 → 직렬 1kΩ → GND | UPGRAD_KEY | 일치 |
| 37 | 38 | NC | NC | (NC) | 일치 |
| 38 | 37 | SD0_PWR_EN | microSD 전원 스위치 (High = 켬, B101 방식) | SD0_PWR_EN | 일치 |
| 39 | 40 | NC | NC | (NC) | 일치 |
| 40 | 39 | SDIO_D3/3V3 | microSD | SDIO_D3 | 일치 (이름 규칙 N1) |
| 41 | 42 | NC | NC | (NC) | 일치 |
| 42 | 41 | SDIO_D2/3V3 | microSD | SDIO_D2 | 일치 (이름 규칙 N1) |
| 43 | 44 | NC | NC | (NC) | 일치 |
| 44 | 43 | SDIO_D1/3V3 | microSD | SDIO_D1 | 일치 (이름 규칙 N1) |
| 45 | 46 | NC | NC | (NC) | 일치 |
| 46 | 45 | SDIO_D0/3V3 | microSD | SDIO_D0 | 일치 (이름 규칙 N1) |
| 47 | 48 | NC | NC | (NC) | 일치 |
| 48 | 47 | SDIO_CMD/3V3 | microSD | SDIO_CMD | 일치 (이름 규칙 N1) |
| 49 | 50 | NC | NC | (NC) | 일치 |
| 50 | 49 | GND | GND | GND | 일치 |
| 51 | 52 | NC | NC | (NC) | 일치 |
| 52 | 51 | SDIO_CLK/3V3 | microSD | SDIO_CLK | 일치 (이름 규칙 N1) |
| 53 | 54 | BT_UART1_RX | 예비 패드 (NC 허용) | UART1_RX | 일치 (이름 규칙 N1) |
| 54 | 53 | GND | GND | GND | 일치 |
| 55 | 56 | BT_UART1_TX | 예비 패드 | UART1_TX | 일치 (이름 규칙 N1) |
| 56 | 55 | SDIO_CD/3V3 | microSD 카드 감지 (GND로) | SDIO_CD | 일치 (이름 규칙 N1) |
| 57 | 58 | BT_UART1_CTS | 예비 패드 | UART1_CTS | 일치 (이름 규칙 N1) |
| 58 | 57 | DEBUG_UART0_TX | 디버그 헤더 TX (부하·풀다운 금지) | DEBUG_UART0_TX | 일치 |
| 59 | 60 | BT_UART1_RTS | 예비 패드 | UART1_RTS | 일치 (이름 규칙 N1) |
| 60 | 59 | DEBUG_UART0_RX | 디버그 헤더 RX | DEBUG_UART0_RX | 일치 |

집계: 일치 38, 일치 (이름 규칙 N1) 22

### 전면 J1 (ST-BTB-058060-B) ↔ 계약 5절

| 핀 | 코어 핀 | 계약 넷 | 계약 용도 | 회로도 넷 | 판정 |
|---|---|---|---|---|---|
| 1 | 2 | RESERVE2 | 미사용 (NC) | (NC) | 일치 |
| 2 | 1 | GND | GND | GND | 일치 |
| 3 | 4 | RESERVE1 | 미사용 (NC) | (NC) | 일치 |
| 4 | 3 | CAM_RX0_4N | 미사용 | (NC) | 일치 |
| 5 | 6 | WH_PWM | ICR IN2 (DRV8837) | WH_PWM | 일치 |
| 6 | 5 | CAM_RX0_4P | 미사용 | (NC) | 일치 |
| 7 | 8 | GND | GND | GND | 일치 |
| 8 | 7 | GND | GND | GND | 일치 |
| 9 | 10 | CAM_I2C2_SCL | 센서 + LTR-329 SCL | CAM_I2C2_SCL | 일치 |
| 10 | 9 | CAM_RX0_CLKN | 센서 CLK− (DF30-9) | CAM_RX0_CLKN | 일치 |
| 11 | 12 | CAM_I2C2_SDA | 센서 + LTR-329 SDA | CAM_I2C2_SDA | 일치 |
| 12 | 11 | CAM_RX0_CLKP | 센서 CLK+ (DF30-11) | CAM_RX0_CLKP | 일치 |
| 13 | 14 | GND | GND | GND | 일치 |
| 14 | 13 | GND | GND | GND | 일치 |
| 15 | 16 | IR_PWM | IR_LED_PWM → N-MOSFET → AL8860 CTRL | IR_PWM | 일치 |
| 16 | 15 | CAM_RX0_0N | 센서 D0− (DF30-5) | CAM_RX0_0N | 일치 |
| 17 | 18 | LIGHT_SENSE | 예비 (아날로그 조도 차선용 패드) | LIGHT_SENSE | 일치 |
| 18 | 17 | CAM_RX0_0P | 센서 D0+ (DF30-7) | CAM_RX0_0P | 일치 |
| 19 | 20 | NC | NC | (NC) | 일치 |
| 20 | 19 | GND | GND | GND | 일치 |
| 21 | 22 | NC | NC | (NC) | 일치 |
| 22 | 21 | CAM_RX0_1N | 센서 D1− (DF30-13) | CAM_RX0_1N | 일치 |
| 23 | 24 | NC | NC | (NC) | 일치 |
| 24 | 23 | CAM_RX0_1P | 센서 D1+ (DF30-15) | CAM_RX0_1P | 일치 |
| 25 | 26 | NC | NC | (NC) | 일치 |
| 26 | 25 | GND | GND | GND | 일치 |
| 27 | 28 | NC | NC | (NC) | 일치 |
| 28 | 27 | CAM_RX0_3N | 미사용 (GC2053 2레인) | (NC) | 일치 |
| 29 | 30 | NC | NC | (NC) | 일치 |
| 30 | 29 | CAM_RX0_3P | 미사용 | (NC) | 일치 |
| 31 | 32 | NC | NC | (NC) | 일치 |
| 32 | 31 | GND | GND | GND | 일치 |
| 33 | 34 | GND | GND | GND | 일치 |
| 34 | 33 | GPIO15/IR_CUT | ICR IN1 (DRV8837) | IR_CUT | 일치 (이름 규칙 N1) |
| 35 | 36 | GND | GND | GND | 일치 |
| 36 | 35 | GND | GND | GND | 일치 |
| 37 | 38 | VIN | DRV8837 VM(5V) · 전면 3.3V LDO 입력 | VIN | 일치 |
| 38 | 37 | GND | GND | GND | 일치 |
| 39 | 40 | VIN | DRV8837 VM(5V) · 전면 3.3V LDO 입력 | VIN | 일치 |
| 40 | 39 | AUD_MIC | 미사용 (NC) | (NC) | 일치 |
| 41 | 42 | VIN | DRV8837 VM(5V) · 전면 3.3V LDO 입력 | VIN | 일치 |
| 42 | 41 | GND | GND | GND | 일치 |
| 43 | 44 | VIN | DRV8837 VM(5V) · 전면 3.3V LDO 입력 | VIN | 일치 |
| 44 | 43 | AUD_AOUTR | 미사용 (NC) | (NC) | 일치 |
| 45 | 46 | GND | GND | GND | 일치 |
| 46 | 45 | GND | GND | GND | 일치 |
| 47 | 48 | GND | GND | GND | 일치 |
| 48 | 47 | CAM_EN | 센서 전원 스위치·24MHz 발진기 EN·센서 리셋 | CAM_EN | 일치 |
| 49 | 50 | 1V8 | 센서 1.8V·I2C 풀업 | CORE_1V8 | 일치 (이름 규칙 N1) |
| 50 | 49 | NC | NC | (NC) | 일치 |
| 51 | 52 | 1V8 | 센서 1.8V·I2C 풀업 | CORE_1V8 | 일치 (이름 규칙 N1) |
| 52 | 51 | NC | NC | (NC) | 일치 |
| 53 | 54 | GND | GND | GND | 일치 |
| 54 | 53 | NC | NC | (NC) | 일치 |
| 55 | 56 | GND | GND | GND | 일치 |
| 56 | 55 | NC | NC | (NC) | 일치 |
| 57 | 58 | 3V3 | 센서 AVDD/IOVDD 스위치 입력 (S401 방식) | CORE_3V3 | 일치 (이름 규칙 N1) |
| 58 | 57 | NC | NC | (NC) | 일치 |
| 59 | 60 | 3V3 | 센서 AVDD/IOVDD 스위치 입력 (S401 방식) | CORE_3V3 | 일치 (이름 규칙 N1) |
| 60 | 59 | NC | NC | (NC) | 일치 |

집계: 일치 55, 일치 (이름 규칙 N1) 5

## 7. 센서 커넥터 J3 (DF30 24P) ↔ 계약 5.1 · V-002 ④

| J3 핀 | 넷 | 모듈 핀 (V-002 대응식, **추론**) | 모듈 기능 |
|---|---|---|---|
| 1 | CAM_I2C2_SDA | 12 | SDA |
| 3 | CAM_I2C2_SCL | 11 | SCL |
| 4 | CAM_MCLK | 14 | MCLK |
| 5 / 7 | CAM_RX0_0N / 0P | 10 / 9 | MDN0 / MDP0 |
| 9 / 11 | CAM_RX0_CLKN / CLKP | 8 / 7 | MCN / MCP |
| 13 / 15 | CAM_RX0_1N / 1P | 6 / 5 | MDN1 / MDP1 |
| 12 | CAM_AVDD | 18 | 3.3V (AVDD) |
| 14 | CAM_IOVDD | 19 | 3.3V (IOVDD) — 전원 입력 |
| 16 | CAM_AVDD | 20 | 3.3V (DVDD) — S401과 같이 AVDD 레일 |
| 24 | CAM_RESET | 24 | RESET |
| 2·6·8·10·17~23 | GND | 1~4·13·15~17·21~23 | GND |

- 경로: 코어 J1 → 전면 J1 → J3. 짝 핀은 CLKN 10→9, CLKP 12→11, 0N 16→5, 0P 18→7, 1N 22→13, 1P 24→15, SCL 9→3, SDA 11→1로, V-002의 경로 대조와 같다.
- 넷리스트 확인: `CAM_RX0_CLKP` = J1-12 · J3-11.

## 8. 검사 결과 (verifiable 예)

| 명령 | 보드 | 종료 코드 | 위반 |
|---|---|---|---|
| `kicad-cli sch erc --severity-all --exit-code-violations --format json -o carrier-erc.json carrier.kicad_sch` | 캐리어 | **0** | **0** (오류 0 · 경고 0) |
| 같은 명령, front | 전면 | **0** | **0** |
| `kicad-cli sch export netlist --format kicadsexpr -o carrier.net carrier.kicad_sch` | 캐리어 | 0 | 부품 91 · 넷 93 (그중 KiCad가 `unconnected-…`로 이름 붙인 NC 핀 넷 37) |
| 같은 명령, front | 전면 | 0 | 부품 78 · 넷 64 (NC 넷 24) |
| GUI ERC (회로도 편집기 「ERC 실행」) | 캐리어 | — | 위반 0 · 오류 0 · 경고 0 (05 스크린샷) |

- **ERC 제외 항목 (KiCad 기본값, 손대지 않음):** single_global_label · four_way_junction · simulation_model_issue · footprint_filter. 무시 주석은 쓰지 않았다.
- **핀 하나짜리 넷:** 0 (생성기 검사)
- **원인이 확인된 실패 1회:**
  - 증상: 처음 생성한 파일을 GUI가 「이전 버전 KiCad에서 만든 파일」로 열었다.
  - 원인: 파일 형식 번호 20250114.
  - 수정: KiCad 10 형식 20260306으로 바꿔 다시 생성했다.
  - 재시험: ERC 종료 0, 위반 0, GUI 경고 없음.

## 9. GUI 스크린샷 (verifiable 아니오 — 사용자 확인용)

`C:/workspace_python/OpenHW/validation/runtime/kicad-gui/`

| 작업 | 파일 | 볼 것 |
|---|---|---|
| L-001 | `L-001/01-project.png` | 라이브러리 프로젝트 (레인 경로) |
| L-001 | `L-001/02-symbol-AP1511B.png` · `02-symbol-LTR-329.png` | 새 심벌 핀 번호·이름 |
| L-001 | `L-001/03-footprint-*.png` (5장) | BTB A/B, LTR-329, M12 홀더, VSMA 랜드 |
| C-002 | `C-002/01-carrier-schematic.png` | 캐리어 회로도 전체 (창 제목 「carrier — 회로도 편집기」) |
| C-002 | `C-002/02-carrier-detail.png` | TPS26600 eFuse 연결 확대 (SHDN·UVLO·ILIM) |
| C-002 | `C-002/03-front-schematic.png` | 전면 회로도 전체 |
| C-002 | `C-002/04-front-detail.png` | 전면 U2(DRV8837) 주변 확대 |
| C-002 | `C-002/05-carrier-erc-gui.png` | GUI ERC 결과 (위반 0) |

## 10. DNP (미실장) 목록

| 보드 | 레퍼런스 | 이유 |
|---|---|---|
| 캐리어 | R13~R17 | SD 풀업 옵션 (코어 내부 풀업 기대) |
| 캐리어 | C15·C16 | EPHY 센터탭 커패시터 (R-004 P6-주의) |
| 전면 | C6 | AVDD 켜짐 지연 옵션 |
| 전면 | C10 | RESET RC 옵션 (O-22) |
| 전면 | Q4·R11 | 아날로그 조도 차선 (C15) |
| 전면 | U5·R14·D_IR_B1·D_IR_B2·L2·D2·C16·C17 | IR 스트링 B (O-25) |

## 11. R-004 BOM과 다른 점 (orch·R-004로 넘김)

| 항목 | R-004 | 회로도 | 이유 |
|---|---|---|---|
| ICR 드라이버 | UMW AP1511B | **TI DRV8837DSGR** | 계약 C13 (V-001 ⑤) |
| microSD | SHOU HAN TF PUSH (C393941) | **Hirose DM3AT-SF-PEJM5** (R-004 차선) | KiCad 공식 심벌·풋프린트가 있다. SHOU HAN으로 가려면 L-00x에서 풋프린트를 작성해야 한다(분기 C2-1) |
| IR LED | VSMA1085600 ×2 | **VSMA1085400 ×4 자리(2 DNP)** | O-25 |
| 새로 넣은 부품 (BOM에 없음) | — | F1 퓨즈 3A, D1 제너 BZT52C12, USB-C 커넥터, USBLC6-2SC6, TPD4E05U06 ×2, 쌍별 TVS ×2, DMG1012T ×4, AO3401A ×3, JST SH 3P, PTS810 ×2, 10µH·68µH 인덕터, SS24, 수동소자 | 계약 3·11·12절 회로를 실제로 그리면서 필요해진 것 |

## 12. 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C2-1 | microSD 커넥터 | Hirose DM3AT (공식 라이브러리) | 검증된 풋프린트로 ERC·PCB 위험이 낮다 | R-004 대표 SHOU HAN TF PUSH (풋프린트 새로 작성) |
| C2-2 | 회로도 작성 방식 | 생성기 + 넷 라벨 (선 없음) + GUI 확인 | 120핀 BTB와 계약 표를 기계로 맞추고 사람 실수를 없앤다 | GUI에서 직접 배선 |
| C2-3 | FPC 핀배치 | **대칭**: 1 GND · 2·3 12V_IR · 4 GND · 5 SPARE1 · 6 ALS_INT_RSV · 7 GND · 8·9 12V_IR · 10 GND | FFC 방향(같은 면/반대 면)이 바뀌어도 전원·GND가 맞는다. 12V_IR이 4접점이 되어 2스트링 1.22A를 견딘다(TE 접점 1A). 뒤집히면 5↔6만 바뀌고 둘 다 1.8V 예비선이다 | 계약 v1.1의 비대칭 1~3 12V_IR |
| C2-4 | 12V_IR ILIM | **8.06kΩ ≈ 1.49A** (V-002의 1.2A에서 바꿈) | 2스트링 최악: LED Vf max 3.3V×2×1.0A×2 / 0.9 효율 / 12V ≈ 1.22A. 1.2A 한도로는 부족하다. 합계 12V 최악 ≈ 0.62(5V측) + 1.22 = 1.84A < 어댑터 2.08A | 10kΩ(1.2A) — 스트링 B를 실장하지 않으면 그대로 써도 된다 |
| C2-5 | AL8860 CTRL | 두 스트링이 IR_PWM 하나를 공유한다 (Q5 오픈드레인 하나, CTRL 직결) | GPIO가 하나뿐이다(IR_PWM). 스트링 B는 DNP로 시작한다 | 스트링 B CTRL을 SPARE1(FPC 5)로 따로 구동 |
| C2-6 | I2C2 풀업 (O-22) | 4.7k를 **CORE_1V8(상시)**에. 모듈 쪽 풀업 레일은 없음 | LTR-329 폴링이 CAM_EN과 무관해진다 | **역급전 근거:** CAM_EN=0이면 모듈 IOVDD(3.3V)가 꺼진다. 이때 1.8V 풀업이 꺼진 모듈 I/O 보호다이오드로 흐를 수 있는 전류는 최대 1.8V/4.7k ≈ 0.38mA/선(두 선 0.77mA)이다. 모듈 내부 회로는 미공개라 이 전류가 레일을 들어 올리는지는 **실물 측정 대상**이다. FW 기본은 CAM_EN 상시 1(S70hardware)이다. 차선: CAM_EN=1일 때만 폴링하는 FW 규칙 |
| C2-7 | MCLK 발진기 전원 | CORE_1V8 상시 + OE = CAM_EN | 스위칭 1.8V 레일이 필요 없다 | S401처럼 스위칭 1.8V |
| C2-8 | DVDD (J3-16) | AVDD 레일 (S401과 같음) | Seeed 양산품과 같은 연결 | IOVDD 레일 (모듈 문서의 IOVDD→DVDD→AVDD 순서) |
| C2-9 | 1.8V GPIO로 NMOS 구동 | DMG1012T (공식 심벌, SOT-523) | 저전압 구동용 저문턱 소자다. 문턱값은 데이터시트 미열람이라 **P-003 전 확인** | 2N7002는 문턱이 높아 제외 |
| C2-10 | HR911105A 핀 8 | GND (KiCad 공식 심벌에서 전원 핀) | 공식 심벌 정의를 따른다 | CHASSIS — 데이터시트 확인 후 |
| C2-11 | DC 잭 풋프린트 | `BarrelJack_Horizontal` (일반형) | XKB DC-005 전용 풋프린트가 없다 | XKB 도면으로 전용 풋프린트 작성 (P-003 전) |

## 13. 계약 v1.2로 넘긴 변경 (C-001 레인)

- 3.1/3.2절:
  - eFuse 연결: SHDN, UVLO=IN, ILIM 8.06k, dVdT 22n
  - IR 2스트링(B는 DNP)
  - 12V 최악 1.84A
- 5.1절: 14 IOVDD = 3.3V 전원 입력, 24 RESET + RC 자리
- 6절: I2C2 상시 1.8V 풀업, 역급전 분기
- 12A절(새 절): FPC 대칭 핀배치, 12V_IR 4접점
- 12절: 12V_IR 보호 행을 eFuse 연결로 교체
- 13절: C18(=C2-3·C2-4·C2-5·C2-6) 추가

## 14. 남은 확인

**PCB 발주 전 게이트 (O-17 · R-006 G2):**
1. HCTL ↔ SUNGTECH 실물 결합: **1번 핀 방향**, 짝 높이 8.0, **VIN 핀 전류 정격** (O-23)
2. S401 1장으로 모듈 홀더 분리와 높이 실측 (O-26 G2, 구매는 사용자 지시 필요)
3. BXF4677 ↔ DF30 번호 대응 실물 도통 (V-002 ④)

**P-003 배치 전 확인:**
1. DMG1012T 문턱값
2. XKB DC 잭 풋프린트
3. HR911105A 핀 8·LED 핀 데이터시트
4. CLA216 ICR 케이블 헤더 계열과 코일 극성
5. OT7EL89 랜드(지금은 SiT 2.0×1.6 풋프린트)
6. TE 84952 정격(R-004는 1A로 기록)
