# R-004 견적용 BOM — 짝 BTB·GC2053 결론과 근거

- 배정: orch t18r R-004. 보충 3건:
  - 모듈 5개 확보 근거
  - C-001 3층 구조 반영
  - V-001 ① Digi-Key Marketplace 분리
- 조사자: research t18s · 확인일 **모두 2026-11-26** · 공개 웹과 공개 파일만 읽음 (구매·장바구니·견적·문의·로그인 없음)
- 읽기 전용 입력:
  - D-001/D-002/D-003 (lead 레인 41491d6)
  - R-001~R-003
  - C-001 `hardware/schematic/hw-fw-contract.md` (ac12920)
  - V-001 `validation/review-V001-R002-R003.md` (2a7bf47)
- 산출: `docs/research/bom-quote-draft.csv` (bom-template 21열, 부품 24행). 회로를 아직 설계하지 않았으므로 모든 행은 **대표 후보**다.
- 표기: **확인됨** = 1차 페이지·파일에서 직접 확인 · **미확인** = 검색 요약·차단·추정

## 결론

1. **짝 BTB 커넥터:**
   - 원품번은 **SUNGTECH ST-BTB-058060-A (플러그, Seeed SKU 320210641) / -B (소켓, 320210642)**로 확정했다.
   - 원품은 공개 유통(LCSC·JLC·Digi-Key·Mouser)에 없다. Seeed Fusion OPL(조립 전용 부품 목록)에만 있다.
   - 그래서 PCBWay 턴키 견적용 대표 후보로 **치수가 일치하는 HCTL 범용품**을 넣었다.
     - 캐리어: HC-PBB05-2-60-M-H4.0-G1-R-P-04, LCSC C41421115, 재고 3,540
     - 전면 보드: HC-PBB05-2-60-F-H4.0-G1-R-P-04, LCSC C41421025, 재고 867
   - **이종 짝맞춤(HCTL과 SUNGTECH)은 검증하지 않았다.** 실물 결합 확인 전에는 PCB를 발주하지 않는다(분기점 B1).
2. **GC2053:**
   - 칩 단품은 공인 유통에 없다. 47볼 CSP 패키지이고 AliExpress 브로커에만 있다.
   - **기성 센서 모듈(宝信发 BXF4677-GC2053, DF30 24P)은 Seeed S401(100041077)을 사서 확보하는 것을 1안으로 한다.** S401은 Seeed에서 판매 중이고 Switch Science에 재고 5개가 있다.
   - IQ는 reCamera-OS에 기본으로 들어 있다.
   - O-3 차선 순서(GC4653 → CAM-GC2083)를 바꿀 근거는 없다.
3. **모듈 5개 수치 (판정은 orch O-7):**
   - Seeed 공개 JSON의 101991223 재고는 **창고 2(중국 추정) 55 · 창고 11(독일 추정) 7 · 창고 5(미국) 0**이다.
   - Digi-Key 재고 3개는 **Marketplace(제3자)**이므로 공식 재고 합에서 뺐다.
   - 같은 PCB를 쓰는 변형도 재고가 있다(3절).

## 1. 짝 BTB 커넥터 (최우선)

### 1.1 J1/J2 역할 (확인됨)

| 코어 커넥터 | 형식·면 | 역할 | 주요 신호 | 우리 보드 짝 | 근거 |
|---|---|---|---|---|---|
| J1 ST-BTB-058060-A | 플러그 · **윗면**(SoC 면) | 센서용 | CAM_RX0 4레인+CLK, CAM_I2C2, CAM_EN, IR_PWM, WH_PWM, LIGHT_SENSE, GPIO15/IR_CUT, AUD, VIN×4, +1V8×2, +3V3×2 | **전면 보드 = -B 소켓** (S401과 같다) | 코어 SCH 07 시트 · `BTB_Connector.png` · 코어 STEP (z=+1.65, 위를 향함) · C-001 |
| J2 ST-BTB-058060-B | 소켓 · **아랫면** | 베이스용 | EPHY TX/RX±, USB, USB_DET, VIN×4, +3V3, nRESET, UPGRAD_KEY, DEBUG_UART0, SDIO0, SD0_PWR_EN, MIPI_TX 겸용 GPIO/I2C/PWM, (2002 전용) SD1·BT_UART1 | **캐리어 = -A 플러그** (B301과 같다) | 같음 (STEP z=−0.05, 아래를 향함) |

