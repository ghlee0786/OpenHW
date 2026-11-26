# V-002 R-004 핵심 주장 독립 검증

- 배정: orch t18r V-002 · 검토자: review t18y (Opus 5.5 high) · 레인 t-20261126-163344-e260
- 확인일: **2026-11-26** (웹 확인 07:35–07:50 UTC 전후)
- 방법: 원 출처(KiCad 원본 파일, 제조사 도면·데이터시트, 판매 페이지 내장 데이터, 코어 STEP)를 다시 열어 값을 뽑았다. R-004의 결론은 전제로 쓰지 않았다.
- 검증 대상:
  - R-004 `docs/research/r004-notes.md`·`bom-quote-draft.csv` (레인 t-20261126-155203-5811, 7a9923c)
  - orch 확정 O-16·O-17·O-18
- 대조 기준:
  - 계약 v1 `hardware/schematic/hw-fw-contract.md` (레인 t-20261126-155208-d030, 8613910)
- 범위 밖으로 하지 않은 것: 구매·장바구니·견적·로그인·판매자 연락·업로드. 제품 파일·조사 문서·계약 문서는 수정하지 않았다.
  - Seeed OPL 목록 API에 읽기 조회(POST) 2회를 시도했으나 Cloudflare 403으로 막혔다. 우회하지 않았다.
- 실측: 없음. 아래 「일치·적합」은 모두 도면·데이터시트·파일 기준이고 실물 결합·기능 통과가 아니다.

## 판정표

| # | 항목 | 판정 | 핵심 근거 | 영향 받는 분기 행 |
|---|---|---|---|---|
| ① | 짝 BTB 원품번 SUNGTECH ST-BTB-058060-A/B | **일치** (OPL 부분은 확인 불가) | B301 J1: Manufacturer "SUNGTECH", MPN/Value "ST-BTB-058060-A", SKU "320210641", "SMD BTB Male CONN;2*30P-0.5mm-17.7*4.4*4mm" / S401 J1: "ST-BTB-058060-B", "320210642", Female | O-17 · R-004 B1 |
| ② | HCTL HC-PBB05-2-60-M/F-H4.0 도면 ↔ B301 풋프린트·코어 STEP | **부분 일치** (불일치 2건 · 확인 불가 1건) | 피치·핀수·패드열 간격 4.0·1~30번 14.5·기둥 간격 16.4·치우침 1.25·높이는 일치. **플러그 몸체 폭**(HCTL 4.40 / ST 원품 4.00)과 **패드 폭**(풋프린트 0.25 / HCTL 권장 0.30)은 다름. HCTL 도면에 **1번 핀 표기가 없음** | O-17 · R-004 B1·B1-조건 |
| ③ | 짝 높이 8.0mm | **일치** (ST끼리 결합은 간접 확인) | HCTL 「Ass'y High(H)」 표 「8.00 \| Female 4.00 \| Male 4.00」, 「H±0.15 = H1 + H2」. LCSC System Fit Height에 8mm 포함. 코어 STEP: 플러그 어깨 4.00·혀 끝 5.90, 소켓 4.00 | O-17 · 기구 M-001 적층 높이 |
| ④ | BXF4677 모듈 DF30 24P ↔ S401·계약 v1 | **일치** (주의 4건) | 모듈 도면 「P/NO. PIN define」 24핀이 S401 J2 넷과 모두 맞음. 단 번호 체계가 다름(대응식은 추론). 24번 = **RESET**(확정). S401 J2 ↔ 계약 5.1 24핀 일치. 전면 BTB 60핀 ↔ S401 J1 불일치 0건 | O-18 · R-004 S1 · 계약 5.1 |
| ⑤ | Seeed 공개 재고 JSON 101991223 | **일치** (07:37 UTC 재조회) | `warehouseStockData` = {"2": 55, "5": 0, "11": 7}, `stock_status IN_STOCK`, `product_stage MP`, `price_tiers []`. 창고 5=US는 가격으로 확정, 2·11의 국가 대응은 미확정 | O-16 |
| ⑥ | TPS26600(12V_IR)·TPS54302(5V) ↔ 계약 v1 전력 | **TPS54302 적합 · TPS26600 조건부** | TPS54302: VIN 4.5~28V(절대최대 30V), 3A 연속, 예산 피크 1.3A에서 여유 큼. TPS26600: 정격·전류제한은 충분하지만 **UVLO 핀을 GPIO EN으로 쓰는 용법은 데이터시트에 없다**. GPIO 제어 핀은 SHDN이다 | R-004 P1·P2 · 계약 3·12절 (IR_LED_EN 연결) |

