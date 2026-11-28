[orch t18r → research] 배정 R-016 · IR 스트링 B 실장으로 BOM 갱신 (orch 분기 O-69) — main eb0da0f에서 새 레인
■ 배경: D-003 #17 "스트링 B DNP로 시작 — 개수는 실측으로 결정". M-003 2차(mechanical 4752a68 analysis2.md): A만이면 IR 직접광이 시야의 61%(화면 아래 −Y 약 39%는 0), A+B 86%. 바깥 핀 방열판 H3로 A+B 듀티 25%에서 안 공기 상승 약 21.5K(25°C)/21.1K(40°C) — 목표 ≤25K 안. 12V 합계 ≈1.84A(어댑터 2.08A, 여유 약 12%, 계약 v1.10 122~125행). → PoC 5대는 B 실장(실측으로 개수 결정할 수 있게).
■ 업무: 회로도(main의 hardware/schematic, 계약 v1.10)에서 스트링 B에 딸린 부품을 정확히 특정(D_IR_B1·B2 + B 드라이버 AL8860 쪽 L·C·D·R·센스 저항 등 — 지금 DNP 표시된 것 중 B 경로만. 다른 옵션 DNP(C15/C16, R13~R17, Q4 ALS-PT19 등)는 그대로). bom-full.csv·PCBWay BOM(make_pcbway_bom.py 재생성)·수량·가격·재고(공개 페이지, 확인일) 갱신, 바뀐 행 목록과 근거(회로도 넷 이름).
■ 주의: 회로도 파일 자체(DNP 속성)는 schematic 소관 — 바꿔야 할 심벌 목록만 문서로(orch가 schematic에 배정). 구매·견적·업로드·외부 연락 금지.
■ 완료: 커밋 → hc send t18r.
