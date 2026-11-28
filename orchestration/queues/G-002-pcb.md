[orch t18r → pcb] 배정 G-002 · KiCad 실시간 GUI 작업 (사용자 요구, lead 결정 D-003 #33, orch 분기 O-59) — 같은 P-003 레인 t-20261126-171922-251f, P-004 목표 그대로
■ 상태: lead가 KiCad API 서버를 켬(kicad_common.json api.enable_server=true, 백업 .bak-20261127-lead), lead 사본 pcbnew 2창 종료 — 지금 KiCad 프로세스 0. GUI 단일 작성자 = pcb.
■ 순서(같은 파일 동시 쓰기 금지):
 1) 돌고 있는 스크립트 배선기/Freerouting이 있으면 단계 끝에서 저장·커밋 후 정지(hc 칸이면 그 칸 프로그램 종료 확인).
 2) 자기 레인 보드(.kicad_pcb)를 PCB 편집기로 연다(전면·캐리어 중 지금 고칠 보드 하나씩 — 한 번에 한 보드 파일만 GUI가 소유).
 3) kicad MCP(iQreu/kicad-mcp, kipy IPC)의 연결 상태 도구로 IPC 연결 true 확인. MCP 서버가 칸 시작 때 IPC 없음으로 굳어 있으면 그 사실·출력을 그대로 보고(칸 재시작은 lead 결정) — 그동안은 스크립트·kicad-cli로 계속.
 4) IPC로 배치·트랙·비아·존 재충전·실크 정리·저장. 호출 1회 = 되돌리기 1단계. 단계마다 스크린샷 → C:/workspace_python/OpenHW/validation/runtime/kicad-gui/G-002/<순번>-<내용>.png (사용자가 화면 갱신을 볼 수 있게).
 5) 판정은 저장된 파일에 대한 kicad-cli pcb drc --severity-all --schematic-parity 종료 코드 — GUI DRC 아님. 라우터·자동 배선은 스크립트/Freerouting(O-52b) — 그때는 GUI에서 저장·닫기 후 실행, 결과 파일을 GUI로 다시 연다(되돌리기 대신 파일 다시 읽기).
■ 주의(R-014): KiCad 10.0.x에서 풋프린트를 IPC로 고칠 때 3D 모델이 빠지는 보고 — 첫 수정 뒤 3D 모델 경로 유지 확인을 첫 시험 항목으로. 회로도 편집기는 IPC 없음(회로도는 건드리지 않음). 다른 프로젝트 창·컨테이너 건드리지 않음.
■ 완료 조건: P-004 조건 그대로 + G-002 스크린샷 목록·IPC 연결 확인 출력, 커밋 → hc send t18r.
