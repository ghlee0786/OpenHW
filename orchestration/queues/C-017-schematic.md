[orch t18r → schematic] 배정 C-017 · SIM-001b 수정 반영 (firmware 레인 t-20261127-041440-3ed1 a3b988c, hardware/sim/SIM-001b-results.md — orch 분기 O-87) — C-014 레인 b9cd에서 이어서(SIM-001a 잠시 멈춤 — 작음)
■ S1 B5 CAM_1V8 돌입 5.11A(기준 ≤0.3A) → 전면 Q7 드레인–Q6 게이트 직렬 1kΩ + Q6 게이트–드레인 10nF (같은 모델로 돌입 0.133A·켜짐 36µs 검증됨).
■ S2 B2/B3 12V_IR eFuse 20µs 창 1.585A > ILIM 1.49A(평균 1.425A = ILIM의 96%) → 캐리어 TPS26600 ILIM 저항 R6 8.06k → 6.98k(E96, ≈1.72A) — 계약 전력 표·D-003 #… 문구 갱신.
■ S4 B6 꺼진 CAM_1V8에서 SDA 0.42V(기준 ≤0.3V) → 전면 CAM_1V8–GND 10kΩ 블리더(켬 때 180µA) 추가.
■ S3(끔 구간 링잉 6mA)은 회로 변경 없음 — 기준 그대로 불합격으로 남기고 근거(역방향 변위 전류, 평균 41µA, 발광 아님)와 bring-up 확인 항목으로(O-87).
■ 계약 v1.13: 위 변경 + FW 규칙 'IIC2 내부 풀업 켜지 않음'(켜면 꺼진 센서로 11.8µA 역급전).
■ 판정: ERC 0, netcompare 의도 차이만(목록), contract_check 0·selftest 0. 커밋 sha → hc send t18r(orch가 pcb·research BOM·firmware 재시뮬 배정) → SIM-001a 재개.
