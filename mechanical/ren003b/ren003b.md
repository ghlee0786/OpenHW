# REN-003b Blender 제품 렌더 파이프라인 (헤드리스, O-125 2단계)

- 범위: `mechanical/ren003b/` 안 파일만 새로 썼다. `mechanical/ren003/materials.py`·`m003`·`m010`·`ren002`는 읽기만 했다. Fusion은 쓰지 않았다.
- 한 명령:
  ```
  python -I -B mechanical/ren003b/run.py                 # 저해상도 시험 (현재 외함, 컷 6 + 턴테이블 24프레임)
  python -I -B mechanical/ren003b/run.py --final         # 4K 컷 6 + 턴테이블 200프레임 1080p + 대표본
  python -I -B mechanical/ren003b/run.py --design A --final   # 시안 히어로 4K 1장
  ```
- 종료 코드 = 불합격 항목 수. 기계 증거만 판정한다. **사실감·보기 품질은 verifiable 아니오**(사람 확인 전까지 통과 아님).

## 1. 파일

| 파일 | 하는 일 |
|---|---|
| `prep.py` | 메시 준비. 보드 GLB(커밋 사본 → `kicad-cli pcb export glb`, 또는 있는 GLB 복사), 외함 STEP → STL(gmsh OpenCASCADE 삼각화, 곡면 오차 ≤ 0.01 mm), 부품 STL 복사, `index.json` |
| `scene.py` | Blender 장면. 재질 · 베벨 · HDRI · 무한 배경 · 카메라 · 컷 6종 · 턴테이블, `scene_report.json` |
| `materials_ext.py` | 재질 확장(새 재질 6종, 시안 부품 이름 규칙, 미세 질감 노드). `materials.py`는 고치지 않는다 |
| `fetch_hdri.py` · `assets.json` | CC0 HDRI 받기와 출처 · 라이선스 · sha256 기록 |
| `run.py` | 한 명령: 준비 → HDRI 확인 → 렌더 → 1600px 축소 → MP4 → 판정 → `report.json` |

## 2. 입력을 바꾸는 법 (메시만 바꿔 다시 돌리기)

| 인자 | 기본값 (main 체크아웃 `validation/runtime/vd001/`) | 뜻 |
|---|---|---|
| `--case` | `case/step` | 외함 STEP/STL 폴더. STEP은 곡면 오차 0.01 mm로 삼각화한다 |
| `--extra` | `render/mesh` | 외함 폴더에 없는 부품 STL(렌즈 · 나사 · 하니스 · 코어 등). `none`이면 안 쓴다 |
| `--boards-from` | `render/mesh` | 보드 GLB 폴더. `--pcb <커밋>`을 주면 그 커밋 보드를 새로 내보낸다 |
| `--design A` | — | `design/A/`의 부품 STL + 보드로 히어로 1장. 같은 폴더의 통짜 STEP은 쓰지 않는다 |

- 출력은 main 체크아웃 `validation/runtime/vd001/render/blender-b/<tag>/`이다(O-100, 커밋하지 않음).
- 대표본은 `--final`이고 전부 통과일 때만 `docs/renders/final/blender-product.png`(히어로 1600px) · `blender-turntable.mp4`로 복사한다.
- 도구 경로는 환경 변수로 바꾼다: `BLENDER`, `FFMPEG_BIN`, `KICAD_BIN`, `OPENHW_HDRI_DIR`, `OPENHW_MAIN`.

## 3. 장면 설정

