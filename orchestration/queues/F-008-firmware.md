[orch t18r → firmware] 배정 F-008 · bring-up PC 도구 설치 (사용자 허가 2026-11-27, lead 전달, orch 분기 O-79) — main 0c2ec91 이후에서 새 레인
■ 설치 대상(O-79): ffmpeg/ffprobe만. OpenSSH 클라이언트는 Windows 내장(C:\Windows\System32\OpenSSH\ssh.exe) 있음 → 설치 안 함. mosquitto-clients는 장치 1883이 루프백 전용(D-003 #30)이라 PC 직접 구독을 안 쓰고 event_log record --stdin(ssh 파이프)로 충분 → 설치 안 함(필요해지면 다시 결정).
■ 조건: 사용자 홈 아래 격리(예: C:/Users/gh/tools/ffmpeg/<버전>/), PATH·시스템 설정 변경 없음 — 도구는 전체 경로 또는 rtsp_check.py의 ffprobe 경로 인자/환경 변수로(도구에 그런 인자가 없으면 최소 추가). 배포처는 ffmpeg.org 다운로드 페이지가 링크하는 Windows 빌드(gyan.dev 또는 BtbN GitHub releases)만, 공개 2주 넘은 릴리스. 버전·URL·sha256(배포처 공개값 대조)을 firmware/docs(도구 13절)에 기록. 받은 파일은 빈 폴더에.
■ 시험: Windows 호스트에서 그 ffprobe로 F-007 rtsp_check probe(파일 입력)·record 스모크 종료 0 + 컨테이너 test_host_tools.sh 재실행 종료 0.
■ 추가(R-019 결과 오면 orch가 전달): F-005/F-006 절차서에 G1·G2 문서 게이트로 남는 위험의 첫 PCBA bring-up 확인 항목.
■ 완료: 커밋 → hc send t18r → 셸 루트(O-73).
