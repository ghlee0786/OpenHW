# C-001 HW/FW 계약 — reCamera Core 2002 캐리어·전면 보드

- 상태: **계약 v1.6 (FW 대조 완료 · C-006 회로도 반영)** · 2026-11-26
- 배정: orch t18r C-001 → C-001b(FW 대조) · 작성자: schematic (단독) · 레인 `t-20261126-155208-d030`
- 이력: 초안 `ac12920` → v1 `8613910` → v1.1 `be646c2` → v1.2 `fd12ba4` → v1.3 `e3ccdd0` → v1.4 `d159068` → v1.5 `a2b4945` ( V-004b — IR_PWM Hi-Z 상태 정정·듀티 기준, N1 Q6 게이트, X1 OE, SMBJ6.0A, USB_DET 필터 — C-005 회로도 `b3b376a`와 일치) → v1.6 (이 커밋: R17 100k → 10k, V-004c/O-36)
- KiCad 회로도는 C-002에서 그린다. 부품은 「1안」이고 재고·정격 확정은 C-002/R-004에서 한다.

## 0. 입력과 근거

**읽기 전용 입력:**
- D-001~D-003 (lead 레인 `t-20261126-144135-5470`, D-003 최신 `41491d6`), product-brief
- R-001 `soc-sg2002.md`, R-002 `optics-ir.md`, R-003 `module-sg2002.md`
- F-001 `firmware/docs/sdk-facts.md` (레인 `t-20261126-155208-b6b4`, 커밋 `e23e9ec`)
- V-001 `validation/review-V001-R002-R003.md` (레인 `t-20261126-155240-aa11`, 커밋 `2a7bf47`)
- orch 확정 O-2(모듈 101991223), O-3(센서 GC2053 잠정), O-4/O-12(라이선스), O-9(조도센서)

**직접 읽은 원본 (2026-11-26, 공개 파일 읽기만):**

| 약칭 | 파일 (저장소 · 커밋) | sha256 | 읽은 방법 |
|---|---|---|---|
| 코어 SCH | Seeed-Studio/OSHW-reCamera-Series `main` · `core/c1-2002/static/reCamera_Core_2002w_8GB_v1.2_SCH_PDF_241014.pdf` (표제란 Rev V1.0, 2024-04-25) | 95fbc621d666f3c9db3df467e3d64d9fc67bd8b9fef037d9294c199add89358f | 시트를 렌더링해 판독. 「시트」 번호 = 표제란 시트 이름 (03 Power IN · 04 SG2002 PWR & XTAL · 05 SG2002 & EMMC · 06 SG2002 & WiFi · 07 BTB Connector) |
| 코어 STEP | 같은 저장소 · `core/c1-2002/3D_Printed_Case/Recamera Core 2002.step` | 7de9f15f29d9645e57321e57cf6ce0f864bc81fdfdc1a1a9490f0500b8ac8785 | AXIS2_PLACEMENT_3D 엔티티를 스크립트로 판독 (2절) |
| B101 | 같은 저장소 · `base/b101-default/PCB/V1.2/reCamera B101 v1.2.kicad_sch` | 469a9927a5e541bd5982c6a7dacd56543aa534afab97ec6f34083f851745a325 | `kicad-cli 10.0.8 sch export netlist` (종료 0)로 넷리스트 추출 |
| S401 | 같은 저장소 · `sensors/s401-gc2053/PCB/reCamera 2002 S4 GC2053 Sensor Board_V1.0_SCH&PCB_250905.kicad_sch` | 3da62d3bbdffc5ec534d0eaecf454a42428d96376bc9756c7aacaaff6a2174ba | 위와 같음 (종료 0) |
| 핀먹스 표 | sophgo/u-boot-2021.10 `050d49a7` · `board/cvitek/cv181x/cv181x_pinlist_swconfig.h` | 4fc61178de00d74aff4695c669d5d6bec6ef673acea7e240e83d95e8cd62ab97 | 패드별 기능 번호 대조 |
| 보드 초기화 | Seeed-Studio/reCamera-OS `0529ca0a` · `external/build/boards/cv181x/sg2002_recamera_emmc/u-boot/cvi_board_init.c` | 4b6000c833faa202379b1a7e0dc9b4424e2f77b2d455939b89574d798532eda9 | PINMUX_CONFIG 줄과 주석(gpio 번호) |
| 보드 DTS | 같은 커밋 · `.../dts_riscv/sg2002_recamera_emmc.dts` | b92a1a2775afdcc093c0b682b64a131d0c7356d9fc410594d489c4a019f395c9 | GPIO를 쓰는 노드 확인 |
| DRV8837 | TI SLVSBA4F (June 2012, rev. April 2021) https://www.ti.com/lit/ds/symlink/drv8837.pdf | 3092ce1aa74c098d1bc881f23f3f71846d760b75128bd5a76de04acfcaebdfc2 | 6.3·6.4·6.5절 수치 추출 |
| LTR-329 주소 | adafruit/Adafruit_LTR329_LTR303 `5c00157` · `Adafruit_LTR329_LTR303.h` 26행 `#define LTR329_I2CADDR_DEFAULT 0x29` | — | 2차 근거 (제조사 데이터시트 아님) |

- **표기:**
  - **확인됨**: 원본에서 직접 읽은 값
  - **추론**: 확인된 근거를 조합한 결론
  - **미확인**: 근거 없음
  - **가정**: 계약을 맺으려고 정한 값
  - 남은 미확인은 14절에서 「C-002 전 필요」와 「실물 확인」으로 나눴다.
- **라이선스 (V-001 ③, orch O-12):**
  - CC BY-SA 4.0 표기는 **코어 회로도 PDF에만** 있다.
  - B101·B301·S401 KiCad 파일에는 별도 표기가 없어 저장소 기본값 **Apache-2.0**이 적용된다.
  - 이 문서는 인터페이스 사실(핀·넷·전압)만 인용하고 회로 블록은 복제하지 않는다.
  - 짝 BTB 풋프린트의 B301 파생은 L-001에서 Apache-2.0 고지와 함께 한다(O-12).

## 1. 결론 요약

1. **3층 적층 (확인됨, 2절 STEP 좌표):** 코어 J1(ST-BTB-058060-A, 센서 신호)은 윗면, J2(-B, 베이스 신호)는 아랫면이다. 그래서 구조는 「**캐리어(뒤) – 코어 – 전면(센서) 보드**」다. 짝 커넥터는 핀 번호의 홀짝이 뒤바뀐다(n ↔ n±1).
2. **FW 대조 결과:** 계약 핀표의 모든 사용 신호에 SoC 패드, Linux GPIO 번호(또는 버스), 기본 DTS 상태를 채웠다(4·5·7절). 불일치 4건을 고쳤다.
   - GC2053 주소: 0x37 → **0x3f**
   - IR_LED_EN·SPARE1: **I2C1(ADS1015 사용 중) 패드에서 MIPI_TXP1/TXM1로 이동**
   - IR_PWM 패드: F-001 미확인 → **PAD_ZQ = GPIO_ZQ (PWR_GPIO_24 = gpio376 또는 PWM_2)**
   - CSI 레인: F-001 미확인 → **lane_id {2,0,3}과 넷 대응 일치**
3. **ICR 구동 (V-001 ⑤ 반영):** 1안을 **TI DRV8837**로 바꾼다(VM = 5V VIN, VCC = 전면 2.8V (v1.4), 펄스 100~500ms). AP1511B는 차선으로 내린다. 이유는 정격 근거다. DRV8837은 데이터시트에 VIH·UVLO·rDS(on)·열저항이 있고, AP1511B는 권장 전류·열 데이터가 없다.
4. **IR LED (V-001 ⑥ 반영):**
   - AL8860을 **1.0A(Rs 0.1Ω)**로 설정하고, 12V에서 **직렬 2개 이하**, 방열 기판을 전제로 한다.
   - **LED 개수는 R-006 대기.**
   - 12V 입력 최악값은 약 **14.4W(1.2A)**로 줄었다. 어댑터는 여유를 두어 12V 2A로 유지한다.
5. **조도센서 (O-9):**
   - LTR-329를 전면 보드 CAM_I2C2(`/dev/i2c-2`)에 두고, 사용자 공간 i2c-dev로 폴링한다. 주소 0x29는 0x3f와 겹치지 않는다.
   - **1.8V I2C 호환 확인 (v1.1):** DS86-2014-0006 Rev C 8절 「Interface Bus Power Supply Voltage VIO 1.7~3.6V」, VDD 2.4~3.6V. 따라서 VDD 3.3V + 1.8V 버스 직결로 간다. 레벨시프터는 넣지 않는다(13절 C15).
