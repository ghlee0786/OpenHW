# V-004 C-002 회로도 독립 검토 (README 단계 4)

- 배정: orch t18r V-004 · 검토자: review t18y (Opus 5.5 high) · 레인 t-20261126-172041-ddef · 확인일 **2026-11-26**
- **기준 커밋:**
  - 본 검토: C-002 레인 t-20261126-165741-b193 **276fc89**
  - C-003 추가 절: **7f69f63** (C-002b 4dc59dc는 orch netcompare 차이 0 → 본 검토 유효)
  - 두 커밋 모두 `git archive`로 scratchpad에 풀어 그 사본만 검토했다. 수정 중인 작업 트리는 보지 않았다.
- 대조 기준:
  - 계약 v1.2 (레인 t-20261126-155208-d030, fd12ba4)
  - Seeed 검증 보드 B301·B101·S401 원본
  - 코어 회로도 PDF
  - SG2002 핀표·HDG·TRM (R-005 보관본)
  - 각 부품 제조사 데이터시트 원문
- 방법:
  - 회로도 README 결론은 전제로 쓰지 않았다.
  - `carrier.net`·`front.net`을 파싱해 실제 핀 연결을 뽑고, 데이터시트 값으로 계산·판정했다.
  - 판정 근거가 된 부적합 연결은 검토자가 넷리스트에서 다시 확인했다.
- 수정하지 않은 것: 제품 파일, 저장소, KiCad 설치 폴더.
- 실측: 없음. 「적합」은 회로·데이터시트 기준이며 실물 기능 통과가 아니다.

## kicad-cli ERC 재실행

| 기준 | 명령 | 종료 코드 | 위반 |
|---|---|---|---|
| 276fc89 | `kicad-cli sch erc --severity-all --format json -o erc_carrier.json <snap>/carrier/carrier.kicad_sch` | 0 | 0 |
| 276fc89 | 같은 명령 · `front/front.kicad_sch` | 0 | 0 |
| 7f69f63 | 같은 명령 · `carrier.kicad_sch` | 0 | 0 |
| 7f69f63 | 같은 명령 · `front.kicad_sch` | 0 | 0 |

ERC 0은 연결 규칙 통과일 뿐이다. 아래 부적합(전원 순서·역급전·부품값)은 ERC가 잡지 못하는 종류다.

## 판정표

