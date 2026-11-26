[orch t18r → firmware] 배정 SIM-001b · VD-001 7) 회로 시뮬레이션 — 부하·제어 회로 (사용자 지시 2026-11-27, orch 분기 O-80) — F-008 끝난 뒤, main 최신에서 새 레인
■ 도구: schematic이 설치하는 ngspice 경로(orch가 전달)만 사용 — 따로 설치하지 않음.
■ 시험(각각 합격 기준 먼저 커밋 → 실행 → 파형 PNG + 수치 표 + 합격/불합격), 회로 값은 main 회로도(front/carrier.kicad_sch, 계약 v1.11) 그대로:
 1) AL8860 ×2: LED 전류 1A(센스 저항 R13/R14 ±1% 최악), 리플, PWM 25% 디밍(IR_CTRL, daynight 주기), 인덕터 포화(SRN6045 47µH Isat), 스트링 A+B 동시 — 12V_IR eFuse 입력 전류 합.
 2) DRV8837 ICR 펄스: 코일 전류·펄스 시간(daynight 코드 값)·극성(IN1/IN2 → OUT 방향, 계약 표와 대조).
 3) CAM_1V8 스위치 Q6/Q7: 켜짐/꺼짐 시간·돌입 전류·꺼진 센서 역급전 0(O-33 — 꺼진 상태 I2C/클록 핀 경유 누설 경로 포함).
 4) I2C 풀업 상승 시간(버스 용량 추정 근거 — 핀 용량·트랙 길이), 100kHz·400kHz 규격 판정; 리셋 RC 시간.
■ 모델: 제조사 SPICE가 ngspice에서 안 돌면 데이터시트 수치 동작 모델 + 근거. 불합격은 D-003 방식 수정 제안 → orch 판단. 결과 hardware/sim/(SIM-001a와 같은 결과 JSON 형식 — schematic과 맞춤).
■ 완료: 커밋 → hc send t18r → 셸 루트.