- 짝을 이룰 때 홀수·짝수 핀 번호가 뒤바뀐다(코어 J2 1번 = 캐리어 2번). C-001 4·5절 핀맵과 일치한다.
- 배치는 B301 KiCad에서 읽었다(보드 중심 원점).
  - 보드 30×30mm, 고정 구멍 Ø2.1 4개가 (±13, ±13)에 있다.
  - 캐리어 짝 커넥터 중심은 (+11.8, 0)이고 −90° 회전, 1번 패드는 (+13.8, −7.25)다.
  - 위치 보스 Ø0.6 NPTH는 (+10.55, ±8.2)에 있다.
  - 전면 쪽 J1은 (0, −11.8)에 가로로 놓인다.

### 1.2 원품 식별

| 항목 | 값 | 근거 | 확인 |
|---|---|---|---|
| 원품번 | SUNGTECH ST-BTB-058060-A (Male) / -B (Female) | B301·S401 kicad_pcb의 Manufacturer·MPN·SKU 필드 | 확인됨 |
| 설명 | 「SMD BTB Male CONN;2*30P-0.5mm-17.7*4.4*4mm」 | Seeed Fusion OPL (`POST https://napi.seeedstudio.com/opl/list`, 조회 전용) | 확인됨 |
| OPL 단가 | 두 SKU 모두 1개 USD 0.5851 | 같음 | 확인됨 |
| 3D 모델 이름 | `SHANGQI_0_5BTB_60P_4_0H_PLUG` / `_SOCKET` | 코어 STEP | 확인됨 |
| 짝 높이 | **8.0mm 추정**: 소켓 4.0, 플러그 몸체 4.0, 혀 끝 5.9 (= 4.0 + 삽입 1.9) | STEP 점군 측정 + 범용 시리즈 높이표 | 추정 |
| SUNGTECH 실체·원 데이터시트 | 찾지 못함. OPL 데이터시트 URL은 S3 AccessDenied | — | 미확인 |
| 공개 유통 | LCSC·JLC·Digi-Key·Mouser 모두 없음 · Seeed Bazaar 부품 검색 「No results」 | — | 확인됨 (없음) |

### 1.3 치수 일치 대체품 (ST 기준: 몸체 17.7×4.4, 보스 16.4·중심선에서 1.25 치우침, 패드 열 간격 4.0, 패드 1.8×0.25, 피치 0.5, 높이 4.0H)

| 품번 | 제조사 | 형식 | 몸체 | 보스 | 열 간격 | 높이 | LCSC | 재고 | 1/10개 USD | 판정 |
|---|---|---|---|---|---|---|---|---|---|---|
| **HC-PBB05-2-60-M-H4.0-G1-R-P-04** | HCTL (深圳华灿天禄) | 플러그 | 17.70×4.40 | 16.40 | 4.0 | 4.0 + 혀 1.9 | C41421115 | 3,540 | 1.133 / 0.938 | 도면 치수 일치 (이종 짝맞춤 미검증) |
| **HC-PBB05-2-60-F-H4.0-G1-R-P-04** | HCTL | 소켓 | 17.70×4.40 | 16.40 (Ø0.55) | 4.0 | 4.0 | C41421025 | 867 | 1.078 / 0.868 | 도면 치수 일치 (이종 짝맞춤 미검증) |
| BTB0.580-60PLBSC-G71 / -M71 | XUNPU | 플러그 / 소켓 | 17.70×4.40 | 16.40 (Ø0.60) | 4.0 | 4.0 / 4.0 | 찾지 못함 | — | — | 도면 일치, 판매 미확인 |
| BTB0.585-60PLBSC-G71 / -M71 | XUNPU | 〃 | 〃 | 〃 | 〃 | 4.0 / **4.5** | C42420591 / C42420593 | 100 / 87 | 1.32 / 1.29 | 소켓 높이 불일치 |
| Hirose DF12 60P · Panasonic P5KS · Molex 52991 · HCTL HC-PBB12NB(4.0) | — | — | 17.1~18.8 | 16.6 등 | — | — | — | — | — | 불일치 |

