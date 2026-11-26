# R-001 SG2002 조달·문서·SDK·센서 조사 (V851s 비교)

- 배정: orch t18r R-001 (lead t18q 지시) · 입력: D-001-soc.md 「확인 필요」 1~5, product-brief.md (lead 레인 aca3dd1)
- 조사자: research t18s · 확인일: **모두 2026-11-26** (아래 표의 값은 이 날 공개 페이지·GitHub API로 본 값)
- 방법: 공개 웹/GitHub API 읽기만. 가입·로그인·견적요청·장바구니·주문·업로드 없음. 내려받은 공개 문서는 실행하지 않고 sha256만 계산(저장소에는 넣지 않음).
- 표기: **확인됨** = 해당 페이지/파일에서 직접 본 값 · **미확인** = 검색 요약·추정·접속 차단 등으로 직접 확인 못 함. 가격 검색만으로 호환을 확정하지 않는다.

## 결론 (요약)

1. **SG2002 칩 단품 소량 조달: 불확실(현재 정상 경로로 구매 불가).**
   - Milk-V가 SG2002 공식 유통사(Authorised Global Distributor)인데, 공식 샘플 채널 Arace 5개 팩(USD 24.99)이 **품절**이다.
   - Spotpear 5개 팩은 **「停产」(단종)** 표시다.
   - LCSC·Digi-Key·Findchips(Arrow·Mouser 등 집계)·Octopart에는 Sophgo SG2002가 **없다**.
   - JLCPCB에는 고객 위탁 등록 항목만 있고 모두 재고 0이며 「This product is no longer manufactured.」로 표시된다.
   - 남은 경로는 ① Milk-V 영업 직접 문의(외부 연락 — 사용자 승인 필요), ② AliExpress 재판매(Arace 가격의 3~6배, 진위 불명)뿐이다.
   - 단종(EOL) 여부는 Sophgo/Milk-V 공식 확인이 없어 **미확인**이다. 다만 두 곳의 단종 표시는 위험 신호다.
2. **PCBWay 턴키 조립: SG2002는 어려움(추정).** PCBWay가 부품을 사 오는 Digi-Key·Mouser·Arrow·Avnet에 칩이 없다. 칩을 직접 보내는 위탁(Kitted/Consigned) 조립은 공식 옵션으로 있다.
3. **문서·SDK는 SG2002 쪽이 공개도가 높다.**
   - 공개 문서: TRM v1.02, 데이터시트(1.0-alpha), HW 설계 가이드, 핀아웃, 레퍼런스 SCH/PCB 원본(BSD-2-Clause).
   - SDK·NPU 도구: SDK는 공개 git, tpu-mlir 는 cv181x를 지원한다.
   - 단, 벤더 커널은 **5.10.4 고정**이다. 메인라인 커널에는 카메라·ISP·NPU가 없다.
4. **V851s는 칩 조달이 훨씬 쉽다.**
   - LCSC 재고: V851s 175개, V851SE 44개. 1개부터 살 수 있고 1개 단가는 $12~15다.
   - JLCPCB 라이브러리에 등록돼 있다.
   - 대신 DDR이 **64MB DDR2**다(128MB인 V851s3는 단품 판매처 없음).
   - SDK는 **AWOL 포럼 LV2 계정**이 있어야 받을 수 있다.
   - NPU 변환 도구(Acuity)는 공개 다운로드처가 없다.
   - 공개된 데이터시트는 「Confidential」 미러본이다.
   - 메인라인 리눅스는 사실상 미지원이다.
5. **사용자에게 돌아갈 선택지** (D-001의 「조달 불가 시」 조항에 해당):
   - (A) Milk-V 영업에 재고·EOL·소량 조건 문의 후 SG2002 유지
   - (B) V851s/V851SE 전환
   - (C) SG2002 모듈 캐리어 경로 — 예: LicheeRV Nano 코어보드(풋프린트 공개). 모듈 단품 구매성은 **미확인**.
   - (D) AliExpress 재판매 칩을 위험 감수하고 사용
   - 질문 목록은 맨 아래에 있다.

---

## 1. SG2002 칩 단품 조달

