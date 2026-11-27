# SIM-001a 전원 경로 회로 시뮬레이션 (VD-001 7, schematic)

**결론 (C-019 `7760f38`):** 15개 시험이 **모두 pass**다. 실행 스크립트 종료 코드는 **0**이다.

| 판 | 결과 |
|---|---|
| 첫 실행 (C-018 `a61dc63`, 커밋 `4733be6`) | 2개 fail: SIM-B1 5V 공차 5.298V, SIM-C3 CAM_EN 때 CORE_3V3 강하 0.230V |
| C-019 (O-93) | 아래 P1·P2를 회로도에 반영한 뒤 **같은 기준**(`64bde61`, 바꾸지 않음)으로 다시 돌렸다 → 둘 다 pass |

- 대상 회로도: C-019 `7760f38`
  - 캐리어 R6 6.04k · R2 78.7k / R3 10.7k
  - 전면 R17 4.7k · C19 4.7nF · R18 1k · R19 10k · R20 1k · C20/C21 4.7nF
- 기준: [criteria.md](criteria.md)
  - 결과보다 먼저 커밋했다: `d00a3ac` → A4 `781961b` → 개정 1 `ef3c0d0` → 개정 2 `33ea3bf` → A5 `64bde61`
  - 결과 JSON의 `criteria_commit` = `64bde61`
- 다시 돌리기: `python hardware/sim/run_all.py`
  - `results/*.json`(SIM-result-format), `png/*.png`, `SIM-*.cir`, `SIM-A5-current-order.md`를 모두 다시 만든다.
  - 종료 코드 = fail + error 수
- 도구: ngspice-47 공식 판. 실행 파일은 환경변수 `NGSPICE`로 준다(없으면 PATH 의 `ngspice_con`).
  - KiCad 10 내장 시뮬레이터는 쓰지 않았다(배치 실행·재현은 공식 판으로).

## 결과

| ID | 항목 | 판정 | 핵심 값 (기준) |
|---|---|---|---|
| SIM-A1 | TPS26600 기동 돌입 (dVdT 22nF) | pass | 피크 0.235A (≤ I(OL) 최소), 램프 2.3ms (≤ 10ms) |
| SIM-A2 | 켜짐(POR)·OVP 문턱 | pass | 켜짐 4.10V (≤ 11.3V), OVP 31.0V (≥ 12.6V) — UVLO→IN·OVP→RTN이라 분압 저항 없음 |
| SIM-A3 | 전류 제한·회로차단기 (R6 6.04k) | pass | I(OL) 최소 1.86A (≥ 1.22A), 과부하 입력 피크 2.74A (≤ 3.34A), 재시도 평균 0.017A (≤ 1.22A) |
| SIM-A4 | 어댑터 GST40A12-P1J + 최악 부하·과부하 | pass | 정상 피크 1.84A / 평균 0.92A, 과부하 피크 2.74A (< OLP 3.51A), 5V_SYS 최소 4.98V(정전류·hiccup). 참고 GST25A12: 과부하 때 5V_SYS 3.9V(정전류)·0V(hiccup) |
| SIM-A5 | 12V 전류 순서 표 | pass | [표](SIM-A5-current-order.md): 1.585 × 1.15 = 1.823A ≤ I(OL) 최소 1.861A, I(OL) 최대 2.115 + 0.648 = 2.763A < 3.51A |
| SIM-B1 | TPS54302 출력 공차 | pass (C-019) | 4.770~5.196V (4.75~5.25V). 첫 실행(100k/13.3k)은 5.298V로 fail. 코어 VIN 차단 3.0V까지 여유 1.77V |
| SIM-B2 | 리플 | pass | 9mVpp (≤ 30mV), VIN 12.6V·L 8µH·fsw 290kHz |
| SIM-B3 | 부하 과도·루프 | pass | 0.1↔1.5A 편차 142mV (≤ 250mV), fc 18.2kHz (≤ 40kHz), 위상 여유 100° (≥ 45°) — R2 78.7k로 피드포워드 영점이 옮겨 간 뒤 |
| SIM-B4 | 기동 | pass | 오버슈트 0.1%, 95% 4.8ms |
| SIM-B5 | 인덕터 | pass | Isat 6.0A = I(LIM_HS) 최대 6A (여유 0), Irms 3.5A, 정상 피크 1.96A |
| SIM-B6 | 출력 C DC 바이어스 | pass | 5V에서 C/C0 = 0.795 (Samsung) → 유효 최소 63µF (≥ 30µF) |
| SIM-C1 | RT9013-28 | pass | 2.744V 최소 (≥ 2.744V), 여유 1.97V |
| SIM-C2 | 부하 스위치 강하 | pass | SD 10mV, CAM 5mV, CAM_1V8 1.757V (≥ 1.71V) |
| SIM-C3 | 스위치 켬 순간 코어 레일 강하 | pass (C-019) | CAM_EN: CORE_3V3 0.046V (≤ 0.166V; 첫 실행 0.230V fail), CORE_1V8 0.018V, SD 0.034V |
| SIM-D1 | 전원 순서 | pass | 12V_IN > 4.4V 뒤 3.5ms에 5V_SYS 4.75V. 오버슈트 < 0.2%, 12V_IR 0V, 2V8 단조 |

