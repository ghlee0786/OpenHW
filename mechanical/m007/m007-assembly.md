# M-007 VD-001 조건 5 — 전체 조립 STEP 틀과 대체 3D 모델

- 배정: orch t18r M-007 · 레인 t-20261127-040816-30c6 · mechanical t18x · 2026-11-27
- **한 명령:** `python -I -B mechanical/m007/run_all.py [--pcb <pcb 레인 커밋>]`
  1. pcb 커밋에서 kicad-cli로 보드 STEP 2장을 내보낸다.
  2. 캐리어 커넥터 4개(J2·J3·J4·J5)의 Fab 외곽을 읽는다.
  3. Fusion 새 문서 `M007_assembly`에 조립을 만든다(02).
  4. 기계 판정을 돌린다(03).
  5. `judge.md`와 VD-001 조건 5 결과 파일 `validation/runtime/vd001/results/cond5-mechanical.json`(docs/review/vd001-format.md §1)을 쓴다.
  - **종료 코드 = 조건 5 불합격 항목 수**(결과 파일의 `pass: false` 수 = VD-001 생성기와 같은 셈) = 판정 실패(J1~J6) + 3D 모델이 빠진 보드 + J3 삽입.
  - 3D 모델 빠짐 (pcb 3012bf3): 캐리어 J3 · J5 · L1 · Q3 · Q4, 전면 Q3 · Q5 · Q7 · X1 → pcb가 §1 모델을 연결하면 0이 된다.
  - pcb가 새 커밋을 내면 이 명령 하나로 바뀐다(커넥터 위치·외함 개구도 따라감).
  - 렌더: `fusion_cli run mechanical/m007/scripts/04_render.py`
- 산출물(조립 STEP·보드 STEP·판정 JSON·렌더 PNG)은 `validation/runtime/vd001/`에 둔다(gitignore). 해시는 아래 §5.

## 1. 대체 3D 모델 (`mechanical/models/*.step`)

| 파일 | 쓰는 자리 | 몸체 (풋프린트 F.Fab, 로컬) | 높이 | 높이 출처 | sha256 앞 16 |
|---|---|---|---|---|---|
| USB_C_Receptacle_HRO_TYPE-C-31-M-12.step | 캐리어 J3 | x ±4.47 × y ±3.65 | 3.26 | HRO TYPE-C-31-M-12 REV A (2020-12-08) 측면도 — LCSC C165948 원문 | bc48835b529d5556 |
| RJ45_Hanrun_HR911105A_Horizontal.step | 캐리어 J5 | x −3.58…12.46 × y −4.04…17.26 (16.04 × 21.30) | 13.50 | HanRun HR911105A REV A/2 p2 — LCSC C12074 원문 | 965b414e5af75a0f |
| L_Bourns_SRP7028A_7.3x6.6mm.step | 캐리어 L1 | x ±3.35 × y ±3.30 + 단자 x ±4.2 × y ±1.75 | 3.0 (2.8 ±0.2 최대) | Bourns SRP7028A — Farnell 사본 (2차 출처) | bb3a99b9c254843b |
| SOT-523.step | 캐리어 Q3·Q4, 전면 Q3·Q5·Q7 | x ±0.4 × y −0.8…0.8 + 리드 x ±0.9 × y ±0.7 | 0.90 (최대) | Union-IC Outline SOT523 Rev.02 (2차 출처) | 52ee0567c1febc10 |
| Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm.step | 전면 X1 | x ±1.0 × y ±0.8 + 패드 범위 | 0.80 (0.75 + 여유) | SiTime 2.0×1.6 — 유통사 0.75 (미확인) | 9b1cb046c9d063d1 |

**pcb 연결 규칙 (orch가 pcb에 전달):**
- 원점 = 풋프린트 원점, 회전 0, 오프셋 0, 배율 1, 단위 mm.
- 모델 +Z = 부품 윗면 방향이다. 뒷면 실장은 KiCad가 뒤집는다.
- 경로(보드 파일 기준 상대): `${KIPRJMOD}/../../../mechanical/models/<파일>.step` (`hardware/schematic/<board>/`에서 저장소 루트까지 3단계)
- 리드는 두께 0.15 상자로 나타낸 단순 외형이다. 간섭·렌더용이고 제조용 정밀 모델이 아니다.
- 만든 스크립트: `mechanical/m007/scripts/01_models.py` (사양 `models_spec.py`, KiCad 10 표준 풋프린트의 F.Fab·패드에서 XY를 읽음)

