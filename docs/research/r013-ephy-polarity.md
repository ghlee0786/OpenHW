# R-013 SG2002 내장 EPHY — 10BASE-T 자동 극성 보정 · Auto MDI/MDI-X

- 배정: orch t18r R-013 · 작성 research t18s · 2026-11-26
- 배경: 캐리어 RJ45 쪽 MDI P/N 맞바꿈 예정(O-46)

## 결론

| 기능 | 판정 | 근거 |
|---|---|---|
| **Auto MDI/MDI-X** | **지원 (문서 근거 있음)** | TRM v1.02 18.2.2 「Supports the automatic movement and flip function of Ethernet line crossover lines or direct lines.」 (인쇄 340쪽 · PDF 369쪽). 드라이버가 이 기능을 끄는 설정은 없다 |
| **10BASE-T 자동 극성 보정** | **미확인 — 근거 없음** | TRM · 데이터시트 · HDG 어디에도 polarity 언급이 없다. EPHY 레지스터 설명이 TRM에 없다(주소 범위 0x03009000–0x03009FFF만 있음). SDK 드라이버는 극성 관련 레지스터를 쓰지 않는다 |

- TRM 문구의 「flip」이 극성 반전을 뜻하는지는 문장으로 가릴 수 없다. 「crossover lines or direct lines」에 걸려 있어 **MDI/MDI-X 교차 전환으로만** 해석한다.
- **설계 판단(O-46):**
  - 100BASE-TX 데이터는 MLT-3 위에 NRZI로 실린다. 신호의 부호가 아니라 전이 유무로 비트를 정하므로, 쌍 안의 P/N 반전에 원리상 영향을 받지 않는다. 이것은 원리에 근거한 판단이고, 이번에 문서로 확인하지는 않았다.
  - **10BASE-T 데이터와 자동 협상 링크 펄스(NLP/FLP)는 극성의 영향을 받는다.** 이것을 받아내려면 PHY의 자동 극성 보정이 필요한데, SG2002에서는 그 근거를 찾지 못했다.
  - 따라서 P/N을 맞바꾸면 10M 링크와 자동 협상이 PHY의 문서화되지 않은 동작에 기대게 된다. **배선상 가능하면 맞바꾸지 않는 쪽을 기본값으로 권한다.** 맞바꾼다면 첫 보드에서 아래 시험 T1–T4를 통과해야 확정한다.

## 근거 상세

### 1. TRM v1.02 (`sg2002_trm_en_v1.02.pdf`, sha256 26ed9508…1bda00)

R-005 레인 t-20261126-165133-a21b 커밋 7bd141e `hardware/datasheets/sophgo/`. 읽기만 했다.

| 쪽 (인쇄 / PDF) | 내용 |
|---|---|
| 340 / 369 | 18.2 EthernetPHY · 18.2.2 Function Description, 4줄:<br>• 「Supports IEEE 802.3 10/100 Base-TX compliant.」<br>• 「Supports automatic negotiation of transmission speed and full-half-duplex working mode.」<br>• 「Supports the automatic movement and flip function of Ethernet line crossover lines or direct lines.」<br>• 「Supports Ethernet WOL (Wake on Lan) function.」<br>18.2.3은 블록 그림뿐이다(「transmission and reception signals are connected to the RJ45 standard interface through a transformer」) |
| 333 / 362 | 18.1 MAC 절. 「Ethernet MAC0 supports built-in EPHY function」 — MAC 레지스터(Reg_MdioAddr 등)만 있고 **EPHY 내부 레지스터 표는 없다** |
| 52쪽 부근 (PDF) | 핀 EPHY_RXN/RXP/TXN/TXP · EPHY_RTX |

- 전문에서 `polarity` · `MDI-X` · `MDIX` · `auto-polarity`를 검색했다. EPHY 관련 결과는 0건이었다(나온 polarity는 GPIO · RTC · SPI · VO 항목뿐).

### 2. 데이터시트 · HDG (같은 폴더, docx 본문 추출)

| 문서 | 내용 |
|---|---|
| `01_SG2002_Datasheet_V1.0_EN.docx` (sha256 59b53739…18d0) | 단락 314–315: 「Ethernet MAC with built-in 10/100Mbps Fast Ethernet Transceiver can work in 10/100Mbps full duplex or half duplex mode」. MDI-X나 극성에 대한 언급은 없다 |
| `02_SG2002_Hardware_Design_User_Guide_EN.docx` (sha256 9774fd0d…9655) | 단락 467–470 (EPHY-RJ45):<br>• 「built-in 100MB PHY, which can be directly connected to the network port」<br>• 차동선에 5.1Ω 이하 직렬 저항을 둔다<br>• RC를 쓰지 않는다<br>단락 690–697 (RJ45 배선): TX0/TX1 · RX0/RX1을 각각 GND로 감싼다.<br>**P/N 교체 허용 여부에 대한 언급은 없다** |

### 3. SDK EPHY 드라이버 (reCamera-OS 0.2.4, CHANGELOG 2026-03-17, docker 볼륨 `openhw-recamera-sdk`를 읽기 전용으로 마운트)