## 수정 제안 (D-003 방식) — orch O-93 판단으로 C-019에 반영

- **P1:** orch가 E192 13.5k(0.5% 필요)는 채택하지 않았다. 대신 1% E96 중 LCSC 재고가 있고 최악 범위의 가운데가 5V에 가장 가까운 **R2 78.7k / R3 10.7k**를 반영했다.
- **P2:** 1안 그대로 반영했다(전면 R20·C20·C21).
- 아래 표는 첫 실행 때 제안이다.

| # | 시험 | 분기점 | 1안 | 이유 · 근거 | 차선 |
|---|---|---|---|---|---|
| P1 | SIM-B1 | FB 분압 R2 100k / R3 13.3k는 전형 5.077V로 위로 치우쳐 있다. VFB ±2.5%(−40~125°C)와 R ±1%를 겹치면 5.298V가 된다 | **R3 13.3k → 13.5k (E192 1%)** → 4.799~5.228V, 전형 5.007V | 중심을 5.0V로 옮기면 양쪽 모두 들어간다. 부품 1개 값만 바뀌고 넷 변화는 없다 | R2 100k → 97.6k (E96) → 4.760~5.185V (하한 여유 10mV). 또는 기준 유지 — VFB 전형 온도 변화는 Figure 5-5에서 ±0.5% 안이고, 코어 VIN 상한이 확인되면 그 값으로 기준을 바꾼다 |
| P2 | SIM-C3 | 전면 Q1(CAM_IOVDD)은 게이트가 CAM_PG에 바로 붙어 Q3가 수십 ns 안에 켠다. C7 1µF·C8/C9 1.1µF를 CORE_3V3에서 순간 충전한다 | **Q1 게이트 직렬 1k + Q1·Q2 게이트–드레인 4.7nF (밀러 소프트스타트, C-017 S1과 같은 방식)** → 같은 모델로 강하 0.046V, IOVDD 켜짐 10µs, AVDD 81µs (IOVDD → AVDD 순서 유지) | CORE_1V8에 이미 쓴 방식과 같다. 부품 3개 | 직렬 4.7k + 4.7nF → 강하 0.019V, IOVDD 39µs. 끄는 순서(GC2053 9.3절, V-004 R13)에 주는 영향은 firmware SIM-001b 끄기 시험으로 다시 확인해야 한다 |

- P2의 강하 값은 코어 레일 모델(이상 전원 + 0.1Ω + 로컬 C 12µF)에 기댄 값이다. 코어 SoC 주변 디커플링을 더하면 실제 강하는 더 작다. 그래서 1안 대신 bring-up 실측(CAM_EN 켤 때 CORE_3V3 파형)으로 판정하는 길도 있다.

## 모델 · 출처 (제조사 SPICE 모델은 쓰지 않음 — 모두 데이터시트 수치 동작 모델, 이 저장소 작성)

