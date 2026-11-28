[orch t18r → schematic] 배정 C-012 · IR 스트링 B 실장 (orch 분기 O-69, D-003 #17 lead 갱신 ae14432) — main(eb0da0f 이후 최신)에서 새 레인
■ 변경 목록 = research R-016 문서 3절(레인 t-20261127-021842-688a 커밋 2463aad, docs/research/r016-ir-string-b.md):
 - hardware/schematic/tools/boards.py 215줄 ('B', True) → ('B', False), 210줄 블록 제목 「(B 스트링 DNP)」·214줄 주석 문구.
 - 생성기 재실행 → front.kicad_sch 8개 심벌 U5·R14·D_IR_B1·D_IR_B2·L2·D2·C16·C17의 (dnp yes) → (dnp no). 다른 DNP(전면 C6·Q4·R11·R16, 캐리어 C15·C16·R13–R17)는 그대로.
 - 계약 hw-fw-contract.md v1.10 → v1.11: 99·122·125행 문구(스트링 B 실장, 12V 합계 ≈1.84A·어댑터 여유 약 12%, bring-up 실측 판정 평균 ≤1.9A — D-003 #10).
■ 판정: front ERC kicad-cli sch erc --severity-all --exit-code-violations 종료 0, 넷리스트 83728da 대비 넷·연결 차이 0(바뀐 것은 8개 DNP 속성만 — 비교 결과 기록), carrier 변경 없음. inputs/front-kicad-bom.csv 다시 내보내 manufacturing/bom/make_pcbway_bom.py 종료 0(R-016의 예상 출력과 cmp 같음).
■ pcb 연동: 커밋 sha를 orch에 알리면 orch가 pcb에 "그 커밋의 front.kicad_sch·boards.py를 pcb 레인에 반영하고 보드 풋프린트 DNP 속성 맞춤(schematic-parity 0)"을 전달. pcb 레인 파일은 건드리지 않음.
■ 완료: 커밋 → hc send t18r. 
