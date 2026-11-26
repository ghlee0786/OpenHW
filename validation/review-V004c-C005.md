# V-004c C-005 수정분 재검토

- 배정: orch t18r V-004c · 검토자: review t18y · 레인 t-20261126-183643-3f9e · 확인일 **2026-11-26**
- **기준:**
  - 회로도: C-002 레인 t-20261126-165741-b193 **b3b376a**, 수정 전 **58eb49b**와 비교. 두 커밋 모두 `git archive` 사본으로 검토했다.
  - 계약: v1.5 **a2b4945**
- 대상: V-004b(`validation/review-V004b-C004.md`, 6404bf7)의 미해소·부분 해소 항목과 신규 N1
- 방법: 두 넷리스트를 직접 비교하고 핀 기능별 연결을 확인했다. 판정 근거로 쓴 원문은 이전에 받아 둔 데이터시트에서 다시 확인했다.
- 수정하지 않은 것: 제품 파일과 저장소. 실측은 없다.

## kicad-cli

| 명령 (b3b376a 사본) | 종료 코드 | 위반 |
|---|---|---|
| `kicad-cli sch erc --severity-all --exit-code-violations --format json -o erc4_carrier.json carrier.kicad_sch` | 0 | 0 |
| 같은 명령 · `front.kicad_sch` | 0 | 0 |

## 판정표

| # | V-004b 항목 | 판정 | 근거 |
|---|---|---|---|
| **N1** | Q6 게이트 공유 | **해소** (권고 1건) | 넷: 새 `/CAM_1V8_G` = Q6.1(G) · Q7.3(D) · R17.2. R17.1 = **CORE_1V8**(= Q6.2 S). Q7 DMG1012T G = CAM_EN, S = GND. Q6.1은 CAM_PG에서 분리됐다. CAM_EN=0(R6 풀다운)이면 Q7이 꺼져 Q6 VGS ≈ 0V가 되므로, CORE_3V3/1V8 상승 순서와 상관없이 정적으로 꺼져 있다. CAM_EN=1이면 Q7(VGS(th) ≤1.0V, 1.8V 구동)이 게이트를 0V로 내려 VGS ≈ −1.8V로 켠다(DMG2305UX 원문 RDS(on) ≤200mΩ @−1.8V). S401 Q6/Q7과 같은 구조다. **권고:** CORE_1V8이 오를 때 게이트가 R17·Ciss(원문 808pF) τ ≈ 81µs만큼 늦게 따라온다. 1.8V가 약 290µs보다 빨리 오르면 순간적으로 \|VGS\| > 0.5V가 될 수 있다. S401도 같은 100k 구조라 양산 실적은 있다. 여유를 원하면 R17을 10k로 낮춘다(τ 8µs, Q7 전류 180µA) |
| **R1** | I2C 역급전 | **해소** | V-004b에서 정상 상태는 이미 해소됐고, 남은 N1이 위에서 해소됐다 |
| **R2** | X1 OE | **해소** | X1.1(EN) = **CAM_1V8**, X1.4(Vdd) = CAM_1V8. OE와 VDD가 같은 레일이라 OE가 VDD보다 먼저 걸리는 구간이 없다. FW 「CAM_EN=1 후 첫 I2C까지 ≥5ms」(X1 Start-up 3ms Max)는 계약 쪽 규칙으로 유지 |
| **R5** | 5V TVS | **해소** | D7 = **SMBJ6.0A**. 원문 행(Littelfuse 표, LCSC 사본, 검토자 확인): 「SMBJ6.0A … 6.0 · 6.67 7.37 · 10 · 10.3 · 58.3 · 800」. VRWM 6.0V ≥ 벅 출력 최대 5.30V. 방향 K = 5V_SYS(V-004b에서 확인, 바뀌지 않음) |
| **R8** | SD 전원 VGS | **해소** | R11.2: SD_PWR_G → **SD_PWR_GD**(Q3 드레인 · R22). Q3 꺼짐 → GD = CORE_3V3 → R22로 게이트 3.3V, VGS 0. Q3 켜짐 → GD = 0 → 게이트 0V, **VGS −3.3V** → AO3401A RDS(on) ≤85mΩ 보증(@−2.5V) 안. 켤 때 τ = R22·C21 = 4.7ms, 끌 때 τ = (R11+R22)·C21 = 14.7ms. B101 패턴과 같다 |
| **R10** | D1·D2 품번 | **해소** | MPN 「Vishay SSA24-M3/61T (SMA)」. Vishay 89280 원문: 「SMA (DO-214AC)」, SSA24 VRRM 40V, IF(AV) 2.0A, 주문 예 「SSA23L-M3/61T … PREFERRED PACKAGE CODE 61T」 → 같은 계열 표기 규칙으로 SSA24-M3/61T가 성립한다(주문 예 행은 SSA23L만 있어 SSA24는 표기 규칙으로 판정). 풋프린트 D_SMA 일치 |
| **R11** | USB_DET 필터 | **해소** | 새 C22 10nF 0402: USB_DET–GND. τ = 66.7k × 10nF = 0.67ms |
| **R12** | F1 지연형 | **해소** | MPN 「Bel Fuse 0685T3000-01」. Bel C1T 원문(검토자 확인): 「Surface Mount **Slow Blow** Chip Fuse」, 표 「0685T3000-XX 3A T3」, 정격 「2A-8A/63V AC/DC @50A」, 「0685T=C1T; [XXXX]=Ampere Rating」, 주문 「0685TXXXX-01」(EIA-481 테이프 5000). 1206(Fuse_1206_3216Metric) 그대로. 80% 감액 2.4A > 최악 1.84A |
| **계약** | v1.5 IR_PWM 문구 | **해소** | 324행: 「전기 High = LED 끔 · **Hi-Z = 끔(R12 풀업)** · Low = 켬(CTRL 개방)」, 「**IR_PWM Low(켬) 비율 ≤25%**」, FW 규칙 「IR_LED_EN을 올리기 전에 IR_PWM을 High」. 3.1 표 CAM_1V8 행(110행)에 「게이트 CAM_1V8_G = R17 100k → CORE_1V8 풀업, Q7 DMG1012T(G = CAM_EN)」, 260·329행에 발진기 OE = CAM_1V8이 반영됐다 |

