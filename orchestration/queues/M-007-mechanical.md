[orch t18r → mechanical] 배정 M-007 · VD-001 조건 5 — 전체 조립 STEP 틀과 대체 3D 모델 (M-006과 같은 새 레인에서 이어서)
■ 대체 3D 모델: 보드 STEP에서 빠진 것(캐리어 J3 USB-C·J5 RJ45·L1 SRP7028A·Q3/Q4 SOT-523, 전면 X1·Q3/Q5/Q7 SOT-523 — pcb aebd293 보고) — 데이터시트 치수로 STEP 만들어 mechanical/models/에 커밋(출처 쪽·치수 표). pcb가 풋프린트 3D 경로에 연결하도록 orch가 전달(경로·원점·회전 규칙을 문서로).
■ 조립 STEP 틀(스크립트로 재생성): 캐리어·코어 모듈·전면·센서 블록·CLA216·렌즈 CIL093·GH 하니스(26AWG 35mm)·외함 HOUSING/FRONT_COVER·SK 444 방열판+받침대·PMMA 창 4·폼·패드. pcb 새 STEP이 오면 한 명령으로 교체.
■ 기계 판정(스크립트 출력 표, 종료 코드 = 실패 수): 바디 쌍 간섭 0(의도된 것 이름 규칙으로 제외·목록), 최소 틈 표(주요 쌍), 커넥터 플러그 삽입 공간(USB-C·RJ45·DC·microSD 플러그 바디 모델로 삽입 경로 간섭 0), 광축-창 중심 어긋남, LED 조사 원뿔 ↔ 창 주머니·덮개 가림 0(직접광), 짝 BTB 결합 높이(M-006/R-019 값). 렌더(앞·뒤·단면·분해)는 VD-001 HTML용으로 validation/runtime/vd001/에.
■ 완료: 커밋 → hc send t18r → 셸 루트.
