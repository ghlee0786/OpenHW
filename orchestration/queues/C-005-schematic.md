[orch t18r → schematic] 배정 C-005 · R-009·V-004b 결과 반영 (V-004b 회수 뒤 한 번에 배정 — 대기열)
■ 입력: R-009 C:/workspace_python/OpenHW/.harness-worktrees/t-20261126-171912-e7d2/docs/research/r009-bom-risks.md (커밋 898ed80) ⑨·②
■ orch 분기 O-34 (CLA216 리드 짝 커넥터): 1안 Molex PicoBlade 53261-0271 (도면 실측·CLA214 사진 근거, LCSC C177225 재고 10,160) — 전면 J2 풋프린트를 GH에서 PicoBlade 2P 직각 SMD로 교체(공식 KiCad 라이브러리 우선). 차선 JST GH SM02B-GHS-TB. G2(실물 홀더)에서 하우징 길이(≈4.0 PicoBlade / ≈5.75+레버 GH) 확인 전 PCB 확정 금지. 극성: 빨강=+이면 필터 열림 → ICR_A/ICR_B 핀 배정 주석.
■ 업무: 1) 전면 J2 → PicoBlade 2) 전면 Q4 ALS-PT19(DNP) 새 풋프린트(0.8×0.8 @ ±0.75, 핀1 콜렉터, Everlight 도면 근거) 3) 캐리어 J2 DC 잭 풋프린트를 R-009 XKB 도면 A1 2025-04-22(핀2 5.90·슬롯 1.0×3.5·몸체 14.0, 앞면 −13.6)와 C-004 결과 대조해 다르면 맞춤 4) V-004b 미해소 항목.
■ 조건: 참조 지정자 유지, netcompare 의도 차이, ERC 0, pcb용 변경 부품표, 표제란 Rev C-005.
■ 추가(pcb P-003 f0edd7d 요청): 라이브러리 실크 위반 수정 — 캐리어 J2 XKB DC 잭 실크가 외곽·패드에 걸림 9건, 전면 DF30·SRN6045 실크가 패드 위 10건 → 실크를 패드·외곽 밖으로(공식 풋프린트는 덮어쓰지 말고 openhw 파생). 고친 뒤 시험판 pcb drc silk 위반 0 확인.
■ V-004b (review 레인 t-20261126-180645-0fa1 커밋 6404bf7 validation/review-V004b-C004.md, 읽기 전용) 미해소·신규 — 원문 수정안대로:
 - [N1 중요] Q6 DMG2305UX 게이트가 CORE_3V3 풀업 CAM_PG(R4)를 공유 → 코어 1V8이 3V3보다 먼저 오르는 구간에 Q6이 켜져 IOVDD 꺼진 채 I2C 풀업·X1 켜짐 → Q6 게이트를 100k로 CORE_1V8 풀업 + 새 DMG1012T(G=CAM_EN)로 구동(S401 패턴)
 - R2: X1 OE를 CAM_1V8로(또는 직렬 1k) — 기본값 고르고 근거
 - R5: SMBJ5.0A(VRWM 5.0 < 출력 5.08~5.30V) → SMBJ6.0A
 - R8: R11 풀업이 게이트에 남아 VGS −2.24V(AO3401A 보증 −2.5V 밖) → R11 핀2를 SD_PWR_GD로(B101 패턴)
 - R10: 'SS24-E3/61T'는 없는 품번 → Vishay SSA24-M3/61T(SMA)
 - R11: USB_DET 필터 C 권고 반영 여부 분기 기록
 - R12: F1 0437003.WR은 Fast-Acting → Bel 0685T3000-01(Slow Blow 1206 3A 63V)
 - R6 경미: DC 잭 실크 4·courtyard
 - 계약 v1.5: 324행 'Low/Hi-Z=켬' → R12 풀업 뒤 'Hi-Z=끔', '≤25% 끔 비율' → 'IR_PWM Low(켬) 비율 ≤25%'
 - README 10절 DNP 목록에 C10(실장으로 바뀜)·R16 반영
■ 완료 조건: 최종 커밋, netcompare 의도 차이, ERC 두 보드 0, pcb용 변경 부품표, 계약 v1.5 커밋 → hc send t18r. 표제란 Rev C-005.