## 2. 조립 틀 구성 (`scripts/02_assembly.py`, 사양 `asm_spec.py`)

| 부분 | 출처 |
|---|---|
| 캐리어·전면 보드 (부품 3D 포함) | pcb 커밋 → kicad-cli `pcb export step --subst-models --drill-origin` (판 아랫면 z 0 → 적층 높이로 옮김) |
| 코어 모듈 외형·keep-in·짝 BTB 외형, 센서 블록·받침·렌즈 CIL093·IR LED 4 | `mechanical/step/stack-reference.step` (M-001/M-002b, Seeed 형상 없음) |
| 덮개 B 창 가운데 연장 (J5 개선 V4, `mechanical/m003/params.py` `b_ext`) | M-003 원본에 반영(O-94) — 조립은 원본 형상을 그대로 쓴다. 비교는 `led_study.md` |
| CLA216 (M-008 방향 수정)·스페이서·리드·ICR 패드·DF30 (0, −11.55)·FPC | `mechanical/m008/cla216_spec.py` |
| 외함 HOUSING/FRONT_COVER, SK 444 방열판 + 받침대, PMMA 창 4, 폼 2, P340 패드, 방열판(내부), 스탠드오프·나사 | `mechanical/m003/params.py` + `geom.py` (M-003/M-005 — 8089 레인 사본, 이 레인에서 고치지 않음) |
| 커넥터 개구·플러그 블록 위치 | pcb 커밋의 J2·J3·J4·J5 Fab 외곽으로 덮어씀 (`boards/connectors.json`) |
| microSD 카드 삽입 블록 | 11 × 1, 소켓 앞면 y 19.6부터 바깥 +20 |
| GH 6P 하니스 26AWG 35 mm | 6가닥 튜브, 플러그 뒤 → −X → 대각선 → +X (모서리 2개, R 3.0). 경로 **24.72**, 남는 길이 **10.28**은 −X 통로(자리 표시) 안에서 느슨하게 휜다고 보고 모델에는 넣지 않음 |

- 대체되어 숨긴 기준 바디: CARRIER/FRONT 상자, 옛 창·칼라·방열판·기둥·절연 패드, GH·ICR 자리 표시, 옛 CLA216·스페이서·리드·DF30·FPC.

## 3. 기계 판정 (`judge.md` — 현재 pcb 3012bf3, 03_judge **실패 4**, 조건 5 결과 파일 불합격 항목 **7** = 실패 4 + 3D 모델 빠진 보드 2 + J3 삽입 1)

| 항목 | 결과 |
|---|---|
| J1 바디 쌍 간섭 (181 바디) | **실패 4:** USB-C 플러그 ↔ 캐리어 PCB 가장자리 9.72 mm³ (**O-61 — pcb 3012bf3에도 J3 x −19.455 그대로**) · 스페이서 ↔ 전면 R9·R10·R11 각 0.15 mm³ (**M-008 F1–F3 이동 전**). 의도 14건은 이름 규칙으로 목록화 (keep-in ↔ 짝 BTB·스탠드오프, 하니스 ↔ 통로, DC 잭 일반 모델 ↔ XKB 블록, 홀더 ↔ 렌즈 나사, FPC ↔ 센서 블록, 리드 ↔ 패드, DF30 외형 ↔ J3) |
| J2 최소 틈 (16쌍) | 모두 통과 — 렌즈 ↔ 덮개 0.6 · 렌즈 ↔ 렌즈 창 0.5 · 받침대 ↔ 벽 창 0.3 · 하니스 ↔ 벽 0.3 · USB 플러그 ↔ 개구 0.225 · DC 0.25 · RJ45 2.0 · 카드 0.65 · CLA216 ↔ LED A 2.65 |
| J3 플러그·카드 삽입 공간 | 실패 1 (= J1의 USB-C ↔ PCB). 외함 개구와는 모두 틈 있음 |
| J4 광축 ↔ 렌즈 창 중심 | 0.000 mm 통과 |
| J5 LED 직접광 (광선 추적, A+B, 시야 19 × 13 방향) | **97.6%** (V4 반영, 기준 analysis2 86%, O-69). 원형 M-003은 84.6% — 놓친 방향은 전부 시야 아래 2줄이고, 원인은 B 창 턱 바깥 끝 y −27.4다. 렌즈 경통 그림자는 이 지표를 바꾸지 않는다(가리는 방향은 B가 비춤). 안 7개 비교와 선택 이유는 `led_study.md` |
| J6 짝 BTB 결합 높이 | 8.000 / 8.000 (3사 높이표 8.00, M-006: 3D 모델로는 판정 불가) |

