# R-003 SG2002 코어 모듈 구매처·캐리어 설계 자료 조사

- 배정: orch t18r R-003 (lead t18q, 사용자 직접 요청, 우선순위 최상) · 보충: 제조사·판매처 품번 기록 · 운영 변경: D-003 기본값으로 판정(질문 대신)
- 입력: lead 레인 t-20261126-144135-5470
  - D-002-module-carrier.md (6e2c286)
  - D-003-working-defaults.md (8ac5ce5)
  - D-001
  - product-brief
  - R-001 soc-sg2002.md (레인 t-20261126-144331-462e, bbf3930)
- 조사자: research t18s · 확인일 **모두 2026-11-26** · 공개 웹 읽기만 (구매·장바구니·견적·문의·로그인 없음)
- 표기: **확인됨** = 판매·제조사 페이지나 파일에서 직접 확인 · **미확인** = 검색 요약·접속 차단·추정 · 가격만 보고 호환을 확정하지 않는다.

## 결론

**권고 모듈 1종: Seeed Studio reCamera Core 2002 (C1-2002, 8GB eMMC, 무선 없음)**
- 제조사 SKU: **101991223**
- 판매처 품번: Seeed Bazaar 101991223 · Digi-Key 1597-101991223-ND · Mouser 713-101991223 (Mouser는 미확인)

- **D-003 #15 기준을 가장 많이 충족한다.** 세 조건별 충족 상태는 다음과 같다.
  - 구매: 공식 판매처(Seeed)와 공식 유통(Digi-Key, Active)에서 산다.
  - 신호: **MIPI CSI와 이더넷 MDI가 모두 B2B 커넥터로 캐리어에 나온다.**
  - 설계 자료: 짝 커넥터 풋프린트가 들어간 베이스 보드 KiCad PCB가 CC BY-SA 4.0으로 공개되어 있다.
  - 미충족: 코어 보드 자체의 STEP 파일은 없다.
- **D-003 #15의 우선 후보 LicheeRV Nano-E를 1안에서 내린 이유:**
  - MIPI CSI는 보드 위 22P FPC로만 나온다.
  - 이더넷은 보드 위 RJ45로만 나온다. 스탬프홀에는 둘 다 없어 캐리어로 끌어올 수 없다.
  - D-003 #5 센서 GC2083을 Nano SDK가 기본으로 지원하지 않는다(IQ 파일 없음, 커넥터 핀배치 다름).
  - 상세는 아래 판정표에 있다. 이 갈림길은 분기점 M1로 기록했다.