6. **FW가 DTS에서 할 일 (8절):** 바뀌는 GPIO가 쓰던 노드를 정리하고 새 기능을 연결한다.
   - 지움: LED 3개(red/blue/white), ADS1015, spi0/mcp2518fd, mm610x, wifi_pin
   - 추가: ICR·IR_LED_EN·STATUS_LED·PWM_2

## 2. J1/J2 판정 근거 (V-001 ② 요청: 파일명·좌표 명시)

**근거 파일:** `hardware/recamera-2002/core/c1-2002/3D_Printed_Case/Recamera Core 2002.step` (sha256 7de9f15f…8785). 어셈블리 「Recamera Core 2002 1」 안의 하위 부품 배치를 읽었다(단위 mm).

| 하위 부품 (PRODUCT) | 배치 엔티티 | 원점 | 법선(Z축) | 판정 |
|---|---|---|---|---|
| `320210641_Sungtech_ST-BTB-058060-A_3D` (→ `SHANGQI_0_5BTB_60P_4_0H_PLUG`) = **코어 J1** | `#123 AXIS2_PLACEMENT_3D('',#124,#125,#126)` | `#124 (60., -53., 1.646672)` | `#125 (0., 0., 1.)` | **윗면** (+Z, z = 판 윗면) |
| `320210642_Sungtech_ST-BTB-058060-B_3D` (→ `..._4_0H_SOCKET`) = **코어 J2** | `#295 AXIS2_PLACEMENT_3D('',#296,#297,#298)` | `#296 (71.8, -65., -5.E-02)` | `#297 (-1.2E-16, -1.4E-32, -1.)` | **아랫면** (−Z, z ≈ 판 아랫면) |
| `QFN88` (SoC, 기준) | `#247` | `#248 (64.262, -61.468, 1.646672)` | `#249 (0., -0., 1.)` | 윗면 |

- **판 두께:** z = 1.646672와 −0.05의 차이로 보면 약 1.6mm다(추론).
- **두 커넥터 중심 간격:** (+11.8, −12.0)mm (STEP 좌표계).
- **기구 독립 확인 (M-001, 레인 `t-20261126-161155-50dc`, 커밋 `ad23d15`, `mechanical/stack-reference.md`, 읽기 전용):** 같은 STEP에서 J1 윗면(중심 0,+12, 긴 축 X), J2 아랫면(중심 +11.8,0, 긴 축 Y)을 따로 확인했고 이 절과 **일치**한다.
  - **보드 외형·나사·커넥터 좌표·적층 높이는 이 문서를 기준으로 한다.** 내용: 코어 30×30×1.6mm, Ø2.0 구멍 3개, M1.6 나사 4곳, 적층 z안(캐리어 −5.6…−4.0, 전면 5.6…7.2), IR LED 후보 영역(남북 21×7).
  - 코어 STEP은 2002w(무선) 모델이다. BTB 짝 높이 4.0mm와 1번 핀 방향은 미확인이며 R-004 SUNGTECH 데이터시트를 기다린다.
- **신호로 본 판정:**
  - J1: CAM_RX0·CAM_I2C2·CAM_EN·IR_PWM 등 → 센서 쪽
  - J2: EPHY·USB·SDIO0·UART0·nRESET 등 → 베이스 쪽
  - 근거: 코어 SCH 07
- **짝 보드로 본 판정:** S401(센서)은 -B로, B101(베이스)은 -A로 짝을 이룬다. 두 넷리스트의 넷 이름이 홀짝 반전 규칙으로 코어와 일치한다(확인됨).
- **README:** 「built from three interchangeable layers: a C1 core board, an S-series sensor board, and a B-series base board」
- **우리 보드:** 캐리어 = ST-BTB-058060-**A** 실장, 전면 보드 = ST-BTB-058060-**B** 실장
  - 원품번·치수는 R-004에서 SUNGTECH 데이터시트로 대조한다.
  - 짝 높이 4.0mm는 모델명 「4_0H」에서 나온 **추정**이다.

## 3. 전원 트리와 전력 예산

### 3.1 트리

```
12V DC 잭 ─ 퓨즈/PTC ─ 역접 P-MOSFET ─ TVS ─┬─ 5V 벅 (≥3A) ── 5V_SYS ─┬─ 캐리어 BTB VIN (29·31·33·35) ─▶ 코어 VIN
                                              │                         │     코어 안: VDDC 0.96V(1.3A) · VDDQ 1.344V(1A) · +3V3(1A) · +1V8 LDO(0.3A) · VDD_RTC 1.8V(0.1A)
                                              │                         │     코어 VIN ─▶ 코어 J1 VIN(38·40·42·44) ─▶ 전면: DRV8837 VM(5V) · 2.8V LDO(DRV8837 VCC·LTR-329, v1.4)
                                              │                         │     코어 +3V3 ─▶ 캐리어 27 ─ P-FET(SD0_PWR_EN) ─▶ microSD
                                              │                         │     코어 +3V3/+1V8 ─▶ 전면 센서 전원 스위치(CAM_EN)
                                              │                         └─ 전원 LED, STATUS_LED
                                              └─ eFuse TPS26600 (SHDN ← IR_LED_EN, 10k 풀다운) ── 12V_IR ─▶ JST GH 6P(12V_IR 2접점) ─▶ 전면 AL8860 ×2 (스트링 A 실장 · B DNP, 각 1.0A) ─▶ VSMA1085400 직렬 2개 ×2
```

| 레일 | 출처 | 정격/제한 | 근거 | 확인 |
|---|---|---|---|---|
| 모듈 VIN | 캐리어 5V 벅 | 5V ±5%로 계약. 하한: VIN < 3.0V면 꺼짐(VBAT_DET 30k/15k, 「<1.0V shutdown」). 상한: 미확인 | 코어 SCH 04·03 | 하한 확인됨(계산) · 상한 미확인 |
| 코어 +3V3 | 코어 SY80004 | Imax 1A, 공유 | 코어 SCH 03 | 확인됨 |
| 코어 +1V8 | 코어 SGM2036 LDO | Imax 300mA, 공유 | 코어 SCH 03 | 확인됨 |
| 5V_SYS | 캐리어 벅 | 3A급, 입력 정격 ≥28V | 3.2절 | 가정 |
| 12V_IR | 캐리어 eFuse TPS26600 | **2스트링 최악 1.22A · ILIM 8.06kΩ ≈ 1.49A** (MODE 개방 = 회로차단기 + 자동 재시도, v1.4) | V-001 ⑥, V-004 K3 | 가정 |
| 전면 2V8 (v1.4, 넷 FRONT_2V8) | 전면 LDO RT9013-28GB (입력 코어 VIN) | ≥50mA (DRV8837 VCC + LTR-329) | DRV8837 VIH max 0.5×2.8 = 1.4V → 1.8V GPIO 여유 0.4V (V-004 R9) | 가정 |
| CAM_1V8 (v1.5) | 전면 Q6 DMG2305UX (CORE_1V8 스위칭, **게이트 CAM_1V8_G = R17 10k(v1.6, V-004c: τ 약 8µs) → CORE_1V8 풀업, Q7 DMG1012T(G = CAM_EN)로 끌어내림** — V-004b N1, S401 패턴) | I2C2 풀업 + 24MHz 발진기 | V-004 R1·R2, O-33 | 가정 |

### 3.2 전력 예산 (야간 최악)

| 부하 | 레일 | 전류 | 전력 | 근거 | 확인 |
|---|---|---|---|---|---|
| 코어 모듈 + 센서 | 5V VIN | 1.0A | 5.0W | Seeed 「5V 1A」 (R-003) | 공식 표기 · 실측 필요 |
| microSD | 코어 +3V3 | ≤0.2A | ≤0.66W | SD 일반값 | 가정 (코어 3V3 1A에 포함) |
| ICR 코일 (CLA216 20Ω) | 5V VIN (DRV8837 VM) | 약 0.245A, 100~500ms 펄스 | 피크 1.2W, 평균 ≈0 | 5V/(20Ω+rDS 0.33Ω max) 계산 | 계산 |
| 전면 2V8 LDO · 발진기 · LED | — | <30mA | <0.15W | 일반값 | 가정 |
| **5V_SYS 합계 (피크)** | | **≈1.3A** | **6.5W** | | 가정 |
| 5V 벅 입력 (효율 88%) | 12V | 0.62A | 7.4W | | 가정 |
| IR LED (v1.2, O-25): VSMA1085400 2직렬 × 2스트링, 스트링마다 1.0A | 12V_IR | — | LED 12.4W typ / 13.2W max | V-001 ⑥, R-006 | 스트링 B는 DNP로 시작 |
| AL8860 ×2 입력 (효율 90%) | 12V | 1.22A (max Vf) | 14.7W | 계산 | 가정 |
| **(O-31, v1.3) IR LED 열 상한** | | | 스트링당 평균 ≤1.6W → 1.0A 피크·IR_PWM 듀티 ≤25% (FW 강제). PCB는 LED·AL8860 아래 열 비아와 구리 확산 | pcb 열 추정 | 차선: 0.3A 연속 / MCPCB 서브보드 |
| **12V 입력 합계 (v1.2)** | | **≈1.84A** | **≈22W** | | 가정 → **어댑터 GST25A12 2.08A (여유 약 12%)**. 스트링 B DNP이면 ≈1.23A |
| 주간 (IR 꺼짐) | | ≈0.62A | ≈7.4W | | 가정 |

