# R-002 광학 일체 실장 조사 — 렌즈·IR-cut(ICR)·IR LED·주야 판별·기구 (초안)

- 배정: orch t18r R-002 (lead t18q) · 입력: product-brief.md (lead 레인 c6ba2bc 「광학 일체 실장」) · D-001 · R-001 결과(soc-sg2002.md, bbf3930)
- 형태 변경 반영: D-002(6e2c286)에 따라 형태가 「SG2002 코어 모듈 + 자체 캐리어」로 바뀌었다. 광학 부품은 **캐리어 보드 또는 별도 센서 보드**에 실장하는 것을 기준으로 정리한다. 모듈 쪽 카메라 커넥터·MIPI 제약은 R-003(module-sg2002.md)과 연결한다.
- 조사자: research t18s · 확인일: **모두 2026-11-26** · 공개 웹 읽기만 (가입·로그인·견적·주문 없음)
- 표기: **확인됨** = 1차 페이지/데이터시트에서 직접 확인 · **미확인** = 검색 요약·2차 자료·접속 차단 · **계산** = 공개 값으로 계산한 것
- 상태: **초안(WIP)** — 3절(IR LED·센서 NIR 감도)은 조사 결과를 기다리는 중이다.

## SoC와 무관한 부분 / 센서 포맷에 묶인 부분

| 구분 | 항목 |
|---|---|
| SoC와 무관 | M12 홀더 구멍 간격·높이, ICR 코일 구동(H-브리지), IR LED와 드라이버, 조도센서(I2C/ADC), 창·가스켓·차광 기구 |
| 센서 포맷에 묶임 | 렌즈 이미지 서클·화각, 홀더 높이(렌즈 BFL + ICR 두께), 센서 NIR 감도 → 850/940nm 선택 |
| SoC·SDK에 묶임 | 주야 판별 API(Sophgo `CVI_ISP_IrAutoRunOnce` / Allwinner는 직접 구현), ICR·IR LED GPIO 제어 코드, IR용 IQ(PQ bin) 전환 |
| V851s에만 해당 | 센서 후보 GC2053·GC4663·SC4336 (포맷은 1절 표). 주야 자동 판별 함수가 공개 소스에서 확인되지 않았다(4절). |

## 1. 렌즈와 렌즈홀더

### 1.1 후보 센서 광학 포맷

| 센서 | 포맷 | 해상도 | 픽셀 | 유효 대각 mm | 근거 | 확인 |
|---|---|---|---|---|---|---|
| GC4653 | 1/3" | 2560×1440 | 2.0µm | 5.87 (계산) | Sipeed MaixCAM 카메라 표 https://wiki.sipeed.com/hardware/en/maixcam/cameras.html (GalaxyCore 사이트 점검 중) | 미확인 (2차) |
| OS04A10 | 1/1.79" | 2688×1520 | 2.9µm | 9.02 (공식 image area로 계산) | OVT PB v1.2 (2023-06) https://www.ovt.com/wp-content/uploads/2023/06/OS04A10-PB-v1.2-WEB.pdf · CRA 9° | 확인됨 |
| OS04C10 | 1/3" | 2688×1520 | 1.998µm | 6.21 (계산) | OVT PB v1.1 (2022-10) https://www.ovt.com/wp-content/uploads/2022/10/OS04C10-PB-v1.1-WEB.pdf · CRA 12° | 확인됨 |
| SC2336 | 1/3" | 2MP | 미확인 | 미확인 | https://www.smartsenstech.com/en/page?id=163 | 포맷만 확인됨 |
| IMX307 | Type 1/2.8 | 1945×1097 (권장 1920×1080) | 2.9µm | 6.46 (1080p 영역은 6.39, 계산) | Sony 플라이어 https://www.sony-semicon.com/files/62/flyer_security/IMX307LQD_LQR_Flyer.pdf | 확인됨 |
| GC2083 | 1/3" (1/3.02"로 표기한 곳도 있음) | 1920×1080 | 2.7µm | 5.95 (계산) | https://milkv.io/docs/duo/camera/gc2083 | 미확인 (2차) |
| OV5647 (참고) | 1/4" | 2592×1944 | 1.4µm | 4.58 (계산) | ovt.com 원본 못 찾음 | 미확인 |
| SC035HGS (참고) | 1/6" | 640×480 글로벌 셔터 | 3.744µm | 3.00 (계산) | Sipeed 표 | 미확인 |
| GC2053 (V851) | 1/2.9" | 1920×1080 | 2.8µm | 6.17 (계산) | 모듈 업체 페이지 | 미확인 |
| GC4663 (V851) | 1/3" | 4MP | 2µm | 미확인 | 검색 요약 | 미확인 |
| SC4336 (V851) | 1/3" | 4MP | 미확인 | 미확인 | smartsenstech.com page?id=167 | 포맷만 확인됨 |

