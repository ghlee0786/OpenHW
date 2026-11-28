[orch t18r → firmware] 배정 F-005 · bring-up 확인 절차서 (lead 요청 2026-11-27, orch 분기 O-67)
■ 먼저(병합 막힘 해소): lead의 batch b-20261127-012222… 다음 묶음 b-20261127-021022-80bf(firmware 레인 1e37 + lead 레인 46d1)가 "firmware 세션이 1e37 worktree에 살아 있음"으로 accept가 막혀 있다. ① 1e37에 미커밋 변경 0 확인 ② 셸을 C:/workspace_python/OpenHW 로 옮김(cd) ③ 거기서 node harness/cli.js start "F-005 bring-up 확인 절차서"로 새 레인(main 기준) 생성 → 그 worktree로 이동 ④ 1e37을 더 이상 쓰지 않는다고 hc send t18r(orch가 lead에 알림). 1e37 파일은 이후 읽기만.
■ 업무: 보드 도착 시 확인 절차서 firmware/docs/bringup-checklist.md — 항목마다 목적·준비물·명령(정확히)·기대값·합격/불합격 판정·불합격 시 차선(D-003/원장 번호), verifiable 예/아니오 열:
 1) 전원 순서·전압(12V 입력 → 5V TPS54302 → CAM_1V8 Q6/Q7 순서, 측정점 TP 번호)
 2) 부팅·이미지 기록(out-f004c emmc.zip 00b685a0…, recovery 절차), 콘솔 UART 위치
 3) 카메라: GC2053 i2c 감지·mirror+flip·주야 IQ bin 전환
 4) persond: BF16 cvimodel 로드(sha256 eee83a22…)·실검출·FPS 측정법(목표값 근거 — 없으면 측정만), sscma-node 프레임 행 정렬(F-004c 원인 L) 확인법
 5) daynight: LTR-329 값·히스테리시스, PWM 완전 끔(1/250000 Low 잔여 가정 확인), ICR 극성, IR 듀티 ≤25% 강제(오실로스코프 측정점), IR_LED_EN 순서
 6) 이더넷 O-47 링크 시험: 100M 자동 협상·10M 강제·10M만 광고 상대·직결/크로스 — 실패 시 차선(회로도 P/N 반전)
 7) USB-C·microSD·버튼·상태 LED
 8) 열: IR 듀티 25% + SoC 부하에서 온도 측정 위치·기준(M-003 2차 결과 오면 갱신)
■ 근거는 원장·계약 hw-fw-contract.md v1.10·F-002~F-004 문서에서 인용(경로·커밋). 하드웨어 없이 할 수 있는 사전 시험(스크립트 문법 검사 등)이 있으면 종료 코드 기록. 완료: 커밋 → hc send t18r. 구매·외부 연락 금지.