- **차선책:**
  - ① LicheeRV Nano-E와 GC4653(D-003 #5의 차선 센서, SDK 정식 IQ 있음)을 함께 쓴다. 모듈의 RJ45와 22P FPC를 그대로 쓰는 배치다.
  - ② Milk-V Duo 256M과 CAM-GC2083을 쓴다(16P FPC와 IQ 파일이 그대로 맞는다). 이더넷은 5패드로 나온다. 다만 공식 판매처 재고는 Platima(호주) 1곳뿐이고 STEP과 풋프린트가 없다.
- **위험:**
  - **5개 수량(D-003 #12) 재고:** Digi-Key 101991223 재고는 3개다. Seeed는 재고 수량을 표시하지 않는다.
  - **Digi-Key 가격 이상:** Digi-Key 가격(USD 31.25)이 Seeed 정가의 약 절반이고, 상품 설명이 "Recamera Gimbal"로 되어 있다. 등록 오류 가능성이 있다.
  - **GC2083 IQ 파일:** Seeed SDK에 없다. Milk-V SG2002 SDK의 GC2083 IQ를 옮겨 쓸 수 있는지는 미확인이다.

## D-003 #15 판정표

판정 기호: ○ 충족 · △ 부분 충족 · × 미충족

| 후보 (SoC) | ① 공식 판매처 구매 가능 | ② MIPI CSI 노출 | ② 이더넷 노출 | ③ 풋프린트 공개 | ③ STEP 공개 | D-003 #5 GC2083 연결 | 종합 |
|---|---|---|---|---|---|---|---|
| **Seeed reCamera Core 2002 (SG2002)** | ○ Seeed 판매 중 · Digi-Key Active 재고 2~4 | ○ B2B 60P로 CAM_RX0 4레인+CLK, I2C2, CAM_EN | ○ B2B로 내장 EPHY MDI(TXP/N·RXP/N), 트랜스는 베이스 보드 쪽 | ○ 짝 BTB 풋프린트가 베이스 보드 KiCad PCB에 있음 (CC BY-SA 4.0) | △ 케이스 STEP만 있고 코어 보드 STEP은 없음 | △ Seeed IQ는 GC2053·OV5647뿐. GC2083은 드라이버 목록에만 있고 IQ 이식은 미확인 | **권고** |
| Sipeed LicheeRV Nano-E (SG2002) | △ 공식 AliExpress 가격·재고는 로그인에 막혀 미확인 · 재판매처 Spotpear는 In Stock USD 39.9 (대표 페이지는 "Off-production"으로 상충) | △ 보드 위 22P 0.5mm FPC로만 (스탬프홀 없음) | × 스탬프홀 없음, 보드 위 RJ45와 자석만 | ○ KiCad·JLCEDA 풋프린트(캐리어 컷아웃 포함) · 라이선스 명시 없음 | ○ E·W STEP · 라이선스 명시 없음 | × 기본 defconfig에서 꺼져 있고 IQ 없음 · CAM-GC2083 16P와 직결 불가 | 차선 ① (GC4653과 함께) |
| Milk-V Duo 256M (SG2002) | △ 공식 대리점 Platima(AU) 미납땜판만 재고 · Arace·Spotpear 품절 | △ 보드 위 16P FPC로만 | ○ 5패드 J8 (RXN·RXP·GND·TXN·TXP), 위치는 미확인 | × 256M 전용 없음 (원조 Duo .dra만, 동일 여부 미확인) | × 없음 | ○ CAM-GC2083 16P 직결 + IQ `cvi_sdr_bin_GC2083` + sensor_cfg | 차선 ② |
| Milk-V Duo Module 01 (SG2000) | × Arace 전 변형 품절 · Spotpear Out of Stock | ○ 스탬프 72~83 (6쌍) | ○ 스탬프 61~64 MDI | △ Allegro .dra + DXF (KiCad 없음) · 라이선스 명시 없음 | × 없음 | △ Milk-V SDK(sg200x)에 IQ 있으나 SG2000 적용은 미확인 | 재고가 생기면 재검토 |
| Milk-V Duo S (SG2000) | × Arace 전 변형 품절 · Spotpear "Off-production" | △ 보드 위 FPC | △ 보드 위 RJ45 | × 헤더형 | ○ duo_s_pcb_3d.stp | — | 제외 |
| 기타 (Radxa·Banana Pi·100ask·중국 核心板·Sophgo EVB) | 검색 결과 없음 (없다고 단정하지는 않음) | — | — | — | — | — | — |

## 1. 후보별 사양과 실장 방식

### 1.1 Seeed reCamera Core 2002 (C1)

| 항목 | 값 | 근거 | 확인 |
|---|---|---|---|
| 변형·SKU | 101991223 (2002 · 8GB) · 101991224 (2002w · 8GB, AW-AM497 Wi-Fi/BT) · 102991898 (2002 · 64GB) · 102991899 (2002w · 64GB) | Seeed 상품 페이지 | 확인됨 |
| SoC·메모리 | SG2002 (256MB 내장) · eMMC KLM8G1GETF-B041 8GB 또는 64GB | 회로도 v1.2 | 확인됨 |
| 실장 | **B2B 60핀 0.5mm 2개**: J1 ST-BTB-058060-A, J2 ST-BTB-058060-B. 풋프린트 이름 "BTB60-Male-Female-0.5-17.7x4.4mm" · 커넥터 제조사 원품번 미확인 | 회로도 · 저장소 BTB_Connector.png | 확인됨 (원품번 미확인) |
| 캐리어로 나오는 신호 | 센서 쪽 BTB: CSI 4레인+CLK, I2C2, CAM_EN · 베이스 쪽 BTB: EPHY MDI, USB2, SDIO0, (2002) SD1/UART1, 디버그 UART, VIN | 회로도 신호 목록 (J1/J2 어느 쪽이 센서용이고 어느 쪽이 베이스용인지는 추정) | 부분 확인 |
| 전원 | BTB VIN, 베이스 보드가 5V 공급 (시리즈 공식 5V 1A), 코어 안 SY80004 강압 3개 | 회로도 | 확인됨 |
| 크기 | 완성 카메라 40×40×36.5mm · **코어 보드 단독 외형은 공식 표기 없음** | Seeed | 미확인 |
| 조립 (D-003 #2) | 모듈은 짝 BTB에 꽂으므로 납땜이 없다 → 캐리어는 턴키, 모듈은 조립 후 꽂는다. 짝 커넥터의 턴키 조달성은 원품번 확인 후 판단 | 추론 | 미확인 |

### 1.2 Sipeed LicheeRV Nano

| 변형 | 이더넷 | Wi-Fi6/BT | 비고 |
|---|---|---|---|
| LicheeRV-Nano-B | 없음 | 없음 | 마이크와 1W 앰프는 공통 |
| LicheeRV-Nano-E | 100M RJ45 온보드 (자석 PSTFAQ3416) | 없음 | |
| LicheeRV-Nano-W | 없음 | AIC8800D (SDIO1 공유) | |
| LicheeRV-Nano-WE | 별도 소형 보드 (상면 패드에 플랫케이블 납땜) | 있음 | 패드 신호 정의 미확인 |

- **Sipeed 공식 SKU:** 공개된 것이 없다. 변형명만 있다.
- **하드웨어 리비전:** 70405(시험판), 70415·70418(양산판). 리비전 사이에 카메라 FPC 레인 배열이 다르다.
- **실장 정보:**
  - 스탬프홀: 28개(2×14), 피치 2.54mm, 열 간격 800mil
  - 크기와 두께: 22.86×35.56mm, 부품 포함 두께 3.9mm
  - **하면에 SoC·TF·FPC·앰프가 있어 캐리어 컷아웃이 필요하다.** 공식 KiCad 풋프린트의 Edge.Cuts에 35.56×18.288mm 컷아웃이 들어 있다.
  - 풋프린트 9·10·11번 패드가 격자에서 −0.069mm 어긋나 있어 보정 검토가 필요하다.
  - Sipeed 문구: 「直插/半孔设计，方便量产贴片」 / 「Its through-hole/half-hole design facilitates easy mass production and soldering」
  - 리플로 조건은 공개되지 않았다. 공개 사례(Lichee-Jack, GPL-3.0)는 모듈을 PCBA에 넣지 않고 저온 솔더(Sn42/Bi58)로 손 납땜했다.
- **스탬프홀로 나오는 신호:** UART0/1/2, GPIO, SPI, SDIO1(W/WE에서는 Wi-Fi와 공유), ADC(24번), SPK±, 전원(13 VSYS, 14 VBUS, 15 3V3 출력, 3·26 GND; 「Voltage: 3.6~5.5V」, 최대 1A)
- **스탬프홀로 나오지 않는 신호:** MIPI CSI(22P FPC JUSHUO AFC11-S22ICC-00, LCSC C11074), 이더넷 MDI, USB D±, 리셋·부트
- **22P 핀배치(70418):**
  - GND: 1·4·7·10·13·16·19
  - 데이터 레인: 2-3 RX4 · 5-6 RX3 · 8-9 RX2 · 11-12 RX1 · 14-15 RX0
  - 제어: 17 CAM_IO0 · 18 CAM_IO1 · 20 SCL · 21 SDA · 22 VDD3V3
  - GC4653 매핑: RX4=CLK, RX3=D0, RX2=D1
- 근거: https://wiki.sipeed.com/hardware/en/lichee/RV_Nano/1_intro.html · 70418 회로도 · KiCad 풋프린트

### 1.3 Milk-V Duo 256M / Duo Module 01 / Duo S

| 항목 | Duo 256M (SG2002) | Duo Module 01 (SG2000) | Duo S (SG2000) |
|---|---|---|---|
| 실장 | 40핀 2.54mm 가장자리 핀 (SMT 공식 문구는 원조 Duo 데이터시트에만 있음) | **스탬프홀 88핀** (4×22, 1.1mm 피치, 패드 0.55×1.0, DXF 측정) · 「Supports SMD to Baseboard.」 | 26핀 헤더 2개 |
| 크기 | 21×51mm | 27.3×27.3mm (DXF) · 브리프는 25×25로 상충 | 43×43mm |
| CSI | 보드 위 16P 0.5mm FPC J1 | 스탬프 72~83 (MIPI0 6쌍) + 10~16 제어 | 보드 위 FPC |
| 이더넷 | 5패드 J8 (1 RXN, 2 RXP, 3 GND, 4 TXN, 5 TXP) | 스탬프 61 RXP, 62 RXN, 63 TXP, 64 TXN · LED 49·50 | 보드 위 RJ45 |
| USB | USB-C + 2패드 J10 | 65 DM, 66 DP, 46 VBUS_EN, 48 VBUS_DET | — |
| 전원 | VSYS 39번 → MP1657 (주석 「MAX 18V FOR IC PROTECTION」, 문서는 VSYS 5V) | 3V3 7·8번, VDD_BAT 44번 (범위 미표기) | — |
| 부트 | 35번 ARM/RISC-V 선택 · 30번 RUN | 60번 ARM_RISV_SWITCH · 47번 UPDATE (리셋 핀 없음) | — |
| 공급 보장 | 표시 없음 | 브리프: 「guarantees availability of the Meles until at least September 2028」 (제품명이 Meles로 잘못 적혀 있음) | — |

16P 카메라 핀배치(Duo 256M J1 = Module 01 평가보드 J8):
- GND: 1·4·7·10
- 데이터 레인: 2/3 D0−/+ · 5/6 D1−/+ · 8/9 CK−/+
- 제어: 11 RSTN · 12 CLK · 13/14 SCL/SDA (1.8V)
- 16 3V3

근거: https://milkv.io/docs/duo/getting-started/duo256m · https://milkv.io/docs/duo/getting-started/duo-module-01 · https://milkv.io/docs/duo/camera/gc2083

## 2. 구매처·단가·재고 (2026-11-26, 수량 할인표는 모든 판매처에 없음 → 1개 단가만 기록)

| 후보 | 제조사 품번/SKU | 판매처 | 판매처 품번 | 1개 단가 | 통화 | 재고 | 배송·납기 | 공식/재판매 | EOL 표시 | URL | 확인 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| reCamera Core 2002 8GB | 101991223 | Seeed Bazaar | 101991223 | 60.63 (정가 65.90) | USD | 표시 없음 | 결제 단계에서 계산 | 공식 | 없음 | https://www.seeedstudio.com/reCamera-Core-2002-8GB-p-6433.html | 확인됨 |
| 〃 | 101991223 | Digi-Key | 1597-101991223-ND | 31.25 (등록 오류 의심) | USD | 3 | 제조사 납기 4주 | 공식 유통 | Active | https://www.digikey.com/en/products/detail/seeed-technology-co-ltd/101991223/26834463 | 확인됨 |
| 〃 | 101991223 | Mouser | 713-101991223 | 미확인 | — | 검색 요약상 비재고 | 약 4~6주 (요약) | 공식 유통 | 미확인 | mouser.com | 미확인 (접근 거부) |
| 〃 | 101991223 | Pakronics (AU) | SS101991223 | A$59.71 (요약) | AUD | 238 (요약) | 7~10일 (요약) | 재판매 | — | pakronics.com.au | 미확인 (429) |
| reCamera Core 2002w 8GB | 101991224 | Seeed / Digi-Key | 101991224 / 1597-101991224-ND | 64.31 / 38.75 | USD | 표시 없음 / 3 | — / 4주 | 공식 | Active | https://www.seeedstudio.com/reCamera-Core-2002w-8GB-p-6435.html | 확인됨 |
| reCamera Core 2002 64GB | 102991898 | Seeed / Digi-Key | 102991898 / 1597-102991898-ND | 69.83 / 42.50 | USD | 표시 없음 / 2 | — / 4주 | 공식 | Active | https://www.seeedstudio.com/reCamera-Core-2002-64GB-p-6434.html | 확인됨 |
| reCamera Core 2002w 64GB | 102991899 | Seeed / Digi-Key | 102991899 / 1597-102991899-ND | 73.51 / 52.50 | USD | 표시 없음 / 4 | — / 4주 | 공식 | Active | https://www.seeedstudio.com/reCamera-Core-2002w-64GB-p-6436.html | 확인됨 |
| LicheeRV Nano-B | LicheeRV-Nano-B (공식 SKU 없음) | Spotpear | 0903001 / 옵션 LicheeRV-Nano-Basic | 32.9 | USD | In Stock | 처리 지연 수 시간 문구 | 재판매 | 대표 페이지에 "Off-production" (상충) | https://spotpear.com/shop/Sipeed-LicheeRV-Nano-SG2002-256MB-WiFi6-ETH/LicheeRV-Nano-Basic.html | 확인됨 |
| LicheeRV Nano-E | LicheeRV-Nano-E | Spotpear | 0903001 / LicheeRV-Nano-ETH | 39.9 | USD | In Stock | 〃 | 재판매 | 〃 | …/LicheeRV-Nano-ETH.html | 확인됨 |
| LicheeRV Nano-W | LicheeRV-Nano-W | Spotpear | 0903001 / LicheeRV-Nano-WIFI | 42.9 | USD | In Stock | 〃 | 재판매 | 〃 | …/LicheeRV-Nano-WIFI.html | 확인됨 |
| LicheeRV Nano-WE | LicheeRV-Nano-WE | Spotpear | 0903001 / LicheeRV-Nano-WIFI-ETH | 49.9 | USD | In Stock | 〃 | 재판매 | 〃 | …/LicheeRV-Nano-WIFI-ETH.html | 확인됨 |
| LicheeRV Nano (B/E/W/WE) | 〃 | Sipeed AliExpress | item 1005006519668532 (SKU 옵션명 미확인) | 미확인 (2024 출시 기사 B $8.90 · E $9.90) | USD | 미확인 | — | 공식 | — | https://www.aliexpress.com/item/1005006519668532.html | 미확인 (로그인 리다이렉트) |
| LicheeRV Nano-B | — | electronicscomp (IN) | EC-27345 | Rs.1160 | INR | Out Of Stock | — | 재판매 | — | https://www.electronicscomp.com/sipeed-licheerv-nano-b-sg2002-ai-visual-risc-v-linux-development-board | 확인됨 |
| LicheeRV Nano-WE | — | Robu.in | R123369 | ₹1,932.84 | INR | in stock (요약) | — | 위키에 나온 대리점 | — | — | 미확인 (403) |
| Duo 256M 미납땜 | MV002 계열 (판매처 SKU 체계) | **Platima (AU, 공식)** | MV002-V1000 / variant 47792552673559 | 36.00 | AUD | **재고 있음** | 미확인 | 공식 | — | https://shop.plati.ma/products/milk-v-duo-256m | 확인됨 (Shopify JSON) |
| Duo 256M | MV002-H0 / MV002-H1 | Arace (공식) | variant 42555014545588 / 42525052534964 | 7.99 / 8.99 | USD | 품절 | 결제 후 3~7 영업일 출고 | 공식 | — | https://arace.tech/products/milk-v-duo | 확인됨 (JSON) |
| Duo 256M | — | Spotpear | 0808010 | 17.9 | USD | Out of Stock | — | 공식 대리점 | — | https://spotpear.com/shop/Milk-V-Duo-256MB.html | 확인됨 |
| Duo Module 01 (5변형) | MM003-E0W0 / E0W1 / E8W0 / E8W1 / E16W1 | Arace | 43520663650484 / …683252 / …716020 / …748788 / 67612205613236 | 8.90 / 9.90 / 9.90 / 10.90 / 39.99 | USD | 전부 품절 | — | 공식 | — | https://arace.tech/products/milk-v-duo-module-01 | 확인됨 |
| Duo Module 01 | — | Spotpear | 080801500000 | 10.9 | USD | Out of Stock | — | 재판매 | — | https://spotpear.com/shop/Milk-V-Duo-Module-01-SG2000-512MB-RISC-V-Duo-S-Core-Module.html | 확인됨 |
| Duo S (5변형) | MV003-W0E0 ~ W1E16 | Arace / Platima / Spotpear(0808011) | 위 조사 기록 | 9.99~112 | USD/AUD | 전부 품절 · Spotpear "Off-production" | — | 공식 | — | https://arace.tech/products/milkv-duo-s | 확인됨 |
| CAM-GC2083 (참고) | MA002 | Arace / Platima | variant 42342173212852 / MA002-V1100 (47181442023703) | 3.99 / 8.00 | USD / AUD | 재고 있음 / 재고 있음 | — | 공식 | — | https://arace.tech/products/milk-v-cam-gc2083 | 확인됨 |

- **검색 결과 없음:** Digi-Key(LicheeRV Nano, Milk-V), DFRobot(reCamera), Elecrow, 디바이스마트, 엘레파츠
- **접속 실패:** Mouser, Farnell, Arrow, LCSC, Taobao, Seeed 검색, Pimoroni, The Pi Hut, openelab, Pajenicko, Elektor, Arace HTML(429 — 대신 Shopify JSON으로 확인)

## 3. 캐리어 설계 자료

| 대상 | 파일 | URL | sha256 | 라이선스 |
|---|---|---|---|---|
| reCamera C1 코어 | 회로도 v1.2 (KiCad 8, 2002w 8GB 기준) · BTB_Connector.png · 케이스 STEP(Recamera Core 2002.step, core_cooler.step) | https://github.com/Seeed-Studio/OSHW-reCamera-Series/tree/main/hardware/recamera-2002/core/c1-2002 | 미계산 | 회로도 표제란 **CC BY-SA 4.0** (저장소 LICENSE는 Apache 2.0. 파일별 표기가 우선한다고 판단) |
| reCamera 베이스 B301 (PoE, 짝 BTB, MDI·PoE 회로) | b301.kicad_pcb (하위 시트 2개 누락) | …/hardware/recamera-2002/base/ | b4b974b3ba8f8bc0fdc734af4925cf7ff8678d039a9a0372eb0d25f4211adf1f | 위와 같음 |
| reCamera 센서 보드 | S101 OV5647 (KiCad) · S401 **GC2053** (KiCad, 제조 zip) | …/hardware/recamera-2002/sensors/ | s101.kicad_pcb 7c4be75e948e732a7b41ad1943da2ded2ffb75dcf1e6903a517130ecbde083d7 | 위와 같음 |
| LicheeRV Nano | 사양서 V1.0 en | https://dl.sipeed.com/shareURL/LICHEE/LicheeRV_Nano /01_Specification/ | 4a2840ecb75f4a40f1f454dc3ccfc2b24d25a45e21363993e281613cf4ba375d | 「All rights reserved」 |
| 〃 | 회로도 70405 / 70415 / 70418 | /02_Schematic/ | b09ec99069e7f696498b3501785f5296fd0ecaed6d1895d16de2c2e057c2fd19 / ee8211a4c75c40f2327114a93b6d4aa4a80b8a6cf057b5eda5bb5a64365e4955 / 7fdc7cbcda36a676ef73e3525f61e9ddec7507cca76828490225143696284efe | 명시 없음 |
| 〃 | KiCad 풋프린트·심볼 rar | /05_PCB_Lib/KICAD/ | 13628505c7674e9740e2285e03191554345ee3520e255257a1e2a9c6f36c21b1 | 명시 없음 |
| 〃 | JLCEDA Pro 풋프린트 | /05_PCB_Lib/JLCEDApro/ | 617a6b3a6d05f3260787ac930f1c68519af7059bc30b10cf64fbbb727a171ee1 | 명시 없음 |
| 〃 | 치수도 7z | /04_Mechanical_drawing/ | 637c4d45b18ae4d3668a319a64daf57a3ee9965b9b9b371803bc7ecba2a71c25 | 명시 없음 |
| 〃 | STEP (E) / (W) | /06_3D_file/ | 3c6ce0bc3b7ccfb562dd47410074450826c5777b73d3762ba3ed80fbbde07879 / 608949e11f6cc39f72c72f9a8880c02e15f1f8af5bf368dbe347d7e8592b692b | 명시 없음 |
| 〃 | iBOM 70405 | /03_Designator_drawing/ | 834b235f651fb78c79c6fc7546475457a41aae6519932dd4c976295a304ada59 | 명시 없음 |
| Duo Module 01 | 회로도 V1.1 · 풋프린트 STAMP_0R55_88.dra · TOP/BOT DXF · 조립도 · 브리프 | https://github.com/milkv-duo/duo-files/tree/main/duo-module-01 | 8a513a34a0a7a13dc14c52412ce281e3824c03912d378c20a6eedf8e5d228d61 · d91dedb855fa7799e3e357db61fe61b5dfb1294b512f4eb092d7ea1bca6fd7cf · 93a4406d3c8945fc9d0e3b8664ed0098e0dd7b1aeef47527fa6d57dcb8fea939 / 2267e8e4f638d3662cf4ad873fa4dc9534e15723748614b25f913061d7b93d0e · 5357e6ba8c6ae25997b62a70a7335eb78f551c265b0e8e0db66e4a83f0280f8c · 129dd3bcb6755e5bb471f7238d59d10ba5c7896c19719dd67a95383b87381d2c | **명시 없음** (LICENSE 없음) |
| Duo Module 01 평가보드 | 회로도 v1.1 | 같은 저장소 evaluation-board/ | 739195fd3e4eaf65c8d10cb36877f63c58722d21f8db9b08a1b3bc53a7727ce8 | 명시 없음 |
| Duo 256M | 회로도 v1.01 | duo-files/duo-256M/hardware/ | 65135f0d556b4d321b2a4b02f100e2032d2ee39bfaf4fc07d5e8cfe63512eaa7 | 명시 없음 |
| 원조 Duo (256M에도 맞는지 미확인) | 풋프린트 .dra · 기구도 zip | duo-files/duo/hardware/ | 09b13cbd7c83564216a4a718e786554bda8b73d06bdbf1b313859f5a5dee1b8a · a99a9a623edcda1d9bda9ad54a1ee8622a0a5573fdb62a15f1801a9e805b3b8b | 명시 없음 |
| Duo S | 회로도 v1.1 · STEP | duo-files/duo-s/hardware/ | 75ea3082a96903e23c643e60b1399c45d8eebac70ec14544a25b834d34513c83 · df70e8718bfe8cfbe01fac98a7f2a282f321eaac069bfd4d11bd32cd2052ef1a | 명시 없음 |

- **보관 (D-003 #14):** 공개 라이선스가 명시된 자료는 reCamera(CC BY-SA 4.0)뿐이다. hardware/datasheets 보관은 이 조사의 소유 파일 범위 밖이라 하지 않았다. 내려받은 파일은 세션 임시 폴더에만 있다.
- **CC BY-SA 주의:** 베이스 보드 설계를 고쳐서 캐리어를 만들면 결과물도 CC BY-SA 4.0으로 내야 한다(ShareAlike). 짝 커넥터 풋프린트만 참고해 새로 그리는 경우와 구분해야 한다(판단은 lead/사용자 몫).

## 4. SDK·카메라 센서 연결 (R-001 IQ 목록과 대조)

| 모듈 | SDK | 기본 IQ 보유 센서 | GC2083 (D-003 #5) | GC4653 (#5 차선) |
|---|---|---|---|---|
| reCamera Core | reCamera-OS (sophpi sg200x-evb 기반, Buildroot 2021.05, Linux 5.10) · 최신 0.2.6 (2026-11-02, 프리릴리스) · 정식 0.2.4 (2026-03-23) | `external/isp_tuning/cv181x/src/`: ov_ov5647_sdr, gcore_gc2053_sdr / sdr_ir · SENSOR_COMPATIBILITY.md에 드라이버 79종 (「커넥터 호환을 뜻하지 않는다」) | 드라이버 목록에만 있음, IQ 없음 → Milk-V IQ 이식 필요 (미확인) | 드라이버 있음 · Sophgo 기본 isp_tuning에 IQ 있음 (이식 미확인) |
| LicheeRV Nano | sipeed/LicheeRV-Nano-Build (main a4d8622) | gc4653 (기본) · os04a10 · os04c10 · sc2336 · imx307 | 드라이버 소스만 있고 defconfig에서 꺼짐, IQ 없음. CAM-GC2083(16P)과 직결 불가 | **기본 지원** (22P FPC, IQ 있음) |
| Duo 256M / Module 01 | milkv-duo/duo-buildroot-sdk-v2 (6f8962c, 2025-11-04) | rootfs: cvi_sdr_bin_GC2083 (sha256 77702b1f…b474, 628,456 B) · OV5647 · SC035HGS · sensor_cfg_GC2083.ini (bus_id 2, 주소 37) | **기본 지원** (16P FPC 직결) | 드라이버 있음 |

- 근거:
  - reCamera: https://github.com/Seeed-Studio/reCamera-OS
  - LicheeRV Nano: https://github.com/sipeed/LicheeRV-Nano-Build
  - Milk-V: https://github.com/milkv-duo/duo-buildroot-sdk-v2
- **R-002 연결:** 별도 센서 보드 FPC(R-002 O1)의 핀배치는 모듈마다 다르다.
  - reCamera는 BTB 센서 쪽이다. 짝 커넥터와 센서 보드 S101/S401 설계를 참고할 수 있다.
  - Nano는 22P, Duo는 16P다.
  - 따라서 센서 보드 커넥터는 아래 M1 선택(reCamera)에 맞춰 다시 정해야 한다.

## D-003 행 번호별 적용 결과

| D-003 # | 값 | 적용 결과 |
|---|---|---|
| 1 | 커널 5.10.4 수용 | 세 SDK 모두 5.10 계열 → 영향 없음 |
| 2 | 모듈 위탁 허용 | reCamera는 BTB에 꽂으므로 납땜 위탁이 필요 없다(조립 뒤 꽂음). Nano·Module 01은 위탁 또는 손 납땜(공개 사례는 저온 솔더 손 납땜) |
| 5 | GC2083 | 권고 모듈에는 GC2083 IQ가 없음 → **위험**. IQ 이식이 안 되면 #5 차선 GC4653 또는 Seeed가 IQ를 공개한 GC2053을 쓴다(lead 판단) |
| 8 | microSD | reCamera 2002(무선 없음)는 SD1이 BTB로 나와 캐리어에 microSD를 둘 수 있다(신호 목록 기준, 미검증) |
| 10 | 12V DC | 모듈 입력: reCamera VIN 5V, Nano 3.6~5.5V, Duo 256M VSYS 5V → 캐리어에 12V→5V 강압 필요 |
| 11 | 유선 이더넷 | reCamera는 BTB MDI + 캐리어 쪽 트랜스·RJ45 (B301 참고) → 충족 |
| 12 | 5장 | reCamera 101991223의 Digi-Key 재고 3개 + Seeed(수량 미표시) → 5개 확보는 **미확인** |
| 14 | 공개 라이선스 자료만 보관 | reCamera CC BY-SA 4.0만 해당 (보관은 범위 밖) |
| 15 | 모듈 기준 | 판정표 참고 → 권고 reCamera Core 2002, 우선 후보였던 Nano-E는 차선 ① |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| M1 | 권고 모듈 | **reCamera Core 2002 8GB (101991223)** | D-003 #15 ①②③ 중 STEP을 빼고 모두 충족. CSI와 MDI가 커넥터로 나와 캐리어에서 광학·이더넷을 자유롭게 배치할 수 있다 | ① LicheeRV Nano-E + GC4653 (CSI·이더넷이 모듈 위치에 묶임) ② Duo 256M + CAM-GC2083 (재고·STEP 약함) |
| M2 | 무선 변형 | 무선 없음 (2002) | D-003 #11 유선 이더넷 · 가격이 낮음 · SD1을 쓸 수 있음 | 2002w (101991224) — 5개 재고가 모자라면 섞어 쓴다(같은 핀배치인지 확인 필요) |
| M3 | eMMC 용량 | 8GB | 최소 구성 (D-003 #8 이벤트 전송 기본) | 64GB (102991898) — 재고 보완용 |
| M4 | 코어 STEP 부재 | 케이스 STEP과 회로도 외형으로 기구 기준을 잡고, 실물을 받은 뒤 측정 | 공개된 코어 STEP이 없다 | 차선 모듈(Nano는 STEP 공개)로 전환 |

## 확인 못 한 것

- **reCamera:**
  - 코어 단독 외형
  - J1/J2 중 어느 쪽이 센서용이고 어느 쪽이 베이스용인지, BTB 원품번
  - Seeed 재고 수량
  - Digi-Key 가격 이상(등록 오류 여부)
  - Mouser 가격·재고
  - GC2083 IQ 이식 가능 여부
- **LicheeRV Nano:**
  - 공식 AliExpress·Taobao의 가격·재고·SKU 옵션명
  - WE 이더넷 패드 정의
  - PCB 두께, 리플로 가능 여부
  - 카메라 I2C 전압
- **Milk-V:**
  - Duo 256M 스탬프홀 SMT 공식 문구, 하면 부품, J8 위치
  - Module 01 3V3 입력 범위, 외형 25mm와 27.3mm 중 어느 쪽인지
  - Platima Module 01 JSON (429)
- **공통:**
  - 모든 판매처의 5/10개 단가 (공개된 곳 없음)
  - 실제 납기
  - PCBWay/JLC가 모듈을 위탁부품으로 받은 공개 사례
