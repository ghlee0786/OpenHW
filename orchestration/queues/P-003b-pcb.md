[orch t18r → pcb] P-003 추가 · Freerouting 설치 허가 (사용자 지시 2026-11-27, lead 전달, orch 분기 O-51) — 지금 돌고 있는 캐리어 배선은 멈추지 말 것
■ 허가: Freerouting(GPL-3.0) + Java 21 설치. 도입 여부·시점은 pcb 판단 — 스크립트 배선이 저속까지 잘 끝나면 그대로 써도 됨. 결과만 보고.
■ 도입 시 조건:
 1) 사용자 홈 아래 격리 설치(예: C:/Users/gh/tools/freerouting, 포터블 JDK 21 압축본). 시스템 PATH·JAVA_HOME·기존 Java 변경 금지, 실행은 전체 경로로.
 2) 공식 배포처(freerouting GitHub releases, Adoptium Temurin)에서만 받고, 버전·다운로드 URL·sha256을 docs(pcb 레인)에 기록 → orch가 원장에 옮김. 내려받은 파일은 빈 폴더에 따로 둔다(압축 해제도 그 폴더 안에).
 3) 대상은 저속 신호만. 이미 끝난 고속 차동(CSI·MDI·USB)·전원·IR 열 패드 구간은 고정(fixed)으로 둔 뒤 DSN 내보내기. 결과 SES를 가져온 뒤 kicad-cli DRC(--schematic-parity)·차동 규칙 재검사 종료 코드로 판정. V-005 독립 검토 통과 전에는 완료로 보지 않음. 자동 배선 결과가 최적이라고 쓰지 않음.
 4) DSN 내보내기·SES 가져오기는 pcbnew Python(헤드리스)으로 — KiCad GUI는 열지 않음(G-001 단일 작성자 원칙). 다른 프로젝트·컨테이너·WSL 배포판 건드리지 않음.
 5) 실행은 O-48처럼 hc 칸에서 일반 프로그램으로(메모리 압박 강제 종료 방지), 무거우면 node harness/cli.js slot --.
■ 완료 조건(P-003 원래 조건에 더해): 사용했으면 설치 기록(버전·URL·sha256·경로)과 고정 구간 목록 커밋.