| 조달처 | 품명(페이지 그대로) | 1/5/10개 단가 | MOQ | 재고 | 납기·배송 | 확인 | URL |
|---|---|---|---|---|---|---|---|
| Arace (Milk-V 공식 샘플 채널) | "SOPHON CV1800B / SG2002 / SG2000 chip【5pcs】" 변형 SG2002 | 1개 단위 없음 · 5개 팩 USD 24.99 · 10개 = 팩 2개 (계산값) | 1팩 | **품절** (available:false) | 결제 단계에서 산정 · 재입고일 미확인 | 확인됨 (직접 접속은 429 → 공개 리더 프록시로 공개 상품 JSON 읽음) | https://arace.tech/products/sophon-cv1800b-5pcs |
| Milk-V 공식 Taobao | — | — | — | — | — | 미확인 (로그인 필요) | https://item.taobao.com/item.htm?id=748015537624 |
| Spotpear | "SG2002-5PCS-For-Duo-256M" | 5개 팩 ¥224 | 5개 팩 | **「停产」** | — | 확인됨 | https://www.spotpear.cn/shop/Milk-V-Duo-Chip-CV1800B-SG2000-SG2002-64MB-256MB-512MB-RISC-V/SG2002-5PCS-For-Duo-256M.html |
| AliExpress 재판매자 4곳 | "SOPHON CV1800B / SG2002 / SG2000 Chip【5pcs】" 등 | 목록 카드 USD 73.29~164.99 (어느 변형인지 불명) | — | — | — | 카드 가격만 확인, 상세는 CAPTCHA로 미확인 | 예: https://www.aliexpress.us/item/3256812718931893.html |
| LCSC / szlcsc | 해당 칩 없음 (Sensata IPSS-G2002 압력센서만 나옴) | — | — | — | — | 확인됨 (없음) | https://www.lcsc.com/search?q=SG2002 |
| Digi-Key | 없음 | — | — | — | — | 확인됨 (없음) | https://www.digikey.com/en/products/result?keywords=SG2002 |
| Mouser / Arrow | — | — | — | — | — | 미확인 (Access Denied) | — |
| Findchips / Octopart | Sophgo 항목 없음 (Authorized 0, Independent 0) | — | — | — | — | 확인됨 (없음) | https://www.findchips.com/search/sg2002 |
| Sipeed | 칩 단품 판매 안내 없음 (보드만) | — | — | — | — | 확인됨 | https://wiki.sipeed.com/hardware/en/lichee/RV_Nano/1_intro.html |

