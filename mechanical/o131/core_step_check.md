# O-131 시안 A — 코어 STEP 실형상 간섭 재확인 (기록)

- 배정: orch t18r O-131 · 작성: mechanical t18x · 2026-11-28
- **결론: 무선 부품을 뺀 코어 실형상은 시안 A 케이스 바디와 간섭 0이다.**
  - 케이스 바디와의 최소 거리는 SHELL_ALU ↔ 코어 PCB 5.75 mm다.
  - 간섭은 BTB 짝 결합 2건뿐이다(의도된 결합). 케이스 파일은 바꾸지 않았다.

## 방법

| 항목 | 내용 |
|---|---|
| 조립 | `02_assembly.py --set CASE=A` 로 새 M007_assembly 문서를 만든다(pcb 995b872 보드 STEP, 시안 A f3d 22 바디) |
| 코어 | `Recamera Core 2002.step` (CC BY-SA 4.0, 읽기·측정만, 저장소에 넣지 않음). sha256 7de9f15f…8785 일치(확인) |
| 위치 | M-001 원점 O. STEP 좌표 PCB 중심 (60, −65) → (0, 0), PCB 아랫면 z 0 그대로 |
| 위치 검산 | PCB bbox x·y ±15, z 0…1.597. J1 플러그 중심 (0.0, 11.8) 윗면, J2 소켓 중심 (11.8, 0.0) 아랫면. stack-reference §2.1과 일치(확인) |
| 무선 부품 제외 | DZcc-U4(AP6212로 판단 — 12×12, 보드 위 1.5. §2.2의 1.58과 높이로 맞춤, **가정**) · U.FL-R-SMT-1 · ANT-SPRING. 숨김 3개 |
| 자리 표시 제외 | CORE_ENVELOPE_30x30 · CORE_BOT_KEEPIN · CORE_TOP_KEEPIN · J1/J2_MATED_ENVELOPE |
| 간섭 | Fusion `analyzeInterference`(맞닿는 면 제외). 대상: 코어 바디 208개 + 코어 상자 0.5 mm 안의 바디 16개 |
| 최소 거리 | `measureMinimumDistance`. 케이스 A 바디마다 측정하고, 코어 근처 바디는 참고로 측정 |
| 실행 | `python -I -B mechanical/fusion_run.py mechanical/o131/core_step_check.py` → `validation/runtime/vd001/o131/core_step_check.json` (main, 커밋 안 함) |

## 간섭 (코어 ↔ 그 밖)

간섭 결과는 5건이다. 그중 코어끼리이거나 코어 밖끼리인 3건은 판정 밖이다. 이름을 못 찾은 결과는 0건이다.

| 코어 바디 | 상대 | 부피 mm³ | 위치 (x, y, z mm) | 판정 |
|---|---|---|---|---|
| J1 SHANGQI 플러그 | 전면 보드 BTB_ST-BTB-058060-B | 39.35 | ±8.85, 9.8…13.8, 5.51…7.55 | BTB 짝 결합(플러그 혀가 소켓에 들어감) — 의도 |
| J2 SHANGQI 소켓 | 캐리어 BTB_ST-BTB-058060-A | 0.28 | 9.6…14.0, ±8.85, −4.05…−4.04 | BTB 짝 결합(두께 0.01 접촉) — 의도 |

- 짝 결합이 아닌 간섭은 **0 mm³** 이다.

## 최소 거리 — 시안 A 케이스 바디

| 케이스 바디 | 최소 mm | 가장 가까운 코어 바디 |
|---|---|---|
| SHELL_ALU | 5.750 | PCB |
| INNER_MASK_PLATE | 7.053 | J1 플러그 |
| LIGHT_PIPE | 7.481 | J2 소켓 |
| SHELL_PLASTIC | 10.285 | PCB |
| GASKET_SPLIT | 10.523 | PCB |
| COVER_USBC | 12.639 | PCB |
| INSERT_M25_1 / _3 | 16.869 | PCB |

## 참고 — 케이스 밖 근처 바디 (간섭 쌍 제외)

| 바디 | 최소 mm | 코어 바디 | 비고 |
|---|---|---|---|
| HW_STANDOFFS | 0.000 | PCB | 장착면 맞닿음(간섭 결과에 없음) |
| SPREADER_M003 | 0.403 | QFN88 SoC | M-003 열 경로 틈 |
| 캐리어 CP_Elec_63x54 | 2.644 | PCB | |
| 캐리어 JST_SM06B_GHS_TB | 2.883 | eMMC | |

## 미확인·주의

- **무선 부품 포함 시(2002w):** 같은 방법으로 처음 돌렸을 때(무선 숨김이 안 된 실행) ANT-SPRING이 여러 바디와 최소 거리 0.0이었다.
  - 상대: 캐리어 D_SMA · JST GH · C_0402, SPREADER_M003.
  - 그 실행은 간섭 이름 대조에 결함이 있어 부피는 재지 못했다(**미확인**).
  - 무선 판을 쓰면 스프링 안테나 자리를 따로 봐야 한다.
- DZcc-U4 = AP6212 대응은 높이와 크기로 본 **가정**이다.
- 사람 눈 확인 항목은 없다. 이번 판정은 모두 수치(verifiable 예)다.
