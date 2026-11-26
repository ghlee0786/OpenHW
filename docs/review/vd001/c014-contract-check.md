# VD-001 조건 1 — 계약↔회로도 기계 대조 (C-014)

- 대조 대상: `hardware/schematic/hw-fw-contract.md` v1.11과 `carrier.kicad_sch`·`front.kicad_sch`의 kicad-cli 넷리스트 (main 434e960 기준 레인 t-20261127-041255-b9cd)
- 스크립트: `hardware/schematic/tools/contract_check.py` — 한 번 실행하면 계약 대조, 두 보드 ERC `--exit-code-violations`, netcompare(C-013 656b50a 대비)를 모두 돈다.
  **종료 코드 = 계약 불일치 수 + ERC 실패 보드 수 + netcompare 차이 보드 수**
- 다시 돌리기: `cd hardware/schematic && python tools/contract_check.py --md <표.md> --json <결과.json>`
- 기계 결과 JSON: [c014-contract-check.json](c014-contract-check.json)

## 결과

| 항목 | 값 | verifiable |
|---|---|---|
| 계약 대조 줄 | 374 | 예 |
| 계약 불일치 | **8** (모두 계약 문구가 회로도보다 낡은 것으로 보임 — 아래 근거. 고치지 않음, orch 판단) | 예 |
| ERC 종료 코드 | carrier 0 · front 0 | 예 |
| netcompare 656b50a 대비 | carrier 0 · front 0 (comps 99/85, nets 95/66) | 예 |
| 고장 주입 `--selftest` | 13건 모두 잡음 (놓침 0, 종료 0) | 예 |
| 스크립트 종료 코드 | 8 | 예 |

| 절 | 대조 줄 | 불일치 |
|---|---|---|
| 4절 | 125 | 2 |
| 5절 | 120 | 0 |
| 5.1 | 25 | 1 |
| 6절 | 5 | 0 |
| 13절 C18 | 2 | 1 |
| 7절 | 41 | 2 |
| 12A | 22 | 0 |
| 3.1·12절 | 7 | 0 |
| 12절 | 6 | 0 |
| 3.1 | 11 | 0 |
| 9절 | 1 | 0 |
| 13절 C17 | 2 | 0 |
| DNP | 7 | 2 |

| 판정 | 절 | 항목 | 계약 | 회로도 |
|---|---|---|---|---|
| 불일치 | 5.1 | MCLK 직렬 저항 (X1 OUT → J3-4) 참조·값 | R18 0R | R8 22R |
| 불일치 | 13절 C18 | I2C2 풀업 레일 (C18 ④ 문구) | CORE_1V8 | CAM_1V8 |
| 불일치 | 7절 | 예비: 「FPC 8」 = 캐리어 J7-8 | SPARE1 | NC |
| 불일치 | 7절 | 조도 INT 예비: 「FPC 7」 = 캐리어 J7-7 | ALS_INT_RSV | NC |
| 불일치 | 4절 | 용도 「SPARE1 → FPC 8」 = 캐리어 J7-8 | SPARE1 | NC |
| 불일치 | 4절 | 용도 「ALS_INT_RSV → FPC 7」 = 캐리어 J7-7 | ALS_INT_RSV | NC |
| 불일치 | DNP | 13절 C19 「B는 DNP」: 스트링 B DNP 수 | 3 | 0 |
| 불일치 | DNP | 5.1 RESET RC 커패시터 100nF DNP | 100nF DNP | 100nF 실장 |
| 정보 | DNP | carrier: 계약에 근거 문구가 없는 DNP (정보) |  | C15,C16,R13,R14,R15,R16,R17 |
| 정보 | DNP | front: 계약에 근거 문구가 없는 DNP (정보) |  | C6,R16 |

ERC 종료 코드: carrier 0 · front 0 / netcompare(656b50a 대비): carrier 0 · front 0
종료 코드 = 8 + 0 + 0 = 8

## 불일치별 근거 (어느 쪽이 맞는지는 orch 판단)