- 데이터시트(LCSC 사본):
  - 플러그: https://datasheet.lcsc.com/datasheet/pdf/ee313a7bf73f17b02eb2735a2b008b8f.pdf?productCode=C41421115
  - 소켓: https://datasheet.lcsc.com/datasheet/pdf/85738d87feeec2151dd73ca6cfcedf74.pdf?productCode=C41421025
- HCTL·XUNPU·Huamingtong 세 회사 도면이 같은 높이표(짝 8.00 = 母座 4.00 + 公座 4.00, 삽입 1.90)를 쓴다. 즉 업계 공용 치수 계열이다.
- 추천 패드 폭은 범용 1.80×0.30, ST 0.25로 다르다.
- **도면만으로 판단할 수 없는 것:**
  - 접점 형상과 유지력
  - 1번 핀 방향
  - 보스 치우침 방향과 키 위치의 관계
  - 정격 전류 (C-001의 VIN 4핀 1.25A 가정 검증에 필요)

### 1.4 분기점

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | 짝 BTB 조달 | **HCTL 범용품 (LCSC 턴키)** · 풋프린트는 ST/범용 공통 치수로 그린다 | PCBWay 등 턴키 견적(사용자 의도)에 맞는다. 치수가 같아 원품으로 바꿔도 BOM 행만 바꾸면 된다 | ① Seeed Fusion PCBA에서 원품 OPL 320210641/642 사용(조립처가 Seeed Fusion으로 바뀜) ② Seeed 보드(B301 SKU 100074316 = -A 실장 · S401 100041077 = -B 실장)를 개발용으로 쓰거나 커넥터 재사용 |
| B1-조건 | 이종 짝맞춤 위험 | 실물 결합(유지력·1번 핀·키) 확인 전 PCB 발주 금지 | 미검증 | 확인 실패 시 B1 차선 ① |

## 2. GC2053 센서

### 2.1 칩 단품

| 항목 | 값 | 근거 | 확인 |
|---|---|---|---|
| 주문 품번 | 「GC2053 (Colored, 47PIN-CSP)」, 시장 품번 GC2053-C47Y0 | GalaxyCore 문서 (Seeed 게시) | 확인됨 |
| 패키지 | 유리 덮개 47볼 CSP 6.135×4.102×0.76mm, 볼 피치 0.69×0.65, 볼 Ø0.30 | 「GC2053 CSP 모듈 설계 지침」 Rev1.1 (2018-09-17) | 확인됨 |
| 실장 난이도 | BGA형 리플로, X-ray, 유리면 오염 관리, 홀더 정렬이 필요 | 위 패키지에서 추론 | 추론 |
| 공인 유통 | LCSC/szlcsc는 차단·색인 없음, Digi-Key 칩 없음, Mouser 시간 초과 | — | 미확인 (없어 보임) |
| 브로커 | AliExpress 1개 ₩2,700~7,120, 5개 ₩16,600~20,500, 10개 ₩31,800 (검색 결과 표시가, 재고·판매자·정품 여부 미확인) · 예: https://www.aliexpress.com/item/1005013671106494.html | — | 표시가만 확인 |

### 2.2 기성 센서 보드·모듈

