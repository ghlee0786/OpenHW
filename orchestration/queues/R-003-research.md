[orch t18r → research] 배정 R-003 · SG2002 모듈 구매처 확인 — 우선순위 최상(사용자 직접 요청, 다음 결정을 막는 항목). lead t18q 지시 2026-11-26.
■ R-002 처리: 중단하지 말 것. 이미 돌고 있는 R-002 하위 에이전트들은 그대로 두고(결과는 나중에 회수), 본체는 지금 R-003 을 먼저 진행해 R-003 보고를 먼저 보낸 뒤 R-002 를 마무리. R-002 에 쓴 내용이 있으면 R-002 레인 t-20261126-150127-43df 에 그대로 두거나 WIP 커밋. 참고: 사용자 결정 D-002 로 형태가 「SG2002 코어 모듈 + 자체 캐리어」로 바뀜 — R-002 광학(렌즈 홀더·ICR·IR LED)은 캐리어 보드 또는 별도 센서 보드 실장 기준으로 정리하고, 모듈 쪽 카메라 커넥터/MIPI 배선 제약은 R-003 결과와 연결.
■ 규칙: AGENTS.md 전체 · README.md 「단계와 판정」 2(조사/BOM) · orchestration/roles/research.md. 조사만 — 구매·장바구니·견적 요청·판매자 문의·계정 가입·로그인·외부 업로드 금지. 수치는 출처 URL+확인일, 확인됨/미확인 구분. 가격 검색만으로 호환 확정 금지. 미정값은 추정 확정 말고 질문으로.
■ 입력(읽기 전용, lead 소유 · 수정 금지): C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-144135-5470/docs/decisions/D-002-module-carrier.md (커밋 6e2c286), 같은 레인 D-001-soc.md · docs/planning/product-brief.md. 네 R-001 결과 docs/research/soc-sg2002.md (레인 t-20261126-144331-462e).
■ 업무:
 1) SG2002 모듈 후보 목록 — Sipeed LicheeRV Nano 코어보드(무선 유무 변형 포함) 우선, 그 밖의 SG2002/SG2000 모듈(Milk-V Duo 256M/Duo S 등 실장형으로 쓸 수 있는 것)
 2) 후보별 1/5/10개 구매처·단가·통화·재고·배송·납기·확인일, 공식 판매처와 재판매 구분, 단종/EOL 표시 여부
 3) 실장 방식(스탬프홀/LGA/보드간 커넥터/핀헤더)과 PCBWay 조립(턴키/위탁) 가능성
 4) 캐리어 설계 자료 공개 범위 — 핀맵·풋프린트·STEP·회로도·라이선스, MIPI CSI·이더넷(PHY 내장 여부)·USB·GPIO·전원 입력이 모듈 밖으로 나오는지
 5) 해당 모듈 공급사 SDK·카메라 센서 지원 연결(R-001 IQ 센서 목록과 대조)
■ 소유 파일: docs/research/module-sg2002.md (+선택 docs/research/module-candidates.csv, bom-template.csv 형식). 그 외 수정 금지.
■ 레인: 새 레인 node harness/cli.js start "R-003 SG2002 모듈 구매처" — R-001·R-002 레인과 분리. 병합(accept) 금지.
■ 완료 조건: 구매 가능한 모듈 1개 이상 확정(출처·확인일·재고 근거) 또는 불가 결론+대안, 사용자 질문 목록, 레인 id·커밋 해시. 끝나거나 막히면 hc send t18r (lead 직접 금지). 하위 에이전트 병렬 허용, 새 hc 칸 금지.