- **IR LED 조건 (V-001 ⑥):**
  - Rs 0.1Ω(VSENSE 100mV ±4%)이면 피크가 약 1.2A로 LED 절대최대 1.5A 안이다.
  - 2직렬 max Vf 6.6V에서 듀티는 약 60%로, 권장 25~75% 안이다.
  - LED는 MCPCB 같은 방열 기판에 올린다. FR4라면 thermal via를 넣고 0.8A 이하로 낮춘 뒤 Tsp를 실측한다.
  - LED가 전면 보드에 있으면 C-002/기구에서 방열 방식을 정한다.
- **BTB 핀 전류 정격은 미확인이다.** J2 VIN 4핀으로 피크 1.3A, 핀당 약 0.33A가 흐른다. B101도 같은 경로를 퓨즈 2A로 쓴다.

## 4. 캐리어 BTB 핀맵 (캐리어 = ST-BTB-058060-A, 코어 J2와 짝)

- 「캐리어 핀」은 B101 J1 넷리스트에서 읽었다. 「코어 J2 핀」은 홀짝 반전 규칙으로 구했다.
- 「FW 대조」 열은 F-001과 0절의 핀먹스 표·보드 초기화·DTS에서 채웠다.
- portc의 gpio 번호(416+n)는 F-001의 **추론**값이다.

| 캐리어 핀 | 코어 J2 핀 | 넷 | SoC 패드 (코어 SCH) | 전압 도메인 | 캐리어 용도 | FW 대조 (F-001·SDK) | 시트 |
|---|---|---|---|---|---|---|---|
| 1 | 2 | USB_DN | 70 USB_DM (R90 2.2Ω) | USB2 HS | USB-C 디바이스 D− | DWC2 OTG (일치) | 05 |
| 2 | 1 | EPHY_TXP | 65 PAD_ETH_RXM_EPHY_TXP (R85 2.2Ω) | 아날로그 MDI | MDI → 마그네틱/RJ45 | 내장 EPHY 100M (일치) | 05 |
| 3 | 4 | USB_DP | 69 USB_DP (R89 2.2Ω) | USB2 HS | USB-C 디바이스 D+ | DWC2 OTG (일치) | 05 |
| 4 | 3 | EPHY_TXN | 64 PAD_ETH_RXP_EPHY_TXN (R86 2.2Ω) | 아날로그 MDI | MDI → 마그네틱/RJ45 | 내장 EPHY 100M (일치) | 05 |
| 5 | 6 | GND | GND | — | GND | — | — |
| 6 | 5 | GND | GND | — | GND | — | — |
| 7 | 8 | RESERVE1 | SoC 미연결 — 코어 J1-4 ↔ J2-8 관통 | — | 미사용 (NC, 시험점) | SoC 미연결 (회로도) — F-001 미확인 해소 | 07 |
| 8 | 7 | EPHY_RXP | 63 PAD_ETH_TXM_EPHY_RXP (R87 2.2Ω) | 아날로그 MDI | MDI → 마그네틱/RJ45 | 내장 EPHY 100M (일치) | 05 |
| 9 | 10 | RESERVE2 | SoC 미연결 — 코어 J1-2 ↔ J2-10 관통 | — | 미사용 (NC, 시험점) | SoC 미연결 (회로도) — F-001 미확인 해소 | 07 |
| 10 | 9 | EPHY_RXN | 62 PAD_ETH_TXP_EPHY_RXN (R88 2.2Ω) | 아날로그 MDI | MDI → 마그네틱/RJ45 | 내장 EPHY 100M (일치) | 05 |
| 11 | 12 | SD1_CLK | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | wifisd okay · 2002 실장 실물 확인 | 07 |
| 12 | 11 | GND | GND | — | GND | — | — |
| 13 | 14 | GND | GND | — | GND | — | — |
| 14 | 13 | USB_DET | 60 USB_VBUS_DET | 분압 입력 (B101: VIN 20k/10k) | USB-C VBUS **200k/100k** 분압 + C22 10nF 필터 (v1.4·v1.5, V-004 R11·V-004b 권고) | USB_VBUS_DET 기능 (일치) | 05 |
| 15 | 16 | SD1_CMD | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | wifisd okay · 2002 실장 실물 확인 | 07 |
| 16 | 15 | MIPI_TXM2/IIC1_SDA/PWM | 83 PAD_MIPI_TXM2 | 1.8V 추정(VDD18A_MIPI) | IIC1_SDA → 캐리어 예비 I2C 패드 | IIC1 (i2c1 okay) · ADS1015@0x48 노드 삭제 → FW | 05 |
| 17 | 18 | SD1_D0 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | wifisd okay · 2002 실장 실물 확인 | 07 |
| 18 | 17 | MIPI_TXP2/IIC1_SCL/PWM | 84 PAD_MIPI_TXP2 | 1.8V 추정 | IIC1_SCL → 캐리어 예비 I2C 패드 | IIC1 · ADS1015@0x48 노드 삭제 → FW | 05 |
| 19 | 20 | SD1_D1 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | wifisd okay · 2002 실장 실물 확인 | 07 |
| 20 | 19 | MIPI_TXM1/IIC2_SDA/PWM | 85 PAD_MIPI_TXM1 | 1.8V 추정 | SPARE1 → FPC 8 | XGPIOC_14 = gpio430 (portc 416 추론) · DTS spi0(mcp2518fd) 삭제 → FW | 05 |
| 21 | 22 | SD1_D2 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | wifisd okay · 2002 실장 실물 확인 | 07 |
| 22 | 21 | MIPI_TXP1/IIC2_SCL/PWM | 86 PAD_MIPI_TXP1 | 1.8V 추정 | IR_LED_EN → 12V_IR 부하 스위치 | XGPIOC_15 = gpio431 (추론) · DTS spi0(mcp2518fd) 삭제 → FW | 05 |
| 23 | 24 | SD1_D3 | SG2002 SD1 (R48~R53 0Ω, 2002w DNP) · 패드 번호 미확인 | 미확인 (1.8V 추정) | 미사용 (NC) | wifisd okay · 2002 실장 실물 확인 | 07 |
| 24 | 23 | MIPI_TXM0/GPIO12/PWM | 87 PAD_MIPI_TXM0 | 1.8V 추정 | STATUS_LED (N-MOSFET) | XGPIOC_12 = gpio428 (추론) · DTS mm610x reset·mcp2518fd IRQ(portc 12) 삭제 → FW | 05 |
| 25 | 26 | GND | GND | — | GND | — | — |
| 26 | 25 | MIPI_TXM0/WL_BT_EN/GPIO13 | 88 PAD_MIPI_TXP0 (R14 0Ω, 2002w 회로도 DNP) | 1.8V 추정 | 미사용 (2002 R14 실장 미확인) | XGPIOC_13 · 실물 확인 | 05·07 |
| 27 | 28 | +3V3 | 코어 SY80004 3.3V 출력 (Imax 1A, 코어와 공유) | 3.3V 출력 | microSD 전원 스위치 입력 (B101 방식) | — | 03·07 |
| 28 | 27 | GND | GND | — | GND | — | — |
| 29 | 30 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 30 | 29 | GND | GND | — | GND | — | — |
| 31 | 32 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 32 | 31 | PWR_WAKEUP1 | 44 PWR_BUTTON1 (기능 PWR_GPIO_8, 2002w: BT_HOST_WAKE) | 1.8V (VDDIO_RTC) | ALS_INT_RSV → FPC 7 | PWR_BUTTON1 → PWR_GPIO_8 = gpio360 (pinlist·DTS 주석 porte 8) | 04·06 |
| 33 | 34 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 34 | 33 | nRESET | 39 PWR_RSTN/1V8 (10k PU→VDD_RTC, 100nF) | 1.8V | 리셋 버튼 (GND로) | 하드웨어 (일치) | 04 |
| 35 | 36 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | 5V_SYS 공급 | — | 03·07 |
| 36 | 35 | UPGRAD_KEY | 30 AUX0 (4.7k PU→VDDIO_EMMC) | 3.3V | 업그레이드 버튼 → 직렬 1kΩ → GND | AUX0 = XGPIOA_30 = gpio510, 누르면 0 · DTS wifi_pin이 출력으로 씀 → 삭제(FW) | 05 |
| 37 | 38 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 38 | 37 | SD0_PWR_EN | 15 SD0_PWR_EN | 3.3V | microSD 전원 스위치 (High = 켬, B101 방식) | XGPIOA_14 = gpio494 (일치) | 05 |
| 39 | 40 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 40 | 39 | SDIO_D3/3V3 | 12 SD0_D3 | 3.3V | microSD | SDIO0 3.3V 전용 no-1-8-v, 50MHz (일치) | 05 |
| 41 | 42 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 42 | 41 | SDIO_D2/3V3 | 11 SD0_D2 | 3.3V | microSD | SDIO0 3.3V 전용 no-1-8-v, 50MHz (일치) | 05 |
| 43 | 44 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 44 | 43 | SDIO_D1/3V3 | 10 SD0_D1 | 3.3V | microSD | SDIO0 3.3V 전용 no-1-8-v, 50MHz (일치) | 05 |
| 45 | 46 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 46 | 45 | SDIO_D0/3V3 | 8 SD0_D0 | 3.3V | microSD | SDIO0 3.3V 전용 no-1-8-v, 50MHz (일치) | 05 |
| 47 | 48 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 48 | 47 | SDIO_CMD/3V3 | 7 SD0_CMD | 3.3V | microSD | SDIO0 3.3V 전용 no-1-8-v, 50MHz (일치) | 05 |
| 49 | 50 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 50 | 49 | GND | GND | — | GND | — | — |
| 51 | 52 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 52 | 51 | SDIO_CLK/3V3 | 6 SD0_CLK (R36 0Ω) | 3.3V | microSD | SDIO0 3.3V 전용 no-1-8-v, 50MHz (일치) | 05 |
| 53 | 54 | BT_UART1_RX | 29 IIC0_SDA (R68 0Ω, 2002w DNP) | 3.3V (VDDIO_EMMC) | 예비 패드 (NC 허용) | UART1 (pinmux IIC0_SDA→UART1_RX) · 2002 실장 실물 확인 | 05·07 |
| 54 | 53 | GND | GND | — | GND | — | — |
| 55 | 56 | BT_UART1_TX | 28 IIC0_SCL (R67 0Ω, 2002w DNP) | 3.3V | 예비 패드 | UART1 (pinmux IIC0_SCL→UART1_TX) · 2002 실장 실물 확인 | 05·07 |
| 56 | 55 | SDIO_CD/3V3 | 14 SD0_CD (R39 33Ω + C53 100nF) | 3.3V | microSD 카드 감지 (GND로) | cvi-cd-gpios porta 13 = gpio493 (일치) | 05 |
| 57 | 58 | BT_UART1_CTS | 27 JTAG_CPU_TCK (R70 0Ω, 2002w DNP) | 3.3V | 예비 패드 | UART1 (pinmux JTAG_CPU_TCK→UART1_CTS) · 2002 실장 실물 확인 | 05·07 |
| 58 | 57 | DEBUG_UART0_TX | 18 UART0_TX (R4 100Ω, R32 4.7k PU = 부트 스트랩) | 3.3V | 디버그 헤더 TX (부하·풀다운 금지) | ttyS0 콘솔 · 보드율 실물 확인 | 05 |
| 59 | 60 | BT_UART1_RTS | 26 JTAG_CPU_TMS (R69 0Ω, 2002w DNP) | 3.3V | 예비 패드 | UART1 (pinmux JTAG_CPU_TMS→UART1_RTS) · 2002 실장 실물 확인 | 05·07 |
| 60 | 59 | DEBUG_UART0_RX | 19 UART0_RX (R5 100Ω, R30 4.7k PU) | 3.3V | 디버그 헤더 RX | ttyS0 | 05 |

