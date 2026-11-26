[orch t18r → schematic] SIM-001a 전류 순서 표 + C-018 묶음 (lead 대조 요청, orch 분기 O-91) — SIM-001a 레인 44b5 / 회로도는 b9cd에서
■ ① SIM-001a에 표 하나(기준 먼저 커밋): 12V 입력 전체 vs eFuse 뒤 12V_IR을 나눠서 —
 - 정상 최악: 12V 입력 합계(계약 전력 표 ≈1.84A, 벅 입력 포함) / 12V_IR만(SIM-001b′ B2: 평균 1.425A, 20µs 창 피크 1.585A)
 - eFuse 제한: TPS26600 ILIM 식(데이터시트 식·쪽, R6 값) → R6 6.98k 계산값·최소/최대(허용 오차)
 - 어댑터 보호: GST40A12 OLP 3.51~5.01A
 - 판정 조건(lead): 12V_IR 정상 최악(피크 기준) × 1.15 ≤ eFuse 제한 최소, 그리고 (eFuse 제한 최대 + 벅 입력 최악) < 어댑터 OLP 최소. orch 계산: 1.585 × 1.15 ≈ 1.82A > 1.72A → 지금 R6 6.98k는 불합격 예상.
■ ② C-018(회로도, 표 판정 뒤 한 커밋): R6 다시 계산(위 조건 만족하는 E96 값 — 예: 데이터시트 식으로 ≥1.82A 최소값이 되는 값), S5 전면 R17 10k → 4.7k·C19 10n → 4.7n(SIM-001b′ 55480c0 같은 모델 검증: 꺼짐 47µs·돌입 0.242A), U2 TPS26600 풋프린트를 ThermalVias 없는 HTSSOP-16-1EP 변형으로(pcb가 배선 때 Ø0.3 열 비아 넣음 — O-86 #21), .net 파일 두 보드 kicad-cli로 다시 내보내기(f0745ed .net이 C-016/017 이전 상태로 남았음 — pcb 발견). 계약 v1.14(R6·어댑터 GST40A12-P1J·S5 값).
■ 판정: SIM-001a 표 통과, ERC 0, contract_check 0·selftest 0, netcompare 의도 차이만. 커밋 sha → hc send t18r(orch가 pcb·firmware 재시뮬·research BOM 배정).
