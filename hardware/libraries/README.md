# OpenHW KiCad 프로젝트 라이브러리 (L-001)

- 배정: orch t18r L-001 (README 단계 4 준비) + G-001 (KiCad GUI로 보이게 작업) · 작성: schematic · 레인 `t-20261126-161205-dcb9` · 2026-11-26
- 도구: KiCad 10.0.8 (`C:/Users/gh/AppData/Local/Programs/KiCad/10.0`)
- 계약 기준: `hardware/schematic/hw-fw-contract.md` v1 (C-001 레인 `t-20261126-155208-d030`, 커밋 `8613910`)
- **원칙:** KiCad 공식 라이브러리에 있는 부품은 새로 만들지 않고 아래 표에 「공식 참조」로 적는다.

## 파일

| 파일 | 내용 |
|---|---|
| `openhw-libs.kicad_pro`, `sym-lib-table`, `fp-lib-table` | GUI로 라이브러리를 열기 위한 프로젝트. 라이브러리 이름은 `openhw`, 경로는 `${KIPRJMOD}` 기준 |
| `openhw.kicad_sym` | 새 심벌 2개: `AP1511B`, `LTR-329ALS-01` |
| `openhw.pretty/` | 새 풋프린트 2개(LTR-329, VSMA1085600)와 파생 풋프린트 3개(BTB A/B, M12 홀더) |
| `licenses/Apache-2.0.txt` | 파생 풋프린트의 원저작물 라이선스 전문 (Seeed와 Antmicro 저장소의 LICENSE가 같은 Apache-2.0 본문) |

C-002 회로도·PCB 프로젝트에서는 이 폴더의 `openhw.kicad_sym`과 `openhw.pretty`를 프로젝트 라이브러리 테이블에 `openhw`라는 이름으로 등록한다.

## 부품별 결정

| 부품 (계약 역할) | 심벌 | 풋프린트 | 구분 | 데이터시트 (리비전 · 확인일 2026-11-26) |
|---|---|---|---|---|
| TI **DRV8837DSGR** (ICR 1안, 계약 C13) | `Driver_Motor:DRV8837` (공식) | `Package_SON:Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` (공식) | **공식 참조** | TI SLVSBA4F (2012-06, rev. 2021-04) https://www.ti.com/lit/ds/symlink/drv8837.pdf · sha256 3092ce1a…dfc2 |
| UMW **AP1511B** (ICR 차선) | `openhw:AP1511B` (**신규**) | `Package_TO_SOT_SMD:SOT-23-6` (공식) | 심벌만 신규 | UMW 「AP1511」 Jul.2025, LCSC C347457 https://datasheet.lcsc.com/datasheet/pdf/e09a6a93d89c64626cab32bc2d1d53e8.pdf · sha256 5e64bda0…f052. **Diodes AP1511과는 다른 부품** |
| Diodes **AL8860MP-13** (IR LED 드라이버) | `Driver_LED:AL8860MP` (공식) | `Package_SO:MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm` (공식) | **공식 참조** | Diodes AL8860 DS39014 Rev. 8-2 (April 2026) https://www.diodes.com/assets/Datasheets/AL8860.pdf · sha256 a0c8c9a6…65f0 |
| Vishay **VSMA1085600** (850nm IR LED) | `Device:LED` (공식, 1 = K, 2 = A) | `openhw:Vishay_VSMA1085600_3.4x3.4mm` (**신규**) | 풋프린트만 신규 | Vishay 문서 80298 Rev. 1.4 (2022-07-08) https://www.vishay.com/docs/80298/vsma1085600.pdf · sha256 bb97a209…b748 · 권장 풋프린트 도면 6.550-5366.9-3 |
| Lite-On **LTR-329ALS-01** (조도) | `openhw:LTR-329ALS-01` (**신규**) | `openhw:Lite-On_LTR-329ALS-01_2x2mm_P1.2mm` (**신규**) | 신규 | DS86-2014-0006 Rev. C (2020-03-14, 파일명 V1.5). 제조사 사이트는 자동 접근을 거부해서 Adafruit 미러로 받았다: https://cdn-learn.adafruit.com/assets/assets/000/115/507/original/LTR-329ALS-01_DS_V1.5.PDF · sha256 72948664…8b22 |
| Commonlands **CLA216-ICR** M12 홀더 | 없음 (기구 부품) — 회로도에는 `Mechanical:MountingHole`류나 풋프린트만 쓰는 심벌로 넣는다(C-002) | `openhw:M12_Holder_20mm_CLA216-ICR` (**파생**) | Antmicro 파생 | 제품 페이지 https://ja.commonlands.com/products/ir-cut-off-filter-switcher-m12-cla216 (V-001 인용: 20Ω 코일, 2핀 1.25mm JST). STP/도면은 미열람(DocSend) |
| FFC 1.0mm 10P (계약 12절) — 대표 MPN **TE 1-84953-0** | `Connector_Generic:Conn_01x10` (공식) | `Connector_FFC-FPC:TE_1-84953-0_1x10-1MP_P1.0mm_Horizontal` (공식) | **공식 참조** | TE 84953 고객 도면 (공식 풋프린트 설명의 URL) http://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=84953&DocType=Customer+Drawing&DocLang=English&DocFormat=pdf&PartCntxt=84953-4 — 미열람 |
| SUNGTECH **ST-BTB-058060-A** (캐리어 쪽, 코어 J2와 짝) | `Connector_Generic:Conn_02x30_Odd_Even` (공식) | `openhw:BTB_ST-BTB-058060-A_2x30_P0.5mm` (**파생**) | Seeed B301 파생 (O-12) | SUNGTECH 데이터시트는 R-004를 기다리는 중 |
| SUNGTECH **ST-BTB-058060-B** (전면 쪽, 코어 J1과 짝) | `Connector_Generic:Conn_02x30_Odd_Even` (공식) | `openhw:BTB_ST-BTB-058060-B_2x30_P0.5mm` (**파생**) | Seeed S401 파생 (O-12) | 위와 같음 |