- 1/3"~1/2.8" 후보(대각 약 5.9~6.5mm)는 **이미지 서클 6.5mm 이상(1/2.7"~1/2.5"용) 렌즈**로 모두 덮인다.
- 이미지 서클 6.00mm 렌즈(예: Edmund Blue 계열)는 GC4653·GC2083은 덮는다. IMX307·OS04C10·GC2053은 코너가 어두워질 위험이 있다(계산값 기준이라 확정은 아님).
- **OS04A10은 1/1.8"용 렌즈**(이미지 서클 약 9mm 이상)가 따로 필요하다.

### 1.2 M12 렌즈홀더 (보드 실장)

| 공급자 | 품번 | 구멍 간격 | 높이 | 재질 | 도면 | 단가(1개) | 재고 | URL | 확인 |
|---|---|---|---|---|---|---|---|---|---|
| Commonlands | CLA021-LCP | 20mm | 7.4mm (제목은 7mm) | LCP | STP·도면(DocSend, 리비전·라이선스 미확인) | USD 4.50 | 939 (FAQ는 820+로 상충) | https://ja.commonlands.com/products/m12-lens-mount-20mm-spacing-cla021 | 높이·재고 상충 |
| Commonlands | CLA020-PC | 20mm | 10.0mm | PC, M1.6 셀프태핑 | DocSend | USD 4.50 | 품절 | https://ja.commonlands.com/products/m12-lens-mount-20mm-spacing | 확인됨 |
| Commonlands | CLA022-PC | 22mm | 7.9mm | PC | DocSend | USD 4.50 | 380 | https://ja.commonlands.com/products/m12-lens-holder-22mm | 확인됨 |
| Commonlands | CLA024-LCP / CLA025-PC | 22mm | 12 / 14mm | LCP / PC | DocSend / 없음 | USD 4.50 | 1 / 8 | ja.commonlands.com | 확인됨 |
| Sunex | CMT104-6H | 20mm | 16.7mm | 알루미늄, 측면 M2 고정나사 | PDF Rev A (2010) | USD 11 (1~99개 같은 단가) | 미확인 | http://www.optics-online.com/Detail.asp?PN=CMT104-6H | 확인됨 |
| Lensation | SH05H70 / SH02M13V3 | 20 / 22mm | 7 / 13mm (도면은 12.5±0.5) | ABS / 플라스틱 | JPG / PDF Rev A | 견적 필요 | 미확인 | https://www.lensation.de/product/SH05H70/ | 확인됨 (가격 제외) |
| Teledyne | ACC-01-5006/-5007 | M1 정렬 다월핀 2개 | 15.3mm | 금속 | ZIP(PDF·STEP·IGS, 2009) | USD 61.46 / 44.94 | 문의 | https://www.teledynevisionsolutions.com/products/s-mount-m12-lens-holder/ | 확인됨 |
| Edmund | #66-382 | 미확인 | 미확인 | 플라스틱 | 없음 | USD 13 | 20개 이상 | https://www.edmundoptics.com/p/m12-mu-video-lens-holder-for-camera-boards/20897/ | 일부 확인 |
| AliExpress | (일반품) | 대부분 20mm | 7~16.5mm | 금속/PC | 없음 | 약 ₩1,000~6,240 | 미확인 | — | 미확인 |

