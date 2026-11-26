# R-008b 남은 MPN 확인 (C-004 README 16절 「남은 확인」 + V-004b/C-005 새 품번)

- 배정: orch t18r R-008b.
  - 조정: C-005로 부품이 다시 바뀌었으므로 **BOM 재추출은 C-005 최종 커밋을 받은 뒤** 한다. 이 문서는 MPN 확인만 담는다.
- 조사자 research t18s · 확인일 **2026-11-26** · LCSC 공개 JSON(`productModel`로 검증)과 Digi-Key 공개 페이지 기준. 구매·견적·업로드·문의는 하지 않았다.
- **최종:** orch가 최종 회로도로 **355ab3e**(C-006: 전면 R17 100k→10k만 바뀜, b3b376a 대비)를 알려 왔다. 그 커밋으로 두 보드 BOM을 다시 내보내 `bom-full.csv`를 갱신했다(4절).
  - b3b376a로 내보낸 BOM과 비교한 차이는 전면 R17 값 하나뿐이었다(스크립트 비교 결과).
  - 중간에 C-004(58eb49b)로도 한 번 내보냈다(종료 코드 0/0). 그 결과는 반영하지 않았다.

## 1. C-004 16절 「남은 확인」

| 항목 | 결론 (1안) | LCSC · 재고 · 가격 (USD) | 차선 | 근거 | 상태 |
|---|---|---|---|---|---|
| 전면 U1 RT9013-28GB (2.8V) | **Richtek RT9013-28GB 재고 있음** | C2972227 · 2,730 · 5+ 0.1778 / 50+ 0.1412 | 재고가 있어 대체 불필요 | DS9013-10 (April 2011, LCSC 사본) | 확인됨 |
| 캐리어 C1 47µF/35V 전해 (리플 정격) | **ROQANG RVT1V470M0605** (6.3×5.4, 105°C, 리플 56mA rms@120Hz) | C72522 · 142,740 · 20+ 0.0304 / 200+ 0.0246 | ROQANG RVE1V470M0605 저임피던스 (C131122, 170mA rms@100kHz, 0.85Ω) | 제조사 표 | 확인됨 |
| 캐리어 L1 10µH Isat ≥6A | **Bourns SRP7028A-100M** 유지 — Isat **6A** (20% 강하 기준), Irms 3.5A → 조건 ≥6A를 **경계값으로 충족** | C2687402 · 2,675 · 1+ 0.8325 / 10+ 0.6674 | 여유가 필요하면 Isat가 더 큰 같은 크기 부품을 따로 조사해야 한다 | Bourns SRP7028A REV.11/26 | 확인됨 |
| 전면 L1·L2 47µH (Irms ≥1.3A, Isat ≥2A) | **Bourns SRN6045TA-470M** — DCR 200mΩ, Irms 1.60A, Isat 2.00A (typ, 30% 강하) | C5151734 · 3,990 · 5+ 0.3642 / 50+ 0.2886 · Digi-Key 11,160 (USD 0.47) | Ceaiya CR6045H-470M (C7588777, Isat 2.0A, Irise 1.3A — 하한값, 패드 미비교) | Bourns REV.06/24 (위치 기반 추출로 행 밀림을 바로잡음) | 확인됨 |
| 캐리어 C7·C8·C20 22µF/25V X7R 1210 · DC 바이어스 | **Samsung CL32B226KAJNNNE** | C309062 · 60,309 · 1+ 0.1881 / 10+ 0.1441 (JLC Extended — 1210 X7R은 Basic에 없음) | Murata GRM32ER71E226KE15L (C21397 · 19,420, DC 바이어스 미확인) | Samsung 공식 특성 데이터 `weblib.samsungsem.com/mlcc/mlcc-ec-data-sheet.do?partNumber=CL32B226KAJNNN` (25°C, 120Hz, 0.5Vrms) | 확인됨 |
| ↳ DC 바이어스 판정 | **5V에서 ΔC −20.52% → 개당 17.49µF**, 3개 **52.5µF ≥ 44µF 달성** · 공차 −10%를 넣으면 47.2µF로 달성 · 온도 −15%까지 겹치면 약 40.1µF로 미달(추정) | — | — | 같은 데이터 · 3.3V 20.39µF · 6V 15.80µF | 25°C 조건은 확인됨 · 최악 조건은 추정 |
| 캐리어 J2 XKB DC-005-5A-2.0 풋프린트 (`openhw:BarrelJack_XKB_DC-005-5A-2.0_Horizontal`) | **핀·슬롯은 도면과 일치, 외곽은 수정 필요** | — | — | XKB 도면 Rev A1 (2025-04-22) https://datasheet.lcsc.com/datasheet/pdf/781816078c0f2c3415b95730e83b719f.pdf?productCode=C381116 | 확인됨 (아래 표) |
| 보드 간 GH 6P 케이블 (GHR-06V-S + SSHL-002T-P0.2, AWG26, 1:1) | **양끝 하우징이 달린 1:1 AWG26 기성 조립품은 없다 → 자가 크림프 조립** (하우징 ×2 + 단자 ×12 + AWG26 전선) | GHR-06V-S C22465348 · 83,980 · 10+ 0.0621 / SSHL-002T-P0.2 C189897 · 414,400 · 100+ 0.0109 / 헤더 SM06B-GHS-TB(LF)(SN) C133065 · 33,570 · 5+ 0.2857 | JST 프리크림프 리드 **AGHGH28K51** (양끝 SSHL-002T-P0.2, **28AWG**, 50.8mm, Digi-Key 455-3072-ND · 44,430 · USD 0.43) — AWG26 조건 미충족(GH 1.0A 정격은 AWG26 기준) | JST eGH · Farnell JST 리드 도면 https://www.farnell.com/datasheets/4803930.pdf · Digi-Key 「AGHGH26」 검색 0건 | 확인됨 (기성품이 없다는 것은 검색 범위 안 결과) |