## ① 짝 BTB 원품번

| 출처 | 원문 | 판정 |
|---|---|---|
| B301 `b301.kicad_pcb` (sha256 b4b974b3…adf1f) 3217행 부근 | footprint "Connector:BTB60-Male-Female-0.5-17.7x4.4mm", Reference "J1", Value "ST-BTB-058060-A", Description "SMD BTB Male CONN;2*30P-0.5mm-17.7*4.4*4mm", Manufacturer "SUNGTECH", MPN "ST-BTB-058060-A", SKU "320210641". 3D 모델 `320210641_Sungtech_ST-BTB-058060-A_3D.stp` | 일치 |
| S401 `s401.kicad_pcb` (783d3aa3…eb2) · `s401.kicad_sch` (3da62d3b…74ba) | Description "SMD BTB Female CONN;2*30P-0.5mm-17.7*4.4*4mm", Manufacturer "SUNGTECH", MPN "ST-BTB-058060-B", SKU "320210642" | 일치 |
| 코어 STEP `Recamera Core 2002.step` (7de9f15f…8785) | 모델 이름 J1 `SHANGQI_0_5BTB_60P_4_0H_PLUG`(윗면), J2 `SHANGQI_0_5BTB_60P_4_0H_SOCKET`(아랫면) | 일치 (3D 모델 이름은 제조사명이 다르게 적혀 있음) |
| Seeed Fusion OPL (`napi.seeedstudio.com/opl/list`) | 2회 시도 모두 HTTP 403 (Cloudflare "Just a moment…") | **확인 불가** — R-004의 OPL 단가 USD 0.5851은 재확인하지 못했다 |

- 참고: B301 파일에는 SUNGTECH 필드가 하나 더 있다(USB-C `ST-USB-Y3120`). 짝 BTB와는 무관하다.

## ② HCTL 도면 ↔ B301 풋프린트 ↔ 코어 STEP 수치 대조

출처:
- HCTL 플러그 데이터시트(LCSC 사본, e132724c…4064): https://datasheet.lcsc.com/datasheet/pdf/ee313a7bf73f17b02eb2735a2b008b8f.pdf?productCode=C41421115
- HCTL 소켓 데이터시트(LCSC 사본, 8424de3b…768b): https://datasheet.lcsc.com/datasheet/pdf/85738d87feeec2151dd73ca6cfcedf74.pdf?productCode=C41421025
- B301·S401 풋프린트는 파일에서 파싱했다.
- 코어 STEP: https://raw.githubusercontent.com/Seeed-Studio/OSHW-reCamera-Series/main/hardware/recamera-2002/core/c1-2002/3D_Printed_Case/Recamera%20Core%202002.step (저장소 HEAD f5fcf0a). gmsh(OpenCASCADE)로 B-rep 꼭짓점을 집계했다.