- **도면 라이선스:** 재사용 라이선스를 명시한 공급자는 없다. Marshall V-LH4 도면에는 「PROPRIETARY」 사용 제한 문구가 있다.
- **KiCad 풋프린트:**
  - KiCad 공식 라이브러리에 M12 홀더는 **없다**(전체 목록 검색으로 확인).
  - 공개된 예는 Antmicro `Camera_Lens_20mm` 하나다: NPTH Ø1.5 ×2, 20mm 간격, STEP 포함, **Apache-2.0**. https://github.com/antmicro/ov9281-camera-board
- **5/10개 단가:** 공개한 곳이 없다(Commonlands 대량 단가는 50개부터).

### 1.3 M12 렌즈 (FOV 대역별 예시 — 확정 아님)

| 대역 | 품번 | 포맷/이미지 서클 | f / F | 화각 | BFL | IR 보정 / IR컷 내장 | 단가(1개) | URL | 확인 |
|---|---|---|---|---|---|---|---|---|---|
| 광각 | Kurokesu L187-2.8-M12 | 1/2.7" | 2.8 / 2.2 | D 133.6° | 플랜지 2.6 | 미확인 / IRCUT 변형 있음 | EUR 35.09 | https://www.kurokesu.com/item/L187-2.8-M12 | 확인됨 |
| 광각 | Commonlands CIL327 | 1/2.5" (약 7.1mm) | 2.7 / 1.8 | 125° | 미확인 | 미확인 / 660nm·무필터 변형 | USD 39 | https://commonlands.com/products/wide-angle-3mm-m12-lens-cil327 | 가격만 확인 |
| 광각 | Arducam M27210H08 | 1/2.7" | 2.1 / 2.0 | D/H 131/125° (1/2.8") | 6.3 | 미확인 / 650nm 내장 | 미확인 | Arducam LK005 데이터시트 | 사양만 확인 |
| 표준 | Arducam M27280M07S | 1/2.7" | 2.8 / 2.8 | D/H 98/90° (1/2.8") | 2.6 | 미확인 / 650nm 내장 | 미확인 | 같음 | 사양만 확인 |
| 표준 | Edmund #20-055 | 6.00mm | 3.0 / 2.5 | H 91.2° (1/3") | 4.7~4.8 | 미확인 / 내장 | USD 115 | edmundoptics.com/p/…/47410/ | 확인됨 |
| 협각 | Commonlands CIL382 | 1/2.5" | 7.8 / 2.0 | 53° | 미확인 | **IR corrected 명시** / 650nm·무필터 변형 | USD 29 | https://commonlands.com/products/ir-corrected-8mm-m12-lens-cil382 | 가격 확인 |
| 협각 | Arducam M2508ZH02 | 1/2.5" | 8 / 2.0 | D/H 45/40° (1/2.8") | 8.1 | 미확인 / 650nm 내장 | 미확인 | LK005 | 사양만 확인 |
| OS04A10용 | Commonlands CIL083 / CIL085 / CIL034 | 1/1.8" | 8 / 8.2 / 3.2 | — | 미확인 | 미확인 | USD 19 / 49 / 39 | commonlands.com | 가격 확인 |

- **ICR을 쓰면** 렌즈 자체에 IR컷이 **없어야** 한다(「무필터」 변형). IR 보정(IR corrected) 여부를 확인한 것은 CIL382뿐이다.
- **고정 초점:** USD 13~49, 4~10g, 접착하면 안정적이다. 화각을 바꾸려면 렌즈를 바꿔야 한다.
- **수동 바리포컬:** 예) Marshall CV-2812-3MP, 2.8~12mm F1.4, IR 보정, USD 22.99, 품절. 크고 BFL이 6.9~14.4mm로 변해 홀더 높이를 정하기 어렵다.
- **전동·AF:** 예) Commonlands CLA321-VCM USD 29 + 별도 드라이버 DW9714 등. 드라이버와 제어가 더 필요하다.

### 1.4 마운트 비교 (Commonlands 카탈로그 종 수 기준, https://www.edmundoptics.com/knowledge-center/application-notes/imaging/lens-mounts/)

