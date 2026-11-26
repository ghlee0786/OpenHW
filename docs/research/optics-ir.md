# R-002 광학 일체 실장 조사 — 렌즈·IR-cut(ICR)·IR LED·주야 판별·기구 (초안)

- 배정: orch t18r R-002 (lead t18q) · 입력: product-brief.md (lead 레인 c6ba2bc 「광학 일체 실장」) · D-001 · R-001 결과(soc-sg2002.md, bbf3930)
- 형태 변경 반영: D-002(6e2c286)에 따라 형태가 「SG2002 코어 모듈 + 자체 캐리어」로 바뀌었다. 광학 부품은 **캐리어 보드 또는 별도 센서 보드**에 실장하는 것을 기준으로 정리한다. 모듈 쪽 카메라 커넥터·MIPI 제약은 R-003(module-sg2002.md)과 연결한다.
- 조사자: research t18s · 확인일: **모두 2026-11-26** · 공개 웹 읽기만 (가입·로그인·견적·주문 없음)
- 표기: **확인됨** = 1차 페이지/데이터시트에서 직접 확인 · **미확인** = 검색 요약·2차 자료·접속 차단 · **계산** = 공개 값으로 계산한 것
- 상태: 조사 완료 · D-003 기본값 적용 결론 포함 (맨 아래 「결론」)

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

## 3. IR LED와 센서 NIR 감도

### 3.1 센서 NIR 감도

| 센서 | 850 / 940nm | 기술 표기 | 확인 | 근거 |
|---|---|---|---|---|
| OS04A10 | **QE 60% / 40%** | Nyxel | 확인됨 (공식) | https://www.ovt.com/products/os04a10/ |
| OS04C10 | 수치 없음 (「850·940nm 모두 높은 QE」 문구만) | Nyxel, PureCel Plus | 표기만 | https://www.ovt.com/wp-content/uploads/2026/05/OS04C10-PB-v1.2-WEB.pdf |
| SC4336(H) (V851) | 절대값 없음. SC4336H는 전작 대비 850nm +21%, 940nm +15% | SFCPixel | 상대값만 | https://www.smartsenstech.com/en/page?id=323 |
| SC2336 | NIR 언급 없음 | SFCPixel | 미확인 | https://www.smartsenstech.com/en/page?id=163 |
| IMX307 | 수치 없음 (STARVIS 제품군 일반 설명만) | STARVIS | 표기만 | https://www.sony-semicon.com/en/technology/security/index.html |
| GC4653 · GC2083 · GC2053 · GC4663 | 없음 | 없음 | 미확인 (GalaxyCore 사이트 점검 중) | — |

→ 850/940 선택 근거가 되는 공식 수치는 OS04A10 하나뿐이다. 나머지 센서는 **실측(같은 LED·거리에서 영상 밝기 비교)이 필요**하다.

### 3.2 IR LED 후보 (데이터시트 값, 1A 기준)

