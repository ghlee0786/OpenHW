# F-001 reCamera Core 2002 (SG2002) SDK 사실 정리

- 배정: orch t18r F-001 (README 단계 3 HW/FW 계약용) · 작성: firmware t18w · 레인 t-20261126-155208-b6b4
- 대상: Seeed reCamera Core 2002 8GB, 무선 없음 (SKU 101991223, orch O-2) · 센서 GC2053 잠정 (O-3)
- 확인일: **모두 2026-11-26** · 방법: 공개 웹·GitHub 파일 읽기만. SDK 내려받기·빌드·실행 없음
- 표기: **확인됨** = 원문 파일·문서를 직접 읽음 · **추론** = 확인된 근거를 조합한 결론 · **미확인** = 찾지 못함 또는 검색 요약뿐
- 컴파일·실물 동작은 하나도 검증하지 않았다. 보드가 없어서 **HIL은 미검증**이다.

## 기준 커밋

| 저장소 | 브랜치/태그 | 커밋 | 커밋일 |
|---|---|---|---|
| https://github.com/Seeed-Studio/reCamera-OS | `sg200x-reCamera` HEAD | `0529ca0a8bc6b6b88a70c8b15e40d77c9e01cb82` | 2026-11-04 |
| 〃 릴리스 | 0.2.6 (prerelease, 2026-11-02, `fa2a903f`) · 0.2.5 (prerelease, 2026-10-26) · **0.2.4 (정식, 2026-03-23, `01debc99`)** | — | — |
| https://github.com/Seeed-Studio/OSHW-reCamera-Series | `main` | `f5fcf0abce794806ffbd7a274686f022bb0acd4b` | 2026-09-18 |
| https://github.com/sophgo/linux_5.10 (서브모듈) | sg200x-dev | `d0486a96f7e8756c663acbc6a57371360f38871f` | 2025-08-04 |
| https://github.com/sophgo/u-boot-2021.10 | 〃 | `050d49a7b19289407c9f9998e16869c97ced891c` | 2025-08-04 |
| https://github.com/sophgo/buildroot-2021.05 | 〃 | `5b7acd1bf99574b818f9ec1f61232c69f6150202` | — |
| https://github.com/sophgo/build | 〃 | `85f705b17cfce87c82020786ba8a7fce5299e4ac` | — |
| https://github.com/sophgo/SensorSupportList | 〃 | `86b0708e0101dfd4b60abafe98fef28c92773dbb` | — |
| https://github.com/sophgo/cvi_mpi | 〃 | `6dbbbb8bed877cd3a08f76ce4aed61645c38bbe1` | — |
| https://github.com/sophgo/isp_tuning | 〃 | `f7b23013ad67d902fa8ad03eb6d6f68c96717d0b` | — |
| https://github.com/Seeed-Studio/sscma-example-sg200x (reCamera 앱) | main | `4926df702acba990b2ebd36a086f171a7964466e` | 2026-10-22 |
| https://github.com/sophgo/tpu-mlir | v1.30.2 (2026-08-31) · master | `41d7a05e52df442edf8425dcee8c050fc77c598e` | 2026-11-16 |
| https://github.com/milkv-duo/duo-buildroot-sdk-v2 (참고) | — | `6f8962c394dd0a05729abb089f0feb7d5cc4aa5e` | 2025-11-04 |

아래 표의 약어: **RC** = reCamera-OS `0529ca0a` · **OSHW** = OSHW-reCamera-Series `f5fcf0ab` · **SC** = sscma-example-sg200x `4926df70` · **SS** = SensorSupportList `86b0708e`

## 1. 항목별 사실