| 항목 | HCTL 도면 | B301/S401 풋프린트 | 코어 STEP (ST 원품) | 판정 |
|---|---|---|---|---|
| 피치 | 0.50±0.1 | 0.50 | 0.50 | 일치 |
| 핀 수 | 60 | SMD 패드 60 | 리드 60 | 일치 |
| 몸체 길이 | 17.70 (C) | 17.70 (실크·코트야드·Fab) | 17.70 | 일치 |
| 몸체 폭 — 플러그 | **4.40** (F, H2=4.0 행) | 4.40 (외곽선) | **4.00** | **불일치** — HCTL 플러그가 원품보다 0.4mm 넓다. 4.4 코트야드 안이라 실장 간섭은 없어 보인다 |
| 몸체 폭 — 소켓 | 4.40 | 4.40 | 4.40 | 일치 |
| 리드 끝 폭 | 5.20±0.1 | — | 5.20 | 일치 |
| 패드 | 권장 0.30×1.80 | **0.25×1.8** (60개, roundrect) | — | **불일치** — 폭 0.05mm 차이. 제조 DFM·솔더량 검토 대상 |
| 패드 열 중심 간격 | 4.00 (바깥 5.80, 안쪽 2.20) | 4.00 (y ±2.0) | 리드 열 4.0 | 일치 |
| 1~30번 패드 중심 길이 | 14.50 (A) | 14.50 (x −7.25~+7.25) | 14.50 | 일치 |
| 위치 결정 기둥 | 보스 Ø0.50, 권장 구멍 Ø0.55 +0.05/−0 | NPTH Ø0.60 (드릴 0.6) | 보스 Ø0.50 | 일치 (0.60은 권장 상한) |
| 기둥 간격 | 16.40 (D) | 16.40 (±8.2) | 16.40 | 일치 |
| 기둥 치우침 | 중심선에서 1.25 (두 구멍 같은 쪽) | 1.25, **1번 열 반대쪽(짝수 열)** | 1.25 | 일치 |
| 1번 핀 ↔ 기둥 치우침 관계 | **핀 번호 표기 없음** | 기둥이 1번 열 반대쪽 | 핀 번호 없음 | **확인 불가** (HCTL 쪽) |
| 정격 전류 | 기술 지표에 항목 없음(125V AC, ≤0.02Ω, ≥100MΩ, −40~85°C). LCSC 「Current Rating (Max)」 "-" | — | — | **확인 불가** — 계약 3.2의 VIN 4핀 핀당 0.33A 근거 없음 |

B301 배치 주장(보드 중심 원점):
- 보드 30×30
- 짝 커넥터 중심 (+11.801, −0.001), 회전 −90°
- 1번 패드 (+13.801, −7.251)
- NPTH (+10.551, ±8.2)

→ R-004 1.1절 값과 **일치**한다. y는 KiCad 좌표 방향(아래가 +)이다.

**판정: 부분 일치.**
- 랜드 패턴, 기둥, 높이는 원품·풋프린트와 같다. 그래서 「풋프린트는 ST/범용 공통 치수로 그린다」는 B1 선택은 유지할 수 있다.
- 다만 아래 세 가지는 O-17의 「치수 일치」 표현에서 빠져 있다.
  1. HCTL 플러그 몸체가 원품보다 0.4mm 넓다.
  2. 패드 폭이 HCTL 권장과 다르다.
  3. HCTL 쪽 1번 핀 방향을 도면으로 정할 수 없다. 혀 폭과 접점 형상도 HCTL 도면에 없다(ST 혀 폭 약 2.4).
- **영향:**
  - O-17 · B1-조건(실물 결합 확인 전 발주 금지) 게이트는 **유지가 맞다.** 확인 항목에 다음을 더해야 한다:
    - 1번 핀 방향(기둥 치우침 기준으로 매핑)
    - 혀 폭·유지력
    - 핀 전류 정격(VIN 4핀)
  - C-002 풋프린트 패드 폭(0.25 원품 기준 vs 0.30 HCTL 권장)은 새 분기로 정해야 한다.
- R-004 표 표현 정정: 「소켓 Ø0.55」는 소켓 보스 지름이 아니라 **PCB 권장 구멍 지름**이다(보스 Ø0.50).

## ③ 짝 높이 8.0mm