### XKB DC 잭 풋프린트 대조 (핀1 원점, −x = 잭 앞면)

| 항목 | 풋프린트 | 도면 (A1) | 판정 |
|---|---|---|---|
| 핀1→2 / 핀1→3 / 핀3 측면 | 5.90 / 3.00 / 4.70 | 5.90 / 3.00 / 4.70 | 일치 |
| 슬롯 | 1·2번 1.0×3.5 (축에 수직), 3번 3.5×1.0 (축 방향) | 3-1.0×3.5, 같은 방향 | 일치 |
| Fab 앞면 / 뒤끝 / 길이 | −13.7 / +0.8 / 14.5 | −13.6 / +0.4 / 14.00 | **불일치 → −13.6 ~ +0.4로 수정** |
| Fab 폭 | ±4.5 | 9.00 | 일치 |
| Courtyard | x −14.0~+1.0, y ±4.75, 핀3 돌출부 x −5~−1 | — | 몸체는 감싸지만 **패드3이 양쪽 0.1, 패드1 모서리가 경계 밖** |
| 실크 | x=0.9 선 끝이 패드1 위, y=4.6 선 끝이 패드3 위 | — | 0.1~0.2 겹침 (경미) |
| 3D 모델 | KiCad 일반 BarrelJack | XKB 몸체 | 미검증 |

→ 몸체 외곽은 KiCad 원본 값이 남아 있다. Fab·Courtyard·실크를 도면 기준으로 고치는 것은 라이브러리 소유자 몫이다.

## 2. C-004 노트와 다른 점 (C-005에서 이미 반영됐을 수 있음)

| 노트 | 사실 | 근거 |
|---|---|---|
| F1 「candidate Littelfuse 0437003.WR (1206 Slo-Blo 3A)」 | **0437003.WR은 Fast-Acting이다** (데이터시트 제목 「437 Series – 1206 Fast-Acting Fuse」, 32V, 50A, I²t 0.506A²s) | https://www.farnell.com/datasheets/2722487.pdf (Revised 12/14/17) |
| D1·D2 「Vishay SS24-E3/61T (SMA)」 | **SS24 계열은 SMB이고, 61T 포장 코드가 없다.** SMA에 61T를 쓰는 것은 SS24S-E3/61T(C84317)다. C-005는 SSA24-M3/61T로 바꿨다(3절) | Vishay SS22 데이터시트 https://www.vishay.com/docs/88748/ss22.pdf · SS22S https://www.vishay.com/docs/89008/ss22s.pdf |

## 3. V-004b / C-005 새 품번 재고

