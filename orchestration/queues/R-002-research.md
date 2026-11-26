[orch t18r → research] 배정 R-002 · 광학 일체 실장 조사 (lead t18q 지시, 사용자 추가 요구 2026-11-26) — R-001 끝낸 뒤 착수
■ 규칙: R-001과 같음 — AGENTS.md 전체 · README.md 「단계와 판정」 2(조사/BOM)·7(기구) · orchestration/roles/research.md. 조사만 — 설계·회로·PCB·기구 착수, 구매, 견적요청·주문, 외부 업로드, 계정 가입 금지. 미정값(FOV·초점 방식·마운트·IR 파장·조사 거리·주야 판별 방식)은 확정하지 말고 선택지·장단점·근거 URL·확인일로 정리해 질문으로 올릴 것.
■ 입력(읽기 전용, lead 소유 · 수정 금지): C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-144135-5470/docs/planning/product-brief.md (커밋 c6ba2bc 「광학 일체 실장」·「미정 · 광학 세부」), 같은 레인 docs/decisions/D-001-soc.md. R-001 결과(지원 센서 목록)를 전제로 쓴다.
■ 업무:
 1) SG2002 지원 센서와 조합 가능한 M12 등 소형 렌즈·렌즈홀더 — 마운트 치수, 고정 구멍, PCB 풋프린트 도면 공개 여부, 센서 광학 포맷·이미지 서클 적합
 2) IR-cut 필터 모듈(ICR) 종류, 구동 방식(코일 극성 반전 전압·전류·펄스폭), 홀더 일체형 여부
 3) IR LED 850nm/940nm 후보, 센서 NIR 감도(QE)와의 궁합, 구동 전류·방열·방사각
 4) 주야 판별 방식(조도센서/포토다이오드 · 영상 기반 ISP 통계) 선택지와 SDK 지원 여부
 5) 기구 관점 주의점(렌즈–IR LED 광차단, 창 반사·플레어, 광축 정렬·공차)과 위 부품들의 소량(1/5/10) 조달성
■ 소유 파일: docs/research/optics-ir.md (항목마다 출처 URL·리비전·확인일, 확인됨/미확인), 필요하면 docs/research/optics-candidates.csv (bom-template.csv 형식). 그 외 수정 금지.
■ 레인: R-001 레인과 분리 — node harness/cli.js start "R-002 광학·IR 조사" 로 새 레인. 병합(accept) 금지.
■ 완료 조건: 1~5 각각 출처 URL+확인일, 확인됨/미확인, 선택지·장단점 표, lead에 올릴 질문 목록, 레인 id·커밋 해시. 끝나거나 막히면 hc send t18r 로 보고(lead 직접 금지). 하위 에이전트 병렬 조사 허용, 새 hc 칸 금지.