| 근거 | 원문·측정 | 판정 |
|---|---|---|
| HCTL 도면 「公、母座-合高图」 | 「Ass'y High(H)」 표 행 「8.00 \| Female 4.00 \| Male 4.00」, 「H±0.15 = H1 + H2」. 주문 코드 「H4.0=4.0mm」(플러그 H2·소켓 H1), 플러그 혀 G 1.90 | 일치 |
| LCSC 상품 페이지 System Fit Height | 플러그 「7mm;7.5mm;8mm;8.5mm」, 소켓 「5mm;6mm;8mm」 | 일치 |
| 코어 STEP (ST 원품) | 플러그 어깨 4.00, 혀 끝 5.90 / 소켓 전체 4.00 (리드 바닥 기준) | 4.0+4.0과 들어맞음. 결합 상태는 직접 측정 못 함 → 간접 |

- **판정: 일치.** 공차는 HCTL끼리 ±0.15다.
- ST 원품끼리의 결합 높이, 그리고 HCTL과 ST를 섞어 결합한 높이는 도면 근거가 없다. 실물 측정이 필요하다.
- 「업계 공용 높이표」 주장은 HCTL 도면에서만 확인했다. XUNPU·Huamingtong은 보지 않았다.

## ④ BXF4677-GC2053 DF30 24P 핀배치

출처:
- 모듈 문서 https://files.seeedstudio.com/wiki/reCamera/reCamera_hq_poe/lens_document.pdf (HTTP 200, 764,312 B, sha256 9f811140…fdd1)
  - 5쪽 「5.结构图」의 「P/NO. PIN define」 표를 렌더링 이미지로 직접 판독했다.
  - 3쪽 규격 「电源电压 AVDD:2.8V;DVDD:1.2V;DOVDD1.8V」, 「连接方式 BTB」
- S401 회로도·PCB 넷: kicad-cli 넷리스트와 PCB 패드 넷
- 제조 zip `319000023_…_final_250905(1).zip`의 회로도 PDF: J2 넷과 DNP 목록이 같음

모듈 원문:
`01 GND · 02 GND · 03 GND · 04 GND · 05 MDP1 · 06 MDN1 · 07 MCP · 08 MCN · 09 MDP0 · 10 MDN0 · 11 SCL · 12 SDA · 13 GND · 14 MCLK · 15 GND · 16 GND · 17 GND · 18 3.3V(AVDD…) · 19 3.3V(IOVDD…) · 20 3.3V(DVDD…) · 21 GND · 22 GND · 23 GND · 24 RESET`

| S401 J2 핀 | S401 넷 | 모듈 P/NO | 계약 v1 5.1 | 판정 |
|---|---|---|---|---|
| 1 / 3 | CAM_I2C2_SDA / SCL (풀업 4.7k → CAM_1V8) | 12 SDA / 11 SCL | SDA / SCL | 일치 |
| 5 / 7 | CAM_RX0_0N / 0P | 10 MDN0 / 9 MDP0 | D0−/+ | 일치 |
| 9 / 11 | CAM_RX0_CLKN / CLKP | 8 MCN / 7 MCP | CLK−/+ | 일치 |
| 13 / 15 | CAM_RX0_1N / 1P | 6 MDN1 / 5 MDP1 | D1−/+ | 일치 |
| 17·19·21·23 | GND | 4·3·2·1 GND | GND | 일치 |
| 2·6·8·10 | GND | 13·15·16·17 GND | GND | 일치 |
| 4 | 24MHz (X1 → R18 0Ω) | 14 MCLK | MCLK | 일치 |
| 12 | AVDD (Q8 스위치, 3.3V) | 18 3.3V(AVDD) | AVDD | 일치 |
| 14 | IOVDD (Q3 스위치, 3.3V) | 19 3.3V(IOVDD) | IOVDD | 일치 — **3.3V 전원 입력**이다(신호 레벨 아님) |
| 16 | AVDD (Q8) | 20 3.3V(DVDD) | AVDD | 넷 일치. 모듈 쪽 기능은 DVDD 공급 |
| 18·20·22 | GND | 21·22·23 GND | GND | 일치 |
| 24 | R8 10k ← CAM_EN, R7 10k → GND **DNP** | 24 **RESET** | 「리셋/PWDN 추정」 | 일치 — **RESET으로 확정** |

