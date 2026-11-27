# R-016 IR 스트링 B 실장 — BOM 갱신 (O-69)

- 배정: orch t18r R-016 (orch 분기 O-69) · 작성 research t18s · 2026-11-27 · 레인 t-20261127-021842-688a (main eb0da0f 기준)
- 배경: D-003 #17 「스트링 B DNP로 시작 — 개수는 실측으로 결정」. M-003 2차(mechanical 4752a68)에서 A만 켜면 IR 직접광 시야 61%, A+B면 86%였다. 방열 H3에서 A+B 듀티 25%일 때 상승 약 21.5K로 목표 ≤25K 안이다. 12V 합계 ≈1.84A, 어댑터 2.08A로 여유는 약 12%다.
- 범위: 회로도 파일은 고치지 않았다(schematic 소관). 바꿔야 할 심벌은 3절에 목록으로만 적었다. 구매·견적·업로드·외부 연락은 하지 않았다.

## 결론

- **스트링 B 경로 부품은 전면 보드 8개다:** U5, L2, D2, R14, C16, C17, D_IR_B1, D_IR_B2.
  - 근거: 회로도 넷 `IRB_SET`, `IRB_M`, `IRB_K`, `IRB_SW`에 붙은 부품 전부, 그리고 `12V_IR`에 붙은 B 전용 입력 커패시터 C16·C17이다.
- **그대로 DNP로 남는 전면 부품은 4개다:** C6(CAM_PG_AV), Q4·R11(LIGHT_SENSE 차선 ALS-PT19), R16(CAM_RESET 풀다운).
  - 캐리어의 C15·C16(MDI 센터탭)과 R13~R17(SD 풀업)도 그대로 둔다.
- **bom-full.csv는 17행을 바꿨다.**
  - B 8행: 수량을 「5보드 실장 5 · 주문 5」로, AssemblyNotes를 「실장 · … · O-69」로 바꿨다.
  - 같은 MPN을 쓰는 9행(전면 A 쪽 7행, 캐리어 C5, VSMA 행 확인일)은 재고와 확인일만 갱신했다.
- **PCBWay front BOM:** 실장 50→**58**, DNS 12→**4**.
  - 생성기 종료 코드는 **1**이다. 회로도 DNP 해제를 기다리는 8개 차이만 있고, 예정된 차이다.
  - 8개 DNP를 해제했다고 가정한 입력으로 돌리면 종료 코드 **0**이고 출력도 같다.
- **추가 비용 (5대 부품값):** 약 **USD 31.45** (대당 약 6.29). VSMA1085400 10개가 23.40으로 대부분이다. 조립비와 운송비는 빠져 있다.

## 1. 회로도 근거 (넷 이름)

출처는 main eb0da0f의 `hardware/schematic/front/front.kicad_sch`(rev C-011, 커밋 83728da, git blob sha256 7fb86024…7566)다. 이것을 `kicad-cli sch export netlist`(종료 0)로 내보내 파싱했다. 이 회로도는 `tools/boards.py` 214~229줄의 `for k, dn in (('A', False), ('B', True))` 반복이 만든 B 스트링이다.

| 참조 | 값 | 핀 → 넷 | B 경로 판정 |
|---|---|---|---|
| U5 | AL8860MP-13 | 1 `IRB_SET` · 4 `IR_CTRL` · 5·6 `IRB_SW` · 8 `12V_IR` · 2·3·9 `GND` · 7 NC | 예 (B 드라이버) |
| R14 | 0.1R 1% 0.25W (센스) | 1 `12V_IR` · 2 `IRB_SET` | 예 |
| D_IR_B1 | VSMA1085400 | 2 `IRB_SET` · 1 `IRB_M` | 예 |
| D_IR_B2 | VSMA1085400 | 2 `IRB_M` · 1 `IRB_K` | 예 |
| L2 | 47uH (SRN6045TA-470M) | 1 `IRB_K` · 2 `IRB_SW` | 예 |
| D2 | SS24S-E3/61T | 1 `12V_IR` · 2 `IRB_SW` | 예 (프리휠) |
| C16 | 10uF/50V X7R | 1 `12V_IR` · 2 `GND` | 예 (B 입력. A의 C14와 짝. boards.py 228줄 `C{14 if A else 16}`, dnp=dn) |
| C17 | 100nF/50V | 1 `12V_IR` · 2 `GND` | 예 (B 입력. A의 C15와 짝. boards.py 229줄) |
| C6 | 100nF | `CORE_3V3` · `CAM_PG_AV` | 아니오: 센서 전원 옵션, DNP 유지 |
| Q4 | ALS-PT19 (alt) | `CORE_1V8` · `LIGHT_SENSE` | 아니오: 조도 차선, DNP 유지 |
| R11 | 10k | `LIGHT_SENSE` · `GND` | 아니오: 조도 차선, DNP 유지 |
| R16 | 10k | `CAM_RESET` · `GND` | 아니오: 리셋 옵션, DNP 유지 |