| 대상 | 모델 | 근거 (문서 · 쪽) |
|---|---|---|
| TPS26600 | 평균 모델. dVdT 전류·이득, POR/OVP, I(OL) = 12/R(kΩ) ±5.4%, 회로차단기 4ms / 재시도 540ms | TI SLVSDG2G 7.5·7.6, 9.3.5.1.1 Equation 3 (22쪽), Table 1 — https://www.ti.com/lit/ds/symlink/tps2660.pdf sha256 b781cbce…e1de |
| TPS54302 | 평균 전류 모드 모델: gm 240µA/V, 내부 보상 20k/2.04nF/2pF, Gcs = 11.2 A/V(Equation 14에서 역산), fsw/2 샘플링 지연, EA 클램프·OV 108%, 소프트 스타트 5ms. 리플은 이상 스위치 스위칭 모델 | TI SLVSDG6C 5.5·5.6·6.1·6.2·6.3 — sha256 d81679ba…51b8 |
| L1 | SRP7028A-100M 10µH ±20%, DCR 85mΩ 최대, Isat 6A, Irms 3.5A | Bourns SRP7028A 데이터시트 sha256 64bc2dfa…226f |
| C7·C8·C20·C23 | 5V 바이어스에서 17.42µF / 0V 21.92µF (−20.5%) | Samsung Electro-Mechanics Component Library DC-Bias 차트 API (CL32B226KAJNNN, 25°C) sha256 501635c3…13e0 |
| RT9013-28 | 정확도 ±2%, 드롭아웃 400mV @ 500mA 최대 | Richtek DS9013-09 (2010, LCSC 사본) sha256 15023cfb…1ac8 |
| AO3401A · DMG2305UX | 레벨 1 (VGS(th)·RDS(on) 점 맞춤, Ciss) | AOS AO3401A Rev 3.1 sha256 0d8e3261…a785c · Diodes DS36196 Rev 8-2 sha256 7421a751…eb2d |
| 어댑터 | GST40A12-P1J: Vout 11.64V 최소, 0.11Ω + 케이블 26mΩ, OLP 3.51A 정전류 또는 hiccup(1ms 감지·1s 끔, 가정) | research R-021 `19a69d0` §2.3 · 참고 MEAN WELL GST25A-SPEC sha256 95f99967…9345 |
| 코어 레일 | 이상 전원 + 0.1Ω + 로컬 C (3V3 12µF, 1V8 8.5µF), 3V3 1ms 램프 | 코어 SCH 03 출력 C (DC 바이어스 감액은 가정) |

- 재배포: 데이터시트·제조사 자료는 저장소에 넣지 않았다(라이선스 미표기). URL과 sha256만 남긴다.
- 넷리스트(`SIM-*.cir`)와 모델은 이 저장소에서 작성했다.

## 한계

- 펄스 스킵(경부하), 히컵, TPS26600 빠른 차단(1.87×I(OL)), 온도는 모델에 없다.
- 코어 내부 전원 순서(PWR_SEQ)는 가정이다.
- AL8860 부하는 25% 듀티 전류원으로 두었다(두 스트링 같은 위상 = 최악). 실제 스트링 동작은 firmware SIM-001b가 맡는다.
- GST25A12 hiccup 참고 시험은 어댑터가 꺼진 뒤 붕괴 구간에서 ngspice가 일찍 끝날 수 있다. 그래서 5V 최소 0V는 「꺼짐」의 뜻으로만 읽는다.

## SIM-001d — C-020 게이트 결선으로 재실행 (orch, 2026-11-27)

- **대상:** 회로도 C-020 `a2d878c` (S6)
  - 전면 R20 100k ∥ (R21 1k + D4 BAT54)
  - R5 100k ∥ D5 BAT54
  - C20·C21 4.7nF
- **기준:** 바꾸지 않았다(`64bde61`).
- **SIM-C3 넷리스트:** Q1·Q2 게이트 결선을 위와 같이 갱신했다. BAT54WS는 VF 0.32V @ 10mA 최대값에 맞춘 다이오드 근사(IS 4e-8, RS 2Ω, CJ 10pF)로 넣었다.
- **결과:** `run_all.py` 종료 **0** (15/15 pass)
  - SIM-C3 CAM_EN 켤 때 CORE_3V3 강하 **0.041V** (≤ 0.166V). C-019 때는 0.046V.
  - CORE_1V8 강하 0.018V, SD 강하 0.034V
  - 그림 [SIM-C3-cam.png](png/SIM-C3-cam.png): IOVDD가 먼저 오른다(약 10µs). AVDD는 약 170µs 뒤에 오르기 시작한다(firmware SIM-001c ②의 180µs와 맞음).
  - 나머지 A·B·C·D 항목은 값이 C-019 재실행과 같다(회로 변경 없음).
- 이 폴더의 SIM-L*·SIM-001b/c 파일은 firmware 몫이라 건드리지 않았다.
