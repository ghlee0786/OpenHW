[orch t18r → schematic] 배정 C-014 · VD-001 조건 1 — 계약↔회로도 기계 대조 (main 0c2ec91 이후 새 레인)
■ 스크립트(hardware/schematic/tools/contract_check.py): hw-fw-contract.md 최신판(v1.11)의 핀·넷 표(코어 J1/J2 핀 배정, GPIO·PWM·I2C·전원 레일, 하니스 결선 J7-n↔J4-(7−n), DNP 목록)를 읽어 두 보드 kicad-cli 넷리스트와 한 줄씩 대조 — 불일치 수 = 종료 코드. 고장 주입(표 한 줄 바꾼 사본) 시험 포함.
■ 함께: 두 보드 ERC --exit-code-violations 0, netcompare(C-013 656b50a 기준) 0을 같은 실행 스크립트에서. 결과 표를 docs(VD-001 조건 1)로.
■ 계약 문구와 회로도가 다르면 고치지 말고 목록 보고(어느 쪽이 맞는지 orch 판단). 완료: 커밋 → hc send t18r → 셸 루트.
