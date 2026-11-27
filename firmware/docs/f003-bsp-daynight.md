# F-003 계약 v1.8 기준 BSP 변경과 주야 전환·조도 앱

- 배정: orch t18r F-003 · 작성: firmware t18w · 레인 t-20261126-203052-0734 (F-002 레인 t-20261126-161240-92e6에서 이어 시작) · 날짜 2026-11-26
- 입력:
  - 계약 C-001 **v1.8** (`2dde4a2`): 6절 I2C, 7절 GPIO, 8절 DTS, 12A절, 14절
  - 회로도 기준 `c653eac`
  - F-001 `sdk-facts.md`, F-002 `build-baseline.md`
  - O-31, O-33(V-004 K1), V-004b R2, P-003(`9355bd1`)
- **결과:** 패치를 적용한 빌드가 **종료 코드 0**으로 끝났다. 호스트 시험은 **37개 통과·0개 실패**다.
- **판정 범위:** 보드가 없어 **HIL은 미검증**이다. 이 문서의 판정은 컴파일·패키징 성공과 이미지 안의 내용 확인까지이며, 실물 동작을 뜻하지 않는다.

## 1. 산출물 (파일)

| 경로 | 내용 |
|---|---|
| `firmware/patches/reCamera-OS/0001-openhw-carrier-bsp.patch` | DTS·보드 초기화(핀먹스) 변경, br2-external 패키지 `openhw-daynight` 등록 |
| `firmware/patches/sscma-node/0001-openhw-orient-daynight-pqbin.patch` | 카메라 앱 sscma-node 0.2.3 패치: GC2053 mirror+flip 기본 켬(설정으로 끔), `/run/daynight/mode`에 따라 ISP PQ bin(sdr ↔ sdr_ir) 전환 |
| `firmware/apps/daynight/` | 주야 전환 데몬. `daynight.c`가 하드웨어를 다루고 `daynight_logic.[ch]`는 순수 로직이다. 그 밖에 `test_logic.c`(호스트 시험), `Makefile`, `daynight.conf`, `S96daynight` |
| `firmware/scripts/apply-f003.sh` | 빌드 볼륨에 패치·앱을 넣고 해당 패키지를 dirclean한다. 다시 돌려도 된다 |
| `firmware/.gitattributes` | 패치·셸·C 파일의 줄끝을 LF로 고정한다. 이 저장소는 `core.autocrlf` 경고가 나는 환경이다 |

## 2. BSP 변경 (계약 8절 대조)

| 계약 8절 항목 | 변경 | 확인 (빌드 산출물) |
|---|---|---|
| `leds/led0 red` porta 15 heartbeat | 삭제. gpio495는 ICR IN1로 쓴다 | dtb 3개(linux·u-boot·ramdisk)를 `dtc`로 풀어 `heartbeat` 0건 |
| `leds/led2 white` porte 0 | 삭제. gpio352는 ICR IN2로 쓴다 | 같음 |
| `leds/led1 blue` porte 24 + `PINMUX_CONFIG(GPIO_ZQ, PWR_GPIO_24)` | LED 삭제, 핀먹스를 **`PWM_2`**로(`GPIO_ZQ__PWM_2 = 4`, 핀 기능표) | dtb 확인. u-boot `board.o`(11:39:58 UTC)가 패치된 `cvi_board_init.c`(11:39:31)보다 나중에 컴파일됐다 |
| `&i2c1/adc@48` ti,ads1015 | 노드 삭제. i2c1은 okay로 남긴다(예비) | dtb `ads1015` 0건 |
| `&spi0/mcp2518fd` | 삭제, spi0 disabled, `mcp2518fd_osc` 삭제 | dtb `mcp2518fd` 0건 |
| `&sd/mm610x-sdio` | 삭제 | dtb `mm610x` 0건 |
| `wifi_pin` porta 30 | 삭제. gpio510은 UPGRAD_KEY 입력 | dtb `wifi_pin` 0건 |
| 새 핀먹스 | `PAD_MIPI_TXM0/TXM1/TXP1 → XGPIOC_12/14/15` (STATUS_LED·SPARE1·IR_LED_EN) | 소스와 `board.o` 시각 |
| (계약 7절) STATUS_LED | `gpio-leds` `status` = `&portc 12 GPIO_ACTIVE_HIGH`, `default-state = "off"` | dtb 3개에 `status_led` 있음 |