| 마운트 | 크기 | 렌즈 폭 | 가격대 | 판단 근거 |
|---|---|---|---|---|
| M12 (M12×0.5) | 외경 14~18mm | 133종 (가장 넓음) | USD 19~149 | 보드 카메라 표준, 홀더·ICR 일체품이 흔함 |
| M8 / M7 | 작음 / 약 10.5mm 정사각 | 4종 / 3종 (주로 1MP급) | USD 19~39 | 소형이지만 선택 폭이 좁다 |
| CS / C | 큼 | 3 / 45종 | USD 59~499 | 크고 비싸다 |

## 2. IR-cut 필터 전환기 (ICR)

### 2.1 종류

| 종류 | 장점 | 단점 | 예시 | URL |
|---|---|---|---|---|
| M12 홀더 일체형 2선 코일(회전) | 흔하고 쌈(USD 1.5~12), 구멍 간격 18/20/22mm, 극성 반전 구동 | 높이 7.6~14mm, 딸깍 소리, 수명 5만~10만 회 | Commonlands CLA216-ICR (20mm, 7.6mm) · CLA214-ICR (20mm, 14mm) · IPCameraBoard IR0117-M12 (20mm, 7.9mm) · ICR204-M12 (20/22mm) | https://ja.commonlands.com/products/ir-cut-off-filter-switcher-m12-cla216 · https://ipcameraboard.com/product/icr204-m12-8mp-1-2.5-20-22mm-ir-cut-filter-m12-lens-mount-double-filter-switcher-cctv-camera |
| 일체형 직선 이동 자석(슬라이드) | 판매처는 회전형보다 수명이 길다고 함 | 구멍 18mm, 높이 9.5mm | Commonlands CLA219-ICR | https://ja.commonlands.com/products/ir-cut-off-filter-exchanger-cla219 |
| 650nm 차단 ↔ 850nm 대역통과 전환 | 850nm 조명 전용일 때 야간 대비가 좋다 | **940nm 조명은 못 쓴다** | CLA216-ICR-850BP | https://ja.commonlands.com/products/ir-cut-off-850nm-bandpass-switcher-cla216 |
| 액정·전기변색(무가동) | 소음·마모 없음 | **상용 제품 없음**(특허만: US10547783 등) | — | — |
| 대안: 고정 듀얼밴드 필터 | 움직이는 부품 없음 | 주간에 850nm가 섞여 색이 틀어지고 전환이 안 된다 | Commonlands CDB850 | https://commonlands.com/products/dual-bandpass-filter-850nm-cdb850 |

- **필터 사양:** 낮 쪽은 645~650nm(±10)에서 50%로 차단한다. 밤 쪽은 반사방지 코팅 전대역 유리다(ICR204는 400~1100nm에서 90% 이상).
- **도면:** Commonlands STEP·도면은 DocSend로 공개된다. ICR204 도면은 이미지로만 있다.

### 2.2 코일 사양 (구동 조건)

| 품번 | 전압 | 저항 / 전류 | 펄스폭 | 래칭(무전원 유지) | 수명 | 확인 |
|---|---|---|---|---|---|---|
| CLA216/214/219-ICR | 3.3V 구동 (3.0~5.0V) | 20Ω±10Ω (3.3V에서 약 165mA, 계산) | 100~500ms | 명시 없음 | 최소 5만 회 | 확인됨 |
| IR0117-M12 | ±3.3V 정격 (3.3~12V) | 25Ω±3Ω | 100~200ms | 명시 없음 | 5만 회 | 확인됨 |
| ICR204-M12 | 3.3~12V | 3.3V에서 0.083A | 100~500ms | 명시 없음 | 10만 회 | 부분 확인 |
| Seculens IR0722 | 3.5~12V (권장 3.5V) | 45±8Ω, 430µH | 100ms | **예** (「不通电时滤光片保持不动」) | 5만 회 | 확인됨 http://www.seculens.cn/static/upload/file/20220324/1648099155118815.pdf |

→ 코일 전류가 약 80~165mA라 **SoC GPIO로 직접 구동할 수 없다. H-브리지가 필요하다.**

