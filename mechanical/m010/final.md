# M-010 최종 (O-124) — main 995b872 보드 · Fusion 케이스 판정

- 명령:
  ```
  python -I -B mechanical/m010/run_case.py --pcb-carrier 995b872 --pcb-front 995b872
  ```
  - 종료 코드 0, 막힌 단계 0/17 (`run.md`).
  - 조건 5는 `run_all.py`로 종료 코드 0, 불합격 0 (`mechanical/m007/judge.md`, 결과 파일 `validation/runtime/vd001/results/cond5-mechanical.json`).
- 두 보드 모두 DRC 0 (pcb 995b872). 3D 모델 빠짐: 원본 0 · 연결 사본 0. kicad-cli STEP `--subst-models --user-origin 100x100mm`.
- **케이스 수정 없음.**
  - params.py와 pcb fab 커넥터 위치 차이 0.
  - 내보낸 외함 STL의 sha256이 커밋된 `mechanical/m003/out`과 같다: HOUSING a4bd9a46… · FRONT_COVER 98ec5c78… · PRINT_COUPON 81b0e098….

## 1. 판정 (verifiable = 기계 증거로 가림)

| 항목 | 값 | 기준 | verifiable | 판정 |
|---|---|---|---|---|
| 5.M-carrier 3D 모델 빠짐 (kicad-cli STEP 내보내기) | 0 | 0 | 예 | 통과 |
| 5.M-front 3D 모델 빠짐 (kicad-cli STEP 내보내기) | 0 | 0 | 예 | 통과 |
| 5.J1 조립 간섭 (의도 37건 제외) | 0 | 0 | 예 | 통과 |
| 5.J2-1 최소 틈 LENS_CIL093 ↔ FRONT_COVER | 0.6 | >= 0.3 | 예 | 통과 |
| 5.J2-2 최소 틈 LENS_CIL093 ↔ LENS_WIN_PMMA | 0.5 | >= 0.3 | 예 | 통과 |
| 5.J2-3 최소 틈 HS_PEDESTAL ↔ HOUSING | 0.3 | >= 0.2 | 예 | 통과 |
| 5.J2-4 최소 틈 SPREADER_M003 ↔ HOUSING | 1.0 | >= 0.3 | 예 | 통과 |
| 5.J2-5 최소 틈 HARNESS_GH6P ↔ HOUSING | 0.3 | >= 0.1 | 예 | 통과 |
| 5.J2-6 최소 틈 HARNESS_GH6P ↔ SPREADER_M003 | 4.296 | >= 0.1 | 예 | 통과 |
| 5.J2-7 최소 틈 BLK_J3_PLUG ↔ HOUSING | 0.225 | >= 0.0 | 예 | 통과 |
| 5.J2-8 최소 틈 BLK_J5_PLUG ↔ HOUSING | 2.0 | >= 0.0 | 예 | 통과 |
| 5.J2-9 최소 틈 BLK_J2_PLUG ↔ HOUSING | 0.25 | >= 0.0 | 예 | 통과 |
| 5.J2-10 최소 틈 BLK_J4_CARD ↔ HOUSING | 0.65 | >= 0.0 | 예 | 통과 |
| 5.J2-11 최소 틈 FOAM_ALS_GASKET ↔ FRONT_COVER | 0.0 | >= -0.01 | 예 | 통과 |
| 5.J2-12 최소 틈 LED_A1 ↔ FRONT_COVER | 10.348 | >= 1.0 | 예 | 통과 |
| 5.J2-13 최소 틈 CLA216_M008 ↔ LED_A1 | 2.65 | >= 1.0 | 예 | 통과 |
| 5.J2-14 최소 틈 CLA216_M008 ↔ LED_A2 | 2.65 | >= 1.0 | 예 | 통과 |
| 5.J2-15 최소 틈 DF30_M008 ↔ LED_B1 | 2.173 | >= 1.0 | 예 | 통과 |
| 5.J3 플러그·카드 삽입 공간 (블록 간섭 수) | 0 | 0 | 예 | 통과 |
| 5.J4 광축 ↔ 렌즈 창 중심 어긋남 mm | 0.0 | <= 0.1 | 예 | 통과 |
| 5.J5 LED A+B 직접광 방향 % (시야 19×13) | 97.6 | >= 84 (analysis2 86) | 예 | 통과 |
| 5.J6 짝 BTB 결합 높이 mm | 8.0 | 8.0 | 예 | 통과 |
| D5 이동 (전면 B면 D_SOD-323, 기구 (3.3, −2.55), z 8.405…9.515) ↔ 가장 가까운 기구 바디 | 3.651 mm (SPACER_M008/SPACER_M008) | > 0 (간섭 없음) | 예 | 통과 |

