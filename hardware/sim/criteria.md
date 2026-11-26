# SIM-001a 합격 기준 (결과보다 먼저 커밋)

- 배정: orch SIM-001a (VD-001 7, O-80) · 작성: schematic t18t · 2026-11-27
- 대상 회로도: `hardware/schematic` C-016 `ea1336b`. 전원 부품 값은 C-013 `656b50a`와 같다.
- 규칙:
  - 기준은 이 파일을 커밋한 다음에 시뮬레이션을 돌린다.
  - 결과 JSON의 `criteria_commit`이 이 커밋을 가리킨다.
  - 기준을 바꾸면 새 커밋으로 하고 이유를 남긴다. 결과를 보고 기준을 고치지 않는다.
- 최악 조합:
  - 저항 ±1%
  - 세라믹 커패시터 ±10%(K) / ±20%(M)
  - 데이터시트 min/max
  - 입력 12V ±5%(11.4~12.6V, 어댑터 GST25A12 가정)

## A. TPS26600 12V_IR eFuse (캐리어 U2 · R6 8.06k ILIM · C9 22nF dVdT · UVLO→IN · OVP→RTN · MODE 개방)

| ID | 항목 | 기준 | 근거 |
|---|---|---|---|
| SIM-A1 | 기동 돌입전류 피크 (SHDN↑, 출력 C 최대 = C11 + 전면 C14·C16 각 10µF +10%, + 100nF ×2) | ≤ I(OL) 최소. 기동 중 전류 제한·회로차단기 타이머가 걸리지 않아야 함 | SLVSDG2G 7.5 I(dVdT) 4.0~5.5µA, GAIN(dVdT) 23.75~25.5 |
| SIM-A1 | 출력 램프 시간 (10→90 %, 최악 느린 쪽) | ≤ 10 ms | 부팅 흐름에 영향 없을 것 (FW는 IR_LED_EN 후 IR_PWM 사용) |
| SIM-A2 | 켜짐 문턱 (UVLO→IN 이므로 내부 POR) 최대 | ≤ 입력 최소 11.4V − 역접 P-FET 강하 | 7.5 V(PORR) 3.9~4.1V |
| SIM-A2 | OVP (OVP→RTN = 내부 고정) 상승 문턱 최소 | ≥ 입력 최대 12.6V | 7.5 V(IN_OVP) 31~34V |
| SIM-A3 | I(OL) 최소 (ILIM 데이터시트 ±5% × R ±1%) | ≥ 2스트링 최악 부하 1.22A | 계약 3.2 · 7.5 I(OL) (8k: 1.425~1.575A) |
| SIM-A3 | 과부하 중 12V 입력 피크 = I(OL) 최대 + 5V 벅 입력 0.62A | ≤ 어댑터 2.08A | 계약 12절 「과부하 때 합계가 어댑터 2.08A를 넘지 않게」 |
| SIM-A3 | 과부하 지속 시 12V_IR 평균 (회로차단기 4ms 켜짐 / 540ms 재시도) | ≤ 1.22A | 7.6 tCB(dly) 4ms · tCBretry 540ms |

## B. TPS54302 5V_SYS 벅 (캐리어 U1 · L1 10µH SRP7028A-100M · C7·C8·C20·C23 22µF/25V 1210 · R2 100k/R3 13.3k · C19 75pF)

