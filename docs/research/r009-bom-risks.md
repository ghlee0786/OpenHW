# R-009 BOM 미확정·재고 위험 해소 (R-008 diff 4절 ①②④⑤⑥⑨)

- 배정: orch t18r R-009 · 조사자 research t18s · 확인일 **2026-11-26**
- 레인: R-008과 같은 레인 (t-20261126-171912-e7d2)
- 방법: 공개 페이지와 LCSC 공개 JSON(`productModel`로 검증)만 사용했다. 구매·장바구니·견적·업로드·문의·로그인은 하지 않았다.
- `bom-full.csv` 갱신: 12행의 비고·차선·유통처를 고쳤다. 21열과 92행은 그대로다(python csv로 확인).

## 결론표

| # | 항목 | 결론 (1안) | 차선 | 근거 | 재고·가격 | 상태 |
|---|---|---|---|---|---|---|
| ① | AC 코드 (GST25A12-P1J의 C14 인렛과 짝) | **GlobTek 2313K3432M5701(R)** — KS C 8305 플러그 ↔ IEC C13, 2.5m, 10A/250VAC, H05VV-F 3×1.0mm² | Interpower 86263010 (DK 재고 0, No Backorders) / 디바이스마트 MachLink ML-PWG050 (C13 250V/16A, 13,200원, KC 번호 미기재) | https://www.digikey.com/en/products/detail/globtek-inc/2313K3432M5701-R/9837681 · 도면 https://www.globtek.com/pdf/manual-datasheets/2313K3432M5701(R).pdf | Digi-Key 1939-1616-ND 재고 1,319 · USD 8.41 (1) / 7.146 (10) | 확인됨. 도면의 플러그·케이블·커넥터에 KC 마크가 있다. **KC 인증번호는 미확인** |
| ② | CLA216-ICR 리드 짝 헤더 | **계열 미확정. 근거상 Molex PicoBlade(MX1.25) 추정** → 직각 **Molex 53261-0271** (LCSC C177225 재고 10,160, 5개 USD 0.148 / Digi-Key WM7620 재고 38,882) | GH로 판명되면: JST **SM02B-GHS-TB** (Digi-Key 재고 52,844, USD 0.35. LCSC 재고 0) 또는 수직 BM02B-GHS-TBT (DK 재고 92,471) | 아래 「② 판정 근거」 | — | 계열은 **추정** · 극성과 선 색은 확인됨 |
| ④ | 68µH 6045 인덕터 (Isat ≥1.5A) | **Bourns SRN6045TA-680M 원품을 Digi-Key에서** (SRN6045TA-680MCT-ND) | Chilisin **LVS606045-680M-N** (LCSC C304398 재고 895, 5개 USD 0.10) — Isat 1.6A typ, DCR 330mΩ±30%, Irms 1.0A (원품 1.1A보다 약간 낮음) | Bourns·Chilisin 데이터시트 (LCSC 사본) | Digi-Key 재고 5,650 · USD 0.50 (1) / 0.408 (10) | 확인됨 |
| ⑤ | C15849 (0603 1µF 50V X5R, LCSC 재고 0 · JLC 1,133만) | **JLC 턴키면 그대로** · LCSC 조달(PCBWay 등)이면 **Yageo CC0603KRX7R9BB105 (C559769, X7R 50V)** | FH 0603B105K500NT (C90540, X7R 50V) · Murata GRM188R61H105KAALD (C77386) | LCSC JSON | C559769 재고 266,960 (20개 USD 0.0356) · C90540 재고 322,720 (20개 USD 0.0141) | 확인됨 (대체품은 JLC Extended) |
| ⑥ | VSMA1085400 (LCSC C6604340 재고 3) | **Digi-Key 751-VSMA1085400CT-ND** (Active) → **LCSC 턴키는 불가, 위탁(Digi-Key 확보)으로 표시** | Mouser 78-VSMA1085400 | https://www.digikey.com/en/products/detail/vishay-semiconductor-opto-division/VSMA1085400/15786357 · Vishay 재고 조회 | Digi-Key 재고 1,534 · USD 3.21 (1) / 2.34 (10) · Mouser 973 (Vishay 조회 기준 2차 수치, 가격 미확인) | Digi-Key 확인됨 · Mouser 미확인 |
| ⑨ | 풋프린트 3종 vs 제조사 도면 | 아래 표: **J2 DC 잭 수정 필요 · X1 발진기 그대로 · Q4 ALS-PT19 새 풋프린트 필요** | — | 도면 URL·sha256은 아래 | — | 확인됨 (일부 판독) |

## ② 판정 근거 (CLA216-ICR 리드 커넥터)

1. **원문:** 「2ピン1.25mm JSTコネクタ」 / 「2-pin 1.25mm JST connector」. CLA214·CLA219도 같은 문구이고, 계열명은 없다.
   - 출처: https://ja.commonlands.com/products/ir-cut-off-filter-switcher-m12-cla216
   - CLA216-ICR-850BP 페이지는 「compatible with a standard 2 pin connector」라고 하고 Alibaba 「Wafer Connector 1.0/1.25」로 링크한다. 그 페이지는 캡차로 열지 못했다.
