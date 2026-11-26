# F-005 bring-up 확인 절차서 — reCamera Core 2002 캐리어·전면 보드

- 배정: orch t18r F-005 (O-67) · 추가 O-69(IR 스트링 B) · lead #10(12V 입력 전류) · 작성: firmware t18w · 레인 `t-20261127-021240-b74e` (main `1a6147a` 기준) · 2026-11-27 · **F-006 갱신** (O-70 ethtool · O-71 열 판정 수치, 레인 `t-20261127-022900-ed35`) · **F-007** PC 쪽 도구 연결(13절, 레인 `t-20261127-033718-7bdb`)
- 판정 원칙:
  - 이 문서의 모든 판정은 **보드가 도착한 뒤** 한다. 지금까지 HIL은 0건이다.
  - `verifiable` 열의 뜻:
    - **예**: 종료 코드, 읽은 값, 계측값으로 기계적으로 판정한다.
    - **아니오**: 사람이 눈으로 본다(영상, LED, 극성 방향). 이 항목은 사진과 영상을 모아 사용자가 확인하기 전까지 통과가 아니다.
  - 불합격하면 그 항목에서 멈추고, 근거(값·로그·사진)를 남긴 뒤 오른쪽 "차선"을 orch에 보고한다. 같은 원인의 재시험은 원인마다 3회까지다.
- **자동 확인 스크립트:** `firmware/scripts/bringup-check.sh`
  - 보드에서 `sh bringup-check.sh`로 실행한다. 줄마다 PASS / FAIL / SKIP을 출력하고, 종료 코드는 FAIL 개수다.
  - 아래 표의 "스크립트" 열에 대응하는 검사 번호를 적었다.

## 0. 근거 (인용 경로 · 커밋)