| 항목 | 값 |
|---|---|
| 조명 | CC0 HDRI `studio_small_09` 2k (Poly Haven, 세기 0.7 · 회전 110°) + KEY · RIM 면광. 무한 배경(바닥이 곡면으로 벽이 됨) |
| 카메라 | 85~100 mm, f/8 피사계 심도(초점은 제품 앞쪽), hero · rear · inuse는 주제를 3분할선에 |
| 색 관리 | AgX (Medium High Contrast), 노출 `--exposure` |
| 메시 | 겹친 꼭짓점 합침 → 30° 넘는 모서리만 날카롭게 → 베벨 0.3 mm(3단) → Weighted Normal. 얇은 패드 · 폼 · 창은 베벨 제외 |
| 엔진 | Cycles, OptiX GPU(없으면 CUDA → CPU), 적응 샘플링, OptiX 디노이즈 |
| 해상도 | 시험 960×540 · 48 샘플 / 최종 3840×2160 · 256 샘플, 축소본 긴 변 1600 px |
| 턴테이블 | 제품만 돈다(카메라 · 조명 고정). 최종 200프레임 @ 25 fps = 8 s, 1920×1080, libx264 |

컷 (제품을 돌리고 카메라는 정면 쪽에 둔다 — 무한 배경 벽이 늘 뒤에 있다):

| 컷 | 제품 yaw · 고도 · 렌즈 | 내용 |
|---|---|---|
| `hero` | 34° · 16° · 90 mm | 앞 3/4 |
| `front` | 0° · 4° · 100 mm | 정면 |
| `rear` | 146° · 18° · 90 mm | 뒤 3/4 (포트 · 방열) |
| `exploded` | −42° · 20° · 85 mm | 분해도(부품을 제품 축 방향으로 벌림, 바닥 그림자) |
| `section` | 78° · 12° · 100 mm | 단면(제품 x > 0 절반을 평면으로 잘라 내고 잘린 테두리를 면으로 메움) |
| `inuse` | 카메라 방위 36° · 고도 −12° · 85 mm | 벽 브래킷에 달린 모습(무광 벽, 내장 브래킷 소품 또는 시안의 브래킷 부품) |

## 4. 재질

- `materials.py` `MATS` 37종을 그대로 Principled 재질로 만든다. 부품 이름은 `NAME_RULES` → 없으면 `materials_ext.EXT_NAME_RULES` 순으로 본다. 어느 쪽에도 없으면 「재질 빠짐」으로 세고 판정에서 불합격이다.
- 보드는 GLB 재질 원값 + 모델 이름 + 참조 번호로 `body_key()`를 부른다. `keep`(못 가른 색)은 빠짐이다.
- 보충 규칙 2개(REN-002 `scene.py`와 같음): 하니스 6선 색(`HARNESS_GH6P__n`), 렌즈 조각 중 맨 앞 것은 유리.
- 확장(`materials_ext.py`, 값은 보기용 가정):

| 대상 | 덧입힌 것 |
|---|---|
| 무광 흑색 플라스틱 (`petg` · `plastic` · `holder` · `conn_black`) | 미세 잡음 요철(입자 약 0.12 mm) + 거칠기 0.45~0.55 얼룩. `materials.py`의 FDM 층 결 범프는 뗀다 |
| 양극산화 알루미늄 (`anod` · `al` · `mount`) | 한 방향으로 늘인 잡음(헤어라인) + 이방성 0.7 |
| IR 투과 앞유리 (`ir_glass`, 새 재질) | 짙은 검정 · 투과 0.3 · 코팅 0.3 · 박막 110 nm |
| 렌즈 유리 (`glass`) | 코팅 1.0 + 박막 420 nm(보라 · 초록 기미) |
| 투명 창 (`pmma` 등) | 코팅 + 그림자 광선은 통과(창 안쪽에 빛이 들어가게) |
| 고무 · 폼 (`rubber`(새) · `foam`) | 미세 요철 + 약한 sheen |
| 나사 · 쉘 (`steel` · `brass` · `shield` · `lens`) | 거칠기 얼룩 + 이방성 0.35 |
| 실크 라벨 | 앞 덮개 아래 가장자리에 「OpenHW」 글자(시안은 음각이 있어 뺀다) |

## 5. 시험 결과 (기계 증거)