| 파장 | 품번 | 방사 강도 | 방사속 | 연속 / 펄스 | Vf | 반치각 | 패키지 / Rth(실측) | 데이터시트 |
|---|---|---|---|---|---|---|---|---|
| 850 | ams OSRAM SFH 4715AS A01 | 일반 770 mW/sr | 1360 mW | 1.5A / 5A | 2.95V | ±40° | OSLON Black 3.75mm / 5.5 K/W | v1.5 2024-03-14 https://look.ams-osram.com/m/597061415877617c/original/SFH-4715AS-A01.pdf |
| 850 | Vishay VSMA1085600 | 490 mW/sr | 1425 mW | 1.5A / 5A | 3.1V | ±60° | 3.4mm / 6~9 K/W | Rev 1.4 2022-07-08 https://www.vishay.com/docs/80298/vsma1085600.pdf |
| 850 | Vishay VSMA1085250 (좁은 각) | 1350 mW/sr | 1425 mW | 1.5A / 5A | 3.1V | ±28° | 3.4mm / 6~9 K/W | Rev 1.4 https://www.vishay.com/docs/80297/vsma1085250.pdf |
| 850 | ams OSRAM SFH 4170S (넓은 각) | 280 mW/sr | 1250 mW | 1A / 2A | 3.25V | ±65° | P1616 / 11 K/W | v1.7 2025-03-27 https://look.ams-osram.com/m/6e65e7d69e599e4b/original/SFH-4170S.pdf |
| 850 | JNJ LTJI0112W120 (중국) | 220 mW/sr | 520 mW | 최대 1A | 1.5V | 시야각 120° | 3535 세라믹 | A3 2025/05 (LCSC 사본) |
| 940 | ams OSRAM SFH 4725AS A01 | 일반 760 mW/sr | 1340 mW | 1.5A / 5A | 2.65V | ±40° | OSLON Black / 5.5 K/W | v1.10 2025-10-16 https://look.ams-osram.com/m/5c2c1ba34b2984b8/original/SFH-4725AS-A01.pdf |
| 940 | Vishay VSMA1094751 | 320 mW/sr | 1250 mW | 1.5A / 5A | 2.8V | ±75° | 3.4mm / 7 K/W 미만 | Rev 1.1 2025-03-24 https://www.vishay.com/docs/80554/vsma1094751.pdf |
| 940 | ams OSRAM SFH 4180BS | 325 mW/sr | 1485 mW | 1A / 2A | 2.8V | ±65° | P1616 / 6.2 K/W | v1.0 2024-08-13 https://look.ams-osram.com/m/639d5b4ecc74cc99/original/SFH-4180BS.pdf |
| 940 | Silverlight M3535O1IRS9G06-940 (중국) | 표기 없음 | 400 mW (700mA) | 700mA / 최대 1A | 1.4~2.0V | 시야각 60° | 3535 / 4.5 °C/W | LCSC 사본 |

- **신규 설계에 쓰지 않을 품번:**
  - 「Not planned for new design」: SFH 4715AS(A01이 붙지 않은 기본형), SFH 4716AS
  - Obsolete: SFH 4180S A01, LTE-R38381S-S-U, EAIST3535A1
  - 위 표의 품번은 이것들을 뺀 것이다.

### 3.3 850nm vs 940nm

