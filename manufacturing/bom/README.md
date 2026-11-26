# PCBWay 형식 BOM (보드별) — R-011

- 배정: orch t18r R-011 · 작성 research t18s · 2026-11-26
- 생성기: `make_pcbway_bom.py` — 표준 라이브러리만 쓴다. `python -I`로 실행한다.
- 출력: `carrier-pcbway.csv` · `front-pcbway.csv`
  - PCBWay 공식 템플릿 9열이다(R-010 1.1절, `Sample_BOM_PCBWay.xlsx?v=1.1`의 머리글을 그대로 썼다).
  - 수량은 **보드 1장 기준**이다. 주문 수량은 주문 폼에 넣는다.
- **견적 요청·업로드는 하지 않았다.**

## 입력 (고정 사본 — `inputs/`)

| 파일 | 출처 | sha256 |
|---|---|---|
| `inputs/bom-full.csv` | research R-016 레인 t-20261127-021842-688a의 `docs/research/bom-full.csv` (같은 커밋, **IR 스트링 B 실장 — O-69**). 이전 판: R-008 9a5fbfb (sha256 9738121e…fa02) | 321c7402b6f58fb225580d1707a2eb017520f563f75192fbf01fc9f53808890a |
| `inputs/carrier-kicad-bom.csv` | 회로도 **c653eac** `hardware/schematic/carrier/carrier.kicad_sch`(sha256 1f7cb20b…62b0)를 `git show`로 꺼내 `kicad-cli sch export bom`으로 내보냄 | 3c597c2ec691b0ca3bfe4fe8e48ae14848c6cbaee718313650fe46eea7149a58 |
| `inputs/front-kicad-bom.csv` | 같은 방법 (`front.kicad_sch` sha256 4bd5b354…1b304) | c4f429b83e7ae6de4293e304dfd6ebb0a37604c8a8f4c7fd24ce24466c8c0eab |

- R-016 (2026-11-27): main eb0da0f의 회로도(C-011 `83728da`)로 다시 내보냈다(종료 0). 결과는 위 두 파일과 바이트까지 같았다(sha256 동일). 그래서 KiCad 입력은 바꾸지 않았다.
- **R-021 (2026-11-27): 입력 3개를 모두 바꿨다.** `inputs/bom-full.csv` = R-021 레인 t-20261127-051043-fac0의 `docs/research/bom-full.csv`(sha256 93e344677d719e73a13b2c57908b1bc66621c6b461ae260acb51695767db57ba → **O-90 판 c364206b04a7f73e96c54ef7bd4a0efd903ba563329b263bccefd63cd1edd124**: 캐리어 C18·C22를 FH 0402B103K500NT C1524로). KiCad BOM 2개는 회로도 **f0745ed**(C-017, C-016 ea1336b 포함)를 `git show`로 꺼내 같은 명령으로 내보냈다(종료 0 · 0): carrier sha256 9f2b6eea1f530f5b521e15aa075824b077773e209d0593456376b712213f1abd, front sha256 ce2a9138418a36cc1a74bf6ba7e7a3c7068309bfc0041f234fc7ff41e889b8e7. 위 표의 sha256은 이전 판 기록이다.
- **R-022 (2026-11-27): 입력 3개를 다시 바꿨다.** `inputs/bom-full.csv` = R-022 레인 t-20261127-054531-37bc의 `docs/research/bom-full.csv`(sha256 e3fae849edcd7fbdf6c145ecad58107bcf8510a7be7aba717df9290357b8cbd0). KiCad BOM은 회로도 **7760f38**(C-019, C-018 a61dc63 포함)을 `git show`로 꺼내 같은 명령으로 내보냈다(종료 0 · 0): carrier sha256 9f44da04eaf791a8789afd6b05bae157172e6f67980fe7a486510043dd2ba45d, front sha256 fa44d6f9f8185853c27c6ca756439d01df0c3929430d7f782ad1b19b82f821db.
- **R-023 (2026-11-27):** `inputs/bom-full.csv` = R-023 레인 t-20261127-060023-2ca0의 `docs/research/bom-full.csv`(sha256 23a0aeebd53a7e5983b8af05d99e787dca9f1574242ebb72775a9e614574bce8). KiCad BOM은 회로도 **a2d878c**(C-020)에서 내보냈다(종료 0 · 0): carrier는 R-022와 같음(sha256 9f44da04…a45d), front sha256 b379086400b3131923d15a5453a2dacd4a3cdb3e2f5769d037512fb5e44f1ac0.
- **R-024 (2026-11-27):** `inputs/bom-full.csv` = R-024 레인 t-20261127-063202-e8f3의 `docs/research/bom-full.csv`(sha256 0f8bea5df3f28da4f218422cd7d5812d66b33df47c52df8ec28cb1bd9a3d8675). KiCad BOM은 회로도 **613cf14**(C-021)에서 내보냈다(종료 0 · 0): carrier 변화 없음, front sha256 90862738ed47cfde3d5db0cc0b63c0ccdae8d0bd9426504c954bd5837f457e39(LF 기준).

