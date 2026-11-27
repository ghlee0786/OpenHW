# V-004b C-004 수정분 재검토

- 배정: orch t18r V-004b · 검토자: review t18y (Opus 5.5 high) · 레인 t-20261126-180645-0fa1 · 확인일 **2026-11-26**
- **기준 커밋:**
  - 회로도: C-002 레인 t-20261126-165741-b193 **58eb49b** (수정 전 비교 기준 **7f69f63**)
  - 계약 v1.4: 레인 t-20261126-155208-d030 **d159068**
  - 두 회로도 커밋은 `git archive` 사본으로 검토했다.
- 대상: V-004(`validation/review-V004-C002.md`, 레인 t-20261126-172041-ddef, 26b46b3)의 R1~R13 · K1~K4 · 권고 MODE
- 방법:
  - 회로도 README 16절은 참고만 했다.
  - 넷리스트(`front.net`·`carrier.net`)와 `kicad_sch` dnp 속성을 직접 파싱해 실제 연결을 확인했다.
  - 판정은 데이터시트 원문 값과 계산으로 했다.
  - 핵심 근거는 검토자가 원본에서 다시 확인했다: F1 퓨즈 종류, SMBJ5.0A/6.0A 표, CAM_PG 넷, 코어 PWR_SEQ1.
- 수정하지 않은 것: 제품 파일, 저장소, KiCad 설치 폴더.
- 실측: 없음.

## kicad-cli

| 명령 | 대상 (58eb49b 사본) | 종료 코드 | 결과 |
|---|---|---|---|
| `kicad-cli sch erc --severity-all --format json -o erc3_carrier.json carrier.kicad_sch` | 캐리어 | 0 | 위반 0 |
| 같은 명령 · `front.kicad_sch` | 전면 | 0 | 위반 0 |
| `sch erc --severity-all --exit-code-violations` (캐리어 갈래 재실행) | 캐리어 | 0 | 위반 0 |
| `sch export netlist --format kicadsexpr` | 캐리어 | 0 | 커밋된 `carrier.net`과 차이 0 |
| `fp export svg --footprint BarrelJack_XKB_DC-005-5A-2.0_Horizontal` (출력 폴더 먼저 만듦) | 라이브러리 | 0 | 파일 생성 확인 |
| `pcb drc --severity-all` (scratch 보드: 새 J2 / 대조군 일반형) | — | 0 / 0 | 새 J2: silk_over_copper 4 + lib 경고 1 · 대조군: lib 경고 1 |

## 판정표

