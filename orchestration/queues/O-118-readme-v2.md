# O-118 README 2판 — 예쁘게, 사진 다양하게 (사용자 지시 2026-11-27)

사용자 원문: "Readme 에 예쁘게 꾸미고, 사진을 다양하게 넣고 https://github.com/ghlee0786/open-nvr-dev 이걸 참고하던지해"

## 참고 형식 (open-nvr-dev README, 사용자 본인 저장소 — 형식만 참고, 내용·이름 가져오지 않음)
- 맨 위 `<div align="center">`: 아이콘 SVG(96px) → 제목 → 한 줄 소개 → 배지 줄(shields, 로고 포함) → 넓은 히어로 SVG(width 880, 움직임, 의미 있는 alt).
- 섹션마다 `<p align="center"><img src="docs/readme/<주제>.svg" width="880" alt="…">` 그림 한 장 + 짧은 설명.
- 진행 상태 표, 주요 기능, 아키텍처 하위 절(그림별), 기술 스택 표, 저장소 구조, 사용법, 문서 목록, 라이선스.

## 지금 README(main 9b18a14) 보완점
- 아이콘·히어로 없음, 그림이 회전 GIF 1 + SVG 4뿐 → 사진을 다양하게.

## 넣을 그림 (모두 저장소 안 파일로 만들고, 만드는 스크립트도 커밋)
1. 아이콘 `docs/readme/icon.svg` (카메라+칩 모티프, 단색 2톤, 테마 대응).
2. 히어로 `docs/readme/hero.svg` (880 폭): 피사체 → 렌즈·센서(전면) → SG2002 코어(AI 추론) → 캐리어(이더넷·USB·SD) → 결과, 빛·신호가 흐르는 애니메이션.
3. 3D 갤러리 (2×2 또는 3열 표): docs/renders/p005 4장(앞·뒤·비스듬 2) + docs/readme/media/front_spin.gif. 각 사진 아래 한 줄 캡션.
4. PCB 층 그림: kicad-cli pcb export svg 로 전면 보드 F.Cu / In1 / In2 / B.Cu / 실크 각 1장(또는 한 장에 겹친 색 구분) → PNG 변환(폭 ≤ 900, ≤ 400KB). 어두운 배경에서도 보이게 배경 칠함.
5. 회로도 그림: kicad-cli sch export svg 로 전면·캐리어 회로도 첫 장 → 미리보기 PNG(클릭하면 원본 SVG).
6. 시뮬레이션 파형: hardware/sim/png 중 대표 3~4장(전원 기동·IR LED·센서 전원 순서 등) 갤러리 + 통과 수(15/15, 10/10 — 결과 파일 값).
7. 기구 초안: mechanical/m003/render 중 대표 2~3장 — "케이스 1차 초안(최종 아님)" 표시.
8. 캐리어 보드: 진행 중 — 자리만 두고 "배선 마무리 중" 표시(캐리어 DRC 0 뒤 회전 GIF·갤러리 추가는 REN-004 후속).
- 새 이미지는 docs/readme/gallery/** 에 두고, 원본을 복사할 때는 크기 줄인 사본만(원본 경로 링크).
- 사진마다 alt·캡션, 클릭 시 원본으로 링크.

## 규칙 (O-116 그대로)
- 스크립트 없는 SVG(CSS/SMIL), 외부 폰트·href 없음, 밝은·어두운 테마, reduced-motion 정지, SVG ≤ 60KB, PNG ≤ 600KB, GIF ≤ 5MB, README 전체 이미지 합 ≤ 15MB.
- 한국어 본문 + 맨 위 영문 요약 유지.
- 제조사·견적·비용, 내부 운영 도구(herdr·hc·orch·칸·Pilot·harness 운영 서술)·다른 프로젝트 이름·로컬 경로·사람·회사 이름·이메일 금지. open-nvr-dev 이름도 README에 쓰지 않음.
- 모든 수치는 저장소 결과 파일 값 + 각주.

## 담당
- research(t18s): README·SVG(icon·hero·섹션 그림)·갤러리 표.
- mechanical(t18x): 그림 4·5·7 내보내기 스크립트와 PNG(docs/readme/gallery/**) — research 파일과 안 겹치게. Fusion·Blender 안 씀.
- 끝나면 check_readme.py 확장(이미지 크기 한도·alt 누락 0)으로 종료 0, GFM 렌더 확인, 레인 미커밋 0 → lead batch.
