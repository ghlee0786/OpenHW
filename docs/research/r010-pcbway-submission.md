# R-010 PCBWay 제조·조립 제출 요건 (README 단계 6 준비)

- 배정: orch t18r R-010 · 조사자 research t18s · 확인일 **모두 2026-11-26**
- 방법: PCBWay 공개 페이지(Help Center·FAQ·capabilities·주문 폼 화면·템플릿 파일)와 공식 KiCad 플러그인 GitHub 소스만 읽었다. **견적 요청·파일 업로드·가입·로그인·문의는 하지 않았다.**
- 겹치는 문서: 제조 규칙·적층·패널·미세 피치 근거는 P-002 `hardware/pcb/fab-rules-pcbway.md`(레인 t-20261126-163344-acdf, ea8d1f6)에 있다. 이 문서는 **제출 파일 형식과 KiCad 10 내보내기**를 다룬다.
- 표기: **확인됨** = 페이지 원문 · **불일치** = PCBWay 문서끼리 값이 다름 · **미확인** = 근거 없음 · **열람 불가** = 공개 페이지에 없음(로그인·주문 후 안내로 보임)

## 결론

1. **PCBA 필수 파일은 Gerber + Centroid(좌표) + BOM이다** — 「We need Gerber files, Centroid data and BOM for your PCBA orders.」 (https://www.pcbway.com/assembly-faq.html)
2. **회전 보정 정책은 공개된 것이 없다.**
   - PCBWay는 「top point of view」 기준 0~360° 회전만 요구한다. IPC-7351 0° 기준이나 패키지 방향 보정은 언급이 없다.
   - 공식 KiCad 툴킷도 KiCad 회전값을 **보정 없이** 그대로 쓴다.
   - 그래서 **극성·1번 핀을 실크로 표시하고 조립도를 함께 내는 것**을 기본 방어책으로 둔다(PCBWay 공식 요구).
3. **「Standard/Advanced PCBA」 같은 조립 등급은 공개 페이지에 없다.** 주문 폼에는 부품 공급 방식, 조립 면, X-ray 횟수, BGA/QFP 개수만 있다. 우리 보드에는 BGA가 없고, 0.4/0.5mm 피치 커넥터와 QFN/WSON/USON이 있다.
4. **PCBWay 문서끼리 값이 다른 것:** 좌표 단위(mm/mil), 드릴 PTH·NPTH 합침 여부, Protel 확장자, 위치 파일 면별 분리, MOQ, BGA 피치. 아래에서 각각 하나를 고르고(분기 S1~S6) 근거를 남겼다.
5. **보드 크기:** 30×30mm(P-002 외형)는 「50×100mm보다 작으면 패널」 조건에 해당한다 → **조립용 패널화가 필요하다**(P-002 §A와 같은 결론).

## 1. PCBA 제출 파일 요건

### 1.1 BOM

| 요건 | 값 / 원문 | URL | 상태 |
|---|---|---|---|
| 형식 | 「.xls, xlsx or .csv」 · 「We do not accept BOM files in pdf」 | https://www.pcbway.com/assembly-file-requirements.html · https://www.pcbway.com/smt_ordering_guide.html | 확인됨 |
| 필수 열 (위탁) | 「Line#」「Quantity Per Part Number」「Reference Designator」「Part Number」「Part Description」「Package」「Type (Surface mount, Thru-hole or Hybrid)」 | assembly-file-requirements | 확인됨 |
| 추가 열 (턴키·부분 턴키) | 「Manufacturers Name」「Manufacturers Part Number」「Distributors Part Number」 | 같음 | 확인됨 |
| **공식 템플릿** | https://www.pcbway.com/img/images/pcbway/Sample_BOM_PCBWay.xlsx?v=1.1 — 6행 머리글: `Item #` · `*Designator` · `*Qty` · `Manufacturer` · `*Mfg Part #` · `Description / Value` · `*Package/Footprint ` (끝 공백 포함) · `Type` · `Your Instructions / Notes` | 템플릿 직접 열람 | 확인됨 |
| 참조 지정자 | 템플릿 예시가 `U2,U4` · `R16, R31`처럼 콤마로 구분한다. 규정 문장은 없다 | 템플릿 | 예시만 확인 |
| **DNP** | 템플릿은 `Type` 열에 `DNS`를 쓴다 · 도움말: 「Components should not be purchased or soldered so you can mark them as DNP or DNS.」 | 템플릿 · https://www.pcbway.com/helpcenter/pcb_assembly_ordering/Common_factors_that_affect_the_efficiency_of_Assembly_service_.html | 확인됨 |
| 턴키·위탁 구분 | BOM 열이 아니라 **주문 폼**에서 고른다: 「Turnkey / Kitted or Consigned / Combo (You supply some parts we do the rest)」 · 행별 지시는 `Your Instructions / Notes` 열에 쓴다 | https://www.pcbway.com/quotesmt.aspx | 확인됨 |
| BOM과 좌표가 다를 때 | 「Normally we purchased and solder the parts according to your BOM. And centroid file is just used to confirm the position」 | helpcenter/SMT_Engineering_Questions/How_to_avoid_the_problem_that_missing_to_solder_the_parts_on_centroid_file_but_not_show_on_BOM_.html | 확인됨 → **BOM이 기준**이다 |

### 1.2 Centroid (좌표, Pick-and-Place)

| 요건 | 값 / 원문 | URL | 상태 |
|---|---|---|---|
| 내용 | 「the reference designator, X and Y position, rotation and side of Board (Top or Bottom)」 · 「Only surface mounting parts are listed in the Centroid」 · 「THT designators can be excluded」 | assembly-file-requirements · smt_ordering_guide | 확인됨 |
| 템플릿 | https://www.pcbway.com/img/images/pcbway/a-sample-of-PCBWay-Centroid-File.txt — `Designator Footprint Mid X Mid Y Ref X Ref Y Pad X Pad Y TB Rotation Comment` (mil, T/B) | 템플릿 | 확인됨 |
| 단위 | 도움말: 「its format can be excel, .txt or .pos … please set the unit to be mm」 ↔ 템플릿은 mil | helpcenter/pcb_assembly_ordering/What_files_are_requested_for_assembly_production_.html | **불일치** → S2 |
| 원점 | 「located at the lower left corner」 · 「Even the reverse side of the board uses the lower left corner as the origin's reference point」 | helpcenter/design_instruction/How_to_create_a_Centroid_File_from_Eagle__Altium_Sprint_Layout_and_ORCAD_.html | 확인됨 |
| 회전 | 「referenced from a top point of view … Both the top and reserve side components use a top point of view」 · 「0 to 360 degree value」 · IPC-7351 언급 없음 | 같음 | 확인됨 · **보정 정책은 미확인** |
| 뒷면 X 미러 | 하지 않는다. 뒷면도 왼쪽 아래가 원점이고, KiCad 9 튜토리얼 화면에서 「Use negative X coordinates for footprints on bottom layer」가 해제돼 있다 | helpcenter/generate_gerber/How_to_Export_Gerber__BOM__and_Pick_and_Place_Files_in_KiCad_9_0.html | 확인됨 (화면 기준) |
| 면별 분리 | 「Pick and place file for top and bottom side are together, which cause confusion」(문제 사례로 듦) ↔ 공식 툴킷은 한 파일에 side 열로 낸다 | helpcenter/Assembly_files_problems/Top_13_suggestions_for_solving_PCB_Assembly_files_problems.html | **불일치** → S3 |
| KiCad 파일 | 「.pos」 허용 · KiCad 9 화면: Format CSV, Units Millimeters, 「Use drill/place file origin」 체크 | 위 두 페이지 | 확인됨 |

### 1.3 Gerber·드릴

| 요건 | 값 / 원문 | URL | 상태 |
|---|---|---|---|
| Gerber 형식 | 「Copper, silkscreen, and solder paste layer gerbers in RS274X format」 · 조립에 필요한 최소 층: 「Silkscreen, Copper (Track) and Solder Paste」 | assembly-file-requirements | 확인됨 |
| KiCad 층 이름 | KiCad 이름을 인식한다(`F_Cu.gbr` · `B_Cu.gbr` · `F_Silkscreen.gbr` · … · `Edge_Cuts.gbr`) · KiCad 9 화면: 「Use Protel filename extensions」 해제, X2 해제, 좌표 4.6 mm ↔ 2021 블로그는 Protel 확장자 권장(옛 글) | helpcenter/generate_gerber/Gerber_File_Extension_from_Different_Software.html · KiCad 9 글 · blog/PCB_Design_Tutorial/How_to_Export_Gerber_and_Production_Files_in_KiCad.html | 확인됨 (옛 글과는 불일치) → S4 |
| 드릴 | KiCad 9 화면: Excellon, **「PTH and NPTH in single file」 체크(빨간 상자로 강조)**, Absolute, Millimeters, Decimal ↔ 확장자 안내 글은 `NPTH.drl`·`PTH.drl`을 따로 적음 ↔ 공식 툴킷은 분리 출력 | 위 글들 | **불일치** → S5 |
| 외곽 | 「There is no board outline, pls add board outline layer」 (누락 사례) | helpcenter/file_issues/Gerber_files_are_not_completed.html | 확인됨 → Edge_Cuts 필수 |
| 4층 층 순서 | 지시 파일이 아니라 **주문 폼에 적는다**: 「Please fill in the layer order from the top-side view to the bottom-side view according to the layer names in the Gerber file… L1: L2: L3: L4:」 | quotesmt.aspx · helpcenter/layers_issues/No_layer_orders_for_multi_layers_boards.html | 확인됨 |

### 1.4 조립도·극성

| 요건 | 값 / 원문 | URL | 상태 |
|---|---|---|---|
| 극성·1번 핀 | 「Please add polarity cathode or anode mark and pin 1 in silkscreen layer. If you do not want this… send an individual assembly drawing」 | smt_ordering_guide | 확인됨 |
| 조립도 필요 여부 | 「If the silkscreen layer of pcb file is clear, it isn't need to be provided」 | What_files_are_requested… | 확인됨 → 실크가 분명하면 선택이지만 **우리는 낸다**(S6) |

## 2. 위탁(Consigned / Kitted) 부품

| 요건 | 값 / 원문 | URL | 상태 |
|---|---|---|---|
| 포장 | 「We accept parts in Reels, Cut Tape, Tube & Tray, Loose Parts and Bulk.」 · 「SMT parts which are not supplied on reels should be on one continuous strip of tape… do not cut them into strips」 | https://www.pcbway.com/assembly-capabilities.html · https://www.pcbway.com/assembly-special-remind.html | 확인됨 |
| 리더 테이프 | 「reserve a blank tape with a length greater than 50mm… there will be 10-20PCS for each material to be removed」 (2018 사양서) | smt_ordering_guide | 확인됨 |
| 라벨 | 「mark on any individual package or box with the corresponding line number on BOM, manufacturer's part# or customer's part#, quantities. A detailed packing list is preferred」 · 「Each packaging should include part number, package, value… better to add designators」 | assembly-faq · helpcenter/pcb_assembly_ordering/What_issues_should_be_paid_attention_to_for_customer_supplied_components_.html | 확인됨 |
| 여분 | 0603~1206·SOT·SOD·MELF: 「minimum of 50 pieces and… exceed the required quantity by 30 pieces」 · 0201·0402: 「minimum of 100 pieces… exceed… by 50 pieces」 · IC·BGA·QFP·커넥터: 「1-5 pieces」 · 남은 부품은 「will not be returned by default」 | assembly-special-remind · assembly-faq | 확인됨 |
| 배송지 | 공개 페이지에 주소가 없다. 「send components to correct address… add your PCB order number to the package or waybill」만 있다 | 위 도움말 | **열람 불가** |
| 부분 턴키 | 「Yes. This practice is called partial Turn-key.」 · 폼 옵션 이름은 「Combo」 | assembly-faq | 확인됨 |

- **우리 BOM에 대입 (참고):**
  - 위탁 후보 중 Digi-Key 품목(VSMA1085400 · SRN6045TA)은 PCBWay가 턴키로 Digi-Key 등에서 조달할 수 있다(P-002 S1 「Digi-Key·Mouser·Arrow·Avnet」). 그래서 **Combo**로 두면 위탁할 품목이 줄어든다.
  - 리플로 대상이 아닌 품목(모듈 101991223 · CLA216-ICR · 렌즈 · 케이블 · S401 모듈)은 PCBA 밖에서 우리가 조립한다.

## 3. 조립 능력 (등급 구분 없음)

| 요건 | 값 / 원문 | URL | 상태 |
|---|---|---|---|
| Standard / Advanced PCBA | 공개 페이지에 없음. 폼에는 부품 공급 방식 · 면 · X-ray 횟수 · BGA/QFP 개수만 있다 | quotesmt.aspx | 미확인 |
| 미세 피치 | 「Fine Pitch Parts: we can assemble 0.25mm fine pitch parts.」 · SMT 페이지 「Small Chip Packages (0.2mm pitch)」 | assembly-capabilities · pcb_prototype/SMT_Assembly_Capabilities.html | 확인됨 → 0.4mm(DF30)·0.5mm(BTB)는 범위 안 (추론) |
| BGA | 「0.3mm pitch for rigid PCBs and 0.4mm for flex boards with X-ray testing」 ↔ FAQ 「0.25mm pitch」 | assembly-capabilities · assembly-faq · pcb_prototype/BGA_Assembly_Capabilities.html | 불일치 · **우리 보드에는 BGA 없음** |
| QFN | 조립 대상 목록에 있음. 피치 제한은 따로 없음 | SMT_Assembly_Capabilities | 피치 제한 미확인 |
| 최소 부품 | 「as small as 01005, 0201, 0402」 | assembly-capabilities | 확인됨 (우리 최소 0402) |
| 양면 | 「We also offer single or double-sided placement.」 · 폼: Top / Bottom / Both | assembly-capabilities | 확인됨 → **전면 보드는 양면**(J1 BTB가 뒷면) |
| AOI | 「Normally we do AOI test after assembly.」 | helpcenter/pcb_assembly_ordering/Can_you_do_test_after_assembly__What_documents_should_I_offer_.html | 기본으로 확인됨 |
| X-ray | 「we can do X-ray test if you request」 · 폼에 「Number of X-ray test」 | 위 글 · quotesmt.aspx | 요청하면 해 준다는 것은 확인됨 · 비용과 자동 적용 여부는 미확인 |
| MOQ | 「Our minimum is as low as 5 pieces」 ↔ 도움말(2020) 「Assembly MOQ is 1 piece」 | assembly-capabilities · helpcenter …What_s_the_min_quantity… | 불일치 · D-003 #12의 5장이면 어느 쪽이든 충족 |
| 패널 | 「smaller than 50mmx100mm… must be panelized」 · 가장자리와 3.5mm 미만이면 레일 필요 | assembly-special-remind | 확인됨 → **30×30mm 두 보드 모두 패널** |
| BGA 주변 비아 | 「tent and fill any vias near pad of the BGAs…」 | assembly-faq | 해당 없음 (BGA 없음) |

- **우리 보드의 하단 노출 패드·리드 없는 패키지** (X-ray 요청 후보):
  - 전면: U2 DRV8837 (WSON-8 EP) · U4 AL8860 (MSOP-8EP) · J3 DF30 0.4mm
  - 캐리어: U4·U5 TPD4E05U06 (USON-10) · U2 TPS26600 (HTSSOP EP) · J1 BTB 0.5mm
  - → 분기 S7

## 4. PCB 4층 1.6mm ENIG 주문 폼 용어 (https://www.pcbway.com/orderonline.aspx)

| 항목 | 폼 이름과 선택지 (기본값) | 우리 값 (P-002 기준) |
|---|---|---|
| Layers | 「4 Layers」 (기본 2) | 4 Layers |
| Material | 「FR-4」 | FR-4 |
| FR4-TG | 「TG 130-140 / TG 150-160 / TG 170-180 / S1000H TG150 / S1000-2M TG170」 (기본 TG 150-160) · 다층판은 「automatically upgraded to TG150 for FREE」 | TG 150-160 |
| Thickness | 「1.6」 mm | 1.6 |
| Min track/spacing | 「3/3mil, 4/4mil, 5/5mil, 6/6mil, 8/8mil ↑」 (기본 6/6mil) | 6/6mil (P-002: 0.15/0.16mm) |
| Min hole size | 「0.15mm, 0.2mm, 0.25mm, 0.3mm ↑ …」 (기본 0.3mm ↑) | 0.3mm ↑ |
| Solder mask / Silkscreen | Green / White (기본) | 기본 |
| Surface finish | 「Immersion gold(ENIG)」 · 「Thickness of Immersion Gold: 1U" 2U" 3U"」 (기본 1U") · 공정 범위 Ni 「100-150 µin」 Au 「1-8 µin」 | ENIG 1U" |
| Finished copper / Inner Copper | 「1 oz Cu」 / 「1 oz」 (기본) | 1/1 oz |
| Via process | 「Tenting vias / Plugged vias with solder mask / Vias not covered」 (기본 Tenting) · 주석 「For Gerber files this choice will not affect anything」 · 레진 충전은 Additional Options 「All vias filled with resin and capped」 | Tenting (마스크 레이어로 결정) |
| Impedance | Additional Options 「Impedance control」 · 「±10%，50Ω and below：±5Ω」 · 적층 지정은 「Custom stackup」 | CSI·MDI 100Ω / USB 90Ω 차동이 있으므로 **선택 검토** (P-002 §4.4) |
| 표준 적층 (4층 1.6mm) | L1 0.5oz→1oz 도금 / PP 7628 0.1855 / Core 1.03 (Dk 4.6) / PP / L4 · 「Finished PCB Thickness: 1.61mm, tolerance: ±10%」 | P-002 §4와 같음 · https://www.pcbway.com/multi-layer-laminated-structure.html |

