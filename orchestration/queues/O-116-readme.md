# O-116 공개 README (사용자 지시 2026-11-27, D-003 #61)

사용자 원문: "우리 git은 공개로 가고 Readme는 최대한 잘 꾸미고 모션그래픽, 인포그래픽을 활용해서 Readme를 최대한 공유할 수 있는 형식으로 제공한다."

## 결정된 것 (묻지 말 것)
- 저장소 ghlee0786/OpenHW 를 그대로 공개로 전환한다 — 전환은 lead 가 README 병합·민감 정보 재점검 뒤에 한다(칸은 전환하지 않음).
- 루트 LICENSE = Apache-2.0 (main 1898e1f 에 이미 있음). 제3자 자료는 각 폴더 라이선스 유지.
- 언어: 한국어 본문 + 맨 위 짧은 English summary(공유용).

## 담당·병렬
- research(t18s): README 본문 + 인포그래픽 SVG (새 레인, main 기준). 파일: README.md, docs/readme/**.
- mechanical(t18x): 회전 GIF·정지 렌더만 (새 레인). 파일: docs/readme/media/**. Fusion·Blender 쓰지 않음 — kicad-cli pcb render 만.
  - 전면 보드(main d1fa9e2 hardware/schematic/front/front.kicad_pcb): --rotate 로 0~360° 36~48장 → ffmpeg(C:/Users/gh/tools 의 격리 ffmpeg) GIF, 폭 ≤ 720px, 5MB 이하, 무한 반복. 앞·뒤 정지 PNG 각 1장(≤ 600KB).
  - 캐리어·3층 적층 GIF 는 캐리어 DRC 0 뒤 같은 방식으로 추가(자리만 비워 둠).
- 두 레인은 파일이 겹치지 않게: research 는 media/ 를 쓰지 않고 경로만 참조.

## README 구성 (research)
1. 히어로: 제목·한 줄 설명·배지(shields.io 정적: License Apache-2.0, KiCad 10, Status 가상 설계 진행, SoC SG2002) + 회전 GIF.
2. English summary (5~8줄).
3. 무엇인가: SG2002(reCamera Core 2002) 기반 엣지 AI 카메라 PoC — 우리 설계 PCB 2장(전면·캐리어) + 구매 코어 모듈, 광학·IR 통합.
4. 인포그래픽(움직이는 SVG, docs/readme/*.svg):
   - stack.svg: 3층 적층(전면–코어–캐리어) 분해→결합 애니메이션, 보드 사이 커넥터·광축 표시.
   - block.svg: 시스템 블록도(12V 입력→전원→코어, CSI 센서, IR LED·IR-cut, 이더넷·USB·SD) 신호 흐름 점선 애니메이션.
   - pipeline.svg: 설계 흐름(요구→회로도→시뮬→PCB→DRC→3D→케이스→렌더) 단계별 진행 상태(완료·진행 중·대기) — 현재 상태 반영.
   - numbers.svg: 핵심 수치 카드(ERC 0, 시뮬레이션 25/25 통과, 전면 DRC 0·미연결 0, 3D 모델 빠짐 0 등 — 저장소의 실제 결과 파일 값만, 출처 경로 주석).
   - 각 SVG: 스크립트 없음(SMIL <animate>/CSS @keyframes 만), 외부 폰트·이미지 없음(system-ui), prefers-color-scheme 로 밝은·어두운 테마, prefers-reduced-motion 이면 멈춤, viewBox 고정·폭 100%, 파일당 ≤ 60KB. README 에서는 <img src> 로 넣음(GitHub 는 <img> SVG 의 SMIL/CSS 애니메이션을 재생함).
5. 사양 표(보드별 주요 부품·크기·층수) — 저장소 문서의 값만.
6. 진행 현황(체크리스트, 날짜 2026-11-27 기준).
7. 저장소 지도(폴더별 한 줄) + KiCad 로 여는 법(kicad 10, 프로젝트 경로).
8. 검증 방법(ERC/DRC/시뮬레이션 명령과 결과 파일 위치).
9. 결정 기록 링크(docs/decisions/D-003-working-defaults.md).
10. 라이선스·제3자 고지(hardware/datasheets/INDEX.md 근거).
- Mermaid 는 보조로만(GitHub 렌더 확인된 문법만).

## 하지 말 것
- 제조사 이름·견적·주문·비용 언급, 내부 운영 도구(herdr·hc·orch·칸·Pilot·다른 프로젝트 이름·로컬 경로 C:\Users\...) 언급.
- 확인 안 된 수치·주장. 모든 수치는 저장소 결과 파일에서 읽어 출처 경로를 README 주석이나 표 각주로.
- 사람·회사 이름, 이메일.

## 함께 할 일 (research)
- 추적 파일에서 다른 프로젝트·내부 환경 이름 점검: `git grep -n -iE "gop|opennvr|gis-test|ironwall|sensorway"` → 문서 서술은 일반 표현으로 바꿈(예: firmware/docs/build-baseline.md 의 gop-ha-b → "다른 WSL 배포판"). 코드 동작이 바뀌는 곳은 건드리지 말고 목록만 보고.

## 완료 조건 (기계 증거)
- 모든 SVG: xml 파싱 0 오류, <script> 0, 외부 href 0, 크기 ≤ 60KB, 밝은·어두운 테마 미디어쿼리 존재.
- GIF ≤ 5MB, PNG ≤ 600KB.
- README 의 모든 상대 링크·이미지 경로가 실제 파일로 해결(스크립트로 검사).
- `gh api -X POST /markdown -f mode=gfm -f context=ghlee0786/OpenHW -f text=@README.md` 로 렌더 HTML 생성해 오류 없음 + 그 HTML 과 SVG·GIF 를 브라우저로 열어 스크린샷(사람 확인 항목 — verifiable 아니오, 화면 모음 HTML 한 장).
- 레인 미커밋 0, 끝나면 lead 에 batch 요청.
