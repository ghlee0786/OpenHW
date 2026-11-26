# R-021 C-016·C-017 BOM 갱신 + 12V 3A급 어댑터 선정 (O-88)

- 배정: orch t18r R-021 · 작성 research t18s · 확인일 2026-11-27 · 레인 t-20261127-051043-fac0 (main 45fa2be 기준)
- 범위: 회로도는 `git show f0745ed`(C-017, C-016 ea1336b를 포함)로 읽기만 했다. 구매·견적·문의는 하지 않았다. **비용 계산은 하지 않았다(사용자 지시).** 재고는 BOM 칸을 채우려고만 확인했다.

## 결론

1. **BOM 갱신 완료.** `docs/research/bom-full.csv`(21열, 99→100행)와 PCBWay BOM 2개를 다시 만들었다. `make_pcbway_bom.py`는 **종료 코드 0**이고, 참조와 DNP가 carrier 73/7, front 63/4(TP 24개 제외)로 KiCad와 같다.
2. **어댑터 1안: Mean Well GST40A12-P1J** (12V 3.34A 40W, 과부하 105~150%에서 **hiccup** 자동 복귀, 리플 120mVp-p, KC K60950-1 포함, P1J 플러그 2.1×5.5).
   - **차선: GST60A12-P1J** (12V 5A 60W, 같은 보호 방식·리플·플러그, 과열 보호 추가).
   - 지금 쓰는 GST25A12-P1J와 같은 계열·플러그라 우리 DC 잭 J2(XKB DC-005-5A-2.0, 중심 핀 Ø2.00, 57V 5A)에 그대로 맞는다.
3. **발견:** 캐리어 C18·C22의 10nF Samsung CL05B103KB5NNNC(C15195)는 LCSC **재고 0**이다(2026-11-27). 새 C19에는 재고가 있는 FH 0402B103K500NT(C1524, 재고 2,900,700)를 넣었다. 캐리어 두 개도 바꿀지는 이 배정 범위 밖이라 그대로 두었다(제안만 함).

## 1. BOM 갱신 (C-016·C-017)

KiCad BOM 차이: 이전 입력(main) → f0745ed 내보내기, `kicad-cli sch export bom`, 종료 0 · 0.

| 보드 | 회로도 변경 | bom-full 행 | 부품 · 근거 (LCSC 공개 JSON, 2026-11-27) |
|---|---|---|---|
| 캐리어 | R6 8.06k → **6.98k 1%** (C-017, ILIM ≈1.72A, SIM-001b) | `[캐리어] R6` 수정 | **UNI-ROYAL 0402WGF6981TCE, C47500**, 재고 48,300, 100+ 0.0007. 차선 YAGEO RC0402FR-076K98L(C137944)은 재고 0 |
| 전면 | **J2** PicoBlade → 2.54mm 납땜 패드, BOM/CPL 제외 (C-016, O-84) | `[전면] J2` **삭제** | KiCad BOM에서도 빠짐. CLA216 리드는 납땜 |
| 전면 | **R15** 삭제 (C-016, ALS_INT_RSV 풀업) | `[전면] R1,R5,R7,R15,R17` → `R1,R5,R7,R17,R19` | 같은 0402WGF1002TCE(C25744, 재고 9,383,500). 보드당 5개는 그대로 |
| 전면 | **R19 10k** 추가 (C-017, CAM_1V8 블리더) | 위 묶음에 넣음 | 같음 |
| 전면 | **R18 1k** 추가 (C-017, Q6 게이트 밀러 소프트스타트) | `[전면] R18` **추가** | UNI-ROYAL 0402WGF1001TCE, C11702, 재고 11,737,400 (캐리어 R19와 같은 품번) |
| 전면 | **C19 10nF** 추가 (C-017, 밀러 소프트스타트) | `[전면] C19` **추가** | **FH 0402B103K500NT, C1524**, X7R 50V, 재고 2,900,700, 100+ 0.0043. 차선 Samsung CL05B103KB5NNNC(C15195)는 **재고 0** |
| 전면 | **TP24** 추가 (C-016, ALS_INT_RSV) | `[전면] TP (24개)` | 부품 아님 (생성기·검사에서 제외) |

- 파일 sha256: bom-full 93e34467…57ba · carrier KiCad BOM 9f2b6eea…1abd · front KiCad BOM ce2a9138…b8e7. `manufacturing/bom/README.md`에 기록했다.
- 생성기 결과:

