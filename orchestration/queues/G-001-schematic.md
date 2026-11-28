[orch t18r → schematic] 지시 G-001 · KiCad GUI로 보이게 작업 (사용자 요청 2026-11-26, lead 전달) — L-001부터 적용, C-001b는 지금 방식대로 마무리
■ 업무 방식: L-001(라이브러리)과 이후 회로도(C-002)는 이 PC 데스크톱에서 KiCad 10 GUI(C:/Users/gh/AppData/Local/Programs/KiCad/10.0)를 자기 레인 worktree 안의 프로젝트로 열어 진행. 사용자가 볼 수 있게 창을 띄워 둠. 창 조작·스크린샷은 desktop-automation 스킬(창 목록·포커스·스크린샷·UIA) 사용.
■ 단일 소유: KiCad GUI·활성 문서는 schematic 단독(pcb t190 은 그동안 KiCad GUI 금지 — orch가 알림). 활성 문서 경로가 자기 레인 worktree인지 창 제목으로 확인해 기록. 사람이 연 다른 KiCad 창이 있으면 손대지 말고 보고.
■ 편집 방식: GUI 직접 조작 또는 파일 편집 후 GUI 재로드 — 네 판단, 문서에 기록. 실험적 MCP 회로도 편집(KICAD_MCP_ENABLE_SCH_EDIT)은 계속 끔(README: 복사본 검증 전 금지).
■ 스크린샷: 단계마다(프로젝트 생성 · 심벌 추가 · 풋프린트 추가 · 회로 배치 · ERC) 창 스크린샷을 C:/workspace_python/OpenHW/validation/runtime/kicad-gui/<작업id>/<번호>-<단계>.png 에 저장(메인 체크아웃의 gitignore 폴더 — 레인 정리(gc) 뒤에도 남게, orch 분기 O-15). 저장소 커밋 대상 아님.
■ 판정: ERC·라이브러리 검사는 kicad-cli 종료 코드 기준(verifiable 예). 화면 스크린샷은 verifiable 아니오(사용자 확인용) — 보고에 두 열 구분.
■ 보고: KiCad 창이 처음 떴을 때 즉시 hc send t18r 「KiCad 창 뜸 · 창 제목 · 활성 프로젝트 경로 · 첫 스크린샷 경로」(orch가 lead에 전달). 이후 단계별 스크린샷 경로는 작업 완료 보고에 목록으로.