**전압 도메인:**
- PWR_* 패드: VDDIO_RTC = XC6206P182 1.8V (확인됨)
- SD0·UART0·AUX0 그룹: 3.3V. DTS `no-1-8-v`로 SDIO0이 3.3V 전용임을 확인했다(F-001).
- MIPI_TX 패드: VDD18A_MIPI = 1.8V로 추정

## 5. 전면(센서) 보드 BTB 핀맵 (전면 = ST-BTB-058060-B, 코어 J1과 짝)

| 전면 핀 | 코어 J1 핀 | 넷 | SoC 패드 (코어 SCH) | 전압 도메인 | 전면 보드 용도 | FW 대조 (F-001·SDK) | 시트 |
|---|---|---|---|---|---|---|---|
| 1 | 2 | RESERVE2 | SoC 미연결 — 코어 J1-2 ↔ J2-10 관통 | — | 미사용 (NC) | SoC 미연결 | 07 |
| 2 | 1 | GND | GND | — | GND | — | — |
| 3 | 4 | RESERVE1 | SoC 미연결 — 코어 J1-4 ↔ J2-8 관통 | — | 미사용 (NC) | SoC 미연결 | 07 |
| 4 | 3 | CAM_RX0_4N | 72 PAD_MIPIRX4N | MIPI CSI | 미사용 | — | 05 |
| 5 | 6 | WH_PWM | 47 PWR_GPIO0 | 1.8V | ICR IN2 (DRV8837) | PWR_GPIO_0 = gpio352 · DTS white LED 삭제 → FW | 04 |
| 6 | 5 | CAM_RX0_4P | 73 PAD_MIPIRX4P | MIPI CSI | 미사용 | — | 05 |
| 7 | 8 | GND | GND | — | GND | — | — |
| 8 | 7 | GND | GND | — | GND | — | — |
| 9 | 10 | CAM_I2C2_SCL | 48 PWR_GPIO1 | 1.8V (VDDIO_RTC) | 센서 + LTR-329 SCL | /dev/i2c-2 · GC2053 0x3f · LTR-329 0x29 | 04 |
| 10 | 9 | CAM_RX0_CLKN | 76 PAD_MIPIRX2N | MIPI CSI | 센서 CLK− (DF30-9) | CLK = lane2 = MIPIRX2 (일치) | 05 |
| 11 | 12 | CAM_I2C2_SDA | 49 PWR_GPIO2 | 1.8V | 센서 + LTR-329 SDA | /dev/i2c-2 · GC2053 0x3f · LTR-329 0x29 | 04 |
| 12 | 11 | CAM_RX0_CLKP | 77 PAD_MIPIRX2P | MIPI CSI | 센서 CLK+ (DF30-11) | CLK = lane2 = MIPIRX2 (일치) | 05 |
| 13 | 14 | GND | GND | — | GND | — | — |
| 14 | 13 | GND | GND | — | GND | — | — |
| 15 | 16 | IR_PWM | 35 PAD_ZQ (SDK 이름 GPIO_ZQ) | 미확인 (PWR_GPIO 계열 → 1.8V 추정) | IR_LED_PWM → N-MOSFET → AL8860 CTRL | GPIO_ZQ → PWR_GPIO_24 = gpio376 또는 PWM_2 · DTS blue LED 삭제 → FW | 04 |
| 16 | 15 | CAM_RX0_0N | 80 PAD_MIPIRX0N | MIPI CSI | 센서 D0− (DF30-5) | lane_id {2,0,3}: D0 = lane0 = MIPIRX0 (일치) | 05 |
| 17 | 18 | LIGHT_SENSE | 59 ADC1 | 아날로그 (입력 범위 미확인) | 예비 (아날로그 조도 차선용 패드) | ADC1 (pinlist: 대체 기능 XGPIOB_3) · ADC 드라이버 미확인 | 05 |
| 18 | 17 | CAM_RX0_0P | 81 PAD_MIPIRX0P | MIPI CSI | 센서 D0+ (DF30-7) | lane_id {2,0,3}: D0 = lane0 = MIPIRX0 (일치) | 05 |
| 19 | 20 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 20 | 19 | GND | GND | — | GND | — | — |
| 21 | 22 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 22 | 21 | CAM_RX0_1N | 74 PAD_MIPIRX3N | MIPI CSI | 센서 D1− (DF30-13) | D1 = lane3 = MIPIRX3 (일치) | 05 |
| 23 | 24 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 24 | 23 | CAM_RX0_1P | 75 PAD_MIPIRX3P | MIPI CSI | 센서 D1+ (DF30-15) | D1 = lane3 = MIPIRX3 (일치) | 05 |
| 25 | 26 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 26 | 25 | GND | GND | — | GND | — | — |
| 27 | 28 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 28 | 27 | CAM_RX0_3N | 78 PAD_MIPIRX1N | MIPI CSI | 미사용 (GC2053 2레인) | — | 05 |
| 29 | 30 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 30 | 29 | CAM_RX0_3P | 79 PAD_MIPIRX1P | MIPI CSI | 미사용 | — | 05 |
| 31 | 32 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 32 | 31 | GND | GND | — | GND | — | — |
| 33 | 34 | GND | GND | — | GND | — | — |
| 34 | 33 | GPIO15/IR_CUT | 17 SPK_EN (XGPIOA_15) | 미확인 (SD0/EMMC 그룹 3.3V 추정) | ICR IN1 (DRV8837) | XGPIOA_15 = gpio495 · DTS red LED(heartbeat) 삭제 → FW | 05 |
| 35 | 36 | GND | GND | — | GND | — | — |
| 36 | 35 | GND | GND | — | GND | — | — |
| 37 | 38 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | DRV8837 VM(5V) · 전면 2.8V LDO 입력 | — | 03·07 |
| 38 | 37 | GND | GND | — | GND | — | — |
| 39 | 40 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | DRV8837 VM(5V) · 전면 2.8V LDO 입력 | — | 03·07 |
| 40 | 39 | AUD_MIC | 2 PAD_AUD_AINL_MIC (R97 0Ω) | 아날로그 | 미사용 (NC) | — | 05 |
| 41 | 42 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | DRV8837 VM(5V) · 전면 2.8V LDO 입력 | — | 03·07 |
| 42 | 41 | GND | GND | — | GND | — | — |
| 43 | 44 | VIN | 모듈 전원 입력 (코어 내부 VIN 공통, J1 38~44와 같은 넷) | 5V | DRV8837 VM(5V) · 전면 2.8V LDO 입력 | — | 03·07 |
| 44 | 43 | AUD_AOUTR | 4 PAD_AUD_AOUTR | 아날로그 | 미사용 (NC) | — | 05 |
| 45 | 46 | GND | GND | — | GND | — | — |
| 46 | 45 | GND | GND | — | GND | — | — |
| 47 | 48 | GND | GND | — | GND | — | — |
| 48 | 47 | CAM_EN | 43 PWR_WAKEUP0 (기능 PWR_GPIO_6) | 1.8V | 센서 전원 스위치·CAM_1V8 스위치(Q7)·센서 리셋 (발진기 OE는 v1.5부터 CAM_1V8) | PWR_GPIO_6 = gpio358, S70hardware가 켬 (일치) | 04 |
| 49 | 50 | 1V8 | 코어 SGM2036 1.8V LDO 출력 (Imax 300mA, 공유) | 1.8V 출력 | 센서 1.8V·I2C 풀업 | — | 03·07 |
| 50 | 49 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 51 | 52 | 1V8 | 코어 SGM2036 1.8V LDO 출력 (Imax 300mA, 공유) | 1.8V 출력 | 센서 1.8V·I2C 풀업 | — | 03·07 |
| 52 | 51 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 53 | 54 | GND | GND | — | GND | — | — |
| 54 | 53 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 55 | 56 | GND | GND | — | GND | — | — |
| 56 | 55 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 57 | 58 | 3V3 | 코어 SY80004 3.3V 출력 (Imax 1A, 코어와 공유) | 3.3V 출력 | 센서 AVDD/IOVDD 스위치 입력 (S401 방식) | — | 03·07 |
| 58 | 57 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |
| 59 | 60 | 3V3 | 코어 SY80004 3.3V 출력 (Imax 1A, 코어와 공유) | 3.3V 출력 | 센서 AVDD/IOVDD 스위치 입력 (S401 방식) | — | 03·07 |
| 60 | 59 | NC | (코어 쪽 미연결, ✕ 표시) | — | NC | — | 07 |