- `IR_CTRL`(Q5 오픈드레인, IR_PWM)은 A와 B가 같이 쓰는 넷이고 이미 실장돼 있다. 12V_IR 쪽 eFuse 설정(TPS26600 ILIM 8.06k ≈ 1.49A)은 계약 v1.10 108행에 따라 처음부터 2스트링 최악값 1.22A로 잡혀 있어 바꿀 것이 없다.

## 2. 바뀐 행 (`docs/research/bom-full.csv`, 21열 99행 유지)

재고와 가격의 확인일은 2026-11-27이다. LCSC 공개 JSON `wmsc.lcsc.com/ftps/wm/product/detail?productCode=…`과 Digi-Key 검색 쪽에서 확인했다.

| 행 (Reference) | 바뀐 열 | 새 값 · 근거 |
|---|---|---|
| [전면] C16 | Quantity · Stock · PriceDate · AssemblyNotes | 보드당 1 · 5보드 실장 5 · 주문 5 / C89632 재고 113,230 (5+ 0.2146) |
| [전면] C17 | 〃 | 〃 / C307331 재고 1,966,800 (100+ 0.0077, MOQ 100) |
| [전면] D2 | 〃 | 〃 / C84317 재고 14,190 (5+ 0.1272). DK 30,046은 11-26 값 |
| [전면] D_IR_B1 · D_IR_B2 | Quantity · PriceDate · AssemblyNotes | 〃 / Digi-Key 751-VSMA1085400CT-ND 재고 1,534 (1+ 3.21 · 10+ 2.34 · 100+ 1.8227). 위탁(Consigned)은 그대로다 |
| [전면] L2 | Quantity · Stock · PriceDate · AssemblyNotes | 〃 / C5151734 재고 3,985 (5+ 0.3642). DK 11,160은 11-26 값 |
| [전면] R14 | 〃 | 〃 / C25334 재고 183,200 (50+ 0.0085, MOQ 50) |
| [전면] U5 | 〃 | 〃 / C500782 재고 2,116 (1+ 1.2867 · 10+ 1.0868) |
| [캐리어] C5 · [전면] C14 · C15 · D1 · L1 · R13 · U4 | Stock · PriceDate | 같은 MPN이라 재고와 확인일을 맞췄다(값은 위와 같음). 수량은 그대로다 |
| [전면] D_IR_A1 · D_IR_A2 | PriceDate | Digi-Key 재고와 가격은 11-26과 같다 |

- B 8행 AssemblyNotes의 변화: 맨 앞 `DNP · ` → `실장 · `, 끝에 ` · O-69 스트링 B 실장 (R-016, 회로도 DNP 해제 대기)`를 붙였다. 생성기는 이 맨 앞 글자로 DNS를 판정한다.
- 단가 사다리는 11-26과 같다. 같은 MPN의 합계 수량이 두 배가 되면서 바뀐 구간:
  - AL8860: 5개 → 10개, 1+ → **10+** 구간
  - VSMA1085400: 10개 → 20개, 10+ 구간 그대로
- **재고 판정:** 모두 충분하다. 가장 빠듯한 것은 LCSC VSMA C6604340(재고 3)인데 원래부터 Digi-Key 위탁이라 영향이 없다.

### 추가 비용 (5대, 부품값만, USD)

| 부품 | 추가 수량 | 추가액 |
|---|---|---|
| D_IR_B1·B2 VSMA1085400 | 10 | 23.40 (10+ 2.34) |
| U5 AL8860MP-13 | 5 | 4.43 (10개 × 1.0868 − 5개 × 1.2867) |
| L2 SRN6045TA-470M | 5 | 1.82 |
| C16 CL31B106KBHNNNE | 5 | 1.07 |
| D2 SS24S-E3/61T | 5 | 0.64 |
| R14 · C17 | 5 · 5 | 0.04 · 0.04 (MOQ 50·100 안이라 실제 주문액은 그대로일 수 있음) |
| **합계** | | **≈ 31.45 (대당 ≈ 6.29)** |

- 이 합계에는 PCBWay 조립비(부품 종류·납땜점 수 기준), 위탁 VSMA 운송비, 예비분이 빠져 있다.

## 3. 회로도에서 바꿔야 할 심벌 (schematic 소관, orch가 배정)