- 플러그 삽입: 5.J3 = 0. 최소 틈은 USB-C 0.225, RJ45 2.0, DC 0.25, microSD 카드 0.65 mm.
- 광축: 5.J4 = 0.000 mm.
- LED 창: 5.J5 = 97.6 %, 5.J2-12 = 10.348 mm.
- D5 근처 다음 바디: FPC_M008 3.987 · CLA216_M008 4.467 · SPREADER_M003 4.505 · DF30_M008 5.609 mm (`mechanical/m010/scripts/10_part_gap.py`, 결과 `validation/runtime/vd001/m010_part_gap.json`).
- M003 외함 문서 간섭(`case/interference.txt`): 생성물이 낀 것 3건. 모두 기존 의도(keep-in 2, 하니스 통로 0.255 mm³)이고, 대체 블록 9개는 뺐다(보드 3D 모델 연결).

## 2. 산출 (main 체크아웃 `validation/runtime/vd001/`, gitignore — 렌더 파이프라인 입력)

| 파일 | 바이트 | sha256 |
|---|---|---|
| `boards/carrier.step` | 4538912 | `d141704ca7e992b1f50fc6a37677f4d165dfd601e072c9f35e3517a71b177048` |
| `boards/front.step` | 1918627 | `ae9e5d1455fce65e407fb2aca9ad336817fd17492dacb1067fafac3faef4386e` |
| `case/M003_enclosure.f3d` | 4462839 | `5fa128ac711f70954e2f334326835d0679ab9b05a80d404e3f789fcb9605b2f8` |
| `case/M003_assembly_with_refs.step` | 6710705 | `925dafe625fb6dc3d1dc54d184b87580f125c002e77a5011c2b4ce0fb7a02b31` |
| `case/step/ALS_WIN_PMMA.step` | 15328 | `0487edf5f548b8ce9c455a1659c2b350d6b24cc127d775b68edfb1035e5893e6` |
| `case/step/FOAM_ALS_GASKET.step` | 14578 | `cbab598fba0c69a7de01c52779027225d66d78d95d87265c1f24e201f10ab07a` |
| `case/step/FOAM_LENS_RING.step` | 7682 | `281437f1399aa4be7406029361bd07dbae22e59209f6ecf8719f36f76d4127ee` |
| `case/step/FRONT_COVER.step` | 70115 | `964f7f8bea8e45a8dd4c2eaaa343da81ae9f058f1f46bf5dbc4a0a31f06b2c22` |
| `case/step/GAP_PAD_PX.step` | 9524 | `ad501035a32b987ce9ec1c592075b9431f97f77683944b117b28c80e9ac24e30` |
| `case/step/HOUSING.step` | 118228 | `fbd5053e4619efc7cd61a4b3dd661c7f0a27b648e21d732b00bd69a27d151907` |
| `case/step/HS_EXTRUSION.step` | 78051 | `ce515d88a49738b2d2161ffd88495d15ba5673a097dcaa2424c3c473373b1af5` |
| `case/step/HS_PEDESTAL.step` | 15022 | `a62ef2f95d3b993189608b875b2da265709e3154106b651f926a4b1eb528ef49` |
| `case/step/INS_PADS_P340.step` | 23385 | `b3bf236331245300c36aceb954a17cf37fee06660a0c3f3e1b08260afab25cd4` |
| `case/step/LENS_WIN_PMMA.step` | 6091 | `3b61ff73cb9b188965aa90cbcb5d25e6e4d0967537dc6b38a1ae812fca77a7c5` |
| `case/step/SPREADER_M003.step` | 46570 | `c46cfae8d672e5dbd51fa67ca940441c6ac6568b02523f82150b69b89523197b` |
| `case/step/WIN_A_PMMA.step` | 15277 | `f2350bee26deda3436ea912649e12c904a787de2d479719a665df8d1db4f0cf8` |
| `case/step/WIN_B_PMMA.step` | 23226 | `218ec8da9e84b807c321691137ee6db9e59236a68f7a606ee518f6f3bbdd590f` |
| `case/stl/FRONT_COVER.stl` | 84284 | `98ec5c78024f4be40adcffe2e3369e7370b38c3e889931be4fb027b17a28f5b3` |
| `case/stl/HOUSING.stl` | 279684 | `a4bd9a46875710f6732b193fcac3b2a65afe18a11cf6136504a2e18feb982c70` |
| `case/stl/PRINT_COUPON.stl` | 90284 | `81b0e09840e222987352a7af581fb52f7d2fc73a849e22e110a06f102450c112` |
| `m007_assembly.step` | 7041911 | `4826d5ab136b46f612b09cb363a5a912a1fd8a45182af921c0f8d0de761a5319` |