- 번호 대응(**추론**, 24핀 모두 이 식으로 맞음): 모듈 m=1~12 ↔ J2 (25−2m), m=13~24 ↔ J2 2(m−12). 1↔1로 맞대면 바로 어긋난다(모듈 1 GND ↔ J2-1 SDA). 실물 도통으로 확인해야 한다.
- 경로: 코어 J1 → 전면 BTB → DF30 경로를 스크립트로 대조했다(계약 5절 60핀 ↔ S401 J1 넷, 불일치 0건). 예: CLKN 10→9, CLKP 12→11, 0N 16→5, 0P 18→7, 1N 22→13, 1P 24→15, SCL 9→3, SDA 11→1.
- 코어 SCH 6쪽: MIPIRX0→CAM_RX0_0, RX2→CLK, RX3→CAM_RX0_1. SDK `{2,0,3}` 해석과 일치한다.

**판정: 일치.** 주의 4건:
1. **전압 도메인**
   - 모듈 전원 3핀은 모두 3.3V 입력이고, 신호(I2C 풀업·MCLK)는 1.8V다.
   - I2C 풀업과 MCLK 발진기 전원은 CAM_1V8이다. CAM_1V8은 코어 1V8을 Q6로 스위치한 것이고 CAM_EN이 켠다. 레벨 변환은 없다.
   - 따라서 CAM_EN=0이면 I2C 풀업도 꺼진다. 같은 버스의 LTR-329는 「CAM_EN=1에서만 접근」 제약을 따른다(계약에 이미 있음).
2. **전원 순서(위험, 확인 불가)**
   - S401에서 IOVDD·CAM_1V8 지연 커패시터 C26·C27은 DNP이고, AVDD만 C28 100nF로 약 0.1ms 늦게 켜진다.
   - RESET에는 RC가 없어 공급 전원보다 먼저 올라갈 수 있다. 이는 모듈 문서 4쪽 순서(IOVDD→DVDD→AVDD→PWDN→RESETB)와 다르다.
   - Seeed 양산품은 이대로 동작하는 것으로 보인다. 전면 보드에는 **RESET RC 자리(DNP 가능)**를 두는 것을 C-002에 넘길 만하다.
3. **MCLK**: S401 X1 9C24000004 「SMD Oscillator;24MHZ-1.8V-15ppm-3mA」. VDD=CAM_1V8, EN←CAM_EN(R9 1k). 계약 9절과 일치한다.
4. **모듈 쪽 커넥터 품번**: 문서에는 「BTB」라고만 적혀 있다. 후보 Hirose DF30RC-24DP-0.4V는 **추론**이다. Hirose 공식 페이지는 403이라 짝 핀 번호 규칙을 1차 자료로 확인하지 못했다.

**영향:**
- O-18·S1 핀 계약은 그대로 써도 된다.
- 계약 5.1 표기 정정 권고 3건:
  - 14 「IOVDD」 → 「IOVDD 3.3V 전원」
  - 16 「AVDD」 → 「모듈 DVDD용 3.3V(AVDD 넷)」
  - 24 「추정」 → 「RESET」
- M12·ICR 병용은 범위 밖이다(R-006).

## ⑤ Seeed 공개 재고 JSON (101991223)

- 출처: https://www.seeedstudio.com/reCamera-Core-2002-8GB-p-6433.html
  - 기본 UA 요청은 HTTP 403(Cloudflare)이었다.
  - 브라우저 헤더로 다시 요청해 HTTP 200, 276,076 B를 받았다.
  - 확인 시각 **2026-11-26T07:37:27Z**, sha256 28f76679…42e5df
- 원문(이스케이프 제거): `"warehouseStockData":{"2":{"available_qty":55,"shipment_date":"","batch":[{"BatchNO":"CUSTOM250101","AvaTransitQTY":1000000,"Date":"2027-01-16 07:32:10"}],"xn_available_qty":1000000},"5":{"available_qty":0,"shipment_date":"","batch":[],"xn_available_qty":0},"11":{"available_qty":7,"shipment_date":"","batch":[],"xn_available_qty":0}}`
- 같은 페이지 값:
  - `"stock_status":"IN_STOCK"`, `"product_stage":"MP"`, `"sku":"101991223"`
  - `price_range_by_warehouse`: 2 → 60.63(정가 65.90), **5 → 63.47(정가 68.99)**, 11 → 60.63
  - `price_tiers []`
  - UI 문자열 "Production begins after payment. Estimated lead time 4-6 weeks."
