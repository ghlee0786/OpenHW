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
  - (C-002 초안) 선(wire) 없이 부품 격자 배치였다. C-002b부터 기능 블록 배치 + 블록 안 배선이다(2A절).
- **BTB 60핀 넷:** Seeed B101/S401 넷리스트(인터페이스 사실, Apache-2.0)를 읽어 계약 4·5절 이름 규칙으로 바꿔 만들었다. 손으로 옮겨 적지 않았다. 대조 결과는 6절에 있다.
- **GUI(G-001):** KiCad 10.0.8 회로도 편집기로 두 프로젝트를 열어 확인했고, GUI에서 ERC도 돌렸다(9절 스크린샷).
  - 편집은 「파일 생성 → GUI로 불러 확인」 방식이다. GUI에서 저장하지 않았다.
  - 실험적 MCP 회로도 편집은 쓰지 않았다(KICAD_MCP_ENABLE_SCH_EDIT=0).
- **다음 편집:** 사람이 GUI에서 고치면 그 파일이 원본이 된다. 생성기를 다시 돌리면 GUI 편집을 덮어쓰므로, 그 뒤에는 생성기를 쓰지 않는다.

## 2A. C-002b 가독성 정리 (lead 분기 O-28)

- **방식:** 시트 하나 안에 기능 블록을 둔다. 계층 시트로 나누지 않은 이유는 로컬 라벨이 `/시트/넷`으로 바뀌어 넷 이름이 달라지기 때문이다(분기 C2b-1).
  - 블록마다 점선 틀, 제목, 주석 1~2줄(전압·전류·계약 절)을 둔다.
  - 부품은 블록 안에 신호 순서대로 놓는다.
  - 블록 글자는 「Malgun Gothic」으로 지정했다. KiCad 기본 글꼴에는 한글이 없다.
- **블록:**
  - 캐리어: 코어 BTB · 12V 입력·보호 · 5V 강압 · 12V_IR eFuse · USB-C · microSD · 이더넷 · FPC·디버그·버튼·LED · 시험점 · PWR_FLAG
  - 전면: 코어 BTB · 전면 3.3V LDO · ICR · 센서 DF30·24MHz·전원 스위치 · 조도·I2C 풀업 · IR LED 2스트링 · FPC · 시험점 · PWR_FLAG
- **배선 규칙:**
  - **블록 안에서만 쓰이는 넷**(전원 넷 제외)은 짧은 직교 배선으로 잇는다. 넷 이름을 지키려고 라벨을 하나 남긴다. → 캐리어 11넷(선 25개), 전면 5넷(선 12개).
  - 블록 사이 넷과 전원 넷(GND·12V_IN·5V_SYS·12V_IR·CORE_3V3·CORE_1V8·FRONT_3V3·VIN·SD_PWR_3V3·CHASSIS)은 핀마다 라벨을 둔다.
  - 배선이 다른 넷의 핀·선·NC 핀에 닿으면 생성기가 그 넷 전체를 라벨 방식으로 되돌린다. 우연히 이어지는 일을 막기 위해서다.
  - 아래 넷리스트 비교가 최종 판정이다.
- **참조 지정자:** 바꾸지 않았다(R1, U3 …, PCB 재연결 기준).
- **동일성 증명 (verifiable 예):**
  - 정리 전 = 커밋 `276fc89`의 `carrier.net`·`front.net`. 정리 후 = 이 커밋의 넷리스트.
  - 비교 스크립트: `tools/netcompare.py`
    - 부품마다 (참조, 값, 풋프린트)를 비교한다.
    - 넷마다 (이름, 핀 집합)을 비교한다.
    - 넷 이름의 시트 경로 접두어(`/`)만 무시한다.
    - 같으면 종료 0, 다르면 1.

| 비교 | 부품 | 넷 | 차이 | 종료 코드 |
|---|---|---|---|---|
| `python tools/netcompare.py <276fc89>/carrier.net carrier/carrier.net` | 91 / 91 | 93 / 93 | **0** | 0 |
| `python tools/netcompare.py <276fc89>/front.net front/front.net` | 78 / 78 | 64 / 64 | **0** | 0 |
| 음성 시험: front.net 사본에서 R1 값 하나와 C14 핀 하나를 바꿔 비교 | — | — | 3건 검출 | 1 |

- **ERC:** `kicad-cli sch erc --severity-all --exit-code-violations` → 캐리어 종료 0·위반 0, 전면 종료 0·위반 0.
- **그림 (verifiable 아니오, 사용자·lead 확인용):** `kicad-cli sch export svg` (종료 0, 파일 생성 확인)
  - `validation/runtime/kicad-gui/C-002b/carrier.svg` · `front.svg`
  - 미리보기 PNG: `carrier-preview.png` · `front-preview.png` · `*-preview-topleft.png`
- **GUI는 쓰지 않았다** (O-27, 소유권 pcb).

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C2b-1 | 계층 시트 vs 시트 안 블록 | 시트 안 블록 | 넷 이름(넷클래스 패턴·PCB 재연결)이 그대로 남는다 | 계층 시트 + 전역 라벨(넷 이름 유지는 되지만 시트 경로가 바뀐다) |
| C2b-2 | 블록 안 연결 | 자동 직교 배선 + 이름 라벨 1개, 충돌하면 라벨 방식 | 넷 동일성을 기계로 보장한다 | 사람이 GUI에서 배선 (pcb가 소유권을 돌려준 뒤) |
| C2b-3 | 한글 글꼴 | Malgun Gothic (Windows 기본) | KiCad 기본 스트로크 글꼴에 한글이 없다 | 블록 주석을 영문으로 |

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

`validation/runtime/kicad-gui/`

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
| 전면 | C6 | AVDD 켜짐 지연 옵션 — **DNP 유지 필수**(실장하면 GC2053 9.3절 전원 끄는 순서 위반, V-004 R13) |
| 전면 | R16 | CAM_RESET → GND 10k 자리 (C-004 R3). 실장하려면 ≥100k (V-004b R3) — **C10은 C-004에서 실장으로 바뀌어 이 목록에서 뺌** |
| 전면 | Q4·R11 | 아날로그 조도 차선 (C15) |
| ~~전면~~ | ~~U5·R14·D_IR_B1·D_IR_B2·L2·D2·C16·C17~~ | ~~IR 스트링 B (O-25)~~ → **C-012(O-69)에서 실장, 목록에서 뺌.** 최신 DNP 목록은 계약 12B절(v1.12, `contract_check.py`가 넷리스트와 대조) |

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
| C2-3 | FPC 핀배치 (**C-003에서 JST GH 6P로 대체됨, 15절**) | **대칭**: 1 GND · 2·3 12V_IR · 4 GND · 5 SPARE1 · 6 ALS_INT_RSV · 7 GND · 8·9 12V_IR · 10 GND | FFC 방향(같은 면/반대 면)이 바뀌어도 전원·GND가 맞는다. 12V_IR이 4접점이 되어 2스트링 1.22A를 견딘다(TE 접점 1A). 뒤집히면 5↔6만 바뀌고 둘 다 1.8V 예비선이다 | 계약 v1.1의 비대칭 1~3 12V_IR |
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

## 15. C-003 — V-003 지적 반영 (2026-11-26)

- **방식:** 파일 편집과 kicad-cli만 썼다. GUI는 쓰지 않았다(O-27).
- **커밋 구분:** C-002b(`4dc59dc`, 넷 동일)와 C-003(이 커밋, 의도한 변경만)을 나눴다.

### 15.1 바뀐 것