| 실행 | 결과 |
|---|---|
| 1단계 기본 장면 (EEVEE 960×540, M-010 최종 메시, 48프레임) — 커밋 `b32d5f2` | 종료 0. 객체 190 · 재질 37/37 · 빠짐 0 · 스틸 3 · MP4 48프레임 |
| 2단계 저해상도 시험 `run.py` (현재 외함 `case/step` + `render/mesh`, Cycles 960×540 · 48 샘플) | 종료 0. 삼각화 0.01 mm(STEP 13개) · HDRI sha256 일치 · OptiX + 디노이즈 · 재질 37/37(+6) · 빠짐 0 · 베벨 11개 · 컷 6/6 · 단면 190객체 · 턴테이블 24/24 · MP4 h264 |
| 시안 A · B 히어로 1차 (흑색 아노다이즈, 틀 반지름 62 mm) | 종료 0. 3840×2160 · 256 샘플 · 빠짐 0. `render/blender-b/design/{A,B}_black_hero.png`으로 남김 |
| 시안 A · B · C 히어로 2차 `run.py --design A|B|C --final` (최종 시안 메시, 아래 §7 설정) | 종료 0 ×3. 3840×2160 · 256 샘플 · OptiX · 빠짐 0. 출력 `render/blender-b/design/{A,B,C}_hero.png` · `_hero_1600.jpg` · `ABC_sheet.jpg` |

- `--final` 전체 세트(4K 컷 6 + 200프레임)는 아직 돌리지 않았다. 사용자가 시안을 고른 뒤 최종 메시로 돌린다(O-125 3단계).

## 6. 분기점 · 가정 · 미확인

| 분기점 | 고른 것 | 이유 | 차선 |
|---|---|---|---|
| STEP → 메시 | gmsh의 OpenCASCADE 삼각화(선형 편차 0.01 mm · 각 편차 0.1 rad) | Blender에 STEP 가져오기가 없다. 격자 생성보다 평면이 큰 삼각형으로 남아 베벨이 깨끗하다 | Fusion 고해상도 STL(시안은 이쪽) |
| 뒤 3/4 · 단면 컷 | 카메라가 아니라 제품을 돌림 | 무한 배경 벽이 늘 화면 뒤에 있다 | 배경을 원형으로 |
| 시안의 브래킷 부품 | 히어로에서 숨기고 사용 장면에서만 보임 | 브래킷 없는 시안과 비교가 안 되고 구도가 달라진다 | 히어로에 같이 |
| 시안끼리 같은 카메라 | 틀 반지름 62 mm 고정 | 시안마다 크기가 달라도 거리 · 조명이 같다 | 시안마다 맞춤 |
| FDM 층 결 | 뗌 | O-125는 사출 제품 표면 | `materials.py` 그대로 |
| IR 앞유리 | 투과 0.3 · 코팅 0.3 | 코팅 1.0이면 흰 스튜디오가 비쳐 검정이 회색으로 뜬다 | 투과 0.55 |

- 가정: 재질 확장 값은 모두 보기용이다(측정값 아님). HDRI 회전 · 조명 세기는 제품 반지름 60 mm 기준으로 잡았다.
- 미확인: 사실감 · 구도 · 색은 사람이 봐야 한다. 턴테이블 1080p 200프레임의 렌더 시간은 재지 않았다.
- 알려진 한계: 히어로에서 투명 PMMA 창(현재 외함)은 비스듬히 보면 안쪽 무광 면이 얼룩으로 비친다. 시안의 IR 앞유리에는 해당 없다.

## 7. 시안 히어로 설정 (lead 지시 반영, 세 장 같은 조건)

- 명령: `python -I -B mechanical/ren003b/run.py --design <A|B|C> --final` (흑색 알루미늄 비교판은 `--alu black` → 이름에 `_black`).
- 입력: `design/<이름>/`의 부품 STL(같은 폴더의 통짜 STEP과 「이름 (1)」 같은 중복 파일은 쓰지 않는다) + 보드 GLB + 내부 부품 5종(`materials_ext.DESIGN_INTERNALS`: 렌즈 경통 · 센서 · 받침 · 코어 · FPC, `render/mesh`에서).
- 카메라 · 조명: 틀 반지름 80 mm 고정(가장 큰 C에 맞춤), 제품 yaw 34° · 고도 24° · 90 mm · f/8, 3분할 이동 −0.18(중앙 쪽).