- V-001 때 「값 6개(55, 1000000, 0, 0, 7, 0)」로 기록한 것은 `available_qty` 3개와 `xn_available_qty` 3개였다. 이번에 구조를 확인해 해소했다.

**판정: 일치** (R-004 3.1의 55 / 0 / 7). 정리:
- 창고 5 = US는 가격으로 확정된다. 창고 2·11이 CN·DE 중 어느 쪽인지는 데이터에 이름이 없어 **미확정**이다. 두 창고의 가격이 같다.
- 창고 2의 `batch CUSTOM250101 AvaTransitQTY 1000000 (2027-01-16)`은 자리표시 값으로 보인다(**추정**). 재고 합에 넣지 않는다.
- **O-16 영향:** 공개 데이터상 55+7=62로 5개 조건을 넘으므로 (a) 유지 판단과 맞는다. 다만 `available_qty`가 실제 주문 가능 수량인지는 공개 자료로 확정할 수 없다(화면 문구 틀과 주문 전 확인 필요). 구매는 사용자 지시 사항이다.

## ⑥ 12V_IR TPS26600 · 5V TPS54302 ↔ 계약 v1 전력

계약 v1 3절 기준값(가정):
- 12V 입력 합계 ≈1.2A(14.7W)
- 5V_SYS 「3A급, 입력 정격 ≥28V」, 예산 피크 ≈1.3A
- 12V_IR 1.0A 연속(AL8860 입력 ≈0.61A)
- 어댑터 12V 2.08A
- 보호: TVS SMBJ15A
- IR_LED_EN은 1.8V GPIO, 풀다운, Low=끔

### TPS54302DDCR — **적합** (3A 연속은 방열 조건부)
- 출처: TI SLVSDG6C (2026-03 개정) https://www.ti.com/lit/ds/symlink/tps54302.pdf (d81679ba…51b8). 부록상 Active.
- 원문·값:
  - 권장 VIN 4.5~28V, 절대최대 −0.3~30V
  - "Integrated 85mΩ and 40mΩ MOSFETs for 3A, continuous output current"
  - 상측 전류제한 4/5/6A, 400kHz(290~510), Eco-mode(피크 500mA 미만에서 펄스 스킵)
  - tMIN_ON 110ns typ
  - θJA 118.9°C/W (JEDEC) / 57.2°C/W (EVM)
- 계산:
  - 12V→5V 듀티 0.417, 온타임 약 1.04µs ≫ 110ns
  - 효율(그림 7-2 판독): 1.3A에서 약 95.5% → 손실 약 0.31W, JEDEC 기준 +36°C
  - 3A에서 약 92.4% → 총손실 약 1.23W, IC 손실 약 0.8~1.0W. JEDEC 보드면 +95~119°C로 불가, EVM급 구리면적이면 +46~57°C
- 판정:
  - 계약 「3A급」은 정격으로 **일치**한다. 예산 1.3A에서는 여유가 크다.
  - 3A 연속을 실제로 쓰려면 EVM급 구리면적이 필요하다.
  - 「입력 정격 ≥28V」는 권장 최대 28V로 경계에서 충족한다.
  - SMBJ15A 클램프 24.4V가 절대최대 30V 이하라는 점은 맞다. 다만 Littelfuse 공식 데이터시트가 403으로 막혀 24.4V는 유통사 자료(VBR min 16.7V, VC 24.4V @IPP 24.6A)로만 확인했다 → **확인 불가(공식)**.