2. **도면 실측 (판독, 9.1 px/mm로 보정):** 하우징은 너비 약 4.9/4.5, 길이 약 4.85, 두께 약 3.5/2.65이고, 전선 쪽에 넓은 칼라가 있으며 잠금 레버는 없다.
   - 이 형상은 MX1.25(PicoBlade 호환, 칼라가 있고 너비:길이 약 1:1)와 같다.
   - GH(길이 5.75, 위쪽 잠금 레버, 칼라 없음)와는 다르다.
   - 단, 실측 절대값은 두 계열 모두와 15~30% 차이가 난다.
3. **사진:** CLA214 고해상도 사진의 하우징은 Molex 51021형에 가깝다. CLA216 사진은 해상도가 낮아 판별할 수 없다.
4. **판정을 막는 것:** 상세 도면과 STP는 DocSend 링크로만 제공된다. DocSend가 가입·이메일을 요구할 수 있어 열지 않았다.
   - 확정하려면 **실물 하우징 길이를 재야 한다.** 약 4.0이면 PicoBlade, 약 5.75에 레버가 있으면 GH다.
   - 이 확인은 게이트 G2 시점에 같이 하기를 권고한다.
5. **극성·선 색 (확인됨):** 「正極を赤色のリード線に接続する正極性ではフィルタが開き、逆極性では閉じます」 (CLA216 FAQ) · 「Red is positive and black is negative」 (CLA214 FAQ) · 코일 20Ω, 3.3V로 100~500ms 펄스
6. **호환:** 두 계열 모두 피치 1.25이고 고정 탭이 2개다.
   - 1안 Molex 53261-0271은 Molex 51021 하우징의 원래 짝이다.
   - 저가 호환품(CJT·HCTL)이 Molex/JST와 맞물리는지는 미확인이다. 그래서 1안은 원품으로 잡았다.
7. **회로도와 불일치:** C-002 전면 J2의 풋프린트는 JST GH(`SM02B-GHS-TB`)다. 판정 결과에 따라 schematic이 풋프린트를 바꿔야 할 수 있다(orch에 전달).

## ⑨ 풋프린트 대조 (KiCad 10.0 기본 라이브러리 vs 제조사 도면)

### 캐리어 J2 DC 잭 — `Connector_BarrelJack:BarrelJack_Horizontal` vs XKB DC-005-5A-2.0

- **도면:** https://datasheet.lcsc.com/datasheet/pdf/781816078c0f2c3415b95730e83b719f.pdf?productCode=C381116
  - 도면번호 X-DC-005-5A-2.0, Rev **A1 (2025-04-22, 치수 변경)**
  - sha256 `39bae627e5a7c251b060ae2546a004b09bc0ab5d4249a639b3deb15e9cfa3886`
- **비교한 풋프린트:** sha256 `b5b39b4f0299b939893b90d5de5b2f8bf3eb6a1057b42d6fd1ea733db7aa5080`

| 항목 | 풋프린트 | 도면 | 차이 | 판정 |
|---|---|---|---|---|
| 핀 1→2 간격 (축 방향) | 6.00 | 5.90 (±0.05) | +0.10 | **수정** |
| 핀 1→3 간격 (축 방향) / 핀 3 측면 거리 | 3.00 / 4.70 | 3.00 / 4.70 | 0 | 일치 |
| 슬롯 | 1×3.0 | **1.0×3.5** | −0.5 | **수정** (패드도 함께 키움) |
| 핀 1 탭 폭 | — | 2.50±0.10 (판독) | 슬롯 3.0이면 한쪽 여유 0.2 | 참고 |
| 몸체 | 14.5 × 9.0, 앞면 −13.7 | **14.0 × 9.00±0.15, 앞면 −13.6, 뒤끝 +0.4** | 길이 +0.5 | **수정** (Fab·실크·코트야드) |
| 핀 기능 | 1 중심 / 2 슬리브 / 3 스위치 | 1 중심 핀 / 2 슬리브 스프링 / 3 스위치(평상시 닫힘) (판독) | — | 일치 · 실물 통전 확인 권고 |

### 전면 X1 24MHz — `Oscillator:Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm` vs YXC OT7EL89CJI-111YLC-24M

- **도면:** https://datasheet.lcsc.com/datasheet/pdf/b336a5b52993e15e0134a8f3d7decec7.pdf?productCode=C5280583
  - YSO110TR 시리즈 공통이고 리비전 표기는 없다(PDF 수정일 2025-12-30).
  - sha256 `d155dd2bc59fe81f90c6c434328061beb8159ce3c6d0538de4ce96c34d44b8e5`