| 품번 | LCSC · 재고 · 가격 (USD) | Digi-Key | 근거 | 상태 |
|---|---|---|---|---|
| 캐리어 D7 **SMBJ6.0A** | **Littelfuse SMBJ6.0A C83270 · 2,160** · 5+ 0.1884 / 50+ 0.1471 (JLC Extended) · 차선 Vishay SMBJ6.0A-E3/52 C553974 · 500 | Littelfuse SMBJ6.0ALFCT-ND · 934 · USD 0.53 / Vishay SMBJ6.0A-E3/52GICT-ND · **12,337** · USD 0.56 | 600W, VRWM 6.0V, VBR 6.67~7.37V @10mA, VC 10.3V @58.3A · Littelfuse LCSC 사본 「Revised JC.07/04/25 v4」 · Vishay Doc 88392 Rev 09-Jan-2024 | 확인됨 (Littelfuse 원본은 403이라 LCSC 사본 기준) |
| 전면 D1·D2 **Vishay SSA24-M3/61T** | C7369179 · **0** (JLC 0) · 1+ 0.2042 | SSA24-M3/61T-ND · **0** (「not normally stocked」, 리드타임 15주) | SMA (DO-214AC), VRRM 40V, IF(AV) 2A, VF 0.49V max @2A · Doc 89280 Rev 24-Apr-2020 | 확인됨 → **재고가 없어 BOM 1안은 SS24S-E3/61T (C84317 · 14,200, DK 30,046)** (분기 B5) |
| 캐리어 F1 **Bel Fuse 0685T3000-01** | C5456894 · 5,346 · 1+ 0.4458 / 10+ 0.3475 (JLC Extended) | 5923-0685T3000-01CT-ND · **308,446** · USD 0.49 | C1T 「Slow Blow」, 63V AC/DC, 차단 50A, 3A: 냉간저항 0.050Ω, I²t @10In 1.64A²s, 최대 0.70W · Rev. C1T Feb2025 https://www.belfuse.com/media/datasheets/products/circuit-protection/ds-cp-c1t-series.pdf | 확인됨 |
| 캐리어 C22 10nF 0402 (새로 추가) | Samsung CL05B103KB5NNNC C15195 · 405,900 · 0.0033 / 0.0024 (JLC Basic) | — | R-008 조회값 | 확인됨 |
| DMG1012T (1개 추가) | C20512 (DMG1012T-7) · 19,265 · 5+ 0.0905 / 50+ 0.0725 | — | R-008 조회값 | 확인됨 (R-008) |
| 전면 J2 Molex PicoBlade 53261-0271 | C177225 · 10,160 · 5+ 0.148 | WM7620 · 38,882 · USD 0.60 | R-009 ② | 확인됨 (R-009). CLA216 리드 계열은 아직 추정 — 실물 확인 게이트 유지 |
| ALS-PT19 풋프린트 | C146233 · 18,110 | — | R-009 ⑨: 패드 0.8×0.8 @ ±0.75, Fab 1.7×0.8, 핀1 콜렉터 (Everlight DLS-0000039 Rev.8) | 확인됨 (C-005 풋프린트와 대조는 C-005 커밋을 받은 뒤 한다) |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | GH 6P 케이블 | 자가 크림프 (GHR-06V-S + SSHL-002T-P0.2 + AWG26 전선, 전선 MPN 미확정) | AWG26 1:1 기성품이 없다. 계약 정격(1.0A)이 AWG26 기준이다 | JST AGHGH28K 리드(28AWG)로 조립 — 정격 여유를 다시 검토해야 한다 · JST 맞춤 제작은 외부 문의라 사용자 지시가 필요하다 |
| B2 | 22µF 1210 | CL32B226KAJNNNE ×3 | Samsung 공식 데이터로 5V에서 52.5µF | 최악 조건(공차 + 온도)이 걱정되면 4개로 늘린다(회로도 소유자 판단) |
| B3 | SRP7028A-100M | 유지 | Isat 6A로 조건을 경계값으로 충족한다 | Isat가 더 큰 부품을 따로 조사 |
| B4 | BOM 재추출 기준 | **C-005 355ab3e** (orch 지정) | 최종 회로도 | — |
| B5 | 전면 D1·D2 MPN | **Vishay SS24S-E3/61T (C84317)** | 회로도 노트의 SSA24-M3/61T는 LCSC·Digi-Key 모두 재고 0이고 리드타임이 15주다. SS24S는 같은 Vishay SMA 40V 2A이고 재고가 있다 | SSA24-M3/61T (재고가 들어오면) · MDD SS24 (C50645) |
| B6 | 캐리어 D7 | Littelfuse SMBJ6.0A (LCSC 2,160) | LCSC 턴키 재고 | Vishay SMBJ6.0A-E3/52 (DK 12,337) |