### 1.1 저장소·버전·커널

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| SDK 구성 | reCamera-OS가 sophgo/* 서브모듈을 대부분 `sg200x-dev` 브랜치로 가져온다: host-tools, build, fsbl, opensbi, u-boot-2021.10, linux_5.10, osdrv, cvi_mpi, isp_tuning, SensorSupportList, cviruntime, tdl_sdk, buildroot-2021.05, freertos 등. Seeed 수정분은 `external/` 아래에 있다 | RC `.gitmodules` | 확인됨 |
| 커널 | **5.10.4** (Makefile VERSION 5 · PATCHLEVEL 10 · SUBLEVEL 4). 0.2.4 태그도 같은 SHA | https://raw.githubusercontent.com/sophgo/linux_5.10/d0486a96f7e8756c663acbc6a57371360f38871f/Makefile | 확인됨 |
| u-boot | 2021.10 | sophgo/u-boot-2021.10 `050d49a7` Makefile | 확인됨 |
| Buildroot | 2021.05 (`BR2_VERSION`) | sophgo/buildroot-2021.05 `5b7acd1b` Makefile | 확인됨 |
| 보드 설정 이름 | `sg2002_recamera_emmc` (그 밖에 `sg2002_recamera_sd`, `sg2002_xiao_sd`) · DDR `ddr3_1866_x16` | RC `external/configs/sg2002_recamera_emmc_defconfig` | 확인됨 |
| README 클론 URL | 옛 이름 `Seeed-Studio/reCamera.git`로 적혀 있다. 실제 저장소는 reCamera-OS | RC README | 확인됨 |

### 1.2 빌드 호스트

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| OS | 권장 Ubuntu 20.04 LTS, GCC/G++ 11.4 이상, cmake 3.31.2 | RC README §2.3.1 | 확인됨 |
| Docker | 지원하지만 필수는 아니다. `./docker_build.sh sg2002_recamera_emmc`가 이미지 `recamera-os-builder`를 만든다(Dockerfile 기본 VARIANT `noble` = Ubuntu 24.04). VS Code Dev Container도 있다 | RC `docker_build.sh`, `.devcontainer/Dockerfile` | 확인됨 |
| 디스크 | 여유 30 GB 권장 | RC README | 확인됨 |
| 빌드 명령·산출물 | `make sg2002_recamera_emmc` → `output/<proj>/install/soc_<proj>/`에 `*_emmc.zip`, `*_ota.zip`, `*_recovery.zip`, `*_sd_compat.zip` | RC README §2.3.3 | 확인됨 |
| 툴체인 | `riscv64-unknown-linux-musl-` (`CONFIG_TOOLCHAIN_MUSL_RISCV64`). host-tools 서브모듈에서 받는 것으로 보인다 | RC defconfig | 이름은 확인됨, 입수 경로는 추론 |

### 1.3 부트·저장장치·플래시·복구

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| CPU | RISC-V C906에서 리눅스를 부팅한다(`CONFIG_ARCH="riscv"`). ARM A53은 쓰지 않는다 | RC board `config.json`, defconfig | 확인됨 |
| 부트 체인 | fsbl → OpenSBI → u-boot 2021.10 → Linux 5.10. 작은 코어에서는 FreeRTOS가 돈다(`CONFIG_ENABLE_FREERTOS=y`) | RC `.gitmodules`, defconfig | 구성은 확인됨, 순서는 일반 SG200x 흐름으로 추론 |
| 부트 스트랩 핀 | `GPIO_RTX(EPHY_RTX)`: PU = C906 · PD = CA53. `UART0_TX`: PU = Normal · PD = ROM Fail Mode | core 회로도 PDF 6/8쪽 (OSHW `hardware/recamera-2002/core/c1-2002/static/reCamera_Core_2002w_8GB_v1.2_SCH_PDF_241014.pdf`) | 확인됨 |
| eMMC 배치 | FIP → `/dev/mmcblk0boot0`. 파티션: BOOT 8MB(p1) · ENV 128KB(p2, fw_env 0x20000) · ROOTFS 512MB(p3) · ROOTFS2 512MB(p4) · RESERVED 256MB(p5, 복구 패키지) · USERDATA 나머지(p6) | RC `.../sg2002_recamera_emmc/partition/partition_emmc.xml`, `fw_env.config`, `external/ramdisk/.../upgrade.sh` | 확인됨 (p6 번호는 추론) |
| A/B | rootfs A/B. u-boot 환경변수 `use_part_b`, `boot_failed_limits`(5), `boot_rollback`. swupdate `sw-description` | RC `external/u-boot/include/configs/cv181x-asic.h`, `external/build/tools/common/sw-description` | 확인됨 |
| bootcmd | `run sdboot \|\| cvi_update \|\| cvi_otp; run boot_record; run is_use_part_b; run emmcboot` | RC cv181x-asic.h L342 | 확인됨 |
| USB 굽기 | Windows `usb_dl.exe -c cv181x -s linux -i <압축 푼 폴더> [-m MAC]`. 드라이버 `CviUsbDownloadInstallDriver.zip`, 도구 `CviBurn_v2.0_cli_windows.zip` | RC README §2.4 | 확인됨 |
| SD 복구 | `*_emmc_recovery.zip`을 SD에 쓰고 꽂은 채 전원을 넣으면 eMMC에 자동으로 굽는다. `*_sd_compat.zip`은 SD에서 바로 부팅 | RC README §2.4 | 확인됨 |
| OTA·초기화 | WebUI `http://192.168.42.1/#/system` 또는 `/mnt/system/upgrade.sh latest <url>`. 초기화는 `upgrade.sh recovery` (D-003 #9로 PoC에서는 OTA 제외) | https://wiki.seeedstudio.com/recamera_os_version_control/ | 확인됨 |
| 버튼 | `UPGRAD_KEY` = AUX0 패드(4.7k 풀업) → J2-36 · `nRESET` → J2-34. USB 굽기 모드로 들어가는 버튼 절차는 문서에서 찾지 못했다 | core PDF 6·8쪽 | 신호는 확인됨, 절차는 미확인 |

### 1.4 장치 트리·핀먹스

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| 보드 DTS | `external/build/boards/cv181x/sg2002_recamera_emmc/dts_riscv/sg2002_recamera_emmc.dts` (model "Seeed reCamera"). **2002와 2002w가 같은 DTS를 쓴다**(wifisd, wifi_pin 포함) | RC | 확인됨 |
| 공통 dtsi | sophgo/build `boards/default/dts/cv181x/cv181x_base.dtsi`, `cv181x_riscv/cv181x_base_riscv.dtsi`, `cv181x_default_memmap.dtsi` | sophgo/build `85f705b1` | 확인됨 |
| 핀먹스 | u-boot 보드 초기화 `external/build/boards/cv181x/sg2002_recamera_emmc/u-boot/cvi_board_init.c`의 `PINMUX_CONFIG(...)`. 패드 기능표는 u-boot `board/cvitek/cv181x/cv181x_pinlist_swconfig.h` | RC / u-boot `050d49a7` | 확인됨 |
| 커널 defconfig | `.../sg2002_recamera_emmc/linux/cvitek_sg2002_recamera_emmc_defconfig` | RC | 확인됨 |

### 1.5 카메라 센서·IQ

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| GC2053 드라이버 | `sensor/cv181x/gcore_gc2053/` (SensorSupportList). `CONFIG_SENSOR_GCORE_GC2053=y` (OV5647, SC530AI_2L도 켜짐) | SS · RC `external/configs/sg2002_recamera_emmc_defconfig`, `external/SensorSupportList/sensor.mk` 18행 | 확인됨 |
| GC2053 IQ | `external/isp_tuning/cv181x/src/gcore_gc2053/gcore_gc2053_sdr.bin`(주간) · `gcore_gc2053_sdr_ir.bin`(IR) → rootfs `/mnt/cfg/param/`에 복사된다(`external/setenv.sh` `pack_cfg`) | RC | 확인됨 |
| 런타임 IQ 선택 | 앱 `app_ipcam_Isp_pq_bin()`은 `gcore_gc2053_sdr.bin`만 읽는다. **`sdr_ir.bin`을 읽는 코드는 없다** | SC `components/sophgo/video/src/video_paramparse.c` 419–435행 | 확인됨 |
| 센서 설정 | **ini 파일이 없고 C 코드에 고정돼 있다**: `sns_cfg_gc2053` = `s32BusId=2`, `s32I2cAddr=0x3f`, `MipiDev=0`, `as16LaneId={2,0,3,-1,-1}`, PN swap 없음, `bMclkEn=1`, 1920×1080 30fps. 앱이 OV5647 → SC530AI → GC2053 순서로 센서를 자동 감지한다 | SC `video_paramparse.c` 47–61, 337, 381–417행 | 확인됨 |
| 센서 리셋·전원 | DTS가 `&mipi_rx`의 `snsr-reset`을 지운다(리셋 핀 없음). 센서 전원 `CAM_EN` = gpio358(PWR_GPIO_6)을 `/etc/init.d/S70hardware`가 켠다 | RC dts, `cvi_board_init.c`, `S70hardware` | 확인됨 |
| MCLK | 앱은 cam0 MCLK를 켠다. 하지만 S401 보드에도 24MHz 1.8V 오실레이터 X1이 있다. 실제로 어느 클럭을 쓰는지는 모른다 | SC · OSHW S401 kicad_sch | 미확인 |
| GC4653 | 드라이버는 있지만 reCamera 설정에서 **꺼져 있고**, reCamera rootfs에 IQ가 없다. Sophgo `isp_tuning/cv181x/src/gcore_gc4653/` (sdr, sdr_ir)에는 있다 | SS · RC defconfig · https://github.com/sophgo/isp_tuning/tree/f7b2301/cv181x/src/gcore_gc4653 | 확인됨 |
| GC2083 | 드라이버는 있지만 reCamera에서 **꺼져 있고**, 앱 분기도 없다. Milk-V에 IQ `cvi_sdr_bin_GC2083`(628,456 B)과 `sensor_cfg_GC2083.ini`(bus 2, addr 0x37, `lane_id=1,0,2`)가 있다 | SS · milkv duo-buildroot-sdk-v2 `6f8962c` | 확인됨 |

### 1.6 I2C·GPIO 번호

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| 켜진 I2C | **i2c1, i2c2만** okay. i2c0, i2c3, i2c4는 disabled. `CONFIG_I2C_CHARDEV=y` | RC dts, 커널 defconfig | 확인됨 |
| 카메라 I2C | **I2C2** (`/dev/i2c-2`): PWR_GPIO1 = IIC2_SCL, PWR_GPIO2 = IIC2_SDA → 넷 `CAM_I2C2_SCL/SDA` | RC `cvi_board_init.c`, SC | 확인됨 |
| I2C1 | PAD_MIPI_TXM2 = IIC1_SDA, PAD_MIPI_TXP2 = IIC1_SCL. DTS에 `ti,ads1015` @0x48 (`CONFIG_TI_ADS1015=m`) | RC | 확인됨 |
| IIC0 | 회로도에 "Not Support IIC0" 표기. 해당 패드는 UART1로 쓴다 | core PDF 6쪽 | 확인됨 |
| GPIO 컨트롤러 | dw-apb-gpio 5개, 각 32핀: porta 0x03020000, portb 0x03021000, portc 0x03022000, portd 0x03023000, porte 0x05021000 (= PWR_GPIO) | sophgo/build cv181x_base.dtsi | 확인됨 |
| Linux 번호 | `XGPIOA n` = **480+n**, `PWR_GPIO n` = **352+n** (근거: `cvi_board_init.c` 주석 XGPIOA_15 = gpio495, PWR_GPIO_6 = gpio358 등). portb = 448, portc = 416, portd = 384 | RC `cvi_board_init.c` | A·PWR은 확인됨 · B·C·D는 추론 (512에서 32씩 내려가는 동적 배정) |
| 문서화된 사용 | 사용자 버튼 gpio510(AUX0, 누르면 0) · LED red = porta15(495, heartbeat) · blue = porte24(376) · white = porte0(352) · CAM_EN = 358 | https://wiki.seeedstudio.com/recamera_2002_series_hardware_and_specs/ · RC dts · `S70hardware` | 확인됨 |

### 1.7 IR-cut·주야·조도센서

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| 판단 API | `CVI_S32 CVI_ISP_IrAutoRunOnce(ISP_DEV, ISP_IR_AUTO_ATTR_S*)`. 속성은 `bEnable`, `u32Normal2IrIsoThr`, `u32Ir2NormalIsoThr`, `u32RG/BGMax/Min`, `enIrStatus`, `enIrSwitch`(NONE / TO_NORMAL / TO_IR) | cvi_mpi `include/isp/cv181x/cvi_isp.h` 326행, `cvi_comm_isp.h` 614–637행 | 확인됨 |
| AE IR-cut 필드 | `ISP_AE_ATTR_S.s16IRCutOnLv`, `s16IRCutOffLv`, `enIRCutStatus`(AUTO/ON/OFF) | cvi_mpi `cvi_comm_3a.h` | 필드는 확인됨, 동작은 미확인 |
| 예제 | `cvi_mpi/sample/sample_ir_auto/sample_ir_auto.c`: ISO와 R/B 게인으로 주야를 판단하는 소프트웨어 방식. **실제 전환 함수 `switch_to_ir()`·`switch_to_normal()`은 비어 있다**(주석 "1. switch pq BIN 2. switch ir cut"만 있음) | cvi_mpi `6dbbbb8` | 확인됨 |
| IQ 교체 API | `CVI_BIN_SetBinName()`, `CVI_BIN_ImportBinData()`, `CVI_BIN_LoadParamFromBin()` | cvi_mpi `include/cvi_bin.h` | 확인됨 |
| reCamera 구현 | **없다.** ircut, IrAuto, IR bin 교체 코드가 OS와 앱 어디에도 없다. `PQ_BIN_IR` 정의는 쓰이지 않는다 | RC · SC `app_ipcam_isp.h` | 확인됨 |
| IR_CUT 핀 | `GPIO15/IR_CUT` = XGPIOA_15 = gpio495, J1-33. **reCamera DTS는 이 핀을 빨간 LED(heartbeat)로 쓴다** | RC `cvi_board_init.c`, dts · core BTB | 확인됨 |
| S401의 IR 관련 부품 | ICR H-브리지, IR LED, 조도 IC가 **없다**. IR_CUT·IR_PWM은 BSS138로 상태 LED를 구동한다 | OSHW S401 kicad_sch | 부품 목록은 확인됨, 연결은 추정 |
| LIGHT_SENSE | 코어 J1-18, 라벨상 ADC1. S401 안에서는 어디에도 연결되지 않는다 | core BTB_Connector.png · S401 sch | 핀은 확인됨, SoC 패드는 라벨 기준 |
| LTR-329 드라이버 | 메인라인 `drivers/iio/light/ltr501.c`의 ltr329 지원은 커밋 `e5aaf9e06c326e44e6b20ff46ec28642b555096d`(compatible `liteon,ltr329`, partid 0x0A, IRQ 없음)로 들어왔고 master에만 있다(v7.2 태그까지는 없음). 5.10 `ltr501.c`는 ltr501/559/301만 지원. **sophgo linux_5.10에는 없어 백포트가 필요하다.** reCamera 커널에 `CONFIG_LTR501`이 없다 | torvalds/linux · sophgo/linux_5.10 `d0486a96` · RC 커널 defconfig | 확인됨 (포함될 릴리스 버전은 미확인) |

### 1.8 이더넷·microSD

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| MAC | `ethernet@4070000`, compatible `cvitek,ethernet`, rmii, stmmac `dwmac-cvitek.c` (`CONFIG_STMMAC_ETH=y`) | sophgo/build dtsi · linux_5.10 | 확인됨 |
| 내장 EPHY | `drivers/net/phy/cvitek.c`, phy_id 0x00435649 "CVITEK CV182XA" (`CONFIG_CVITEK_PHY=y`), 100Mbps | linux_5.10 · wiki | 확인됨 |
| MDI 핀 | EPHY_TXP/TXN/RXP/RXN = J2-1/3/7/9. 트랜스포머는 베이스 보드에 둔다 | core PDF 8쪽 | 확인됨 |
| MAC 주소 | u-boot `cvi_otp`가 efuse에서 ethaddr를 읽는다 | RC `cvi_board_init.c` | 확인됨 |
| microSD | `cv-sd@4310000` (SDIO0) okay, `cvi-cd-gpios=<&porta 13>`. reCamera DTS는 `no-1-8-v`(3.3V 전용)와 최대 50MHz로 설정한다. 베이스의 TF는 `/dev/mmcblk1p1`로 보이고 ext4만 인식한다 | RC dts · wiki | 확인됨 |
| SD0 핀 | SDIO0_D3/D2/D1/D0/CMD/CLK/CD = J2-39/41/43/45/47/51/55 · SD0_PWR_EN(XGPIOA_14) = J2-37 | core BTB · `cvi_board_init.c` | 확인됨 |
| SD1 | `wifi-sd@4320000`. 2002(무선 없음)는 SD1과 UART1을 BTB로 내보낸다고 README에 적혀 있다. 공개 회로도는 2002w 기준이라 R48~R53, R67~R70이 미실장으로 그려져 있다 | OSHW core README · PDF 8쪽 | 2002에 실장되는지는 추론 |

### 1.9 NPU·사람 감지 (D-003 #3)

| 항목 | 값 | 출처 | 확인 |
|---|---|---|---|
| tpu-mlir | 최신 v1.30.2 (2026-08-31). `model_deploy.py` chip 목록에 `cv181x`, `.cvimodel` 옵션(`--merge_weight`, `--model_version`)이 있다. cv18xx 지원을 뺐다는 공지는 없다 | https://github.com/sophgo/tpu-mlir/blob/v1.30.2/python/tools/model_deploy.py | 확인됨 (v1.30.2로 실제 변환되는지는 미확인) |
| 변환 호스트 | Docker `sophgo/tpuc_dev` (Seeed 최근 가이드 v3.4 + `tpu_mlir[onnx]==1.28.1`, 옛 가이드 v3.1 + 1.7). ONNX opset 17 이하 | https://wiki.seeedstudio.com/recamera_deploy_monocular_depth/ · https://wiki.seeedstudio.com/recamera_model_conversion/ | 확인됨 |
| INT8 순서 | `model_transform` → `run_calibration`(100~500장) → `model_deploy --quantize INT8 --processor cv181x --fuse_preprocess ...` → 기기 `sscma-model`이나 Node-RED로 배포 | Seeed wiki | 확인됨 |
| 기기 런타임 | cviruntime (고정 `3f493864`) → tdl_sdk (`1d86f4dd`, BSD-2) → Seeed `sscma-node`/`sscma-supervisor` 0.2.5 (Apache-2.0) → Node-RED `node-red-contrib-sscma` v0.2.8 | RC `.gitmodules`, `external/br2-external/sscma-node/sscma-node.mk` | 확인됨 |
| 사람 감지 모델 (Sophgo) | `tdl_models/cv181x`: `mbv2_det_person_*_INT8_cv181x.cvimodel` (256×384 ~ 896×896), `yolov8n_det_person_vehicle_384_640`, `yolov8n_det_ir_person_384_640` 등. SG2002 FPS 수치 없음. 라이선스 표기 없음 | https://github.com/sophgo/tdl_models/tree/main/cv181x (`62b3dff4`) | 파일은 확인됨, 라이선스는 미확인 |
| 사람 감지 모델 (Seeed) | `yolo11n_detection_cv181x_int8.cvimodel`, `yolo26n_cv181x_int8.cvimodel` (COCO-80, person 포함, 640×640). YOLO11n INT8 기준 **20 FPS, 50ms, 1.5W**. **AGPL-3.0(Ultralytics)**이다. 그 밖에 `person_cv181x_int8.cvimodel`(사양 미기재) | https://github.com/Seeed-Studio/sscma-example-sg200x/tree/main/models/detection · https://wiki.seeedstudio.com/recamera_benchmarking/ | 확인됨 |

## 2. 핀·버스·GPIO 요약 (schematic 계약 초안 대조용)

코어 보드 B2B: J1 `ST-BTB-058060-A`, J2 `ST-BTB-058060-B` (60P 0.5mm). 출처는 OSHW `core/c1-2002/static/BTB_Connector.png`와 core PDF 8쪽이다. 회로도 PDF 파일명은 v1.2이지만 내부 표제란은 Rev V1.0 (2024-04-25)이다. **실물 보드의 판은 받은 뒤 확인해야 한다.**

| 기능 | 커넥터-핀 | 넷 | SoC 패드 / Linux | SDK 기본 상태 | 확인 |
|---|---|---|---|---|---|
| MIPI CSI | J1-3/5, 9/11, 15/17, 21/23, 27/29 | CAM_RX0_4N/P, CLKN/P, 0N/P, 1N/P, 3N/P | MIPI RX0. GC2053 lane `{2,0,3}` | 사용 | 넷은 확인됨, 레인↔넷 대응은 미확인 |
| 카메라 I2C | J1-10 / J1-12 | CAM_I2C2_SCL / SDA | PWR_GPIO1 / 2 → `/dev/i2c-2` | 사용 (GC2053 0x3f) | 확인됨 |
| 센서 전원 | J1-47 | CAM_EN | PWR_GPIO_6 = gpio358 | `S70hardware`가 켬 | 확인됨 |
| IR-cut | J1-33 | GPIO15/IR_CUT | XGPIOA_15 = gpio495 | **빨간 LED로 쓰임** → DTS 수정 필요 | 확인됨 |
| IR LED PWM | J1-16 | IR_PWM | 미확인 | — | 핀만 확인됨 |
| 흰색 LED PWM | J1-6 | WH_PWM | PWR_GPIO0 = gpio352 추정 | white LED | 추론 |
| 조도 (아날로그) | J1-18 | LIGHT_SENSE | ADC1 (라벨 기준) | 드라이버 미확인 | 핀은 확인됨 |
| 오디오 | J1-39 / J1-43 | AUD_MIC / AUD_AOUTR | — | — | 확인됨 |
| 전원 | J1-38~44 · J2-30~36 짝수 / J1-50·52 / J1-58·60 · J2-28 | VIN (5V) / +1V8 / +3V3 | — | — | 확인됨 |
| 이더넷 MDI | J2-1/3/7/9 | EPHY_TXP/TXN/RXP/RXN | 내장 EPHY 100M | 사용 | 확인됨 |
| USB2 | J2-2/4, J2-13 | USB_DN/DP, USB_DET | DWC2 OTG | 사용 | 확인됨 |
| microSD | J2-39/41/43/45/47/51/55, J2-37 | SDIO0_D3~D0/CMD/CLK/CD, SD0_PWR_EN | SDIO0, CD = porta13 (gpio493), PWR = XGPIOA_14 | okay, 3.3V 전용 | 확인됨 |
| I2C1 / PWM | J2-15 / J2-17 | MIPI_TXM2/IIC1_SDA, MIPI_TXP2/IIC1_SCL | IIC1 | **ADS1015 @0x48이 사용 중** | 확인됨 |
| GPIO / PWM / IIC2 대체 | J2-19 / 21 / 23 / 25 | MIPI_TXM1/IIC2_SDA, TXP1/IIC2_SCL, TXM0/GPIO12, WL_BT_EN/GPIOC13 (R14 미실장) | XGPIOC 12~17 계열 → 416+n 추론 | — | 넷은 확인됨, 번호는 추론 |
| SDIO1 | J2-12/16/18/20/22/24 | SD1_CLK/CMD/D0~D3 | SDIO1 (`wifi-sd`) | DTS okay | 2002 실장은 추론 |
| UART | J2-57/59 · J2-54/56/58/60 | DEBUG_UART0_TX/RX · BT_UART1_RX/TX/CTS/RTS | ttyS0 디버그 · UART1 | — | 확인됨 (UART1 실장은 추론) |
| 제어 | J2-34 / J2-36 / J2-31 | nRESET / UPGRAD_KEY / PWR_WAKEUP1 | — / AUX0 = gpio510 (DTS는 wifi_pin으로도 사용) | 사용자 버튼 | 확인됨 |
| 부트 스트랩 | (코어 내부) | EPHY_RTX, UART0_TX | PU = C906 / Normal | — | 확인됨 |
| 예비 | J1-2/4, J2-8/10 | RESERVE1/2 | 미확인 | — | 미확인 |

### schematic·HW/FW 계약에 넘길 주의점
1. **IR-cut 구동:** ICR 구동 회로(H-브리지)와 IR LED 드라이버는 캐리어나 센서 보드에 새로 넣어야 한다. 소프트웨어 쪽도 SDK 예제의 전환 함수가 비어 있어 F-002에서 새로 써야 한다. GPIO15를 IR-cut에 쓰려면 DTS에서 heartbeat LED를 빼야 한다. ICR을 2핀(정·역)으로 구동하면 핀이 하나 더 필요하다. 후보는 J2-23·25(XGPIOC) 또는 IR_PWM이며, 계약에서 정한다.
2. **조도 센서:** 두 가지 방법이 있다. LTR-329(I2C)를 쓰면 5.10용 백포트가 필요하다. I2C 버스는 i2c1(ADS1015와 공유) 또는 i2c2(센서와 공유)다. LIGHT_SENSE(J1-18, ADC1)에 포토다이오드나 포토트랜지스터를 다는 방법은 커널 패치가 필요 없지만 ADC 드라이버 확인이 남아 있다.
3. **I2C1:** ADS1015가 0x48을 쓰고 있다. 캐리어에 ADS1015를 두지 않으면 DTS에서 지워야 한다.
4. **microSD:** SDIO0은 3.3V 전용(`no-1-8-v`)이고 CD = porta13이다. B301/B101 베이스 회로를 참고하되 새로 그린다(O-4).
5. **전원:** 모듈 VIN은 5V다. 12V를 5V로 내리는 강압 회로는 캐리어에 둔다(D-003 #10).

## 3. 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| F1 | 기준 SDK 판 | reCamera-OS 0.2.4 정식 (커널 `d0486a96`이 HEAD와 같다) | 정식 릴리스이고 커널 SHA가 최신과 같다 | 0.2.6 prerelease (F-002 빌드 때 다시 비교) |
| F2 | 센서 GC2053 vs D-003 #5 GC2083 | **GC2053** (orch O-3) | reCamera에서 드라이버가 켜져 있고 IQ(sdr·sdr_ir)가 rootfs에 들어가는 유일한 2MP 센서다 | GC4653 (Sophgo IQ 이식) → GC2083 (Milk-V IQ 이식, 둘 다 defconfig·앱 수정 필요) |
| F3 | 주야 판별 | 하드웨어 조도 (D-003 #7) 유지. 수단은 계약에서 정한다 | reCamera 쪽에 주야 전환 구현이 전혀 없어 어느 쪽이든 새로 써야 한다 | `CVI_ISP_IrAutoRunOnce` 소프트웨어 판단 (D-003 #7 차선) |
| F4 | 사람 감지 모델 | Sophgo `tdl_models` 사람 전용 모델(`mbv2_det_person` 등)을 1순위 후보로 둔다 | Seeed YOLO11·YOLO26은 AGPL-3.0이다 | Seeed YOLO11n (성능 수치 공개, AGPL 수용 시) |
| F5 | 빌드 호스트 | Docker (`docker_build.sh`) | Windows 호스트이고 공식 지원 경로다 | WSL2 Ubuntu 20.04 직접 빌드 |

## 4. 미확인 목록
- USB 굽기 모드로 들어가는 버튼 절차
- RESERVE1/2·IR_PWM·WH_PWM이 연결되는 SoC 패드 (회로도 PDF 연결선을 해석하지 못함)
- 2002(무선 없음) 판의 SD1·UART1 저항 실장 여부
- CSI 레인 번호와 물리 넷 대응, S401 MCLK 출처
- portb/c/d GPIO 베이스 번호 (실물 `/sys/class/gpio`로 확인해야 함)
- B301 하위 시트 (파일을 받지 못함)
- tdl_models·cviruntime 라이선스, TDL 사람 모델의 SG2002 FPS
- tpu-mlir v1.30.2로 cv181x를 실제로 변환할 수 있는지
- ADC1(LIGHT_SENSE) 커널 드라이버와 노출 경로