### 2.3 구동 IC (LCSC 공개 값, 2026-11-26)

| IC | 전압 | 전류 | 패키지 | LCSC 재고 / 단가 | URL |
|---|---|---|---|---|---|
| UMW AP1511B (ICR 전용) | 2.5~5.5V | 연속 500mA(절대최대) | SOT-23-6 | 28,105 / 5개 USD 0.113 | https://www.lcsc.com/product-detail/C347457.html |
| BORN BE1511B (ICR 전용, 원샷 펄스 T=1.5×10⁶×C) | 2.5~5.5V | 권장 300mA | SOT-23-6 | 2,870 / 5개 USD 0.109 | https://www.lcsc.com/product-detail/C41374261.html |
| TI DRV8837DSGR | 1.8~7V | 미확인 | WSON-8 | 120,550 / 5개 USD 0.236 | https://www.lcsc.com/product-detail/C39159.html |
| TI DRV8838DSGR | 1.8~7V | 1.8A | WSON-8 | 1,105 / 1개 USD 0.891 | https://jlcpcb.com/partdetail/TexasInstruments-DRV8838DSGR/C86667 |
| MX6208 / AD6208S (BA6208 계열) | 4~15V / 4.5~18V | 0.2A | SOIC-8 | 3,770 / 1,180 | **3.3V 단일 전원에는 맞지 않는다** |

### 2.4 SDK의 ICR 제어

- **Sophgo sophapp(ipcamera):** `app_ipcam_IRCut_Switch()`가 GPIO A/B 중 하나를 High로 올리고 500ms 뒤 Low로 내린다. 주야 판정은 4절 참고. 근거: https://github.com/sophgo/sophapp/blob/master/modules/peripheral/ircut/src/app_ipcam_ircut.c (확인됨)
- **CV180x u-boot 보드 초기화:** `//IRCUT` 아래 PWR_GPIO18/19 설정이 주석으로 들어 있다(Milk-V·Sipeed 공통). ISP 헤더에 `s16IRCutOnLv/OffLv` 항목이 있다. (확인됨)
- **Allwinner:**
  - `sunxi-ircut.c`: `ircut_pin_a/b`, `hold_time` 기본 100ms. V821 BSP의 **제3자 미러**에서만 확인했다.
  - TinyVision `sensor_set_ir()`: 200ms. (부분 확인)

## 3. IR LED와 센서 NIR 감도 — **조사 결과 대기 중**

## 4. 주야 판별 방식

### 4.1 선택지

| 방식 | 추가 부품비 | 신뢰도 | 펌웨어 | SDK 의존 |
|---|---|---|---|---|
| A. ISP 통계만 (AE ISO/LV + AWB 색비) | 0 | Sophgo API는 IR→주간 복귀 때 색비 조건으로 자기 IR 오판을 줄인다. 점광원(가로등)에 대한 영향은 미확인 | 중 (센서·렌즈·LED 조합별 보정) | 높음 (Sophgo에는 있고, Allwinner는 직접 구현) |
| B. CdS + ADC | 약 USD 0.05 | 느리고 비보정, **RoHS 부적합 가능성** | 낮음 | 없음 |
| C. 포토트랜지스터(ALS-PT19) + ADC | 약 USD 0.1 | 제조사가 IR 제거비가 높다고 함(850nm 수치는 미확인) | 낮음~중 | ADC 드라이버만 |
| D. 디지털 조도센서 I2C | 약 USD 0.44~2.6 | lux 보정됨, IR 채널 센서는 IR 비율로 걸러낼 수 있다(추론, 미검증) | 중 | 없음 |
| E. 하이브리드 (C 또는 D + A, 히스테리시스·유지시간) | C·D와 같음 | 가장 높을 것으로 판단(업계 직접 권고 문구는 못 찾음) | 높음 | 부분 |

- **CdS의 RoHS 문제:**
  - RoHS 부속서 III 40항 예외는 「professional audio equipment」 한정이었고 2013-12-31에 **만료**됐다. https://www.legislation.gov.uk/eudr/2012/51/annex/adopted (확인됨)
  - 그런데 LCSC는 GL5528을 RoHS 적합으로 표기한다. 근거와 모순된다.