- **비교한 풋프린트:** sha256 `d589f1e140b64d1a94aa191bfee8367ff0c621e22fbb7f8d4fead215fc3e6e14`

| 항목 | 풋프린트 | 도면 권장 랜드 | 차이 | 판정 |
|---|---|---|---|---|
| 패드 크기 | 0.9×0.8 | 0.9×0.8 | 0 | 일치 |
| 패드 중심 | (±0.75, ±0.60) | (±0.70, ±0.55) | +0.05 | 경미 (허용, 단자를 덮음) |
| 핀 배치 (위에서 봄) | 1 좌하 · 2 우하 · 3 우상 · 4 좌상 | 같음 | — | 일치 |
| 핀 기능 | 1 CAM_EN · 2 GND · 3 MCLK · 4 1V8 | 1 Tri-state · 2 GND · 3 OUT · 4 VDD | — | 일치 |
| 외형 | 2.0×1.6 | 2.0±0.1 × 1.6±0.1 × 0.9 max | 0 | 일치 |

→ **그대로 사용한다.** 도면값과 똑같이 맞추고 싶으면 패드 중심을 (±0.70, ±0.55)로 옮긴다(선택).

### 전면 Q4 ALS-PT19 (DNP) — `LED_SMD:LED_0805_2012Metric` (자리값) vs Everlight ALS-PT19-315C/L177/TR8

- **도면:** https://en.everlight.com/wp-content/plugins/ItemRelationship/product_files/pdf/ALS-PT19-315C-L177-TR8_V8.pdf
  - DLS-0000039 Rev.8
  - sha256 `448c33a1c3ca58d344ad5636a1d1b8654ef80bec69a215a7c7f4bb5e77389bed`
- **비교한 풋프린트:** sha256 `ce3a8266ee445b343374e2391b3b931a2bbc27f83d4f06af397cbea91df53178`

| 항목 | 풋프린트 | 도면 | 판정 |
|---|---|---|---|
| 패드 | 0.975×1.4, 중심 간격 1.875 | **0.8×0.8, 중심 간격 1.5** | 수정 |
| 외형 | 2.0×1.2 | 1.7±0.2 × 0.8±0.2 × 0.6 | 수정 |
| 극성 | 패드 1 = C (콜렉터) | ① Collector, ② Emitter | 일치 |

→ **새 풋프린트가 필요하다** (KiCad 기본 라이브러리에 없음). DNP라 1차 제작에는 영향이 없다.

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| K1 | AC 코드 | GlobTek 2313K3432M5701(R) | KC 마크가 도면으로 확인됐고 Digi-Key 재고가 있다 | 국내 MachLink ML-PWG050 (KC 번호 확인 후) |
| K2 | ICR 짝 헤더 | **실물 확인 전까지 미확정으로 두고**, 근거가 더 맞는 PicoBlade 53261-0271을 1안으로 적는다 | 도면과 사진 형상이 MX1.25에 가깝다. 하지만 상세 도면은 열람할 수 없다 | GH SM02B-GHS-TB (Digi-Key 재고 충분) |
| K3 | 68µH 인덕터 | Bourns 원품 (Digi-Key) | 같은 6045 풋프린트에서 Isat ≥1.5A이고 재고가 있는 대체품이 드물다 | Chilisin LVS606045-680M-N |
| K4 | 0603 1µF | 조립처가 JLC면 C15849, LCSC 조달이면 Yageo C559769 | 같은 사양에 재고가 충분하다 | FH C90540 |
| K5 | VSMA1085400 | 위탁 (Digi-Key) | LCSC 재고는 3개뿐이다 | Mouser |

## 다른 레인에 넘길 것 (참고 — 수정은 소유자가 한다)

- **schematic/라이브러리:**
  - 캐리어 J2: DC-005 전용 풋프린트를 만든다(위 수치).
  - 전면 Q4: ALS-PT19 풋프린트를 만든다.
  - 전면 J2: ICR 헤더 계열 판정에 따라 풋프린트를 바꿀 수 있다.
- **조립:** VSMA1085400과 SRN6045TA-680M은 Digi-Key에서 확보해 위탁(또는 조립처가 Digi-Key로 조달)한다.

## 확인 못 한 것

- **KC 인증번호:**
  - GlobTek은 도면의 KC 마크만 확인했고 번호는 없다.
  - MachLink는 페이지에 KC 번호가 없다.
- **ICR 헤더:** CLA216 리드 하우징 실물 치수, DocSend 상세 도면
- **Mouser 수치:** 직접 조회하면 차단돼 Vishay 조회의 2차 수치만 있다.
- **차단된 판매처:** TME·RS·Farnell·엘레파츠는 봇 차단으로 열지 못했다.
- **DC-005 핀 기능:** 판독값이다(실물 통전 확인 필요).
- **원 데이터:** 근거 원본(PDF·JSON)은 세션 임시 폴더에만 있다(제조사 저작물이라 저장소에 보관하지 않음).
