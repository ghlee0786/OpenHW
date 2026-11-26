[orch t18r → schematic] 배정 C-005 · R-009·V-004b 결과 반영 (V-004b 회수 뒤 한 번에 배정 — 대기열)
■ 입력: R-009 C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-171912-e7d2/docs/research/r009-bom-risks.md (커밋 898ed80) ⑨·②
■ orch 분기 O-34 (CLA216 리드 짝 커넥터): 1안 Molex PicoBlade 53261-0271 (도면 실측·CLA214 사진 근거, LCSC C177225 재고 10,160) — 전면 J2 풋프린트를 GH에서 PicoBlade 2P 직각 SMD로 교체(공식 KiCad 라이브러리 우선). 차선 JST GH SM02B-GHS-TB. G2(실물 홀더)에서 하우징 길이(≈4.0 PicoBlade / ≈5.75+레버 GH) 확인 전 PCB 확정 금지. 극성: 빨강=+이면 필터 열림 → ICR_A/ICR_B 핀 배정 주석.
■ 업무: 1) 전면 J2 → PicoBlade 2) 전면 Q4 ALS-PT19(DNP) 새 풋프린트(0.8×0.8 @ ±0.75, 핀1 콜렉터, Everlight 도면 근거) 3) 캐리어 J2 DC 잭 풋프린트를 R-009 XKB 도면 A1 2025-04-22(핀2 5.90·슬롯 1.0×3.5·몸체 14.0, 앞면 −13.6)와 C-004 결과 대조해 다르면 맞춤 4) V-004b 미해소 항목.
■ 조건: 참조 지정자 유지, netcompare 의도 차이, ERC 0, pcb용 변경 부품표, 표제란 Rev C-005.
■ 추가(pcb P-003 f0edd7d 요청): 라이브러리 실크 위반 수정 — 캐리어 J2 XKB DC 잭 실크가 외곽·패드에 걸림 9건, 전면 DF30·SRN6045 실크가 패드 위 10건 → 실크를 패드·외곽 밖으로(공식 풋프린트는 덮어쓰지 말고 openhw 파생). 고친 뒤 시험판 pcb drc silk 위반 0 확인.