## 핀 ↔ 패키지 ↔ 패드 대조

### DRV8837 (공식 심벌 핀 = SLVSBA4F 「Pin Functions」 = 공식 풋프린트 패드)
| 패드 | 데이터시트 | 공식 심벌 | 일치 |
|---|---|---|---|
| 1 | VM | VM (power_in) | ○ |
| 2 | OUT1 | OUT1 | ○ |
| 3 | OUT2 | OUT2 | ○ |
| 4 | GND | GND | ○ |
| 5 | IN2 | IN2 | ○ |
| 6 | IN1 | IN1 | ○ |
| 7 | nSLEEP | ~{SLEEP} | ○ |
| 8 | VCC | VCC | ○ |
| 9 (EP) | Thermal pad (GND) | GND (passive) | ○ |
- **주의:** 공식 풋프린트가 가리키는 3D 모델 `Texas_DSG0008A_….step`은 이 설치본에 **없다**. 같은 치수의 `Package_SON.3dshapes/WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.step`은 있으므로, C-002에서 풋프린트 속성의 3D 경로를 이것으로 바꾼다.

### AL8860MP (공식 심벌 핀 = DS39014 「Pin Descriptions」 MSOP-8EP 열)
| 패드 | 데이터시트 | 공식 심벌 | 일치 |
|---|---|---|---|
| 1 | SET | SET | ○ |
| 2, 3 | GND | GND | ○ |
| 4 | CTRL | CTRL | ○ |
| 5, 6 | SW | SW | ○ |
| 7 | N/C | NC | ○ |
| 8 | VIN | VIN | ○ |
| EP (9) | Exposed pad → GND, 「Should not be used as electrical ground conduction path」 | GND (passive) | ○ |
- **CTRL (원문):** 「Leave floating for normal operation · Drive to voltage below 0.2V to turn off output current · Drive with PWM signal from open-collector or open-drain transistor」. 계약 C8의 N-MOSFET 끌어내림 방식과 맞는다.

### AP1511B (`openhw:AP1511B` = UMW 「4.Pinning Information」 1511B 열)
| 패드 | 데이터시트 | 신규 심벌 (전기 유형) | 일치 |
|---|---|---|---|
| 1 | CE — External capacitor (one-shot) | CE (passive) | ○ |
| 2 | GND | GND (power_in) | ○ |
| 3 | FBC — Forward/Backward control | FBC (input) | ○ |
| 4 | OUT1 | OUT1 (output) | ○ |
| 5 | VDD | VDD (power_in) | ○ |
| 6 | OUT2 | OUT2 (output) | ○ |
- **패키지:** SOT-23-6, 1번 핀은 공식 풋프린트 규칙을 따른다.
- **입력 방식:** AP1511B는 **한 선 제어(FBC) + one-shot**이다. 계약의 「두 선 IN1/IN2」와 다르므로, 차선으로 바꿀 때는 GPIO 1개(FBC)만 쓰고 CE에 펄스 폭 커패시터를 단다(V-001: 0.47µF → 약 282ms).

