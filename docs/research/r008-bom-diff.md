# R-008 전체 BOM — 회로도(C-002)와 맞춘 결과와 R-004 초안 대비 차이

- 배정: orch t18r R-008 · 조사자 research t18s · 확인일 **2026-11-26**
- 입력 (읽기 전용):
  - C-002 회로도 `hardware/schematic/{carrier,front}` (레인 t-20261126-165741-b193, 커밋 276fc89) · README 6·11·12·14절
  - 계약 v1.2 (fd12ba4) · M-001d (c05bb28) · P-002 (022c364·ea8d1f6)
  - R-004 `bom-quote-draft.csv` (레인 t-20261126-155203-5811, d919541)
- 산출: `docs/research/bom-full.csv` — bom-template **21열**, 헤더 제외 **92행** (python csv 모듈로 확인)
  - 캐리어 47그룹 + 전면 37그룹
  - 시험점 요약 2행 (보드별)
  - 보드 밖 부품 6행: 모듈 · S401 · 렌즈 · FFC · 어댑터 · AC 코드
- 견적 요청·장바구니·업로드는 하지 않았다. 재고와 단가는 LCSC 공개 JSON(`productModel`로 검증)과 앞선 R-004 값이다.

## 1. BOM 추출 (돌린 명령과 종료 코드)

| 명령 | 대상 | 종료 코드 | 결과 |
|---|---|---|---|
| `kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP},Manufacturer,MPN,LCSC,Datasheet,Description' --group-by 'Value,Footprint,MPN,${DNP}' --ref-range-delimiter '' -o carrier-bom.csv carrier.kicad_sch` | 캐리어 | **0** | 72그룹 · 부품 91 = 시험점 26 + DNP 7 + **실장 58** |
| 같은 명령, `front.kicad_sch` | 전면 | **0** | 58그룹 · 부품 78 = 시험점 22 + DNP 12 + **실장 44** |
| `python -I build_bom.py bom-full.csv` (세션 임시 폴더의 생성 스크립트) | 합치기 | **0** | 92행 · 21열 · 매핑되지 않은 그룹 0 (있으면 스크립트가 중단되게 짰다) |

- KiCad 10.0 `kicad-cli` (`%LOCALAPPDATA%\Programs\KiCad\10.0\bin`) 기준이다.
- C-002 레인 파일은 읽기만 했다. 출력은 세션 임시 폴더에 썼다.
- front에 `~front.kicad_sch.lck`가 있었다. 다른 작성자가 파일을 열어 둔 상태일 수 있다. BOM 내보내기는 읽기 전용이라 잠금 파일은 건드리지 않았다.
- **ERC는 다시 돌리지 않았다.** orch가 다시 돌린 결과(carrier 0 · front 0)를 인용한다.

## 2. 열 채우는 규칙