- **pcb가 O-61(J3 −X 약 1.0)과 M-008 F1–F3를 반영하면 실패 0이 될 것으로 본다.** 그때 `run_all.py --pcb <새 커밋>`으로 확인한다.

## 4. 하니스 관찰 (O-77b 26AWG)

- GH 단자 SSHL-002T-P0.2는 26~30AWG를 받는다(RS 판매 표기). 피복 외경 범위는 원문을 찾지 못했다.
- GH 핀 간격 **1.25**보다 굵은 피복(일반 UL1007 26AWG 약 1.4–1.5)은 나란히 들어가지 않는다.
- 모델은 외경 1.0(가정)으로 넣었다. **26AWG 얇은 피복 전선이 필요하다** → pcb·research 확인 요청.

## 5. 해시 (sha256)

| 파일 | 해시 |
|---|---|
| validation/runtime/vd001/m007_assembly.step | a330f6b21abffd1ca11b444283c3158b42e44988c840d3c120454ce4d01ecef7 |
| boards/carrier.step (pcb 3012bf3) | judge.md §입력·산출 해시 |
| boards/front.step (pcb 3012bf3) | judge.md §입력·산출 해시 |
| render_m007/m007_front_iso.png (2560×1440) | 8ac10eddd744daf3386837c6d4182c7c7e3235f943eb1d195a464d166f025e3f |
| render_m007/m007_back_iso.png | 6a9d55b519e0c85295deb5ba423a034a22f7c3f7a5e9c96a0962c15c6acfbead |
| render_m007/m007_section_x0.png | 3746c866fd0db9365db058b1566a91e53f3aa8dafe86d3a489ec52954c8091f9 |
| render_m007/m007_section_y0.png | edcd83bb575623c35c100e971be1b89d692b3aefac09109ffdaed871ccb8289e |
| render_m007/m007_exploded.png | 2afca46b786ee1b3fc74a8d3cc1353013eafdcc3ab5a5bd8217f4ba7b50895a2 |

## 6. 돌린 것

| 명령 | 결과 |
|---|---|
| 01_models (fusion_cli) | 종료 0. 첫 실행은 F.Fab 파서가 항목 경계를 넘어 외곽이 커짐 → 항목 단위로 고쳐 재실행 |
| run_all.py --pcb 3012bf3 (전체) | 종료 7 (= 불합격 항목 7, 위). J5 V4 반영 뒤 같은 문서에서 렌더 · REN-001 메시를 만듦. 고친 경과: ① 판정 이름 불일치(렌즈 = `LENS_CIL093` 한 부품) ② 하니스 외경 1.5가 GH 간격 1.25보다 굵어 가닥끼리 겹침 → 1.0 + 모델 간격 1.6 ③ 카드 블록이 소켓 모델 안까지 → 소켓 앞면부터 ④ 커넥터 위치를 pcb에서 직접 읽게 함 ⑤ 기준 자리 표시 ↔ 실제 KiCad 모델 중복을 대체 목록으로 |
| 04_render | 종료 0, PNG 5장 2560×1440 |
| 저장소 검사 명령 | 없음 → 돌리지 않음 |