### LTR-329ALS-01 (`openhw:LTR-329ALS-01` = DS86-2014-0006 Rev C 「I/O Pins Configuration Table」 · 「5. Outline Dimensions」)
| 패드 | 데이터시트 | 신규 심벌 | 패드 중심 (mm, 위에서 본 면, y 아래 +) | 일치 |
|---|---|---|---|---|
| 1 | VDD | VDD (power_in) | (−0.60, +0.70) — Pin #1 표시 모서리 | ○ |
| 2 | GND | GND (power_in) | (+0.60, +0.70) | ○ |
| 3 | SDA (open drain I/O) | SDA (bidirectional) | (+0.60, −0.70) | ○ |
| 4 | SCL (open drain input) | SCL (input) | (−0.60, −0.70) | ○ |
- **랜드 (14절 「Recommended Land Pattern」):** 패드 0.70 × 0.60mm 4개, 가로 간격 0.50, 세로 간격 0.80 → 중심 ±0.60 / ±0.70. 스텐실은 랜드와 같은 0.70 × 0.60.
- **전기 (8절):** VDD 2.4~3.6V, **VIO 1.7~3.6V**(Interface Bus Power Supply Voltage), 절대최대 VDD·SDA·SCL 3.8V. 7비트 주소 0x29. INT 핀 없음.

### VSMA1085600 (`Device:LED` + `openhw:Vishay_VSMA1085600_3.4x3.4mm`)
| 패드 | 데이터시트 | 심벌 | 패드 (mm) |
|---|---|---|---|
| 1 | Cathode 스트립 (캐소드 표시 쪽) | K (pin 1) | 마스크 개구 2.8×0.55 @ (0, +1.125) + 구리 2.8×1.9 @ (0, +1.8) |
| 2 | Anode 스트립 | A (pin 2) | 2.8×0.55 @ (0, −1.125) + 구리 2.8×1.9 @ (0, −1.8) |
| 2 | 가운데 패드 (bottom view에서 Anode 화살표가 가리킴 = 방열) | A | 2.8×1.0 @ (0,0) + 구리 H형 (좌우 막대 1.0×5.5 @ ±2.25 + 가운데 띠 3.5×1.0) |
- **근거:** 7쪽 「RECOMMENDED FOOTPRINT」 — Cu area 5.5×5.5, 안쪽 3.5, 사각 2.8 / Solder resist 개구 0.55-1.0-0.55, 전체 2.8 / Stencil 2.6×0.4, 2.6×0.9.
  - 페이스트 여유값으로 스텐실 크기를 맞췄다(바깥 −0.075, 가운데 −0.05).
  - 구리만 있는 확장 패드에는 마스크·페이스트가 없다.
- **극성:** 6쪽 bottom view에서 Anode는 왼쪽 스트립과 가운데 패드, Cathode는 오른쪽 스트립이다. top view의 캐소드 표시는 왼쪽 위다. 이를 7쪽 「Component location on pad」(캐소드 표시가 왼쪽 아래)에 맞춰 돌리면 **아래 스트립 = 캐소드**가 된다.
- **방열 (V-001 ⑥):** 가운데 패드가 anode 전위다. 방열 구리를 anode 넷(12V 쪽 LED 직렬의 위쪽)으로 키운다. 다른 넷의 방열면과 붙이지 않는다.

### BTB 60P (파생, A/B 공통 랜드)
- **패드:**
  - 홀수 1~59: y = −2.0 줄, x = −7.25 … +7.25 (0.5 피치)
  - 짝수 2~60: y = +2.0 줄
  - SMD 1.8 × 0.25mm (90° 회전)
  - NPTH Ø0.6 2개: (±8.2, +1.25) — 짝수 줄 쪽으로 치우친 위치결정 구멍
- **A와 B:** 패드·구멍 좌표가 **완전히 같다**. Seeed 원본도 「BTB60-Male-Female-0.5-17.7x4.4mm」 하나를 두 품번에 함께 쓴다.
- **핀 번호 ↔ 넷:** 계약 4절(캐리어 = A)과 5절(전면 = B)에 있다. 짝 사이 홀짝 반전 규칙을 따른다.
- **추출:** KiCad 10.0.8 `pcbnew` 파이썬으로 원본 보드에서 풋프린트를 복제했다.
  - 뒷면에 놓인 S401은 앞면으로 뒤집었다.
  - 회전 0, 원점 (0,0)으로 맞추고 넷을 지웠다.
  - 원본 3D 경로(Seeed 사내 `Y:/01_Cadence_Library/...stp`)는 지웠다.

