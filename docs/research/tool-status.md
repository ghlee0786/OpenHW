# 도구 상태 (2026-11-26)
- Find MCP: https://catalog.agentage.io/mcp initialize / tools/list / mcp_search(kicad) 실제 성공. 읽기 전용 검색.
- KiCad: winget 10.0.8 설치 성공. C:/Users/gh/AppData/Local/Programs/KiCad/10.0.
- KiCad MCP: iQreu/kicad-mcp 별도 venv 설치, initialize/tools/list 55개 및 kicad_status 성공. CLI 10.0.8 확인. PCB Editor가 열리지 않아 GUI IPC false. GUI 읽기/편집, ERC/DRC/출력 실검증은 미수행. 회로도 실험 편집 비활성.
- Fusion: 공식 내장 MCP http://127.0.0.1:27182/mcp initialize / initialized / tools/list 성공. 앱 실행 중에만 연결. 형상 생성/간섭 검증 미수행. 앱 제목에 4일 후 만료 안내 표시됨. 계정/라이선스는 사용자 확인 필요.
- 펌웨어: 타깃 MCU 결정 후 SDK/툴체인 선정. 제품 설계/거버/기능 시험은 아직 없음.
## 증거
C:/Users/gh/.claude/orchestration/openhw-20261126/finder-search-kicad.json
C:/Users/gh/.claude/orchestration/openhw-20261126/fusion-tools.json
C:/Users/gh/.local/share/openhw-tools/kicad-mcp/smoke-result.json
## 출처
https://www.kicad.org/download/windows/
https://docs.kicad.org/10.0/en/cli/cli.html
https://github.com/iQreu/kicad-mcp
https://github.com/agentage/find-mcp
https://github.com/Autodesk/ai-integrations/tree/main/fusion/local-mcp-server