## 5. KiCad 10에서 내보내는 방법

### 5.1 공식 툴킷 (참고 — 쓰지 않아도 됨)

- **저장소와 동작:** PCBWay Fabrication Toolkit for KiCad — https://github.com/pcbway/PCBWay-Fabrication-Toolkit-for-KiCad (v1.0.5, 최종 커밋 2026-03-31)
  - 출력 위치는 `<프로젝트>/pcbway_production/<시각>/`이다.
  - Gerber는 KiCad 이름(.gbr), X2 켬, drill/place 원점을 쓴다.
  - 드릴은 Excellon, PTH/NPTH 분리로 낸다.
  - IPC-D-356 넷리스트를 함께 낸다.
- **positions.csv 열:** `pos_x, pos_y, rotation, side, designator, mpn, pack, footprint, value, mount_type`
  - 단위는 mm이고 aux 원점 기준이다.
  - **회전 보정이 없고**(KiCad 값 그대로), 뒷면 X 미러도 없다.
  - THT·DNP 부품도 들어간다. 「Exclude from position files」 속성을 켠 부품만 빠진다.
  - 소스: `plugins/process.py`
- **bom.csv 열:** `Designator, Quantity, Value, Footprint, Package, MPN, DNP(Yes), Mount_Type, …` (Designator 구분자는 `", "`)
- **주의:** 툴킷은 실행 중에 **보드 설정의 솔더마스크 여유값을 0으로 바꾼다**(소스 확인). P-002 규칙과 충돌할 수 있으므로 우리는 `kicad-cli`를 쓴다(분기 S8).