V-004b에서 남은 경미·권고 항목은 이번 커밋 메시지 기준으로 다음과 같이 처리됐다(넷 영향 없음, 라이브러리 쪽 변경).
- R6: DC 잭 courtyard·실크·몸체
- R3: R16 주석, FW 규칙

이 둘은 넷 비교 범위 밖이라 이번 판정에 넣지 않았다.

## 넷 비교 (58eb49b → b3b376a, 직접 추출)

- **캐리어 (부품 97 → 98, 넷 95 → 95):**
  - 새 C22(USB_DET–GND)
  - 값/MPN 변경: D7 SMBJ5.0A → SMBJ6.0A, F1 MPN → Bel 0685T3000-01
  - 넷 변경: R11.2 SD_PWR_G → SD_PWR_GD, USB_DET·GND에 C22 추가
  - **목록 밖 차이 0.**
- **전면 (부품 83 → 85, 넷 65 → 66):**
  - 새 Q7 · R17, 새 넷 CAM_1V8_G
  - 넷 변경:
    - Q6.1 CAM_PG → CAM_1V8_G
    - X1.1 CAM_EN → CAM_1V8
    - CORE_1V8에 R17 추가
    - GND에 Q7.2 추가
  - MPN 변경: D1·D2 → SSA24-M3/61T
  - V-004b 밖이지만 커밋 메시지·계약 C21에 적힌 의도 변경(R-009 · O-34):
    - J2 → Molex PicoBlade 53261-0271. J2 넷 연결은 바뀌지 않았다(NET-CHG 없음).
    - L1·L2 풋프린트 → `openhw:L_Bourns_SRN6045TA` 사본(실크 이격)
    - Q4 풋프린트 → `openhw:Everlight_ALS-PT19_1.7x0.8mm`. descr 「Pad 1 = collector, pad 2 = emitter」, 넷 Q4.1(C) = CORE_1V8, Q4.2(E) = LIGHT_SENSE로 일치. DNP다.
- **의도 밖 전기 변경: 0** (두 보드).
- 전체 출력: `C:\Users\gh\AppData\Local\Temp\claude\152719db0d1b2c74\2304a8aa-eb88-41c3-9975-aa6fda3de30c\scratchpad\v004c\netdiff.txt`

## 남은 것
- 미해소: 없음
- 권고: N1의 R17을 10k로 낮추기(선택)
- 확인 불가로 남은 것(이번 범위 밖, 이전 보고서 그대로):
  - CLA216 코일 극성과 PicoBlade 핀 순서 → 실물 확인
  - 실측 전 bring-up 항목

## 돌린 명령
- kicad-cli `sch erc` 2회: 종료 0 · 위반 0
- 넷 비교: scratchpad 파이썬 스크립트(`v004\c003\scripts\netdiff.py`)
- 저장소 테스트·빌드 명령: 돌리지 않음(문서 1개만 추가하고, 하네스 검사가 「찾지 못했다」로 나옴)
