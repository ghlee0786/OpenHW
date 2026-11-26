# OpenHW
환경 구성 완료. 제품 방향 결정(D-001, 2026-11-26).

## 배정 · 진척
| id | 요청자 | 담당 | 업무 | 소유 파일 | 완료 조건 | 상태 |
|---|---|---|---|---|---|---|
| R-001 | lead t18q (사용자 결정 2026-11-26) | research t18s | D-001 「확인 필요」 1~5 조사: SG2002 소량 조달·PCBWay 공급, 데이터시트·설계 가이드·참고 보드 공개 범위, SDK·tpu-mlir, 지원 센서·IQ 파일, V851s 비교 | docs/research/soc-sg2002.md, (선택) docs/research/soc-candidates.csv | 항목별 출처 URL+확인일, 확인됨/미확인 구분, SG2002 조달 결론(불가 시 대안), 사용자 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | completed — 레인 t-20261126-144331-462e 커밋 bbf3930(미병합). 결론: SG2002 소량 조달 불확실 → 사용자 결정 A~D·질문 7개를 lead 보고(2026-11-26) |
| R-002 | lead t18q (사용자 추가 요구 2026-11-26, brief c6ba2bc) | research t18s | 광학 일체 실장 조사: M12 렌즈·홀더 치수/풋프린트, ICR 구동, IR LED 850/940nm·센서 QE 궁합, 주야 판별 방식, 기구 주의점·소량 조달 | docs/research/optics-ir.md, (선택) docs/research/optics-candidates.csv | 항목별 출처 URL+확인일, 확인됨/미확인, 선택지·장단점, lead 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | running (R-001 회수 직후 2026-11-26 배정 · 접수 확인. 배정문 orchestration/queues/R-002-research.md) |
| R-003 | lead t18q (사용자 결정 D-002 경로 C, 2026-11-26 · 우선순위 최상) | research t18s | SG2002 모듈 구매처 확인: LicheeRV Nano 코어 등 후보, 1/5/10 구매처·단가·재고·EOL, 실장 방식·PCBWay 조립, 핀맵·풋프린트·STEP·라이선스·MIPI/이더넷/USB/전원 인출, SDK·센서 지원 | docs/research/module-sg2002.md, (선택) docs/research/module-candidates.csv | 구매 가능 모듈 1개 이상 확정 또는 불가+대안, 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | running (2026-11-26 배정 · 접수 확인. R-002 하위 에이전트는 계속, 본체는 R-003 먼저. 배정문 orchestration/queues/R-003-research.md. D-003 #15 판정·권고 1종 요구 추가) |
| R-004 | lead t18q (2026-11-26) | research t18s (예정) | PCBWay 턴키 견적 확인용 짧은 BOM: 확정 모듈 1종 + 캐리어 핵심 부품 대표 후보(카메라 커넥터·이더넷 잭/마그네틱·전원 입력 IC·IR-cut 구동 IC·IR LED 드라이버) | (제안) docs/research/bom-quote-draft.csv | bom-template.csv 열, 제조사·MPN·패키지·수량(1/5/10)·출처 URL·확인일, 레인 id·커밋 | reserved (R-003이 D-003 #15 만족 모듈을 내면 orch가 확정 후 즉시 시작. 배정문 orchestration/queues/R-004-research.md) |

## 운영 변경 (2026-11-26, 사용자 지시 · lead 전달)
- 의견 묻지 않고 진행: 사람 쪽 미정값은 D-003(lead 레인 t-20261126-144135-5470 docs/decisions/D-003-working-defaults.md, 커밋 8ac5ce5) 값으로 확정 취급. 새 갈림길은 기본값 선택 → 아래 「분기 기록」에 분기점·선택·이유·차선책 → lead 요약 보고. 문제 시 해당 행으로 돌아가 차선책.
- R-003 결과가 D-003 #15를 만족하면 orch가 모듈 확정 → lead 통지 없이 R-004 시작. 없으면 #15 차선책 순서.
- 그 뒤 README 단계 3(HW/FW 계약)부터 회로·PCB·펌웨어·기구 의존 순서로 진행 허가. 역할 지침의 「설계 시작 금지」 문구는 이 지시로 해제됨(배정문에 명시).
- 계속 금지: 구매·제조 주문·견적 요청/업로드·외부 연락·계정 가입·main 병합/push. CAD 단일 작성자·Pilot 레인 유지. 공개 라이선스 데이터시트는 hardware/datasheets 보관 배정 가능(D-003 #14).

## 분기 기록 (orch)
| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| O-1 | R-003 우선순위 요청 시 진행 중 R-002 처리 | R-002 하위 에이전트는 계속, 본체가 R-003 먼저 | 끊으면 19분치 조사 손실 | R-002 중단(interrupt) |
