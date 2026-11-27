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
| `carrier_spin.gif` · `carrier_top.png` · `carrier_bottom.png` | 캐리어 | — | — | — | **자리만**: 캐리어 DRC 0 뒤 `--board carrier`로 같은 방식 |
| `stack_spin.gif` | 3층 적층(전면–코어–캐리어) | — | — | — | **자리만**: 캐리어 DRC 0 뒤 |

- 보기(색·잘림·겹침)는 사람이 확인한다.
