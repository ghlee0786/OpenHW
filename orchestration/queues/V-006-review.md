[orch t18r → review] 배정 V-006 · VD-001 최종 감수 준비 + 보고 틀 (main 0c2ec91 이후 새 레인 — V-005 스크립트는 main에 있음)
■ 조건 2 준비: run_v005.sh에 추가 — ① 보드 .kicad_dru·.kicad_pro의 규칙 완화(기본값보다 느슨한 조건·영역 예외)·ignore를 전부 뽑아 D-003(main docs/decisions/D-003-working-defaults.md) 기록 항목(#28 비결합·#31 꼬임 등)과 대조 — 기록 없는 완화 = 불합격 ② parity 0 ③ O-74b 사본 판정(이미 있음).
■ 조건 3 검사: R-010 16항 체크리스트(docs/research/r010-pcbway-submission.md 「P-004 체크리스트」)를 자동 검사로 — Gerber 층 수·이름·외곽 닫힘(gerbv/파이썬 파서 등 있는 것), 드릴 PTH/NPTH, CPL 열·회전·면·부품 수 = BOM 실장 수, BOM 9열·DNP 일치, 조립도 PDF 존재·쪽 수. 종료 코드 = 실패 수. pcb 산출물 커밋 전에는 가짜 산출물로 고장 주입 시험.
■ 조건 6 틀: validation/runtime/vd001/index.html 생성기 — 항목(조건 1~5 하위 항목)·verifiable 예/아니오·결과·근거 링크(커밋·로그), PCB 3D 앞뒤·조립·단면·분해 렌더 자리, bring-up으로 넘기는 남은 위험 목록(원장 대기 목록에서). 입력은 각 칸 결과 파일/JSON — 형식을 문서로 정해 orch에 알림.
■ 완료: 커밋 → hc send t18r(포그라운드) → 셸 루트.