- **Milk-V 공식 문구:**
  - 「Milk-V is the Authorised Global Distributor of the SG2002 chips」 · 대량은 「contact Milk-V Sales Team」. 가격·MOQ는 공개되지 않았다. (https://milkv.io/docs/duo/getting-started/duo256m)
  - 칩 페이지 https://milkv.io/chips 에는 「Buy Samples」(Taobao·Arace), 「Large-scale Supply」가 있다.
  - 같은 페이지에 SG2002 호환 품번으로 CV1812C-PA, CV1811C-A, CV1810C-A가 나온다. 이들의 조달성은 **미조사**다.
- **정식 주문 코드:** 「SG2002」 외에 접미사가 붙은 MPN은 찾지 못했다 (미확인).
- **오래된 가격:** 2024년 CNX 기사의 「$5/개, 5개 $25」는 오래된 값이라 쓰지 않는다.
- **JLCPCB:** 4개 항목이 있다(C9900114545, C9900117139, C9900248086 「SOPHON SG2002 QFN-88_L9.0-W9.0-P0.35-TL-EP6.5」, C9900312128). 모두 브랜드가 "JLCPCB Assembly"이고 재고 0이며 「no longer manufactured」로 표시된다.
  - 이 항목은 고객이 맡긴 부품을 등록한 것이다. 페이지의 0.0398달러 등의 가격은 칩 가격이 아니다.
  - SOPHGO 정식 브랜드로 등록된 품목은 CV1835/CV1838/CV180ZB/CV1843H-P뿐이다.
- **PCBWay:** 공개 부품 라이브러리 검색 경로를 찾지 못했다(판단 불가). 턴키가 어렵다는 것은 공급 유통사에 칩이 없다는 점에서 나온 **추정**이다.
- **SG2000 (512MB, LFBGA 205핀 10×10mm):**
  - Arace 5개 팩 USD 29.99, 품절
  - Spotpear ¥307, 「停产」
  - 결론은 SG2002와 같다.

## 2. 공식 문서·참고 보드

### 문서 (공식 = Sophgo GitHub, 라이선스 BSD 2-Clause "Copyright (c) 2023, Sophgo Technologies")

| 문서 | 리비전/날짜 | sha256 | 공식/미러 | URL |
|---|---|---|---|---|
| SG2002 TRM (영) 841쪽 | **v1.02, 2025-02-27** | 26ed9508ab701ba89226f2a74b0a1faa355cba251695233b7a89c2a2a21bda00 | 공식 | https://github.com/sophgo/sophgo-doc/releases/download/sg2002-trm-v1.02/sg2002_trm_en_v1.02.pdf |
| SG2002 TRM (중) | v1.02, 2025-02-27 | 5381ffcfd344810db122544a004b49b4a207c2562c6033a841f2d686d7fc70f2 | 공식 | 같은 릴리스 sg2002_trm_cn_v1.02.pdf |
| TRM 이전판 | v1.01 2024-07-05 · v1.0 2024-06-17 · v1.0-beta 2024-02-27 · v1.0-alpha 2023-12-04 | 미계산 | 공식 | https://github.com/sophgo/sophgo-doc/releases |
| SG2002 Preliminary Datasheet (영, docx) | **1.0-alpha, 2023-12-15** (이후 판 없음, 미확인) | 59b537396a7fd280a7a7525f713b75a574d1b32f1bf057c788b12b6a6f2418d0 | 공식 | https://github.com/sophgo/sophgo-hardware/blob/master/SG200X/04_SG2002/01_SG2002_Datasheet/01_SG2002_Datasheet_V1.0_EN.docx |
| 같은 문서 (중, docx) | 1.0-alpha | cbe115b6bf8511621a93fb1e9f00d5a917a9163fbdde3c95b951c33f8d3f3c9e | 공식 | 같은 폴더 _CN.docx |
| 같은 문서 (중, PDF) | 1.0-alpha | a6fa64a1e4e91b04d32331b20e47c9fe03450eb1274c8eae22ea37e6f7e6d072 | 미러 (Sipeed) | https://cn.dl.sipeed.com/fileList/LICHEE/LicheeRV_Nano/07_Datasheet/SG2002_Preliminary_Datasheet_V1.0-alpha_CN.pdf |
| HW Design User Guide (영, docx) | V1.0 (1.0-alpha) 2023-12-16 | 9774fd0dd64b6da6a0ba1dfb560851f707f9745e84750c59b94748377b0e9655 | 공식 | sophgo-hardware …/04_SG2002/02_SG2002_Hardware_Design_User_Guide/02_SG2002_Hardware_Design_User_Guide_EN.docx |
| PINOUT xlsx (중) | V0.1 2023-12-11 "Preliminary release" | a20e1d2f02b0350a333ff16538cc59c13372b88c8a96f9737a3ef4f5ff57c148 | 공식 | …/04_SG2002/04_SG2002_PINOUT.xlsx |
| QFN_38 GPIO List xlsx | 수정일 2023-12-19 | 8a1e0b26797a908fbd36f543f4893a1901436a8070b2b4974822626f6a2b1043 | 공식 | …/04_SG2002/05_SG2002_QFN_38_GPIO_List.xlsx |
| PCB 풋프린트 Allegro qfn88_9d0x9d0_0d35_e.dra | 미확인 | eb3585666d5992fff7b2ad3a5136e276bbb283d4686ae697b5d1bfd8b1b81757 | 공식 | …/04_SG2002/11_SG2002_PCB_Package/ |
| 레퍼런스 2층 SCH PDF (+DSN, brd) | 파일명 V13 20230323 · 도면 2023-12-13 | 733b2e42d59d577632bab3d7db101c3be2a60e475d0a53e2dfda381cf7058ace | 공식 | …/04_SG2002/06_SG2002_38_2L_SCH&PCB/ |
| 레퍼런스 4층 SCH PDF (+DSN, brd) | V1.3 20230301 | bf902176ce0f6ba17797d72313839aeb83e78fe5c451d6b46559d2008f50edb2 | 공식 | …/04_SG2002/07_SG2002_38_4L_SCH&PCB/ |
| 4L 38×38mm Layout 가이드 pptx (중), OrCAD 심볼 OLB, HDG 중문판 | 미확인 | 미다운로드 | 공식 | …/04_SG2002/ |

**sophgo-hardware SG200X 커밋:** 2023-12-27 "add SG200X hardware resources", 2024-07-09 "Upload EN version".
**데이터시트 상태:** 공식 데이터시트는 「Preliminary 1.0-alpha」 docx뿐이다. 공식 PDF는 없고 미러에만 있다. Sophgo 웹사이트에 더 새로운 판이 있는지는 **미확인**이다.

### 데이터시트 핵심값 (확인됨, 원문 기준)

| 항목 | 값 | 출처 |
|---|---|---|
| 패키지 | QFN 9×9×0.9mm, 0.35mm 피치, 88핀. 노출 패드 6.0×6.0mm는 풋프린트 이름 기준 추정(미확인). JLC 항목명에는 EP6.5로 나옴 | TRM v1.02 인쇄 p20 / DS p20 |
| 내장 DRAM | DDR3 16bit ×1, 최대 1866Mbps, 2Gbit (256MB) | TRM 인쇄 p10 / DS p13 |
| 전원 레일 (Typ) | VDDC 0.9V(0.81–0.99) · VDDC_RTC 0.9(내부 LDO) · VDD18A_AUD/USB_PLL_ETH/MIPI 1.8 · VDD33A_ETH_USB 3.3 · VDDIO_SD0_EMMC/SD1 1.8 또는 3.0/3.3 · VDDIO_RTC 1.8 · VDDQ/VDDQ_DRAM 1.35(DDR3L) | DS Table 2-7 p30 |
| MIPI CSI | 영상 입력 2개 동시 (mipi 2L + 1L) | TRM 2.3.4 인쇄 p7 / DS 1.2.5 p10 |
| 동작 온도 | 주변 Tamb −30~70°C, 권장 Tj −30~85(105)°C | DS Table 2-5 p26 |
| 열저항 (JEDEC 2s2p) | θJA 20.3/15.9/14.8 °C/W (0/1/2 m/s), θJC 6.9 | DS Table 2-4 p26 |

### 참고 보드

| 보드 | SoC | 회로도 | 레이아웃 원본 | BOM | 라이선스 | URL |
|---|---|---|---|---|---|---|
| Milk-V Duo 256M | SG2002 | 공개 duo-256m-v1.01-schematic.pdf (도면 V1.0 2024-01-02) sha256 65135f0d556b4d321b2a4b02f100e2032d2ee39bfaf4fc07d5e8cfe63512eaa7 | **미공개** (같은 폴더의 WDMB-0006A-V01.brd는 Sophgo 4층 레퍼런스) | 미공개 | **명시 없음** (LICENSE 파일 없음) | https://github.com/milkv-duo/duo-files/tree/main/duo-256M |
| Milk-V Duo S (참고) | SG2000 | 공개 duo_s_SCH_v1.1.pdf sha256 75ea3082a96903e23c643e60b1399c45d8eebac70ec14544a25b834d34513c83 | **미공개** (외형 DXF·STEP만 공개) | 미공개 | 명시 없음 | https://github.com/milkv-duo/duo-files/tree/main/duo-s |
| Sipeed LicheeRV Nano | SG2002 | 공개 70405 (sha256 b09ec99069e7f696498b3501785f5296fd0ecaed6d1895d16de2c2e057c2fd19) · 70415 · 70418 (7fdc7cbcda36a676ef73e3525f61e9ddec7507cca76828490225143696284efe) | **미공개**. 공개된 것은 코어보드 풋프린트(KiCad, JLCEDA)·치수·STEP | iBOM rar (열지 않음) | 명시 없음 (©深圳矽速科技 문구만) | https://cn.dl.sipeed.com/shareURL/LICHEE/LicheeRV_Nano |

→ 레이아웃 원본으로 쓸 수 있는 것은 **Sophgo 레퍼런스(BSD-2-Clause, OrCAD/Allegro)** 뿐이다. 참고 보드 회로도는 라이선스가 명시되지 않아 참고용으로만 쓴다.

## 3. SDK·커널·NPU 도구

| 저장소 | 최신 릴리스/날짜 | 최근 커밋 | 커널 | Buildroot | 툴체인 | 상태 | URL |
|---|---|---|---|---|---|---|---|
| milkv-duo/duo-buildroot-sdk (V1) | v1.1.4 / 2024-11-22 | develop 2026-11-06 (봇 동기화) | 5.10.4 | 2021.05 | RISC-V musl GCC 10.2.0 | 정체 (최근 12개월 병합 PR 0) · ARM 대상 없음 | https://github.com/milkv-duo/duo-buildroot-sdk |
| milkv-duo/duo-buildroot-sdk-v2 | v2.0.1 / 2025-05-30 | main 2025-11-04 · develop 2025-12-30 | 5.10.4 | 2025.02 | RISC-V musl/glibc GCC 10.2.0 · ARM64 Linaro 6.3.1 | 정체 (최근 12개월 병합 PR 0) · `sg2002_milkv_duo256m_glibc_arm64_sd` 있음 | https://github.com/milkv-duo/duo-buildroot-sdk-v2 |
| sophgo/sophpi (manifest) | 태그 없음 | sg200x-evb 2026-11-11 (주간 rls) | 5.10.4 (sophgo/linux_5.10 sg200x-dev 2026-10-28) | 2021.05 | GCC 10.2.0 / Linaro 6.3.1 | 벤더가 일방향 공개 (이슈 응답 사실상 없음) | https://github.com/sophgo/sophpi |
| sipeed/LicheeRV-Nano-Build | 20261109 / 2026-11-10 | 2026-11-09 | 5.10.4 | 2023.11.2 | RISC-V musl GCC 10.2.0 · ARM 32bit | 가장 활발 (병합 PR 8건, NanoKVM 중심) | https://github.com/sipeed/LicheeRV-Nano-Build |

- 네 저장소 모두 루트에 LICENSE 파일이 없다. 구성요소별 라이선스는 **미조사**다.
- `sophgo/cvi_mmf_sdk`, `sophgo/sg200x-sdk` 저장소는 404다.
- **메인라인 (v7.3 기준, torvalds/linux 각 태그에서 직접 확인):** SG2002는 RISC-V dts 기준으로만 지원된다.
  - 클록·MMC·I2C·SPI v6.10 · pinctrl·DMA v6.12 · SAR ADC v6.13 · 이더넷 v6.15(dts v6.17) · RTC·reset v6.17 · USB v6.18/6.19
  - 보드 dts: LicheeRV Nano B v6.13, Duo256M v7.3
  - **카메라/ISP/영상/NPU 드라이버는 메인라인에 없고 벤더 SDK에만 있다.**
  - ARM64 dts는 SG2000만 있다.
- **tpu-mlir:** v1.30.2 (2026-08-31), master 2026-11-16, BSD-2-Clause. https://github.com/sophgo/tpu-mlir
  - `model_deploy.py --chip cv181x` 지원. Milk-V와 Sipeed MaixCAM 문서가 이 옵션을 쓴다.
  - CV18xx 안내서 기준 입력은 **ONNX·Caffe만** 된다(TFLite 미지원). 양자화는 **BF16과 대칭 INT8**이다. 문서 사이에 표현이 엇갈리는 부분이 있어 실측이 필요하다.
  - 예시: https://github.com/sophgo/tpu-mlir/blob/master/docs/quick_start/source_en/Appx.02_cv18xx_guide.rst
- **런타임:**
  - sophgo/cviruntime: 릴리스 없음, 주간 동기화
  - sophgo/tdl_sdk: v2.3, 2025-10-29, CV181X 지원 명시, BSD-2-Clause, README는 중국어
  - Milk-V가 재배포한 tpu-sdk/tdl-sdk는 2024-05 이후 갱신이 없다.
- **예제 문서:**
  - https://milkv.io/docs/duo/application-development/tpu/tpu-introduction
  - https://milkv.io/docs/duo/application-development/tdl-sdk/tdl-sdk-yolov8 (yolo11·yolo12 페이지도 있음)
  - https://wiki.sipeed.com/maixpy/doc/en/ai_model_converter/maixcam.html
- **위험 (근거 있음):**
  - 커널 5.10.4 고정, ARM 툴체인 GCC 6.3.1 (2017)
  - Milk-V 저장소 유지보수 정체
  - 중국어 문서 비중이 높음
  - SG2002 ARM 코어 지원이 SDK마다 다름 (V1 없음, Sipeed는 32bit)

## 4. 카메라 센서와 IQ 튜닝 파일

- **센서 드라이버 수 (SG2002 계열 대상 디렉터리):**
  - Milk-V v2 `cvi_mpi/component/isp/sensor/cv181x`: 101개
  - Sophgo SensorSupportList sg200x-dev: 117개
  - Sipeed: 85개
  - 근거: https://github.com/milkv-duo/duo-buildroot-sdk-v2/tree/main/cvi_mpi/component/isp/sensor/cv181x · https://github.com/sophgo/SensorSupportList/tree/sg200x-dev/sensor
- **IQ 파일 (드라이버가 있다고 IQ가 있는 것은 아님):**

| 센서 | 해상도 (Sophgo 지원목록) | IQ 파일 | 위치 |
|---|---|---|---|
| GC4653 | 2560×1440 MIPI | 있음 (sdr, sdr_ir) · Sipeed 보드 기본 | SDK `isp_tuning/cv181x/src` |
| OS04A10 | 2688×1520 MIPI/LVDS | 있음 (sdr, wdr) | SDK |
| OS04C10 | 2688×1520 MIPI | 있음 (sdr, wdr) | SDK |
| SC2336 | 미확인 (SC2336P는 1080p) | 있음 (sdr) | SDK |
| IMX307 | 1937×1097 MIPI/LVDS | 있음 (sdr, wdr) | SDK |
| GC2083 | 1920×1080 MIPI/DVP | 있음 — Milk-V rootfs에만 (Duo 256M 기본) | duo-buildroot-sdk-v2 `device/generic/rootfs_overlay/common/mnt/cfg/param` |
| SC035HGS | 640×480 글로벌셔터 | 있음 — Milk-V rootfs에만. **CV180ZB용 튜닝**이라 SG2002에 그대로 써도 되는지 미확인 | 같은 위치 |
| OV5647 | 지원목록에 없음 | 있음 — Milk-V rootfs에만 (어느 칩에서 튜닝했는지 미확인) | 같은 위치 |
| GC02M1, OV2685 | 1600×1200 / — | 있음 — Sipeed에만 | LicheeRV-Nano-Build `buildroot/board/cvitek/SG200X/overlay/mnt/cfg/param` |

- **센서 모듈 소량 조달:**
  - 1/5/10개 수량별 단가는 공개된 곳이 **없다**.
  - 재고 수량은 "In Stock" 표시 외에는 미확인이다.

| 모듈 | 센서 | 커넥터 | 판매처·단가 | 확인 |
|---|---|---|---|---|
| Milk-V CAM-GC2083 | GC2083 2MP | 16P 0.5mm, MIPI 2-lane | Arace USD 3.99 판매 중 · Spotpear USD 8.59 In Stock | 확인됨 (https://arace.tech/products/milk-v-cam-gc2083 · https://spotpear.com/shop/Milk-V-Duo-Camera-GC2083.html) |
| LicheeRV Nano GC4653 카메라 | GC4653 | 22P 4-lane, 피치 미확인 | Spotpear USD 12.9(?) — 카메라 가격인지 불명 | 미확인 |
| RPi Camera (B) | OV5647 | 15P 1.0mm (Duo S J2에 맞음) | Waveshare USD 15.99 | 단가만 확인됨 (https://www.waveshare.com/rpi-camera-b.htm) |
| OS04A10 / SC2336 / IMX307 / OS04C10 단품 모듈 | — | — | 판매처 못 찾음 (OS04A10은 MaixCAM Pro 묶음만) | 미확인 |
| 센서 칩 단품 (LCSC) | — | — | LCSC 접근 거부 | 미확인 |

→ 현재 **"IQ 파일 있음 + 모듈 조달 확인"**을 함께 만족하는 것은 **GC2083 (CAM-GC2083)** 하나다. GC4653은 IQ 파일은 SDK 정식이지만 모듈 조달이 일부만 확인됐다.

## 5. Allwinner V851s / V851SE 비교

| 항목 | SG2002 | V851s / V851SE | 근거 |
|---|---|---|---|
| 칩 조달 1/10개 | 공식 채널 품절·단종 표시·유통사 없음 | **LCSC 1개부터**. V851s: 1개 $15.46, 10개 $13.85, 재고 175 · V851SE: 1개 $12.42, 10개 $10.61, 재고 44 (5개 단가는 10개 가격 구간 아래라 1개 단가 적용) | 확인됨 https://www.lcsc.com/product-detail/C5365286.html , LCSC C5332073 |
| JLC/PCBWay 조립 | JLC 고객 등록 항목만 (재고 0) · PCBWay 미확인 | JLCPCB 라이브러리 등록 (Extended, MSL3) · PCBWay 미조사 | https://jlcpcb.com/partdetail/V851s/C5365286 |
| 납기 | 미확인 | 미확인 | — |
| 패키지 | QFN88 9×9mm, 0.35mm | QFN88 9×9mm, 0.35mm | 각 데이터시트 |
| 내장 DRAM | DDR3 256MB | **DDR2 64MB** (V851s3만 DDR3L 128MB — 단품 판매처 없음) | V851SX DS Rev1.2 |
| CPU | C906 RISC-V / A53 (SDK마다 지원 다름) | Cortex-A7 900MHz + XuanTie E907 600MHz | V851SX DS Rev1.2 (TinyVision의 "1200MHz"는 보드 측 주장) |
| NPU | tpu-mlir 공개 (cv181x) | 최대 0.5 TOPS. 변환은 Acuity Toolkit — **공개 다운로드 없음**, 입수 경로 미확인 | TinyVision docs |
| ISP / CSI | ISP · MIPI 2L+1L | ISP 1개 최대 2560×1440 · MIPI 4-lane 1개 또는 2-lane 2개 | V851SX DS |
| 이더넷 | MAC+PHY 내장 (레일 VDD33A_ETH_USB) | V851s: RMII (외부 PHY) · V851SE: 100M EPHY 내장 | V851SX DS |
| 데이터시트 | 공식 GitHub 공개 (Preliminary) | Brief만 LCSC에 공개 · 전체 DS(1194쪽 Rev 1.2, 2023-07-14)는 **「Confidential」 미러** (TinyVision 저장소) | sha256 d7bcdee2de8728fe92ae71a81264033ec8c98428ad435261fa642b186294e260 |
| HW 설계 가이드 | 공개 | 찾지 못함 | — |
| 레퍼런스/참고 보드 원본 | Sophgo SCH/PCB (BSD-2) · 보드 레이아웃 미공개 | Allwinner 레퍼런스 DSN/brd 미러 (재배포 라이선스 미확인) · **Yuzukilizard LCEDA Pro + Altium 원본, CERN-OHL-S v2** (미러 SoCXin/V851S, 원본 저장소 404) · TinyVision Gerber/BOM 공개 (EDA 원본 없음, HW 라이선스 불명확) | https://github.com/SoCXin/V851S · https://github.com/YuzukiHD/TinyVision |
| SDK 입수 | 공개 git | tina-v853-open: **AWOL 포럼 LV2 계정 필요** (https://docs.aw-ol.com/v853/study/study_3getsdktoc/). 오늘은 sdk.aw-ol.com 403, 포럼 점검 중 | 확인됨 |
| 벤더 커널 | 5.10.4 | 4.9 / 5.4 (카메라·NPU는 4.9.191). 커뮤니티 5.15/6.1 있음 | 확인됨 |
| 메인라인 | 기본 주변장치 지원 (v6.10~v7.3) | 사실상 없음 (PPU 전원 도메인 드라이버·pinctrl 바인딩만, dtsi/CCU/pinctrl 드라이버 없음) | torvalds/linux master |
| 센서·IQ | IQ 5종 (SDK) + rootfs 추가분 | 드라이버 약 100개 · IQ (미러 lindenis-v853-external 2023-01): gc2053, gc4663, sc4336, imx307 · 공식 ISP 튜닝 문서는 "작성 중" | https://github.com/lindenis-org/lindenis-v853-external |

**V851 문서 sha256 (내려받은 사본, 공식 공개본 아님):**
- V851S Brief (LCSC): a3747691ff37d8bdbf9cd2f4b0e107d6b456eb14363273f95ade3600119c55f9
- V851S Brief (TinyVision 미러): c749d419f89dbd8c51c2928fc76fb97e2c30856e499403d940d81df47ca4552e
- 핀아웃:
  - V851S&V851S3 PINOUT V1.1: 1e01575727e462f343a3e49c4059f8be491de5b473caa7706ef84df6b83075b8
  - V851SE PINOUT V1.0: aa19e631c7fda0cd1c55039c71dcf569201f49182a9f2b31d5ce7ebb52ff5a2a
- Allwinner 레퍼런스 원본:
  - DSN (V1_0 20220325): 57fbfc6700f707ea42adcffe06e9659550e7f05704ea64de3469e4d0a513b562
  - brd: 467fdfd7c1bb2b1d6b58247b0832ee2767354705f583335cd6730b3f3396049f
- TinyVision:
  - SCH: 9396abe2ca5a72e9a397bdc2f7a022e1472bfdf51458e25c06ebeb2d8e59e687
  - BOM: 945b3fbe1de0bd59e59436c81680f1f49c9673d5655c60a8916318debdf54733
- Yuzukilizard:
  - SCH: 74e8a186856dbb282395841a13e16af9671b1653f1d3ca84084305b55bc05828
  - LCEDA Pro: 2a4a0d2467e90bded2f313680c7bde4f83e23a3d15184e4f6475850d0dd4af27
  - Altium: 9df66c137d5bc214cab6634d11cf9eedb2ed5e0d62cdd1fba7fbba1fb1f2d1bd
  - LICENSE: 80b3c74490022dc3f5dc9b8c22aa6808744d2f84e3d8cae76a78702010a3139b

**V851 판단 근거 (근거 있는 것만):**
- **강점:** 칩 조달과 조립 라이브러리, CERN-OHL-S 원본 보드 프로젝트가 있다.
- **약점:** 64MB DDR2(모델·영상 버퍼 여유가 적다 — 실제 충분한지는 감지 모델이 정해진 뒤 판단), SDK·NPU 도구 입수에 계정이나 고객 등록이 필요하다, 데이터시트가 비공개 성격이다, 메인라인 미지원이다.

## 확인 못 한 것 (전체)

- **SG2002 조달:**
  - Arace 재입고 일정
  - Mouser·Arrow 직접 재고
  - Taobao·AliExpress 상세 페이지
  - 정식 주문 코드(MPN 접미사)
  - Milk-V 대량 조건
  - 공식 EOL 여부
  - 호환 품번 CV1812C-PA 등의 조달성
  - PCBWay 부품 라이브러리
- **문서:**
  - 1.0-alpha 이후 데이터시트가 있는지
  - HDG 중문판, Layout 가이드, OLB의 리비전과 해시
  - 패키지 공차와 E-pad 치수: 6.0(풋프린트 이름) vs 6.5(JLC 항목명) 불일치 — 데이터시트 도면에서 확인 필요
  - 참고 보드 하드웨어 라이선스
- **SDK:**
  - 구성요소별 라이선스
  - ARM 타깃 실제 부팅 성공 여부
  - tpu-mlir의 TFLite/PyTorch 직접 사용 실측
- **센서:**
  - 수량별 단가
  - GC4653 카메라 단품 가격과 22P 피치
  - SC035HGS·OV5647 IQ의 튜닝 대상 칩
  - IQ 보유 센서 대부분의 모듈 판매처
- **V851:**
  - 납기, Mouser, PCBWay
  - V851s3 단품 판매처
  - HW 설계 가이드
  - 레퍼런스·TigerISP 재배포 라이선스
  - Tina SDK 최근 업데이트일
  - Acuity 입수 경로와 버전
  - NPU IP 이름
  - GC2083 IQ 파일
- **증거 파일 보관:** 내려받은 데이터시트·회로도는 세션 임시 폴더에만 있다(재부팅 시 사라질 수 있음). 저장소 보관(`hardware/datasheets`)은 배정 범위 밖이라 하지 않았다. 필요하면 별도로 배정받아야 한다.

## lead 문서에 대한 제안 (D-001-soc.md · product-brief.md — 수정하지 않음)

1. D-001 「후보와 판단」의 SG2002 행에 다음을 덧붙인다:
   - 「DDR3 256MB 내장 확인(TRM v1.02)」
   - 「단품 조달 불확실: 공식 샘플 품절, 리셀러 단종 표시, 정규 유통 없음 (2026-11-26)」
   - 「벤더 커널 5.10.4 고정, 메인라인에 카메라·NPU 없음」
2. V851s 행의 「64MB급」을 「V851s/SE DDR2 64MB, V851s3 DDR3L 128MB(단품 미유통)」로 정정한다. 「SDK 계정(LV2) 필요, NPU 변환 도구 비공개」를 추가한다.
3. product-brief 「OS」 항목의 `duo-buildroot-sdk 계열`에, 유지보수 상태를 근거로 Sipeed LicheeRV-Nano-Build 또는 sophgo/sophpi 도 후보로 적는다(선택은 사용자/lead).
4. 「카메라 센서」 미정 항목에 「IQ 파일 보유 센서: GC4653·OS04A10·OS04C10·SC2336·IMX307(SDK), GC2083·SC035HGS·OV5647(Milk-V rootfs), GC02M1·OV2685(Sipeed)」를 후보 목록으로 남긴다.

## 사용자에게 물을 질문

1. **SG2002 조달 경로:** Milk-V 영업팀에 SG2002 재고·EOL·1~10개 조건을 문의해도 되는가? 외부 연락이므로 별도 승인이 필요하다. 누가 어떤 창구로 할지도 정해 주어야 한다.
2. **SG2002가 계속 불확실하면 어느 경로로 갈 것인가?**
   - (A) 문의 회신을 기다린다
   - (B) V851s/V851SE로 전환한다
   - (C) SG2002 모듈(예: LicheeRV Nano 코어보드)을 얹는 캐리어 보드로 간다 — "SoC 직접 탑재" 결정을 바꾸는 것이다
   - (D) AliExpress 재판매 칩을 진위 위험을 감수하고 쓴다
3. **조립 방식:** 칩을 직접 사서 PCBWay에 맡기는 위탁(consigned/kitted) 조립을 허용하는가, 턴키만 허용하는가?
4. **벤더 커널:** 벤더 커널 5.10(SG2002) 또는 4.9(V851, 카메라·NPU 사용 시)에 고정되는 것을 PoC에서 받아들이는가?
5. **V851 전환 시 계정:** AWOL 포럼 계정 가입(외부 계정)과, NPU 도구를 받기 위한 Allwinner 고객 등록을 진행해도 되는가?
6. **감지 요구 (미정값):** 감지 대상, 거리·화각, 주야간(IR) 여부를 알려 달라. 이 값으로 센서(GC2083 2MP / GC4653 4MP / IR 지원 여부)와 메모리 요구(V851 64MB로 충분한지)가 정해진다.
7. **수량·예산 (미정값):** 제조 수량(1/5/10)과 총 PoC 비용 한도를 알려 달라. 칩 팩 단위(5개)와 MOQ 판단에 필요하다.
