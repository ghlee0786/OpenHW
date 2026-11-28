[orch t18r → schematic] 배정 C-019 · SIM-001a fail 2 수정 (orch 분기 O-93) — 회로도 b9cd, SIM 44b5
■ P1 SIM-B1 5V_SYS 최악 5.298V > 5.25V: R3 13.5k(E192)는 0.5% 부품이 필요해 채택 안 함 → 1% E96·LCSC 재고 있는 값만으로 R2/R3 조합을 골라 VFB ±2.5%·R ±1% 최악이 4.75~5.25V 안이고 중앙에 가장 가까운 것(차선으로 제시된 R2 97.6k는 최저 4.760V — 코어 모듈 VIN 하한 근거를 계약/데이터시트에서 확인해 여유 기록). 
■ P2 SIM-C3 CAM_EN 켤 때 CORE_3V3 강하 0.230V > 0.166V: 전면 Q1 게이트 직렬 1k + Q1·Q2 게이트–드레인 4.7nF(밀러, C-017/018과 같은 방식) 채택.
■ SIM-001a B1·C3을 같은 기준(결과 전 커밋된 기준 그대로)으로 재실행 → 종료 0 목표. 끄는 순서는 firmware 재시뮬(SIM-L)이 확인.
■ 계약 v1.15, ERC 0, contract_check 0·selftest 0, netcompare 의도 차이만. ID 규칙(O-92): schematic은 SIM-A/B/C/D 그대로, firmware가 SIM-L로 바꿈 — 겹치는 파일 없게.
■ 커밋 sha → hc send t18r(orch가 pcb·research BOM·firmware 재시뮬 배정).