### 5.2 `kicad-cli` (10.0.8) 대응 — 옵션은 이 PC의 `--help` 출력으로 확인함

| 산출물 | 명령 (권장) | PCBWay 요건 대응 |
|---|---|---|
| Gerber | `kicad-cli pcb export gerbers -l F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts --no-x2 --no-protel-ext --precision 6 --use-drill-file-origin --check-zones -o gerber/ <board>.kicad_pcb` | RS-274X · KiCad 이름 · X2 끔 · 4.6 mm (KiCad 9 튜토리얼 화면과 같음) · 외곽 포함 |
| 드릴 | `kicad-cli pcb export drill --format excellon --drill-origin plot --excellon-units mm --excellon-zeros-format decimal --excellon-oval-format alternate --generate-map --map-format pdf -o gerber/ <board>.kicad_pcb` (PTH/NPTH 분리 여부는 S5) | Excellon · mm · Decimal |
| 좌표 | `kicad-cli pcb export pos --format csv --units mm --use-drill-file-origin --side front -o <board>-top-pos.csv <board>.kicad_pcb` 와 `--side back` 한 번 더 (`--bottom-negate-x`는 쓰지 않음) | mm · 왼쪽 아래 원점 · 면별 파일 · 뒷면 X 미러 없음 |
| 조립도 | `kicad-cli pcb export pdf -l F.Fab,Edge.Cuts …` 와 `B.Fab` (`--sp` 패드 번호, `--cdnp` DNP에 X 표시) | 극성·1번 핀·DNP 표시 |
| IPC-D-356 (선택) | `kicad-cli pcb export ipcd356` | 전기 시험용 넷리스트 |