## 4. BOM 재추출 (C-005 355ab3e) 과 R-008 (dbafdc8) 대비 차이

### 4.1 명령과 결과

| 명령 | 종료 코드 | 결과 |
|---|---|---|
| `kicad-cli sch export bom --fields 'Reference,Value,Footprint,${QUANTITY},${DNP},Manufacturer,MPN,LCSC,Datasheet,Description,Note,Cable' --group-by 'Value,Footprint,MPN,${DNP}' carrier.kicad_sch` | **0** | 부품 98 = 시험점 26 + DNP 7 + **실장 65** (R-008: 91 / 실장 58) |
| 같은 명령, `front.kicad_sch` | **0** | 부품 85 = 시험점 23 + DNP 12 + **실장 50** (R-008: 78 / 실장 44) |
| `python -I build_bom_c.py bom-full.csv` (세션 임시 폴더의 생성기) + R-009 비고 재적용 | **0** | `bom-full.csv` **헤더 제외 99행 · 21열** (python csv로 확인). 매핑되지 않은 그룹 0 |

- C-005 레인(t-20261126-165741-b193)은 읽기만 했다. ERC는 다시 돌리지 않았다(C-005 커밋 메시지 「ERC 0」 인용).
- **보드 밖 행 변화:** FFC1 1행을 지우고 GH 케이블 3행(CBL1 하우징 · 단자 · 전선)을 넣었다. AC1에 R-009 ① 품번을 넣었다.

### 4.2 참조 지정자별 차이 (시험점 제외, 36건)

| 보드 | 참조 | 구분 | R-008 (C-002, dbafdc8) | C-005 (355ab3e) |
|---|---|---|---|---|
| 캐리어 | C1 | 변경 | 47uF/25V · CP_Elec_6.3x5.4 | 47uF/35V · CP_Elec_6.3x5.4 |
| 캐리어 | C7 | 변경 | 22uF/10V · C_1206_3216Metric | 22uF/25V X7R · C_1210_3225Metric |
| 캐리어 | C8 | 변경 | 22uF/10V · C_1206_3216Metric | 22uF/25V X7R · C_1210_3225Metric |
| 캐리어 | C13 | 변경 | 10uF · C_0603_1608Metric | 1uF · C_0603_1608Metric |
| 캐리어 | C19 | 추가 | — | 75pF C0G 50V · C_0402_1005Metric |
| 캐리어 | C20 | 추가 | — | 22uF/25V X7R · C_1210_3225Metric |
| 캐리어 | C21 | 추가 | — | 100nF · C_0402_1005Metric |
| 캐리어 | C22 | 추가 | — | 10nF · C_0402_1005Metric |
| 캐리어 | D7 | 추가 | — | SMBJ6.0A · D_SMB |
| 캐리어 | F1 | 변경 | 3A · Fuse_1206_3216Metric | 3A slow-blow 63V · Fuse_1206_3216Metric |
| 캐리어 | J2 | 변경 | DC-005-5A-2.0 · BarrelJack_Horizontal | DC-005-5A-2.0 · BarrelJack_XKB_DC-005-5A-2.0_Horizontal |
| 캐리어 | J7 | 변경 | FPC 10P 1.0mm · TE_1-84952-0_1x10-1MP_P1.0mm_Horizontal | JST GH 6P (board link) · JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal |
| 캐리어 | L1 | 변경 | 10uH Isat>=4A · L_Bourns_SRP7028A_7.3x6.6mm | 10uH Isat>=6A · L_Bourns_SRP7028A_7.3x6.6mm |
| 캐리어 | R9 | 변경 | 20k · R_0402_1005Metric | 200k · R_0402_1005Metric |
| 캐리어 | R10 | 변경 | 10k · R_0402_1005Metric | 100k · R_0402_1005Metric |
| 캐리어 | R22 | 추가 | — | 47k · R_0402_1005Metric |
| 캐리어 | R23 | 추가 | — | 100k · R_0402_1005Metric |
| 전면 | C10 | 변경 | 100nF · C_0402_1005Metric · DNP | 100nF · C_0402_1005Metric |
| 전면 | C14 | 변경 | 10uF/25V · C_1206_3216Metric | 10uF/50V X7R · C_1206_3216Metric |
| 전면 | C16 | 변경 | 10uF/25V · C_1206_3216Metric · DNP | 10uF/50V X7R · C_1206_3216Metric · DNP |
| 전면 | C18 | 추가 | — | 1uF · C_0402_1005Metric |
| 전면 | D1 | 변경 | SS24 (40V 2A) · D_SMA | SS24 (40V 2A, SMA) · D_SMA |
| 전면 | D2 | 변경 | SS24 (40V 2A) · D_SMA · DNP | SS24 (40V 2A, SMA) · D_SMA · DNP |
| 전면 | D3 | 추가 | — | BAT54WS · D_SOD-323 |
| 전면 | J2 | 변경 | ICR (CLA216 JST 1.25mm 2P) · JST_GH_SM02B-GHS-TB_1x02-1MP_P1.25mm_Horizontal | PicoBlade 53261-0271 (CLA216 lead) · Molex_PicoBlade_53261-0271_1x02-1MP_P1.25mm_Horizontal |
| 전면 | J4 | 변경 | FPC 10P 1.0mm · TE_1-84952-0_1x10-1MP_P1.0mm_Horizontal | JST GH 6P (board link) · JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal |
| 전면 | L1 | 변경 | 68uH Isat>=1.5A · L_Bourns_SRN6045TA | 47uH Irms>=1.3A Isat>=2A · L_Bourns_SRN6045TA |
| 전면 | L2 | 변경 | 68uH Isat>=1.5A · L_Bourns_SRN6045TA · DNP | 47uH Irms>=1.3A Isat>=2A · L_Bourns_SRN6045TA · DNP |
| 전면 | Q4 | 변경 | ALS-PT19 (alt) · LED_0805_2012Metric · DNP | ALS-PT19 (alt) · Everlight_ALS-PT19_1.7x0.8mm · DNP |
| 전면 | Q6 | 추가 | — | DMG2305UX · SOT-23 |
| 전면 | Q7 | 추가 | — | DMG1012T · SOT-523 |
| 전면 | R16 | 추가 | — | 10k · R_0402_1005Metric · DNP |
| 전면 | R17 | 추가 | — | 10k · R_0402_1005Metric |
| 전면 | U1 | 변경 | RT9013-33GB · SOT-23-5 | RT9013-28GB · SOT-23-5 |
| 전면 | U4 | 변경 | AL8860MP-13 · MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm | AL8860MP-13 · Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860 |
| 전면 | U5 | 변경 | AL8860MP-13 · MSOP-8-1EP_3x3mm_P0.65mm_EP1.5x1.8mm · DNP | AL8860MP-13 · Diodes_MSOP-8EP_3x3mm_P0.65mm_EP1.7x2.0mm_AL8860 · DNP |