| 파일 | 위치 | 바꿀 것 |
|---|---|---|
| `hardware/schematic/tools/boards.py` | 215줄 `for k, dn in (('A', False), ('B', True)):` | B의 `True` → `False`. 생성기를 다시 돌리면 아래 8개가 바뀐다. 210줄 블록 제목 「(B 스트링 DNP)」와 214줄 주석도 함께 바꾼다 |
| `hardware/schematic/front/front.kicad_sch` (C-011, 지금 줄 번호) | U5 13717 · R14 13821 · D_IR_B1 13884 · D_IR_B2 13957 · L2 14030 · D2 14103 · C16 14186 · C17 14249 | 각 심벌의 `(dnp yes)` → `(dnp no)`. `in_bom`, `on_board`, `in_pos_files`는 지금도 yes다 |
| `hardware/schematic/hw-fw-contract.md` v1.10 | 99행 「스트링 A 실장 · B DNP」 · 122행 「스트링 B는 DNP로 시작」 · 125행 「스트링 B DNP이면 ≈1.23A」 | 「A·B 실장 (O-69)」로 문구를 바꾼다(전류 합계 ≈1.84A는 이미 A+B 기준) |
| PCB (`hardware/pcb/…/front.kicad_pcb`) | — | 지금 보드 파일에는 D_IR_B1이 없다(외형 단계). 배치할 때 DNP 속성이 회로도를 따르는지 pcb 담당이 확인한다 |

- 회로도를 고친 뒤 할 일: `manufacturing/bom/inputs/front-kicad-bom.csv`를 다시 내보내고 `python -I make_pcbway_bom.py`를 돌린다. 종료 코드 **0**이 나와야 끝난다(research 또는 orch 지정 담당).

## 4. 생성기 실행 (`manufacturing/bom/`)

| 실행 | 입력 | 종료 코드 | 결과 |
|---|---|---|---|
| 일반 `python -I make_pcbway_bom.py` | inputs/ (bom-full 새 판, KiCad BOM은 C-011과 바이트 동일) | **1** | front DNP 불일치: 「KiCad에만: ['C16', 'C17', 'D2', 'D_IR_B1', 'D_IR_B2', 'L2', 'R14', 'U5']」. 참조 집합과 carrier는 일치 |
| 확인 `--kicad-front <8개 DNP를 지운 사본> --out <scratchpad>` | 같음 + 예상 회로도 | **0** | carrier 73/7, front 62/4 일치. 출력 CSV 2개는 일반 실행과 `cmp`로 같음 |

- 바뀐 출력은 `front-pcbway.csv`의 8행이다(Type `DNS`→`SMD`, Notes 앞의 `DNS - do not purchase/place; ` 제거). D_IR_B1·B2는 `Consigned`다. `carrier-pcbway.csv`는 바뀌지 않았다.

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| S1 | C16·C17을 B 경로에 넣을지 | **넣는다** | boards.py가 같은 `dn` 변수로 만든다(A의 C14·C15와 짝). B AL8860의 입력 디커플링이다. orch가 말한 「C15/C16」은 캐리어 MDI 센터탭이라 다른 부품이다 | C16·C17은 DNP로 두고 C14·C15 공유 (AL8860 데이터시트 권고와 어긋남) |
| S2 | 생성기 KiCad 입력 | 실제 회로도 내보내기를 그대로 두고 종료 코드 1을 기록한다. 예상 입력은 scratchpad에서 종료 0으로만 확인한다 | 회로도에 없는 상태를 「KiCad 내보내기」로 커밋하지 않는다. 불일치 목록이 schematic 작업의 확인 기준이 된다 | 예상 입력을 `inputs/`에 커밋해 종료 0으로 맞춤 |
| S3 | 같은 MPN의 A와 B 행 합치기 | 합치지 않는다(행 구조 유지) | A/B 추적과 이전 R-008·R-011 결과와의 비교가 쉽다. PCBWay는 같은 MPN이 두 행에 있어도 받는다 | 행을 합쳐(C14,C16 등) PCBWay 줄 수를 줄임 |
| S4 | 재고 갱신 범위 | B 행 + 같은 MPN 행 | 같은 MPN인데 확인일이 다르면 헷갈린다 | B 행만 갱신 |

## 돌린 명령

- `kicad-cli sch export bom` (front·carrier, C-011): 종료 0 · 0. 커밋된 입력과 sha256이 같다
- `kicad-cli sch export netlist` (front): 종료 0. 넷 파싱은 `python -I`로 했다
- LCSC 공개 JSON 7건(`curl`): 성공. Digi-Key 검색 쪽(WebFetch): 성공
- bom-full 갱신 스크립트: 종료 0. 바꾸지 않은 행은 왕복 검사로 바이트가 같음을 확인했다
- `python -I make_pcbway_bom.py`: **종료 1** (예정된 DNP 8개 차이). 예상 입력으로는 **종료 0**
- 저장소 검사 명령: 돌리지 않음(문서·CSV만 바뀜)