- **원점:** 보드 **왼쪽 아래 모서리에 drill/place(aux) 원점을 두고**, Gerber·드릴·좌표 세 가지 모두 같은 원점(`--use-drill-file-origin` / `--drill-origin plot`)을 쓴다. 세 파일의 좌표계가 맞아야 PCBWay가 대조할 수 있다.
- **회전 보정이 필요한지:**
  - PCBWay는 「top point of view, 0~360°」만 요구하고, 공식 툴킷도 KiCad 값을 보정하지 않는다.
  - KiCad 라이브러리 풋프린트의 0° 방향이 IPC-7351 기준인지는 이 조사에서 확인하지 않았다(**미확인**).
  - 결론: **보정표를 미리 만들지 않는다.** 실크 극성·1번 핀 표시와 조립도로 방향을 고정하고, PCBWay가 생산 전에 보내는 확인 단계에서 회전을 대조한다(분기 S9). 이 확인 단계에서 회신하는 것은 주문 후 외부 연락이라 사용자 지시가 필요하다.
- **BOM 변환:** `bom-full.csv`(21열)를 보드별 PCBWay 템플릿 열(`Item #` · `*Designator` · `*Qty` · `Manufacturer` · `*Mfg Part #` · `Description / Value` · `*Package/Footprint` · `Type` · `Your Instructions / Notes`)로 옮긴다.
  - `Type`: SMD / THT / **DNS**
  - `Notes`: Turnkey / Consigned / Combo 지시와 게이트(G1·G2)

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| S1 | BOM 형식 | PCBWay 템플릿 열 그대로 (xlsx 또는 csv), 보드마다 따로 | 공식 템플릿이고, BOM이 생산 기준이다 | 툴킷 bom.csv 열 |
| S2 | 좌표 단위 | **mm** | 도움말과 KiCad 9 튜토리얼이 mm. 템플릿의 mil은 예시 | mil (템플릿) |
| S3 | 좌표 파일 | **면별 2개 파일** (top/bottom) + 각 파일 안에도 Side 열 | 「top and bottom together … confusion」 사례 · 전면 보드는 양면 | 툴킷식 한 파일 |
| S4 | Gerber 이름 | KiCad 이름(.gbr), Protel 확장자 끔, X2 끔 | 현행 KiCad 9 튜토리얼 | Protel 확장자 (옛 블로그) |
| S5 | 드릴 파일 | **PTH/NPTH 분리 (`--excellon-separate-th`) + 드릴 맵 PDF** | 공식 툴킷 출력과 같고, 확장자 안내 글과도 맞는다. 튜토리얼의 「single file」은 강조돼 있지만 둘 다 받는다 | 한 파일 (튜토리얼 화면) |
| S6 | 조립도 | 낸다 (F.Fab/B.Fab PDF, 패드 번호, DNP X 표시) | 회전 보정 정책이 없고 양면이다 | 실크만 |
| S7 | X-ray | WSON·USON·MSOP-EP·HTSSOP-EP·0.4/0.5mm 커넥터가 있는 보드에 **요청** (폼의 X-ray 횟수) | 노출 패드 납땜은 AOI로 볼 수 없다 | AOI만 |
| S8 | 내보내기 도구 | `kicad-cli` (위 명령) | 툴킷은 솔더마스크 여유값을 0으로 바꾼다 | 공식 툴킷 |
| S9 | 회전 | 보정 없이 KiCad 값 그대로 + 극성 실크·조립도 + 생산 전 확인 | 공개된 보정 정책이 없다 | 사전 보정표 작성 (근거가 생기면) |
| S10 | 부품 공급 | **Combo (부분 턴키)** — LCSC·Digi-Key 유통 부품은 턴키, 정해진 품목만 위탁 | PCBWay 턴키 조달처에 Digi-Key가 포함된다 | 전부 위탁 |