### TPS26600PWPR — **조건부** (P1의 연결 방식은 불일치)
- 출처: TI SLVSDG2G https://www.ti.com/lit/ds/symlink/tps2660.pdf (b781cbce…e1de). TPS26600PWPR Active.
- 원문·값:
  - 권장 IN 4.2~60V(절대최대 −60~62V)
  - "0.1-A to 2.23-A Adjustable current limit (±5% accuracy at 1 A)", I(OL)=12/R(ILIM)[kΩ]
  - RON 25°C 150mΩ typ, 최대 250mΩ(−40~125°C)
  - HTSSOP θJA 38.6°C/W
  - 역전류 차단(V(REVTH) −10mV typ)
  - MODE 핀: 개방=회로차단기+자동재시도 / RTN=전류제한+자동재시도 / 402kΩ=래치
- 계산:
  - 1.0A에서 손실 0.15W typ / 0.25W 최악 → +9.7°C
  - 실제 0.61A면 최대 0.093W
- **연결 방식 문제(원문으로 확인):**
  - UVLO 핀 설명: "Connect UVLO pin to RTN pin to select the internal default threshold" (283행)
  - V(SEL_UVLO) 180/200/240mV (414행)
  - V(IN_UVLO) 「Factory set V(IN) undervoltage, V(IN) rising, V(UVLO) = 0 V」 **14.25/14.9/15.75V** (409행)
  - "If the Under-Voltage Lock-Out function is not needed, the UVLO terminal must be connected to the IN terminal. UVLO terminal must not be left floating." (1277–1278행)
  - GPIO 제어용으로 명시된 것은 SHDN이다: "can be switched off by pulling the SHDN pin below 0.76 V threshold with a micro-controller GPIO pin … the pull down must sink at least 10 µA at 400 mV. To enable the device, SHDN must be pulled up to atleast 1 V." (1677행~)
- **결과:**
  - P1의 「1.8V GPIO로 UVLO 핀을 구동」은, 켜는 쪽은 동작한다. 상승 문턱 1.225V max < 1.8V이고 핀 누설은 ±100nA다.
  - 그러나 GPIO=Low이면 데이터시트상 「내부 UVLO 선택」 상태가 된다. 이때 꺼짐은 12V가 내장 UVLO 14.25~15.75V보다 낮아서 생기는 결과일 뿐이다.
  - SMBJ15A는 VWM 15V라 14.25~16.7V 구간을 막지 않는다. 입력이 이 구간이면 **GPIO Low에서도 12V_IR이 켜질 수 있다.**
  - 데이터시트에 이 용법의 근거가 없다 → **불일치**.
- **조건(이렇게 하면 적합):**
  1. IR_LED_EN → **SHDN**, 외부 풀다운 10kΩ. 0.4V에서 40µA로 ≥10µA를 충족한다. SHDN 내부 풀업 2.7V typ이 있어 풀다운이 없으면 기본 ON이 된다.
  2. UVLO → IN 직결(또는 분압으로 설정)
  3. ILIM **10.0kΩ ≈ 1.2A** (1.0A 연속 + 여유, 5V 벅 입력 약 0.6A와 합쳐도 1.8A로 어댑터 2.08A 안). 8.06kΩ(1.49A)은 합계가 어댑터 한도에 닿아 비권장.
  4. dVdT 22nF ≈ 2.1ms 램프(AL8860 입력 47µF 기준 돌입 약 0.27A). 기본(개방) 램프면 47µF에서 약 0.7A다.
- 탈락 사유 확인: TPS27S100(SLVSE42B)과 TPS1H000-Q1(SLVSDO6E)은 VIH min 2V, VIL max 0.8V → R-004 주장과 **일치**한다.
- **영향:**
  - R-004 P1의 「선택 IC」는 유지한다. 「1.8V GPIO로 UVLO 핀 구동」은 「SHDN 구동 + 10k 풀다운」으로 고쳐야 한다.
  - 계약 v1 3.1 트리의 「부하 스위치(IR_LED_EN)」와 12절 12V_IR 행(전류 제한 부하 스위치)도 같은 연결로 넘겨야 한다(C-002).
  - 계약 수치(12V 1.2A, 5V 3A급)와는 두 IC 모두 정격이 맞는다.