- **IR LED 자기반사:** TI SSZTD81(2025-04)은 「For camera applications … ALS have high infrared rejection … to filter out the infrared light from LEDs used for camera night vision」이라고 한다. 배치·차광의 수치 지침은 찾지 못해 **실측이 필요**하다.

### 4.2 조도센서 후보 (LCSC, 2026-11-26, USD)

| 품번 (LCSC) | 인터페이스 | 범위 | 패키지 | 1개 / 10개 | 재고 | 데이터시트 | 확인 |
|---|---|---|---|---|---|---|---|
| VEML6030 (C132182) | I2C+INT | 0~140k lx | 2×2×0.87mm | 0.7714 / 0.6148 | 2,941 | https://www.vishay.com/docs/84366/veml6030.pdf Rev 1.8 2024-11-28 | 확인됨 |
| VEML7700-TT (C1850416) | I2C | 0~약 140k lx | SMD-4P 6.8×2.35 | 1.2015 / 0.9980 | 1,328 | https://www.vishay.com/docs/84286/veml7700.pdf Rev 1.8 | 확인됨 |
| LTR-303ALS-01 (C364577) | I2C+INT, CH0+CH1(IR) | 0.01~64k lx | DFN-6 2×2 | 0.5486 / 0.4369 | 9,867 (페이지 필드는 sold_out으로 상충) | DS86-2013-0004 Rev A | 확인됨 (상충 있음) |
| LTR-329ALS-01 (C284894) | I2C, CH0+CH1(IR) | 0.01~64k lx | VDFN-4 | 0.6148 / 0.4978 | 8,120 | DS86-2014-0006 Rev B | 확인됨 |
| TSL25911FN (C176812) | I2C, 광대역+IR | 600M:1 | DFN-6 | 3.0853 / 2.6123 | 234 | ams DS000338 v2-04 | 확인됨 |
| BH1750FVI-TR (C78960) | I2C | 1~65535 lx | WSOF-6 | 0.9336 / 0.7799 | 27,369 | ROHM Rev.D, 「The influence of infrared is very small」 | 확인됨 |
| ALS-PT19-315C (C146233) | 아날로그 | 미추출 | 0603 | 5개 0.1116 | 18,110 | Everlight V8 | 확인됨 |

### 4.3 SDK 지원

- **Sophgo CV181x (SG2002) — 확인됨:**
  - 구조체: `ISP_IR_AUTO_ATTR_S` (milkv-duo/duo-buildroot-sdk-v2 `cvi_mpi/include/isp/cv181x/cvi_comm_isp.h` L627, 커밋 6f8962c394 2025-11-04)
  - 판정 함수: `CVI_ISP_IrAutoRunOnce()` (선언 `cvi_isp.h` L325, 구현 `cvi_mpi/modules/isp/cv181x/isp/src/cvi_isp.c` L3839)
    - 주간→IR: ISO가 임계값 이상
    - IR→주간: ISO가 임계값 이하이고 R/G·B/G가 IR 범위를 벗어날 때
    - **판정만 하고, ICR·LED·PQ bin 전환은 앱이 한다.**
  - 샘플: `cvi_mpi/sample/sample_ir_auto/` (보정 모드 0 / 검증 모드 1). Sipeed `middleware/v2/sample/ir_auto/`에도 있다.
  - 레퍼런스 앱 sophapp ipcamera: `CVI_ISP_GetCurrentLvX100` 기반이다.
    - 야간 진입 LV×100 < 400, 주간 복귀 > 600, 5회 연속, 1초 주기
    - ICR·IR LED·PQ bin을 함께 전환한다.
    - **광센서는 쓰지 않는다**(ADC 모듈이 있지만 호출하지 않음).