| 항목 | 850nm | 940nm | 근거 |
|---|---|---|---|
| 붉은 잔광 | 고출력에서 붉게 보임 | 850nm보다 50~100배 낮음 | OSRAM AN095 (2018-11-09, 제3자 사본 https://orwintech.com/static/pdf/SFH%204711A.pdf) |
| 센서 감도 | OS04A10 QE 60% | 40% | OVT 공식 |
| LED 출력 (같은 계열, 1A) | 1360~1425 mW | 1250~1340 mW | 각 데이터시트 |
| ICR 선택 | 850nm 대역통과 ICR(CLA216-ICR-850BP) 사용 가능 | 850BP ICR은 쓸 수 없음 → 일반 전대역 ICR | 2.1절 |
| 눈 안전 | 단품은 IEC 62471 Exempt. 고출력 어레이를 연속 구동하면 한계를 넘을 수 있음 | 같음 | 각 데이터시트 Notes · Vishay https://www.vishay.com/docs/81935/eyesafe.pdf · OSRAM AN002 https://look.ams-osram.com/m/1d720a7b18ab3fce/original/Details-on-photobiological-safety-of-LED-light-sources.pdf |

### 3.4 구동·방열·방사각

| 드라이버 IC | 방식 | 입력 | 출력 | 밝기 조절 | 패키지 | LCSC 1개 / 10개 USD | 재고 |
|---|---|---|---|---|---|---|---|
| Diodes AL8860MP-13 (C500782) | 히스테리시스 벅 | 4.5~40V | 1.5A | CTRL 핀 DC/PWM | MSOP-8EP | 1.2867 / 1.0868 | 2,126 |
| TI TPS92515DGQR (C2678910) | 벅 | 5.5~42V | 2A | 아날로그·PWM·shunt PWM | HVSSOP-10 | 2.1088 / 1.8227 | 195 |
| UMW PT4115 (C347356) | 벅 | 6~30V | 1.2A | DIM 아날로그/PWM | SOT-89-5 | 5개 이상 0.1098 | 143,400 |

- **입력 전압 주의:** 세 IC 모두 벅 방식이다. 입력이 LED Vf보다 충분히 높아야 하므로(예: 12V DC나 PoE 이후 레일), 전원 방식이 정해진 뒤에 고른다. 5V USB 입력이면 부스트형을 따로 조사해야 하는데, 이번에는 조사하지 않았다.
- **구동 방식 (Vishay AN 80327, 개정 2025-11-26):** 저전류는 저항이나 LDO, 고출력은 스위칭을 권장한다. 저항으로 병렬 구동하면 열폭주 위험이 있다. https://www.vishay.com/docs/80327/designing_vsma_highpower_ireds.pdf
- **방열:** 같은 앱노트 Table 5의 접합-주변 열저항(RthJA,real)은 다음과 같다.
  - IMS + 방열판: 16 K/W
  - IMS: 30 K/W
  - FR4 + thermal via: 80 K/W
  - 일반 FR4: 150 K/W
  - 동박 면적과 열저항을 연결한 정량 자료는 찾지 못했다.
- **방사각과 조사 거리 (AN095):** LED 방사각을 렌즈 FOV에 맞추고, 맞는 부품이 없으면 2차 렌즈를 쓴다. 조사 거리는 다음 식을 차례로 적용해 추정한다(이번에는 계산하지 않음).
  1. 피사체 조도 E = Ie/d²
  2. 피사체 휘도 L = E·R/π
  3. 센서 조도 E_sensor = L·T·π/(4·f#²·(m+1)²)

### 3.5 IR LED 조달 (2026-11-26, USD)

| 품번 | 판매처 | 1개 / 10개 | 재고 | 확인 |
|---|---|---|---|---|
| SFH 4715AS A01 | Digi-Key | 4.00 / 2.942 | 4,874 | 확인됨 (Active) |
| SFH 4725AS A01 | Digi-Key / LCSC C2900419 | 4.00 / 2.942 · 2.4723 / 2.4161 | 7,959 · 80 | 확인됨 |
| VSMA1085600 | Digi-Key | 3.40 / 2.481 | 3,003 | 확인됨 |
| VSMA1094751 | Digi-Key | 3.15 / 2.294 | 596 | 확인됨 |
| SFH 4170S | Digi-Key | 2.43 / 1.745 | 13,674 | 확인됨 |
| SFH 4180BS-FA2FB2-13 | Digi-Key | 2.24 / 1.606 | 3,972 | 확인됨 |
| JNJ LTJI0112W120 | LCSC C19185834 | 0.455 / 0.3548 | 412 | 확인됨 |
| Silverlight M3535O1IRS9G06-940 | LCSC C2833581 | 0.7981 / 0.649 | 106 | 확인됨 |

Mouser는 접속 시간 초과로 확인하지 못했다.

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

## 결론 — D-003 기본값 적용 (lead 레인 t-20261126-144135-5470 `docs/decisions/D-003-working-defaults.md`, 커밋 8ac5ce5)

운영 변경(사용자 지시 2026-11-26)에 따라 질문을 올리지 않는다. D-003 값을 확정값으로 보고 대표 1안과 차선책을 정했다. 아래 HFOV는 왜곡을 무시하고 2·atan(센서폭/2f)로 **계산**한 값이다. 실제 화각은 렌즈 왜곡에 따라 달라진다.

### D-003 행 번호별 적용 결과

| D-003 # | 값 | 이 조사에서 정한 것 |
|---|---|---|
| 4 | 약 10m, HFOV 약 90°, M12 고정초점 | 센서폭 5.18mm(GC2083, 1920×2.7µm, 계산)에서 HFOV 90°가 되는 f는 약 2.6mm(계산) → f 2.7~2.8mm급 M12 렌즈 |
| 5 | 센서 GC2083 (2MP) | 1/3"·대각 약 5.95mm(계산) → 이미지 서클 6.5mm 이상(1/2.7"~1/2.5"용) 렌즈. NIR 감도 공식 수치는 없어 실측 필요 |
| 6 | IR 850nm | IR LED는 850nm. ICR은 전대역 야간 유리형을 기본으로 둔다(940 차선책을 열어 두려는 것). 850 대역통과형은 차선책 |
| 7 | 주야 판별 = 조도센서 | IR 채널이 있는 I2C 조도센서를 쓴다. 차선책 「영상 밝기」는 SDK `CVI_ISP_GetCurrentLvX100` / `CVI_ISP_IrAutoRunOnce`로 바로 전환 가능(4.3절) |
| 10 | 12V DC | IR LED 구동은 12V 입력 벅 정전류 IC로 정한다(3.4절의 입력 전압 주의가 풀림) |
| 2 | 위탁 허용 | ICR·렌즈·홀더는 유통 표준 부품이 아니므로 위탁 공급 또는 조립 후 수작업 장착 |
| 12 | 5장 | 아래 조달은 5세트 기준이다. 수량 할인 구간은 대부분 공개돼 있지 않다 |
| 14 | 공개 라이선스 자료만 보관 | 이번 광학 자료(데이터시트·도면)는 제조사 저작물이라 라이선스가 명시되지 않았다. 따라서 저장소에 보관하지 않고 링크만 남긴다. Antmicro 풋프린트(Apache-2.0)는 저장소에 가져올 수 있다 |

### 분기점·선택·이유·차선책 (이 조사에서 새로 생긴 갈림길)

| # | 분기점 | 선택(1안) | 이유 | 차선책 |
|---|---|---|---|---|
| O1 | 센서 실장 형태 (D-002 모듈+캐리어) | **별도 센서 보드**: GC2083 + M12 ICR 일체 홀더. 캐리어와는 FPC로 연결한다. **R-003 권고 모듈(reCamera Core 2002, 커밋 c958a25)에 맞춰**, 모듈의 센서 쪽 B2B(CSI 4레인+CLK, I2C2, CAM_EN)에서 캐리어를 거쳐 센서 보드로 잇는다. 공개된 Seeed 센서 보드 S101/S401(KiCad, CC BY-SA 4.0)의 배선을 참고한다. 모듈이 차선 ①(LicheeRV Nano 22P)이나 ②(Duo 256M 16P)로 바뀌면 그 커넥터에 맞춘다 | ICR은 렌즈와 센서 사이에 들어가야 하므로 렌즈 광축·홀더 구멍을 우리 PCB 기준으로 잡아야 한다. 센서를 보드에 붙이면 외함 안에서 광축을 따로 배치할 수 있다 | 기성 CAM-GC2083 모듈을 그대로 쓰고 고정 듀얼밴드 필터(CDB850)로 바꾼다(전환 없음). 또는 같은 센서 보드를 캐리어에 일체로 둔다 |
| O1-위험 | GC2083 **센서 칩 단품 조달** | **미확인** (R-001에서 LCSC 접근 거부, 판매처 못 찾음) | — | 칩을 구하지 못하면 O1 차선책(CAM-GC2083 모듈 + 듀얼밴드 필터)이나 D-003 #5 차선 GC4653(IQ 정식)으로 간다. **후속 조사 항목** |
| O2 | 렌즈 | **Commonlands CIL327 무필터 변형** (f 2.7, F1.8, 1/2.5" 약 7.1mm 이미지 서클, USD 39). GC2083 기준 HFOV 약 88°(계산) | 이미지 서클이 GC2083을 덮고, ICR(CLA216)과 같은 공급사라 호환을 확인하기 쉽다. 무필터 변형이 있어 ICR과 함께 쓸 수 있다 | Kurokesu L187-2.8-M12 IRCUT 없는 기본형 (f 2.8, EUR 35.09, HFOV 약 86° 계산) |
| O2-위험 | 렌즈 IR 보정·BFL과 ICR 높이 | CIL327의 IR 보정과 BFL은 **미확인** | 주야 초점 차이, ICR 7.6mm 안에서 초점이 맞는지 | 실물로 주간·850nm 초점을 확인하고, 안 맞으면 IR corrected가 명시된 렌즈(예: CIL382은 협각이라 화각 조건 불충족 — 같은 계열 광각 IR 보정품을 재조사) |
| O3 | ICR | **Commonlands CLA216-ICR** (20mm, 높이 7.6mm, 3.3V·20Ω, 100~500ms, USD 12, 재고 315) | 3.3V 구동이고 도면(STP)이 공개돼 있으며 재고가 확인됐다. 야간 쪽이 전대역 유리라 940nm로 돌아갈 여지가 남는다 | CLA216-ICR-850BP(850nm 대역통과, 재고 690) / IPCameraBoard IR0117-M12(USD 1.50, 재고 미표시) |
| O4 | ICR 드라이버 | **UMW AP1511B** (LCSC C347457, SOT-23-6, 재고 28,105, 5개 USD 0.113) | ICR 전용 IC이고 3.3V에서 동작하며 재고가 많다 | TI DRV8837DSGR (C39159, 재고 120,550) — GPIO 2개로 펄스 생성 |
| O5 | 렌즈홀더 풋프린트 | CLA216 20mm 구멍 간격 → Antmicro `Camera_Lens_20mm`(Apache-2.0)를 출발점으로 쓰고 CLA216 도면으로 구멍 지름을 맞춘다 | KiCad 공식 라이브러리에 없다 | CLA216 STP에서 직접 작성. CLA216 도면(DocSend) 열람은 이번에 확인하지 못했다 |
| O6 | IR LED (850nm) | **Vishay VSMA1085600** (±60°, 490 mW/sr, 1.5A, Digi-Key 1개 USD 3.40, 재고 3,003) | 반치각 ±60°(전폭 120°)이 HFOV 약 90°를 덮는다. Active 품번이고 데이터시트 Rev 1.4가 있다 | ams OSRAM SFH 4715AS A01 (±40°, 770 mW/sr, Digi-Key USD 4.00, 재고 4,874) — 중앙 거리를 우선할 때 |
| O6-미정 | LED 개수·전류 (10m 조건) | **미정** — AN095 식(3.4절)으로 GC2083 감도를 실측한 뒤 계산한다 | GC2083의 NIR 감도 공식값이 없다 | — |
| O7 | IR LED 드라이버 (12V 입력) | **Diodes AL8860MP-13** (C500782, 1.5A, 4.5~40V, CTRL로 PWM, 재고 2,126) | 12V 입력 벅이고 PWM 밝기 조절이 되며 VSMA 1.5A 정격과 맞는다 | UMW PT4115 (C347356, 1.2A, 재고 143,400, 5개 단위) |
| O8 | 조도센서 | **Lite-On LTR-329ALS-01** (C284894, I2C, CH0+CH1(IR), 0.01~64k lx, 재고 8,120, 10개 USD 0.4978) | IR 채널 비율로 자기 IR LED의 영향을 걸러낼 수 있다(추론). 재고가 확인됐다 | Vishay VEML6030 (C132182, 재고 2,941). LTR-303ALS-01은 재고 숫자와 sold_out 표시가 상충해 제외 |
| O8-기구 | 조도센서 배치 | IR LED와 광학적으로 분리하고, LED를 끈 순간에 샘플링할지는 펌웨어에서 결정한다 | 차광 수치 지침이 없다 | 실측 후 차광 리브 추가 |
| O9 | 보호창 | **투명 PMMA** (주문 재단) + 렌즈 둘레 **흑색 PORON 폼**을 창에 밀착 | 가시광과 850nm를 함께 투과하고 값이 싸다. halo는 폼 밀착으로 막는다(5.1절) | Edmund N-BK7 VIS-NIR AR 창 (#45-658, USD 101) |

**SoC 관련:** 렌즈·ICR·IR LED·조도센서·창은 SoC와 무관하다. SDK와 엮이는 것은 ICR 제어 GPIO 2개와 주야 판정 코드뿐이다. D-002로 SG2002 모듈이 확정됐으므로 V851s에만 해당하는 차이는 결론에서 뺐다.

### 남은 미확인(후속에서 확인할 것)
1. GC2083 센서 칩 단품 조달 (O1-위험)
2. CIL327의 IR 보정·BFL과 CLA216 ICR 안에서 초점이 맞는지 (O2-위험)
3. CLA216 도면 열람 (구멍 지름·높이 공차)
4. 10m 조건의 LED 개수·전류 — 실측 기반
5. 모듈 측 카메라 연결 — R-003 결과: reCamera Core의 센서 쪽 B2B 60P 0.5mm. J1/J2 중 어느 쪽이 센서용인지와 BTB 원품번은 미확인이다. 그리고 reCamera SDK에는 GC2083 IQ가 없다(Seeed IQ는 GC2053·OV5647). GC2083 IQ 이식이 안 되면 D-003 #5 차선(GC4653)이나 GC2053을 고르는데, 이 판단은 lead가 한다. GC2053은 1/2.9"·대각 약 6.17mm(계산)로 O2 렌즈의 이미지 서클(약 7.1mm)에 들어간다.