| 항목 | 내용 |
|---|---|
| 라이브러리 | `hardware/libraries/README.md` 「C-003 수정」 — BTB courtyard·실크, AL8860 Diodes 권장 랜드(새 풋프린트), DRV8837 3D 경로(새 풋프린트), M12 홀더 속성·구멍 |
| 회로도 (전면) | U4·U5 → `openhw:Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860` · U2 → `openhw:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` |
| 회로도 (두 보드) | 보드 간 연결을 FFC 10P(TE 1-84952-0)에서 **JST GH 6P (SM06B-GHS-TB)** 로 바꿈 (캐리어 J7, 전면 J4, 기호 `Conn_01x06_MountingPin`). 대칭 핀: 1 GND · 2 12V_IR · 3 SPARE1 · 4 ALS_INT_RSV · 5 12V_IR · 6 GND · MP GND |
| 프로젝트 (O-30) | 두 보드 `.kicad_pro`의 `net_settings`에 P-002 넷클래스와 패턴을 넣음 (원본 `t-20261126-171922-251f/hardware/pcb/rules/netclasses.json`, sha256 c6c272f9…441b).<br>`fp-lib-table`에 `OpenHW_Mech` (`${KIPRJMOD}/../../pcb/lib/OpenHW_Mech.pretty`) 추가.<br>**이 커밋 뒤로 `.kicad_pro`·`fp-lib-table`은 pcb 소유** |
| 주석 | 전면 IR 블록에 O-31 열 상한(스트링 평균 ≤1.6W = IR_PWM 듀티 ≤25%, FW가 강제)을 적음. 회로는 바꾸지 않음(Rs 0.1Ω 유지) |

### 15.2 넷리스트 차이 (C-002b `4dc59dc` → C-003, `tools/netcompare.py`) — 의도한 변경만

- **캐리어 (차이 9):**
  - J7 값·풋프린트 교체
  - 넷 4개의 J7 핀 번호가 바뀜:
    - GND: J7 1·4·7·10 → 1·6
    - 12V_IR: J7 2·3·8·9 → 2·5
    - SPARE1: J7 5 → 3
    - ALS_INT_RSV: J7 6 → 4
  - 그 밖의 부품·핀은 그대로다.
- **전면 (차이 12):**
  - J4 교체, 넷 4개는 캐리어와 같은 방식으로 바뀜
  - U2·U4·U5 풋프린트 교체(값과 핀 연결은 그대로)
- 부품 수(91/78)와 넷 수(93/64)는 그대로다.

### 15.3 검사 (verifiable 예)

| 명령 | 캐리어 | 전면 |
|---|---|---|
| `kicad-cli sch erc --severity-all --exit-code-violations` | 종료 0 · 위반 0 | 종료 0 · 위반 0 |
| `kicad-cli sch export netlist --format kicadsexpr` | 종료 0 | 종료 0 |
| `kicad-cli sch export svg` → `validation/runtime/kicad-gui/C-003/` | 종료 0 · `carrier.svg` 생성 확인 | 종료 0 · `front.svg` 생성 확인 |