| 열 | 규칙 |
|---|---|
| Reference | `[캐리어]` / `[전면]` / `[모듈]` / `[센서]` / `[광학]` / `[보드간]` / `[외부]` + 회로도 참조 지정자(그룹) |
| Quantity | `보드당 n · 5보드 실장 5n · 주문 m` (D-003 #12). DNP 행은 `5보드 실장 0 · 주문 0 (옵션 시 5n)` |
| Manufacturer · MPN | 회로도 MPN 필드가 있으면 그것(R-004 값과 같음). 없는 수동부품·잔여 부품은 **LCSC 기본(JLC Basic) 우선**, 없으면 재고가 가장 많은 Extended를 대표 품번으로 했다 |
| Package · Footprint | 회로도의 Footprint 필드 그대로 |
| PinMapVerified | 「ERC 0 (C-002) · 심벌↔풋프린트 미대조」 — 핀 대조는 P-003/L 단계 몫 |
| Distributor · Stock · MOQ · UnitPrice | LCSC 번호, 재고(LCSC, 다르면 괄호에 JLC), 첫 두 가격 구간(USD) |
| AssemblyNotes | 실장/DNP · 턴키/위탁/별도 · JLC Basic/Extended · 게이트와 주의 |

## 3. R-004 초안 대비 차이 (C-002 README 11절 + 이번 매핑)

### 3.1 품번이 바뀐 것

| 항목 | R-004 (d919541) | bom-full (C-002) | 이유 |
|---|---|---|---|
| ICR 드라이버 | DRV8837DSGR (d919541에서 이미 정정) | 전면 U2 **DRV8837DSGR** | 같음 (계약 C13) |
| microSD | SHOU HAN TF PUSH (C393941) | 캐리어 J4 **Hirose DM3AT-SF-PEJM5 (C114218)** | KiCad 공식 심벌·풋프린트가 있다 (C-002 분기 C2-1). TF PUSH는 차선(풋프린트 새로 작성 필요) |
| IR LED | VSMA1085400 4자리 (2 DNP) | 전면 D_IR_A1·A2 실장, D_IR_B1·B2 DNP | 같음 (O-25 / R-006 I2) |
| AL8860 | 2자리 (1 DNP) | 전면 U4 실장, U5 DNP | 같음 |
| 택트 스위치 | (R-004에 없음) | 캐리어 SW1·SW2 **PTS810SJG250SMTRLFS (C221895, 400gf)** | 회로도 값은 PTS810. SJM(160gf, C116501)은 LCSC 재고 0 → 분기 Q3 |

### 3.2 새로 들어간 부품 (R-004에 없음)

| 보드 | 참조 | 부품 (대표 품번) | 출처 |
|---|---|---|---|
| 캐리어 | F1 | 퓨즈 1206 3A Slow-Blow — Walter 1206T3A63V (C354897) | 계약 12절 (퓨즈/PTC 2.5~3A) |
| 캐리어 | D1 | BZT52C12 (C173429) — AO4407A 게이트 클램프 12V | 계약 11절 |
| 캐리어 | J3 · U3 | USB-C 16P HRO TYPE-C-31-M-12 (C165948) · USBLC6-2SC6 (C7519) | 계약 C4 (데이터 + VBUS 검출만) |
| 캐리어 | U4 · U5 | TPD4E05U06DQAR ×2 (C138714) — 이더넷·SD ESD | 계약 11절 |
| 캐리어 | D4 · D5 | UDD32C03L01 ×2 (C78439) — 쌍별 TVS | 계약 11절 |
| 캐리어 | Q2 / 전면 Q1·Q2 | AO3401A ×3 (C15127, JLC Basic) | microSD 전원 · 전면 스위치 |
| 캐리어 Q3·Q4 / 전면 Q3·Q5 | — | DMG1012T-7 ×4 (C20512) — 1.8V 레벨 구동 | 계약 11절 |
| 캐리어 | J6 | JST SM03B-SRSS-TB(LF)(SN) (C160403) — 디버그 UART | 계약 |
| 캐리어 | SW1 · SW2 | PTS810 ×2 (위 3.1) | RESET · UPGRADE |
| 캐리어 | L1 | Bourns SRP7028A-100M 10µH (C2687402) — TPS54302 인덕터 | 계약 3절 |
| 전면 | L1 (L2 DNP) | Bourns SRN6045TA-680M 68µH (C1330786) — AL8860 인덕터 | AL8860 DS39014 예제 |
| 전면 | D1 (D2 DNP) | SS24 (C50645) — AL8860 프리휠링 | 같음 |
| 전면 | R13 (R14 DNP) | 0.1Ω 1206 1% (C25334) — AL8860 Rs | V-001 ⑥ |
| 전면 | J2 | JST SM02B-GHS-TB(LF)(SN) (C189893) — CLA216 ICR 리드 | 계약 |
| 전면 | Q4 (DNP) | Everlight ALS-PT19 (C146233) — 아날로그 조도 차선 | 계약 C15 |
| 전면 | MH1 | CLA216-ICR (회로도 부품, 위탁) | R-002 O3 |
| 캐리어 | D3 · D6 | LED 0603 초록·파랑 — Everlight 19-217 (C2986059 / C2986058) | 전원·상태 표시 |
| 양쪽 | R·C 수동소자 | 저항 0402/0603/1206, 세라믹 0402~1206, 전해 47µF (ROQANG C72521) | 회로도 |
| 양쪽 | TP | 시험점 캐리어 26 · 전면 22 (부품 아님, 수량 0) | 회로도 |

### 3.3 R-004에서 빠진 것 / 그대로인 것

- **회로도 밖이라 bom-full에 따로 행을 둔 것:** 모듈 101991223(5), S401(7), CIL093(6), FFC(6), GST25A12-P1J(5). R-004와 같고, **AC 코드(C13)는 이번에 새로 추가**했다(MPN 미확정).
- **R-004와 품번이 같은 것:** TPS54302, TPS26600(비고 V-002 ⑥), SMBJ15A, AO4407A, DC-005-5A-2.0, HR911105A, TE 1-84952-0 ×2, HCTL BTB ×2(게이트 G1), DF30FC-24DS, RT9013-33, LTR-329, OT7EL89CJI 24MHz.
- **R-004 행 중 C-002에 없는 것:** 없다.

## 4. 미확정·주의 MPN 목록

| # | 참조 | 항목 | 상태 | 조치 (기본값 / 차선) |
|---|---|---|---|---|
| 1 | [외부] AC1 | IEC C13 전원 코드 | **MPN 미확정** (국가 플러그) | 견적 단계에서 지역 결정 |
| 2 | [전면] J2 | JST SM02B-GHS-TB (C189893) | **재고 0** (JLC 1) · CLA216 리드 커넥터가 GH 계열인지·극성 미확인 | 차선 XYECONN XY-SM02B-GHS-TB (C54582897, JLC 322) — LCSC JSON 미검증 · CLA216 실물로 계열 확인 |
| 3 | [캐리어] SW1·SW2 | PTS810 SJM (160gf) | 재고 0 → **SJG 400gf (C221895)로 대체** | 작동력 차이 수용(분기 Q3) |
| 4 | [전면] L1 | SRN6045TA-680M (C1330786) | 재고 55 (JLC 74) — 5보드 5개에는 충분 · Isat ≥1.5A 대체품 없음 | 그대로 · 재고 재확인 |
| 5 | [캐리어] C10 | CL10A105KB8NNNC (C15849) | LCSC 재고 0, JLC 11.33M | JLC 턴키면 문제없음 · PCBWay 조달은 미확인 |
| 6 | [전면] D_IR | VSMA1085400 | LCSC C6604340 재고 3 · Digi-Key 1,534 | 위탁 공급이 필요할 수 있음 |
| 7 | [캐리어/전면] J1 | HCTL BTB (치수 일치품) | 이종 짝맞춤 미검증 | 게이트 G1 |
| 8 | [센서] CAM1 | S401 → BXF4677 | 홀더 분리·강판 외곽·DF30 결합 높이 | 게이트 G2 |
| 9 | [캐리어] J2 · [전면] X1 · Q4 | DC 잭·발진기·ALS-PT19 풋프린트 | 범용·자리값 풋프린트 (C-002 Note) | 레이아웃 전에 제조사 도면과 대조 |
| 10 | 전체 | 데이터시트 리비전 | 수동부품은 시리즈 공통 문서 (리비전 미기록) | — |

## 5. 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| Q1 | 주문 수량 | 턴키 부품 = 5보드 × 보드당 수량(조립처 손실분은 조립처 몫) · 위탁·별도 = +1 예비 (렌즈·CLA216·FFC 6, S401 7) · 모듈 5 (O-16) | D-003 #12 · 위탁품은 조립 실수에 대비 | 10보드면 수량 ×2 |
| Q2 | 수동부품 대표 품번 | JLC Basic 우선 (UNI-ROYAL 저항 · Samsung/FH 세라믹) | 턴키 조립비·조달이 유리하다 | 값이 Basic에 없으면 재고 많은 Extended (13.3k·8.06k 1% YAGEO · 전해 ROQANG) |
| Q3 | 택트 스위치 | PTS810SJG (400gf, C221895) | SJM(160gf) 재고 0 | 재고가 생기면 SJM으로 돌아감 |
| Q4 | 퓨즈 | Walter 1206T3A63V Slow-Blow (63V) | 12V 입력 돌입전류(벅·eFuse) 대비 슬로우 · 정격 전압 여유 | Littelfuse 0468003 (슬로우 32V) / 0466003 (패스트) |
| Q5 | 시험점 | 수량 0인 요약 행으로 표시 | 부품이 아니다 (PCB 패드) | — |
