# README 그림 (회전 GIF · 정지 렌더)

`make_media.py`로 만든다. KiCad 3D 뷰어 렌더(`kicad-cli pcb render`)를 쓰고, GIF는 ffmpeg로 묶는다.

```
FFMPEG=<ffmpeg 경로> python -I -B docs/readme/media/make_media.py --board front --pcb <커밋>
```

- 보드 사본에 `mechanical/ren002/apply_models.py`로 3D 모델을 연결한 뒤 그린다.
- 3D 모델 빠짐은 0이어야 한다(`mechanical/ren002/audit_models.py`).
- 기준:
  - GIF: 폭 ≤ 720 px, ≤ 5 MB, 무한 반복.
  - PNG: ≤ 600 KB(팔레트 256색, 투명 배경).
  - 결과는 `media.json`에 적고, 종료 코드 = 불합격 수.

| 파일 | 보드 · 커밋 | 크기 | 해상도 | 프레임 | 렌더 |
|---|---|---|---|---|---|
| `front_spin.gif` | 전면 · d1fa9e2 | 2.42 MB | 720×540 | 40장 @ 12 fps, 무한 반복 | 기울임 −40°, Z 0~360° · high · 원근 · 바닥 그림자 |
| `front_top.png` | 전면 · d1fa9e2 | 53 KB | 915×915 | — | 윗면 정사영 |
| `front_bottom.png` | 전면 · d1fa9e2 | 77 KB | 915×915 | — | 아랫면 정사영 |
| `carrier_spin.gif` | 캐리어 · 995b872 | 2.83 MB | 720×540 | 40장 @ 12 fps, 무한 반복 | 기울임 −40°, Z 0~360° · sha256 `4ce6f414200f…` |
| `carrier_top.png` · `carrier_bottom.png` | 캐리어 · 995b872 | 74 / 54 KB | 686×916 | — | 윗면 · 아랫면 정사영 · sha256 `2753f7c5d933…` / `85628aa944ca…` |
| `docs/renders/carrier/carrier-{top,bottom,iso,iso-back}.png` | 캐리어 · 995b872 | 146 / 106 / 167 / 78 KB | 1568×1568 | — | 정지 렌더 4장 (투명, 팔레트 256) · sha256 `38aad4c562e1…` / `9b2bd0a08eca…` / `bdd48ea6f0bf…` / `00455b7d563c…` |
| `stack_spin.gif` | 3층 적층 · 캐리어·전면 995b872 | 1.57 MB | 720×540 | 40장 @ 12 fps, 무한 반복 | 전면 사본 MH1 에 캐리어 STEP·코어 외형 VRML 을 3D 모델로 붙여 kicad-cli 한 번에. 기울임 −62°, 회전 중심 −10 mm, zoom 0.45 · sha256 `8401de1fe126…` |

- `--renders <폴더>`: 정지 렌더 4장 `<보드>-top/-bottom/-iso/-iso-back.png`(1600 요청, 투명, 팔레트 256색, ≤ 600 KB, `docs/renders/p005`와 같은 짜임).
- 적층의 코어는 구매 모듈이라 단순 외형이다. 판 30×30, 부품 층 윗면 0.92·아랫면 1.26, 짝 BTB 플러그 4.0.
- 높이는 기구 적층 값 그대로다. 판 1.6, BTB 결합 8.0(`mechanical/m003/params.py`).
- 보기(색·잘림·겹침)는 사람이 확인한다.
