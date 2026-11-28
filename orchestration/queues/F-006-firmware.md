[orch t18r → firmware] 배정 F-006 · F-005 후속 (orch 분기 O-70·O-71) — 같은 F-005 레인 t-20261127-021240-b74e
■ O-70 ethtool 패키지 추가: 이더넷 O-47 링크 시험(10M 강제·광고 제한)을 장치 쪽에서도 하려면 필요 → buildroot BR2_PACKAGE_ETHTOOL=y(기존 패치 방식, apply 스크립트로), 이미지 빌드(slot, F-002 방식) 종료 0·해시, rootfs에 ethtool 있음 확인, 크기 증가 기록. 절차서 T1~T4에 장치 쪽 명령 추가(PC 쪽 방법은 차선으로 남김).
■ O-71 열 판정 수치(절차서 8절): M-003 2차(mechanical 레인 t-20261127-013549-8089 4752a68, mechanical/m003/analysis2.md) H3 방열판 계산값 — 25/40°C 주변에서 안 공기 44.8/59.4, SoC 접합 50.0/64.9, LED 접합 57.1/71.9(A), A+B 안 공기 46.5/61.1. 판정 기준: 계산값 + 여유(근거 명시) 또는 부품 정격(VSMA·SG2002 데이터시트 Tj max 인용). 측정 위치(TP_A1/A2·TP_B1/B2·방열판·외함 벽)와 열평형 판정(예: 5분 변화 ≤0.5K).
■ 시험: test-bringup-check.sh 다시 rc 0. 완료: 커밋 → hc send t18r.