| 약칭 | 경로 | 커밋 |
|---|---|---|
| 계약 | `hardware/schematic/hw-fw-contract.md` v1.10 | `4d5d49e` (main 병합 `281043b`) |
| 회로 생성기 | `hardware/schematic/tools/boards.py` (`carrier.kicad_sch` · `front.kicad_sch` 생성) | `32e9ed9` / C-011 `83728da` |
| 회로 README | `hardware/schematic/README.md` | `83728da` |
| D-003 | `docs/decisions/D-003-working-defaults.md` (#1~#32) | `4a1949b` |
| R-013 | `docs/research/r013-ephy-polarity.md` | `5e456c5` (병합 `03a5794`) |
| 기구 열 | `mechanical/stack-reference.md` L433~465 | `e33bdde` |
| F-001 | `firmware/docs/sdk-facts.md` | `e23e9ec` |
| F-003 | `firmware/docs/f003-bsp-daynight.md` | `37644e4` (병합 `281043b`) |
| F-004/b/c | `firmware/docs/f004-person-event.md` (레인 `t-20261126-210506-1e37`) | `335f3e7` (이 절차서 작성 때 아직 main에 없음 — lead batch 대상) |
| M-003 2차 | `mechanical/m003/analysis2.md` (mechanical 레인 `t-20261127-013549-8089`) | `4752a68` |
| VSMA1085400 | Vishay 데이터시트 Document Number 80294 Rev. 1.4 (08-Jul-2022), https://www.vishay.com/docs/80294/vsma1085400.pdf (sha256 `642c5635c26b48e48d4f095e0907963a4e54c5f9936d3810f06d6aa0798692b3`, 2026-11-27 읽음) | — |
| SG2002 | `hardware/datasheets/sophgo/01_SG2002_Datasheet_V1.0_EN.docx` (Preliminary 1.0-alpha, 온도 표) | `hardware/datasheets/INDEX.md` |
| 원장 | `orchestration/request-ledger.md` (orch 레인 `harness/t-20261126-144334-727e`) | `2151f63` (main의 원장은 빈 틀) |
| 이미지 | `C:/Users/gh/.local/share/openhw-tools/recamera-sdk/out-f010/` (저장소 밖) — F-006 이미지(ethtool) + vo 노드 gpio 속성 삭제 | F-010 (`0004-openhw-vo-gpio.patch`) |

시험점 번호는 `boards.py` 시험점 목록 순서다(캐리어 L135–138, 전면 L237–239). 위치(좌표)는 PCB 배치가 main에 없어 **미기재**이므로, 실물 실크로 찾는다.
- **캐리어:** TP1 12V_IN · TP2 5V_SYS · TP3 12V_IR · TP4 CORE_3V3 · TP5 SD_PWR_3V3 · TP6/7 GND · TP8/9 USB_DP/DN · TP10 USB_DET · TP11 nRESET · TP12 UPGRAD_KEY · TP13 STATUS_LED · TP14 IR_LED_EN · TP15 SPARE1 · TP16/17 I2C1 SDA/SCL · TP18/19 RESERVE1/2 · TP20–23 UART1 RX/TX/CTS/RTS · TP24/25 DEBUG_UART0 TX/RX · TP26 ALS_INT_RSV
- **전면:** TP1 VIN · TP2 FRONT_2V8 · TP3 CORE_1V8 · TP4 CORE_3V3 · TP5 CAM_AVDD · TP6 CAM_IOVDD · TP7 CAM_MCLK · TP8 CAM_EN · TP9 CAM_RESET · TP10/11 ICR_A/ICR_B · TP12 IRA_SW · TP13 IRA_SET · TP14 IR_PWM · TP15 IR_CTRL · TP16 LIGHT_SENSE · TP17/18 CAM_I2C2 SDA/SCL · TP19 12V_IR · TP20/21 GND · TP22 SPARE1 · TP23 CAM_1V8

**공통 준비물:**
- 12V 2A 이상 가변 전원(전류 제한 가능)
- 어댑터 GST25A12 (12V 2.08A)
- DMM 2대
- 오실로스코프 2ch 이상 (100MHz급이면 충분)
- 전류 측정: 전류 프로브 또는 0.1Ω 정밀 션트 + 차동 측정
- 3.3V USB-UART (JST SH 3P 케이블)
- microSD (8GB 이상)
- 기가비트 스위치 1대, 리눅스 PC 1대(`ethtool`, `iperf3`, `mosquitto-clients`, `ffplay` 또는 VLC), 랜선(직결·크로스)
- 열전대 2ch 이상 또는 열화상
- 실내 조도계, 어두운 상자, 사람(피사체)

> 구매가 필요한 계측기는 사용자 지시 대기 목록에 올린다. 이 절차서는 구매하지 않는다.

**데몬 로그 보기:**
- `S96daynight`·`S97persond`는 `start-stop-daemon -b`로 띄운다. 그래서 stderr가 남지 않고 `logread`에도 나오지 않는다.
- 로그가 필요한 항목에서는 init 스크립트로 멈춘 뒤 포그라운드로 다시 띄워 콘솔에서 본다:
  `/etc/init.d/S97persond stop; persond /etc/openhw/persond.conf`
  `/etc/init.d/S96daynight stop; daynight /etc/openhw/daynight.conf`
- 확인이 끝나면 Ctrl-C로 끊고 `start`로 되돌린다.

## 1. 전원 순서 · 전압 · 12V 입력 전류

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 1-1 | 첫 전원 단락·과전류 | 가변 전원, DMM | **모듈(코어)을 꽂지 않은 캐리어만** 놓고, 12V를 전류 제한 0.3A로 J2 DC 잭에 넣는다. 전류를 읽는다 | 무부하 < 50mA (벅 대기 + 전원 LED D3·R4 2.2k ≈ 2mA) | 제한에 걸리지 않으면 합격 | 전원을 끊고 Q1 AO4407A 방향·D2 SMBJ15A·U1 주변 단락을 찾는다. 원인을 고치기 전에는 다음 단계로 가지 않는다 | 예 |
| 1-2 | 역접 보호 | 가변 전원 | 극성을 바꿔 12V를 0.3A 제한으로 2초 넣는다 | 전류 ≈ 0, TP2 = 0V | 손상 없이 1-1이 다시 통과하면 합격 | Q1 역접 P-FET 배치 확인(계약 12절) | 예 |
| 1-3 | 5V 벅 출력 | DMM | 1-1 상태에서 TP1(12V_IN) · TP2(5V_SYS)를 잰다 | TP1 ≈ 12V − Q1 강하. **TP2 = 5.08V** (R2 100k / R3 13.3k 계산, README L97). 계약 기준 5V ±5% = 4.75~5.25V | 4.75~5.25V면 합격 | 5.30V 이상: D7 SMBJ6.0A가 동작하기 전에 전원을 끊고 R2·R3 값을 확인한다 | 예 |
| 1-4 | 리플 | 스코프 (20MHz 대역 제한, 접지 스프링) | TP2에서 AC 결합으로 본다 | 리플 수치 계약 없음 → **측정만 기록** | 기록 | — | 예 |
| 1-5 | 코어 장착 후 레일 | DMM | 전원을 끄고 코어를 장착한 뒤 1.0A 제한으로 켠다. TP2, 캐리어 TP4(CORE_3V3), 전면 TP1(VIN)·TP2(FRONT_2V8)·TP3(CORE_1V8)·TP4(CORE_3V3)를 잰다 | VIN ≈ 5.08V · FRONT_2V8 2.8V (RT9013-28) · CORE_3V3 3.3V · CORE_1V8 1.8V | 각 ±5% 안이면 합격 (허용 오차 문서 값 없음 → ±5%로 둔다) | 레일별로 해당 LDO·BTB 핀을 확인한다(계약 4·5절 핀맵, 홀짝 반전 규칙) | 예 |
| 1-6 | **CAM_1V8 순서** (Q6/Q7) | 스코프 2ch | ch1 = 전면 TP8(CAM_EN), ch2 = TP23(CAM_1V8), 트리거는 CAM_EN 상승. 부팅 중 `S70hardware`가 CAM_EN을 1로 만드는 순간을 잡는다. 다시 보려면 콘솔에서 `echo 0 > /sys/class/gpio/gpio358/value; sleep 1; echo 1 > /sys/class/gpio/gpio358/value` | CAM_EN 1 → Q7 켜짐 → CAM_1V8_G Low → Q6 켜짐 → CAM_1V8 상승. 게이트 τ ≈ 8µs (R17 10k, 계약 L110) → **수십 µs 안에 1.8V** · 꺼질 때 CAM_1V8 하강 | CAM_1V8이 CAM_EN 상승 뒤 1ms 안에 1.71V 이상이면 합격 | Q6 게이트 극성 또는 R17 값 확인(V-004b N1·V-004c) | 예 |
| 1-7 | MCLK와 첫 I2C 간격 (V-004b R2, **≥5ms**) | 스코프 3ch | ch1 CAM_EN(TP8) · ch2 CAM_MCLK(TP7) · ch3 CAM_I2C2_SCL(TP18), 트리거는 CAM_EN 상승 | MCLK 24MHz가 시작된 뒤 첫 SCL 활동까지 ≥5ms. 근거: X1 시작 최대 3ms + MCLK 1200주기, F-003 `dn_may_poll`이 CAM_EN 상승 뒤 5ms를 기다림 | ≥5ms면 합격 | 5ms 미만이면 sscma-node의 센서 초기화 시점 문제다. `S70hardware` 뒤 지연 추가를 F-00x로 보고 | 예 |
| 1-8 | 12V_IR 기본 끔 | DMM | 부팅 직후 낮 모드(밝은 실내)에서 TP3(캐리어 12V_IR) · TP14(IR_LED_EN)를 잰다 | IR_LED_EN 0V → TPS26600 SHDN 차단 → **12V_IR ≈ 0V** | 0.5V 미만이면 합격 | R5 10k 풀다운, gpio431(portc 베이스 추론) 확인 → 2-5 | 예 |
| 1-9 | **12V 입력 전류 — 최악 조건 (lead #10)** | 전류 측정 2종(아래), 리눅스 PC, 스위치 | 아래 「1-9 절차」 | 계약 3.2절 L125: 2스트링 최악 **≈1.84A / ≈22W**. 어댑터 GST25A12 2.08A, 여유 약 12% | **평균 ≤ 1.9A면 합격.** 피크는 기록하고, 어댑터 2.08A를 넘으면 함께 보고 | 평균이 1.9A를 넘으면 **12V 3A급 어댑터로 교체** (구매는 사용자 지시 — 대기 목록) | 예 |

### 1-9 절차 (12V 입력 전류 최악 조건)

**조건:** 세 부하를 동시에 30분 이상 건다. 30분은 열이 안정될 때까지의 시간이며, D-003 #26의 듀티 25%·30분과 같다. 이 시험은 8-2 열 시험과 같은 회차로 해도 된다.

**1. IR A + B, 켬 비율 25% (O-69: PoC는 스트링 B도 실장한다)**
- 어두운 상자로 LTR-329를 가려 밤 모드로 만든다. `cat /run/daynight/mode`가 `night`이어야 한다.
- 또는 시험 동안만 `/etc/openhw/daynight.conf`에서 `night_lux = 100000`, `day_lux = 200000`으로 두고 `/etc/init.d/S96daynight restart` 한다. 시험이 끝나면 원래 값(5 / 20)으로 되돌린다.
- 확인: `bringup-check.sh`의 D2가 `IR 켬 비율 250000ppm` 근처이고 D4가 밤이어야 한다.

**2. NPU 사람 감지 연속**
- persond 기본 동작 그대로 둔다(720p 15fps, BF16 모델).
- 카메라 앞에 사람이 계속 있거나, 사람 사진을 화면에 띄워 둔다.
- 확인: `mosquitto_sub -h 127.0.0.1 -t openhw/v1/event -v`에서 `person_enter`가 나오고, F1 FPS가 0보다 커야 한다.

**3. 이더넷 100M 트래픽**
- RTSP 스트림을 켠다. 이 시험 동안만 `/etc/openhw/persond.conf`에 `rtsp_pass = <임시값>`을 넣고 `/etc/init.d/S97persond restart` 한다.
  - PC에서 `ffplay rtsp://admin:<임시값>@<장치IP>:554/live`(또는 VLC)로 재생을 유지한다.
  - **시험이 끝나면 `rtsp_pass =`(빈 값)로 되돌리고 재시작한다.** D-003 #30 닫힘 기본을 지키기 위해서다. 확인: N3 PASS.
- 동시에 iperf3로 트래픽을 건다(장치 안에 `iperf3`가 있다):
  - 장치: `iperf3 -s -D`
  - PC: `iperf3 -c <장치IP> -t 1800 -b 90M`, 다른 창에서 `iperf3 -c <장치IP> -t 1800 -b 90M -R`(역방향)을 번갈아 건다.
  - 장치 쪽 CPU 부하도 함께 걸린다.
  - 끝나면 장치에서 `killall iperf3`.

**측정**
- **평균**
  - 계측기: 12V 경로(어댑터 → J2 사이)에 직렬로 넣은 DMM(DC A, 분해능 1mA 이상). 로깅 기능이 있으면 1초 간격으로 30분 기록하고 평균을 낸다.
  - 로깅이 없으면 시작 5분 뒤부터 1분 간격으로 25회 읽어 평균을 낸다.
  - 가변 전원의 전류 표시는 분해능 10mA 이상일 때만 보조값으로 쓴다.
- **피크**
  - 계측기: 스코프 + 전류 프로브(DC 결합, 대역 ≥1MHz). 프로브가 없으면 12V 리턴 쪽 0.1Ω 1% 션트 양단을 차동으로 잰다(100mV/A).
  - 샘플: ≥1MS/s, 기록 길이는 IR PWM 10주기(400Hz → 25ms) 이상.
  - IR 켬 구간(PWM Low)의 최댓값과 ICR 전환 펄스(밤↔낮 전환 순간, 약 0.245A × 200ms)를 따로 잡는다.
- **기록:** 평균 A, 피크 A, 12V 전압(TP1)의 최저값, 시험 시작·끝 시각, 장치 `top -b -n1` 한 장, 그리고 `bringup-check.sh` 출력.
- **집계 (F-007):** 로거 CSV(시간 열 + 전류 열, A 또는 mA)를 `python firmware/tools/host/current_csv.py <기록.csv>`로 집계한다. 출력은 전체 평균, 피크, **30분 이동 창 평균의 최댓값**이다. 종료 코드 0 = ≤ 1.9 A, 1 = 넘음(3A급 어댑터 교체 — 구매는 사용자 지시), 2 = 기록이 30분보다 짧음. 피크가 2.08 A를 넘으면 경고만 한다.
- **RTSP 부하 유지·확인 (F-007):** `python firmware/tools/host/rtsp_check.py record rtsp://admin:<임시값>@<장치IP>:554/live load.mkv --seconds 1800`으로 30분 녹화하면 부하가 유지된다. 끝나면 `rtsp_check.py probe load.mkv --expect-fps 15`로 끊김이 없었는지 본다.

## 2. 부팅 · 이미지 기록 · 콘솔 UART

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 2-1 | 이미지 무결성 | 호스트 | `sha256sum out-f010/*.zip` | `sg2002_reCamera_0.2.4_emmc.zip`(= `upgrade.zip`) **`a275afb12988a2185640ccf0417983a67e11925fafc3ce7ad598e48e59bda134`** · recovery `3dd2d5c66da10e764e0213460de76305590a124b34d2a6730f0eb7076d9e1df7` · sd_compat `38d71b1cb275a437e2ceabf3e4e554eee18cf1b36369da7a396545bac0322b48` (F-010 = F-006 이미지 `1553210f…` + vo gpio 속성 삭제, 14절) | 일치하면 합격 | 다르면 쓰지 않고 다시 collect한다 | 예 |
| 2-2 | 콘솔 연결 | 3.3V USB-UART | 캐리어 **J6 JST SH 3P**: 1 = GND, 2 = DEBUG_UART0_TX, 3 = DEBUG_UART0_RX (`boards.py` L116–117). 어댑터 RX ← J6-2, TX → J6-3. 호스트에서 `115200 8N1` | 보드율 근거: 이미지 `/etc/inittab` `ttyS0::respawn:/sbin/getty -L ttyS0 115200 vt100` (out-f004c rootfs 확인). 계약 11절은 "실물로 확인" | 부트로그(fsbl → OpenSBI → u-boot → Linux)가 깨지지 않고 나오면 합격 | 글자가 깨지면 보드율을 바꿔 본다. 아무것도 나오지 않으면 TP24/TP25 파형 확인. **TX에 풀다운·LED를 달지 않는다**(부트 스트랩, 계약 10절) | 예 |
| 2-3 | 공장 이미지 부팅 확인 | 콘솔 | 받은 그대로 부팅한다(굽기 전) | `login:` 프롬프트 | 프롬프트가 나오면 합격 | 코어 불량 또는 BTB 결합 문제 → 1-5 다시 | 예 |
| 2-4 | **우리 이미지 기록** | microSD, 콘솔 | 1안 SD 복구: `*_emmc_recovery.zip`을 SD에 준비하고 꽂은 채 전원을 넣으면 eMMC에 굽는다(F-001 L63, RC README §2.4). SD에 쓰는 정확한 형식(압축 풀기·파티션)은 RC README §2.4 원문을 따른다 — **이 레인에서 원문 형식은 다시 확인하지 않았다**. 부트 순서는 SD가 먼저다(`run sdboot \|\| cvi_update …`, F-001 L61). 2안 USB: `usb_dl.exe -c cv181x -s linux -i <압축 푼 폴더>`, 캐리어 USB-C(J3) 디바이스 모드. 버튼 절차는 미확인(계약 14절 실물 3) | 콘솔에 굽기 진행이 보이고, SD를 빼고 재부팅하면 eMMC로 부팅된다 | `cat /etc/openhw/persond.conf`가 있고 P1(모델 sha256)이 PASS면 합격 | USB 굽기 모드 진입 절차는 UPGRAD_KEY(SW2)를 누른 채 전원/RESET으로 시험해 기록한다(F-001 L65 "절차 미확인"). 3회 실패하면 멈추고 보고 | 예 |
| 2-5 | DTS·GPIO 베이스 | 콘솔 | `sh bringup-check.sh` (B1·B2) · `cat /sys/class/gpio/gpiochip*/label /sys/class/gpio/gpiochip*/base` | B1 `Seeed reCamera` (`S70hardware`가 이 문자열일 때만 CAM_EN = gpio358을 쓴다. 다르면 gpio495 = **우리 ICR IN1**을 건드린다) · B2 portc 베이스 **416** → gpio428 STATUS_LED · gpio431 IR_LED_EN (계약 14절 실물 2) | 둘 다 PASS면 합격 | 베이스가 다르면 `daynight.c` `GPIO_IR_EN`, DTS `status_led`를 다시 계산해야 한다 → F-00x 수정 보고 | 예 |
| 2-6 | 데몬 기동 | 콘솔 | `bringup-check.sh` P2 | mosquitto · sscma-node · daynight · persond 실행 중 | P2 4줄이 PASS면 합격 | 빠진 데몬을 포그라운드로 띄워(0절 「데몬 로그 보기」) 오류 줄을 근거로 해당 항목(3·4·5)으로 | 예 |
| 2-7 | 복구 경로 (계약 10절) | microSD | 2-4 1안을 한 번 더 하고 같은 결과인지 본다 | 같은 해시, 같은 동작 | 같으면 합격 | — | 예 |

## 3. 카메라 (GC2053)

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 3-1 | 센서 I2C 감지 | 콘솔 | `bringup-check.sh` C2 = `i2cget -y -f 2 0x3f 0xf0` / `0xf1` | **0x20 / 0x53** (칩 ID 0x2053, SDK `gc2053_sensor_ctl.c` L14–16). 주소 **0x3f** (계약 6절, F-001 `s32I2cAddr=0x3f`) | 일치하면 합격 | 응답 없음 → 1-6·1-7(CAM_1V8·MCLK) · TP17/18 풀업(4.7k → CAM_1V8) · 센서 FPC 방향(DF30 180°, P-003) | 예 |
| 3-2 | 영상 나옴 | PC (RTSP), 1-9의 임시 `rtsp_pass` | `ffplay rtsp://admin:<임시값>@<장치IP>:554/live` (끝나면 `rtsp_pass` 비움). 기계 판정은 `python firmware/tools/host/rtsp_check.py probe rtsp://admin:<임시값>@<장치IP>:554/live --seconds 20 --expect-fps 15` (F-007: FPS ≥ 13.5 · 최대 간격 ≤ 0.5 s · 실시간 비율 ≥ 0.9이면 rc 0). 지연은 `rtsp_check.py latency <URL> f.png`로 프레임 1장과 PC 수신 시각을 남기고, 카메라가 찍은 PC 화면 ms 시계와 비교한다(사람 눈) | 720p 15fps 영상 (persond `cam_option=1`, `cam_fps=15`) | 영상이 나오면 합격 | sscma-node를 포그라운드로 띄워(0절과 같은 방법) 오류 확인 | 영상 = 아니오 (눈) / probe = 예 |
| 3-3 | **mirror + flip** (P-003) | 글자가 쓰인 종이 | 카메라 앞에 글자를 보이고 3-2 화면을 본다. 이어서 `/etc/openhw/daynight.conf`에 `isp_mirror_flip = 0`을 넣고 `/etc/init.d/S91sscma-node restart; /etc/init.d/S97persond restart` 한 뒤 다시 본다. 끝나면 원래대로 되돌린다 | 기본(1): 글자가 바로 읽히고 위아래가 맞다. 0: 상하좌우가 뒤집힌다 (F-003 3절, sscma-node 패치 `u8Orien`) | 기본에서 바로 보이면 합격 | 반대면 기본값을 0으로 바꾸는 것을 F-00x로 보고(설정 한 줄) | 아니오 (눈, 사진 2장) |
| 3-4 | 주야 IQ bin 전환 | 어두운 상자, 3-2 화면 | 밤으로 만든다(1-9 절차 1). `cat /run/daynight/mode`로 모드를 확인하고 영상 톤을 본다. bin 로드 로그는 sscma-node를 포그라운드로 띄웠을 때의 콘솔 출력에서 본다(`/etc/init.d/S91sscma-node stop` 뒤 같은 명령줄로 실행 — 명령줄은 그 init 스크립트 안에서 확인). 낮으로 되돌린다 | `/run/daynight/mode`가 `night`일 때 `gcore_gc2053_sdr_ir.bin`, `day`일 때 `sdr.bin`을 `CVI_BIN_ImportBinData`로 읽는다(F-003 3절 `OPENHW_DN` 스레드, 500ms 주기). 밤에는 IR 영상(흑백 경향) | 로그 줄이 있고 영상 톤이 바뀌면 합격 | ISP가 도는 중의 교체 반영은 미확인(F-003 미확인 5) → 차선은 bin 교체 뒤 sscma-node 재시작 | 로그 = 예 / 영상 = 아니오 |
| 3-5 | I2C2 공유 | 콘솔 | daynight를 포그라운드로 띄운 채(0절) 밤·낮 전환을 10회 하면서 daynight 콘솔과 `dmesg`의 I2C 오류를 센다 | 오류 0 (GC2053 0x3f와 LTR-329 0x29가 같은 버스, F-003 미확인 6) | 0이면 합격 | 폴링 주기(`poll_ms`)를 늘리는 것을 보고 | 예 |
| 3-6 | **IIC2 내부 풀업 꺼짐 (계약 v1.13 FW 규칙, F-009)** | DMM | `echo 0 > /sys/class/gpio/gpio358/value`(CAM_EN = 0, sscma-node·daynight는 먼저 멈춘다: `/etc/init.d/S91sscma-node stop; /etc/init.d/S96daynight stop`) 뒤 전면 TP17(SDA)·TP18(SCL) 전압을 잰다. 끝나면 CAM_EN = 1, 서비스 시작 | SoC 패드 기본 PD(51~169 kΩ) → **≤ 0.3 V** (SIM-001b B6 기본 조건 계산 0.42 V는 누설 최대값 가정). 내부 풀업이 켜져 있으면 약 0.78 V (B6 민감도) | ≤ 0.5 V면 합격 | 0.5 V를 넘으면 패드 풀 설정을 찾아 끈다(`f009-als-int-iic2.md` 2절 — 레지스터 주소 미확인) · C-017 블리더 10 kΩ 판은 더 낮아야 함 | 예 |

## 4. 사람 감지 (persond · BF16 cvimodel)

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 4-1 | 모델 파일 | 콘솔 | `bringup-check.sh` P1 = `sha256sum /usr/share/openhw/models/yolox_nano_person_416_bf16_cv181x.cvimodel` | **`eee83a224e203248e141ad51426cb6c151f1597c9d5e5b893c66c661baea9835`** (2,808,720 B, F-004c 9.3절) | 일치하면 합격 | 2-4 다시 | 예 |
| 4-2 | 모델 로드 | 콘솔 | persond를 포그라운드로 띄운다(0절). persond는 sscma의 `create` 응답을 `persond: sscma …`로 stderr에 찍는다 | `openhw_person` create 응답 `code` 0, 오류 없음 | 오류가 없으면 합격 | 로드 실패 → sscma-node가 BF16 cvimodel을 받는지(F-004c 미확인 1). 차선: INT8은 기준 불합격이므로 부분 BF16(O-62, `--quantize_table`) | 예 |
| 4-3 | 실검출 | 사람, 빈 벽 | PC에서 `mosquitto_sub`가 불가하다(1883은 로컬 전용, D-003 #30). **콘솔에서** `mosquitto_sub -h 127.0.0.1 -t openhw/v1/event -v`. PC에 남기려면 (F-007) `ssh root@<장치IP> "mosquitto_sub -h 127.0.0.1 -t openhw/v1/event -v" | python firmware/tools/host/event_log.py record --stdin -o ev.jsonl` → 끝나면 `event_log.py check ev.jsonl`(등장/퇴장 짝·쿨다운 30 s·score ≥ 0.5·필드 검사, 종료 코드 = 위반 수) · ① 사람이 화면 가운데에 3초 서 있다 → ② 화면 밖으로 나가 10초 · ③ 빈 벽 1분 | ① `person_enter`, `boxes` 중심 ≈ (0.5, 0.5) ±0.2 ② 5초(`leave_ms`) 뒤 `person_leave` ③ 이벤트 0 | ①②③이 모두 맞으면 합격 | ③에서 오검출 → `min_score` 상향 기록. ①에서 박스 위치가 엇나감 → 4-5 | 예 |
| 4-4 | **FPS 측정법** | 콘솔 | `SECS=60 sh bringup-check.sh` → F1. PC에서 길게 (F-007): `ssh root@<장치IP> "mosquitto_sub -h 127.0.0.1 -t sscma/v0/recamera/node/out/openhw_person -v" | python firmware/tools/host/event_log.py record --stdin -o inv.jsonl` → `python firmware/tools/host/fps_stats.py inv.jsonl` (FPS · MQTT 누락 · perf 단계별 평균/p50/p95/최대, 목표가 없어 rc 0 = 기록). sscma-node `invoke` 메시지(`sscma/v0/recamera/node/out/openhw_person`) 개수 ÷ 60초, `data.perf` `[[pre, inf, post]]` ms 평균 (sscma-node `model.cpp` L76·L251) | **목표 수치 없음.** product-brief·D-003에 FPS·지연 목표가 없다. 참고로 Seeed YOLO11n INT8은 20 FPS · 50ms(sdk-facts L136)인데, 우리 모델·정밀도와는 다르다 | **측정만 기록**: FPS, inf ms, 카메라 15fps 대비 비율 | FPS가 사용에 부족하다고 사용자가 판단하면 차선은 부분 BF16 → INT8 혼합(O-62) 또는 `cam_fps` 조정 | 예 (기록) |
| 4-5 | **프레임 행 정렬 확인** (F-004c 원인 L) | 사람, 줄자 | 모델 입력은 `images_raw [1,1,416,1280] uint8`(행 1248B + 64B 정렬 패딩)이다. sscma-node는 카메라 채널 프레임(`raw->img`, physical)을 그대로 `setInput`한다(`model.cpp` L103–110). ① 사람이 화면 왼쪽 1/4, 오른쪽 1/4, 위, 아래에 차례로 선다 ② 이벤트 `boxes`의 cx·cy를 기록한다 | 박스 중심이 실제 위치를 따라간다(왼쪽 cx < 0.4, 오른쪽 > 0.6). 점수가 F-004c 호스트 모의(사람 0.6~0.93)와 비슷하다 | 4곳이 모두 맞으면 합격 | **점수가 늘 0.01 안팎이거나 박스가 대각선으로 밀리면** 행 정렬 불일치다(호스트에서 F-004b까지 본 증상과 같다) → 카메라 채널 stride와 모델 입력 크기(532,480 B)를 sscma-node 로그로 대조. 차선: `--aligned_input` 없이 재변환 | 예 |
| 4-6 | 야간 IR 정확도 | 어두운 방, 사람 | 밤 모드에서 4-3을 반복한다 | 기록만 (COCO 가시광 가중치라 떨어질 수 있다, F-004 7절) | 기록 | — | 예 (기록) |

## 5. 주야 전환 (daynight) — IR 스트링 A + B

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 5-1 | LTR-329 값 | 콘솔, 조도계 | `bringup-check.sh` C3 (PART_ID `i2cget -y -f 2 0x29 0x86`). daynight는 lux를 찍지 않는다 → 원시값을 직접 읽는다: `i2ctransfer -y -f 2 w1@0x29 0x88 r4` (CH1 L·H, CH0 L·H — daynight가 ALS를 active로 켜 둔 상태에서) | PART_ID 0xA0 (Lite-On 데이터시트 값 — 이 레인에서 원문 재확인 안 함). 원시값(CH0)이 조도계와 같은 경향을 보인다 (lux 식은 앱노트 계수, 창·필터 보정 전, F-003 미확인 7) | ID가 맞고, 밝음/어둠에서 CH0이 10배 이상 달라지면 합격 | 차선 LIGHT_SENSE ADC(`als_source = adc`, 드라이버 미확인, F-003 3절) | 예 |
| 5-2 | 히스테리시스 | 어두운 상자, 시계 | 밝음 → 상자 덮기 → 3초 뒤 `cat /run/daynight/mode` → 상자 열기 → 3초 뒤 다시 | 밤 진입: lux < 5가 3회 연속(1초 주기 → 약 3초). 낮 복귀: lux > 20이 3회 연속. 5~20 사이에서는 바뀌지 않는다 (F-003 3절, `daynight.conf`) | 순서와 시간이 맞으면 합격 | 실측 뒤 값 조정(F3-4) | 예 |
| 5-3 | **PWM 완전 끔** (1/250,000 Low 잔여 가정) | 스코프 | 낮 모드에서 전면 TP14(IR_PWM)를 본다. 400Hz, 1µs 이상 분해능, 단발 트리거(하강 엣지) | `cvi_pwm.c`는 duty == period를 period − 1 카운트로 만든다 → 주기마다 1 카운트(가정: 100MHz 클록 → 10ns, 2.5ms 주기의 1/250,000)만큼 Low 펄스가 남을 수 있다. **낮에는 IR_LED_EN = 0이 먼저 12V_IR을 끊는다** (F-004 4절, `a328164`) | ① TP14 Low 펄스 폭 ≤ 1µs(또는 없음) ② 캐리어 TP3 12V_IR ≈ 0V ③ IR LED가 꺼져 있다(휴대폰 카메라로 확인) | 펄스가 길면 PWM을 disable해 출력 레벨을 확인한다(F3-6 차선). EN 차단이 있으므로 안전 문제는 아니다 | ①② 예 / ③ 아니오 |
| 5-4 | **ICR 극성** | 스코프, 눈 | 전면 TP10(ICR_A)·TP11(ICR_B), 밤↔낮 전환 때. IN1 = gpio495, IN2 = gpio352, 펄스 200ms(`icr_pulse_ms`) 뒤 0/0 코스트 | 밤 = IN1 High / IN2 Low (`icr_night_in1 = 1`) → OUT1(ICR_A) H 펄스 약 200ms. 밤에는 필터가 빠지고 낮에는 들어간다(CLA216 「正極性で開路、負極性で閉路」, 계약 7절) | 파형이 맞고, 밤 = 필터 빠짐(IR 영상) · 낮 = 필터 들어감(색 정상)이면 합격 | 반대면 `icr_night_in1 = 0`(설정 한 줄) 또는 J2 PicoBlade 핀 순서(계약 14절 실물 4) | 파형 = 예 / 필터 = 아니오 (영상·사진) |
| 5-5 | **IR 듀티 ≤25% 강제** | 스코프 2ch | 밤 모드. ch1 = 전면 TP14(IR_PWM), ch2 = TP15(IR_CTRL). 이어서 `/etc/openhw/daynight.conf`에 `ir_on_ratio = 1.0`을 넣고 `/etc/init.d/S96daynight restart` 한다(강제 시험). 끝나면 0.25로 되돌린다 | 400Hz, **Low(켬) 비율 ≤ 25%**. 1.0을 줘도 25% (`dn_clamp_on_ratio`, O-31). `bringup-check.sh` D2·D3 | 스코프 Low 폭 ≤ 625µs/2.5ms이면 합격 | 넘으면 FW 결함 → 즉시 전원을 끊고 보고 (열 위험) | 예 |
| 5-6 | **IR_LED_EN 순서** (O-33) | 스코프 2ch | ch1 = 캐리어 TP14(IR_LED_EN), ch2 = 전면 TP14(IR_PWM). 낮 → 밤 전환을 단발로 잡고, 이어서 밤 → 낮 | 밤 진입: IR_PWM High(끔)가 먼저, 그 뒤 EN 1, 그 뒤 PWM 시작. 낮 진입: **EN 0이 먼저**, 그 뒤 PWM High (F-004 4절 `a328164`) | 순서가 맞으면 합격 | 순서가 틀리면 FW 결함 보고(`dn_plan`) | 예 |
| 5-7 | **스트링 B 제어 (O-69)** | 전류 프로브 또는 DMM | 회로 확인: 두 AL8860(U4 = A, U5 = B)의 CTRL(4번 핀)이 **같은 넷 IR_CTRL**이다(Q5 하나, `boards.py` L211–218, 계약 13절 C18 ③). 전원도 같은 12V_IR(eFuse U2, SHDN ← IR_LED_EN)이다. 따라서 **B에는 별도의 EN·PWM이 없고 A와 공통**이며, daynight가 A와 똑같이 켜고 끄고, 25% 강제도 B에 그대로 걸린다(코드는 `pwmchip0/pwm2` 하나와 gpio431 하나만 다룬다, `daynight.c` L20·L33). 실측: 밤 모드에서 B 스트링 전류를 A와 같은 방법으로 잰다(B에는 시험점이 없다 — 전면 TP12/13은 A의 IRA_SW/IRA_SET뿐. R14(IRB_SET 0.1Ω) 양단 전압을 재거나 전류 프로브로) | B 켬 구간 전류 ≈ 1.0A (Rs 0.1Ω, VSENSE 100mV), 켬 비율 = A와 같은 ≤25%, 낮에는 0 | A·B 파형이 같으면 합격 | **회로도에서 B가 DNP다**(`boards.py` L215 `('B', True)`, U5·R14·D_IR_B*). PoC 실장은 BOM/조립 쪽 변경이다(hardware 담당). **daynight 수정은 필요 없다** | 예 |
| 5-8 | eFuse 한계 | 전류 측정 | 1-9의 IR 부분에서 12V_IR 전류 피크를 잰다 | A+B 최악 1.22A < ILIM 8.06k ≈ 1.49A (계약 3.1절) → 자동 재시도가 일어나지 않는다 | 12V_IR이 끊기지 않으면 합격 | 끊기면 ILIM(R6) 상향 검토를 hardware에 보고 | 예 |
| 5-9 | **IR 끔 구간 잔류 (SIM-001b S3, O-87)** | 스코프 + 전류 프로브, 휴대폰 카메라(IR 보임), 어두운 상자 | 밤 모드 PWM 25 %에서 끔 구간(IR_PWM High)의 LED 전류를 R13·R14 양단 또는 전류 프로브로 잰다(끈 뒤 0~2 ms). 어두운 상자 안에서 끔 구간에 LED 발광이 보이는지 카메라로 본다 | 시뮬레이션: 끈 뒤 100 µs의 \|I\| 최대 6 mA는 인덕터(47 µH)·접합 용량 2.84 MHz 링잉이고, **작은 순방향 꼬리**(100~200 µs 순방향 평균 0.84 mA/스트링, 0.5 ms 뒤 0.12 mA)가 있다 — SIM-001e(`hardware/sim/SIM-001e-criteria.md`)에서 SIM-001b의 "발광 없음"을 정정. 개선 후보 c1(LED 양단 10 kΩ)이면 1.4 µA | 끔 구간 순방향 평균 ≤ 1 mA이고 발광이 보이지 않으면 확인. SIM 판정은 기준대로 불합격으로 남긴다 | 순방향 잔류가 있으면 CTRL 끌어내림(Q5)·AL8860 대기 동작을 확인하고 hardware에 보고 | 전류 = 예 / 발광 = 아니오 |

## 6. 이더넷 링크 (O-47 · R-013 T1~T4)

> **F-006부터 이미지에 `ethtool` 5.10이 들어 있다** (`/usr/sbin/ethtool`, O-70). 그래서 R-013 T1~T4를 **장치 쪽 `ethtool`로 그대로** 한다.
> - 이 EPHY 드라이버가 속도 강제·광고 제한을 실제로 받는지는 미확인이다(드라이버 ethtool ops — HIL에서 확인).
> - 받지 않으면 **차선**: 장치는 sysfs(`/sys/class/net/eth0/{carrier,speed,duplex}`, `bringup-check.sh` N1)로 읽고, 강제·광고 제한은 상대(PC) 쪽 `ethtool`로 한다(F-005 방식).

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 6-1 (T1) | 100M 자동 협상 | 스위치 | 스위치에 연결한다. 장치에서 `ethtool eth0` · `ping -c 1000 -i 0.2 <PC>` · `ip -s link show eth0` | `Speed: 100Mb/s`, `Duplex: Full`, `Link detected: yes`, 손실 0, RX errors 0 (R-013 T1) | 모두 맞으면 합격 | 링크가 없으면 J5 핀(1/2/3/6 = TXP/TXN/RXP/RXN, `boards.py` L106–113), PCB 쌍 비아 교차(D-003 #31) 확인 | 예 |
| 6-2 (T2) | 10M 강제 | PC 직결 | 장치: `ethtool -s eth0 speed 10 duplex full autoneg off`, PC도 같은 값으로 고정(`sudo ethtool -s <if> speed 10 duplex full autoneg off`). 장치 `ethtool eth0` · `ping -c 1000 -i 0.2` · `ip -s link`. 끝나면 장치 `ethtool -s eth0 autoneg on` | 링크 업, 10Mb/s Full, 손실 0, RX 오류 0 (R-013 T2) | 모두 맞으면 합격 | 장치 `ethtool -s`가 `Operation not supported`면 PC 쪽만 고정하는 F-005 방식(장치는 병렬 감지로 10/half일 수 있음 — 기록). **링크 실패 = 10BASE-T 자동 극성 보정 없음**(R-013 L66) → 다음 판에서 회로도 RJ45 쪽 P/N 반전(O-47 · D-003 #31 차선). 100M만 쓰면 T1만으로 운용 가능 | 예 |
| 6-3 (T3) | 10M만 광고 | PC 직결 | ① 장치: `ethtool -s eth0 autoneg on advertise 0x002`(10baseT/Full만), PC는 자동 협상 그대로. 확인 뒤 장치 `ethtool -s eth0 advertise 0x00f`로 되돌림 ② 상대 쪽: PC `sudo ethtool -s <if> autoneg on advertise 0x002`, 장치는 기본 | 두 경우 모두 `Speed: 10Mb/s`, `Duplex: Full` | 둘 다 맞으면 합격 | 장치 쪽 명령이 거부되면 ②만으로 판정(F-005 방식). 실패 시 6-2와 같은 차선 | 예 |
| 6-4 (T4) | 직결·크로스 (Auto MDI-X) | 랜선 2종 | PC에 직결 케이블로, 이어서 크로스 케이블로 각각 6-1 절차. 장치 `ethtool eth0`의 `MDI-X:` 줄도 기록(드라이버가 보고하면) | 두 경우 모두 100/Full, 손실 0 (TRM 18.2.2 Auto MDI-X 지원, R-013 L10) | 둘 다 맞으면 합격 | 한쪽만 되면 MDI-X 미동작 → 스위치 경유만 지원으로 기록 | 예 |
| 6-5 | 노출 닫힘 (D-003 #30) | 콘솔, PC | `bringup-check.sh` N2·N3 · PC에서 `mosquitto_sub -h <장치IP> -t '#' -W 3` | 1883은 루프백만 열림 → PC 접속 실패. `rtsp_pass`가 비어 있으면 554도 닫힘 | N2·N3 PASS이고 PC 접속이 실패하면 합격 | 열려 있으면 출하 전 차단 필수 → FW 결함 보고 | 예 |

## 7. USB-C · microSD · 버튼 · 상태 LED

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 7-1 | USB-C 디바이스 | PC, USB-C 케이블 | J3 연결. 캐리어 TP10(USB_DET) 전압, PC `lsusb`/장치관리자, 장치 `dmesg \| tail` | USB_DET ≈ 1.67V (VBUS 5V × 100k/(200k+100k), README L466) · PC에 장치가 나타난다(DWC2 디바이스, 계약 4절) · 장치 5V_SYS와 VBUS는 분리 | 셋이 다 맞으면 합격 | CC 5.1k(R7·R8) 확인 · USB 굽기는 2-4 2안 | 예 |
| 7-2 | microSD | 카드 | 부팅 뒤 꽂기·빼기 · `dmesg \| tail` · `cat /sys/class/gpio/gpio493/value`(있으면) · `blkid` · 캐리어 TP5(SD_PWR_3V3) | 카드 감지(CD gpio493), 마운트 가능, SD_PWR 3.3V(SD0_PWR_EN gpio494 High = 켬), 3.3V 전용 | 읽기·쓰기 `dd if=/dev/zero of=<마운트>/t bs=1M count=50` + `md5sum`이 맞으면 합격 | Q2/Q3 전원 스위치, U4·U5 ESD 확인 | 예 |
| 7-3 | RESET 버튼 | 콘솔 | SW1을 누른다 | 콘솔에 재부팅 로그 | 재부팅되면 합격 | — | 예 |
| 7-4 | UPGRADE 버튼 | 콘솔 | `cat /sys/class/gpio/gpio510/value`(필요하면 export, 입력) — 누를 때와 뗄 때 | 뗌 1 · 누름 0 (UPGRAD_KEY → R19 1kΩ → SW2, 계약 7절. DTS `wifi_pin`은 삭제됨, F-003 2절) | 값이 바뀌면 합격 | 2-4 USB 굽기 진입 절차와 함께 기록 | 예 |
| 7-5 | 상태 LED | 콘솔, 눈 | `ls /sys/class/leds/`로 이름을 확인한다(DTS 노드 `status_led`, label 없음 → 노드 이름일 것으로 추정). 그 뒤 `echo 1 > /sys/class/leds/<이름>/brightness` → `echo 0 > …` | D6(청색) 켜짐 → 꺼짐 (gpio-leds, portc 12 = gpio428, 기본 끔, F-003 2절) | 켜지고 꺼지면 합격 | 2-5 portc 베이스 확인 | 아니오 (눈) |
| 7-6 | 전원 LED | 눈 | 전원을 넣는다 | D3 켜짐 | 켜지면 합격 | — | 아니오 |

## 8. 열 (M-003 2차 · O-31 · O-71)

### 8.0 판정 근거 수치

**계산값:** M-003 2차 `analysis2.md`(`4752a68`)의 H3 바깥 핀 9×20 방열판, 정상 상태, 설치 자세 +Y 위.

| 조건 | T_amb | 방열판(내부) | 바깥 방열판 | 안 공기 | 벽 | SoC 접합(추정) | LED 접합(추정) |
|---|---|---|---|---|---|---|---|
| A 듀티 25% | 25 | 42.0 | 38.5 | 44.8 | 32.7 | 50.0 | 57.1 |
| A 듀티 25% | 40 | 56.9 | 53.3 | 59.4 | 47.3 | 64.9 | 71.9 |
| A+B 듀티 25% | 25 | 46.1 | 41.5 | 46.5 | 33.9 | 54.1 | 61.2 |
| A+B 듀티 25% | 40 | 61.0 | 56.3 | 61.1 | 48.4 | 69.0 | 76.0 |
| LED 끔 | 25 | 37.7 | 35.3 | 43.0 | 31.5 | 45.7 | 37.7 |

- 계산 가정은 analysis2에 있다: 코어 2.0W, 보드 1.0W, 흑색 아노다이즈 ε 0.85. 이 가정이 많아서 analysis2는 R에 **25% 여유**를 두었다(L29). 측정값 비교에도 같은 25%를 쓴다.

**부품 정격:**
- **VSMA1085400** (Vishay 80294 Rev. 1.4, Absolute Maximum Ratings)
  - Tj = **145 °C**
  - Tamb −40~+125 °C
  - RthJSP,real 6~9 K/W
  - IF 1.5 A, PV 5.33 W
- **SG2002** (Datasheet V1.0 온도 표)
  - 권장 접합온도 Tjunc: −30 ~ **85~105 °C**
  - 파괴 접합온도: +125 °C
  - Tjunc 최대 **115 °C**(DRAM 때문에 125에서 낮춤)
- **안 공기 상승 목표 ≤ 25 K** (D-003 #26 갱신, analysis2 ① 머리말)

### 8.1 측정 위치와 방법

| # | 목적 | 준비물 | 절차 · 명령 | 기대값 | 판정 | 불합격 시 차선 | verifiable |
|---|---|---|---|---|---|---|---|
| 8-1 | 측정 위치 | 열전대 K형 0.1mm × 8ch (로거 1초 간격), 캡톤 테이프, 열화상(보조) | ① **TP_A1**(−9.5…−0.3, 넷 IRA_SET) ② **TP_A2**(+0.3…+9.5, 넷 IRA_M) ③ **TP_B1**(IRB_SET) ④ **TP_B2**(IRB_M): 전면 아랫면 노출 패드(`mechanical/stack-reference.md` L442–443·L545). 조립하면 절연 패드(INS_PAD_A)와 방열 기둥에 덮이므로, **조립 전에** 패드 가장자리에 열전대를 붙이고 리드를 빼낸다 ⑤ **방열판(내부)**: 기둥 밑동 ⑥ **바깥 방열판**: 핀 뿌리 가운데 ⑦ **외함 벽**: 벽 바깥 가운데 ⑧ **안 공기**: 외함 가운데 허공(벽·부품에 닿지 않게) ⑨ **주변**: 장치에서 30cm, 바람 없는 곳 ⑩ SoC: `cat /sys/class/thermal/thermal_zone*/temp`(있으면 — 경로는 미확인) | — | — | — | 예 |
| 8-1a | **전기 주의** | 캡톤 테이프 | TP_A/TP_B 패드는 LED 애노드 넷(12V_IR 쪽)이다. 열전대 끝을 캡톤으로 절연하고, 서로 다른 패드끼리 열전대로 이어지지 않게 한다 | 열전대 채널 사이 저항이 개방(> 1MΩ) | 개방이면 합격 | 절연을 다시 한다 | 예 |
| 8-2 | **IR A+B 듀티 25% + SoC 부하** | 1-9와 같은 부하 | 1-9 절차 1~3을 그대로 유지한다(밤 모드 + 사람 감지 + RTSP·iperf3). 설치 자세는 +Y 위(analysis2 가정), 주변 온도는 20~30 °C, 바람이 없어야 한다. **열평형 판정: 모든 채널이 5분 동안 변화 ≤ 0.5 K**(최소 30분 뒤부터, D-003 #26). 평형에 이르면 그 5분 평균을 측정값으로 쓴다 | 8.0 표의 A+B · 25 °C 줄 (주변 온도 차이는 아래 ΔT로 맞춘다) | 8.2절 판정 | 8.2절 차선 | 예 |
| 8-3 | A만 (스트링 B 끔과의 비교) | 같은 부하 | B 스트링을 빼고 시험할 수 있으면(B DNP 판) 같은 절차로 A만 한 번 더 한다. 없으면 생략하고 기록한다 | 8.0 표의 A · 25 °C 줄 | 8.2절 판정 | — | 예 |
| 8-4 | LED 끔 기준선 | 낮 모드 + 사람 감지 + 이더넷 부하 | 8-2와 같지만 IR은 끈다 | 8.0 표의 LED 끔 줄 | 기록 (모델 대조용) | — | 예 |

### 8.2 판정 (측정한 주변 온도 Ta에서 ΔT = T − Ta로 바꿔 쓴다)

**① 정격 판정 (필수)**
- 측정한 ΔT를 **주변 40 °C로 옮겨**(T40 = 40 + ΔT) 정격과 비교한다.

| 대상 | 추정식 | 합격선 | 근거 · 여유 | 계산값 (T40, A+B) |
|---|---|---|---|---|
| LED 접합 | T40(TP_A1/A2/B1/B2 중 최고) + 0.78 W × 9 K/W (= +7.0 K) | **≤ 125 °C** | VSMA Tj 145 °C에서 20 K 여유(가정이 많은 열 경로). 0.78 W = 스트링 평균 1.55 W ÷ LED 2개, 빛으로 나가는 몫을 빼지 않은 보수값. 9 K/W는 RthJSP 상한 | 76.0 |
| SoC 접합 | thermal_zone이 있으면 T40(zone). 없으면 T40(방열판 내부) + 8.0 K (analysis2: SoC 접합 − 방열판 내부 = 50.0 − 42.0) | **≤ 85 °C** | SG2002 권장 접합 상한 85~105 °C의 아래쪽 값. DRAM 115 °C까지 30 K 여유 | 69.0 |
| 안 공기 | ΔT(안 공기) | **≤ 25 K** | D-003 #26 갱신 목표 | 21.5 K |

**② 모델 대조 (계산값 + 25% 여유)**
- 측정 ΔT가 아래 상한 이하면 M-003 계산이 맞는 것으로 본다(A+B, 25 °C 계산값 기준).

| 위치 | 계산 ΔT | 상한 (×1.25) |
|---|---|---|
| 방열판(내부) | 21.1 K | 26.4 K |
| 바깥 방열판 | 16.5 K | 20.6 K |
| 안 공기 | 21.5 K | 25.0 K (①의 목표가 더 낮음) |
| 벽 | 8.9 K | 11.1 K |

A만 시험했을 때의 상한(계산값 × 1.25): 방열판(내부) 21.3 K · 바깥 방열판 16.9 K · 안 공기 24.8 K · 벽 9.6 K.

**결과 판정**
- **합격:** ①과 ②가 모두 맞는다.
- **잠정 합격:** ①은 맞고 ②만 넘는다. 실측 ΔT를 mechanical에 넘겨 모델을 갱신하게 하고, 마진을 다시 계산한다.
- **불합격:** ① 중 하나라도 넘는다. 이때는 바로 IR을 끄고 차선으로 간다.
- **차선 순서** (analysis2 "차선 순서 (orch)"):
  1. 방열판 확대 / 핀 추가 (mechanical)
  2. 듀티 상한 하향: `daynight.conf`의 `ir_on_ratio`. 설정 한 줄이고, FW 강제 상한은 0.25 그대로 둔다
  3. 0.3 A 연속 (O-31 차선. analysis2에 따르면 열 이득 없이 조사만 줄어드는 점에 주의)
  4. MCPCB LED 서브보드 (K13)

## 9. 실행 순서 (권장)

1. 1-1 ~ 1-5 (코어 없이 → 코어 장착)
2. 2-1 ~ 2-6 (콘솔 → 공장 부팅 → 우리 이미지)
3. 1-6 ~ 1-8 (부팅된 상태에서 순서 파형)
4. `sh bringup-check.sh` 한 번 → FAIL 항목부터 해당 절로 간다
5. 3 → 4 → 5 → 6 → 7
6. 마지막으로 1-9 + 8-2 (최악 부하, 열평형 = 5분 변화 ≤ 0.5 K까지, 같은 회차) → 8-4 (LED 끔 기준선)
7. `rtsp_pass` 비움 · `daynight.conf` 원래 값 · `bringup-check.sh` 다시 실행해 N2·N3 PASS 확인

## 10. 사전 시험 (하드웨어 없이)

| 무엇 | 명령 | 종료 코드 | 결과 |
|---|---|---|---|
| 문법 (busybox sh / dash / bash) | `busybox sh -n` · `dash -n` · `bash -n firmware/scripts/bringup-check.sh` | 0 / 0 / 0 | — |
| shellcheck | `shellcheck -s sh -S warning firmware/scripts/bringup-check.sh` | 0 | 경고 0 |
| 가짜 트리 시험 | `firmware/scripts/test-bringup-check.sh` (기대 종료 코드와 다르면 0이 아닌 값 · recamera-os-builder 컨테이너, `ROOT=` 가짜 `/sys`·`/proc`·`/run`·`/etc` 트리 3개) | 0 | 낮 정상 FAIL 0 (rc 0) · 밤 정상(켬 25%) FAIL 0 (rc 0) · 고장 주입 5건(DT model · persond 없음 · 켬 50% · ethtool 없음 · 1883 0.0.0.0) → **FAIL 5 (rc 5)**, 주입한 것만 잡힘 |

- 가짜 트리 시험이 보여 주는 것은 판정 논리뿐이다. 하드웨어 명령(C2·C3 `i2cget`, F1 `mosquitto_sub`)은 이 시험에서 SKIP된다.
- 보드에서 처음 돌릴 때 B2의 portc 라벨 매칭이 맞는지도 함께 확인한다. 맞지 않으면 SKIP과 함께 목록을 찍는다.

## 11. 분기점 · 선택 · 이유 · 차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| F5-1 | 이더넷 시험의 `ethtool` | F-005: 장치 sysfs + PC 쪽 `ethtool` → **F-006: 이미지에 `ethtool` 추가(O-70), 장치 쪽 명령이 1안** | R-013 T1~T4 명령을 그대로 쓴다. 크기 증가는 rootfs 사용량 약 393 KiB | 드라이버가 받지 않으면 F-005 방식 |
| F5-2 | 판정 자동화 범위 | 소프트웨어로 읽을 수 있는 것만 `bringup-check.sh`에 넣는다(종료 코드 = FAIL 수) | 전압·파형·열은 계측기 판단이 필요하다 | 계측기 원격 제어 자동화 |
| F5-3 | 1-9 이더넷 부하 | RTSP 재생 + iperf3 양방향 90M | 둘 다 이미지·PC에 이미 있다. RTSP는 시험 동안만 열고 닫는다(D-003 #30) | iperf3만 (RTSP 비밀번호를 쓰지 않는 쪽) |
| F5-4 | 스트링 B | 회로가 A와 공통 제어(CTRL·12V_IR·EN)라 FW 변경 없음, 실측 항목만 추가 | `boards.py` L211–218, C18 ③ | B를 따로 제어하려면 회로 변경(별도 CTRL FET + GPIO) — hardware 결정 |
| F5-5 | 열 합격선 (F-006 O-71) | ① 부품 정격 판정(주변 40 °C 환산: LED Tj ≤ 125 °C = 145 − 20 K, SoC ≤ 85 °C = SG2002 권장 하단, 안 공기 ≤ 25 K)을 필수로, ② M-003 2차 계산값 × 1.25(analysis2의 25% 여유)를 모델 대조로 | 계산은 가정이 많아 단독 합격선으로 쓰기 어렵고, 정격만 보면 모델 오류를 놓친다 | 정격 여유를 줄임(LED 135 °C, SoC 105 °C) — 사용자 결정 |

## 12. F-006 이미지 빌드 기록 (O-70 ethtool)

| 단계 | 명령 | 종료 코드 | 결과 |
|---|---|---|---|
| 패치 | `firmware/patches/reCamera-OS/0003-openhw-ethtool.patch` — `external/buildroot/configs/cvitek_CV181X_musl_riscv64_defconfig`에 `BR2_PACKAGE_ETHTOOL=y` 한 줄 추가. 빌드 때마다 `setenv.sh`가 이 defconfig로 buildroot를 다시 설정한다 | — | — |
| 적용 | `bash firmware/scripts/apply-f004.sh` (→ `apply-f003.sh`: 0001·0002는 표시 파일로 건너뛰고 0003만 적용) | 0 | `apply-f006-1.log` |
| 빌드 | hc 칸 `openhw-fw-build`, `CPUSET=0-3 MEM=16g JLEVEL=4 slot --label F-006 --timeout-min 240 -- build-baseline.sh build` | **0** | 455초, 02:40:47 KST 종료 · `f006-build-1.log` |
| collect | `OUT_DIR=…/out-f006 build-baseline.sh collect` | 0 | 아래 해시 |

| 파일 (`out-f006/`) | 크기 (B) | sha256 |
|---|---|---|
| `sg2002_reCamera_0.2.4_emmc.zip` (= `upgrade.zip`) | 153,022,474 | `1553210f338a0d1c0934605acac29c651c812f7b1c6eb3da2f2ef142a502b168` |
| `sg2002_reCamera_0.2.4_emmc_ota.zip` | 151,811,291 | `3b66f1cf570324b42cccf582c658d8dfa26673edeee708bc15776925cda08676` |
| `sg2002_reCamera_0.2.4_emmc_recovery.zip` | 611,823 | `2408d6257431fb51d44be1ce2de9e001cd16f5b22865cad63264f86e508131bc` |
| `sg2002_reCamera_0.2.4_emmc_sd_compat.zip` | 148,453,409 | `15bd3e5747fe89780880bd329d27441ac72e3a0f43e262838bd4c8394838cd39` |
| `sg2002_reCamera_0.2.4_emmc_swu.zip` | 148,443,255 | `391502a4fa23917c86d715d8e4cc7ba9193846d08a515c7aef67b170afd45ee8` |

**rootfs 확인** (`debugfs`, `rootfs_ext4.emmc`):
- `/usr/sbin/ethtool`: 380,144 B, RISC-V musl ELF. buildroot `ethtool-5.10`, `BR2_PACKAGE_ETHTOOL_PRETTY_PRINT=y`가 따라 켜졌다.
- 모델 `yolox_nano_person_416_bf16_cv181x.cvimodel` sha256 `eee83a22…`. F-004c와 같다.

**크기 증가 (F-004c → F-006):**

| 항목 | F-004c | F-006 | 증가 |
|---|---|---|---|
| buildroot `target/` | 433,840,472 B | 434,244,728 B | **+404,256 B (약 395 KiB)** |
| rootfs 빈 블록 (1 KiB, 전체 520,192) | 63,562 | 63,169 | 사용 +393 KiB. 남은 여유 약 61.7 MiB |
| `emmc.zip` | 151,408,636 B | 153,022,474 B | +1,613,838 B |

- `emmc.zip` 증가가 rootfs 증가보다 크다. 원인은 확인하지 않았다. 추정으로는 같은 빌드에서 sscma-node·daynight를 dirclean 뒤 다시 빌드해 압축 대상 바이트가 바뀐 것이 섞였다.
- **HIL 미확인:** 이 EPHY 드라이버가 `ethtool -s`(속도 강제·광고 제한)를 받는지 확인하지 않았다(6절).

## 13. PC 쪽 도구 (F-007, `firmware/tools/host/`)

- 모두 Python 3 표준 라이브러리만 쓴다. 외부 명령은 `ffprobe`·`ffmpeg`(① 도구)과 `mosquitto_sub`(② 직접 구독)이다.
- 장치의 1883은 루프백 전용이다(D-003 #30). 그래서 이벤트·invoke는 **ssh 파이프 + `--stdin`**으로 받는다.
- **설치 (F-008, 사용자 허가 2026-11-27 · orch O-79):** ffmpeg/ffprobe만 설치했다.
  - 위치: `C:/Users/gh/tools/ffmpeg/9.0.2/ffmpeg-9.0.2-essentials_build/bin/` (`ffmpeg.exe`·`ffprobe.exe`·`ffplay.exe`).
    - 사용자 홈 아래 격리 설치이고, PATH·시스템 설정은 바꾸지 않았다.
    - 받은 zip은 빈 폴더 `C:/Users/gh/tools/ffmpeg/_download-9.0.2/`에 두었다.
  - 배포처: ffmpeg.org 다운로드 페이지(https://ffmpeg.org/download.html)가 링크하는 gyan.dev Windows 빌드.
  - 버전: **9.0.2 essentials** — `https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-9.0.2-essentials_build.zip`.
    - 서버 Last-Modified: 2026-09-19 07:10:16 GMT. 공개된 지 2주를 넘겼다.
    - 최신 9.1(2026-11-20)은 2주가 안 돼서 쓰지 않았다.
  - zip sha256 `60f467265b1e312373dbcd92200c2618a74850f98d3d078e94296bb3fa2047ba`. 배포처 공개값(같은 URL + `.sha256`)과 **일치**한다.
  - 압축 푼 실행 파일 sha256:
    - `ffmpeg.exe`: `3256173f3f8bffd7df12227c68adf68025edb1832273a9530688a7bb1ed8edec`
    - `ffprobe.exe`: `f0d36ecbbdd3bcfac3efa078c96c7271c2e68b3810595552ac3b7f17e9a65c52`
    - `ffplay.exe`: `befbbd00a25965365f7fb3eed6ad5aa5f805eb70fabc567883a006de3b26c06f`
  - 압축 해제 전 zip 안의 경로를 검사했다(절대경로·`..` 0건, 49개).
  - **쓰는 법:** PATH를 바꾸지 않는다. 다음 둘 중 하나로 bin 폴더를 준다.
    - `rtsp_check.py --ffmpeg-dir C:/Users/gh/tools/ffmpeg/9.0.2/ffmpeg-9.0.2-essentials_build/bin <하위 명령> …` (하위 명령 앞에 둔다)
    - 환경 변수 `OPENHW_FFMPEG_DIR`
    - 둘 다 없으면 PATH를 본다.
  - **설치하지 않은 것:**
    - OpenSSH 클라이언트: Windows 내장 `C:\Windows\System32\OpenSSH\ssh.exe`가 있다.
    - `mosquitto-clients`: 장치 1883이 루프백 전용이라(D-003 #30) PC에서 직접 구독하지 않고 `event_log.py record --stdin`(ssh 파이프)을 쓴다. 필요해지면 다시 결정한다.
- **Windows Git Bash에서는** 한글 출력이 깨지므로 `PYTHONIOENCODING=utf-8`을 붙인다(PowerShell은 그대로 된다). 판정은 종료 코드라 영향이 없다. 이 PC에서 `rtsp_check.py probe`(파일)와 `current_csv.py` 스모크 시험은 rc 0이었다.

| 도구 | 하는 일 | 종료 코드 | 절차서 |
|---|---|---|---|
| `rtsp_check.py probe <URL\|파일> [--seconds 20] [--expect-fps 15] [--max-gap 0.5]` | 비디오 패킷 pts로 FPS·최대 간격을 잰다. URL이면 첫 패킷부터의 실시간 비율도 본다. 비밀번호는 출력에서 가린다 | 0 합격 · 1 기준 미달 · 2 수신 실패 | 3-2, 1-9 |
| `rtsp_check.py record <URL> <out.mkv> [--seconds 60]` | `-c copy` 녹화 | 0 · 2 | 1-9 |
| `rtsp_check.py latency <URL> <out.png>` | 프레임 1장 + PC 수신 시각(`.txt`). 비교는 사람 눈 | 0 · 2 | 3-2 |
| `event_log.py record (--stdin \| --host H --port P) [--topic T] [--seconds N] -o x.jsonl` | 줄마다 `{"rx", "topic", "msg"}`로 기록한다 | 0 | 4-3, 4-4 |
| `event_log.py check x.jsonl [--cooldown-ms 30000] [--min-score 0.5]` | 필드 누락 · 모르는 event · 등장 중 등장 · 없는데 퇴장 · 쿨다운 위반 · ts 역행 · 낮은 score · count < 1 | 위반 수 · 이벤트 0건 = 2 | 4-3 |
| `fps_stats.py inv.jsonl [--cam-fps 15] [--min-fps N]` | FPS(count 증가 ÷ 수신 시간), MQTT 누락, perf pre/inf/post 평균·p50·p95·최대 | 0 기록 · 1 `--min-fps` 미달 · 2 invoke < 2 | 4-4 |
| `current_csv.py log.csv [--window-min 30] [--limit 1.9] [--adapter 2.08]` | 평균, 피크, 30분 창 평균 최댓값(시간 가중). 열·단위는 자동으로 찾는다(mA) | 0 ≤ 1.9 A · 1 넘음 · 2 짧음/형식 | 1-9 |

**사전 시험 (하드웨어 없이, `firmware/tools/host/test_host_tools.sh`):**
- recamera-os-builder 컨테이너에서 `ffmpeg`·`mosquitto`·GStreamer RTSP 서버를 apt로 설치해 돌린다.
- 네트워크는 127.0.0.1만 쓴다: 가짜 RTSP(videotestsrc 720p 15fps, `:8554`), mosquitto(`:18830`).
- 판정: 시험 20건(R1~R8 · E1~E4 · F1~F3 · C1~C5)의 종료 코드를 기대값과 맞춘다. 고장 주입(30fps 기대, 서버 없음, 5fps 파일, 1초 끊김, 위반 4건 이벤트, 낮은 score, FPS 하한, 30분 미만, 뒤 30분만 2.0 A)을 포함한다.
- 스크립트 종료 코드 = 기대와 다른 시험 수.

**F-008 시험 (격리 설치한 ffmpeg 9.0.2)**
- Windows 호스트 스모크: PATH에서 다른 ffmpeg 경로를 빼고 돌렸다(설치본만 쓰는지 확인).

| # | 명령 | 종료 코드 | 결과 |
|---|---|---|---|
| S0 | `rtsp_check.py probe src.mkv` (폴더 지정 없음) | 1 (기대) | `ffprobe 없음 — --ffmpeg-dir 또는 OPENHW_FFMPEG_DIR …` |
| S1 | `rtsp_check.py --ffmpeg-dir <bin> probe src.mkv --expect-fps 15` | 0 | 720p 15fps 6초 파일: fps 15.00 · max_gap 0.067 s |
| S2 | `OPENHW_FFMPEG_DIR=<bin> rtsp_check.py record src.mkv rec.mkv --seconds 4` | 0 | — |
| S3 | `… probe rec.mkv --expect-fps 15` | 0 | fps 14.30 · max_gap 0.267 s |
| S4 | `… probe src.mkv --expect-fps 30` (고장 주입) | 1 (기대) | fps 15 < 27 |

- 컨테이너 `test_host_tools.sh` 재실행(2026-11-27 04:10)은 **돌리지 못했다**.
  - 메시지: `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine`
  - Docker Desktop 프로세스가 없다. 이 칸이 끈 것이 아니다.
  - 다른 프로젝트도 함께 쓰는 환경이라, 이 칸이 켜지 않고 orch에 보고했다.
  - 이 시험은 컨테이너 안의 apt ffmpeg를 쓰므로 F-008 설치와는 무관하다. `rtsp_check.py` 변경(`--ffmpeg-dir`)만 다시 확인하면 된다.
  - 마지막 통과 기록: F-007, 20/20, 종료 0.
- **재실행 완료 (2026-11-27 04:19~04:21):** lead 결정(Docker 켠 상태 유지, OpenHW 컨테이너만)에 따라 `docker run --rm --memory 4g recamera-os-builder bash /fw/tools/host/test_host_tools.sh`를 돌렸다. F-008 레인 firmware를 읽기 전용으로 붙였다.
  - 결과: **20/20 기대 일치, 종료 0** (`recamera-sdk/f007-test-5.log`). `--ffmpeg-dir` 변경을 포함한 판이다.
  - 컨테이너는 `--rm`으로 정리했고, 다른 프로젝트 컨테이너는 건드리지 않았다.


## 14. F-010 이미지 빌드 기록 (O-89 — vo 노드 gpio 속성 삭제)

- **변경:** 새 패치 `firmware/patches/reCamera-OS/0004-openhw-vo-gpio.patch`가 보드 DTS `sg2002_recamera_emmc.dts`에 `&vo { /delete-property/ reset-gpio; pwm-gpio; power-ct-gpio; }`를 넣는다.
  - 원본 `cv181x_base.dtsi` L758–760의 `vo` 노드는 porte 0/1/2를 참조한다. porte 0 = gpio352 = ICR IN2, porte 1/2 = IIC2 SCL/SDA 패드다.
  - 보드 DTS는 원래 `&mipi_tx`의 같은 세 속성만 지우고 있었다.
  - **분기점:** orch는 "패치 0001에서 삭제"라고 지시했다. 그러나 `apply-f003.sh`는 적용한 패치를 이름 표시 파일로 건너뛴다. 0001을 고치면 빌드 볼륨에 다시 적용되지 않는다(F-004c 원인 M). 그래서 새 패치 0004로 했다. 새 볼륨에서도 0001 → 0004 순서로 적용된다.

| 단계 | 명령 | 종료 코드 | 결과 |
|---|---|---|---|
| 적용 | `bash firmware/scripts/apply-f004.sh` (0001~0003 건너뜀, 0004 적용) | 0 | `apply-f010-1.log` |
| 빌드 | hc 칸 `openhw-fw-build`, `CPUSET=0-3 MEM=16g JLEVEL=4 slot --label F-010 --timeout-min 240 -- build-baseline.sh build` | **0** | 504초, 05:33:08 KST 종료 · `f010-build-1.log` |
| collect | `OUT_DIR=…/out-f010 build-baseline.sh collect` | 0 | 아래 해시 |
| dtb 역컴파일 (커널·u-boot dtb 둘 다, `dtc -I dtb`) | `vo`·`mipi_tx` 노드의 reset/pwm/power-ct-gpio 개수, porte(phandle 0x0f) 참조 | — | **vo 0 · mipi_tx 0 · porte 참조 0** |
| 호스트 시험 (`run-hosttest-f010.sh`, 컨테이너 `--memory 2g`) | daynight · persond 단위 · 통합 · `test-bringup-check.sh` | 0 · 0 · 0 · 0 | 40/0 · 33/0 · 16/0 · 불일치 0 |

| 파일 (`out-f010/`) | sha256 |
|---|---|
| `sg2002_reCamera_0.2.4_emmc.zip` (= `upgrade.zip`) | `a275afb12988a2185640ccf0417983a67e11925fafc3ce7ad598e48e59bda134` |
| `sg2002_reCamera_0.2.4_emmc_ota.zip` | `2856fe4087182861cb3c0db57dc10b7c4bb14a8d36aa18b3385663c217eeba25` |
| `sg2002_reCamera_0.2.4_emmc_recovery.zip` | `3dd2d5c66da10e764e0213460de76305590a124b34d2a6730f0eb7076d9e1df7` |
| `sg2002_reCamera_0.2.4_emmc_sd_compat.zip` | `38d71b1cb275a437e2ceabf3e4e554eee18cf1b36369da7a396545bac0322b48` |
| `sg2002_reCamera_0.2.4_emmc_swu.zip` | `abd49e85c5b5aef2c90355c67a4349766a70abb15ab542befa4bba838bc723f5` |

- **HIL 미확인:** 보드에서 `cat /sys/kernel/debug/gpio`로 gpio352~354를 아무 드라이버도 잡지 않는지 본다. 이것은 bring-up 2-5 때 함께 본다.
