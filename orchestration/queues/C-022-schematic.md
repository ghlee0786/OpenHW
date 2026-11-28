[orch t18r → schematic] 배정 C-022 · openhw 라이브러리 2건 (mechanical M-009 레인 t-20261127-080335-344a f7fd41e, mechanical/m008/f5f6-drc.md — orch 분기 O-101) — main 최신 새 레인
■ ① 전면 J2 풋프린트 → openhw:CLA216_ICR_SolderPads_1x02_P2.54mm (헤더 몸체 없는 2패드, courtyard = 패드+0.25). 파일은 mechanical/m008/CLA216_ICR_SolderPads_1x02_P2.54mm.kicad_mod를 git show로 가져와 hardware/libraries/openhw.pretty/에 추가, boards.py 169행 J2 풋프린트 변경. 핀 번호·넷(ICR_A 1번 사각/ICR_B)·BOM/CPL 제외 그대로.
■ ② openhw CLA216 홀더 풋프린트(MH1)의 F.CrtYd를 문서의 16점 외형으로(뒷면 BTB 고정 핀 NPTH 두 곳 노치, 구멍까지 0.100) — 판정 근거: HCTL 보스 돌출 최대 0.80 < 판 1.6, 홀더가 앉아도 간섭 0. 패드·구멍·다른 그림 변경 없음.
■ 판정: ERC 0, contract_check 0·selftest 0, netcompare 의도 차이만(J2 풋프린트 이름), .net 재생성, kicad-cli fp upgrade/검사 종료 0. 커밋 sha → hc send t18r(orch가 pcb에 라이브러리·회로도 반영 지시) → 셸 루트.
