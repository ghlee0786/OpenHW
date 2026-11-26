[orch t18r → mechanical] 배정 M-010 · 최종 케이스 경로 고정 (사용자 지시 2026-11-27, lead 전달, orch 분기 O-102) — main 1a9eb97 이후 새 레인
■ 경로(이것으로 고정): pcb 커밋 보드 → kicad-cli pcb export step(3D 모델 포함 — REN-002 apply_models 적용된 보드, --subst-models, --user-origin 코어 중심, 캐리어·전면 각각) → main 체크아웃 C:/workspace_python/OpenHW/validation/runtime/vd001/boards/ → Fusion(MCP)에서 M003 외함 문서에 가져오기 → 간섭·플러그 삽입(USB-C·RJ45·DC·microSD)·광축·LED 창 재판정(M-007 판정 J1~J6 그대로) → 필요하면 Fusion에서 케이스 수정(매개변수 표·params.py 같이) → Fusion에서 STEP/STL·f3d 내보내기 → Blender 최종 렌더(O-100 보관 규칙: main validation/runtime/vd001/render + 대표본 docs/renders 커밋).
■ 먼저: mechanical/m003/scripts/01_new_doc_import.py 등 Fusion 스크립트의 LANE 경로가 취소된 30c6 worktree를 가리킴 → main 체크아웃 기준 경로(또는 레인 경로를 인자로 받게)로 고침.
■ 사전 1회(지금): pcb 중간 커밋 보드(pcb 레인 t-20261126-171922-251f be3125d 전면·6df2865 캐리어 — git show로 사본, 3D 모델 연결은 apply_models로 사본에)로 위 경로를 끝까지 한 번 돌려 막힘 확인(종료 코드·판정 결과). pcb 최종 커밋 알림 오면 같은 명령으로 최종.
■ 완료: 커밋 → hc send t18r → 셸 루트.