### M12 홀더 (파생)
- **구멍:** NPTH Ø1.5mm 2개 (±10.0, 0) — 간격 20mm(R-002 O5 출발점과 같음). 원점 = 렌즈 광축 중심.
- **정리:** Antmicro 원본의 장식 그림(User.9 레이어 939줄)과 뒷면에 남은 요소를 지웠다. 「Author: Antmicro / License: Apache-2.0」 문구는 그대로 둔다.
- **미확인:** CLA216-ICR의 실제 구멍 지름·나사 규격·외곽. Commonlands 도면(DocSend)을 아직 열람하지 못했다. 홀더 높이는 R-002 기준 7.6mm.
- **ICR 배선:** 2핀 1.25mm JST 케이블(V-001 인용). 받는 헤더의 계열(GH 등)이 미확인이라 이번 라이브러리에는 넣지 않았다(C-002 전 확인).

## 원점 · 1번 핀 · 실크 · 3D · 높이

| 풋프린트 | 원점 | 1번 핀 / 극성 표시 | 실크 | 3D 모델 경로 | 부품 높이 (M-001b 허용: 캐리어 윗면 ≤6.2, 전면 아랫면 ≤5.2mm) |
|---|---|---|---|---|---|
| `Lite-On_LTR-329ALS-01_2x2mm_P1.2mm` | 패키지 중심 | 1번 = 왼쪽 아래. 실크 점 (−1.35, +1.25), Fab 모서리 사선 | 위·아래 가로선 | **없음** (제조사 STEP 미확보) | 0.70mm (데이터시트) — 전면 윗면 |
| `Vishay_VSMA1085600_3.4x3.4mm` | 패키지 중심 | 1번(K) = 아래 스트립. 실크 점 (−3.2, +2.9), Fab 원 (−1.35, +1.35) | 구리 밖 점만 | **없음** (Vishay STEP 미확보) | 1.795mm — 전면 윗면 |
| `M12_Holder_20mm_CLA216-ICR` | 광축 | — | Antmicro 원본 F.SilkS 1개 | **없음** (원본 `${ANT3DMDL}/Assembled_Lens.step`은 저장소에 없음) | 홀더 7.6mm (R-002) — 전면 윗면 |
| `BTB_ST-BTB-058060-A/B_2x30_P0.5mm` | 커넥터 중심 | 1번 = (−7.25, −2.0). Seeed 원본 실크와 Fab 유지 | 원본 유지 | **없음** — 코어 STEP 안의 `320210641/320210642_Sungtech_…_3D` 모델을 기구가 쓴다(M-001) | 짝 높이: M-001b btb_h 8.0 기본(모델명 「4_0H」와 차이 — R-004로 확정) |
| 공식 `Texas_DSG0008A_WSON-8…` | 공식 | 공식 | 공식 | 공식 경로의 파일이 설치본에 없음 → `${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.step`로 대체 | 약 0.8mm (추정) |
| 공식 `MSOP-8-1EP_3x3mm…` | 공식 | 공식 | 공식 | `${KICAD10_3DMODEL_DIR}/Package_SO.3dshapes/MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm.step` (있음) | 약 1.1mm (추정) |
| 공식 `SOT-23-6` | 공식 | 공식 | 공식 | `${KICAD10_3DMODEL_DIR}/Package_TO_SOT_SMD.3dshapes/SOT-23-6.step` (있음) | 약 1.45mm (추정) |
| 공식 `TE_1-84953-0_…` | 공식 | 공식 | 공식 | `${KICAD10_3DMODEL_DIR}/Connector_FFC-FPC.3dshapes/TE_1-84953-0_1x10-1MP_P1.0mm_Horizontal.step` (있음) | 공식 설명 기준. 정격 전류/핀은 TE 도면 미열람 → **C-002 전 확인** |

- **FFC 대표 MPN을 TE 1-84953-0으로 고른 이유:**
  - KiCad 공식 풋프린트와 3D 모델이 모두 이 설치본에 있다(Molex 200528-0100은 3D가 없다).
  - PCBWay가 부품을 사 오는 유통(Digi-Key·Mouser)에서 다루는 제조사다(R-001).
  - 차선은 JUSHUO AFA07-S10FCA-00(공식 풋프린트·3D 있음, LCSC)이다.