| 항목 | 설정 |
|---|---|
| IR 앞유리 (`ir_glass`) | 스모크 유리: 직진 투과 면당 0.5(두 면 약 25 %) + 프레넬 반사. 광축 둘레 반지름 7.5 mm 원 안은 투명 + 코팅 반사색(보라 → 초록) |
| 유리 하이라이트 띠 | 4K 히어로 3장(커밋 `f027228`)은 유리의 거울 반사 방향에 둔 띠 조명(`GLASS_STRIP`)으로 만들었다. 그 뒤 §8에서 재질 안 계산으로 바꿨다. **렌더 전용** |
| 유리 안쪽 보조광 | 4K 히어로 3장은 유리 바로 뒤 위 · 아래 점광 2개(각 0.03 W)를 썼다. §8에서 렌즈에만 비추는 면광으로 바꿨다. **렌더 전용** |
| 렌즈 | 내부 적층의 `LENS_CIL093` 메시를 그대로 넣었다(새로 만든 형상 없음). 맨 앞 조각은 유리(박막 코팅) |
| 알루미늄 (`SHELL_ALU` → `anod_grey`) | 스페이스 그레이 + 헤어라인 + 볼록 모서리 다이아컷(밝고 매끈하게, Cycles Pointiness) |
| 렌즈 링 (`LENS_RING` → `al`) | 밝은 알루미늄 |
| 플라스틱 두 톤 | 본체 `SHELL_PLASTIC` = 차콜(`petg_shell`), 그 밖 플라스틱 = 짙은 흑색(`petg` · `plastic`). 한 부품 안에서 톤을 나누지는 않았다 |
| 상태 LED (`LIGHT_PIPE` → `lightpipe_on`) | 청록 발광(세기 2.5) |
| 바닥 | 무한 배경에 약한 반사(코팅 0.25) |
| 브래킷 | `A_WALL_BRACKET`은 히어로에서 숨김(사용 장면 컷에서만) |

- 가정 · 해석: 「플라스틱 두 톤」은 본체와 그 밖 플라스틱의 톤 차이로 풀었다. 유리 투과율 · 보조광 세기 · 다이아컷 밝기는 보기용 값이다.

## 8. 고른 시안의 전체 세트 (O-126 — 사용자 선택 A)

- 명령:
  ```
  python -I -B mechanical/ren003b/run.py --design A --full --glass-t 0.15                       # 저해상도 미리보기 → design/A_preview/
  python -I -B mechanical/ren003b/run.py --design A --full --glass-t 0.15 --final --case <상세 설계 메시 폴더>   # 4K 컷 6 + 턴테이블 200프레임 1080p → design/A_final/ + 대표본
  ```
  - `--case`를 주면 `design/A/` 대신 그 폴더의 부품 STL을 쓴다(상세 설계 메시가 오면 이 인자만 바꾼다). 다른 시안이면 `--design`만 바꾼다.
  - `--full`은 틀을 제품 크기에 맞춘다(시안 비교용 80 mm 고정 틀은 히어로 1장 모드에서만).
  - 4K 히어로 비교판(`design/<이름>_hero.png`)은 `--final`이고 `--full`이 아닐 때만 쓴다. 미리보기가 덮어쓰지 않는다.
- 대표본(`--final --full`이고 전부 통과일 때, 1600px): `docs/renders/final/blender-{product,front,rear,exploded,section,inuse}.png` · `blender-turntable.mp4` · `blender-turntable-poster.jpg`. 4K 원본은 `validation/runtime`에만 둔다.
- 기판 비침 확인 그림: `<출력>/pcb_check/{hero,front}_x3.jpg` (원본 | 밝기 3배). 사람이 본다(verifiable 아니오).

