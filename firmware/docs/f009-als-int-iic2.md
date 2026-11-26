# F-009 ALS_INT GPIO 사용 제거 · IIC2 내부 풀업 확인

- 배정: orch O-83 (F-009) · O-87 (계약 v1.13 FW 규칙 "IIC2 내부 풀업 켜지 않음") · 작성 firmware t18w · 레인 `t-20261127-050450-28b0` (main `45fa2be`) · 2026-11-27
- **결론:**
  - **ALS_INT_RSV(PWR_WAKEUP1 = PWR_GPIO_8 = gpio360)를 쓰는 FW는 없다.** DTS 패치, daynight, persond, 이미지 dtb, init 스크립트 모두 확인했다. 그래서 고칠 코드가 없다.
  - **IIC2(PWR_GPIO1/2) 내부 풀업은 어디서도 켜지 않는다.**
  - 호스트 시험을 다시 돌렸고 모두 종료 0이다.
- 판정 범위: 소스·빌드 산출물만 확인했다. 실물 확인은 bring-up 3-6에서 한다.

## 1. ALS_INT_RSV 사용처 확인

| 대상 | 방법 | 결과 |
|---|---|---|
| `firmware/**` (patches·apps·scripts·tools) | `grep ALS_INT\|gpio360\|PWR_BUTTON1\|PWR_WAKEUP1\|porte 8` | 0건. 패치 0001의 `porte 8`은 원본 DTS `wifi_pin` 노드 안의 주석 줄 `/*wakeup-gpio = <&porte 8 …>;*/`인데, 노드를 지우면서 함께 지워진다 |
| 이미지 dtb (`linux_5.10/build/…/sg2002_recamera_emmc.dtb`, F-006 빌드) | `dtc -I dtb` 후 `*-gpio(s)` 속성 전부 | porte(gpio-controller@4, phandle 0x0f)를 참조하는 것은 `vo` 노드의 0·1·2번뿐이다(아래 3절). porte 8은 없다 |
| init 스크립트 (`S70hardware`·`S96daynight`·`S97persond`·`S91sscma-node`·`S99user`), `loadsystemko.sh` | `debugfs cat` 후 `360\|devmem\|PWR_GPIO\|pull` | 0건 |
| daynight | `GPIO_IR_EN 431`·ICR 495/352·CAM_EN 358(읽기)만 쓴다 | ALS 입력은 i2c-dev 폴링뿐이다. INT 핀은 쓰지 않는다 |

- 그래서 회로에서 ALS_INT_RSV를 지워도(schematic 쪽 결정) FW는 바꿀 것이 없다.
- bring-up 절차서 0절의 캐리어 TP26 `ALS_INT_RSV` 표기는 회로도가 바뀐 뒤 그 판에 맞춰 고친다(지금 main 회로도에는 아직 있다).

## 2. IIC2 내부 풀업 (계약 v1.13 FW 규칙, SIM-001b B6 민감도: 켜면 꺼진 센서로 11.8 µA)

| 위치 | 근거 | 결과 |
|---|---|---|
| u-boot 보드 초기화 | `cvi_board_init.c` L12–13 `PINMUX_CONFIG(PWR_GPIO1, IIC2_SCL)` · `(PWR_GPIO2, IIC2_SDA)`. 매크로(`board.c` L59–62)는 `PINMUX_BASE + FMUX_GPIO_FUNCSEL_*`의 기능 선택 3비트(mask 0x7)만 쓴다 | 패드 풀 레지스터(RTCSYS_IO 0x05027000 영역, PU/PD = 비트 2·3)에는 쓰지 않는다 |
| 커널 DTS (이미지 dtb) | `i2c@…` (i2c2) 노드에 `pinctrl`·`bias-*` 속성이 없다 | 쓰지 않음 |
| 패치 0001 | IIC2 관련 변경 없음 | — |
| 런타임 (init·데몬) | `devmem`·풀 설정 0건 | — |

- 따라서 패드는 리셋 기본값인 **PD**로 남는다. 근거는 `04_SG2002_PINOUT.xlsx` V0.1 "管腳默認狀態"(PWR_GPIO1/2 = PD)다. SIM-001b B6의 기본 조건과 같다.
- **남는 위험:**
  - 기본값은 V0.1 핀 시트로만 확인했다.
  - 실물 패드 레지스터 주소(PWR_GPIO1/2 IO 제어 오프셋)는 SDK·TRM 텍스트에서 찾지 못했다.
  - 그래서 bring-up 3-6에서 **전기적으로** 확인한다. CAM_EN = 0일 때 SDA/SCL이 0 V 근처이면 PD이고, 풀업이 켜져 있으면 수백 mV 이상이다.

## 3. 덤으로 찾은 것 (F-009 범위 밖 — 고치지 않음, orch 판단)

- **이미지 dtb의 `vo` 노드에 원본 Seeed 속성이 남아 있다:**
  - `reset-gpio = <porte 2 …>`, `pwm-gpio = <porte 0>`, `power-ct-gpio = <porte 1>`
  - porte 0 = gpio352 = **우리 ICR IN2(WH_PWM)**
  - porte 1·2 = gpio353·354 = **IIC2 SCL·SDA 패드**
- **지금은 쓰이지 않는다:**
  - 이 속성을 읽는 코드는 `osdrv/interdrv/vo/chip/cv181x/vo_mipi_tx.c`(L655–698 `devm_gpio_request_one`)뿐이다.
  - 그 모듈 `cv181x_mipi_tx.ko`는 `loadsystemko.sh`에서 주석 처리되어 있다(`#insmod …mipi_tx.ko`).
  - 게다가 그 모듈은 `vo` 노드가 아니라 `mipi_tx` 노드(이 속성 없음)에 붙는다.
- **잠재 위험:** 누군가 mipi_tx/패널 드라이버를 켜면 ICR IN2와 I2C 패드를 GPIO로 잡는다.
- **제안:** 패치 0001에서 `vo` 노드의 세 속성을 지운다. 회로 변경 없이 FW만 고치면 된다. 배정이 오면 한다.

## 4. 시험 (호스트, `recamera-os-builder` 컨테이너 `--memory 2g`, 로그 `recamera-sdk/f009-hosttest-1.log`)

| 시험 | 종료 코드 | 결과 |
|---|---|---|
| daynight `make test` | 0 | pass=40 fail=0 |
| persond `make test` | 0 | pass=33 fail=0 |
| persond `test_integration.sh` | 0 | pass=16 fail=0 |
| `firmware/scripts/test-bringup-check.sh` | 0 | 문법 3종 0, shellcheck 0, 불일치 0 |

## 5. bring-up 절차서 추가 (`bringup-checklist.md`)

- **3-6:** CAM_EN = 0일 때 IIC2 SDA/SCL 전압으로 내부 풀업이 꺼져 있는지 확인한다(이 문서 2절).
- **5-9:** SIM-001b S3(끔 구간 링잉, 기준 그대로 불합격)을 실물로 확인한다. IR 끔 상태의 광출력과 LED 전류를 잰다(O-87).
