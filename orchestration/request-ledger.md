# OpenHW
환경 구성 완료. 제품 방향 결정(D-001, 2026-11-26).

## 배정 · 진척
| id | 요청자 | 담당 | 업무 | 소유 파일 | 완료 조건 | 상태 |
|---|---|---|---|---|---|---|
| R-001 | lead t18q (사용자 결정 2026-11-26) | research t18s | D-001 「확인 필요」 1~5 조사: SG2002 소량 조달·PCBWay 공급, 데이터시트·설계 가이드·참고 보드 공개 범위, SDK·tpu-mlir, 지원 센서·IQ 파일, V851s 비교 | docs/research/soc-sg2002.md, (선택) docs/research/soc-candidates.csv | 항목별 출처 URL+확인일, 확인됨/미확인 구분, SG2002 조달 결론(불가 시 대안), 사용자 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | running (2026-11-26 배정 · 접수 확인) |
| R-002 | lead t18q (사용자 추가 요구 2026-11-26, brief c6ba2bc) | research t18s | 광학 일체 실장 조사: M12 렌즈·홀더 치수/풋프린트, ICR 구동, IR LED 850/940nm·센서 QE 궁합, 주야 판별 방식, 기구 주의점·소량 조달 | docs/research/optics-ir.md, (선택) docs/research/optics-candidates.csv | 항목별 출처 URL+확인일, 확인됨/미확인, 선택지·장단점, lead 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | queued (R-001 완료 후 배정 — 진행 중 턴 방해 금지 지시. 배정문 orchestration/queues/R-002-research.md) |