- Blender 최종 렌더(REN-003b)는 메시 입력으로 `render/mesh/*.stl` · `render/mesh/board_*.glb`(같은 실행)를 쓴다. 외함 형상만 필요하면 `case/stl` · `case/step`.

## 3. Fusion 스크린샷 (사람 확인, verifiable 아니오)

- `validation/runtime/vd001/render_m007/`: m007_front_iso · back_iso · section_x0 · section_y0 · exploded (2560×1440, 뷰포트 캡처).
- 대표본 `docs/renders/final/`: fusion-case-section.png(=section_x0) · fusion-case-iso.png(=front_iso) · fusion-case-exploded.png(=exploded).
  - iso와 exploded는 REN-003 Fusion 재질 로컬 렌더가 나오면 바꿀 수 있다.

| 파일 | 바이트 | sha256 |
|---|---|---|
| `docs/renders/final/fusion-case-section.png` | 390124 | `7b87e59bbcae0c63db1b4a43900b9ea70188ca9da92a5cb7d9203f647faa9fda` |
| `docs/renders/final/fusion-case-iso.png` | 276779 | `bc78d99cbbedcb7539814da80e8a00433f7c58c0ccde6f0372ef3b7ea901546d` |
| `docs/renders/final/fusion-case-exploded.png` | 331815 | `8c148dc91e34e00c2cab52ad02dd846da66c34efacddbd3bb9f6732b6f09c8b9` |

## 4. 실패와 고침

- 첫 실행: Blender 단계가 막혔다(`scene.py` 오류 — REN-003 보드 재질 루프의 변수 `k`가 전역 축척 `k`를 덮어씀).
  - Blender는 스크립트 오류에도 종료 코드 0을 돌려줘서 「Blender 스틸 rc 0」으로 보였다.
  - 고침: 변수 이름을 `mk`로 바꿈. run_case의 Blender 호출에 `--python-exit-code 1`을 붙임.
  - 재실행: 막힌 단계 0.
- Fusion이 두 번 꺼져 있었다(첫 실행 전, 계정 재로그인 뒤). 둘 다 `Fusion360.exe`를 직접 띄웠다. 런처는 띄우자마자 꺼졌다.
  - 재시작 뒤 조립 문서를 다시 만들었다(`run_all.py`, 판정 같은 값). 그다음 D5 측정과 스크린샷을 했다.
  - Fusion 만료 표시: 「3일 후에 만료」.