## 라이선스 · 출처 고지 (O-12, Apache-2.0)

| 풋프린트 | 원저작물 | 저장소 · 커밋 | 원본 파일 (sha256) | 라이선스 | 바꾼 것 |
|---|---|---|---|---|---|
| `BTB_ST-BTB-058060-A_2x30_P0.5mm` | Seeed Studio `Connector:BTB60-Male-Female-0.5-17.7x4.4mm` (값 ST-BTB-058060-A) | Seeed-Studio/OSHW-reCamera-Series `f5fcf0abce794806ffbd7a274686f022bb0acd4b` | `hardware/recamera-2002/base/b301-poe/PCB/reCamera 2002 POE Board.kicad_pcb` (b4b974b3…adf1f) | Apache-2.0 — 저장소 LICENSE. 파일에 별도 표기 없음 (V-001 ③) | 앞면·회전 0·원점, 넷과 3D 경로 삭제, 이름과 설명 변경 |
| `BTB_ST-BTB-058060-B_2x30_P0.5mm` | 같은 풋프린트 (값 ST-BTB-058060-B) | 같음 | `hardware/recamera-2002/sensors/s401-gc2053/PCB/reCamera 2002 S4 GC2053 Sensor Board_V1.0_SCH&PCB_250905.kicad_pcb` (783d3aa3…eb2) | 같음 | 뒷면 → 앞면으로 뒤집기, 그 밖은 위와 같음 |
| `M12_Holder_20mm_CLA216-ICR` | Antmicro `antmicro-footprints:Camera_Lens_20mm` | antmicro/ov9281-camera-board `ea69666fa06f66a0691e50eebff9356cc2a08e32` | `ov9281-dual-camera-board.kicad_pcb` (9a73c217…f382) | Apache-2.0 (저장소 LICENSE, 풋프린트 안 「License: Apache-2.0」) | 뒷면 → 앞면, 장식 그림(User.9)과 뒷면 잔여 요소 삭제, 3D 경로 삭제, 이름·설명·참조·값 변경 |

- Apache-2.0 §4에 따라 라이선스 전문을 `licenses/Apache-2.0.txt`에 두고, 바꾼 사실을 각 풋프린트 설명(descr)과 위 표에 적었다.
- 두 원본 저장소에는 NOTICE 파일이 없다(트리 목록 기준).
- CC BY-SA 4.0 표기가 있는 코어 회로도 PDF에서는 아무것도 복제하지 않았다.

## 검사 (kicad-cli 10.0.8, 종료 코드) — verifiable 예

| 명령 | 종료 코드 | 의미 |
|---|---|---|
| `kicad-cli sym export svg -o <tmp> hardware/libraries/openhw.kicad_sym` | 0 | 심벌 2개를 읽고 그림 (파싱 통과) |
| `kicad-cli fp export svg -o <tmp> hardware/libraries/openhw.pretty` | 0 | 풋프린트 5개를 읽고 그림 |
| `kicad-cli sym upgrade --force <사본>/openhw.kicad_sym` | 0 | 현재 형식으로 저장. 원본과 uuid 외 차이 없음 |
| `kicad-cli fp upgrade --force <사본>/openhw.pretty` | 0 | 현재 형식 |

- kicad-cli에는 심벌·풋프린트 규칙 검사(KLC) 명령이 없다. 규칙 검사는 C-002에서 이 부품을 놓은 회로도의 ERC와 PCB DRC 종료 코드로 한다.

## GUI 작업 기록 (G-001) — verifiable 아니오 (사용자 확인용)

| 번호 | 단계 | 스크린샷 | 상태 |
|---|---|---|---|
| 01 | 프로젝트 열기: 창 제목 「openhw-libs — KiCad 10.0」, 상태줄 「프로젝트: C:\workspace_python\OpenHW\.harnes…hardware\libraries\openhw-libs.kicad_pro」, 트리 「openhw-libs.kicad_pro [harness/t-20261126-161205-dcb9]」 | `C:/workspace_python/OpenHW/validation/runtime/kicad-gui/L-001/01-project.png` | 완료 |
| 02 | 심벌 편집기에서 `openhw` 라이브러리 확인 | — | **보류**: 심벌 편집기를 열고 라이브러리를 고르던 중 화면이 잠겼다(「There is no active desktop」, 「screen grab failed」). 화면이 돌아오면 이어서 한다 |
| 03 | 풋프린트 편집기에서 `openhw.pretty` 확인 | — | 보류 (위와 같은 이유) |