- 그대로 둔 것: CAM_EN(`S70hardware`), SD0_PWR_EN·CD, IIC2, UART1 핀먹스, `&wifisd`. `&wifisd`는 계약 8절 목록에 없어 손대지 않았다.

## 3. 주야 전환 데몬 `openhw-daynight` (`/usr/bin/daynight`, `/etc/init.d/S96daynight`, `/etc/openhw/daynight.conf`)

| 규칙 | 구현 위치 | 호스트 시험 |
|---|---|---|
| LTR-329를 i2c-2 0x29에서 i2c-dev로 폴링 (D-003 #18, 계약 6절) | `ltr_open` / `ltr_read_lux`. MEAS_RATE 0x85 = 0x03(100ms/500ms), ALS_CONTR 0x80 = 0x01(active, 1x). 0x88부터 4바이트를 CH1 → CH0 순서로 읽는다 | lux 식 4건 |
| 히스테리시스 | `dn_hyst_update`: 낮→밤은 `lux < night_lux`(5)가 `samples`(3)회 연속, 밤→낮은 `lux > day_lux`(20)가 3회 연속. 경계값은 전환하지 않는다 | 7건 |
| ICR(DRV8837) IN1 gpio495 / IN2 gpio352, 펄스 100~500ms 후 0/0 코스트 | `icr_pulse`. 펄스 폭은 설정해도 100~500으로 강제한다. 방향은 `icr_night_in1`(실물 극성 확인 전 — 계약 14절 실물 4) | 펄스 강제 2건 |
| **IR_PWM 극성 v1.5: High = 끔 · Hi-Z = 끔 · Low = 켬** | Linux `duty_cycle`(High 시간) = 주기 × (1 − 켬 비율) — `dn_pwm_duty_ns` | 2건 |
| **켬 비율(Low) ≤25% 강제 (O-31)**, ≤500Hz | `dn_clamp_on_ratio`, `dn_config_finalize`, `dn_pwm_duty_ns`. 설정이 1.0이어도, 음수·NaN이어도 0.25 이하로 된다 | 전 범위(주파수 1~2000Hz × 요청 0~100%) 검사 포함 7건 |
| **IR_LED_EN을 올리기 전에 IR_PWM High (O-33)** | `dn_plan`: 밤 = ICR_NIGHT → IR_PWM_OFF → IR_EN_ON → IR_PWM_SET → ISP_NIGHT / 낮 = IR_PWM_OFF → IR_EN_OFF → ICR_DAY → ISP_DAY. 시작할 때는 PWM을 High로 켠 뒤 낮 상태를 적용하고, 끝날 때는 PWM High → EN 0 | 순서 5건 |
| **LTR-329는 CAM_EN=1일 때만 폴링 (O-33)**, **CAM_EN 켠 뒤 ≥5ms (V-004b R2)** | `dn_may_poll`. CAM_EN(gpio358)은 읽기만 한다. 0→1로 바뀌는 시각을 기록하고, CAM_EN이 0이 되면 i2c fd를 닫았다가 다시 초기화한다(LTR-329 전원은 CAM_1V8) | 4건 |
| ISP IR 모드(sdr_ir) | 데몬은 `/run/daynight/mode`(`day`/`night`)를 rename으로 원자적으로 쓴다. ISP 파라미터는 카메라 앱 프로세스 안에 있으므로, sscma-node 패치의 스레드(`OPENHW_DN`, 500ms 주기)가 `CVI_BIN_ImportBinData`로 `/mnt/cfg/param/gcore_gc2053_sdr_ir.bin` ↔ `gcore_gc2053_sdr.bin`을 다시 읽는다 | — (실물) |
| 차선 LIGHT_SENSE ADC1 | `als_source = adc`, `adc_path`, `adc_lux_per_count`. ADC 드라이버 경로는 미확인이다. `cv181x_saradc.ko`는 rootfs에 있지만 부팅 때 읽어 들이지 않는다 | — |
| PWM 드라이버 로드 | `loadsystemko.sh`가 `cv181x_pwm.ko`를 읽어 들이지 않는다(rootfs 확인) → `S96daynight`가 `insmod /mnt/system/ko/cv181x_pwm.ko` | — |
| 노출 동기 펄스(O-31 허용) | 구현하지 않았다(허용 사항일 뿐 필수가 아님) | — |

- **영상 반전 (P-003):** sscma-node 패치가 GC2053의 `u8Orien`을 `ISP_SNS_MIRROR_FLIP`으로 바꾼다. 이 값은 VI 채널의 `bMirror`·`bFlip`에 들어간다. `/etc/openhw/daynight.conf`에 `isp_mirror_flip = 0`이 있으면 `ISP_SNS_NORMAL`이 된다. 실제로 180° 맞는지는 bring-up에서 확인한다.

## 4. 시험·빌드 결과

| 무엇 | 명령 | 종료 코드 | 결과 |
|---|---|---|---|
| 호스트 단위 시험 | `docker run recamera-os-builder … make test` (x86 gcc, `-Wall -Wextra -Werror`) | 0 | `pass=37 fail=0` |
| 데몬 호스트 컴파일 | `make daynight` (같은 플래그) | 0 | 경고 0 |
| 패치 적용 | `bash firmware/scripts/apply-f003.sh` (3회, 다시 돌려도 됨) | 0 | — |
| 패치 적용 빌드 1 | hc t197: `CPUSET=0-3 MEM=16g JLEVEL=4 slot --label F-003 --timeout-min 240 -- build-baseline.sh build` | **2** | 원인 F(아래) |
| 패치 적용 빌드 2 | hc t198, 같은 명령 | 0 | 342초. 이후 PWM 모듈 로드를 추가해야 해서 다시 빌드 |
| **패치 적용 빌드 3 (최종)** | hc t199, 같은 명령 | **0** | 338초, 20:59:11 KST 종료 |
| collect | `OUT_DIR=…/out-f003 slot -- build-baseline.sh collect` | 0 | 아래 해시 |

### 최종 산출물 (`%USERPROFILE%/.local/share/openhw-tools/recamera-sdk/out-f003/`)

| 파일 | sha256 |
|---|---|
| `sg2002_reCamera_0.2.4_emmc.zip` (= `upgrade.zip`) | `2a7ba77fd6df85f6491a55db1e4a1aa2b181529540e4a27039ef6fd6f5d45d49` |
| `sg2002_reCamera_0.2.4_emmc_ota.zip` | `aee565037c7b880252b49ec331de10f9c5e1e2f5f07d8e7dc911f1a3bbac2c83` |
| `sg2002_reCamera_0.2.4_emmc_recovery.zip` | `fbdb9570c8aa8412ca4dcaf8f30761db13022853d627d20d719f22229f3a1c6e` |
| `sg2002_reCamera_0.2.4_emmc_sd_compat.zip` | `8beda99c1dd383c662619cac3f334c9857f3eb9a54fcb419dda221c47951ff65` |
| `sg2002_reCamera_0.2.4_emmc_swu.zip` | `74d94120bbcd78e0d7ca1d6327a4d82b8d87153e2dd3d61e07d6ac07d74be936` |

- 파일 크기는 `out-f003/`에서 `ls -l`로 본다. F-002 기준선 해시는 `build-baseline.md`에 있다.
- **이미지 안 확인:** 최종 `rootfs.ext4`를 `debugfs`로 열어 확인했다.

| 파일 | 크기 | 확인 내용 |
|---|---|---|
| `/usr/bin/daynight` | 14,816 B | RISC-V ELF |
| `/etc/init.d/S96daynight` | 517 B | `cv181x_pwm` 포함 |
| `/etc/openhw/daynight.conf` | 715 B | — |
| `/usr/local/bin/sscma-node` | 703,456 B | `/run/daynight/mode` 문자열 포함 |
| `/mnt/cfg/param/gcore_gc2053_sdr_ir.bin` | 347,073 B | — |

### 실패 원인 판정
| 원인 | 횟수 | 근거 | 조치 |
|---|---|---|---|
| F. sscma-node 패치의 C 문자열 안에 줄바꿈 | 1 | `f003-build-1.log` 3577행 `isp.c:661: error: unterminated argument list invoking macro "APP_PROF_LOG_PRINT"`. 패치 37행에서 `"…(%#x)` 뒤에 실제 줄바꿈이 있었다(패치를 만든 스크립트의 이스케이프 오류) | 패치를 한 줄로 고치고(`%.5s` + `\n`) hunk 길이를 42 → 41로 바꿨다. 깨끗한 원본에 `patch -p1` 시험 후 빌드 2에서 통과 |

- 빌드 2 → 3은 실패가 아니다. 이미지 검토 중 PWM 모듈이 로드되지 않는다는 것을 찾아 고친 것이다.

## 5. 미확인 (실물·추가 확인)
1. **pwmchip 번호:** `pwm0`(0x3060000) 컨트롤러가 `pwmchip0`이고 채널 2가 PWM_2라고 추론했다. 다르면 `pwm_chip`을 설정한다.
2. **PWM "끔"의 실제 파형:** `cv181x/cvi_pwm.c`는 `duty == period`일 때 `duty_count = period_count − 1`로 만든다. 그래서 전기 High 100%가 정확히 나오지 않고, 주기마다 1 카운트만큼 Low(켬)가 남는다. 400Hz이고 PWM 클록이 100MHz라면 1/250,000이다(클록값은 미확인). 또 `pwm_disable` 때 출력 레벨도 미확인이라 데몬은 PWM을 끄지 않고 duty만 바꾼다. 실물에서 스코프로 확인해야 한다.
3. **portc 베이스 416** (gpio431 = IR_LED_EN, gpio428 = STATUS_LED): `/sys/class/gpio`로 확인 (계약 14절 실물 2).
4. **ICR 극성:** CLA216 코일 극성 ↔ `icr_night_in1` (계약 14절 실물 4).
5. **ISP bin 실행 중 교체:** `CVI_BIN_ImportBinData`를 ISP가 돌고 있는 중에 불렀을 때 IQ가 바로 바뀌는지 확인해야 한다. cv180x `isp_test.c`가 같은 API를 실행 중에 쓰는 선례가 있을 뿐, cv181x에서 확인한 것은 아니다.
6. **I2C2 공유:** sscma-node(GC2053 0x3f)와 데몬(LTR-329 0x29)이 같은 버스를 쓴다. 커널 i2c 어댑터가 접근을 직렬화하지만, 실제 영향은 실물에서 확인한다.
7. **LTR-329 lux 식:** Lite-On 앱노트 계수를 썼다. 보정은 실물에서 한다(창·필터 투과).
8. ADC 차선: `cv181x_saradc.ko` 노출 경로와 채널 번호.

## 6. 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| F3-1 | ISP IR 전환 위치 | sscma-node 패치(같은 프로세스) + 데몬은 모드 파일 | ISP 파라미터는 ISP를 돌리는 프로세스 안에 있다. 다른 프로세스에서 `CVI_BIN_*`를 부르면 반영된다는 보장이 없다(`RPC_MULTI_PROCESS` 빌드 여부 미확인) | 데몬이 cvi_mpi에 직접 링크(멀티프로세스 RPC 확인 후) |
| F3-2 | 데몬 배포 | br2-external 패키지(`default y`, SITE_METHOD local) | SDK 빌드에 자연스럽게 들어가고, 이미지 해시에 반영된다 | 오버레이에 바이너리 넣기 |
| F3-3 | 조도 읽기 | 사용자 공간 i2c-dev 폴링 | 계약 6절(O-9): 5.10에 드라이버가 없고 백포트는 하지 않는다 | 커널 ltr501 백포트 |
| F3-4 | 히스테리시스 기본값 | 밤 < 5 lux, 낮 > 20 lux, 연속 3회, 1초 주기 | 일반 IP 카메라 범위의 보수적인 값이다. 설정으로 바꿀 수 있다 | 실측 뒤 조정 |
| F3-5 | IR PWM 주파수 | 400Hz | ≤500Hz(V-001)에 여유를 둔다 | 200Hz |
| F3-6 | PWM 상시 enable | 켠 채로 duty만 바꾼다 | disable 때 출력 레벨이 미확인이라 Low(켬)가 될 위험이 있다 | 실물 확인 뒤 끄기 |
| F3-7 | mirror+flip 방식 | `u8Orien` → VI `bMirror`/`bFlip` | 앱에 이미 있는 경로이고 설정 파일로 끌 수 있다 | 센서 레지스터 반전 |
| F3-8 | STATUS_LED | gpio-leds `status`, 기본 끔 | 계약 7절(Low = 끔)대로 | 데몬이 직접 제어 |

## 7. 볼륨 상태
- 볼륨 `openhw-recamera-sdk`의 소스에는 이제 F-003 패치가 적용돼 있다. F-002 기준선 산출물은 `out-0.2.4/`에 따로 보관돼 있다.
- 원본으로 되돌리려면 `/work/src`에서 `patch -R -p1 < 0001-openhw-carrier-bsp.patch`를 하고, `external/br2-external/openhw-daynight`와 sscma-node 패치 파일을 지운 뒤 다시 빌드한다.