### 5.1 센서 모듈 커넥터 (S401 J2 = Hirose DF30FC-24DS-0.4V, S401 넷리스트에서 확인됨)

| 핀 | 넷 | 핀 | 넷 |
|---|---|---|---|
| 1 | CAM_I2C2_SDA | 2 | GND |
| 3 | CAM_I2C2_SCL | 4 | MCLK 24MHz (X1 → R18 0Ω) |
| 5 | CAM_RX0_0N (D0−) | 6 | GND |
| 7 | CAM_RX0_0P (D0+) | 8 | GND |
| 9 | CAM_RX0_CLKN | 10 | GND |
| 11 | CAM_RX0_CLKP | 12 | AVDD 3.3V 전원 입력 (CORE_3V3 → AO3401A 스위치, CAM_EN 제어) |
| 13 | CAM_RX0_1N (D1−) | 14 | **IOVDD 3.3V 전원 입력** (신호 레벨 아님, V-002 ④) |
| 15 | CAM_RX0_1P (D1+) | 16 | DVDD → AVDD 레일 (S401과 같음) |
| 17~23 | GND | 24 | **RESET** (V-002 ④ 확정) — CAM_EN → 10k + 100nF(DNP) RC 자리 (O-22) |

- **CSI 레인 (F-001 대조, 일치):** SDK `sns_cfg_gc2053.as16LaneId = {2,0,3,-1,-1}`, PN swap 없음.
  - 0번 항목은 클록 레인이다(추론, Milk-V GC2083 `lane_id=1,0,2`와 같은 형식).
  - 따라서 CLK = MIPIRX2 = CAM_RX0_CLK, D0 = MIPIRX0 = CAM_RX0_0, D1 = MIPIRX3 = CAM_RX0_1이다. 회로도 넷과 같다.
- **MCLK (F-001 미확인 해소):** BTB에는 MCLK 핀이 없다(코어 SCH 07). 그래서 SoC MCLK는 센서까지 갈 수 없고, 센서 클록은 **전면 보드 24MHz 발진기가 유일한 경로**다. SDK의 `bMclkEn=1`은 BTB 밖 패드에만 영향을 준다(추론).
- **센서 리셋:** DTS가 `snsr-reset`을 지운다. 센서 리셋/PWDN은 CAM_EN(gpio358)에 RC로 묶는다(S401 패턴, F-001 확인).

## 6. I2C 버스와 주소

| 버스 | SoC 패드 | Linux | 전압 | 장치 | 7비트 주소 | 근거 |
|---|---|---|---|---|---|---|
| CAM_I2C2 | 48 PWR_GPIO1(SCL) · 49 PWR_GPIO2(SDA) → IIC2 | `/dev/i2c-2` (okay) | 1.8V | GC2053 | **0x3f** | F-001 (`s32I2cAddr=0x3f`, `s32BusId=2`) — 확인됨 |
| 〃 | 〃 | 〃 | 〃 | LTR-329ALS-01 | **0x29** | Adafruit 드라이버 헤더 (2차). 제조사 데이터시트는 미확보 |
| IIC1 | 83 PAD_MIPI_TXM2(SDA) · 84 PAD_MIPI_TXP2(SCL) | `/dev/i2c-1` (okay) | 1.8V 추정 | 없음 → 캐리어 예비 I2C 패드 (풀업 자리만) | — | 보드 초기화 `PINMUX_CONFIG(PAD_MIPI_TXM2, IIC1_SDA)` — DTS의 ADS1015@0x48은 우리 보드에 없으므로 FW가 삭제 |
| IIC0 | — | disabled | — | 「Not Support IIC0」, 패드는 UART1 | — | 코어 SCH 05 |

- **주소 충돌:** 0x3f와 0x29는 겹치지 않는다(O-9 확인).
- **조도센서 읽기 (O-9):**
  - 커널 5.10에는 LTR-329 드라이버가 없다(F-001).
  - `CONFIG_I2C_CHARDEV=y`이므로 사용자 공간 i2c-dev 폴링으로 읽는다. 커널 백포트는 하지 않는다.
- **풀업 (v1.4, O-33 · V-004 R1·K2 — v1.2의 상시 풀업 분기 C2-6을 되돌림):**
  - 전면 보드가 4.7k를 **CAM_1V8(스위칭)**에 둔다. 스위치는 Q6 DMG2305UX이고 CAM_EN=1일 때 켜진다(S401 방식).
  - 꺼진 센서 I/O로 역급전이 없다. GC2053 데이터시트에는 전원이 꺼진 상태의 입력 허용 근거가 없다(V-004 S4).
  - **FW 규칙: LTR-329는 CAM_EN=1일 때만 폴링한다.** FW 기본은 CAM_EN 상시 1이다(`S70hardware`).