- **편집 방식:** 파일을 작성하고 GUI에서 다시 불러온다.
  - 심벌은 텍스트 생성, 풋프린트는 KiCad `pcbnew` 파이썬 API로 만들거나 추출해 저장했다.
  - GUI로는 불러와서 보기만 한다.
  - 실험적 회로도 편집 MCP는 쓰지 않았다(KICAD_MCP_ENABLE_SCH_EDIT=0).
- **첫 실행 설정:** KiCad 첫 실행 마법사를 기본값으로 지났다. 내장 라이브러리를 쓰고, 업데이트 확인은 기본값(켬), 익명 데이터 수집은 끔이다.

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| L1 | ICR 드라이버 라이브러리 | DRV8837은 공식 참조, AP1511B는 심벌만 신규 | 계약 v1 C13에서 DRV8837이 1안이 됐다. L-001 지시서의 AP1511B는 차선으로 남겨 둔다 | — |
| L2 | VSMA1085600 심벌 | 공식 `Device:LED` | 2단자라 공식 심벌로 충분 (K = 1, A = 2) | 전용 심벌 |
| L3 | VSMA 방열 구리 | 패드 번호를 붙인 구리 전용 패드 프리미티브 | 넷이 따라와 DRC가 단락을 잡을 수 있다 | 존(zone)으로 C-002에서 그림 |
| L4 | BTB 풋프린트 | A·B를 이름만 다른 같은 랜드 2개로 둔다 | BOM과 배치에서 품번을 구분한다. 원본도 같은 랜드 | 하나로 합침 |
| L5 | FFC 대표 MPN | TE 1-84953-0 | 공식 풋프린트와 3D가 있고 유통이 넓다 | JUSHUO AFA07-S10FCA-00 |
| L6 | LTR-329 데이터시트 출처 | Adafruit 미러 V1.5 (Rev C 본문) | 제조사 사이트가 자동 접근을 거부한다 | 사람이 Lite-On에서 받아 sha256 대조 |
| L7 | 3D 모델 없는 부품 | 경로를 비워 두고 표에 「없음」 | 제조사 STEP을 받지 못했다. 추정 모델은 만들지 않는다 | 기구(M-001)가 STEP을 구하면 경로 추가 |

## 남은 확인 (C-002 전)
1. SUNGTECH ST-BTB-058060-A/B 데이터시트와 랜드·짝 높이 대조 (R-004)
2. CLA216-ICR 도면: 구멍 지름·나사, ICR 케이블 헤더 계열
3. TE 84953 정격 전류/핀 (12V_IR 1A를 3핀으로 나누는 조건)
4. VSMA1085600·LTR-329 3D 모델

## C-003 수정 (V-003 지적 반영, 2026-11-26)

- **수정 방식:** 스크립트 `tools/c003_libfix.py`로 `.kicad_mod` 텍스트를 S-expression 단위로 고친다(다시 돌려도 결과가 같다). KiCad GUI는 쓰지 않았다(O-27).

| 풋프린트 | 바뀐 것 | 근거 |
|---|---|---|
| `BTB_ST-BTB-058060-A/B_2x30_P0.5mm` | courtyard를 패드(y ±2.9)·위치결정 구멍(x ±8.5) 포함 **18.3 × 6.4**로 바꿈. 패드를 가로지르던 실크 ±2.2 선을 지우고, 양 끝 세로선(x ±8.9)과 1번 점(−8.1, −2.6)으로 바꿈. 레퍼런스 `REF**`. 패드 폭 0.25는 원품 기준 그대로 둠(O-23) | V-003 ⑦ (권장 18.2×6.3 이상, silk_over_copper 120건) |
| `Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860` (**새로 만듦**) | KiCad 공식 `MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm`에서 파생. 공식 파일은 덮어쓰지 않음.<br>· 신호 패드 0.45 × 1.35, 중심 x ±1.975(Y2 5.3)<br>· EP 1.7 × 2.0<br>· EP 페이스트 4조각(약 66%) | Diodes DS39014 Rev 8-2 p.17 Suggested Pad Layout (V-003 ②) |
| `Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm` (**새로 만듦**) | 공식 풋프린트를 그대로 복사하고 3D 경로만 바꿈: 설치본에 있는 `${KICAD10_3DMODEL_DIR}/Package_SON.3dshapes/WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm.step` | V-003 ① (공식 STEP 파일 없음) |
| `M12_Holder_20mm_CLA216-ICR` | 속성 정정: MPN `CLA216-ICR`, Manufacturer `Commonlands`, Datasheet Commonlands 제품 페이지, Description. 구멍을 NPTH **Ø1.8**, 간격 **20.0**(±10.0)으로 바꿈 | V-003 ⑧ · R-007 (간격 20.0, 홀더 구멍 참고 Ø1.7) · M1.6 나사 ISO 273 medium 여유 1.8 |