| # | 계약 문구 | 회로도 | 회로도 쪽 근거 | 계약을 고치면 |
|---|---|---|---|---|
| 1 | 5.1 「MCLK 24MHz (X1 → R18 0Ω)」 | R8 22R (X1 OUT → CAM_MCLK) | README 「R8 22Ω」 (S401 패턴 직렬 감쇠) | 5.1 행을 「X1 → R8 22Ω」으로 |
| 2 | 13절 C18 ④ 「I2C2 풀업은 CORE_1V8 상시」 | R9·R10 4.7k → CAM_1V8 | 6절 본문·C20(v1.4, O-33)이 이미 CAM_1V8로 되돌림 | C18 ④에 「→ v1.4 C20에서 CAM_1V8로 대체」 표시 |
| 3–6 | 4절 용도 「SPARE1 → FPC 8」·「ALS_INT_RSV → FPC 7」, 7절 커넥터 열 「→ FPC 8」·「→ FPC 7」 | 캐리어 J7 GH 6P: SPARE1 = J7-3, ALS_INT_RSV = J7-4 | 12A절(v1.3·v1.8) GH 6P 핀표 — FFC 10P 시절 번호가 남음 | 「→ J7-3」·「→ J7-4」로 |
| 7 | 13절 C19 「IR LED … 2직렬 × 2스트링, B는 DNP」 | 스트링 B(D_IR_B1·B2·U5 등) 실장 | C-012 / v1.11 (O-69) 3.1절 「스트링 A·B 실장」 | C19에 「v1.11 O-69로 B 실장」 표시 |
| 8 | 5.1 행 24 「RESET … 10k + 100nF(DNP) RC 자리」 | C10 100nF **실장**, D3 BAT54WS, R16 10k DNP | C-004 R3 (README 「C10 DNP → 실장」), 13절 C20 「RESET RC + BAT54」 | 5.1 행을 「10k + 100nF RC + BAT54 (R16 10k DNP)」로 |

**정보(개수에 넣지 않음):** 계약에는 DNP 목록이 따로 없다. 계약 문구에 근거가 없는 회로도 DNP는 다음과 같다.
- carrier: C15, C16 (MDI 센터탭), R13–R17 (SD 47k 풀업)
- front: C6, R16

이 부품들의 근거는 회로도 README 10절의 DNP 목록에 있다. 계약에 DNP 절을 둘지는 orch가 정한다.

## 대조 규칙 (스크립트에 쓴 것)

- **4·5절 BTB 핀:**
  - 각 행의 넷을 회로도 J1 핀 넷과 비교한다. 코어 넷 이름은 ALIAS 표(3.1·6·7절 근거)로 회로도 이름으로 바꾸고, `/3V3` 꼬리표는 뗀다.
  - 「용도」가 「미사용」으로 시작하고 「시험점」이 없으면 NC를 기대한다.
  - 짝 핀(홀수 +1, 짝수 −1)도 함께 확인한다.
- **5.1 DF30:** 24핀을 확인한다. 넷 열의 첫 낱말을 쓰고, MCLK·AVDD·IOVDD·DVDD·RESET은 회로도 넷 이름으로 바꾼다.
- **6·7절:**
  - 풀업 값과 레일, LTR-329 결선을 확인한다.
  - GPIO 행마다 보드 핀 넷, 4·5절 표와 같은 넷인지, 「FPC n」 표기, DRV8837 IN1/IN2를 확인한다.
- **12A:** J7-n과 J4-(7−n)의 넷이 같은지, 「캐리어 n」 BTB 핀을 확인한다.
- **값 문구:** 계약 문구에서 정규식으로 값을 읽어 회로도 부품 값·핀 넷과 비교한다. 대상은 ILIM, dVdT, SHDN, UVLO, OVP, MODE, 22µF ×4, 5V FB 분압(VREF 0.596V, ±5%), R17·Q6·Q7, RT9013, X1 OE, D7, TVS, F1, R12, UPGRAD_KEY 1k, USB_DET 분압, AL8860 Rs·CTRL 공유, nSLEEP이다.
- **고장 주입:** 계약 사본에서 표나 문구 한 줄을 바꾸는 13가지 경우를 시험한다. 경우마다 불일치 수가 늘어야 잡은 것으로 본다.