- **Allwinner V851/V853 — 전환 장치만 있음, 자동 판정은 미확인:**
  - TinyVision `vin_video.h`의 `enum ir_mode {DAY, AUTO, NIGHT}`는 부팅 단계에서 GPADC 광센서와 LV를 쓰는 설계다.
  - Linux에서는 「Linux not support read gpadc vol」이다.
  - lindenis-v853-external libisp에는 `isp_ir_reset()`·`isp_get_lv()`만 있다 → **앱에서 직접 구현해야 한다.**
- **히스테리시스·유지시간 참고:**
  - Espressif esp_ipa IR (`night_ir_factor`): https://docs.espressif.com/projects/esp-video-components/en/latest/esp32p4/Solutions/ir_night_vision.html
  - Realtek AmebaPro2 SW ALS
  - OpenIPC wiki (스스로 outdated라고 표기)

## 5. 기구 주의점과 소량 조달

### 5.1 주의점

| 항목 | 문제 | 대책 | 근거 (성격) |
|---|---|---|---|
| IR 누설(halo) | 렌즈 둘레 폼이 창에 밀착되지 않으면 원형으로 뿌옇게 되는 「CIRCULAR FOG」가 생긴다. 렌즈를 기울이면 더 잘 샌다 | 폼을 살짝 눌러 창에 밀착 (「It is important that the rubber touches the dome」) | https://whitepapers.axis.com/en/ir-reflections-in-dome-cameras · https://downloads.trendnet.com/notes/Technical_Bulletin-Foggy_Dome.pdf (카메라 제조사, 원문 확인) |
| 창 안에 갇힌 빛 | 창 안쪽에서 퍼지는 LED 빛 | 창 아래 LED와 수광부 사이에 흡수 폼(Rogers Poron 4701-30) | ADI 기술 기사 (요약만 확인) |
| 오염 | 지문·물방울이 야간 IR에서 심하게 드러난다 | 보호필름, 세척, 주변 반사면 제거 | TRENDnet·Axis (원문 확인) |
| 창 반사 손실 | 면마다 약 4%, 창 하나에 약 8% | 두께 최소화, AR 코팅 | https://www.vishay.com/docs/80075/mechnote.pdf (원문 확인) |
| 창 거리·기울기 | 수치 권장값을 못 찾음 | 실측 | — |
| 광축 센터링 | 렌즈를 화소 영역 중심에 맞춰야 한다. 나사 고정만으로는 약 ±100µm | PCB 정밀 구멍과 정렬 핀·탭 | TI SBAA217 https://www.ti.com/document-viewer/lit/html/SBAA217/centering-sbaa2175315 |
| 기울기·초점 심도 | f/2, c=3µm이면 초점 허용폭 ±6µm. 일반 센서 규격상 기울기 1° | 렌즈를 90° 돌려 렌즈 기울기와 센서 기울기를 구분 | https://commonlands.com/blogs/technical/active-alignment-for-camera-modules · Allied Vision Alvium Bare-Board AppNote V1.2.0 |
| 능동 정렬 필요 여부 | Sunex: 5MP 초과 또는 픽셀 2µm 미만부터 나사산 조립의 한계 | 후보 센서는 픽셀 2.0~2.9µm라 수동 정렬 범위로 본다(**추론**) | https://sunex.com/2020/09/03/basic-thread-considerations-for-lens-holder-pairing-on-board-mount-cameras/ |
| 초점 고정 | 나사 유격, 접착제 경화 수축 | 1/16회전(31.25µm) 단위로 조정, 백래시 제거, UV(+열) 접착 또는 락링(CLA-M12-LOCKRING USD 4.50), 고정 후 재확인 | https://ja.commonlands.com/blogs/technical/how-to-focus-a-camera |
| 주야 초점 차 | 가시광과 IR의 초점면이 다르다. 850nm 보정이 940nm까지 보장되지는 않는다 | IR 보정 렌즈를 쓰고 주야 양쪽에서 초점을 확인 | https://commonlands.com/blogs/technical/ir-corrected-lens-machine-vision (요약) |
| ICR이 BFL을 잡아먹음 | ICR 높이 7.6~14mm가 렌즈와 센서 사이에 들어가 BFL이 짧은 광각 렌즈는 초점이 안 맞을 수 있다 | 렌즈·ICR·홀더를 묶어서 선정 | https://www.teledynevisionsolutions.com/support/support-center/system-requirements/iis/camera-compatibility-with-m12-microlenses/ |
| ICR 자기 간섭·먼지 | 자석 구동부, 움직이는 필터 | 근처에 인덕터·자성 부품을 두지 않음, 밀폐 | Seculens IR0722 사양 |
| 발열 → 노이즈 | 암전류가 약 6~8°C마다 2배(CCD 측정값이라 CMOS에 그대로 적용은 안 됨) | LED와 센서를 열적으로 분리 | https://www.onsemi.com/pub/Collateral/AND9192-D.PDF |
| 결로·김서림 | 밀폐 함체 안 수분이 차가운 창에 맺힘 | ePTFE 통기 벤트 (데시칸트는 포화되면 역효과라는 시험이 있음) | https://www.gore.com/solutions-condensation-management (제조사 마케팅) |