- **시험점:** 전면 TP2 이름이 FRONT_3V3에서 FRONT_2V8로 바뀌었다. 전면 TP23 CAM_1V8이 새로 들어갔다. 시험점은 부품이 아니라 위 표에서 뺐다.
- **BOM 품번 반영 (위 차이에 대응):**
  - 저항·커패시터: 75pF YAGEO C107010 · 22µF 1210 Samsung CL32B226KAJNNNE C309062 · 10µF/50V Samsung CL31B106KBHNNNE C89632 · 47µF/35V ROQANG C72522 · 200k C25764
  - 보호 소자: SMBJ6.0A C83270 · Bel 0685T3000-01 C5456894 · BAT54WS-7-F C124205
  - 트랜지스터·전원: DMG2305UX-7 C150470 · DMG1012T-7 C20512 · RT9013-28GB C2972227
  - 인덕터·다이오드: SRN6045TA-470M C5151734 · SS24S-E3/61T C84317 (B5)
  - 커넥터: Molex 53261-0271 C177225 · JST SM06B-GHS-TB C133065
  - 보드 간 케이블: GHR-06V-S C22465348 + SSHL-002T-P0.2 C189897

## 확인 못 한 것

- **커패시터:** Murata·TDK 22µF의 DC 바이어스 값
- **인덕터:** SRN6045TA와 CR6045H의 권장 패드 비교
- **케이블:**
  - Digi-Key에서 SSHL-002T-P0.2 소량 포장의 재고
  - JST 공식 양끝 하우징 조립 케이블 시리즈가 있는지 (검색 범위 안에서는 없었다)
  - AWG26 전선 MPN
- **데이터시트:** RT9013 최신 리비전 (LCSC 사본은 2011년판)