| 항목 | 설정 · 바꾼 이유 |
|---|---|
| 유리 투과 | `--glass-t 0.15`(두 면 합, 면당 √0.15). 기본값(약 0.25)은 `materials_ext.py`에 그대로 둔다 |
| 유리 하이라이트 띠 | 조명이 아니라 유리 재질 안에서 계산한다(`smoke_glass`의 `CARD_*` 노드, `stage()`가 컷마다 거울 반사 방향에 맞춤). 띠 조명은 내려다보는 컷에서 반사 광선이 바닥에 막혀 컷마다 밝기가 달랐고, 정면 컷에서는 하얗게 탔다 |
| 렌즈 보조광 (`LENS_FILL`) | 카메라 쪽 0.25 m에서 렌즈 부품에만 비추는 면광 1개(8 W, 빛 연결). 유리 안쪽 점광은 렌즈 바로 위에서 경통을 태우고 기판 글자를 드러냈다. 분해 · 단면 컷에서는 끈다. **렌더 전용** |
| 분해도 | 시안 부품 이동량 추가: 앞유리 +95 · 플라스틱 쉘과 광 파이프 +60 · 알루미늄 쉘 −75 (제품 Z, mm) |
| 단면 | 메시를 평면 x = 0 으로 직접 자르고(bisect) 잘린 테두리를 면으로 메운다. 불리언은 닫히지 않은 메시 · 아주 큰 메시(알루미늄 쉘 112만 삼각형)에서 빈 결과나 깨진 면을 냈다. 자른 쪽에 남은 객체 수를 판정한다. 닫히지 않은 작은 보드 부품은 단면이 열린 채로 남는다(수를 기록) |
| 사용 장면 | 시안의 브래킷 부품이 제품 아래(−Y)로만 뻗어 있으면 그 판을 벽에 붙인다(광축이 아래). 뒤(−Z)로도 뻗어 있으면 벽판이 뒤에 있는 것이라 서 있는 자세 그대로 둔다(`scene_report.json` `inuse_pose`). 내장 소품도 서 있는 자세 |
| 턴테이블 | 중심과 틀 크기를 첫 자세로 고정한다(프레임마다 범위 상자로 다시 잡아 제품이 흔들리고 크기가 변하던 것) |
| 다시 렌더 판단 | 메시 · 설정 · `scene.py` · `materials_ext.py`가 바뀌면 옛 턴테이블 프레임을 지우고 다시 만든다 |

- 미리보기 결과(시안 A 덩어리 메시, 960×540 · 48 샘플 · 턴테이블 24프레임 480×270): 종료 0. 재질 37/37(+확장 10) · 빠짐 0 · 컷 6/6 · 단면 안 잘린 객체 0 · 처리 못 한 객체 0(숨김 4 · 통째로 둠 1) · MP4 h264 24프레임. 현재 외함 기본 시험도 종료 0.
- 사람 확인 필요(통과로 판정하지 않음):
  - 투과 15 %만으로는 기판 비침이 0이 아니다. 정면 컷 원본에서 아래쪽 부품 · 실크가 희미하게 보이고 밝기 3배 그림에서는 뚜렷하다. 유리 안쪽 검정 인쇄 마스크(O-126 mechanical)가 들어와야 없어진다.
  - 덩어리 시안의 `A_WALL_BRACKET`은 곧게 내려간 기둥 + 판이라 벽에 붙이면 광축이 벽과 나란했다. 상세 설계(§9)에서 뒤쪽 벽판 + 팔 + 팬 · 틸트로 바뀌어 풀렸다.
  - 4K 히어로 3장(`design/{A,B,C}_hero.png`)은 커밋 `f027228` 설정으로 만든 것이다. 지금 스크립트로 다시 만들면 유리 띠와 렌즈 밝기가 조금 다르다.

## 9. 시안 A 상세 설계 메시 — 최종 렌더 (O-126)