| ID | 항목 | 기준 | 근거 |
|---|---|---|---|
| SIM-B1 | 출력 DC 최악 (VFB 0.581~0.611V × R ±1%) | 4.75 ≤ V ≤ 5.25V | 계약 3.1 「5V ±5%로 계약」 |
| SIM-B1 | 출력 DC 최대 | < D7 SMBJ6.0A VRWM 6.0V | 계약 12절 |
| SIM-B2 | 출력 리플 (VIN 12.6V, L −20%, C 최소 유효값) | ≤ 30 mVpp | SLVSDG6C Table 7-1 |
| SIM-B3 | 부하 과도 0.1→1.5→0.1A (1A/µs) 편차 | ≤ ±5% (±250 mV) | Table 7-1 「1.5-A load step ΔVOUT = ±5 %」 |
| SIM-B3 | 루프 교차 주파수 | ≤ 40 kHz | 7.2.3 「select the crossover frequency less than 40kHz」 |
| SIM-B3 | 위상 여유 | ≥ 45° | 일반 설계 기준 |
| SIM-B4 | 기동 오버슈트 (무부하·1.3A) | ≤ 4% (OV 비교기 104% 해제점 아래) | 6.1 OV 108%/104% |
| SIM-B4 | 95% 도달 시간 | ≤ 10 ms | tSS 5 ms |
| SIM-B5 | 인덕터 Isat (L −20%) | ≥ HS 전류 제한 최대 6 A (과부하에서도 포화 없음) | Bourns SRP7028A-100M Isat 6A · SLVSDG6C I(LIM_HS) 4~6A |
| SIM-B5 | 인덕터 Irms | ≥ 5V_SYS 피크 부하 1.3 A | 계약 3.2 |
| SIM-B6 | 출력 C 유효값 (5V DC 바이어스 · −10% 공차) | ≥ 30 µF | SLVSDG6C Equation 11 (1.5A step, 5%) |

## C. 보드 레일 (회로도에 있는 것)

| ID | 항목 | 기준 | 근거 |
|---|---|---|---|
| SIM-C1 | FRONT_2V8 (전면 U1 RT9013-28, 입력 VIN = 5V_SYS 최소) 부하 0~50mA | 출력 ≥ 2.744V (−2%), 입력−출력 여유 ≥ 데이터시트 드롭아웃 최대 | DS9013 · 계약 3.1 (DRV8837 VCC·LTR-329 VDD) |
| SIM-C2 | SD_PWR_3V3 (캐리어 Q2 AO3401A, VGS −3.3V) 부하 0.2A 강하 | ≤ 3% | 계약 3.2 microSD ≤0.2A |
| SIM-C2 | CAM_IOVDD·CAM_AVDD (전면 Q1·Q2 AO3401A) 부하 각 0.1A 강하 | ≤ 3% | GC2053 모듈 3.3V 입력 |
| SIM-C2 | CAM_1V8 (전면 Q6 DMG2305UX, VGS −1.8V) 부하 20mA | ≥ 1.71V (1.8V −5%) | 계약 3.1 |
| SIM-C3 | 스위치를 켤 때 CORE_3V3 순간 강하 (SD·CAM) | ≤ 5% | 코어 레일 공유 (코어 SCH 03 출력 C만 가정 — 결과에 가정 표기) |
| SIM-C3 | CAM_1V8을 켤 때 CORE_1V8 순간 강하 | ≤ 5% | 위와 같음 |

## D. 전원 순서 (12V 인가 → 5V_SYS → 코어 레일 → 전면 2V8 · 12V_IR 차단)

| ID | 항목 | 기준 | 근거 |
|---|---|---|---|
| SIM-D1 | 12V 인가 후 5V_SYS 4.75V 도달 | ≤ 15 ms | tSS 5 ms + 여유 |
| SIM-D1 | 모든 레일 오버슈트 | ≤ 5% | — |
| SIM-D1 | IR_LED_EN = 0(R5 풀다운) 동안 12V_IR | ≤ 0.5 V | 계약 12절 SHDN ← IR_LED_EN 기본 끔 |
| SIM-D1 | FRONT_2V8이 5V_SYS보다 늦게·단조 증가 | 단조, 최종값 ±2% | — |

- 판정: 기준 하나라도 넘으면 그 시험은 `fail`이다. 불합격은 D-003 방식(분기점·선택·이유·차선)으로 수정을 제안하고 orch가 판단한다. 회로도는 이 레인에서 고치지 않는다.
- 실행 불가(모델 없음, 수렴 실패)는 `error`로 둔다.
