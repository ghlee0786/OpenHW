[orch t18r → firmware] 배정 F-007 · bring-up 호스트 쪽 도구 (lead 2026-11-27) — 먼저: 셸이 ed35(F-006) 레인 안이면 저장소 루트로 cd, ed35 미커밋 0 확인 → hc send t18r "ed35 해제"(lead가 batch accept — worktree 지워짐). 그 다음 main(533d1b8 이후)에서 새 레인.
■ 도구(PC 쪽, firmware/tools/host/): ① RTSP 수신·녹화·FPS/지연 측정(ffprobe/ffmpeg 또는 OpenCV — 있는 것 우선, 설치 필요하면 목록만) ② MQTT 이벤트 기록기(openhw/v1/event 구독 → JSONL, 등장/퇴장 짝·쿨다운 위반 검사) ③ FPS·추론 시간 집계(persond 로그·invoke count에서 — F-005 절차서 4절 양식) ④ 12V 전류 기록 CSV 집계(평균·피크·30분 창, 판정 ≤1.9A).
■ 시험: 하드웨어 없이 — 가짜 RTSP 소스(ffmpeg testsrc → 로컬 RTSP 서버가 컨테이너에 있으면) 또는 녹화 파일, 로컬 mosquitto + mosquitto_pub 가짜 이벤트, 가짜 로그/CSV로 각 도구 종료 코드·판정 시험(고장 주입 포함). 네트워크는 로컬만(127.0.0.1).
■ 절차서 해당 절에 도구 사용법 연결. 완료: 커밋 → hc send t18r.