KiCad 내보내기 명령(KiCad 10.0.8, 종료 코드 carrier 0 · front 0):

```
kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP}' --labels 'Refs,Value,Footprint,Qty,DNP' --group-by 'Value,Footprint,${DNP}' --ref-range-delimiter '' -o inputs/<board>-kicad-bom.csv <board>.kicad_sch
```

## 실행과 종료 코드

```
python -I make_pcbway_bom.py
python -I make_pcbway_bom.py --bom-full <csv> --kicad-carrier <csv> --kicad-front <csv> --out <dir>
```

| 종료 코드 | 뜻 |
|---|---|
| 0 | 보드마다 **참조 지정자 집합**과 **DNP 집합**이 KiCad BOM과 같다 |
| 1 | 하나라도 다르다. 차이는 stderr에 「BOM에만 / KiCad에만」으로 나온다 |
| 2 | 입력 파일이 없거나 형식이 다르다 (bom-full 21열, KiCad의 Refs/DNP 열) |

## 변환 규칙

| 항목 | 규칙 |
|---|---|
| 보드 구분 | bom-full `Reference`의 접두어 `[캐리어]` → carrier, `[전면]` → front |
| `*Designator` | 콤마로 구분하고(공백 없음) 참조 번호 순서로 정렬한다 |
| `*Qty` | 참조 지정자 개수 (보드 1장) |
| `Manufacturer` · `*Mfg Part #` · `Description / Value` · `*Package/Footprint` | bom-full의 Manufacturer · MPN · Value · Package |
| `Type` | `SMD` · `THT` (DC 잭 J2, RJ45 J5) · `Hybrid` (USB-C J3 — SMD 패드에 쉘 다리가 스루홀) · `Manual` (MH1 CLA216-ICR, 납땜하지 않는 기구 부품) · **DNP는 `DNS`** (R-010: 템플릿 표기) |
| `Your Instructions / Notes` | DNP면 `DNS - do not purchase/place` · bom-full AssemblyNotes에 「위탁」이 있으면 **`Consigned`**, 없으면 `Turnkey` · BTB(J1)는 `Gate G1: BTB mating check before production` · 기구 부품은 `Not soldered…` · 끝에 `Source: <유통처 번호>` |
| **시험점 (TP)** | 부품이 아니므로(PCB 패드) **BOM에서 뺀다**. 일치 검사에서도 KiCad 쪽 TP를 같이 빼고, 뺀 개수를 출력한다 (carrier 26 · front 23) |
| 회로도 밖 부품 | 모듈 101991223 · S401(BXF4677) · 렌즈 CIL093 · GH 케이블 · 어댑터 · AC 코드는 **PCBA BOM에 넣지 않는다**. 실행할 때 목록만 출력한다(우리가 조립 — R-010 S10) |
| 문자 | 출력은 **ASCII만** 쓴다 (`µ`→`u`, `≥`→`>=`, 「재고」→`stock` 등으로 바꾸고, 바꿀 수 없는 문자는 지운다). 줄바꿈은 CRLF |

## 실행 결과 (2026-11-26)

| 보드 | 행 | 참조 지정자 | 실장 | DNS | KiCad 일치 (TP 제외) | 위탁 (Consigned) |
|---|---|---|---|---|---|---|
| carrier | **50** | 73 | 66 | 7 | 참조 73 · DNP 7 **일치** | 없음 |
| front | **39** | 62 | 50 | 12 | 참조 62 · DNP 12 **일치** | D_IR_A1·A2 (VSMA1085400, Digi-Key) · D_IR_B1·B2 (DNS) · MH1 CLA216-ICR (Manual) |

- 일반 실행 `python -I make_pcbway_bom.py` → **종료 코드 0**