| # | V-004 지적 | 판정 | 핵심 근거 |
|---|---|---|---|
| **R1** | I2C2 풀업 역급전 | **부분** (CAM_EN=0 정상 상태는 해소, 새 문제 N1) | R9·R10.1 → **CAM_1V8**. Q6 DMG2305UX: G=CAM_PG · S=CORE_1V8 · D=CAM_1V8. 핀배치는 DS36196 Rev 8-2 Top View G1·S2·D3과 심벌이 일치한다. 원문: VGS(th) −0.5~−0.9V, **RDS(on) ≤200mΩ @VGS −1.8V**, VGSS ±8V. CAM_EN=1 → VGS ≈ −1.71~−1.89V로 켜짐. CAM_EN=0 → CAM_PG = CORE_3V3(R4) → VGS = +1.5V로 꺼짐(±8V 안). 켤 때는 Q1(IOVDD)이 먼저, Q6이 1µs 안에 뒤따른다. 끌 때는 Q6이 약 50~110µs에 Q1(140~400µs)보다 먼저 꺼진다 → 풀업 전원이 먼저 빠지는 바른 방향. CAM_EN=0이면 SDA·SCL이 0V가 되고 LTR-329는 통신만 멈춘다(계약 6절 「CAM_EN=1에서만 폴링」) → **정상 상태의 역급전은 해소**. 단 아래 **N1** |
| **N1** (신규) | Q6 게이트가 CORE_3V3 풀업 넷(CAM_PG)을 공유 | **미해소 위험** | 넷: `/CAM_PG` = Q1.1 · Q3.3 · **Q6.1** · R4.2(R4.1 = **CORE_3V3**) · R5.1 (검토자 직접 확인). 코어 회로도 03 시트에서 **SGM2036(1V8 LDO)과 SY80004(+3V3 벅)의 EN이 둘 다 PWR_SEQ1**이다(검토자 확인). CORE_1V8이 CORE_3V3보다 먼저 오르는 구간에는 CAM_PG ≈ 0V → **Q6 VGS ≈ −1.8V로 켜지고 Q1은 꺼진 상태** → 모듈 IOVDD가 꺼진 채 I2C 풀업 1.8V가 걸리고, X1도 전원을 받아 MCLK를 낼 수 있다. 끌 때도 같은 구간이 생긴다. 구간 길이는 두 레귤레이터 소프트스타트에 달렸고 정량화하지 못했다. S401은 Q6 게이트를 자기 소스(1V8)에 풀업하고 별도 NMOS로 구동해 이 문제가 없다 |
| **R2** | X1 VDD → CAM_1V8 | **부분** | X1.4 VDD = CAM_1V8, C11 = CAM_1V8, X1.1 OE = CAM_EN. CAM_EN=0이면 X1도 꺼져 꺼진 모듈로 MCLK가 들어가지 않는다(해소). 이전 메모(OE 내부 풀업 → CAM_EN 중간 전위)도 사라졌다. 단 CAM_EN이 오를 때 OE 1.8V가 VDD보다 약 1µs 먼저 걸린다. YSO110TR 원문에 입력 절대최대가 없어 **확인 불가**. N1 구간에도 X1이 켜진다 |
| **R3** | RESET RC | **해소** (조건 2건) | C10 dnp yes → no. D3 BAT54WS K=CAM_EN · A=CAM_RESET(SOD323 캐소드 띠 = 패드 1). R16 CAM_RESET→GND DNP. DS30098 Rev 14-2: VF ≤240mV @0.1mA, IRM ≤2µA. 켤 때 τ 1ms → VIH 1.26V까지 1.08~1.47ms > 모듈 3.3V 상승(µs) → GC2053 9.2절 순서 만족. 끌 때 RESET이 µs 안에 0.24~0.3V(< VIL 0.54V)로 내려가고 모듈 전원은 140µs 이상 늦게 꺼진다 → 9.3절 만족. **조건:** ① FW는 CAM_EN을 push-pull Low로 내린다. Hi-Z로 두면 R6 100k·C10 τ 10ms라 RESET이 전원보다 늦게 떨어진다. ② R16을 실장한다면 ≥100k(10k면 RESET High 0.9V < VIH) |
| **R4** | TPS54302 Cff · 출력 C | **해소** | C19 75pF C0G 50V가 5V_SYS–BUCK_FB(R2 병렬). C7·C8·C20 22µF/25V X7R 1210 ×3. 5V 바이어스 실효(Murata GRM32ER71E226KE15 공개 CSV, 25°C): 0.5Vrms 19.05µF ×3 = 57.1µF / 0.01Vrms 15.54µF ×3 = 46.6µF / 85°C 52.3µF. Samsung CL32B226KAJNNN −20.5% → 약 52.5µF. 모두 **≥44µF**. Eq.14 fo = 5.1/(VOUT·CO) → 17.6~23.9kHz < 40kHz. Eq.16 Cff 70~90pF → 75pF는 범위 안. MPN 필드가 비어 있다 → BOM에서 위 품목급으로 정할 것 |
| **R5** | 5V_SYS TVS | **부분** | D7 K=5V_SYS · A=GND, 방향 맞음. **SMBJ5.0A 원문 행(검토자 확인): VR 5.0 · VBR 6.40~7.00 @10mA · VC 9.2 @65.3A · IR 800µA.** 벅 출력 공칭 5.08V · 최대 5.30V가 **VRWM 5.0V를 넘는다** → 「VRWM ≥ 최대 동작전압」 위반, 보증 밖 누설(VBR 미만이라 10mA 미만, 발열은 작음) |
| **R6** | DC 잭 풋프린트 | **해소** (경미 3건) | 새 `openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal`: 1 (0,0) · 2 (−5.9,0) · 3 (−3.0,+4.7), 슬롯 1.0×3.5(1·2 세로, 3 가로). XKB 도면 Rev A1(1–2 = 5.90, 1–3 = 3.00 · 직각 4.70, 「3-1.0x3.5」, ±0.05)과 일치. 핀 1 = 센터 = 12V_IN_RAW. 경미: ① 패드를 4.2로 키워 silk_over_copper 4건(scratch DRC) ② courtyard가 패드 1·3을 다 감싸지 못함 ③ 3D 모델은 6.0 피치 일반형 |
| **R7** | D2 심벌 | **해소** | libsource D_TVS → **D_Zener**(K=1, A=2). D2.1(K) = 12V_IN, D2.2(A) = GND, D_SMB 패드 1 = 캐소드(실크·fab 막대가 패드 1 쪽). 단방향 극성 맞음 |
| **R8** | microSD 소프트스타트 | **부분** | R22 47k(SD_PWR_GD–SD_PWR_G), C21 100nF(Q2 G–S), C13 1µF, R23 100k 방전. **R11 100k가 SD_PWR_G(게이트)에 남아 R22와 분압 → 최종 VGS = −3.3×100/147 = −2.24V.** AO3401A RDS(on) ≤85mΩ 보증은 **−2.5V**부터(VGS(th) max −1.3V) → 보증 밖(추정 약 108mΩ, 0.2A에서 22mV로 동작은 할 것). 켤 때 τ 3.2ms, 돌입 약 110~280mA로 개선됨. B101은 풀업이 Q3 드레인 쪽이라 분압이 없다(VGS −3.3V) |
| **R9** | DRV8837 IN2 여유 | **해소** (재고 확인 불가) | U1 RT9013-28GB, 넷 FRONT_2V8 = U1.5 · DRV8837 VCC · LTR-329 VDD · R1 · C2·C5·C12·C13 · TP2. ±2% → 2.744~2.856V. VIH max 0.5×2.856 = 1.428V → 1.8V GPIO(−5% 1.71V) **최악 여유 0.28V**(README의 0.4V는 공칭 기준). IN1에 3.3V가 와도 허용(VLOGIC 0~5.5V, 「with or without the VCC」). nSLEEP 2.55V. LTR-329 VDD 2.4~3.6V 안 |
| **R10** | AL8860 L · D · C | **부분** (D1·D2 MPN 부적합) | L1(·L2) SRN6045TA-470M 원문(렌더 판독): 47µH ±20% · DCR 200mΩ · **Irms 1.60A · Isat 2.00A**. 재계산(VIN 11.4~12.6V · 2×Vf 5.6~6.6V · ILED 0.95~1.05A · L ±20%): ton 2.2~5.7µs(≥500ns), f 112~222kHz(≤1MHz), 듀티 49~64%(25~75%), 피크 1.26A < 2.0A, rms 1.06A < 1.6A. C14·C16 10µF/50V X7R. **D1·D2 「Vishay SS24-E3/61T」는 없는 품번이다** — Vishay SS24는 SMB(DO-214AA) 전용(포장 52T·5BT). SMA(D_SMA)는 **SSA24-M3/61T**(DO-214AC, 40V 2A) |
| **R11** | USB_DET 역급전 | **해소** (권고 1건) | R9 200k / R10 100k → 1.667V(VBUS 4.75V면 1.58V) > VIH 1.26V. 역급전 약 16~22µA(이전 약 0.17mA). 누설 오차 ±0.09V(VDD18A 표 IL ±1.3µA 기준 추정). 기본 「NO PULL」 — 내부 풀업을 켜면 안 된다. 필터 C가 없다 → 권고 10~100nF |
| **R12** | 기록 · MPN | **부분** (F1 부적합) | U1 pin4 NC, D1 VGS ±25V, VSMA 도면 번호, L1 「Isat ≥ 6A」, C1 47µF/35V 반영. **F1 후보 Littelfuse 0437003.WR 원문 「437 Series – 1206 Fast-Acting Fuse」(검토자 확인) → 「3A 지연형」이 아니다.** L1 후보 SRP7028A-100M은 Isat 6A로 등호(여유 0) |
| **R13** | C6 DNP 유지 | **해소** | C6 dnp yes, 센서 블록 주석 「C6 DNP 유지 (R13)」. 이유(9.3절)는 README에만 있다 |
| **K1** | IR_PWM 극성 | **해소** (문구 2건) | 회로: R12.1 → CORE_1V8, R12.2 → IR_PWM → 기본 High → Q5 on → CTRL Low → LED 끔. 계약 v1.4 324행에 「전기 High = LED 끔」과 「FW 규칙: IR_LED_EN을 올리기 전에 IR_PWM을 High」가 반영됐다. **문구:** ① 「Low/**Hi-Z** = 켬」은 R12 풀업 뒤로는 틀리다(Hi-Z = 끔) ② 「평균 듀티는 ≤25% 끔 비율 기준으로 환산」은 뜻이 모호하다 → 「IR_PWM **Low(켬) 비율** ≤25%」 |
| **K2** | 6·9절 X1·풀업 | **해소** | 계약 3.1 레일 표에 CAM_1V8(Q6, 「I2C2 풀업 + 24MHz 발진기」), 6절 「CAM_1V8(스위칭)… Q6 DMG2305UX… S401 방식」, 9절 「전원 CAM_1V8」. 9·6절 불일치가 사라졌다. N1을 고치면 3.1 표의 Q6 게이트 표기도 함께 고친다 |
| **K3** | 3.1 12V_IR | **해소** | 「2스트링 최악 1.22A · ILIM 8.06kΩ ≈ 1.49A (MODE 개방…)」 |
| **K4** | 12절 5V TVS | **해소** (R5와 연동) | 「D7 SMBJ5.0A (VRWM 5.0V, VBR ≥6.4V, 단방향)」 반영. R5 수정을 받으면 품번을 바꾼다 |
| **MODE** (권고) | TPS26600 MODE 개방 | **해소** (조건 1건) | U2.6 = `unconnected-(U2-MODE-Pad6)`. SLVSDG2G Table 1 원문 「Open — Electronic circuit breaker with auto-retry — TPS26600, TPS26602」, tCB(dly) 4ms, tCBretry 540ms. Eq.4 I(CB) = 12/R − 0.03 = 1.46A(공차 약 1.32~1.59A, 1.22A 대비 여유 약 8%). Table 2 Start-up(Open): 「Inrush limited to I(OL) … Fault timer runs when current is limited to I(OL)」 → 기동 돌입 약 0.17A(30µF, 5.3V/ms) ≪ I(OL) min 1.40A로 오차단 없음. **조건:** 기동 중 LED는 꺼져 있어야 한다(K1 기본 끔 + FW 규칙). 켜 둔 채 기동하면 I(OL)에 근접해 차단·재시도가 반복될 수 있다 |

## netcompare (7f69f63 → 58eb49b) — 의도 차이와 1:1

- **캐리어:**
  - 부품 91 → 97, 넷 93 → 95. 연결 변경은 README 16.2 목록과 **1:1**이고 목록 밖 연결 변경은 0이다.
    - GND: +C20 · D7 · R23, −U2.6
    - SD_PWR_G: −Q3.3
    - 새 SD_PWR_GD
    - unconnected MODE
  - 목록 밖 차이는 필드(Note·MPN·Cable)뿐이다.
  - README의 「D2는 넷리스트 차이에 나오지 않는다」는 연결 기준으로만 맞다. libsource·핀 이름(A1/A2 → K/A)은 바뀌었다.
  - 다시 뽑은 넷리스트 = 커밋본(차이 0).
- **전면:**
  - 부품 78 → 83, 넷 64 → 65. README 16.2와 일치한다.
    - 새 부품: C18 · D3 · Q6 · R16 · TP23
    - 값 변경: C14 · C16 · D1 · D2 · L1 · L2 · U1 · TP2
    - 넷 변경: CAM_1V8 · CORE_1V8 · CAM_PG · CAM_EN · CAM_RESET · IR_PWM, FRONT_3V3 → FRONT_2V8
    - C10 dnp
  - 목록에서 빠진 것은 GND 노드 변경(+C18 · R16, −R12)뿐이고, 의도와 같은 변경이다.
- **의도 밖 전기 변경: 0** (두 보드).
- 문서 불일치: 회로도 README 10절 DNP 목록에 C10이 아직 DNP로 남아 있고 R16이 빠져 있다.

## 미해소·부분의 수정안 (회로도 담당)

| # | 수정안 | 근거 |
|---|---|---|
| **N1** (R1·R2) | **Q6 게이트를 CAM_PG에서 분리한다.** 새 넷(예 CAM_1V8_G)을 100k로 **CORE_1V8**에 풀업하고, 새 DMG1012T(G = CAM_EN, S = GND, D = Q6 게이트)로 끌어내린다(S401 Q6/Q7 패턴). → CAM_EN=0이면 Q6 VGS = 0V로 CORE_3V3/1V8 상승 순서와 무관해진다. 계약 3.1 표의 Q6 게이트 표기도 같이 고친다 | 코어 PWR_SEQ1 공유 · S401 |
| R2 | X1.1 OE를 CAM_1V8에 연결하거나(전원이 있으면 항상 켬), S401처럼 CAM_EN–OE 사이에 직렬 1k를 넣는다. FW: CAM_EN=1 후 첫 I2C까지 ≥5ms(X1 「Start-up 3ms Max」 + MCLK 1200주기) | YSO110TR · GC2053 9.2 |
| R3 | R16 주석을 「실장 시 ≥100k」로 바꾼다. FW 규칙: CAM_EN은 push-pull Low로 내린다(Hi-Z 금지) | BAT54WS · τ 계산 |
| **R5** | D7 → **SMBJ6.0A**(원문 VR 6.0 · VBR 6.67~7.37 · VC 10.3V @58.3A · IR 800µA, 검토자 확인). 계약 12절 「5.6~6V급」과 맞다. 하류 모듈 VIN 절대최대(미확인)는 따로 확인한다 | Littelfuse SMBJ 표 |
| **R8** | R11 핀 2를 SD_PWR_G에서 **SD_PWR_GD**로 옮긴다(B101 패턴, 넷 1개 변경). → VGS −3.3V로 보증 영역에 들어가고, 켤 때 τ 4.7ms, 끌 때 τ 14.7ms가 된다. FW: SD 전원을 다시 켜기 전 ≥250ms | AO3401A Rev 3.1 · B101 |
| **R10** | D1·D2 MPN → **Vishay SSA24-M3/61T**(또는 -E3/61T), DO-214AC = D_SMA | Vishay 89280 · 88748 |
| **R12** | F1 → **Bel 0685T3000-01**(C1T 「Slow Blow」 1206, 3A, 63V AC/DC @50A)로 바꾼다. 풋프린트는 그대로다. 차선은 Littelfuse 0468003.NR(Slo-Blo 32V, 70°C 감액 경계). L1은 Isat ≥ 7A 품목(SRP7028A-100M은 6A 등호)을 권고한다 | 437 원문 「Fast-Acting」 · Bel C1T |
| R6 (경미) | J2 courtyard를 패드 1(y ±2.35)·3(x −5.35~−0.65, y ≤6.70)까지 넓히고, 실크를 패드에서 ≥0.2 떨어뜨리고, 3D를 5.9 피치로 맞추거나 「대체 모델」로 주석한다 | scratch DRC |
| R11 (권고) | USB_DET–GND 10~100nF | 고임피던스 66.7k |
| 문서 | README 10절 DNP 목록 갱신(C10 실장, R16 DNP 추가). R13 주석에 이유(9.3절) 한 줄 | — |

## 계약 담당(C-001)에게

| # | 수정안 |
|---|---|
| K1-문구 | 324행 「Low/Hi-Z = 켬」 → 「Low = 켬 · Hi-Z = 끔(R12 풀업)」. 「≤25% 끔 비율 기준으로 환산」 → 「IR_PWM Low(켬) 비율 ≤25%」 |
| N1 연동 | 3.1 레일 표 CAM_1V8 행의 「게이트 CAM_PG」를 N1 수정에 맞춰 고친다 |
| R3 연동 | 7절 CAM_EN 행에 「Low는 push-pull로(Hi-Z 금지)」, 「CAM_EN=1 후 첫 I2C까지 ≥5ms」를 FW 규칙으로 넣는다 |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| V1 | N1 판정 | 「미해소 위험」 (정량화 못 함) | 두 레귤레이터가 같은 EN이라 상승 순서가 보장되지 않는다. S401은 구조적으로 피했다 | 실측에서 CORE_1V8이 늘 늦게 오르면 완화 |
| V2 | 출력 C 실효 용량 | Murata·Samsung 공개 DC 바이어스 데이터로 판정 | MPN이 비어 있어 대표 품목급 기준. BOM에서 같은 급을 지정하면 유효 | 실측 |
| V3 | R5 판정 | 「부분」 (VRWM 초과) | 정상 출력 공차가 VRWM 5.0V를 넘는다. 손상보다는 규칙 위반·누설 문제 | 출력 전압을 낮추는 방안(5V 사양상 불리) |
| V4 | R8 판정 | 「부분」 | 동작은 하겠지만 RDS(on) 보증 밖 | 넷 1개 변경으로 해소 가능 |

## 증거 파일
모두 `C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\2304a8aa-eb88-41c3-9975-aa6fda3de30c\scratchpad\v004b\` 아래에 있다.

| 위치 | 내용 |
|---|---|
| `snap3\` | 58eb49b 사본 |
| `erc3_*.json` | ERC 결과 |
| `contract_v14.md` | d159068 계약 사본 |
| `front\` | 넷·dnp 추출, DMG2305UX·BAT54WS·SSA24·SRN6045TA 원문, 렌더 이미지 |
| `carrier\` | `netdiff.txt`, `regen.net`, Murata CSV·Samsung 데이터, 퓨즈 원문 `dl_fuse\` (437 f2.pdf, Bel C1T), `drc\`, `fpsvg\` |

새로 받은 데이터시트 sha256:

| 자료 | sha256 |
|---|---|
| DMG2305UX | 7421a751…eb2d |
| BAT54WS | a910241f…26d6 |
| SSA23L/SSA24 (Vishay 89280) | 98baf992…8ec2 |
| 437 시리즈 (Farnell 사본) | 4118dc56… |
| Bel C1T | 1d8f295f… |
| Murata CSV (25°C/0.5Vrms) | de5a82a1… |
| Murata CSV (0.01Vrms) | 273cd947… |
| Murata CSV (85°C) | 6756c3db… |
| SRP7028A | 64bc2dfa… |

## 돌린 명령
- kicad-cli: 위 표(모두 종료 0)
- 저장소 테스트·빌드 명령: 돌리지 않음(이 레인은 문서 1개만 추가하고, 하네스 검사가 「찾지 못했다」로 나옴)