- **회로도 연결:** U4·U5(AL8860)과 U2(DRV8837)가 위 새 풋프린트를 가리키도록 바꿨다(C-003 커밋).
- **라이선스:** AL8860·DRV8837 파생은 KiCad 공식 라이브러리(CC-BY-SA 4.0 + 예외 조항)에서 나왔다. KiCad 라이브러리 예외 조항에 따라 설계 산출물에는 고지 의무가 없지만, 출처는 각 풋프린트 설명(descr)에 적었다.

### 검사 (verifiable 예)

| 명령 | 결과 |
|---|---|
| `kicad-cli fp export svg -o <먼저 만든 폴더> hardware/libraries/openhw.pretty` | 종료 0, SVG 8개 생성 확인(V-003: 폴더가 없으면 0을 돌려주고 파일이 없음) |
| `kicad-cli pcb drc --severity-all --format json` — 시험판: openhw 풋프린트 8개를 한 판에 배치 (scratchpad, 저장소에 넣지 않음) | 종료 0. **BTB A/B·AL8860·DRV8837·M12·VSMA·LTR-329: 위반 0** (BTB silk_over_copper 120 → 0)<br>남은 46건은 모두 **DF30**(S401 파생, 0.4mm 피치): clearance 22(패드 간격 0.17 < 기본 0.2) · silk_over_copper 24. 그 밖에 시험판 외곽 없음 1건 |

- **DF30 → pcb(P-003)로 넘김:** 0.4mm 피치에는 풋프린트 로컬 간격이나 넷클래스 규칙이 필요하다. 실크는 이번 범위 밖이라 고치지 않았다.

## C-004 추가 (V-004 R6)

| 풋프린트 | 내용 | 근거 |
|---|---|---|
| `BarrelJack_XKB_DC-005-5A-2.0_Horizontal` (**새로 만듦**) | KiCad `Connector_BarrelJack:BarrelJack_Horizontal`에서 파생. 핀 1 (0,0) · 핀 2 (−5.9, 0) · 핀 3 (−3.0, 4.7). 슬롯 1.0×3.5(핀 3은 3.5×1.0). 패드 3.5×4.2 / 3.0×4.2 / 4.2×3.5(환형 링 ≥0.35). 몸체 외곽선과 3D는 원본 그대로 → XKB 도면과 대조 필요 | V-004 R6 (XKB 도면 Rev A1, LCSC C381116: 1–2 5.90, 3은 3.0·4.70, 슬롯 1.0×3.5) |

- 스크립트 `tools/c004_libfix.py`.
- `kicad-cli fp export svg --footprint BarrelJack_XKB_DC-005-5A-2.0_Horizontal -o <먼저 만든 폴더>` → 종료 0, SVG 생성 확인.

## C-005 추가 (R-009 ⑨ · V-004b R6 · pcb 실크 요청)

| 풋프린트 | 내용 |
|---|---|
| `BarrelJack_XKB_DC-005-5A-2.0_Horizontal` | 몸체 Fab·실크를 XKB X-DC-005-5A-2.0 Rev A1(2025-04-22) 14.0 × 9.0, 앞면 −13.6, 뒤끝 +0.4로 맞춤. courtyard (−13.85, −4.75)~(2.0, 6.7). 실크는 패드에서 ≥0.2. 패드는 C-004 그대로 |
| `Hirose_DF30FC-24DS-0.4V_2x12_P0.4mm` | 실크를 패드에서 ≥0.2로 잘라냄 (랜드 같음) |
| `L_Bourns_SRN6045TA` (**새로 만듦**) | KiCad 공식 사본. 실크만 잘라냄 (랜드 같음) |
| `Everlight_ALS-PT19_1.7x0.8mm` (**새로 만듦**) | 패드 0.8×0.8 @ ±0.75, 몸체 1.7×0.8, 핀 1 = 콜렉터(실크 점 −1.45), Everlight DLS-0000039 Rev.8 (R-009 ⑨, 도면 sha256 448c33a1…9bed) |