- **LTR-329 레벨 (v1.1 확인됨):**
  - 근거 문서: Lite-On DS86-2014-0006 Rev C (2020-03-14, 파일명 V1.5). 제조사 사이트가 자동 접근을 거부해서 Adafruit 미러로 받았다(sha256 72948664…8b22, L-001 README).
  - 8절 Recommended Operating Conditions: VDD 2.4~3.6V, **VIO 1.7~3.6V**. 절대최대: VDD·SCL·SDA 3.8V.
  - 12절: 7비트 주소 0x29. 7절 핀 표: 1 VDD · 2 GND · 3 SDA · 4 SCL, INT 없음.
  - 권장 풀업은 1k~10k다(7절).
  - **C-002 규칙:** LTR-329 VDD = 전면 2.8V (v1.4), SDA/SCL은 CAM_I2C2(1.8V)에 직결한다. 레벨시프터는 두지 않는다.

## 7. GPIO 배정 (FW 대조 완료)

| 기능 | 넷 | SoC 패드 → 기능 | Linux | 커넥터 (코어 / 우리 보드) | 도메인 | 기본 상태 | 연결 | SDK 기본 상태 → FW 할 일 |
|---|---|---|---|---|---|---|---|---|
| ICR IN1 | GPIO15/IR_CUT | 17 SPK_EN → XGPIOA_15 | gpio495 | J1-33 / 전면 34 | 3.3V 추정 (미확인) | 출력 Low | DRV8837 IN1 | red LED heartbeat → 삭제, ICR용으로 |
| ICR IN2 | WH_PWM | 47 PWR_GPIO0 → PWR_GPIO_0 | gpio352 | J1-6 / 전면 5 | 1.8V | 출력 Low | DRV8837 IN2 | white LED → 삭제 |
| IR LED 밝기 | IR_PWM | 35 PAD_ZQ → PWR_GPIO_24 또는 **PWM_2** | gpio376 / pwm 채널 2 (pwmchip 번호는 FW) | J1-16 / 전면 15 | 1.8V 추정 | **전기 High = LED 끔 · Hi-Z = 끔(R12 풀업) · Low = 켬(CTRL 개방)** (v1.5, V-004b). 하드웨어 기본: R12 100k → CORE_1V8 풀업 = 끔 | N-MOSFET → AL8860 CTRL 끌어내림 (PWM 극성 반전, ≤500Hz — V-001). **FW 규칙: IR_LED_EN을 올리기 전에 IR_PWM을 High로 둔다** · **IR_PWM Low(켬) 비율 ≤25%** (O-31) | blue LED(mmc0) → 삭제, `PINMUX_CONFIG(GPIO_ZQ, PWM_2)` |
| IR LED 전원 | IR_LED_EN | 86 PAD_MIPI_TXP1 → XGPIOC_15 | gpio431 (추론) | J2-21 / 캐리어 22 | 1.8V 추정 | Low = 끔 (하드웨어 풀다운) | 12V_IR 부하 스위치 EN | spi0 SDI 기능 → spi0/mcp2518fd 삭제, GPIO로 |
| 예비 | SPARE1 | 85 PAD_MIPI_TXM1 → XGPIOC_14 | gpio430 (추론) | J2-19 / 캐리어 20 → FPC 8 | 1.8V 추정 | 입력 | 예비 | 위와 같음 |
| 상태 LED | STATUS_LED | 87 PAD_MIPI_TXM0 → XGPIOC_12 | gpio428 (추론) | J2-23 / 캐리어 24 | 1.8V 추정 | Low = 끔 | N-MOSFET + LED | portc 12를 쓰는 mm610x reset·mcp2518fd IRQ → 삭제 |
| 조도 INT 예비 | PWR_WAKEUP1 | 44 PWR_BUTTON1 → PWR_GPIO_8 | gpio360 | J2-31 / 캐리어 32 → FPC 7 | 1.8V | 입력 | 차선 센서 INT | DTS에 주석으로만 있음 |
| 센서 전원·리셋 | CAM_EN | 43 PWR_WAKEUP0 → PWR_GPIO_6 | gpio358 | J1-47 / 전면 48 | 1.8V | 부팅 때 High | 전원 스위치(Q3·Q7)·센서 리셋 (발진기 OE = CAM_1V8, v1.5) | `S70hardware`가 켬 (그대로) |
| 업그레이드 버튼 | UPGRAD_KEY | 30 AUX0 → XGPIOA_30 | gpio510 | J2-35 / 캐리어 36 | 3.3V | 풀업 (누르면 0) | 버튼 → **직렬 1kΩ** → GND | DTS `wifi_pin poweron-gpio = porta 30`이 출력으로 쓸 수 있음 → 삭제. 출력과 버튼이 부딪칠 때를 막으려고 1kΩ을 넣는다 |
| microSD 전원 | SD0_PWR_EN | 15 → XGPIOA_14 | gpio494 | J2-37 / 캐리어 38 | 3.3V | High = 켬 (B101 NPN+PFET 패턴, 같은 SDK로 동작) | P-FET 스위치 | 그대로 |
| microSD 감지 | SDIO_CD | 14 → XGPIOA_13 | gpio493 (`cvi-cd-gpios`) | J2-55 / 캐리어 56 | 3.3V | — | 카드 감지 스위치 → GND | 그대로 |
| 아날로그 조도 (차선) | LIGHT_SENSE | 59 ADC1 | ADC 드라이버 미확인 | J1-18 / 전면 17 | 아날로그 | — | 미실장 패드 | 차선으로 갈 때 FW가 확인 |

- **ICR 동작 (DRV8837 진리표, SLVSBA4F):**
  - IN1=1, IN2=0 → OUT1 H / OUT2 L
  - IN1=0, IN2=1 → 역방향
  - 0/0 → 코스트(무전류). 기본값으로 쓴다.
  - 1/1 → 브레이크
  - CLA216 원문 「正極性で開路、負極性で閉路」의 극성과 JST 핀 순서는 **실물로 확인**한다.
  - 펄스 폭 100~500ms는 FW 타이머로 준다(SDK에 ICR 구현 없음 — F-001, F-002에서 새로 작성).
- **DRV8837 nSLEEP:** VCC(2.8V, v1.4)로 10k 풀업한다(상시 활성). 대기 전류는 FW가 IN1=IN2=0으로 관리한다.
- **IIC1:** 캐리어 예비 I2C 패드로 남긴다(풀업 자리만). DTS의 ADS1015 노드는 FW가 지운다.

## 8. FW가 할 DTS·핀먹스 변경 (F-002로 넘김)

| 대상 (reCamera-OS `0529ca0a`) | 지금 | 바꿀 것 | 이유 |
|---|---|---|---|
| `leds/led0 red` porta 15 | heartbeat | 삭제 → ICR IN1 (gpio495) | GPIO15/IR_CUT를 ICR에 씀 |
| `leds/led2 white` porte 0 | — | 삭제 → ICR IN2 (gpio352) | WH_PWM을 ICR에 씀 |
| `leds/led1 blue` porte 24 + `PINMUX_CONFIG(GPIO_ZQ, PWR_GPIO_24)` | mmc0 표시 | 삭제, 핀먹스 → `PWM_2` | IR_PWM을 PWM으로 |
| `&i2c1/adc@48` (ti,ads1015) | okay | 삭제 (i2c1은 예비로 둬도 됨) | 캐리어에 ADS1015가 없음 |
| `&spi0/mcp2518fd` (cs porta 12, irq portc 12) | okay | 삭제, spi0 disabled | 캐리어에 CAN이 없음. TXM1/TXP1을 GPIO로 |
| `&sd/mm610x-sdio` (reset portc 12) | okay | 삭제 | 무선 없음. portc 12를 STATUS_LED로 |
| `wifi_pin` (porta 30) | okay | 삭제 | 무선 없음. gpio510은 버튼 |
| 새 핀먹스 | — | `PAD_MIPI_TXM0/TXM1/TXP1 → XGPIOC_12/14/15` | STATUS_LED·SPARE1·IR_LED_EN |

## 9. 클록