## P-004 (제조 산출물) 체크리스트

| # | 항목 | 기준 | 확인 방법 (verifiable) |
|---|---|---|---|
| 1 | Gerber 층 | F/In1/In2/B.Cu · F/B.Paste · F/B.Silkscreen · F/B.Mask · **Edge.Cuts** (보드별 11장) | 파일 목록 개수 (예) |
| 2 | Gerber 형식 | RS-274X, KiCad 이름, X2 끔, 정밀도 6 | 파일 머리글 `%FSLAX46Y46*%` 확인 (예) |
| 3 | 드릴 | Excellon, mm, Decimal, PTH/NPTH 2파일 + 드릴 맵 | 파일 머리글 `METRIC` 확인 (예) |
| 4 | 원점 | aux 원점 = 보드 왼쪽 아래 · Gerber·드릴·좌표가 같은 원점 | 좌표 최소값 ≈ 0 (예) |
| 5 | 좌표 | csv, mm, 면별 2파일, 뒷면 X 미러 없음, SMD만 (THT는 빼거나 표시) | 행 수 = BOM의 SMD 실장 수 (예) |
| 6 | BOM | 보드별 PCBWay 템플릿 9열 · 참조 지정자 콤마 · DNP는 `Type=DNS` · 턴키/위탁은 Notes 열 | 참조 지정자 집합 = 좌표 파일 집합 (예) |
| 7 | DNP 일치 | BOM의 DNS 행 = 회로도 DNP = 좌표 파일에서 제외하거나 표시 | 집합 비교 (예) |
| 8 | 극성·1번 핀 | 다이오드·LED·IC·커넥터의 실크 표시 | 사람이 확인 (아니오) |
| 9 | 조립도 | F.Fab / B.Fab PDF (패드 번호, DNP X) | 파일 존재 (예) · 내용은 사람이 확인 (아니오) |
| 10 | 층 순서 | 주문 폼 L1:F.Cu L2:In1.Cu L3:In2.Cu L4:B.Cu — 「readme」에도 적는다 | 문서 (예) |
| 11 | 패널 | 30×30mm → 조립용 패널(≥50×100) · 레일(가장자리 3.5mm 미만 부품) · 피듀셜 | 외형 치수 (예) |
| 12 | 폼 옵션 | 4L · FR-4 TG150-160 · 1.6mm · 6/6mil · 0.3mm↑ · ENIG 1U" · 1/1oz · Tenting · 임피던스(검토) | 체크리스트 (예) |
| 13 | X-ray | 대상 부품 목록과 요청 횟수 | 문서 (예) |
| 14 | 위탁 | 위탁 품목 목록 · 포장(연속 테이프, 리더 50mm) · 라벨(BOM 행 번호·MPN·수량·참조 지정자) · 여분(커넥터·IC +1~5) · 배송지(주문 후 안내 — 열람 불가) | 목록 (예) |
| 15 | 게이트 | G1(BTB 실물 결합) · G2(S401 홀더 분리)·PicoBlade 하우징 확인 전 **발주 금지** | 게이트 기록 (예) |
| 16 | 해시 | 제출 묶음 zip의 sha256과 같은 설계 리비전 (README 단계 6) | sha256 (예) |

## 확인 못 한 것

- **PCBWay 정책·조건:**
  - 회전 보정 정책 (IPC-7351 0° 기준인지, PCBWay 쪽 보정인지)
  - Standard/Advanced PCBA 등급이 있는지
  - X-ray 비용, 자동 적용 여부
  - QFN 최소 피치
  - 0.4/0.5mm 피치 커넥터를 명시한 문구
- **위탁:** 위탁 배송지 주소 (열람 불가)
- **KiCad 라이브러리:** 풋프린트 0° 방향 규칙 (이번 조사 범위 밖)
- **불일치 값:** PCBWay 문서끼리 다른 값(단위·드릴·MOQ·BGA 피치)은 S2~S5에서 하나를 골랐다. 견적·생산 확인 단계에서 다시 확인해야 한다.
- **근거 원본:** 템플릿 원본(xlsx·txt)과 툴킷 소스는 세션 임시 폴더에만 있다. 제조사 저작물이고 라이선스 표기가 없어 저장소에 보관하지 않는다(D-003 #14).