- 입력: main 체크아웃 `validation/runtime/vd001/case/A/`의 부품 STL 22개(mechanical 상세 설계, 조건 5 통과 뒤 sha256 불변을 orch가 확인) + 보드 GLB 2 + 내부 부품 8(렌즈 4 · 센서 · 받침 · 코어 · FPC). 같은 폴더의 통짜 STEP과 `stale/`은 쓰지 않는다.
- 명령: `python -I -B mechanical/ren003b/run.py --design A --full --glass-t 0.15 --final --case <case/A 폴더>` → 종료 코드 0.
- 출력(커밋 안 함): `validation/runtime/vd001/render/blender-b/design/A_final/` — `stills/`(4K 원본) · `web/`(1600px) · `turntable/` · `turntable.mp4` · `pcb_check/` · `report.json`.
- 대표본(커밋, 1600px): `docs/renders/final/blender-{product,front,rear,exploded,section,inuse}.png` · `blender-turntable.mp4` · `blender-turntable-poster.jpg`. `--no-docs`를 주면 쓰지 않는다.

| 판정 항목 | 값 | verifiable | 판정 |
|---|---|---|---|
| 메시 준비 종료 코드 | 0 | 예 | 통과 |
| 보드 GLB 수 | 2 | 예 | 통과 |
| 외함 · 부품 메시 수 | 30 | 예 | 통과 |
| 시안 부품 STL 수 (삼각화는 내보낸 쪽 설정) | 30개 · 삼각형 1961348 | 예 | 통과 |
| HDRI 받음 · sha256 이 assets.json 과 같음 | studio_small_09_2k.hdr | 예 | 통과 |
| Blender 종료 코드 (--python-exit-code 1) | 0 | 예 | 통과 |
| 재질 정의 수 = materials.py MATS | 37 / 37 (+확장 11) | 예 | 통과 |
| 재질 빠짐 (규칙에 없는 이름 · 못 가른 색) | 0 | 예 | 통과 |
| 엔진 · 장치 · 디노이저 | CYCLES · OPTIX · OPTIX | 예 | 통과 |
| 샘플 수 | 256 | 예 | 통과 |
| HDRI 가 장면에 쓰임 (sha256 일치) | studio_small_09_2k.hdr | 예 | 통과 |
| 색 관리 · 렌즈 · 조리개 | AgX · [85, 90, 100] mm · f/8.0 | 예 | 통과 |
| 베벨 넣은 부품 수 (0.3 mm) | 9 | 예 | 통과 |
| 컷마다 틀 반지름 mm (유한 · 1 m 미만) | {'hero': 75.9, 'front': 61.6, 'rear': 75.9, 'exploded': 164.1, 'section': 60.5, 'inuse': 96.1} | 예 | 통과 |
| 컷 수 | 6 / 6 ['hero', 'front', 'rear', 'exploded', 'section', 'inuse'] | 예 | 통과 |
| 컷 해상도 | [[3840, 2160]] | 예 | 통과 |
| 단면 컷에서 잘린 객체 수 | 185 | 예 | 통과 |
| 단면 컷: 자른 쪽에 남은 객체 수 (통째로 빠진 부품 63 · 단면이 열린 채 남은 작은 부품 22) | 0 | 예 | 통과 |
| 축소본 수 (긴 변 ≤ 1600) | 6 | 예 | 통과 |
| 유리 너머 기판 비침 0 (확인 그림: 원본 \| 밝기 3배) | ['validation/runtime/vd001/render/blender-b/design/A_final/pcb_check/hero_x3.jpg', 'validation/runtime/vd001/render/blender-b/design/A_final/pcb_check/front_… | 아니오 | 사람 확인 전 |
| 턴테이블 프레임 수 | 200 / 200 | 예 | 통과 |
| 턴테이블 프레임 해상도 · 빈 파일 없음 | [[1920, 1080]] | 예 | 통과 |
| 프레임이 서로 다름 (돌고 있음) | 200 | 예 | 통과 |
| 격리 ffmpeg 찾음 | True | 예 | 통과 |
| ffmpeg 종료 코드 | 0 | 예 | 통과 |
| MP4 프레임 수 · 길이 · 해상도 · 코덱 | 200 · 8.0 s · 1920x1080 · h264 | 예 | 통과 |
| MP4 길이 8~10 s · 1080p | 8.0 s · 1080p | 예 | 통과 |
| 사실감 · 보기 품질 (재질 · 조명 · 구도) | 사람 확인 필요 — 컷 6장 · MP4 | 아니오 | 사람 확인 전 |

새 부품 재질(이름 규칙 `materials_ext.EXT_NAME_RULES`, 값은 보기용 가정):

| 부품 | 재질 |
|---|---|
| `SHELL_PLASTIC` · `SHELL_ALU` | 차콜 무광 플라스틱 · 스페이스 그레이 알루미늄(헤어라인 + 모서리 다이아컷) |
| `FRONT_GLASS_IR` | 스모크 유리(투과 15 %). 투명 창 부품이 따로 있어 재질 안의 투명 원은 끈다 |
| `LENS_WIN_CLEAR` · `ALS_WIN_CLEAR` | 투명 창(`win_clear`) — 앞유리와 같은 방식(직진 투과 + 앞면 프레넬, 코팅 반사색). `pmma`는 뒷면 반사까지 합쳐 창만 뿌옇게 떴다 |
| `GLASS_MASK` · `INNER_MASK_PLATE` | 무광 검정(`foam`) |
| `GASKET_SPLIT` · `CABLE_GROMMET` | 고무(`rubber`) |
| `INSERT_M25_1..4` · `INSERT_1_4_20` | 황동(`brass`) |
| `COVER_USBC` · `COVER_MICROSD` | 흑색 플라스틱(`petg`) |
| `WALL_BRACKET_ARM/PAN/TILT` · `WALL_BRACKET_PIN/SCREW` | 흑색 분체 도장(`bracket`) · 강(`steel`) |
| `LIGHT_PIPE` | 청록 발광(`lightpipe_on`) |

- 분해도 이동량(제품 좌표 mm): 투명 창 +112 · 앞유리 +95 · 유리 마스크 +80 · 플라스틱 쉘 +60 · M2.5 인서트 +44 · 안쪽 마스크 판 +30 · 가스킷 −22 · 알루미늄 쉘 −75 · 1/4" 인서트 (y −16, z +60) · 그로밋 (y −16, z −75) · USB-C 덮개 (x −18, z −75) · microSD 덮개 (y +16, z −75) · 광 파이프 (y +18, z −75). 브래킷은 사용 장면에서만 보인다.
- 사람 확인 필요(통과로 판정하지 않음): 사실감 · 구도, 유리 너머 기판 비침 0(`pcb_check/{hero,front}_x3.jpg`), 턴테이블 움직임.
- 렌즈(내부 적층의 `LENS_CIL093` 메시 그대로): 경통은 무광 검정(`lens` → `barrel_black`), 앞알은 속이 어두운 유리 + 박막 코팅 반사(`glass` → `lens_coating`, 평평한 원판에 반지름 9 mm 볼록 노멀). 재질 표의 값(금속 경통 · 투명 유리)에 덧입힌 보기용 설정이다.
- 단면 컷에서는 베벨을 끈다. 잘린 큰 쉘 메시에 베벨이 걸리면 꼭짓점이 터져(범위 1e25) 배경에 검은 판이 뻗었다.
- 렌더 전용 보조(제품에 없는 것): 유리 하이라이트 띠(재질 안 계산), 무한 배경 · 벽. 렌즈에만 비추는 면광은 투명 창 부품이 따로 있는 상세 설계에서는 쓰지 않는다.
- 대표본 PNG는 4K 원본을 바로 1600px로 줄인 것이다(JPEG을 거치지 않음).