- 스크립트: `tools/c005_libfix.py`. 실크 자르기 함수는 축에 나란한 실크선만 다룬다(이 풋프린트들에는 사선이 없다).
- 시험판 DRC: silk 위반 0(17.3절).

## C-008 추가 (pcb P-003 `9355bd1` 요청 · 넷 변경 없음)

| 풋프린트 | 내용 |
|---|---|
| `BarrelJack_XKB_DC-005-5A-2.0_Horizontal` | 보드 외곽 = 몸체 앞면(x −13.6)이라 앞면 실크선을 뺐다. 옆 실크선은 x −13.3에서 시작한다(외곽 + 0.2 + 선 두께 절반 0.06). |
| `M12_Holder_20mm_CLA216-ICR` | F.CrtYd x를 ±13.5에서 **±12.45**로 바꿨다(R-007 귀 포함 24.4 → ±12.2, 여유 0.25). y는 ±9.5 그대로다. |
| `M12_Holder_20mm_CLA216-ICR` | 센서 받침 **13.2□** 자리를 표시했다(M-001d K11, 높이 0.75). F.Fab 점선 외곽 + 풋프린트 규칙 영역 `SENSOR_PEDESTAL`(F.Cu, 부품 금지 · 트랙·비아·패드·동박 붓기 허용). 받침은 접착 부품이라 동박은 넣지 않았다(O-39 기본값, 차선은 동박 기준면). |

**시험판 `kicad-cli pcb drc --severity-all` (scratchpad, 외곽선 있음)**

| 판 | 결과 |
|---|---|
| 수정 전(HEAD) | silk_edge_clearance 2 · courtyards_overlap 1 (MH1 / PicoBlade) |
| 수정 후 | **위반 0** |
| 음성 시험(받침 안에 0402) | items_not_allowed 1 → 금지 영역이 동작한다 |

- PicoBlade(90° 회전)의 courtyard 폭은 6.89다. J_ICR(MH1 기준 x 12.65…19.54, 폭 6.89)에 딱 들어간다.
- 스크립트: `tools/c008_libfix.py` (두 번 돌려도 결과가 같다).
- 회로도 ERC는 두 보드 모두 종료 0이다(라이브러리만 바뀌었다).

## C-022 추가 (orch O-101, mechanical M-009 `f7fd41e` `mechanical/m008/f5f6-drc.md`)

| 풋프린트 | 바꾼 것 | 근거 |
|---|---|---|
| `CLA216_ICR_SolderPads_1x02_P2.54mm` (**새로**) | 전면 J2 CLA216 리드 납땜 패드. 헤더 몸체 없는 2패드(1 □1.7 · 2 ○1.7, 구멍 1.0, 간격 2.54). 패드는 PinHeader_1x02와 같다. F.CrtYd = 패드 + 0.25 (−1.10, −1.10)…(1.10, 3.64). 3D 모델 없음(실장 부품 없음). attr `exclude_from_bom` | M-009 F5 — 헤더 courtyard 가 H1 과 겹침 0.350 mm² → 겹침 0, H1 까지 0.337. 파일은 `f7fd41e` 의 제안 파일 그대로 |
| `M12_Holder_20mm_CLA216-ICR` | F.CrtYd 사각(±12.45 × ±9.5)을 **16점 외형**으로 바꿨다: 몸체 x ±8.2 · y −11.9…+8.9, 귀 x ±12.45 · y ±2.75, 뒷면 J1 BTB 고정 핀 NPTH 두 곳(국소 ∓8.2, −10.55, Ø0.6) 둘레 노치 x ±7.80 · y −10.10 (구멍까지 0.100). 패드·구멍·다른 그림·규칙 영역은 그대로 | M-009 F6 — HCTL 보스 돌출 최대 0.80 < 판 1.6, 보스 Ø0.50 ∩ 스페이서 바닥 0 → 홀더가 앉아도 간섭 0 |

- 노치 안 x 7.80…7.95 는 스페이서 몸체가 courtyard 밖으로 0.15 나오는 자리다. pcb 는 그 노치에 부품을 놓지 않는다(f5f6-drc.md).
- 검사: `kicad-cli fp upgrade --force` (라이브러리 사본) 종료 0. 회로도 ERC 두 보드 0.