### 15.4 분기

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C3-1 | 12V_IR 보드 간 전원 (TE 84953/84952 사양: 「Signal application only, 1 ampere maximum for single circuit」 — V-003 ⑥) | **FFC를 없애고 JST GH 6P 하나로 전원·신호를 함께 보냄.** 12V_IR 2접점, GND 2접점, 대칭 배치 | JST GH 데이터시트(eGH, sha256 b1dcb317…b722) 「Current rating: 1.0 A AC/DC (AWG #26)」, 50V. 2스트링 최악 1.22A → 접점당 0.61A(61%). 스트링 B DNP면 0.31A. 커넥터·케이블 하나. 가로형 SMD로 높이가 낮다(부품 높이는 pcb가 M-001b와 대조) | **② FFC 10P는 신호용으로 두고 12V_IR만 JST PH 2P(S2B-PH-SM4-TB) 전원 커넥터로 분리:** 「Current rating: 2 A AC/DC (AWG #24)」, 100V (ePH, sha256 447624f4…0b96). 1.22A/2A = 61%. 커넥터·케이블이 2개가 된다. ③ 전원 정격이 있는 FFC/FPC 커넥터 — 정격 자료를 찾지 못해 보류 |
| C3-2 | GH 6P 핀 배치 | 대칭(1↔6 GND, 2↔5 12V_IR, 3↔4 예비 신호) | 케이블 방향(1:1 또는 뒤집힘)과 상관없이 전원과 GND가 바뀌지 않는다. 뒤집히면 1.8V 예비선 둘만 서로 바뀐다 | 비대칭 + 케이블 방향 고정 |
| C3-3 | M12 홀더 PCB 구멍 | NPTH Ø1.8, 간격 20.0 | 홀더 쪽 구멍 Ø1.7(R-007 참고값)에 M1.6 셀프태핑 나사를 PCB 뒤에서 넣는다고 보고, ISO 273 medium 여유 1.8을 씀 | Ø1.7 (ISO 273 fine) · Ø2.0 (coarse) — 실물 조립 뒤 |
| C3-4 | AL8860 랜드 | 공식 풋프린트에서 파생해 Diodes 권장 랜드로 (공식 파일은 그대로) | V-003 ② 권고 | 공식 EP1.5x1.8 그대로 |
| C3-5 | DRV8837 3D | 공식 랜드를 복사하고 3D 경로만 바꿈 | 공식 STEP 파일이 설치본에 없다 | 공식 풋프린트 + PCB에서 3D 경로 직접 지정 |

- **남은 확인 (pcb·실물):**
  1. GH 6P 위치와 높이(M-001b 제한)
  2. 케이블 길이와 AWG26 전압강하(1.22A × 왕복 약 0.2m)
  3. 인접 접점 동시 통전 감액 자료 없음
  4. CLA216 나사 규격(실물)
  5. DF30 풋프린트 간격 규칙(라이브러리 README)

## 16. C-004 — V-004 부적합 수정 (2026-11-26)

- **입력:** V-004 `validation/review-V004-C002.md` (레인 `t-20261126-172041-ddef`, 커밋 `26b46b3`) R1~R13 · 권고, orch O-33(O-22 → 차선 복귀).
- **방식:** 파일 생성기와 kicad-cli만 썼다. GUI는 쓰지 않았다(O-27).
- **바꾸지 않은 것:** `.kicad_pro`·`fp-lib-table`(pcb 소유, O-30), 기존 참조 지정자.
- **표제란:** Rev 「C-004」.

### 16.1 수정 대응

| V-004 | 수정 | 보드 |
|---|---|---|
| **R1** (O-33) | I2C2 풀업 R9·R10 → **CAM_1V8**(스위칭). 새 Q6 **DMG2305UX**(G = CAM_PG, S = CORE_1V8, D = CAM_1V8), C18 1µF.<br>근거: Diodes DS36196 Rev 8-2 「RDS(on) … 200 mΩ VGS = −1.8V, ID = −2A」, VGS(th) −0.5~−0.9V. AO3401A는 부적합(V-004).<br>LTR-329는 CAM_EN=1일 때만 폴링(계약 6절 FW 규칙) | 전면 |
| **R2** | X1 VDD(4)와 C11 → CAM_1V8 (계약 9절과 같음) | 전면 |
| **R3** | C10 100nF 실장. 새 D3 BAT54WS(K = CAM_EN, A = CAM_RESET, R7과 병렬). 새 R16 10k CAM_RESET→GND **DNP** | 전면 |
| **R4** | 새 C19 75pF C0G (5V_SYS–BUCK_FB). C7·C8 → 22µF/25V X7R 1210, 새 C20 22µF/25V X7R 1210 (3개, DC 바이어스 뒤 실효 ≥44µF 목표 — 곡선 확인은 R-004) | 캐리어 |
| **R5** | 새 D7 SMBJ5.0A (5V_SYS–GND, 단방향) | 캐리어 |
| **R6** | J2 → `openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal` (라이브러리 README C-004) | 캐리어 |
| **R7** | D2 심벌 `Device:D_TVS`(양방향) → `Device:D_Zener`(K = 1, A = 2, 단방향 TVS 표기). 극성과 패드는 그대로 | 캐리어 |
| **R8** | Q3 드레인과 Q2 게이트 사이에 새 R22 47k(넷 SD_PWR_GD), 새 C21 100nF Q2 G–S. C13 10µF → **1µF**, 새 R23 100k 방전(SD_PWR_3V3–GND) | 캐리어 |
| **R9** | 전면 LDO U1 → **RT9013-28GB (2.8V)**, 넷 이름 FRONT_3V3 → **FRONT_2V8**. DRV8837 VIH max 0.5×2.8 = 1.4V → 1.8V GPIO 여유 0.4V. LTR-329 VDD 2.4~3.6V 안. 재고는 확인 필요 | 전면 |
| **R10** | L1·L2 → 47µH Irms ≥ 1.3A · Isat ≥ 2A (SRN6045TA-470M, 풋프린트 같음). D1·D2 → SS24 SMA (Vishay SS24-E3/61T 후보). C14·C16 → 10µF/50V X7R | 전면 |
| **R11** | USB_DET 분압 R9/R10 → **200k/100k** (12V 없이 USB만 꽂았을 때 역급전 약 0.017mA). 분압비는 같아 검출 전압 1.67V 그대로 | 캐리어 |
| **R12** | 노트 정정: U1(전면) pin4 = NC, D1 VGS ±25V, VSMA1085400 패키지 도면 6.550-5367.01-4, 캐리어 L1 Isat ≥ 6A.<br>F1 = 3A 지연형 ≥32V (후보 Littelfuse 0437003.WR, 정격 확인 필요).<br>C1 = 47µF/35V (리플 정격 MPN은 R-004) | 두 보드 |
| **R13** | C6은 **DNP 유지**(실장하면 GC2053 9.3절 전원 끄는 순서 위반). 센서 블록 주석에 적음 | 전면 |
| 권고 MODE | U2(TPS26600) MODE 핀을 RTN(GND)에서 **개방**으로 (circuit breaker + auto-retry, 분기 C4-6) | 캐리어 |
| K1 (하드웨어 쪽) | R12 100k를 IR_PWM 풀다운에서 **CORE_1V8 풀업**으로 → 기본(High) = Q5 on = CTRL Low = **IR 끔** | 전면 |
| 그 밖 | 새 TP23 CAM_1V8 (계약 11절 전면 시험점). J7·J4 케이블 필드: JST GHR-06V-S + SSHL-002T-P0.2 AWG26 1:1 (V-004 C1 권고) | 두 보드 |

### 16.2 넷리스트 차이 (C-003 `7f69f63` → C-004, `tools/netcompare.py`) — 의도한 것만

- **캐리어 (부품 91 → 97, 넷 93 → 95, 차이 29):**
  - 새 부품: C19 · C20 · C21 · D7 · R22 · R23
  - 값/풋프린트 변경: C1 · C7 · C8 · C13 · F1 · J2 · L1 · R9 · R10
  - 넷 변경:
    - BUCK_FB(+C19)
    - 5V_SYS(+C19 · C20 · D7)
    - SD_PWR_G(Q3 빠짐, +R22 · C21)
    - 새 SD_PWR_GD(Q3 · R22)
    - CORE_3V3(+C21)
    - SD_PWR_3V3(+R23)
    - GND(+C20 · D7 · R23 등)
    - U2 MODE(6)가 개방(unconnected 넷)
  - D2는 심벌만 바뀌어 넷리스트 차이에는 나오지 않는다(값·풋프린트·핀 연결 같음).
- **전면 (부품 78 → 83, 넷 64 → 65, 차이 27):**
  - 새 부품: C18 · D3 · Q6 · R16 · TP23
  - 값 변경: C14 · C16 · D1 · D2 · L1 · L2 · U1 · TP2
  - 넷 변경:
    - 새 CAM_1V8(Q6 · R9 · R10 · X1 · C11 · C18 · TP23)
    - CORE_1V8(+Q6 · R12, −R9 · R10 · X1 · C11)
    - CAM_PG(+Q6)
    - CAM_EN(+D3. X1 OE는 그대로 CAM_EN)
    - CAM_RESET(+D3 · R16)
    - IR_PWM(R12 핀 2쪽으로)
    - 이름 변경 FRONT_3V3 → FRONT_2V8
  - C10은 DNP → 실장(넷리스트에는 나오지 않음, 회로도 `dnp` 속성).
- 차이 전체 출력은 `netcompare.py` 결과 그대로다(보고에 첨부).

### 16.3 검사 (verifiable 예)

| 명령 | 캐리어 | 전면 |
|---|---|---|
| `kicad-cli sch erc --severity-all --exit-code-violations` | **종료 0 · 위반 0** | **종료 0 · 위반 0** |
| `kicad-cli sch export netlist --format kicadsexpr` | 종료 0 | 종료 0 |
| `kicad-cli sch export svg` → `validation/runtime/kicad-gui/C-004/` | 종료 0, 파일 확인 | 종료 0, 파일 확인 |

### 16.4 pcb용 변경 부품표 (P-003 재연결)

| 보드 | 참조 | 상태 | 풋프린트 | 위치 힌트 |
|---|---|---|---|---|
| 캐리어 | J2 | **풋프린트 교체** | `openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal` | 기존 J2 자리 (핀 2가 −5.9로 0.1 안쪽, 핀 3은 같음) |
| 캐리어 | C7 · C8 | **풋프린트 교체** 1206 → `Capacitor_SMD:C_1210_3225Metric` | 1210 | U1·L1 출력, 기존 자리 |
| 캐리어 | C20 | 새로 | `Capacitor_SMD:C_1210_3225Metric` | C7·C8 옆 5V_SYS 출력 |
| 캐리어 | C19 | 새로 | `Capacitor_SMD:C_0402_1005Metric` | R2 병렬, U1 FB 핀 가까이 |
| 캐리어 | D7 | 새로 | `Diode_SMD:D_SMB` | 5V_SYS, BTB VIN 핀 근처 |
| 캐리어 | R22 · C21 | 새로 | `R_0402` · `C_0402` | Q2 게이트 옆 |
| 캐리어 | R23 | 새로 | `Resistor_SMD:R_0402_1005Metric` | microSD 전원(SD_PWR_3V3) 옆 |
| 캐리어 | U2 핀 6 | 연결 해제 | — | MODE 패드를 GND에서 떼어 개방 |
| 전면 | Q6 | 새로 | `Package_TO_SOT_SMD:SOT-23` | BTB CORE_1V8 핀(49·51)과 X1·R9/R10 사이 |
| 전면 | C18 | 새로 | `Capacitor_SMD:C_0402_1005Metric` | Q6 드레인(CAM_1V8) |
| 전면 | D3 | 새로 | `Diode_SMD:D_SOD-323` | R7 병렬, DF30 J3-24 가까이 |
| 전면 | R16 | 새로 (DNP) | `Resistor_SMD:R_0402_1005Metric` | CAM_RESET–GND, C10 옆 |
| 전면 | C10 | **DNP → 실장** | 그대로 | — |
| 전면 | TP23 | 새로 | `TestPoint:TestPoint_Pad_D1.0mm` | CAM_1V8 |
| 전면 | R12 | 연결 변경 (GND → CORE_1V8 풀업) | 그대로 | Q5 게이트 옆 |
| 전면 | U1 · L1 · L2 · D1 · D2 · C14 · C16 | 값만 변경 | 그대로 | — |

- **넷클래스(pcb 소유 .kicad_pro):** FRONT_2V8은 `*3V3`·`*1V8` 패턴에 걸리지 않아 Default(0.2mm)다. 부하는 3mA 미만이라 문제는 없다. 원하면 pcb가 `*2V8` 패턴을 PWR_LOGIC에 더한다. CAM_1V8은 `*1V8`에 걸린다.

### 16.5 분기

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C4-1 | R9 IN2 여유 | 전면 LDO를 2.8V로 (RT9013-28GB) | 전면 J1에 남은 3.3V GPIO가 없다(WH_PWM·SPARE1은 1.8V). LDO 값만 바꾸면 된다 | IN2를 3.3V GPIO로 옮김 (핀 재배정 필요) |
| C4-2 | 단방향 TVS 심벌 | `Device:D_Zener` (K/A) | 공식 단방향 TVS 심벌(SMAJ 계열)도 핀 이름이 A1/A2라 극성이 드러나지 않는다 | `Diode:SMAJ5.0A` (SMA로 바뀜) |
| C4-3 | R11 USB_DET | 200k/100k (VBUS 기준 유지) | USB 연결을 검출하는 기능이 남는다. 역급전은 1/10로 준다 | 5V_SYS 기준(항상 Device) |
| C4-4 | R8 SD 전원 | 소프트스타트(47k + 100nF) + C13 1µF + 방전 100k | B101 패턴과 같고, 공유 1A CORE_3V3 레일의 돌입을 줄인다 | C13 10µF 유지 + 소프트스타트 |
| C4-5 | K1 IR 기본 상태 | 하드웨어 풀업(R12 → CORE_1V8)으로 기본 끔 + FW 규칙 | PAD_ZQ의 리셋 풀 상태가 미확인이라 하드웨어로 보장한다 | 풀다운 유지 + FW만 |
| C4-6 | TPS26600 MODE | 개방 = 회로차단기 + 자동 재시도 | IR 쪽 과부하에서 전류 제한이 계속되면 합계가 어댑터 2.08A를 넘을 수 있다(V-004 권고) | RTN = 전류 제한 + 자동 재시도 |
| C4-7 | 캐리어 출력 C | 22µF/25V X7R 1210 × 3 | 데이터시트 예와 같은 25V로 하고, DC 바이어스 여유를 위해 하나 더 둔다 | 1206 × 2 + 실측 |

- **남은 확인:**
  - RT9013-28GB 재고
  - F1·C1·L1(Isat ≥ 6A) MPN 확정 (R-004)
  - SS24-E3/61T 데이터시트
  - C7·C8·C20 DC 바이어스 곡선
  - XKB 도면과 몸체 외곽 대조
  - DMG2305UX 게이트가 CORE_3V3 풀업이라 꺼짐 때 VGS +1.5V (±8V 안, 정상)

## 17. C-005 — R-009 · V-004b 반영 (2026-11-26)

- **입력:**
  - R-009 `docs/research/r009-bom-risks.md` ⑨·② (레인 `t-20261126-171912-e7d2`, `898ed80`)
  - V-004b `validation/review-V004b-C004.md` (레인 `t-20261126-180645-0fa1`, `6404bf7`)
  - orch O-34
  - pcb P-003 실크 요청 (`f0edd7d`)
- **방식:** 파일 생성기와 kicad-cli만 썼다. 참조 지정자는 그대로, `.kicad_pro`·`fp-lib-table`은 건드리지 않았다(O-30). 표제란 Rev 「C-005」.

### 17.1 수정 대응

| 출처 | 수정 | 보드 |
|---|---|---|
| O-34 | J2(CLA216 리드) → **Molex PicoBlade 53261-0271** `Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal` (공식 라이브러리, 3D 있음). 차선 JST SM02B-GHS-TB. 극성 주석: 핀 1 = ICR_A = 빨강(+) 가정 → IN1(IR_CUT)=1 펄스 = 필터 열림(야간), IN2(WH_PWM)=1 = 닫힘(주간). **G2 실물 확인 전 PCB 확정 금지**(하우징 길이 ≈4.0 PicoBlade / ≈5.75+레버 GH, 선 순서) | 전면 |
| R-009 ⑨ | Q4 ALS-PT19(DNP) → 새 `openhw:Everlight_ALS-PT19_1.7x0.8mm` (0.8×0.8 @ ±0.75, 핀 1 = 콜렉터, Everlight DLS-0000039 Rev.8) | 전면 |
| R-009 ⑨ · V-004b R6 | J2 DC 잭: 핀(2 = 5.90, 슬롯 1.0×3.5)은 C-004와 도면이 일치해 그대로 둠. **몸체를 14.0 × 9.0, 앞면 −13.6, 뒤끝 +0.4로 맞춤**(Fab·실크). courtyard를 패드 1·3까지 넓힘(−13.85~2.0 × −4.75~6.7). 실크는 패드에서 ≥0.2. 3D는 「대체 모델(6.0 피치)」로 descr에 주석 | 캐리어 |
| pcb 실크 요청 | DF30(openhw) 실크를 패드에서 ≥0.2로 잘라냄. SRN6045는 공식 파일을 덮어쓰지 않고 **openhw 사본 `L_Bourns_SRN6045TA`** 를 만들어 실크만 고침 → L1·L2가 이 사본을 씀 | 전면 |
| **V-004b N1** | Q6 게이트를 CAM_PG에서 떼어 새 넷 **CAM_1V8_G**에 연결. 새 R17 100k로 **CORE_1V8**(Q6 자기 소스)에 풀업하고, 새 **Q7 DMG1012T**(G = CAM_EN, S = GND, D = CAM_1V8_G)로 끌어내림(S401 패턴). → CAM_EN=0이면 VGS = 0V라 CORE_1V8/3V3이 오르는 순서와 상관없다 | 전면 |
| V-004b R2 | X1 OE(핀 1) → **CAM_1V8**(VDD와 같은 넷). OE가 VDD보다 먼저 오르지 않고, CAM_EN 중간 전위와도 무관하다(분기 C5-2) | 전면 |
| V-004b R5 | D7 → **SMBJ6.0A** (VRWM 6.0V > 5V 벅 최대 5.30V) | 캐리어 |
| V-004b R8 | R11 핀 2 → **SD_PWR_GD**(B101 패턴). VGS −3.3V로 AO3401A 보증 영역 안 (τ 켤 때 4.7ms, 끌 때 14.7ms). FW: SD 전원을 다시 켜기 전 ≥250ms | 캐리어 |
| V-004b R10 | D1·D2 MPN → **Vishay SSA24-M3/61T** (SMA) | 전면 |
| V-004b R11 권고 | 새 **C22 10nF** USB_DET–GND 반영 (τ ≈ 0.67ms, 분기 C5-3) | 캐리어 |
| V-004b R12 | F1 MPN → **Bel Fuse 0685T3000-01** (1206 Slow Blow 3A 63V) | 캐리어 |
| V-004b README | 10절 DNP 목록 정정 (C10은 실장, R16 추가, C6 유지 이유) | — |

### 17.2 넷리스트 차이 (C-004 `58eb49b` → C-005, `tools/netcompare.py`) — 의도한 것만

- **캐리어 (부품 97 → 98, 넷 95 → 95, 차이 11):**
  - 새 C22
  - 값 변경: D7 SMBJ6.0A, F1
  - 넷:
    - SD_PWR_G(−R11)
    - SD_PWR_GD(+R11)
    - USB_DET(+C22)
    - GND(+C22)
- **전면 (부품 83 → 85, 넷 65 → 66, 차이 17):**
  - 새 Q7 · R17
  - 풋프린트 변경: J2(PicoBlade) · L1 · L2(openhw 사본) · Q4(ALS-PT19)
  - 넷:
    - 새 CAM_1V8_G(Q6.1 · Q7.3 · R17.2)
    - CAM_PG(−Q6)
    - CAM_EN(+Q7, −X1)
    - CAM_1V8(+X1 핀 1)
    - CORE_1V8(+R17)
    - GND(+Q7)
  - D1·D2 MPN은 필드라 넷리스트 차이에 안 나온다.

### 17.3 검사 (verifiable 예)

| 명령 | 결과 |
|---|---|
| `kicad-cli sch erc --severity-all --exit-code-violations` | 캐리어 **종료 0 · 위반 0**, 전면 **종료 0 · 위반 0** |
| `kicad-cli sch export netlist` · `sch export svg` → `validation/runtime/kicad-gui/C-005/` | 두 보드 종료 0, 파일 생성 확인 |
| 라이브러리 시험판 `kicad-cli pcb drc --severity-all` (openhw 풋프린트 11개, scratchpad) | 종료 0. **silk 위반 0** (DC 잭·DF30·SRN6045 사본·ALS-PT19 포함). 남은 것: DF30 clearance 22건(0.4mm 피치 0.17 < 0.2, pcb 간격 규칙 대상), 시험판 외곽 없음 1건 |
| `kicad-cli fp export svg` (폴더를 먼저 만듦) | 종료 0, 11개 생성 |

### 17.4 pcb용 변경 부품표

| 보드 | 참조 | 상태 | 풋프린트 | 위치 힌트 |
|---|---|---|---|---|
| 캐리어 | J2 | 풋프린트 그래픽 갱신 (패드 그대로) | `openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal` | 몸체 앞면 −13.6, courtyard 넓어짐 |
| 캐리어 | C22 | 새로 | `Capacitor_SMD:C_0402_1005Metric` | USB_DET, BTB J1-14 가까이 |
| 캐리어 | R11 | 연결 변경 (SD_PWR_G → SD_PWR_GD) | 그대로 | Q3 드레인 쪽 |
| 캐리어 | D7 · F1 | 값/MPN만 | 그대로 | — |
| 전면 | J2 | **풋프린트 교체** | `Connector_Molex:Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal` | CLA216 리드 출구 쪽, **G2 전 확정 금지** |
| 전면 | Q4 (DNP) | 풋프린트 교체 | `openhw:Everlight_ALS-PT19_1.7x0.8mm` | 기존 자리 |
| 전면 | L1 · L2 | 풋프린트 교체 (랜드 같음, 실크만) | `openhw:L_Bourns_SRN6045TA` | 기존 자리 |
| 전면 | Q7 · R17 | 새로 | `Package_TO_SOT_SMD:SOT-523` · `R_0402` | Q6 게이트 옆 |
| 전면 | X1 | 연결 변경 (핀 1 OE: CAM_EN → CAM_1V8) | 그대로 | — |
| 전면 | DF30 J3 | 실크만 바뀜 (랜드 같음) | `openhw:Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm` | — |

### 17.5 분기

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C5-1 | CLA216 리드 커넥터 | PicoBlade 53261-0271 (O-34) | R-009 도면 실측과 CLA214 사진 근거. 공식 풋프린트·3D가 있다 | JST SM02B-GHS-TB (G2 결과에 따라) |
| C5-2 | X1 OE (V-004b R2) | OE = CAM_1V8 (VDD와 같은 넷) | OE가 VDD보다 먼저 오르는 문제가 구조적으로 사라지고, 부품이 늘지 않는다. CAM_1V8은 CAM_EN이 켤 때만 오른다 | 직렬 1k로 CAM_EN 유지 |
| C5-3 | USB_DET 필터 (R11 권고) | 반영: C22 10nF | 66.7k 고임피던스 입력의 잡음을 줄인다. τ 0.67ms는 USB 연결 검출에 영향이 없다 | 미반영 (자리만) |
| C5-4 | SRN6045 실크 | openhw 사본 (공식 파일 보존) | 지시: 공식 풋프린트 덮어쓰기 금지 | 공식 그대로 + pcb에서 실크 수동 정리 |

## 18. C-006 — R17 값 변경 (V-004c 권고, orch O-36)

- **변경:** 전면 R17(Q6 게이트 풀업, CORE_1V8–CAM_1V8_G) **100k → 10k**.
  - 효과: Q6 게이트 τ가 약 81µs에서 약 8µs로 준다. 코어 1V8이 빠르게 오를 때 순간 |VGS|가 0.5V를 넘지 않게 한다.
  - 대가: CAM 켜짐 때 정지 전류 1.8V/10k = 0.18mA (수용).
- **넷리스트 차이 (C-005 `b3b376a` → C-006):** 전면 `COMP R17: 100k → 10k` **1건**. 캐리어 차이 0 (`tools/netcompare.py`).
- **ERC:** `kicad-cli sch erc --severity-all --exit-code-violations` → 캐리어 종료 0·위반 0, 전면 종료 0·위반 0.
- **pcb:** 풋프린트·연결은 그대로이고 값만 바뀐다. 표제란 Rev는 「C-005」로 두었다(값 하나 변경).

## 19. C-007 — 5V 출력 커패시터 추가 · D1/D2 MPN (orch O-37 · O-38)

- **① 캐리어 C23 새로:** 22µF/25V X7R 1210 (**Samsung CL32B226KAJNNNE**). 5V_SYS–GND에 C7·C8·C20과 같은 노드로 연결한다. 4개가 된다.
  - 근거 (R-008b): 5V DC 바이어스에서 실효 17.49µF × 3 = 52.5µF로 공칭은 충족한다.
  - 하지만 공차·온도 최악이면 약 40µF(추정)로 TI 요구 44µF보다 작다.
- **② 전면 D1·D2 MPN:** Vishay SSA24-M3/61T(재고 0, Digi-Key 리드타임 15주) → **Vishay SS24S-E3/61T** (SMA 40V 2A, LCSC C84317).
  - 노트에 차선으로 SSA24-M3/61T를 남겼다.
  - 풋프린트는 같다.
- **넷리스트 차이 (C-006 `355ab3e` → C-007):**
  - 캐리어 부품 98 → 99, 차이 5건: 새 C23, 넷 5V_SYS(+C23.1)·GND(+C23.2)
  - 전면 차이 0 (MPN은 필드라 넷리스트 밖)
- **ERC:** 캐리어 종료 0·위반 0, 전면 종료 0·위반 0. SVG는 `validation/runtime/kicad-gui/C-007/`에 있다.
- **표제란 Rev:** 「C-007」.
- **pcb:** 캐리어 C23 `Capacitor_SMD:C_1210_3225Metric` 새로 — C7·C8·C20 옆, TPS54302 출력 노드. 전면은 바뀌는 것이 없다.

## 20. C-009 — 보드 간 GH 6P 직선 케이블 (orch O-41 · M-001e K23)

- **근거:** 두 커넥터 모두 −X 쪽에서 들어오고 하니스가 U자로 굽는다. 그래서 꼬지 않은 직선 배선이면 핀이 n ↔ 7−n으로 이어진다.
  - 전원(2/5)과 GND(1/6)는 대칭이라 영향이 없다.
  - 3(SPARE1)과 4(ALS_INT_RSV)만 뒤바뀐다.
- **수정:** 전면 J4 핀 3 = **ALS_INT_RSV**, 핀 4 = **SPARE1** (맞바꿈). 캐리어 J7은 그대로다.
- **케이블:** 직선, J7-n ↔ J4-(7−n).
  - J7-3 SPARE1 ↔ J4-4 SPARE1
  - J7-4 ALS_INT_RSV ↔ J4-3 ALS_INT_RSV
- **넷리스트 차이 (C-007 `f651dfe` → C-009):** 전면 넷 2개만 바뀌었다(SPARE1: J4-3 → J4-4, ALS_INT_RSV: J4-4 → J4-3). 도구 출력으로는 before/after 4줄이다. 캐리어 차이 0.
- **ERC:** 두 보드 종료 0·위반 0. SVG는 `validation/runtime/kicad-gui/C-009/`에 있다. 표제란 Rev 「C-009」.
- **pcb:** 전면 J4 핀 3·4의 넷이 맞바뀐다(풋프린트 그대로).

## 22. C-011 — C-010 되돌림 (orch O-47 · R-013)

- **근거 (R-013, research `5e456c5`):**
  - SG2002 EPHY의 10BASE-T 자동 극성 보정은 문서와 드라이버 어디에도 없다. Auto MDI-X는 쌍을 맞바꾸는 기능일 뿐이다.
  - 자동 협상 FLP가 극성에 기대므로, RJ45 쪽 P/N을 반전하면 100M 자동 협상까지 실패할 위험이 있다.
- **수정:** `git revert 21175f3` (C-010).
  - J5 핀 1·2·3·6이 원래대로 EPHY_TXP·TXN·RXP·RXN이 되었다(RJ45 극성 표준 배정).
  - 물리적 P/N 꼬임은 PCB에서 처리한다(O-47).
- **넷리스트:** C-010 이전(`c653eac`)과 비교한 차이는 두 보드 모두 **0**이다(`tools/netcompare.py` 종료 0).
- **ERC:** 두 보드 종료 0·위반 0. SVG는 `validation/runtime/kicad-gui/C-011/`에 있다. 표제란 Rev 「C-011」.

## 23. C-013 — 라벨·필드 겹침 정리 (O-32 남은 것, 가독성만)

- **원인:** 심벌의 Reference·Value 필드가 맨 위 가로 핀 높이에서 1.27 위에 있었다. 그래서 그 핀의 넷 라벨과 겹쳤다. O-32의 J2 12V_IN_RAW, D3 PWR_LED, J1 부품 번호가 모두 이 경우다.
- **수정:** 생성기 `tools/schgen.py`에서 필드를 한 격자(1.27) 위로 올렸다(Reference −5.08, Value −2.54). 표제란은 Rev 「C-013」, 날짜 2026-11-27로 바꿨다.
  - 커밋한 두 회로도는 HEAD 파일의 필드 좌표(캐리어 204개, 전면 178개)와 표제란만 고쳤다. **UUID 목록은 전후가 같다.**
  - 이렇게 고친 파일은 생성기 출력과 UUID만 빼면 같다(두 보드 모두 True).
- **겹침 수 (`tools/overlaps.py`):** 글자 경계 상자가 교차하는 쌍을 센다. 라벨·자유 글자·보이는 필드가 대상이다.

| 보드 | 전 (합계 / 서로 다른 글자 / 같은 자리 같은 이름) | 후 |
|---|---|---|
| 캐리어 | 37 / **17** / 20 | 20 / **0** / 20 |
| 전면 | 17 / **9** / 8 | 8 / **0** / 8 |

- **남은 것:** 같은 넷의 겹친 핀(예: USB-C VBUS 4핀, 커넥터 GND)에 같은 이름 라벨이 같은 자리에 겹쳐 그려진 것이다. 화면에서는 라벨 하나로 보인다. 지우면 객체(UUID)가 줄어들어서 그대로 두었다.
- **판정:**
  - ERC: 두 보드 종료 0·위반 0
  - `tools/netcompare.py` C-012 `f56945b` 대비: 두 보드 차이 0 (종료 0)
  - 부품·DNP·UUID 변경 없음
- **그림:** `validation/runtime/kicad-gui/C-013/index.html`에 전후 PNG를 모았다(`kicad-cli sch export svg` → PyMuPDF PNG). 사람 눈 확인용이다(verifiable 아니오).

## 24. C-016 — 캐리어 32(PWR_WAKEUP1) 미연결 · 전면 R15 삭제 · J2 납땜 패드 (orch O-83 · O-84, R-019)

- **캐리어 BTB J1-32** (코어 J2 짝 핀, 넷 PWR_WAKEUP1):
  - ALS_INT_RSV에서 떼어 **no-connect**로 바꿨다. Seeed B301·B101과 같게 미연결이고 풀 저항도 없다(R-019).
  - 이유: ALS는 i2c-dev 폴링이다(D-003 #18). 또 이 핀은 코어 깨우기 입력이다.
  - 생성기 `boards.py`에서 `PWR_WAKEUP1`을 NC 목록에 넣었다.
- **ALS_INT_RSV:** 하니스 예비선으로만 남는다.
  - 캐리어: J7-4 · TP26
  - 전면: J4-3 · **TP24(새로)**
- **전면 R15 10k(ALS_INT_RSV → CORE_1V8) 삭제:**
  - LTR-329ALS-01에는 INT 핀이 없다. INT 있는 차선은 LTR-303ALS다.
  - 외부 10k를 CORE_1V8에 두면 셧다운 때 핀을 Low로 끌 위험이 있다(O-83).
- **전면 J2 (CLA216 ICR 리드):** PicoBlade 53261 → 2핀 2.54mm 스루홀 납땜 패드(O-84).
  - 풋프린트: `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`
  - 심벌: `Connector_Generic:Conn_01x02`. MP 핀이 없어져 GND 연결도 빠졌다.
  - 헤더는 실장하지 않는다. `in_bom no` · `in_pos_files no`
  - 1번 사각 패드 = ICR_A(극성 표시)
  - 생성기 `schgen.add()`에 `in_bom` 인자를 더했다.
- **UUID 유지:**
  - HEAD 파일에 생성기 출력을 줄 단위로 맞췄다. UUID·path를 가린 비교에서 같은 줄은 HEAD 원문을 쓴다.
  - 결과는 생성기 출력과 UUID만 빼면 같다.
  - 캐리어: UUID 792개 중 791개 유지, 새로 1개(no-connect)
  - 전면: 656개 중 653개 유지, 새로 3개(TP24). J2 심벌 UUID도 유지했다.
- **netcompare (C-015 `0c2e8e7` 대비), 의도한 차이만:**
  - 캐리어 3:
    - J1-32 → `unconnected-(J1-Pin_32-Pad32)`
    - ALS_INT_RSV {J1-32, J7-4, TP26} → {J7-4, TP26}
  - 전면 9:
    - COMP J2: 값·풋프린트
    - COMP R15 삭제
    - COMP TP24 추가
    - ALS_INT_RSV {J4-3, R15-2} → {J4-3, TP24-1}
    - GND에서 J2-MP 빠짐
    - CORE_1V8에서 R15-1 빠짐
- **판정:**
  - ERC 두 보드 종료 0
  - `contract_check.py` 계약 불일치 0
  - `--selftest` 18/18
  - 겹침(`tools/overlaps.py`) 보이는 겹침 0/0
  - 표제란 Rev 「C-016」
  - SVG: `validation/runtime/kicad-gui/C-016/`
- **BOM (넘김):** 전면 BOM을 다시 내보내면 J2·R15가 빠지고 TP24가 생긴다. 그러면 `bom-full.csv`(R-016 소유)에 J2·R15가 남아 `make_pcbway_bom.py`가 종료 1이 된다.
  - 그래서 이 레인에서는 `inputs/front-kicad-bom.csv`를 고치지 않았다.
  - bom-full 갱신과 함께 다시 내보내야 한다.

## 25. C-017 — SIM-001b 수정 반영 (orch O-87, firmware `a3b988c` `hardware/sim/SIM-001b-results.md`)

| # | 바꾼 것 | 이유 (SIM-001b) |
|---|---|---|
| S1 | 전면 Q7 드레인 → 새 넷 CAM_1V8_PD → **R18 1k** → CAM_1V8_G (Q6 게이트). **C19 10nF**를 Q6 게이트–드레인(CAM_1V8_G–CAM_1V8)에 둠 | 밀러 소프트스타트. CAM_1V8 돌입 5.11A → 0.133A, 켜짐 36µs |
| S2 | 캐리어 **R6 8.06k → 6.98k 1%** (TPS26600 ILIM ≈ 1.49A → 1.72A) | 두 스트링 켬 구간 맥놀이로 20µs 창 1.585A. 이전 ILIM 1.49A를 넘음 |
| S4 | 전면 **R19 10k** CAM_1V8 → GND 블리더 | 꺼진 CAM_1V8에서 SDA 0.42V → 0.16V. 켜졌을 때 180µA |
| S3 | 회로 변경 없음 (끔 구간 링잉 6mA, 기준 불합격 유지·bring-up 확인 항목) | O-87 |

- **계약 v1.13:**
  - 3.1 12V_IR·CAM_1V8 행, 12절 eFuse 행, 13절 C18 ②를 갱신했다.
  - FW 규칙 「IIC2 패드 내부 풀업 켜지 않음」을 넣었다(켜면 꺼진 센서로 11.8µA 역급전).
- **`contract_check.py`:**
  - Q7 → R18 → Q6 게이트, C19 게이트–드레인, R19 블리더를 대조한다.
  - 고장 주입은 20건이다.
- **netcompare (C-016 `1f632b6` 대비), 의도한 차이만:**
  - 캐리어 1: COMP R6 8.06k → 6.98k
  - 전면 10:
    - COMP C19·R18·R19 추가
    - CAM_1V8_G {Q6-1, Q7-3, R17-2} → {C19-1, Q6-1, R17-2, R18-2}
    - 새 넷 CAM_1V8_PD {Q7-3, R18-1}
    - CAM_1V8에 C19-2·R19-1 추가
    - GND에 R19-2 추가
- **UUID:**
  - 캐리어는 792/792 유지했다.
  - 전면은 653개 유지에 새로 18개(새 부품 3개)다.
  - SENS 블록에 부품이 늘어 그 블록 뒤 심벌 좌표가 옮겨졌다. UUID는 그대로라 PCB 링크에는 영향이 없다.
- **판정:**
  - ERC 두 보드 0
  - `contract_check.py` 불일치 0
  - `--selftest` 20/20
  - 보이는 라벨 겹침 0/0
  - Rev 「C-017」
- **주의 (orch로 넘김):** ILIM 6.98k이면 I(OL) 최대는 12/(6.98×0.99)×1.05 ≈ 1.82A다. 벅 입력 0.62A를 더하면 과부하 중 12V 입력 피크가 약 2.44A로, 어댑터 2.08A를 넘는다.
  - 계약 12절의 「과부하 때 합계가 어댑터 2.08A를 넘지 않게」와 어긋난다.
  - SIM-001a에서 어댑터 특성 항목(lead 추가 지시)으로 확인한다.

## 26. C-018 — R6 재계산 · S5 · U2 풋프린트 · .net 재생성 (orch O-91, 계약 v1.14)

| 바꾼 것 | 값 | 근거 |
|---|---|---|
| 캐리어 R6 (TPS26600 ILIM) | 6.98k → **6.04k 1%** (I(OL) 1.86~2.12A, 전형 1.99A) | SIM-001a A5 전류 순서 표(`hardware/sim/SIM-A5-current-order.md`). 12V_IR 피크 1.585A × 1.15 ≤ I(OL) 최소, I(OL) 최대 + 벅 입력 0.648A < GST40A12 OLP 최소 3.51A. 두 조건을 만족하는 E96 값 중 I(OL)이 가장 낮다 |
| 전면 R17 | 10k → **4.7k** | S5, SIM-001b′ `55480c0`: 꺼짐 47µs |
| 전면 C19 | 10nF → **4.7nF** | S5: 돌입 0.242A |
| 캐리어 U2 풋프린트 | `…_Mask2.66x2.46mm_ThermalVias` → `Package_SO:HTSSOP-16-1EP_4.4x5mm_P0.65mm_EP3.4x5mm_Mask2.66x2.46mm` | O-86 #21. 열 비아(Ø0.3)는 pcb가 배선할 때 넣는다 |
| `carrier/carrier.net` · `front/front.net` | kicad-cli `sch export netlist --format kicadsexpr`로 다시 내보냄 | f0745ed까지 C-013 상태로 남아 있었다(pcb 발견) |

- **계약 v1.14:**
  - 3.1 12V_IR 행: ILIM 6.04k, SIM-A5 근거
  - 3.1 CAM_1V8 행: R17 4.7k · C19 4.7nF
  - 3.2: 어댑터 GST40A12-P1J 3.34A
  - 12절: 어댑터 OLP 문구, 플러그 2.1×5.5 센터 +
- **netcompare (`5cbd1f3` 대비), 의도한 차이만:**
  - 캐리어: R6 값, U2 풋프린트
  - 전면: R17 값, C19 값
  - 넷 변화는 0이다.
- **UUID:** 두 보드 모두 전부 유지했다(792/792, 671/671).
- **판정:**
  - ERC 두 보드 0
  - `contract_check.py` 불일치 0
  - `--selftest` 20/20
  - 보이는 겹침 0/0
  - Rev 「C-018」

## 27. C-019 — SIM-001a B1·C3 수정 (orch O-93, 계약 v1.15)

| 바꾼 것 | 값 | 근거 |
|---|---|---|
| 캐리어 R2 / R3 (TPS54302 FB) | 100k / 13.3k → **78.7k / 10.7k 1%** | 최악 범위 4.770~5.196V, 전형 4.980V (VFB 0.581~0.611V × R ±1%) |
| 전면 Q1 게이트 | 새 넷 CAM_PG_IO: CAM_PG → **R20 1k** → Q1 게이트 | 밀러 소프트스타트 (C-017 S1과 같은 방식) |
| 전면 C20 · C21 | **4.7nF** Q1 게이트–드레인(CAM_PG_IO–CAM_IOVDD) · Q2 게이트–드레인(CAM_PG_AV–CAM_AVDD) | SIM-C3: CORE_3V3 강하 0.230V → 0.046V, IOVDD 10µs → AVDD 81µs |

- **R2/R3 고른 방법:**
  - E96 1% 조합을 모두 계산했다.
  - 최악 범위가 4.75~5.25V 안에 드는 조합 가운데, 범위의 가운데가 5V에 가장 가까운 것을 골랐다(가운데 4.983V).
  - 다음 후보:
    - 75k/10.2k: 4.768~5.194V
    - 105k/14.3k: 4.763~5.188V
    - 97.6k/13.3k: 4.760~5.185V
- **LCSC 재고 (2026-11-27, 공개 detail API):**
  - 78.7k 0402WGF7872TCE C67239: 2,100개 — 재고가 적은 편이다
  - 10.7k 0402WGF1072TCE C270654: 167,800개
  - 1k C11702
  - 4.7nF CC0402KRX7R9BB472 C106208
- **코어 VIN 하한:** 계약 3.1 「모듈 VIN」 행(코어 SCH 04 VBAT_DET 30k/15k)에서 VIN < 3.0V면 꺼진다. 최악 4.770V면 여유 1.77V다.
- **피드포워드:** C19 75pF와 R2가 만드는 영점이 21kHz → 27kHz로 옮겨 간다. SIM-B3에서 루프를 다시 확인한다.
- **netcompare (`89647b4` 대비), 의도한 차이만:**
  - 캐리어: R2·R3 값
  - 전면:
    - R20·C20·C21 추가
    - Q1-1이 CAM_PG에서 새 넷 CAM_PG_IO {C20-1, Q1-1, R20-2}로 옮김
    - CAM_PG {Q3-3, R20-1, R4-2, R5-1}
    - CAM_PG_AV +C21-1
    - CAM_IOVDD +C20-2
    - CAM_AVDD +C21-2
- **UUID:**
  - 병합을 객체 단위로 바꿨다. 심벌은 레퍼런스별로 HEAD UUID와 핀 UUID를 그대로 쓴다. 라벨·선은 모양이 같으면 HEAD UUID를 쓴다.
  - 두 보드 심벌 UUID 변경은 0이고, 새로 생긴 것은 R20·C20·C21뿐이다.
  - **알림:** C-017(`f0745ed`)의 줄 단위 병합에서 전면 **X1 심벌 UUID가 바뀌었다** (`2a3e25ba…` → `7b69cce2…`). pcb는 X1 링크를 확인해야 한다. 그 뒤 C-018·C-019에서는 바뀌지 않았다.
- **판정:**
  - ERC 두 보드 0
  - `contract_check.py` 불일치 0(388줄)
  - `--selftest` 22/22
  - 보이는 겹침 0/0
  - Rev 「C-019」

## 28. C-020 — 카메라 레일 순서 S6 (orch O-97, SIM-001c ② firmware `43eb4f7`, 계약 v1.16)

- **문제:** Q1(IOVDD)·Q2(AVDD)가 같은 CAM_PG로 거의 동시에 움직인다.
  - 끌 때 IOVDD가 AVDD보다 2.31ms 먼저 떨어진다. GC2053 §9.3은 IOVDD가 마지막이어야 한다.
  - 켤 때 AVDD−IOVDD가 최악 1.0µs다. §9.2는 t1 ≥ 50µs다.
- **바꾼 것 (전면, 게이트 비대칭 RC):**

| 부품 | 값 · 결선 | 동작 |
|---|---|---|
| R20 | 1k → **100k** (CAM_PG–CAM_PG_IO) | Q1을 끌 때 천천히 → IOVDD 마지막 |
| R21 (새) | 1k (CAM_PG_IO–CAM_PG_IOD) | D4와 직렬 |
| D4 (새) | BAT54WS, 애노드 CAM_PG_IOD → 캐소드 CAM_PG | Q1을 켤 때 게이트를 빨리 끌어내림 → IOVDD 먼저 |
| R5 | 10k → **100k** (CAM_PG–CAM_PG_AV) | Q2를 켤 때 천천히 → AVDD 나중 |
| D5 (새) | BAT54WS, 애노드 CAM_PG → 캐소드 CAM_PG_AV | Q2를 끌 때 게이트를 빨리 올림 → AVDD 먼저 꺼짐 |

- **극성 확인:**
  - P-FET라 게이트 Low일 때 켜진다. Q3가 CAM_PG를 끌어내리면 켜지고, R4 100k가 올리면 꺼진다.
  - D4는 CAM_PG가 Low일 때 순방향이다(Q1을 빨리 켬). D5는 CAM_PG가 High일 때 순방향이다(Q2를 빨리 끔).
  - firmware 문서 원문의 방향(「CAM_PG_IO → CAM_PG」 「CAM_PG → CAM_PG_AV」)과 같다.
  - 검증(firmware, 같은 모델 최악 4경우):
    - 켤 때 AVDD−IOVDD 180µs
    - 끌 때 IOVDD−AVDD 1.1ms
    - CORE_3V3 돌입 310mA, 최저 3.269V
- **netcompare (`cdabf3c` 대비), 의도한 차이만:**
  - 캐리어: 0
  - 전면:
    - R5·R20 값
    - R21·D4·D5 추가
    - CAM_PG +D4-1(K)·D5-2(A)
    - CAM_PG_IO +R21-1
    - CAM_PG_AV +D5-1(K)
    - 새 넷 CAM_PG_IOD {D4-2(A), R21-2}
- **UUID:** 심벌 UUID 변경 0(객체 단위 병합). 새로 생긴 것은 R21·D4·D5뿐이다.
- **`contract_check.py`:**
  - 저항 「Rn 값(넷–넷)」과 다이오드 「Dn BAT54(애노드 → 캐소드)」를 대조하는 항목을 더했다(393줄).
  - 고장 주입 24건이다(D5 극성 뒤집힘, R20 값).
- **판정:**
  - ERC 두 보드 0
  - contract_check 불일치 0
  - selftest 24/24
  - Rev 「C-020」
- **남은 것:**
  - 모듈 BXF4677 안 LDO의 지연은 모른다. 실물 순서는 bring-up에서 IOVDD·AVDD를 프로브로 확인한다.
  - BOM 반영이 필요하다: BAT54WS ×2, 1k, R5·R20 100k.

## 29. C-021 — IR LED 끔 구간 블리더 (orch O-99, SIM-001e firmware `8591271`, 계약 v1.17)

- **바꾼 것 (전면):**
  - R22 10k 1% 0402 — IRA_SET–IRA_K, 스트링 A LED 2개 양단
  - R23 10k 1% 0402 — IRB_SET–IRB_K, 스트링 B
- **근거:**
  - 끈 뒤 L 47µH와 접합 용량이 2.84MHz로 공진해 LED에 순방향 꼬리 전류가 흐른다(스트링당 평균 0.84mA).
  - 블리더를 넣으면 끔 구간 |I|가 6.1mA에서 1.4µA로 준다.
  - 대가: 효율 −0.081%p, LED 전류 −0.1% 이내, 소비 4.4mW. 양단 전압은 최대 약 6.7V다.
  - 후보 8종 중 이것만 합격했다. FW 변경은 없다.
- **계약 v1.17:**
  - 3.2 「IR LED 조건」에 블리더와 근거를 넣었다.
  - SIM-001b S3 「발광 아님」을 정정했다(실제로는 LED 순방향 꼬리).
- **netcompare (`491e72a` 대비), 의도한 차이만:**
  - 캐리어: 0
  - 전면: R22·R23 추가, IRA_SET·IRA_K·IRB_SET·IRB_K에 각 1핀
- **UUID:** 심벌 변경 0. 새로 생긴 것은 R22·R23뿐이다.
- **`contract_check.py`:** 저항 대조에서 값 뒤의 「1%」 꼬리표를 떼도록 고쳤다. 고장 주입은 25건이다(R23 넷 바꿈).
- **판정:**
  - ERC 두 보드 0
  - contract_check 불일치 0(395줄)
  - selftest 25/25
  - 보이는 겹침 0
  - Rev 「C-021」

## 30. C-022 — openhw 라이브러리 2건 (orch O-101, mechanical M-009 `f7fd41e`)

- **바꾼 것:**
  - 전면 J2 풋프린트 → `openhw:CLA216_ICR_SolderPads_1x02_P2.54mm` (헤더 몸체 없는 2패드, courtyard 패드 + 0.25). 핀 번호·넷(1 □ = ICR_A, 2 = ICR_B)·BOM/CPL 제외는 그대로다.
  - `openhw:M12_Holder_20mm_CLA216-ICR`(MH1) F.CrtYd → 16점 외형(뒷면 BTB 고정 핀 NPTH 두 곳 노치, 구멍까지 0.100). 자세한 것은 `hardware/libraries/README.md` 「C-022 추가」.
- **netcompare (`613cf14` 대비), 의도한 차이만:**
  - 캐리어: 0
  - 전면: J2 풋프린트 이름 1건
- **UUID:** 심벌 변경 0.
- **판정:**
  - ERC 두 보드 0
  - contract_check 불일치 0, selftest 25/25
  - `kicad-cli fp upgrade` 종료 0
  - `.net` 재생성, 보이는 겹침 0
  - Rev 「C-022」