### R-016 재생성 (2026-11-27, IR 스트링 B 실장 — O-69)

| 보드 | 행 | 참조 지정자 | 실장 | DNS | KiCad 일치 (TP 제외) | 위탁 (Consigned) |
|---|---|---|---|---|---|---|
| carrier | 50 | 73 | 66 | 7 | 참조 73 · DNP 7 일치 | 없음 (출력 변화 없음) |
| front | 39 | 62 | **58** | **4** (C6, Q4, R11, R16) | 참조 62 일치 · **DNP 불일치 8 — 회로도 DNP 해제 대기** | D_IR_A1·A2 · **D_IR_B1·B2** (VSMA1085400, Digi-Key) · MH1 (Manual) |

- `python -I make_pcbway_bom.py` → **종료 코드 1**. stderr 출력: 「불일치 [front DNP] BOM에만: [] / KiCad에만: ['C16', 'C17', 'D2', 'D_IR_B1', 'D_IR_B2', 'L2', 'R14', 'U5']」
  - 회로도(schematic 소관)에는 이 8개가 아직 `dnp yes`로 남아 있어서 생기는 **예정된 차이**다. 다른 차이는 없다.
  - 목록과 근거는 `docs/research/r016-ir-string-b.md`에 있다.
- 확인 실행: 위 8개의 DNP만 지운 front KiCad BOM(scratchpad, 커밋하지 않음)을 `--kicad-front`로 주고 `--out`은 scratchpad로 했다 → **종료 코드 0**. 출력 CSV 2개는 일반 실행 결과와 바이트까지 같다(`cmp`).
- schematic이 DNP를 해제하면 `inputs/front-kicad-bom.csv`를 다시 내보내고 생성기를 다시 돌린다. 종료 코드 0이 나와야 끝난다.

### R-021 재생성 (2026-11-27, C-016·C-017)

| 보드 | 행 | 참조 지정자 | 실장 | DNS | KiCad 일치 (TP 제외) | 바뀐 것 |
|---|---|---|---|---|---|---|
| carrier | 50 | 73 | 66 | 7 | 참조 73 · DNP 7 일치 | R6 8.06k → **6.98k 1%** (UNI-ROYAL 0402WGF6981TCE, C47500) · **O-90: C18·C22** Samsung CL05B103KB5NNNC(C15195, 재고 0) → **FH 0402B103K500NT (C1524)** |
| front | 40 | 63 | 59 | 4 | 참조 63 · DNP 4 일치 (TP 24개 제외) | **J2 삭제**(BOM/CPL 제외 2.54mm 납땜 패드, O-84) · **R15 삭제** · **R18 1k**·**R19 10k**·**C19 10nF**(FH 0402B103K500NT, C1524) 추가 · TP24 추가 |

- `python -I make_pcbway_bom.py` → **종료 코드 0**

### R-022 재생성 (2026-11-27, C-018·C-019)

| 보드 | 행 | 참조 지정자 | 실장 | DNS | KiCad 일치 (TP 제외) | 바뀐 것 (LCSC 공개 JSON, 확인일 2026-11-27) |
|---|---|---|---|---|---|---|
| carrier | 50 | 73 | 66 | 7 | 참조 73 · DNP 7 일치 | R2 100k → **78.7k 1%** UNI-ROYAL 0402WGF7872TCE C67239 (재고 **2,100 적음** → 차선 ROHM MCR01MRTF7872 C308010 재고 9,100) · R3 13.3k → **10.7k 1%** YAGEO RC0402FR-0710K7L C138068 (재고 2,200, 차선 FH RC-02W1072FT C321262 재고 0) · R6 6.98k → **6.04k 1%** UNI-ROYAL 0402WGF6041TCE C25913 (재고 143,400) · U2 풋프린트 `…_ThermalVias` → ThermalVias 없는 변형 |
| front | 40 | 66 | 62 | 4 | 참조 66 · DNP 4 일치 (TP 24개 제외) | C19 10nF → **4.7nF**, **C20·C21 4.7nF** 추가 → `C19,C20,C21` FH 0402B472K500NT C1538 (재고 369,900) · R17 10k → **4.7k** (`R1,R5,R7,R19` 10k ×4 / `R9,R10,R17` 4.7k ×3) · **R20 1k** 추가 (`R18,R20`) |

- `python -I make_pcbway_bom.py` → **종료 코드 0**

### R-023 재생성 (2026-11-27, C-020)

