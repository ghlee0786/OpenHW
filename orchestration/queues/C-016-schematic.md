[orch t18r → schematic] 배정 C-016 · 코어 J2-32에서 ALS 인터럽트 분리 (lead 기본값 2026-11-27, orch 분기 O-83) — C-015와 같은 레인에서 C-015 직후, SIM-001a 전
■ 사실(M-006 ba58c08): 코어 J2-32 = Seeed B301에서 PWR_WAKEUP1(깨우기 입력), 우리는 ALS_INT_RSV(GH J7-4 경유 전면 ALS)로 연결. D-003 #18 ALS는 i2c-dev 폴링이라 인터럽트 불필요.
■ 변경: 캐리어 J2-32를 ALS_INT_RSV에서 떼어 미연결(no-connect 표시) — Seeed 보드의 J2-32 처리(풀업 등)를 research R-019가 알려 오면 그대로 맞춤(orch가 전달, 지금은 미연결). ALS_INT_RSV 넷은 GH 하니스 핀(J7-4/J4-3)과 전면 쪽만 남김(전면 LTR-329에 INT 핀이 없으면 전면 쪽도 미연결 — research 확인 결과 반영). 생성기(boards.py)로 바꾸고 UUID 유지 방식(C-012/C-013처럼).
■ 계약 v1.12(C-015)에 함께: 4절 용도·핀표에서 J2-32 = 미사용(이유 O-83), ALS_INT_RSV 설명.
■ 판정: ERC 두 보드 0, netcompare는 의도한 차이만(넷 1개 연결 변화 — 목록), contract_check 종료 0. 완료: 커밋 sha를 hc send t18r(orch가 pcb에 반영 지시) → SIM-001a.