| 제품 | SKU·판매처 품번 | 가격 | 재고 | 확인 |
|---|---|---|---|---|
| reCamera 2002 Sensor Board GC2053 (S401) | Seeed 100041077 (https://www.seeedstudio.com/reCamera-2002-Sensor-Board-GC2053-p-6556.html) | USD 27.51 (정가 29.90) · US 창고 31.27 | InStock (수량 미표시) | 확인됨 |
| 〃 | Digi-Key 1597-100041077-ND | USD 24.88 | **0**, 3개 입고 예정 2027-01-18 | 확인됨 |
| 〃 | Switch Science 10795 | JPY 4,781 | **5** | 확인됨 |
| 〃 | Mouser 713-100041077 | 검색 요약 USD 24.86~31.11 | 미확인 | 미확인 |

- **S401 구성:**
  - S401 PCB에는 센서 칩이 없다. 센서와 렌즈는 **宝信发 BXF4677-GC2053 「GC2053 Core Camera」 모듈**에 있고, 이 모듈이 S401 J2(Hirose **DF30FC-24DS-0.4V**, 24P)에 꽂힌다.
  - 모듈 사양(lens_document.pdf, 2025-07-19): 21×22×16.5mm, EFL 2.9mm, 화각 93°, 조리개 2.3. 출처 https://files.seeedstudio.com/wiki/reCamera/reCamera_hq_poe/lens_document.pdf
  - 포장 내용 문구는 「센서 보드 1, 플라스틱 커버 1, M2×10 나사 4」다. 모듈이 포함된다는 명시 문구는 없지만 문서 구성으로 보아 포함으로 **추정**한다. 모듈 단품 SKU는 없다.
- **S401 J2 핀(KiCad 넷):**
  - 1 SDA · 3 SCL · 4 24MHz
  - 5/7 RX0_0N/P · 9/11 CLKN/P · 13/15 RX0_1N/P
  - 12·16 AVDD(3V3 스위칭) · 14 IOVDD(3V3 스위칭)
  - 24 CAM_EN 분압(10k/10k)
  - 나머지 GND
  - 모듈은 3.3V를 받는다. 모듈 안에 레귤레이터가 있다고 **추정**한다.
- **S401에는 ICR 구동이 없다.** GPIO15/IR_CUT·IR_PWM은 LED를 켤 뿐이다.
- **광학과 충돌:** 모듈에 자체 렌즈와 홀더가 있다. 그래서 R-002/R-006 광학(CLA216-ICR + M12 렌즈)과 함께 쓸 수 있는지는 **미확인**이다. 모듈 홀더가 M12이고 그것을 CLA216으로 바꿀 수 있는지 실물로 확인해야 한다.

### 2.3 IQ·드라이버 근거 (reCamera-OS, 확인됨)

| 항목 | 값 |
|---|---|
| IQ 파일 | `external/isp_tuning/cv181x/src/gcore_gc2053/gcore_gc2053_sdr.bin` (227,116 B, 커밋 f24df67d 2025-09-04) · `gcore_gc2053_sdr_ir.bin` (347,073 B, 4cdfe5be 2025-08-05) · 같은 폴더 `.json` 2개 |
| 버전 | 브랜치 `sg200x-reCamera` HEAD 0529ca0a (2026-11-04). 태그 0.2.6 (fa2a903f)에도 같은 blob이 있다 |
| 드라이버 | 서브모듈 sophgo/SensorSupportList 86b0708e `sensor/cv181x/gcore_gc2053/` |
| 기본 설정 | `sg2002_recamera_emmc_defconfig`가 `CONFIG_SENSOR_GCORE_GC2053=y`를 켠다. 앱(sscma-example-sg200x `video_paramparse.c`)이 {ov5647, sc530ai, gc2053}을 자동 인식하고 `/mnt/cfg/param/gcore_gc2053_sdr.bin`을 읽는다 |
| 출처 | https://github.com/Seeed-Studio/reCamera-OS |

### 2.4 차선 판정 자료 (O-3 순서)

| 순위 | 후보 | 칩·모듈 조달 | IQ·SDK | 판정 근거 |
|---|---|---|---|---|
| 1 | **GC2053** | 칩은 브로커만. **모듈은 S401로 확보 가능** | 기본 포함 | 유지 |
| 2 | GC4653 | 칩 GC4653-C41Y0 CSP은 브로커만(AliExpress ₩2,620~5,820) · 모듈 Sipeed Just-GC4653-Camera(AliExpress, 커넥터 호환 미확인) | 상류 isp_tuning f7b23013에 IQ 있음. reCamera defconfig·앱 자동 인식 목록에는 없음 → 수정 필요 | 2순위 유지 |
| 3 | CAM-GC2083 | 모듈 Spotpear USD 8.59 In Stock · Arace MA002는 429로 미확인 | 공개 IQ 없음(상류·milkv v2 모두) · 16P FPC라 BTB 어댑터 필요 | 3순위 유지 |

결론: 칩을 구하지 못해도 GC2053은 S401 모듈로 갈 수 있다. 따라서 O-3 차선 순서를 바꿀 근거는 없다.

### 2.5 분기점

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| S1 | GC2053 확보 형태 | **S401(100041077)을 사서 BXF4677 모듈을 쓴다** + 전면 보드에 DF30FC-24DS-0.4V(81) (LCSC C5137456) | 칩 직접 실장(CSP 47볼)보다 위험이 작다. IQ와 모듈 사양이 Seeed 공식 조합과 같다 | GC2053 칩(브로커) 직접 실장 → O-3 차선 |
| S1-위험 | DF30 수명 | Digi-Key 「Last Time Buy」(최종 주문 2027-10-31). LCSC 재고 4,930 | PoC 5장에는 충분 | 후속 품번은 미확인 |

## 3. 모듈 5개 확보 근거 (O-7 판정용 수치, 판정은 orch)

### 3.1 판매처별 재고

**Seeed Bazaar:** 상품 페이지 HTML에 들어 있는 공개 JSON `warehouseStockData.available_qty` 값을 그대로 옮겼다. 화면에는 「Sign in to view available stock」이 표시된다.
- 공통 필드: schema.org `InStock`, `stock_status IN_STOCK`, `product_stage "MP"`, `sales_moq 1`, `price_tiers []`(수량 할인 없음)
- 창고 번호 대응: 5=US는 가격이 하나만 달라 확실하다. 2=CN, 11=DE는 Offer 순서로 짝지은 **추정**이다.

| SKU | 페이지 | 창고 2 (CN 추정) | 창고 5 (US) | 창고 11 (DE 추정) | 가격 USD (CN·DE / US) |
|---|---|---|---|---|---|
| **101991223** (2002 8GB) | https://www.seeedstudio.com/reCamera-Core-2002-8GB-p-6433.html | **55** | **0** | **7** | 60.63 / 63.47 |
| 101991224 (2002w 8GB) | …/reCamera-Core-2002w-8GB-p-6435.html | 2 | 23 | 1 | 64.31 / 29.2 |
| 102991898 (2002 64GB) | …/reCamera-Core-2002-64GB-p-6434.html | 33 | 22 | 0 | 69.83 / 31.6 |
| 102991899 (2002w 64GB) | …/reCamera-Core-2002w-64GB-p-6436.html | 0 | 20 | 0 | 73.51 / 33.2 |

- 이상 값(의미 미확인): 창고 2의 `batch` 「CUSTOM250101」 `AvaTransitQTY 1000000`, `xn_available_qty 1000000`
- UI 공통 문자열: 「Production begins after payment. Estimated lead time 4-6 weeks.」 — 상품별 데이터인지는 확인하지 못했다.

**Digi-Key — Marketplace(제3자). 공식 재고 합에서 제외(V-001 ①):**
- 4종 모두 「Active」, 제조사 납기 4주다.
- 재고: 101991223 **3** · 101991224 3 · 102991898 2 · 102991899 4
- Detailed Description은 「Recamera Gimbal For Cameras」이고, 연결된 데이터시트는 SenseCAP 문서다. 등록 신뢰도가 낮다.

**그 밖의 판매처:**

| 판매처 | 결과 |
|---|---|
| Mouser | 4종 모두 접근 거부. 검색 요약에는 「Non-Stocked, Lead-Time 4 Weeks」 (미확인) |
| Pakronics (AU) | 429. 검색 요약에 SS101991223 A$59.71 「238」 (미확인) |
| openelab | 429. 수량 미확인 |
| The Pi Hut | 코어 없음 |
| 엘레파츠 | 결과 없음 |
| 디바이스마트 | 결과 없음(JS 구조라 확정 아님) |
| ICbanQ | 404 |
| Seeed 공식 대리점 목록 | 로고만 있어 목록을 확보하지 못함 |

**EOL:** Seeed `product_stage MP` · Digi-Key Active · OSHW README 「Currently sold product forms」 · 위키에 EOL 문구 없음 → **EOL 표시 없음**.

### 3.2 변형 동일성 근거

| 항목 | 101991223 (2002) | 다른 변형 | 근거 | 확인 |
|---|---|---|---|---|
| PCB | C1-2002 | 2002w도 같은 PCB | OSHW `core/c1-2002/README.md` 「Both variants originate from the same PCB design」 | 확인됨 |
| B2B 커넥터·핀 정의 | J1 -A / J2 -B | 같음 | 공개 회로도(2002w 8GB v1.2만 있음) 07 시트 | 확인됨 |
| SD1(J2 12·16·18·20·22·24) · BT_UART1(54~60) | README 「exposes additional SDIO/UART signals to the base」 — 실장 여부는 2002 회로도가 없어 **미확인** | 2002w: R48~R53, R67~R70이 미실장(X) → 캐리어로 나오지 않는다. Wi-Fi(AW-AM497)가 SD1·UART1을 쓴다 | 회로도 이미지 판독 | 2002w는 판독, 2002는 미확인 |
| eMMC | 8GB | 102991898/899: 64GB | 위키·README | 확인됨 |
| OS 이미지 | 공통 | 공통 — 릴리스마다 `sg2002_reCamera_<ver>_emmc*.zip` 하나, 설정 `sg2002_recamera_emmc` 하나 · 그 설정은 SD1(wifisd)·UART1을 Wi-Fi/BT용으로 켠다(dts `status="okay"`) | https://github.com/Seeed-Studio/reCamera-OS/releases | 확인됨 |

**캐리어 영향:** C-001은 SD0을 쓰고 SD1은 쓰지 않는다(분기 C5). 따라서 변형을 섞어 써도 캐리어 핀맵에는 영향이 없다고 **판단**한다. 다만 기본 OS 이미지가 SD1을 Wi-Fi용으로 잡는 점은 펌웨어에서 확인해야 한다.

## 4. BOM 작성 기준과 분기점

- **열:** bom-template.csv 21열을 그대로 썼다.
- **Quantity:** 「보드당 n (5보드 / 10보드)」 형식 (D-003 #12 기본 5)
- **Reference 괄호:** 실장 위치 [모듈] / [캐리어] / [전면] / [보드간] / [외부] (C-001 3층 구조)
- **AssemblyNotes 조달 구분:**
  - 턴키: LCSC 재고 부품
  - 위탁: 모듈·S401 모듈·렌즈·ICR (D-003 #2)
  - 별도: FFC·어댑터
- **반영한 보충:**
  - C-001: 짝 BTB 2종, 24MHz 발진기, DF30 24P와 GC2053 모듈, 1.0mm 10P FPC 커넥터 2개와 FFC, 5V 벅 3A급, 12V 2A 이상 어댑터, 12V_IR 부하 스위치, 전면 3.3V LDO
  - ICR·IR LED·조도센서는 전면 보드 실장으로 표시했다.
- **렌즈:** 원지시의 CIL327은 V-001 ④(F-θ 렌즈라 GC2053 HFOV 약 121°)로 무효다. R-006 1안 예정인 **CIL093-F2.4-M12ANIR**를 넣었다. R-006에서 확정한다.
- **IR LED:** V-001 ⑥에 따라 1.0A 구동, 직렬 2개 이하다. 보드당 2개는 **잠정**이고 R-006에서 확정한다.

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| P1 | 12V_IR 부하 스위치 | TI TPS26600PWPR eFuse (LCSC C544399) — 1.8V GPIO로 UVLO 핀을 구동 | TPS27S100·TPS1H000은 EN 문턱이 2V 이상이라 1.8V에서 못 켠다. 4.2~60V에 전류 제한이 있다 | TPS259470ARPWR (C3662799, 절대최대 28V) · AO4407A + NPN (전류 제한 없음) |
| P2 | 5V 벅 | TI TPS54302DDCR (C311983, 4.5~28V 3A) | 3A급(C-001), SMBJ15A 클램프 24.4V보다 내압이 높다 | Silergy SY8205FCC (C111875). TPS563201은 17V로 탈락, MP2315는 NRND |
| P3 | FPC 커넥터 | TE 1-84952-0 (C590890) | 데이터시트로 접점 1A가 확인된 것은 이것뿐이다 (BOOMELE·JST는 0.5A) | 1-84953-0 상접 (C3168738) |
| P4 | FFC | 10P 1.0mm 10cm 동방향 (C35925, 재고 480) | 방향·길이는 기구 배치 전이라 대표값 | 역방향 5cm C68391 / 10cm C111368 (재고 70) |
| P5 | 24MHz 발진기 | YXC OT7EL89CJI-111YLC-24M (C5280583, 2016, OE 핀) | S401 X1(9C24000004, 「Faith Long」 1.8V 15ppm, 정체 미확인)과 핀 배치가 같다 | OT201624MJBA4SL (C725986) |
| P6 | 이더넷 자기부품 | HanRun HR911105A (C12074) | C-001 C9 (통합 마그넷) | Pulse H1102NLT + 비자기 RJ45 |
| P6-주의 | SG2002 EPHY 센터탭 | TCT·RCT 커패시터를 **미실장(DNP) 옵션**으로 둔다 | Sophgo 레퍼런스(SG2002-QFN88-38-4L.pdf 08_RJ45)는 C77·C78이 NC. Milk-V 사용자 보고: RX 센터탭 100nF를 떼자 동작 (https://community.milkv.io/t/rj45-ethernet-not-working/1399) | — |
| P7 | 어댑터 | Mean Well GST25A12-P1J (Digi-Key 1866-2090-ND, 재고 648, KC K60950-1 표기) | 12V 2.08A, 센터+, 인증 표기 | GST25B12-P1J (DK 재고 0) |

## 확인 못 한 것

- **커넥터:**
  - SUNGTECH 원 데이터시트와 정격
  - HCTL↔SUNGTECH 실제 결합
  - 짝 높이 8.0mm 실측
- **센서 모듈:**
  - BXF4677 모듈의 DF30 플러그 품번과 24번 핀 기능
  - 모듈 홀더를 CLA216으로 바꿀 수 있는지
- **부품:**
  - 9C24000004 정체
  - DF30 후속 품번
- **모듈 재고:**
  - Seeed 창고 2·11 대응
  - 101991223 실물의 SD1·UART1 0Ω 실장
  - Mouser·Pakronics·openelab 수량
- **조립:** 전반적인 JLC Basic/Extended 구분과 PCBWay 조달 가능 여부. 견적은 하지 않았다.
- **원본 보관:** 내려받은 근거 자료는 세션 임시 폴더에만 있다. 보관은 R-005에서 한다.