| 보드 | 행 | 참조 | 실장 | DNS | 결과 |
|---|---|---|---|---|---|
| carrier | 50 | 73 | 66 | 7 | 일치 |
| front | 40 | 63 | 59 | 4 | 일치 |

  → **종료 코드 0**
- 갱신 스크립트는 바꾸지 않은 행이 원본과 바이트까지 같은지 왕복 검사를 한다(scratchpad `update_bom.py`, 종료 0).

## 2. 12V 3A급 어댑터 (O-88) — SIM-001a 입력값

### 2.1 선정

| | **1안 GST40A12-P1J** | **차선 GST60A12-P1J** | (참고) 현재 GST25A12-P1J |
|---|---|---|---|
| 출력 | 12V **3.34A** (0~3.34A), 40W | 12V **5A** (0~5A), 60W | 12V 2.08A |
| 과부하 보호 (OLP) | **105~150% 정격 출력**, 「Protection type : **Hiccup mode**, recovers automatically after fault condition is removed」 | 같음 | — |
| 과전압 (OVP) | **12.6~16.2V**, 「Shut down o/p voltage, re-power on to recover」 | 같음 | — |
| 과열 | (표 항목 없음) | 「Shut down o/p voltage, re-power on to recover」 | — |
| 단락 | 「Protections: Short circuit / Overload / Over voltage」(특징) | 같음 | — |
| 리플·잡음 (max) | **120mVp-p** (20MHz, 12" 꼬임선 + 0.1µF·47µF 끝단) | 120mVp-p | — |
| 전압 공차 / 라인 / 부하 조정 | **±3.0% / ±1.0% / ±3.0%** | ±3.0% / ±1.0% / ±3.0% | — |
| 기동·상승 시간 | 1000ms, **50ms** / 230VAC (전부하) | 같음 | — |
| 유지 시간 (typ) | 50ms / 230VAC, 15ms / 115VAC | 같음 | — |
| 효율 (typ) | 89.5% | 89.5% | — |
| 돌입 (AC, max) | 냉간 35A / 115VAC, 65A / 230VAC | 같음 | — |
| 동작 온도 · 디레이팅 | −30~+70°C. **50°C까지 100%, 70°C에서 60%**(직선, 디레이팅 곡선) | −30~+70°C | — |
| 안전 인증 | UL62368-1, CSA, TUV EN62368-1, CB IEC62368-1, CCC, PSE, BSMI, AS/NZS, BIS, **KC K60950-1**, EAC | 같음 | KC K60950-1 표기 |
| EMC | CISPR32 Class B (전도·방사), EN61000-3-2 Class A, EN55035 내성 | 같음 | — |
| AC 입력 | IEC320-C14, Class I(FG) | 같음 | 같음 |
| DC 케이블 | **UL1185 16AWG 1000±50mm** (5~15V) | UL1185 16AWG 1000±50mm (12~15V) | — |
| 플러그 | **P1J: 2.1φ × 5.5φ × 11mm, 센터 +**, 튜닝포크형 | 같음 | 같음 |
| 크기 · 무게 | 125×50×31.5mm, 0.28kg | — | — |
| 출처 | Mean Well GST40A-SPEC (2026-04-03판, sha256 46ab54a2…), 1·2·3쪽 | GST60A-SPEC (sha256 7feee0cf…), 2쪽 | bom-full PSU1 |

- URL:
  - https://www.meanwell.com/Upload/PDF/GST40A/GST40A-SPEC.PDF
  - https://www.meanwell.com/Upload/PDF/GST60A/GST60A-SPEC.PDF
  - 확인일 2026-11-27. GST36A는 같은 경로에 없었다(404).

### 2.2 우리 DC 잭과의 짝

- **J2 XKB DC-005-5A-2.0** (도면 Rev A1 2025-04-22, sha256 39bae627…, LCSC C381116):
  - 「RATING: 57V, 5A」
  - 접촉 저항 「50 MILLIOHMS Max. FOR INITIAL」(5000회 뒤 80mΩ)
  - 중심 핀 **DIM A 2.00mm** (2.5 판은 2.50)
- P1J 플러그는 안지름 2.1, 바깥지름 5.5, 센터 +다. 이것은 2.0mm 핀 잭의 짝이고, 지금 GST25A12-P1J와 같은 플러그다. 기구·회로 변경은 없다.
- 전류: 3.34A(1안)와 5A(차선) 모두 잭 정격 5A 이하다.

### 2.3 SIM-001a용 출력 모델 값 (schematic에 orch가 전달)

| 매개변수 | 1안 GST40A12 | 차선 GST60A12 | 근거 / 계산 |
|---|---|---|---|
| Vout 공칭 | 12.00V | 12.00V | 사양 |
| Vout 범위 (공차 ±3%) | 11.64 ~ 12.36V | 11.64 ~ 12.36V | 12 × (1 ± 0.03) |
| 정격 전류 | 3.34A | 5.0A | 사양 |
| OLP 시작 (105~150% 정격 출력) | **3.51 ~ 5.01A** (12V 기준) | **5.25 ~ 7.5A** | 40W·60W × 1.05/1.5 ÷ 12V |
| OLP 동작 | hiccup — 출력을 끊었다 켰다 반복, 원인이 사라지면 자동 복귀 | 같음 | 사양. hiccup 주기·듀티는 **미기재(미확인)** |
| OVP | 12.6 ~ 16.2V에서 차단, 재투입해야 복귀 | 같음 | 사양 |
| 리플 (최대) | 120mVp-p | 120mVp-p | 사양 (측정 조건 위) |
| 부하 조정 (0→100%) | ±3% (±0.36V) — 출력 저항으로 보면 약 0.11Ω 이하(0.36V/3.34A, 상한 근사) | ±0.36V / 5A ≈ 0.072Ω 이하 | 계산 (모델용 근사) |
| 상승 시간 | 50ms (230VAC, 전부하) | 50ms | 사양 |
| 기동 지연 | 1000ms | 1000ms | 사양 |
| 유지 시간 | 50ms(230VAC) / 15ms(115VAC) | 같음 | 사양 |
| 케이블 | 16AWG × 1000mm 왕복 2m → 약 **26mΩ**(16AWG 13.2mΩ/m, 20°C 일반값) | 같음 | 계산 (AWG 표준 저항, 사양 외 값) |
| 잭 접촉 저항 | ≤50mΩ (초기) | 같음 | XKB 도면 |
| 시스템 최악 전류 (참고) | 12V 합계 ≈1.84A(계약 v1.11) → 정격의 55% · OLP 시작 하한까지 여유 1.67A | 정격의 37% | 계약 §3.2 |
| 온도 여유 | 외함 밖 주위 50°C까지 100% | — | 디레이팅 곡선 |

- **SIM에서 볼 점:**
  - eFuse ILIM ≈1.72A(C-017)와 어댑터 OLP 시작 하한 3.51A 사이가 넓다. 그래서 12V_IR 단락은 eFuse가 먼저 끊고, 어댑터 hiccup은 그 뒤 단계다.
  - 돌입: 5V 벅 입력 커패시터와 eFuse dVdT 소프트스타트는 50ms 상승 램프에 맞춰 본다.

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | 전면 J2 행 | bom-full에서 삭제 | 회로도에서 BOM/CPL 제외 납땜 패드가 됐다. 행이 남으면 생성기 일치 검사가 깨진다 | 「부품 없음」 요약 행 |
| B2 | C19 품번 | FH 0402B103K500NT (C1524) | 캐리어 C18·C22의 Samsung C15195는 재고 0이다 | Samsung CL05B103KB5NNNC (재고가 돌아오면) |
| B3 | 캐리어 C18·C22 재고 0 | 바꾸지 않고 보고 | 배정 범위 밖이다 | 같은 FH C1524로 바꾸기 (다음 배정) |
| B4 | R6 품번 | UNI-ROYAL C47500 | 재고 48,300이고 YAGEO는 재고 0이다 | YAGEO RC0402FR-076K98L |
| B5 | 어댑터 | GST40A12-P1J | 3A 이상, 현재와 같은 계열·플러그·KC, hiccup 자동 복귀. 40W면 12V 1.84A 최악에 여유가 있다 | GST60A12-P1J (5A, 과열 보호 추가, 더 큼) |
| B6 | 가격 | 넣지 않음 | 사용자 지시(비용 계산 안 함) | — |

## 돌린 명령

- `git show f0745ed:hardware/schematic/{carrier,front}/*` → scratchpad, `kicad-cli sch export bom` ×2: 종료 0 · 0
- LCSC 공개 JSON 8건(curl), Mean Well SPEC PDF 3건 + XKB 도면(curl), PyMuPDF 추출
- `python -I update_bom.py`(scratchpad): 종료 0
- `python -I manufacturing/bom/make_pcbway_bom.py`: **종료 0**
- 저장소 검사 명령: 문서·CSV만 바뀌어서 돌리지 않았다