| # | 항목 | 판정 | 핵심 근거 (넷리스트 · 데이터시트) |
|---|---|---|---|
| P1 | 입력 보호: J2 잭 · F1 3A · Q1 AO4407A 역접 · D1 제너 · D2 SMBJ15A · C1 | **적합** (부품 2건 부적합, MPN 확인 불가) | Q1 D=12V_IN_F(퓨즈 쪽), S=12V_IN. 역접 시 VGS≈0으로 차단. D1은 G–S 사이(BZT52C12 11.4~12.7V < AO4407A VGS ±25V). D2는 FET 뒤 12V_IN–GND, 캐소드=12V_IN. 최악 1.84A ÷ 0.75 = 2.45A < F1 3A. **J2 풋프린트·D2 심벌 부적합**(수정안 S5·S6). F1·C1 MPN 없음 |
| P2 | TPS54302 (U1) FB·인덕터·입출력 C·부트스트랩 | **조건부** (Cff 부적합) | 핀 1 GND · 2 SW · 3 VIN · 4 FB · 5 EN 개방(「Float the EN pin to enable」) · 6 BOOT–SW 100nF. Vout = 0.596×(1+100/13.3) = 5.08V. SLVSDG6C Table 7-2(5V: L 10µH · COUT 44µF · 100k/13.3k · **C 75pF**)와 비교하면 **Cff 75pF 없음**. C7·C8은 22µF/**10V** → DC 바이어스로 실효 약 24µF, fo ≈ 42kHz > 「less than 40kHz」 |
| P3 | TPS26600 (U2) SHDN/UVLO/ILIM 8.06k/dVdT | **적합** (권고 1건) | SHDN ← IR_LED_EN + R5 10k 풀다운: 0.4V에서 40µA ≥ 10µA, Hi-Z 시 ≤ 0.1V < V(SHUTF) 0.55V. UVLO→IN(원문 「must be connected to the IN terminal」). OVP·MODE→RTN(=GND): 내장 OVP 31~34V, 「Active current limiting with auto-retry」. RTN=GND는 U2가 Q1 뒤라 허용. ILIM 12/8.06 = 1.49A(공차 1.40~1.58A). 2스트링 최악 1.22A, 12V 합계 1.845A < 어댑터 2.08A. dVdT 22nF → 2.11ms |
| P4 | 전원 LED · 5V_SYS→BTB | **적합** | 5V_SYS → 캐리어 J1 29·31·33·35 (계약 4절 VIN 4핀) |
| P5 | 계약 12절 보호 | **부적합** | 「5V_SYS: 5V 출력 TVS (5.6~6V급)」가 회로에 없다. 5V_SYS 노드는 C7·C8·J1·L1·R2·R21·R4·TP2뿐 |
| D1 | 전면 3.3V LDO U1 (RT9013-33GB, 심벌 AP2112K) | **적합** (기록 정정) | 핀 1 VIN · 2 GND · 3 EN=VIN · 5 VOUT. **4번은 BP가 아니라 NC**(DS9013-10, 「Without Bypass Capacitor」). 부하 2.5mA 미만. 데이터시트는 2011년 미러본(공식 다운로드 실패) |
| D2 | DRV8837 (U2) VM 5V · VCC · IN 레벨 | **조건부** | VM 5V(0~11V), VCC 3.3V(1.8~7V), IN1(IR_CUT, 3.3V 추정)은 VCC와 무관하게 5.5V까지 허용, nSLEEP 3.0V, 코일 0.258A ≪ OCP 1.9A, VM·VCC 바이패스 100n 있음. **IN2 ← WH_PWM 1.8V: VIH max 0.5×VCC = 1.65~1.68V → 최악 여유 27mV** |
| D3 | AL8860 ×2 (U4 실장 · U5 DNP) Rs · CTRL 공유 · 인덕터 · 다이오드 | **회로 적합 · 극성 문구 부적합 · 부품 조건부** | 12V_IR → R13 0.1Ω → SET → LED A → LED → L1 68µH → SW, D1 K=12V_IR / A=SW로 DS39014 응용회로와 같음. 1.0A(0.96~1.04), 듀티 53~65%(권장 25~75%), ton ≥ 4.8µs. **IR_PWM Low → Q5 off → CTRL floating → LED 켬**(원문 「Leave floating for normal operation」). 계약 7절 「Low = 끔」과 반대. L1 Irms 여유 6%(SRN6045TA-680M 가정), D1 SS24 패키지 미정 |
| D4 | DMG1012T 1.8V 게이트 (Q3·Q4·Q5 등) | **적합** | VGS(th) 0.5~1.0V, RDS(on) ≤ 0.7Ω @1.8V (DS31783 Rev 8-2) — C2-9 미확인 해소 |
| D5 | VSMA1085400 극성 · 직렬 · 스트링 B DNP | **적합** | A=SET 쪽, K=L 쪽, 풋프린트 Pad1=K. B 관련 부품 모두 DNP |
| S1 | DF30 J3 ↔ S401 J2 ↔ 계약 5.1 | **적합** | 24핀이 S401과 같은 넷이다. 다른 점은 MCLK 직렬 22Ω과 RESET 회로뿐이다. 풋프린트 패드 좌표가 S401과 같다 |
| S2 | 카메라 전원 Q1·Q2(AO3401A)·Q3 · BXF4677 IOVDD | **적합** (조건: C6 DNP 유지) | P-FET S=CORE_3V3, D=부하, CAM_EN High→Q3 on→VGS −3.3V. 강하 약 5mV. IOVDD(J3-14)는 3.3V 전원 입력으로 맞다. **C6을 실장하면 AVDD/DVDD가 IOVDD보다 약 14ms 늦게 꺼져 GC2053 9.3절 전원 끄는 순서를 어긴다** |
| S3 | RESET RC (R7 10k · C10 DNP) | **부적합** | C10 DNP면 RESET이 CAM_EN과 함께 수 µs 안에 1.8V가 되어 내부 레일보다 먼저 오를 수 있다. GC2053 9.2절(IOVDD→DVDD/AVDD ≥50µs → PWDN → RESETB)과 어긋나고, 끌 때도 RESET이 먼저 떨어지지 않는다 |
| S4 | I2C2 풀업 상시 CORE_1V8 — 역급전 | **부적합** | 넷: R9·R10.1 = /CORE_1V8(상시), .2 = SDA/SCL → J3-1/3. CAM_EN=0이면 모듈 3.3V가 꺼진다. 이때 풀업이 센서 I/O ESD 다이오드를 거쳐 꺼진 레일로 흐른다(선당 약 0.26mA). 버스 High가 「꺼진 레일 + Vf」로 묶여 LTR-329 폴링도 보장되지 않는다. GC2053 데이터시트에는 절대최대·전원 꺼짐 입력 허용 문구가 없다. S401 원본은 스위칭 CAM_1V8에 풀업한다 |
| S5 | 24MHz 발진기 X1 (VDD CORE_1V8 상시, OE=CAM_EN) | **적합** (메모 2건) | YSO110TR 「Disable (Low) 30% of VDD Max」 Tri-State(Hi-Z는 추론) → 꺼진 모듈 MCLK로 역급전 없음. VIH 0.7·VDD = 1.26V < 1.8V. 풋프린트 핀 순서 1 OE · 2 GND · 3 OUT · 4 VDD 일치. 메모: OE 내부 풀업 추정 + R6 100k → 부팅 중 CAM_EN 중간 전위 가능. 계약 9절(CAM_1V8)과 6절·C2-7(CORE_1V8)이 서로 다르다 |
| S6 | LTR-329 (VDD 3.3V · 1.8V 버스 직결) | **적합** | 원문: VIO(Interface Bus Power Supply) 1.7~3.6V, SDA/SCL 절대최대 3.8V. 0x29 ≠ 0x3f |
| I1 | EPHY MDI → HR911105A (센터탭) | **적합** | 코어 패드 65 `PAD_ETH_RXM_EPHY_TXP` → PHYTXP → R85 → **EPHY_TXP가 송신쌍**(이름 교차는 패드 명명 탓). TXP/N→J5.1/2(TD±), RXP/N→J5.3/6(RD±)로 B301 T1 연결과 같다. 센터탭 C15·C16 DNP(B301도 DNP), 핀 8 「CHS GND → PCB Ground」 원문대로. 실드 R18 1M ∥ C17 1nF/2kV는 B301과 같은 구조. Auto-MDIX는 TRM 18.2.2 |
| I2 | USB-C · ESD | **조건부** | CC 5.1k×2, D± 묶음, USBLC6 1·6 D+ / 3·4 D− / 5 VBUS. VBUS는 5V_SYS와 분리(C4). USB_DET 20k/10k → 1.67V > VIH 1.26V. **12V 없이 USB만 꽂으면 전원 없는 SoC 핀으로 약 0.17mA 역급전**. USBLC6 VBUS 핀 경로는 확인 불가 |
| I3 | microSD DM3AT | **부적합 1건** (나머지 적합) | 핀 1 DAT2 … 9 DET_B→SDIO_CD · 10 DET_A→GND, 감지 「Normally Open」. 극성은 B101과 같다. 풀업 DNP는 B101·B301과 같다. ESD 7선. **Q2 게이트를 Q3가 곧바로 끌어내리고(SD_PWR_G = Q2.1 · Q3.3 · R11), 출력 C13 10µF에 방전 저항이 없다.** 입력 CORE_3V3는 SoC·eMMC와 공유하는 1A 레일이고 BTB 1핀(J1-27)으로만 들어온다 → 돌입 전류로 레일이 처질 위험. B101은 47k + 100nF 소프트스타트, 부하 1µF, 방전 100k |
| I4 | BTB 짝 핀 홀짝 반전 | **적합** (불일치 0) | 코어 07 시트를 렌더링해 60핀×2를 옮겨 적고 「우리 m ↔ 코어 m±1」로 전수 대조했다. 캐리어 45 일치 + 15 NC, 전면 39 일치 + 21 NC. 같은 쪽 검증 보드(B301 J1, S401 J1)와도 60핀 같다. 계약 4·5절과 같다 |
| I5 | FPC 대칭 핀배치 (276fc89) | **배치 적합 · 정격 조건부 → C-003에서 대체** | 두 보드 1 GND · 2·3 12V_IR · 4 GND · 5 SPARE1 · 6 ALS_INT_RSV · 7 GND · 8·9 12V_IR · 10 GND로 n↔11−n 대칭(5↔6만 바뀜). TE 108-1393 「Signal application only」 정격 문제(V-003) → C-003이 JST GH 6P로 교체(아래 절) |
| I6 | 디버그 UART · 버튼 · 상태 LED · 시험점 | **적합** | J6 1 GND · 2 TX · 3 RX. SW2 누름 0.58V < VIL 0.99V. 계약 11절 시험점 모두 있음 |

## 부적합·조건부의 수정안

### 회로도 담당(schematic, C-002 레인)에게

| # | 대상 | 수정안 | 근거 |
|---|---|---|---|
| **R1** | I2C2 풀업 역급전 (S4) | S401 방식으로 되돌린다: CORE_1V8 → CAM_1V8 P-FET 스위치(게이트 = CAM_PG; VGS −1.8V에서 RDS(on)이 규정된 소자, **AO3401A는 VGS(th) max −1.3V라 부적합**). R9·R10을 CAM_1V8에 연결한다. LTR-329는 CAM_EN=1일 때만 폴링한다(계약 6절 FW 기본 CAM_EN 상시 1). 차선(I2C 버퍼·CAM_EN 하드웨어 상시 1)은 이점이 없거나 RESET 문제를 키운다 | GC2053 데이터시트 무근거 · S401 |
| **R2** | MCLK 발진기 X1 (S5 연계) | R1을 적용하면 X1 VDD(C11 포함)도 CAM_1V8로 옮긴다. 계약 9절과 일치하고, OE 중간 전위 메모도 사라진다. R1을 하지 않으면 R6을 10k로 낮춘다 | YSO110TR · 계약 9절 |
| **R3** | RESET RC (S3) | C10 100nF를 실장한다(τ 1ms, VIH 1.26V까지 약 1.2ms). R7에 병렬로 쇼트키 다이오드를 단다(캐소드 → CAM_EN) — 끌 때 RESET이 먼저 Low가 된다. CAM_RESET → GND 10k 자리(DNP)를 둔다(S401 R7 패턴, 실물 측정 후 결정) | GC2053 9.2·9.3절 |
| **R4** | TPS54302 Cff · 출력 C (P2) | 75pF C0G(≥16V)를 5V_SYS–BUCK_FB 사이(R2 병렬)에 넣는다. C7·C8은 22µF **25V** X7R(데이터시트 예와 같음)로 바꾸거나 22µF를 하나 더 넣어 실효 44µF 이상을 확보한다(DC 바이어스 곡선으로 확인) | SLVSDG6C Table 7-2, Eq.14·16 |
| **R5** | 5V_SYS TVS (P5) | 5V_SYS–GND에 VRWM 5.0V 단방향 TVS(SMBJ5.0A/SMAJ5.0A급, VBR ≥ 6.4V)를 넣는다. 넣지 않으려면 계약 12절을 개정한다(C-001) | 계약 v1.2 12절 |
| **R6** | J2 DC 잭 풋프린트 (P1) | XKB DC-005-5A-2.0 도면대로 전용 풋프린트를 만든다: 1–2 간격 5.90, 3은 1에서 3.0·직각 4.70, 슬롯 1.0×3.5, 공차 ±0.05. 현재 일반형 BarrelJack_Horizontal은 6.0 간격·드릴 1×3이다 | XKB 도면 Rev A1 (LCSC C381116) |
| **R7** | D2 심벌 (P1) | `Device:D_TVS`(양방향)를 단방향 심벌(K=1, A=2)로 바꾼다. 현재 극성(D_SMB 패드 1 = 캐소드 = 12V_IN)은 맞으므로 유지한다 | SMBJ15A 단방향 |
| **R8** | microSD 전원 스위치 (I3) | Q3 드레인–Q2 게이트 사이에 47k를 넣고, Q2 G–S에 100nF를 단다(τ ≈ 4.7ms). C13을 1µF로 줄이거나(10µF를 유지하면 소프트스타트는 필수), SD_PWR_3V3–GND에 100k 방전 저항을 단다 | B101 R20·C8·R21 |
| **R9** | DRV8837 IN2 여유 (D2) | U1을 RT9013-**28**GB(2.8V)로 바꾸면 VIH max 1.43V로 여유가 0.28V 이상이 된다(LTR-329 VDD 2.4V 이상 충족, 재고 확인 필요). 또는 IN2를 3.3V 도메인 GPIO로 옮긴다 | SLVSBA4F VIH 0.5×VCC |
| **R10** | AL8860 주변 부품 (D3) | L1·L2: Irms ≥ 1.3A로 지정한다(예 SRN6045TA-470M 47µH, Irms 1.6A, Isat 2.0A — 33~100µH 범위). D1·D2: D_SMA 풋프린트에 맞게 SMA 패키지 SS24 MPN을 정한다. C14·C16: X7R 35~50V(또는 2개 병렬) | DS39014 · Bourns · Vishay |
| **R11** | USB_DET 역급전 (I2) | R9/R10을 200k/100k로 키우거나, B301처럼 5V_SYS(모듈 VIN) 기준으로 바꾼다(그러면 항상 Device). USBLC6 핀 5를 5V_SYS로 옮기고 VBUS TVS를 따로 두는 차선도 있다 | SG2002 핀표(USB_DET 1.8V IO, fail-safe 아님) · B301 |
| **R12** | 기록·MPN | U1 노트 「pin4 BP」 → 「NC」. D1 노트 「Vgs ±20V」 → 「±25V」. VSMA 도면 번호 정정(1085400 패키지 6.550-5367.01-4). TPS54302 L1 Isat ≥ 6A(전류 제한 상한 6A). F1(3A, ≥32V, 지연형) · C1(리플 전류, 35V 권장) MPN을 정한다 | 각 데이터시트 |
| **R13** | C6 (S2) | C6은 **DNP로 유지**한다는 주석을 넣는다(실장하면 전원 끄는 순서 위반) | GC2053 9.3절 |

### 계약 담당(C-001)에게

| # | 대상 | 수정안 |
|---|---|---|
| K1 | 7절 IR_PWM 행 | 「Low = 끔」 → **「전기 High = LED 끔 · Low/Hi-Z = 켬(CTRL 개방)」**으로 고친다. FW 규칙: PWM 극성 반전, **IR_LED_EN을 올리기 전에 IR_PWM을 High로 둔다**. 하드웨어로 막으려면 R12 100k를 CORE_1V8 풀업으로 바꿔 기본을 끔으로 한다(PAD_ZQ 리셋 풀 상태는 미확인) |
| K2 | 6절 · 9절 | R1·R2를 적용하면 「I2C2 상시 1.8V 풀업」 분기(C2-6)를 되돌리고, X1 전원을 9절(CAM_1V8)로 통일한다 |
| K3 | 3.1절 레일 표 | 「12V_IR 1.0A 연속」 → v1.2 2스트링 1.22A · ILIM 1.49A로 갱신한다 |
| K4 | 12절 | R5를 적용하지 않으면 5V TVS 행을 개정한다 |

### 권고 (부적합 아님)

- **TPS26600 MODE:** IR 쪽 과부하에서 eFuse가 1.40~1.58A로 계속 전류를 제한하면 벅 0.625A와 합쳐 2.03~2.20A가 되어 어댑터 2.08A를 넘을 수 있다. 시스템 전체가 꺼지는 것을 막으려면 MODE를 개방(circuit breaker + auto-retry)으로 하는 안을 검토한다.
- **CAM_EN 부팅 상태:** OE 내부 풀업과 R6 100k 분압으로 부팅 중 CAM_EN이 중간 전위가 될 수 있다. R1·R2를 적용하면 해소된다.
- **TPS54302 Vout 공차:** 1% 저항까지 넣은 최악값 4.86~5.30V로, 상한이 계약 ±5%를 0.05V 넘는다. 0.5% 저항을 검토한다.

## C-003 추가 확인 (7f69f63)

넷 비교(276fc89 → 7f69f63):
- 부품 수·넷 수가 같다(캐리어 91/93, 전면 78/64).
- 바뀐 것은 다음뿐이다(검토자가 `netdiff.txt`에서 직접 확인).
  - 캐리어 J7·전면 J4: TE 1-84952-0 10P → **JST SM06B-GHS-TB 6P**
  - 전면 U2·U4·U5 풋프린트 교체
  - GND·12V_IR·SPARE1·ALS_INT_RSV의 J7/J4 핀 번호
- 사라지거나 생긴 넷은 없다.

| # | C-003 의도 변경 | 판정 | 근거 |
|---|---|---|---|
| C1 | 보드 간 FFC → JST GH 6P | **적합** (권고 1건) | 양 보드 1 GND · 2 12V_IR · 3 SPARE1 · 4 ALS_INT_RSV · 5 12V_IR · 6 GND · MP GND. 전원·GND가 n↔7−n 대칭이라 케이블 방향과 무관하다. 1:1 케이블에서 3·4가 제자리로 가고, 뒤집히면 두 1.8V 예비선만 바뀐다. JST eGH.pdf(sha256 b1dcb317…b722) 원문 「Current rating: 1.0 A AC/DC (AWG #26)」 · 「50 V AC/DC」 · 「AWG #30 to AWG #26」. 12V_IR 1.22A ÷ 2 = 0.61A/접점, 접점 저항이 최악으로 치우쳐도 약 0.84A < 1.0A. GND 귀환도 2접점. **권고: 정격은 AWG26 기준이므로 BOM에 짝 케이블(GHR-06V-S + SSHL-002T-P0.2, AWG26, 1:1 결선)을 명시한다** — 시중 GH 케이블은 AWG28이 흔하다 |
| C2 | AL8860 Diodes 권장 랜드 파생 | **적합** | 피치 0.65, 신호 패드 1.35×0.45, 외곽 ±2.65(= Y2 5.30), EP 1.7(열 가로)×2.0(열 방향), EP–패드 0.45 → V-003에서 직접 확인한 Diodes 권장값(C 0.650 · G 0.450 · X 0.450 · X1 2.000 · Y 1.350 · Y1 1.700 · Y2 5.300)과 모두 일치. 핀 1 왼쪽 위, EP 9 = GND. U4·U5가 사용 |
| C3 | DRV8837 풋프린트 사본·3D | **적합** (3D 정렬은 verifiable 아니오) | 공식과 패드가 같다(descr·model 두 줄만 다름). 3D `${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.step`이 실제로 있다(99,885 B). U2가 사용. 핀 1 방향 3D 정렬은 사람 눈 확인이 필요하다 |
| C4 | M12 홀더 NPTH Ø1.8 | **적합** (체결 방향 확인 불가) | NPTH Ø1.8 ×2 (±10.0, 0). 속성 Commonlands CLA216-ICR(Arducam은 descr 설명 문구에만 남음). ISO 273 M1.6 여유 구멍 fine 1.7 / **medium 1.8** / coarse 2(IS 1821:1987 = ISO 273-1979 표). CLA216 실제 나사 규격·체결 방향은 Commonlands 429·DocSend로 원문 미확인 |
| C5 | BTB courtyard·실크 | **적합** | 패드·NPTH 62개는 이전과 같다(전기 불변). courtyard 18.3×6.4 ≥ 권장 18.2×6.3. scratch 보드 `kicad-cli pcb drc` 종료 0: silk_over_copper **0**(이전 라이브러리 대조군 120), courtyard 위반 0 (`lib_footprint_issues` 5건은 scratch 보드에 openhw 라이브러리를 등록하지 않아서 나는 경고) |
| C6 | .kicad_pro 넷클래스 | **적합** (참고 2건) | 클래스 8 · 패턴 13이 P-002 99790d9 `netclasses.json`(c6c272f9…441b)과 같다. 12V_IR → PWR_12V_IR 0.6mm 등이 정상 적용된다. 참고: ① P-002 레인 작업본에 미커밋 수정(`*MDI_*` 삭제)이 있어 커밋되면 어긋날 수 있다. ② IR 전류 경로(IRA_SW·IRA_K·IRA_M)는 Default 0.2mm → P-003에서 폭을 지정한다. `OpenHW_Mech` 경로 `hardware/pcb/lib`는 이 커밋에 없다 |

- 경미: 회로도 README C2-3(353행 부근)에 옛 FFC 10P 배치가 남아 있다. 「C-003으로 대체」라고 표기하기를 권한다.
- C-003으로 I5(FPC 정격 문제)는 해소됐다. 본 검토의 R1~R13은 C-003에서 바뀌지 않았다(넷 비교 결과 해당 넷 변화 없음).

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| V1 | 검토 기준 | 276fc89·7f69f63을 `git archive`로 고정한 사본 | 작성 레인이 수정 중이라 작업 트리를 보면 기준이 흔들린다 | — |
| V2 | 판정 기준 | 넷리스트 + 데이터시트 원문 + 검증 보드(B301·B101·S401) 대조 | 작성자 README·계약 문구가 서로 어긋나는 곳(9절 vs 6절)이 있다 | — |
| V3 | I2C 역급전 판정 | GC2053 데이터시트에 허용 근거가 없어 「부적합」 | 근거 없는 꺼진 칩 입력 인가는 위험으로 본다. 검증 보드 S401은 스위칭 레일을 쓴다 | 실물 측정으로 무해함이 확인되면 완화 |
| V4 | IR_PWM 극성 | 회로가 아니라 **계약 문구**의 부적합으로 분류 | 회로는 데이터시트 CTRL 용법대로다. 계약 표의 기본 상태 문구가 반대다 | R12를 풀업으로 바꿔 하드웨어 기본을 끔으로 |
| V5 | RT9013 데이터시트 | 2011년판 미러(DS9013-10) 사용 | Richtek 공식 PDF 경로가 모두 404였다 | 사람이 공식 최신판으로 재확인 |

## 남은 확인 (verifiable 아니오 또는 자료 부족)
1. DRV8837 3D 모델 핀 1 정렬(사람 눈)
2. CLA216 나사 규격·체결 방향 (Commonlands 도면)
3. SoC SD0·USB D+ 풀업이 VBUS 없을 때 동작하는지 (FW F-002)
4. RT9013·HRO·USBLC6 공식 최신 데이터시트 (다운로드 실패 — 미러/공식 심벌로 대조)
5. CORE_3V3 1A 레일 전체 예산 (코어 자체 소비 미상)
6. 모든 판정은 실물 측정 전이다. bring-up에서 RESET 순서, I2C 레벨, 5V 리플·과도, eFuse 동작을 측정한다

## 증거 파일
모두 `C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\2304a8aa-eb88-41c3-9975-aa6fda3de30c\scratchpad\v004\` 아래에 있다.

| 위치 | 내용 |
|---|---|
| `snap\` | 276fc89 사본 |
| `snap2\` | 7f69f63 사본 |
| `erc_*.json`, `erc2_*.json` | ERC 결과 |
| `power\` | 전원 갈래: AO4407A, BZT52C, SMBJ(LCSC 사본), XKB 도면, 넷 추출 |
| `drive\` | 구동 갈래: DMG1012T, SS24, SRN6045TA, RT9013 미러, 파서 |
| `sensor\` | 센서 갈래: AO3401A, YSO110TR, 렌더 이미지 |
| `iface\` | 인터페이스 갈래: HR911105A, TPD4E05U06, BTB 전수 대조 `btbcheck.py`, 코어 07 시트 렌더 |
| `c003\` | C-003 갈래: `netdiff.txt`, eGH.pdf, IS 1821 표, `drc\`, `drc_old\` |

## 돌린 명령
- kicad-cli:
  - `sch erc` 4회: 위 표, 모두 종료 0 · 위반 0
  - `pcb drc`(C-003 scratch 보드, 새 라이브러리·이전 라이브러리 대조): 종료 0 / 0
  - B101 넷리스트 추출: 종료 0
- 저장소 테스트·빌드 명령: 돌리지 않음(이 레인은 문서 1개만 추가하고, 하네스 검사가 「찾지 못했다」로 나옴)