## 범위 밖 관찰 (판정 아님, orch 참고)

- R-004 BOM `U_ICR`은 아직 **UMW AP1511B**다. 계약 v1(8613910) 커밋 메시지와 3.1 트리는 ICR 드라이버를 **DRV8837**로 바꿨다(V-001 ⑤ 반영). BOM과 계약이 다르다.
- BXF4677 모듈 자체 렌즈는 EFL 2.9mm다. Seeed S401 README 공표값은 84°H / 93°D다. D-003 #4 90°와의 비교는 R-006 몫이다.

## 분기점·선택·이유·차선책 (검증 중 생긴 갈림길)

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| V1 | Seeed OPL API 403 | ① OPL 부분은 「확인 불가」, 원품번은 KiCad 원본 필드로 판정 | Cloudflare 차단을 우회하지 않는다(외부 시스템 보호) | 사람이 브라우저로 OPL 확인 |
| V2 | Seeed 상품 페이지 기본 요청 403 | 브라우저형 헤더로 1회 재요청(일반 공개 페이지 GET) | 같은 공개 페이지이고, 로그인·자동화 우회 기술을 쓰지 않았다 | 사람이 브라우저로 확인 |
| V3 | ② 「일치」 기준 | 랜드·기둥·높이 일치와 몸체 폭·패드 폭 차이를 분리해 「부분 일치」 | PCB 랜드 호환과 부품 외형 차이는 영향이 다르다(실장 vs 기구·DFM) | — |
| V4 | ④ 모듈 번호 체계 | 대응식을 「추론」으로 표기하고 24핀 전부 대조 | 모듈 도면과 J2의 번호 규칙이 다르고, Hirose 짝 규칙 원문이 없다 | 실물 도통 시험 |
| V5 | ⑥ SMBJ15A 클램프 값 | 유통사 값(24.4V)을 쓰되 「공식 확인 불가」 표기 | Littelfuse 공식 PDF가 Akamai 403 | 사람이 Littelfuse 데이터시트 확인 |

## 남은 확인 항목
1. HCTL↔SUNGTECH 실물 결합: 1번 핀 방향, 혀 폭·유지력, 결합 높이 실측, VIN 핀 전류 정격(O-17 게이트)
2. C-002 풋프린트 패드 폭(0.25 vs 0.30) 결정
3. BXF4677 ↔ DF30 번호 대응 실물 도통, 모듈 쪽 커넥터 품번
4. 전면 보드 RESET RC 자리 여부(전원 순서)
5. TPS26600 SHDN 연결로 계약·회로 반영, Littelfuse SMBJ15A 공식 수치
6. Seeed `available_qty`가 실제 주문 가능 수량인지(구매 단계, 사용자 지시 필요)

## 증거 파일
모두 세션 임시 폴더 `C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\2304a8aa-eb88-41c3-9975-aa6fda3de30c\scratchpad\` 아래에 있다. 저장소에는 보관하지 않았다. sha256은 본문 각 항목에 적었다.

| 폴더 | 내용 |
|---|---|
| `v002-btb\` | HCTL 데이터시트 2개, 렌더 이미지, 코어 STEP |
| `v002-sensor\` | lens_document.pdf, 핀표 이미지 `pin_rot.png`, S401 넷리스트 |
| `v002-power\` | TPS2660, TPS54302, TPS27S100, TPS1H000-Q1 데이터시트 |
| `v002-seeed\` | p6433b.html |
| `v001-recam\gh\` | B301·S401 KiCad 원본 (V-001에서 받음) |

## 돌린 명령
- 저장소 테스트·빌드 명령: 돌리지 않음(이 레인은 문서 1개만 추가하고, 하네스 검사가 「찾지 못했다」로 나옴)
- KiCad ERC/DRC: 해당 없음(검증 대상 CAD 없음). S401 넷리스트는 하위 에이전트가 `kicad-cli`로 내보냈고, 원본 sha256은 그대로다.
