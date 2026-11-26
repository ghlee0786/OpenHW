[orch t18r → schematic] 배정 C-020 · 카메라 레일 순서 S6 (SIM-001c ② firmware 레인 t-20261127-054721-bf55 43eb4f7, orch 분기 O-97) — main 최신에서 새 레인(b9cd는 batch 대상)
■ 문제: L9 끌 때 IOVDD가 AVDD보다 2.31ms 먼저 떨어짐(GC2053 §9.3 — IOVDD 마지막), L10 켤 때 AVDD−IOVDD 최악 1.0µs(§9.2 t1 ≥50µs). Q1·Q2가 같은 CAM_PG로 거의 동시에 동작.
■ 변경(S6, 같은 모델로 검증: 최악 4경우 켤 때 180µs·끌 때 1.1ms·돌입 310mA·CORE_3V3 3.269V): 전면 Q1 게이트 R20 1k → 100k ∥ (1k + BAT54, CAM_PG_IO→CAM_PG 방향), Q2 게이트 R5 → 100k ∥ BAT54(CAM_PG→CAM_PG_AV 방향). 방향·값은 firmware 결과 문서(hardware/sim/SIM-001b-results.md S6 절) 원문대로 — 극성은 그림과 넷으로 다시 확인.
■ 계약 v1.16(CAM 레일 순서 설명·근거 GC2053 §9.2/9.3), ERC 0, contract_check 0·selftest 0, netcompare 의도 차이만. 커밋 sha → hc send t18r(orch가 pcb·BOM·재시뮬 배정) → 셸 루트.