| 클록 | 위치 | 값 | 근거 | 할 일 |
|---|---|---|---|---|
| SoC 주 클록 | 코어 X1 | 25MHz 10ppm | 코어 SCH 04 | 없음 |
| 센서 MCLK | **전면 보드** | 24MHz 발진기 (S401 X1 「9C24000004」 패턴, **OE = VDD = CAM_1V8** — v1.5 V-004b R2: OE가 VDD보다 먼저 오르지 않음) | BTB에 MCLK 없음 (5.1절) | 실장 **필수** |
| 32.768kHz | 코어 시트 06 X3 (Wi-Fi 쪽) | — | 코어 SCH 06 | 캐리어 영향 없음 |
| 이더넷·USB | SoC 내장 | — | F-001 1.8절 | 없음 |

## 10. 부트·복구 (F-001 대조)

| 항목 | 내용 | 근거 | 확인 |
|---|---|---|---|
| 부트 체인 | fsbl → OpenSBI → u-boot 2021.10 → Linux 5.10.4, C906 | F-001 1.3 | 확인됨 |
| 부트 순서 | `bootcmd = run sdboot \|\| cvi_update \|\| cvi_otp; …; run emmcboot` → **SD가 먼저**, 없으면 eMMC | F-001 (cv181x-asic.h L342) | 확인됨 |
| eMMC | 코어 8GB, rootfs A/B (D-003 #9로 OTA는 빼지만 구조는 그대로) | F-001 | 확인됨 |
| microSD 복구 | `*_emmc_recovery.zip`을 SD에 쓰고 전원을 넣으면 eMMC에 굽는다 → **캐리어 microSD 슬롯이 복구 경로** | F-001 | 확인됨 |
| USB 굽기 | `usb_dl.exe -c cv181x …` (Windows) → 캐리어 USB-C(디바이스) | F-001 | 도구는 확인됨 · **버튼 절차는 실물 확인** |
| 스트랩 | UART0_TX PU = Normal / PD = ROM Fail. EPHY_RTX PU = C906 → **캐리어는 DEBUG_UART0_TX에 풀다운·LED를 두지 않는다** | 코어 SCH 05, F-001 | 확인됨 |
| 버튼 | RESET: nRESET → GND. UPGRADE: UPGRAD_KEY(gpio510) → 1kΩ → GND | 코어 SCH 04·05, F-001 | 확인됨 |
| 저전압 차단 | VIN < 3.0V | 코어 SCH 04 | 확인됨(계산) |
| MAC 주소 | efuse → u-boot `cvi_otp` | F-001 | 확인됨 (캐리어에 EEPROM 불필요) |

## 11. 디버그 UART와 시험점

- **디버그 UART:** DEBUG_UART0_TX/RX(캐리어 58/60)를 3핀 헤더(GND·TX·RX)와 시험점으로 낸다. 3.3V, ttyS0이고 보드율은 실물로 확인한다.
- **캐리어 시험점:**
  - 전원: 12V_IN(보호 후), 5V_SYS, 12V_IR, 코어 +3V3(27), SD_PWR_3V3, GND 2곳 이상
  - 신호: USB D±, USB_DET, nRESET, UPGRAD_KEY, STATUS_LED, IR_LED_EN, SPARE1, IIC1 SDA/SCL, RESERVE1/2
- **전면 시험점:** 전면 2V8, CAM_1V8, AVDD, IOVDD, MCLK, CAM_EN, DRV8837 OUT1/OUT2, AL8860 SW·LED+, IR_PWM, LIGHT_SENSE, I2C2 SDA/SCL

## 12. 보호회로

| 위치 | 위협 | 대책 (1안 — 정격·재고는 C-002/R-004에서 확정) | 근거 |
|---|---|---|---|
| 12V 입력 | 역접 | P-MOSFET (Vds ≥30V, 게이트 제너) | 일반 설계 |
| 〃 | 과전압·서지 | TVS SMBJ15A급 + 하위 IC 입력 정격 ≥28V (AL8860 4.5~40V) | R-002, V-001 |
| 〃 | 과전류 | PTC 또는 퓨즈 2.5~3A (예산 1.2A의 약 2배) | 3.2절 |
| 5V_SYS | 벅 고장 시 과전압 | **D7 SMBJ6.0A** (VRWM 6.0V > 벅 최대 5.30V, 단방향) — v1.5 V-004b R5 (v1.4의 SMBJ5.0A는 VRWM이 출력보다 낮았음). DRV8837 VM 최대 11V, 코어 상한 미확인 | 3.1절 |
| USB-C | ESD | D± 저용량 ESD, VBUS TVS, CC 5.1k 풀다운 | B101 패턴 |
| microSD | ESD | 7선 ESD | B101 패턴 |
| RJ45 | 서지·ESD | 칩 쪽 쌍마다 저용량 TVS, 칩 쪽 센터탭 100nF → GND, 라인 쪽 Bob Smith 75Ω + 1nF/2kV → 실드, GNDPWR–GND 1M + 1nF | B101 넷리스트 |
| 12V_IR | 단락·과전류 | **TPS26600 eFuse**: SHDN ← IR_LED_EN(10k 풀다운, 기본 끔), UVLO → IN(SLVSDG2G: 「must be connected to the IN terminal」), OVP → RTN(내장 33V OVP), **MODE 개방(회로차단기 + 자동 재시도, v1.4 — 과부하 때 합계가 어댑터 2.08A를 넘지 않게)**, RTN = GND(역접은 앞단 P-FET가 맡음), **ILIM 8.06kΩ ≈ 1.49A**(2스트링 1.22A 기준, O-21의 10k/1.2A는 1스트링용), dVdT 22nF | O-21, V-002 ⑥, C-002 C2-4 |
| ICR | 코일 단락 | DRV8837 과전류 차단 1.9~3.5A, 열 차단 150°C | SLVSBA4F 6.5 |
| UPGRAD_KEY | 출력과 버튼 충돌 | 직렬 1kΩ | 7절 |

## 12A. 전면 보드 – 캐리어 보드 간 커넥터 (v1.3)

- **v1.3 변경:** FFC 10P(TE 1-84952-0/84953-0)를 없앴다. 사양 108-1393이 「Signal application only, 1 ampere maximum for single circuit」라 12V_IR 전원 용도는 정격 밖이다(V-003 ⑥).
- **커넥터:** JST GH **SM06B-GHS-TB** (1.25mm 6P 가로형 SMD) ×2 + GH 6P 케이블.
  - 정격: 「Current rating: 1.0 A AC/DC (AWG #26)」, 50V (JST eGH 카탈로그, sha256 b1dcb317…b722)
- **대칭 배치:** 1↔6, 2↔5가 같은 신호라 케이블 방향과 상관없이 전원·GND가 맞는다. 뒤집히면 3↔4(1.8V 예비선 둘)만 서로 바뀐다.

| 핀 | 신호 | 캐리어 J7 | 전면 J4 |
|---|---|---|---|
| 1 | GND | GND | GND |
| 2 | 12V_IR | TPS26600 OUT | AL8860 ×2 VIN |
| 3 | SPARE1 | 캐리어 20 (XGPIOC_14) | 시험점 |
| 4 | ALS_INT_RSV | 캐리어 32 (PWR_GPIO_8) | 10k → CORE_1V8 |
| 5 | 12V_IR | TPS26600 OUT | AL8860 VIN |
| 6 | GND | GND | GND |
| MP | GND | GND | GND |

- **전류:** 2스트링 최악 1.22A / 2접점 = 0.61A/접점(정격의 61%). 스트링 B를 DNP로 시작하면 0.31A.
- **미확인:** 인접 접점 동시 통전 감액, 케이블 길이에 따른 AWG26 전압강하.
- **차선 (C-003 C3-1 ②):** FFC는 신호용으로 남기고, 12V_IR만 JST PH 2P(S2B-PH-SM4-TB, 「2 A AC/DC (AWG #24)」)로 분리한다.

## 13. 분기점·선택·이유·차선책 (v1 갱신)

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| C1 | 보드 구성 | 캐리어(뒤)–코어–전면 보드 3층 | J1 윗면·J2 아랫면 (2절 STEP) | J1 어댑터 + FPC로 CSI를 원격 센서까지 |
| C2 | 센서 실장 | S401과 핀 호환되는 DF30 24P GC2053 모듈 + 전면 24MHz 발진기 | IQ sdr/sdr_ir가 rootfs에 있다 (F-001) | O-3 차선 GC4653 → CAM-GC2083 |
| C3 | IR 드라이버 위치 | 전면 보드 (FPC로 12V) | 스위칭 루프를 LED 옆에 둔다 | 캐리어에 드라이버 |
| C4 | 전원 입력 | 12V 단독, USB-C는 데이터 + USB_DET | 경로가 하나라 단순 | 이상적 다이오드 OR |
| C5 | microSD | SD0 3.3V + 코어 +3V3 스위칭 | DTS `no-1-8-v`, CD = gpio493과 일치 | SD1 (2002 실장 확인 후) |
| C6 | 조도 INT | 폴링 (LTR-329에 INT 없음 — 같은 계열 KiCad 심벌 핀 비교 기준) + 예비선 gpio360 | O-9 | LTR-303/VEML6030 + FPC 7 |
| C7 | ICR 제어선 | GPIO15/IR_CUT(gpio495) + WH_PWM(gpio352) | 둘 다 J1에 있고 SDK에서는 LED 용도라 바꾸기 쉽다 | SPARE1(gpio430) |
| C8 | IR 밝기 | IR_PWM(PWM_2) → N-MOSFET → AL8860 CTRL + IR_LED_EN 하드웨어 차단 | 1.8V PWM으로는 CTRL 선형 구간(0.3~2.5V)에 걸린다. 끔을 두 겹으로 보장 | IR_PWM을 CTRL에 직결 (V-001: 3.3V 로직 직구동 가능 — 패드 도메인이 3.3V로 확인될 때) |
| C9 | 이더넷 자기부품 | 칩 쪽 센터탭이 따로 나오는 통합 마그넷 RJ45 | 부품 수·면적 | B101식 개별 트랜스 |
| C10 | 전면 LDO (v1.4: 2.8V) | 코어 VIN → 전면 LDO | 코어 3V3을 센서에 남긴다 | 코어 +3V3 |
| C11 | 보드 간 링크 (v1.3) | **JST GH 6P SM06B-GHS-TB 대칭** (12A절) | FFC 사양이 「Signal application only」(V-003 ⑥). GH는 1.0A/접점 전원 정격 | FFC 10P(신호) + JST PH 2P(12V_IR) 분리 |
| C12 | BTB 짝 커넥터 | 캐리어 -A, 전면 -B (Sungtech). 풋프린트는 B301 파생 허용 (O-12, Apache-2.0 고지) | 코어와 같은 시리즈 | 호환품 (R-004) |
| **C13** | **ICR 드라이버 (V-001 ⑤)** | **TI DRV8837DSGR**: VM = 5V(VIN), VCC = 전면 3.3V → **v1.4: 2.8V (VIH max 1.4V, 여유 0.4V — V-004 R9)**, IN1/IN2를 GPIO에 직결 | 정격 근거가 있다(SLVSBA4F): VCC 1.8~7V, **VIH ≤ 0.5×VCC = 1.65V** → 1.8V GPIO 직결 가능. rDS(on) HS+LS 280/330mΩ → 코일 약 4.9V·0.245A로 CLA216 3.0~5.0V 안. θJA 60.9°C/W. VCC = 1.8V는 **UVLO 상승 최대 1.8V**에 걸려 쓰지 않는다 | UMW AP1511B (VDD 5V, 펄스만 — V-001 조건). 권장 전류·열 데이터가 없고 1.8V 입력 VIH도 미확인 |
| **C14** | **캐리어 GPIO 재배정 (F-001 대조)** | IR_LED_EN = MIPI_TXP1(gpio431), SPARE1 = MIPI_TXM1(gpio430), IIC1(TXM2/TXP2)은 예비 I2C | 초안은 IIC1 패드에 GPIO를 뒀는데 SDK가 IIC1(ADS1015)로 쓴다. IIC2 대체 기능인 TXM1/TXP1은 IIC2가 이미 PWR_GPIO1/2에 있어 비어 있다 | 초안대로 IIC1 패드를 GPIO로 (FW가 i2c1 삭제) |
| **C15** | **조도센서 레벨 (O-9, v1.1 확정)** | LTR-329를 1.8V CAM_I2C2에 직결 (VDD 3.3V, 레벨시프터 없음) | 데이터시트 Rev C: VIO 1.7~3.6V, 주소 0x29 ≠ 0x3f | LIGHT_SENSE 포토트랜지스터(ALS-PT19) — 미실장 패드만 남긴다 |
| **C16** | **UPGRAD_KEY 보호** | 버튼 직렬 1kΩ | DTS wifi_pin이 gpio510을 출력으로 쓸 수 있다 | FW가 wifi_pin을 지우면 0Ω |
| **C17** | **IR LED 설정 (V-001 ⑥)** | AL8860 Rs 0.1Ω(1.0A), 12V에서 직렬 ≤2, 방열 기판 | 1.5A 설정은 절대최대에 여유가 0 | FR4 + thermal via + 0.8A 이하 |
| **C18** | **C-002 반영 (v1.2)** | ① FPC 대칭 핀배치(12A절) ② ILIM 8.06k ③ 두 AL8860 CTRL이 IR_PWM 하나를 공유 ④ I2C2 풀업은 CORE_1V8 상시 ⑤ DVDD를 AVDD 레일로 | C-002 README 12절 C2-3~C2-8 | 각 행의 차선은 C-002 README에 있다 |
| **C21** | **V-004b 반영 (v1.5)** | Q6 게이트 자기 소스 풀업 + Q7(N1) · X1 OE = CAM_1V8 · SMBJ6.0A · R11 → SD_PWR_GD · USB_DET 10nF · CLA216 리드 PicoBlade(O-34) | V-004b · R-009 | C-005 README 17.5 |
| **C20** | **V-004 반영 (v1.4)** | I2C2 풀업·X1을 CAM_1V8로(O-33) · IR_PWM 극성(High = 끔) + R12 풀업 · 전면 LDO 2.8V · TPS26600 MODE 개방 · USB_DET 200k/100k · 5V TVS · RESET RC + BAT54 | V-004 R1~R13 · K1~K4 | C-004 README 16.5 |
| **C19** | **ICR·IR 부품 (O-25)** | IR LED VSMA1085400(±40°) 4자리 = 2직렬 × 2스트링, B는 DNP. 풋프린트는 VSMA1085600과 같다(도면 6.550-5366.9-3) | R-006 | VSMA1085600(±60°) |

## 14. 남은 미확인

**C-002 전 필요:**
1. ~~LTR-329 데이터시트~~ → **해결 (v1.1):** Rev C 확보, VIO 1.7~3.6V, 핀·랜드는 L-001 README에 대조
2. ~~AL8860 CTRL~~ → **해결 (v1.1):** DS39014 Rev 8-2 원문 「Leave floating for normal operation · Drive with PWM signal from open-collector or open-drain transistor」 → C8의 N-MOSFET 방식과 맞다
2-1. ~~FFC 정격~~ → **v1.3에서 대체:** TE FFC 커넥터는 「Signal application only」라 JST GH 6P로 바꿨다(12A절). 남은 확인: GH 인접 접점 감액, 케이블 전압강하
3. **BTB:** 원품번, 핀당 전류 정격, 짝 높이 (R-004 SUNGTECH 데이터시트)
4. **코어 VIN 상한:** SY80004·SGM2036 정격. 5V 벅 정밀도와 출력 TVS를 정하는 데 쓴다.
5. **GC2053 24P 센서 모듈:** 품번·조달처 (O-3)
6. **IR LED 개수·조사각:** R-006 대기

**실물 확인 (보드를 받은 뒤):**
1. 2002에서 SD1(R48~R53)·UART1(R67~R70)·R14 0Ω이 실장되는지. 우리 설계는 이 신호들을 쓰지 않는다.
2. portc GPIO 베이스(416, 추론)가 맞는지: `/sys/class/gpio`
3. USB 굽기 모드로 들어가는 버튼 절차, 디버그 콘솔 보드율
4. CLA216 코일 극성과 JST 핀 순서 ↔ DRV8837 OUT1/OUT2
5. 패드 도메인: SPK_EN(GPIO15)·PAD_ZQ. 지금 설계는 두 도메인 모두에서 동작하게 했다(DRV8837 VIH 1.65V, CTRL은 N-MOSFET).
6. J1/J2 면, 1번 핀 방향 (기구 M-001이 따로 측정)

**FW 확인 대기 0건:** 초안의 「FW 확인 대기」 항목은 모두 F-001과 SDK 원본으로 채웠다. 남은 것은 위 「실물 확인」으로 옮겼다.

## 15. C-002(회로도)로 넘길 규칙

- 표 4와 표 5를 심벌 핀으로 그대로 쓴다. **홀짝 반전 규칙을 다시 확인한다.**
- B101/S401 회로를 복사하지 않는다. 인터페이스 사실만 쓴다. 풋프린트 파생은 O-12에 따라 L-001에서 고지와 함께 한다.
- 「C-002 전 필요」 항목이 풀리기 전에는 해당 부분을 0Ω·미실장 옵션으로 둔다.
