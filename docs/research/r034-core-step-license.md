# R-034L 코어 모듈 형상(STEP) 라이선스 확인 (O-131)

조사일 2026-11-28 · 외부 읽기만(GitHub API, 계정 쓰기 없음) · 대상 `Seeed-Studio/OSHW-reCamera-Series` 커밋 `f5fcf0abce794806ffbd7a274686f022bb0acd4b`(조사 시점 `main` 과 같음, 2026-09-18)

## 결론

- **렌더 · 영상에 코어 모듈 형상을 쓰는 것은 허용된다.** 저장소 기본 라이선스(Apache 2.0)로 보든, 같은 설계의 회로도 표제란(CC BY-SA 4.0)으로 보든 둘 다 상업 이용을 포함한 복제 · 변형 · 배포를 허락한다. STEP 파일 자체는 저장소에 넣지 않는다(아래 ⑤에서 확인).
- **적용 라이선스는 문서상 갈린다.** STEP 파일과 그 폴더에는 라이선스 문구가 없어 문자 그대로는 저장소 기본값 Apache 2.0이다. 그러나 이 STEP은 표제란에 CC BY-SA 4.0이 찍힌 같은 코어 보드 설계를 KiCad에서 내보낸 것이다.
- **기본값(보수적): CC BY-SA 4.0으로 취급한다.** 코어 형상이 들어간 렌더 · 영상에 출처를 표기하고, 그 렌더 · 영상 파일은 CC BY-SA 4.0으로 배포한다고 적는다. 이 조건을 지키면 Apache 2.0 조건(출처 · 라이선스 고지)도 함께 충족된다.

| 분기점 | 고른 것 | 이유 | 차선책 |
|---|---|---|---|
| STEP에 적용할 라이선스 | CC BY-SA 4.0으로 취급 | 파일에 문구가 없지만 원 설계(회로도) 표제란이 CC BY-SA 4.0이다. 더 엄격한 쪽을 지키면 두 해석을 모두 만족한다 | Apache 2.0만 적용(출처 + 라이선스 고지만, 렌더 파일 라이선스 제약 없음) — Seeed가 STEP의 라이선스를 Apache 2.0으로 따로 밝힐 때 |

## 근거 (원문 인용)

**① 저장소 루트 LICENSE** — Apache License 2.0
https://github.com/Seeed-Studio/OSHW-reCamera-Series/blob/f5fcf0abce794806ffbd7a274686f022bb0acd4b/LICENSE
- 첫 줄 「Apache License / Version 2.0, January 2004」 · 추가 커밋 `1ec9db953a`(2024-08-20, "Create LICENSE") · GitHub 라이선스 판정 `Apache-2.0`.
- `NOTICE` 파일은 저장소에 없다(트리 197개 경로 확인).

**저장소 readme.md (83행 부근)**
https://github.com/Seeed-Studio/OSHW-reCamera-Series/blob/f5fcf0abce794806ffbd7a274686f022bb0acd4b/readme.md
> "Unless a file says otherwise, repository content is provided under the [Apache License 2.0](LICENSE)."

**② STEP 파일과 그 폴더**
- 파일: `hardware/recamera-2002/core/c1-2002/3D_Printed_Case/Recamera Core 2002.step` — 18,887,912 B · sha256 `7de9f15f29d9645e57321e57cf6ce0f864bc81fdfdc1a1a9490f0500b8ac8785`(우리 기록 `hardware/schematic/hw-fw-contract.md` 와 같음) · 추가 커밋 `5cf69c43db`(2026-08-21, "chore: establish repository structure").
- STEP 머리말: `FILE_DESCRIPTION(('KiCad electronic assembly'),'2;1');` · `FILE_NAME('Recamera Core 2002.step','2024-10-23T16:04:32',('Pcbnew'),('Kicad'),…,'KiCad to STEP converter',…)` — 코어 보드 KiCad PCB에서 내보낸 조립 형상이다. 파일 안에 licen · copyright · creative · CC BY 문자열 0건.
- `3D_Printed_Case/` 폴더에는 LICENSE · README가 없다. 바로 위 `core/c1-2002/README.md` 는 라이선스를 말하지 않고 "Mechanical files are in [3D_Printed_Case](3D_Printed_Case/)." 라고만 쓴다.
  https://github.com/Seeed-Studio/OSHW-reCamera-Series/blob/f5fcf0abce794806ffbd7a274686f022bb0acd4b/hardware/recamera-2002/core/c1-2002/README.md
