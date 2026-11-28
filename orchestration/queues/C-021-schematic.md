[orch t18r → schematic] 배정 C-021 · IR LED 끔 구간 블리더 (SIM-001e firmware 레인 t-20261127-061121-2cf0 8591271, orch 분기 O-99) — main 최신 새 레인
■ 변경(firmware 변경 표 그대로): 전면 새 저항 10kΩ 1% 0402 두 개 — IRA_SET–IRA_K, IRB_SET–IRB_K(LED 스트링 양단). 근거: 끈 뒤 L 47µH–접합 용량 2.84MHz 공진으로 LED 순방향 꼬리(평균 0.84mA/스트링) — 블리더로 끔 구간 1.4µA, 효율 −0.081%p·LED 전류 −0.1% 이내(같은 모델, 후보 8종 중 유일 통과). FW 변경 없음.
■ 계약 v1.17(IR 절 블리더·근거, SIM-001b S3 '발광 아님' 정정 문구), ERC 0, contract_check 0·selftest 0, netcompare 의도 차이만. 커밋 sha → hc send t18r(orch가 pcb·BOM·SIM 재실행 배정) → 셸 루트.
