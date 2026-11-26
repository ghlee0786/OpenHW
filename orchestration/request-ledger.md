# OpenHW
환경 구성 완료. 제품 방향 결정(D-001, 2026-11-26).

## 배정 · 진척
| id | 요청자 | 담당 | 업무 | 소유 파일 | 완료 조건 | 상태 |
|---|---|---|---|---|---|---|
| R-001 | lead t18q (사용자 결정 2026-11-26) | research t18s | D-001 「확인 필요」 1~5 조사: SG2002 소량 조달·PCBWay 공급, 데이터시트·설계 가이드·참고 보드 공개 범위, SDK·tpu-mlir, 지원 센서·IQ 파일, V851s 비교 | docs/research/soc-sg2002.md, (선택) docs/research/soc-candidates.csv | 항목별 출처 URL+확인일, 확인됨/미확인 구분, SG2002 조달 결론(불가 시 대안), 사용자 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | completed — 레인 t-20261126-144331-462e 커밋 bbf3930(미병합). 결론: SG2002 소량 조달 불확실 → 사용자 결정 A~D·질문 7개를 lead 보고(2026-11-26) |
| R-002 | lead t18q (사용자 추가 요구 2026-11-26, brief c6ba2bc) | research t18s | 광학 일체 실장 조사: M12 렌즈·홀더 치수/풋프린트, ICR 구동, IR LED 850/940nm·센서 QE 궁합, 주야 판별 방식, 기구 주의점·소량 조달 | docs/research/optics-ir.md, (선택) docs/research/optics-candidates.csv | 항목별 출처 URL+확인일, 확인됨/미확인, 선택지·장단점, lead 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | completed — 레인 t-20261126-150127-43df 커밋 214754d(미병합). 1안 O1~O9, 남은 미확인 ①~⑤ |
| R-003 | lead t18q (사용자 결정 D-002 경로 C, 2026-11-26 · 우선순위 최상) | research t18s | SG2002 모듈 구매처 확인: LicheeRV Nano 코어 등 후보, 1/5/10 구매처·단가·재고·EOL, 실장 방식·PCBWay 조립, 핀맵·풋프린트·STEP·라이선스·MIPI/이더넷/USB/전원 인출, SDK·센서 지원 | docs/research/module-sg2002.md, (선택) docs/research/module-candidates.csv | 구매 가능 모듈 1개 이상 확정 또는 불가+대안, 질문 목록, 레인 id·커밋 → orch 회수 → lead 보고 | completed — 레인 t-20261126-152145-fce6 커밋 c958a25(미병합). 권고 reCamera Core 2002 8GB (101991223) |
| R-004 | lead t18q (2026-11-26) | research t18s (예정) | PCBWay 턴키 견적 확인용 짧은 BOM: 확정 모듈 1종 + 캐리어 핵심 부품 대표 후보(카메라 커넥터·이더넷 잭/마그네틱·전원 입력 IC·IR-cut 구동 IC·IR LED 드라이버) | (제안) docs/research/bom-quote-draft.csv | bom-template.csv 열, 제조사·MPN·패키지·수량(1/5/10)·출처 URL·확인일, 레인 id·커밋 | running (2026-11-26 모듈 확정 후 배정 · 접수 확인. BTB 원품번·GC2053 조달 포함, 이어서 R-005) |
| R-005 | orch (D-003 #14) | research t18s | 공개 라이선스 자료만 hardware/datasheets 보관 + INDEX.md | hardware/datasheets/** | URL·리비전·sha256·라이선스·확인일 | queued (R-004 뒤, 배정문은 R-004-research.md 끝) |
| C-001 | orch (단계 3) | schematic t18z | HW/FW 계약 초안: 전원 트리·예산, B2B 사용 핀, I2C·GPIO, 부트·디버그·보호, FPC 핀배치 | hardware/schematic/hw-fw-contract.md | 표 완성·근거/미확인·분기 기록, 레인·커밋 | completed — 레인 t-20261126-155208-d030 커밋 ac12920. 3층 구조 C1(캐리어–코어–전면 센서 보드), J1 윗면 센서/J2 아랫면 |
| F-001 | orch (단계 3) | firmware t18w | reCamera SDK 사실: 빌드 호스트·부트·DT/핀먹스·센서 IQ·I2C/GPIO·ICR·조도·EPHY·SD·tpu-mlir | firmware/docs/sdk-facts.md | 표·핀 요약 절, 레인·커밋 | completed — 레인 t-20261126-155208-b6b4 커밋 e23e9ec. GC2053 IQ 있음, IR-cut·주야 전환 구현 없음, LTR-329 드라이버 없음 |
| P-001 | orch (단계 5 준비) | pcb t190 | PCBWay 공정 규칙·스택업·임피던스, 0.5mm 커넥터 조립 조건 → KiCad 규칙 제안 | hardware/pcb/fab-rules-pcbway.md | 규칙표 출처·확인일, 스택업 안, 레인·커밋 | running (2026-11-26 접수 확인) |
| V-001 | orch | review t191 | R-002·R-003 핵심 6주장 독립 재확인 | validation/review-V001-R002-R003.md | 판정표·영향, 레인·커밋 | completed — 레인 t-20261126-155240-aa11 커밋 2a7bf47. ①②③ 일치(보완 있음) ④ 불일치(CIL327 HFOV 약 121°) ⑤⑥ 조건부 |
| C-001b | orch | schematic t18z | 계약의 FW 확인 대기 열을 sdk-facts와 대조·확정 → 계약 v1 | hardware/schematic/hw-fw-contract.md (C-001 레인) | FW 대기 0 또는 사유, 커밋 | running (L-001보다 먼저) |
| L-001 | orch (단계 4 준비) | schematic t18z | KiCad 라이브러리: AP1511B·AL8860·VSMA1085600·LTR-329·M12/ICR 홀더·FPC 10P (BTB·벅·RJ45·SD·센서는 의존 대기) | hardware/libraries/** | 핀↔패드 대조표, kicad-cli 결과, 레인·커밋 | queued (C-001b 뒤) |
| F-002 | orch | firmware t18w | reCamera-OS 0.2.4 원본 Docker 기준 빌드(slot 경유, 산출물은 저장소 밖) | firmware/docs/build-baseline.md, firmware/scripts/** | 종료 코드 0+해시 또는 실패 원인 판정, 레인·커밋 | running |
| R-006 | orch (V-001 ④⑥ 분기 복귀, O-8) | research t18s | 렌즈 재선정(GC2053 HFOV 85~95°, 왜곡 모델·BFL·IR 보정) + IR LED 조사각·개수(1.0A, 직렬 ≤2) | docs/research/optics-ir-r006.md (+csv) | 렌즈 1안·차선 계산 근거, LED 결론, 레인·커밋 | queued (R-004 뒤, R-005보다 먼저) |
| M-001 | orch | mechanical t18x | 공개 STEP 측정 → 3층 적층·광축·IR LED·창·체결 기준안 (외함 아님) | mechanical/** | 측정표·기준안·Fusion MCP 결과, 레인·커밋 | completed — 레인 t-20261126-161155-50dc 커밋 ad23d15. Fusion MCP read·execute 성공, J1 윗면/J2 아랫면 독립 확인, 적층안 z·M1.6 나사·IR 후보 영역, 분기 K1~K8 |

## 운영 변경 (2026-11-26, 사용자 지시 · lead 전달)
- 의견 묻지 않고 진행: 사람 쪽 미정값은 D-003(lead 레인 t-20261126-144135-5470 docs/decisions/D-003-working-defaults.md, 커밋 8ac5ce5) 값으로 확정 취급. 새 갈림길은 기본값 선택 → 아래 「분기 기록」에 분기점·선택·이유·차선책 → lead 요약 보고. 문제 시 해당 행으로 돌아가 차선책.
- R-003 결과가 D-003 #15를 만족하면 orch가 모듈 확정 → lead 통지 없이 R-004 시작. 없으면 #15 차선책 순서.
- 그 뒤 README 단계 3(HW/FW 계약)부터 회로·PCB·펌웨어·기구 의존 순서로 진행 허가. 역할 지침의 「설계 시작 금지」 문구는 이 지시로 해제됨(배정문에 명시).
- 계속 금지: 구매·제조 주문·견적 요청/업로드·외부 연락·계정 가입·main 병합/push. CAD 단일 작성자·Pilot 레인 유지. 공개 라이선스 데이터시트는 hardware/datasheets 보관 배정 가능(D-003 #14).

## 분기 기록 (orch)
| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| O-1 | R-003 우선순위 요청 시 진행 중 R-002 처리 | R-002 하위 에이전트는 계속, 본체가 R-003 먼저 | 끊으면 19분치 조사 손실 | R-002 중단(interrupt) |
| O-2 | 모듈 확정 (D-003 #15) | Seeed reCamera Core 2002 8GB 무선 없음 SKU 101991223 | #15 ①② 충족, ③ 풋프린트 충족·코어 STEP 없음(부분). 후보 중 유일하게 CSI·MDI가 커넥터로 캐리어에 나옴. STEP은 케이스 STEP+회로도 외형으로 대체(R-003 M4) | LicheeRV Nano-E + GC4653 → Duo 256M + CAM-GC2083 (R-003 M1) |
| O-3 | 센서 (D-003 #5 GC2083 문제: reCamera SDK IQ 없음, 칩 단품 판매처 없음) | GC2053 잠정 | 모듈 공급사 SDK에 IQ 있음 + Seeed S401 센서 보드 KiCad 공개 → 이식 위험 최소. R-004에서 조달 확인 | GC4653(D-003 #5 차선, IQ 이식 필요) → CAM-GC2083 기성 모듈 |
| O-4 | 참고 설계 라이선스 (B301/S401 CC BY-SA 4.0) | 참고만 하고 캐리어·센서 보드 독자 설계 | ShareAlike 전파 회피, 나중에 수용으로 바꾸기 쉬움 | 파생 수용 후 CC BY-SA 4.0 표기 |
| O-5 | 단계 3 착수 순서 | schematic 계약 초안(C-001) + firmware SDK 사실(F-001) 병렬, KiCad 회로도는 계약 뒤(C-002) | 같은 파일 동시 편집 없이 병렬화, 계약이 회로의 입력 | 순차(FW 사실 먼저) |
| O-6 | 기다리는 동안 병렬 일 | pcb는 PCBWay 공정 규칙(P-001), review는 R-002/R-003 독립 검증(V-001), mechanical 대기 | 의존 없는 일만 병렬, 결정 근거 조기 검증 | 전부 순차 |
| O-7 | 모듈 5개 확보 위험 (D-003 #12·#15, lead 2026-11-26 지시: 판단 기준만 기록) | reCamera Core 2002 유지. R-004에서 공개 정보로 확인: Seeed 수량 표시·Digi-Key·Mouser·공식 대리점 재고 합 | 판단 기준 — (a) 공식 판매처 공개 재고 합 ≥5 또는 Seeed 「In Stock」+수량 제한 없음 표시 → 유지 (b) 합 <5이고 2002w/64GB 변형(101991224·102991898·102991899) 포함 합 ≥5 → 변형 혼용 허용(핀 호환·SDK 동일 근거 확인 조건) (c) 그래도 <5 또는 단종/EOL 표시 → D-003 #15 차선 LicheeRV Nano-E로 복귀 검토 후 lead 보고. 구매·판매자 문의 금지 유지 | LicheeRV Nano-E + GC4653 |
| O-8 | V-001에서 주장 뒤집힘 처리 (lead 지시) | 뒤집힌 주장에 걸린 분기 행(O-2·O-3·D-003 #17 등)으로 복귀해 차선 적용 여부 판정 → lead 보고 | 결정 근거 무결성 | — |
| O-9 | 조도센서 읽기 수단 (F-001: LTR-329 커널 드라이버 5.10에 없음) | LTR-329를 전면 보드 CAM I2C2에 두고 사용자 공간 i2c-dev 폴링 | 커널 백포트 불필요, 주소 0x29 vs GC2053 0x3f 충돌 없음(C-001b에서 레벨·주소 근거 확인) | LIGHT_SENSE(J1-18 ADC1) 포토트랜지스터 |
| O-10 | C-001 3층 구조로 R-002 O1(센서 B2B→캐리어→센서 보드 경로) 무효 | C-001 C1 채택: 캐리어(뒤)–코어–전면 센서 보드, ICR·IR PWM·조도는 J1 신호로 전면 보드 처리, 캐리어→전면은 12V_IR FPC 10P | J1·J2가 코어 윗면·아랫면에 나뉘어 캐리어 한 장으로 둘 다 받을 수 없음(STEP 배치 확인) | — (물리 제약) · D-003 #17 「별도 센서 보드+FPC」 문구 갱신을 lead에 제안 |
| O-11 | 계약 확정 전 병렬 | schematic: C-001b 먼저 → L-001 / firmware: F-002 기준 빌드 / mechanical: M-001 기준 형상 | 각자 다른 파일·의존 없는 일 | 순차 |
| O-12 | 짝 BTB 풋프린트 출처 (V-001 ③: B301/S401 파일은 Apache-2.0, CC BY-SA는 코어 회로도 PDF만) | B301 KiCad 풋프린트에서 파생 허용 + Apache-2.0 고지·출처 기록, SUNGTECH 데이터시트 나오면 치수 대조 | ShareAlike 위험 낮음, 회로·PCB 착수를 막는 항목 해소 | 데이터시트로 독자 작성 |
| O-13 | 렌즈 (V-001 ④ CIL327 F-θ로 HFOV 약 121° > D-003 #4 90°) | R-002 O2 무효 → R-006에서 재선정, 기구는 렌즈 길이 변수로 진행 | 결정 근거 뒤집힘(O-8) | — |
| O-14 | ICR·IR LED 구동 (V-001 ⑤⑥) | ICR 드라이버 VDD 5V+펄스, AP1511B vs DRV8837 정격 근거 있는 쪽 / IR LED 1.0A·직렬 ≤2·방열 기판 | 3.3V에서 코일 전압 하한, 1.5A 여유 0 | AP1511B 3.3V 유지 불가 → DRV8837 |