- `hardware/README.md` · `hardware/recamera-2002/README.md` · `CONTRIBUTING.md` 에도 라이선스 문구가 없다.

**③ 회로도 표제란 (R-003)**
- `hardware/recamera-2002/core/c1-2002/static/reCamera_Core_2002w_8GB_v1.2_SCH_PDF_241014.pdf`(sha256 `95fbc621…`, 우리 사본 `hardware/datasheets/seeed/recamera-2002/`) — 쪽마다 표제란에 「Date: 2024-04-25 · CC BY-SA 4.0」(1~3쪽 텍스트 추출로 다시 확인).
- 관계: 저장소 문구 "Unless a file says otherwise" 의 "file" 에 회로도 PDF는 해당한다(그 파일이 CC BY-SA 4.0이라고 말함). STEP은 스스로 말하지 않으므로 문자 그대로는 Apache 2.0이다. 다만 같은 코어 보드 설계에서 나온 산출물이고, 설계자가 그 설계에 CC BY-SA 4.0을 표시했으므로 형상에도 같은 의도가 있을 수 있다 → 판단이 갈려 보수적으로 CC BY-SA 4.0.

## 조건 (기본값 CC BY-SA 4.0 기준)

1. **출처 표기(BY):** 원 저작자 · 출처 링크 · 라이선스 이름과 링크 · 바꿨다는 사실을 적는다.
2. **같은 조건(SA):** 코어 형상이 보이는 렌더 · 영상은 원 형상을 다른 부품과 함께 배치하고 재질 · 조명을 입힌 각색물(Adapted Material)로 볼 수 있다 → 그 파일들을 CC BY-SA 4.0(또는 호환 라이선스)으로 배포한다고 적는다.
3. **범위:** 우리 케이스 · 보드 설계 파일은 코어 STEP을 고쳐 만든 것이 아니라 그 바깥 치수에 맞춘 독자 설계라서 이 조건이 번지지 않는다고 본다. 같은 이유로 `README` 의 "하드웨어 설계 파일 Apache 2.0" 문구는 그대로 두고, 렌더 · 영상에만 예외 고지를 붙인다.
4. **대상 파일(기본값):** `docs/renders/final/` 의 Blender · Fusion 렌더와 `video/`, README 갤러리 사본 `docs/readme/gallery/case-a/`. 바깥만 보이는 컷(정면 · 뒤쪽 등)은 코어가 안 보일 수 있지만, 한 묶음으로 고지하는 쪽이 단순하고 안전하다.
5. **STEP 비포함 확인:** `main` 에 커밋된 `*.step` · `*.stp` 에서 "Recamera Core" · "Core 2002" · "C1-2002" 이름 0건(조립 판정용 코어 STEP 사본은 커밋하지 않는 실행 폴더에만 있음). 형상 대조까지는 하지 않았다.

## 표기 문구 (렌더 · 영상 고지용)

한국어:
> 렌더 · 영상 속 코어 모듈 형상은 Seeed Studio [OSHW-reCamera-Series](https://github.com/Seeed-Studio/OSHW-reCamera-Series)(커밋 `f5fcf0a`)의 `Recamera Core 2002.step` 에서 가져와 다른 부품과 함께 배치하고 재질 · 조명을 입혔다. 원 설계는 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)(저장소 기본은 Apache 2.0)이며, 이 형상이 들어간 렌더 · 영상 파일(`docs/renders/final/`, `docs/readme/gallery/case-a/`)도 CC BY-SA 4.0으로 배포한다.

English:
> The core-module geometry in these renders and videos comes from `Recamera Core 2002.step` in Seeed Studio's [OSHW-reCamera-Series](https://github.com/Seeed-Studio/OSHW-reCamera-Series) (commit `f5fcf0a`), placed with other parts and given materials and lighting. The original design is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) (repository default: Apache 2.0); the render and video files that contain this geometry (`docs/renders/final/`, `docs/readme/gallery/case-a/`) are likewise distributed under CC BY-SA 4.0.

넣을 자리(제안): README 「라이선스 · 제3자 고지」 표에 한 줄 + 케이스 절 아래 한 줄, `docs/renders/final/` 에 위 문구를 담은 짧은 고지 파일. 이 문서는 조사만 하고 그 파일들은 고치지 않았다.