| 보드 | 행 | 참조 지정자 | 실장 | DNS | KiCad 일치 (TP 제외) | 바뀐 것 (LCSC 공개 JSON, 확인일 2026-11-27) |
|---|---|---|---|---|---|---|
| carrier | 50 | 73 | 66 | 7 | 참조 73 · DNP 7 일치 | 없음 |
| front | 40 | 69 | 65 | 4 | 참조 69 · DNP 4 일치 (TP 24개 제외) | **D4·D5** BAT54WS 추가 → `D3,D4,D5` BAT54WS-7-F C124205 ×3 (재고 51,975) · **R5** 10k → 100k, **R20** 1k → 100k → 10k `R1,R7,R19` ×3 · 100k `R2,R3,R4,R5,R6,R12,R20` ×7 (C25741 재고 3,379,100) · **R21** 1k 추가 → `R18,R21` ×2 |

- `python -I make_pcbway_bom.py` → **종료 코드 0**

### R-024 재생성 (2026-11-27, C-021)

- front: **R22·R23 10k 1%** 추가 → 새 행 `[전면] R22,R23` UNI-ROYAL 0402WGF1002TCE C25744 ×2 (LCSC 재고 9,383,600, 확인일 2026-11-27). KiCad가 값 「10k 1%」를 「10k」(R1,R7,R19)와 다른 묶음으로 내보내므로 bom-full도 따로 둔다
- 결과: carrier 50행 73/66/DNS 7 · front **41행 71/67/DNS 4** 일치 (TP 24개 제외) → `python -I make_pcbway_bom.py` **종료 코드 0**
- 기록: 첫 실행은 **종료 코드 1**(「BOM에만: ['R22', 'R23']」)이었다. 원인은 새 front KiCad BOM을 `inputs/`로 복사하는 명령의 문법 오류라 옛 입력과 비교된 것이다. 복사를 고쳐 다시 돌려 종료 0

- 음성 시험: carrier KiCad BOM에서 C23을 뺀 입력 → **종료 코드 1** (「BOM에만: ['C23']」 출력)
- 음성 시험: 입력 파일 없음 → **종료 코드 2**

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | 시험점 | BOM에서 빼고, 검사에서도 TP를 제외 | 부품이 아니다. PCBWay가 시험점을 구매·실장 대상으로 잘못 볼 수 있다 | `Type=DNS` 행으로 표시 |
| B2 | 회로도 밖 부품 | PCBA BOM에서 빼고 목록만 출력 | 참조 지정자가 없고 납땜하지 않는다. 일치 검사를 깨지 않는다 | 별도 「Box build」 목록으로 PCBWay에 위탁 |
| B3 | 위탁 판정 | bom-full AssemblyNotes의 「위탁」 (R-009 판정: VSMA1085400 · CLA216) | 한 곳(bom-full)에서만 판정하게 한다 | 생성기에 품번 목록을 직접 두는 방식 |
| B4 | SRN6045TA-470M | `Turnkey` | C-005의 47µH(C5151734)는 LCSC 재고 3,990이다. R-009의 위탁 판정은 68µH 기준이었다 | 재고가 부족하면 Consigned |
| B5 | Type 값 | SMD/THT/Hybrid/Manual/DNS | R-010의 「Surface mount, Thru-hole or Hybrid」와 템플릿의 `DNS`. Manual은 우리가 추가한 값이다 | Manual 대신 `DNS`로 쓰고 Notes에 표시 |
| B6 | 입력 고정 | `inputs/`에 사본과 sha256을 둔다 | 다른 레인이 바뀌어도 재현할 수 있다 | 다른 레인 경로를 인자로 직접 준다 |
| B7 | 일치 검사 범위 | 참조 지정자 + DNP 집합 | DNP가 틀리면 실장 사고가 난다 | 참조 지정자만 |

## 한계

- **값·풋프린트 검사:** 일치 검사는 집합만 본다. 값·풋프린트가 회로도와 같은지는 bom-full을 만들 때(R-008b) 맞췄고, 이 생성기는 다시 보지 않는다.
- **회로도가 바뀌면:** `inputs/`를 새 커밋 기준으로 다시 만들고 실행해야 한다.
- **PCBWay 쪽 해석:** `Type`의 `Hybrid`·`Manual` 값을 PCBWay가 그대로 받는지는 미확인이다(템플릿 예시에는 SMD와 DNS만 있다).