| 파일 | sha256 | 확인한 것 |
|---|---|---|
| `src/linux_5.10/drivers/net/phy/cvitek.c` (471줄) | 6f0d5744…a5fc81 | 드라이버 이름 「CVITEK CV182XA」, phy_id 0x00435649 (444–447줄). `cv182xa_phy_config_init`(147줄~)은 MII 페이지(0x7c)를 바꿔 가며 아날로그 보정을 쓴다:<br>• MLT3 위상 코드(page16/17, 239–267줄)<br>• Link Pulse 파형(page10, 276–310줄)<br>• TP_IDLE(page11)<br>• 10BaseT Data 파형(page13–16, 330–370줄)<br>• LED(page1)<br>• LPF/HPF(page18, 385–405줄)<br>이어서 `0x090e`로 자동 협상을 시작하고(410줄) 전이중을 강제한다(414줄). **MDI/MDI-X · 극성 설정 코드는 없다.** `mdix` · `polar` · `cross` · `swap` 검색 결과 0건 |
| `src/u-boot-2021.10/drivers/net/phy/cvitek.c` (361줄) | d1dbb180…79c7b5 | `cv182xa_ephy_init`(27줄~)도 같은 초기화 순서다(288줄 `0x03009800 ← 0x090e`). 극성 · MDI-X 코드는 없다 |
| `src/linux_5.10/drivers/net/ethernet/stmicro/stmmac/dwmac-cvitek.c` | — | `ephy_base_reg` · `ephy_top_reg`를 매핑하고 APB 접근을 고른다(50–66줄). 극성 · MDI-X 코드는 없다 |

- 결론: 두 기능 모두 드라이버가 건드리지 않는다. 따라서 동작은 **PHY 하드웨어의 리셋 기본값**에 따르며, 그 기본값은 문서에 없다. 소스 트리에 git 메타데이터가 없어 커밋 해시 대신 파일 sha256을 적었다.

### 4. 외부 참고 (SG2002가 아닌 일반 사항)

- TI DP83848-EP 데이터시트 「Automatic Link Polarity Detection and Correction」에 일반 PHY의 동작이 나온다. 뒤집힌 링크 펄스를 연속 3개 받으면 극성 반전으로 판정하고 안에서 보정한다(10BASE-T): https://www.ti.com/document-viewer/DP83848-EP/datasheet/automatic-link-polarity-detection-and-correction-snls3414776
- TI E2E 스레드는 「10BASE-T PHY는 IEEE 802.3상 자동 극성 보정을 지원해야 한다」는 Microchip 앱노트를 인용한다: https://e2e.ti.com/support/interface-group/interface/f/interface-forum/1251181/dp83867e-polarity-detection-and-correction
  - 2차 출처다. 규격 원문과 조항 번호는 확인하지 않았다.
- SG2002 · CV18xx EPHY의 극성 동작을 다룬 공개 사례는 찾지 못했다(웹 검색 1회).

## 맞바꾼다면 — 첫 보드 확인 시험

| # | 시험 | 합격 기준 | verifiable |
|---|---|---|---|
| T1 | 일반 스위치에 자동 협상으로 연결 | `ethtool eth0` → 100Mb/s Full, Link detected: yes · `ping` 1,000회 손실 0 | 예 |
| T2 | 10M 강제: `ethtool -s eth0 speed 10 duplex full autoneg off` (상대 포트도 10M 고정) | 링크 업 · `ping` 1,000회 손실 0 · `ip -s link`에 RX 오류 0 | 예 |
| T3 | 10M만 광고하는 상대와 자동 협상: `ethtool -s eth0 advertise 0x002` | 10Mb/s로 협상 성공 | 예 |
| T4 | 직결 케이블과 크로스 케이블을 각각 PC에 직접 연결 | 두 경우 모두 T1 기준 통과 (Auto MDI-X) | 예 |

- T2나 T3가 실패하면 자동 극성 보정이 없다는 뜻이다. 그때는 다음 판에서 P/N을 원래대로 되돌린다. 100M만 쓰는 운용이면 T1만으로 계속 쓸 수 있다.

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| E1 | TRM 「flip」의 해석 | MDI/MDI-X 교차 전환으로만 본다 (극성 보정의 근거로 쓰지 않음) | 문장이 「crossover lines or direct lines」에 걸려 있다. 극성을 뜻한다는 별도 근거가 없다 | 극성 보정까지 포함한다고 보고 P/N 교체를 승인한다 (위험) |
| E2 | 극성 보정 판정 | **미확인**으로 둔다 | 문서 · 레지스터 표 · 드라이버 모두에 근거가 없다 | 일반 PHY 관례로 「있음」 가정 |
| E3 | O-46 권고 | 배선이 허락하면 P/N을 맞바꾸지 않는다. 맞바꾸면 T1–T4로 확정 | 100M는 원리상 안전하다. 10M와 FLP만 위험이 남는다. 되돌리기는 다음 판 수정으로 쉽다 | 그대로 맞바꾸고 100M 전용으로 운용 |

## 돌린 명령

- `pdftotext` / PyMuPDF로 TRM 본문 추출 후 grep — 종료 0
- docx 본문 추출 (`python -I` zipfile) — 종료 0
- `docker run --rm -v openhw-recamera-sdk:/sdk:ro alpine:3.20 …` (find · grep · cat · sha256sum, 읽기 전용) — 종료 0
- 저장소 검사 명령: 이 문서만 바꿔서 돌리지 않음
