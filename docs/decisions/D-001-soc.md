# D-001 SoC 선택: Sophgo SG2002
- 날짜: 2026-11-26 · 결정자: 사용자 · 기록: lead
- 상태: 방향 결정. 조달·SDK·센서 조사로 확인 전 (아래 "확인 필요" 미해결 시 재검토)

## 배경
- 목표: PCBWay 등 극소량 제작, 가장 싸고 빠른 리눅스 SBC형 완전기능 PoC.
- 외장 DDR + BGA SoC는 6층 이상·임피던스/길이 정합·BGA 조립/X-ray·재제작 위험으로 비용과 일정이 커서 피한다 → DDR 내장 QFN SoC 우선.
- 사용자 지정: Rockchip RV 계열 제외 (사내 사용 모델).

## 후보와 판단 (일반 지식 기준, 수치 미검증)
| 후보 | 판단 |
|---|---|
| Sophgo SG2002 | 채택. DDR 내장(256MB급), MIPI CSI·ISP·H.264/265·NPU, QFN, SDK·참고 보드(Milk-V Duo 256M, LicheeRV Nano) 공개 |
| Allwinner V851s/V851se | 2순위. DDR 내장(64MB급), ISP·NPU, QFN, Tina Linux |
| Sophgo CV1800B | NPU 없음 — 감지 기능 요구와 불일치 |
| Ingenic T31/T41, SigmaStar SSC33x | SDK NDA·소량 조달 어려움 |
| RPi CM4/CM5 등 모듈+캐리어 | 사용자가 SoC 직접 탑재 경로 선택 |

## 확인 필요 (research 조사 대상)
1. SG2002 칩 단품 소량(1/5/10개) 조달처·단가·MOQ·재고·납기, PCBWay 조립 공급 가능 여부
2. 공식 데이터시트·하드웨어 설계 가이드 URL/리비전, 참고 보드 회로도 공개 범위·라이선스
3. 공식 SDK(`duo-buildroot-sdk` 등) 버전·커널·유지보수 상태, NPU 모델 변환 도구(`tpu-mlir`) 지원 범위
4. SDK 지원 카메라 센서와 IQ 튜닝 파일 제공 목록, 센서 모듈 소량 조달성
5. 같은 항목의 V851s 비교 (대체 경로 판단용)

조달 불가 시: V851s 전환 또는 모듈 캐리어 경로를 사용자에게 다시 묻는다.