### 5.2 창 재질

| 재질 | 850/940nm 투과 | 판단 |
|---|---|---|
| 투명 PMMA 3mm | 700~1400nm 약 90% (850·940 개별 값 미확인) | 가시광도 통과해 주야 겸용 가능 (https://www.acrylite.co/resources/knowledge-base/article/can-you-explain-infrared-radiation-and-show-a-transmission-curve) |
| 투명 PC | 수치 미확인 | Vishay는 근적외 창에 PC를 권장 |
| **IR 투과 흑색 PC** (Makrolon 2407/AX2477) | 약 90% | **가시광을 막아 주간 컬러(ICR) 카메라에는 쓸 수 없다** (https://www.vishay.com/docs/80582/windowmaterialforproximityreflectivesensors.pdf) |
| Borofloat + NIR AR | 700~1150nm 97% 이상 | 내후성 좋음. 가시광 반사는 미확인 |
| N-BK7 + VIS-NIR AR | 반사 1.25% 이하 (400~870nm) | 주야 겸용 대역, 비쌈 |

### 5.3 기구 부품 소량 조달 (USD)

| 부품 | 판매처 | 단가 | URL | 확인 |
|---|---|---|---|---|
| Borofloat Ø12.5×1.75mm NIR 코팅 창 | Edmund #12-187 | 1~5개 38.75 / 6~25개 31.00 | https://www.edmundoptics.com/p/125mm-diameter-x-175mm-thickness-nir-coated-borofloatreg-window/41151/ | 확인됨 |
| N-BK7 Ø12.5×3mm VIS-NIR 창 | Edmund #45-658 | 101.00 / 81.50 | https://www.edmundoptics.com/p/125mm-dia-3mm-thick-vis-nir-coated-lambda4-n-bk7-window/6129/ | 확인됨 |
| 아크릴 원판 주문 재단 | TAP Plastics | 인치당 0.25 (최소 15) | https://www.tapplastics.com/product/plastics/custom-cut-plastic-circles | 미확인 (403) |
| PORON 4701-30 흑색 폼 | Presbond | 17.95부터 | https://presbond.com/products/poron%c2%ae-4701-30 | 미확인 (429) |
| 차광 flock paper | Edmund #54-574 | 46.00 (5장) | https://www.edmundoptics.com/p/65-8quot-x-10quot-5-sheets-non-adhesive-flock-paper/11262/ | 확인됨 |
| ICR CLA216-ICR / -850BP / CLA219-ICR | Commonlands | 각 12.00 (5/10개 단가 없음) | 위 URL | 확인됨 (재고 315 / 690 / 858) |
| ICR IR0117 / ICR204 / ICR228 | IPCameraBoard | 1.50 / 1.80 / 2.20 | 위 URL | 단가만 확인 (재고·MOQ·배송 표시 없음) |
| M12 홀더 | Commonlands | 4.50 | 1.2절 | 확인됨 |
| 렌즈 | Commonlands / Kurokesu / Edmund | 19~137 | 1.3절 | 일부 확인 |

국내 판매처는 찾지 못했다.

## 선택지·장단점 요약과 lead에 올릴 질문 — 3절 결과 반영 후 확정 (초안)
