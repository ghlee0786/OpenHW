[orch t18r → research] 배정 R-025 · KiCad MCP 교체 설치 (사용자 지시, lead D-003 #52 — 중복 기록 말 것) — 설치는 사용자 홈 격리, 저장소 변경은 main 최신 새 레인
■ 대상: mixelpixx/KiCAD-MCP-Server(MIT, KiCad 9/10, IPC 실시간 백엔드 + SWIG 폴백). Konnect 제외(상업 라이선스).
■ 설치: git clone --branch stable https://github.com/mixelpixx/KiCAD-MCP-Server.git C:/Users/gh/tools/kicad-mcp-server → 커밋 해시 기록 → npm install·npm run build(종료 코드) → Python 의존성은 격리 venv(또는 KiCad 10 번들 python에 꼭 필요한 것만 — 무엇을 넣었는지 기록) → setup-windows.ps1은 먼저 읽고 PATH·전역 설정 변경 줄은 빼고 실행(뺀 줄 기록). 설치 파일 출처·버전·해시는 docs/research/r025-kicad-mcp-server.md.
■ 등록: claude mcp add --scope local 로 main 경로(C:/workspace_python/OpenHW)와 pcb worktree(C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-171922-251f) 두 곳만, 이름 kicad, KICAD_PYTHON·PYTHONPATH 등 env, claude mcp list로 Connected 확인(출력 기록).
■ ★ pcb 칸은 --strict-mcp-config --mcp-config orchestration/roles/pcb.mcp.json으로 떠 있어 claude mcp add 등록을 읽지 않음 → 새 서버 항목을 담은 설정 파일을 하나 더 만듦: orchestration/roles/pcb-kicad2.mcp.json(이름 kicad, 같은 command/args/env — 기존 iQreu 항목은 그 파일에 넣지 않음, 기존 pcb.mcp.json은 그대로 남김). 이 파일은 새 레인에서 커밋 → lead batch.
■ 시험: 그 설정으로 짧은 claude 실행 없이 서버 자체를 stdio로 1회 기동해 tool 목록이 나오는지(종료 코드·도구 수) — KiCad GUI는 열지 않음(pcb가 단일 작성자).
■ 완료: 커밋 → hc send t18r(orch가 pcb 체크포인트에서 같은 sessionId로 칸 재시작) → 셸 루트. 결제·유료 금지, 다른 프로젝트 설정 건드리지 않음.
