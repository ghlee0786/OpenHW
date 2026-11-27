# O-107 병렬 배정 (lead 지시 2026-11-27 10:26, 병목 해소)
## pcb (t1bk) — 캐리어만
- 전면 front.kicad_pcb는 schematic 칸으로 넘김 — pcb는 이제 전면 파일을 열지도 고치지도 않음(병합 충돌 방지).
- 캐리어 결정 A는 11:30까지. 미연결이 줄지 않으면 묻지 말고 C로 감(In1 짧은 점프, 고속 쌍 투영 밖, 길이 최소). 13:00에도 남으면 D(6층). 전환은 사후 보고만(D-003 #54·#56 사전 승인).
- 경로 계산은 넷마다 시간 상한을 두고, 기다리는 동안 다른 넷을 작업.
- 단계 증거(step_evidence)는 DRC 수치가 바뀌는 커밋에만 1회. 스크린샷 도구 수리는 중단.
- 회로도는 동결(③). 막힘 해소용 변경만 lead 승인.
## schematic (t18z) — P-005 전면 보드
- `node harness/cli.js start --from t-20261126-171922-251f "P-005 전면 보드 배선 마무리"`로 새 레인을 만들고 front.kicad_pcb만 맡음. 기준은 fb43088 확정판(위반 9·미연결 26·parity 0).
- 헤드리스(kicad-cli·KiCad 번들 pcbnew python)로 O-103/O-105와 같은 방식:
  - 고속 CSI·전원·IR 열 패드 트랙은 잠금.
  - 막힌 구역은 커넥터·장착 구멍·M-008 금지 영역을 고정한 채 부품만 다시 펼침.
  - 저속만 다시 배선하고, GND 섬은 4층 모두 GND인 자리에 스티칭 비아.
- 캐리어 파일과 공용 hardware/pcb/tools는 수정 금지. 필요하면 레인 안 사본(hardware/pcb/tools_front/ 등)을 씀.
- 판정은 kicad-cli DRC --schematic-parity 종료 코드. 넷 묶음마다 커밋하고 수치를 hc send t18r.
- 시간 상한도 pcb와 같음: 11:30 A → C → 13:00 D, 사후 보고.
## research (t18s) — R-026 Freerouting 규칙 누락 수정(60분 상한)
- 원인 진단: .kicad_pro 넷클래스·설계 규칙(트랙/간격 0.15/0.16, 고속 0.30 둘레, 비아 0.65/0.30, 쌍 규칙)이 DSN에 안 들어감. 참고: pcb 레인 hardware/pcb/tools/fr_board.ps1·freeroute.py·route/carrier-freerouting.log.
- 수정: DSN 후처리 또는 내보내기 옵션으로 규칙을 반영하고, 고속·전원·열 트랙·GND 비아는 fix(잠금).
- 시험: main 사본(git archive)에서 캐리어·전면 저속 넷만 Java Freerouting(C:/Users/gh/tools/freerouting, Temurin 25 전체 경로, Docker 금지).
- 합격 조건: 결과 SES를 보드 사본에 가져와 kicad-cli DRC를 돌렸을 때 위반은 늘지 않고 미연결만 줄어야 함. 그러면 SES와 가져오기 명령을 pcb(캐리어)·schematic(전면)에 전달(orch 경유).
- 60분 안에 안 되면 원인과 근거를 보고하고 멈춤.
## review (t191) — V-006 사전 감수
- WIP 보드(캐리어 ba7bd51 이후 최신 커밋, 전면 fb43088)로 run_v005.sh를 돌려 배선 무관 항목을 끝내 둠:
  - 배치·실크(O-65·O-74b 사본 E4)·규칙 완화 대조(O-86)·열 비아·절연 패드·전원 폭(R-020 전원 항목)·3D 모델 감사.
- 결과는 수정 요청 목록으로(실크 참조 Fab/실크 수 포함). 출력은 main validation/runtime/vd001/(O-100).
## firmware (t18w) — P-004 산출물 파이프라인 시험
- pcb 레인 hardware/pcb/tools/fab_outputs.ps1(·fab.py)를 WIP 보드 사본(git archive)으로 실행. 출력은 scratch 또는 main 사본이고 커밋하지 않음.
- Gerber·드릴·CPL(왼쪽 아래 원점·0~360°)·BOM 9열·조립도·zip이 만들어지는지 확인.
- review의 v006_fab 검사(R-010 16항)도 돌려 오류를 미리 제거. 고칠 것은 목록으로 pcb에 전달(orch 경유) — pcb 파일은 직접 수정 금지.
- Docker 금지.
## mechanical (t18x)
- Fusion은 열지 않음. 가져오기·재질·렌더 스크립트 건식 점검을 유지.
- 각 칸이 커밋을 내면 run_case 비-Fusion 부분(모델 감사·STEP 내보내기·판정 계산)만 WIP로 미리 돌려 막힘을 확인(Fusion 단계는 건너뜀).
