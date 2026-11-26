# F-004 사람 감지 → 네트워크 이벤트

- 배정: orch t18r F-004 · 작성: firmware t18w · 레인 t-20261126-210506-1e37 (F-003 레인에서 이어 시작) · 날짜 2026-11-26
- **결과 요약:**

| 항목 | 상태 |
|---|---|
| 감지 앱 `persond` | 완료. 호스트 시험 33/33, 통합 시험 16/16 통과 |
| `daynight` 끄는 순서 수정 | 완료. 시험 40/40 통과 |
| 이미지 빌드 | 종료 코드 0 |
| **사람 감지 모델** | **미완료.** 라이선스가 확인된 모델이 없다. Apache-2.0 YOLOX-Nano를 변환했지만, 변환한 cvimodel이 호스트 모의 실행 검증에서 3회 연속 실패했다. 같은 원인으로 3회 실패하면 멈추는 규칙에 따라 중단했다. **이미지에 모델은 넣지 않았다** |

- 보드가 없어 **추론 정확도·FPS·HIL은 미검증**이다.

## 1. 모델 출처·라이선스 (D-003 #19)

| 후보 | 라이선스 | cv181x cvimodel | 판정 |
|---|---|---|---|
| Sophgo `tdl_models` `mbv2_det_person_*`, `yolov8n_det_*person*` | **미확인.** GitHub license API는 `null`이고, LICENSE·NOTICE 파일이 없다. README와 18개 커밋에도 라이선스 언급이 없고, 파일 안에도 없다(HEAD `62b3dff417c01dfe2a21872c26691a4c9a009da5`, 2025-10-13). `tdl_sdk`의 BSD-2(`docs/LICENSE`)는 SDK에만 해당한다. `yolov8n_*`는 이름으로 보아 Ultralytics(AGPL-3.0) 기반으로 보인다 | 있다. 예: `cv181x/mbv2_det_person_256_448_INT8_cv181x.cvimodel` 530,016 B, sha256 `f080f044089b68e004cbe2beb5c9a02367727cd774f7ab03b393cc1d87e05874`. 단, sscma-node가 이 TDL 출력 형식을 지원하지 않는다 | **쓰지 않음** (지시: 라이선스가 미확인이면 차선으로) |
| Seeed `yolo11n_detection_cv181x_int8.cvimodel` | AGPL-3.0 | 있다 | **쓰지 않음.** AGPL 채택은 사용자 결정이 필요하다 |
| **YOLOX-Nano** (Megvii) | **Apache-2.0** | 없다 → 직접 변환 | **채택** (차선) |
| NanoDet-Plus-m | Apache-2.0 | 없다 | 예비 후보. sscma 후처리 형식에 맞지 않는다 |

- **원본:** `https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.onnx`(3,659,407 B, 416×416, COCO 80클래스). sha256은 `convert-yolox-person.sh` 실행 로그 `f004-model-2.log`에 있다.
- **COCO 가중치 출처 표시:** 주석은 CC BY 4.0이고 이미지는 Flickr 개별 조건이다. 제품에는 출처를 표시하기를 권한다. 법적 판단은 하지 않았다.

## 2. 모델 변환 (tpu-mlir 1.28.1, `sophgo/tpuc_dev:v3.4`, 볼륨 `openhw-tpumlir`)

**형식을 맞춘 방법:**
- sscma-node model 노드는 YOLO 계열, RTMDet, FOMO 형식만 받는다(sscma-micro `ma_model_factory.cpp`).
- 그중 YoloV5 후처리(`ma_model_yolov5.cpp`)는 출력 1개 `[1,(s²+m²+l²)·3, 6..85]`를 받는다. 각 레코드는 [중심 x, y, w, h, score, class…]이고 0~1로 정규화돼 있으면 그대로 쓴다.
- `firmware/models/yolox_to_sscma.py`가 YOLOX ONNX 그래프에 다음을 덧붙인다.
  - 격자 디코딩: `(reg + grid)·stride/416`, `exp(reg)·stride/416`
  - 점수: `obj × person`
  - 출력: `[1,3549,6]`을 만들고 0으로 채워 `[1,10647,6]`으로 늘린다
- onnxruntime으로 COCO 100장에 돌려 출력 모양 `(1,10647,6)`과 사람 점수 최고 0.94(`000000356531.jpg`)를 확인했다.

| 단계 | 결과 | 근거 |
|---|---|---|
| `model_transform` (BGR, mean 0, scale 1, letterbox) | **통과.** ONNX와 top MLIR의 `output_sscma_Concat` 비교에서 cosine 1.000000, `npz compare PASSED` | `f004-model-2.log` 1458–1477행 |
| `run_calibration` (tpu-mlir `regression/dataset/COCO2017` 100장) | 끝남 (auto tune 48초) | 같은 로그 |
| `model_deploy` INT8 + `--test_input/--test_reference` | **rc=1.** 전처리를 합친 직후, 모의 비교 단계에서 메시지 없이 끝났다(원인 H) | `f004-deploy-dbg.log` 끝 `deploy rc=1` |
| `model_deploy` INT8 (시험 옵션 없이) | rc=0 → `yolox_nano_person_416_int8_cv181x.cvimodel` 1,296,872 B, sha256 `71397280321bdb5e3005aac17cd57b4b353afb8f04e636eab7f17e35a6c7e334` | `f004-deploy-2.log` |
| `model_deploy` BF16 | rc=0 → `yolox_nano_person_416_bf16_cv181x.cvimodel` 2,826,264 B, sha256 `17ac48f843a82212ba0a8beb3dd75d42f9cef93c383a932805c4271c54cda3b8` | `f004-bf16-1.log` |
| **검증** `verify_cvimodel.py` (COCO 20장, cvimodel 호스트 모의 실행 vs float ONNX) | **3회 실패.** ONNX 점수가 0.66~0.93인 이미지에서도 cvimodel 점수는 ≤0.009다. 사람 판정 일치율 50% | `f004-verify-1/2.log`, `f004-bf16-1.log` |

### 변환 실패 원인 판정 (원인마다 따로 센다)

| 원인 | 횟수 | 근거 | 조치 |
|---|---|---|---|
| G. 편집 스크립트 이름 충돌 | 1 | `ValidationError: … 'oh_wh_e' has been used as output names multiple times` (Slice 끝값 initializer 이름이 Exp 출력 이름과 같았다) | 이름을 `_start`/`_end`로 바꾸고 onnxruntime으로 확인 → 해결 |
| H. `model_deploy` 시험 모의 실행이 메시지 없이 rc=1 | 1 | 로그 끝이 `Inserting SwapChannelOp` 다음 진행 막대, 이어서 `deploy rc=1`. VM `dmesg`에 OOM 없음 | 시험 옵션을 빼고 배포하고, 검증은 따로 하기로 했다 |
| **J. cv181x로 내릴 때 마지막 축 Slice 결과가 틀린 것으로 보임** | **3 (상한 도달)** | 실패 1(INT8, 입력 이름 `input`)과 실패 2(INT8, 입력 이름 `images_raw`)의 결과가 같았다 → 입력 이름은 원인이 아니다. 실패 3(BF16)도 같았다 → 양자화도 원인이 아니다. cvimodel 중간 텐서를 보면 `oh_wh_e_Expoh_wh_n_Mul` 최댓값이 **25.0**(정규화 폭·높이라 1 안팎이어야 함), `oh_score_Mul` 최댓값이 0.0074다. 원래 출력은 `output_Transpose [1,3549,85]` 다음에 마지막 축(85채널)을 자르는 구조인데, 이 Slice가 다른 채널을 집어 온 것으로 판정한다. float top MLIR 단계까지는 원본과 같다(cosine 1.0) | **중단.** 앞의 두 번은 틀린 가설(입력 이름, INT8)로 바꿔 돌렸고, 세 번 모두 같은 근본 원인이었다고 다시 판정했다. 4회째는 돌리지 않는다 |

**다음 조치 제안 (orch 결정 필요):**
- YOLOX 출력의 Transpose 앞 `[1,85,3549]`에서 **채널 축(axis 1)으로 자른다.**
- 디코딩을 `[1,k,N]` 배치로 한 뒤 맨 끝에만 Transpose `[1,N,6]`를 둔다.
- 그다음 INT8로 다시 변환하고 같은 `verify_cvimodel.py` 기준(점수 차 평균 ≤0.10, 판정 일치 ≥90%, IoU ≥0.7)으로 판정한다.
- 이 경우 원인 J를 고치는 첫 시도가 된다.

## 3. 감지 앱 `openhw-persond` (`/usr/bin/persond`, `/etc/openhw/persond.conf`, `/etc/init.d/S97persond`)

- **구조:** 카메라와 NPU는 sscma-node가 맡고, persond는 MQTT(로컬 mosquitto)로 sscma-node에 노드를 만들게 하고 결과를 구독한다. persond는 카메라를 직접 열지 않는다.
- **노드 생성:** `create` 요청을 `sscma/v0/recamera/node/in/<id>`에 보낸다.
  - `openhw_cam`: camera. 720p, 15fps, audio·preview·websocket 끔. dependents는 model과 stream
  - `openhw_person`: model. `algorithm: 3`(YoloV5 형식), `tscore = min_score`, `tiou 0.45`, `labels ["person"]`, websocket 끔
  - `openhw_rtsp`: stream. RTSP 554 `live`, 사용자·비밀번호는 설정에서 읽는다. **비밀번호가 비면 만들지 않는다**
  - sscma-node는 의존 노드가 모두 갖춰지면 스스로 시작한다(`node.cpp` 의존 확인 코드)
- **결과 처리:** `sscma/v0/recamera/node/out/openhw_person`의 `invoke` 메시지에서 `boxes [x,y,w,h,score(0~100),target]`(픽셀, 중심)와 `resolution`을 읽는다. `target==0`이고 점수가 `min_score` 이상인 박스만 정규화해 점수순으로 최대 16개 남긴다.
- **이벤트 판정** (`persond_logic.c`):
  - 등장: 연속 `enter_frames`(3)프레임
  - 퇴장: 마지막으로 본 뒤 `leave_ms`(5000). 결과 메시지가 끊겨도 `pn_tick`이 판정한다
  - 쿨다운: 등장 이벤트 사이 `cooldown_ms`(30000)
- **이벤트 JSON** (`event_topic` = `openhw/v1/event`, QoS 1):
  `{"event":"person_enter"|"person_leave","ts":"<UTC ISO, ms>","device":"<호스트명>","mode":"day|night|unknown","score":0.880,"count":1,"resolution":[1280,720],"boxes":[[cx,cy,w,h,score],...]}`
  `mode`는 `/run/daynight/mode`(openhw-daynight)에서 읽는다.
- **수신 브로커:** 기본은 장치 안 로컬 mosquitto다. `event_host`/`event_port`를 주면 별도 연결로 그쪽 브로커에 보낸다.

### 시험

| 시험 | 명령 | 종료 코드 | 결과 |
|---|---|---|---|
| 이벤트 로직 단위 | `docker run recamera-os-builder … make test` (`-Wall -Wextra -Werror`) | 0 | **pass=33 fail=0** (등장·퇴장·끊김·쿨다운 1시간 상한·필터·JSON·설정) |
| 호스트 통합 | `docker run … bash test_integration.sh`. 컨테이너 안의 mosquitto, persond 호스트 빌드, 가짜 sscma 결과를 쓴다. 외부 서버 없음 | 0 | **pass=16 fail=0** (노드 생성 요청 내용, 3프레임 등장, 낮은 점수 제외, 정규화 박스, night 모드, tick 퇴장, 쿨다운, 잘못된 메시지에도 생존, SIGTERM, 비밀번호가 없으면 RTSP 끔) |
| 호스트 컴파일 | `make persond` (libmosquitto·json-c) | 0 | 경고 0 |

- 통합 시험 첫 실행은 15/16이었다. 원인은 시험 스크립트였다: 구독 프로세스가 쓰는 로그를 `: >`로 비워 NUL이 생겼고, `grep`이 바이너리로 판정했다. `grep -a`로 고쳤다. 앱 결함이 아니다.

## 4. 함께: IR 끄는 순서 (F-003 "cvi_pwm duty==period → period−1")

- **근거:** `osdrv/interdrv/pwm/cv181x/cvi_pwm.c`는 `duty_count == period_count`이면 `period_count − 1`로 만든다. 그래서 PWM만으로는 완전한 High(끔)가 안 된다.
- **변경** (`a328164`): 낮 전환 순서를 **IR_LED_EN 끔 → IR_PWM High**로 바꿨다. 데몬을 끝낼 때도 EN을 먼저 끈다. 켤 때 순서(PWM High → EN 켬, O-33)는 그대로다.
- **시험:** `daynight` `make test`가 **pass=40 fail=0**(종료 코드 0)이다. 새로 넣은 핀 상태 모의 시험 3건은 "PWM 끔에도 1/250,000만큼 Low가 남는다"고 가정하고 다음을 확인한다.
  - EN을 켤 때 PWM은 항상 끔 상태다
  - EN=1인 동안 켬 비율은 25% 이하다
  - 낮으로 바뀐 뒤 EN=0이다
- **실물:** EN이 eFuse SHDN으로 전류를 실제로 끊는지는 스코프와 전류계로 확인해야 한다(HIL 미검증).

## 5. 이미지 빌드 (F-003 방식: hc 칸 t19d, `CPUSET=0-3 MEM=16g JLEVEL=4`, `slot --label F-004 --timeout-min 240`)

| 단계 | 종료 코드 | 결과 |
|---|---|---|
| `SKIP_MODEL=1 bash firmware/scripts/apply-f004.sh` | 0 (4회차) | 아래 적용 문제 참고 |
| `build-baseline.sh build` | **0** | 391초, 21:40:55 KST 종료 |
| `collect` (`out-f004/`) | 0 | — |

| 파일 | sha256 |
|---|---|
| `sg2002_reCamera_0.2.4_emmc.zip` (= `upgrade.zip`) | `82012afe3c354b0e3835b103391f9280c0bbd373a730fd1192a8c9a0402a1a46` |
| `sg2002_reCamera_0.2.4_emmc_ota.zip` | `5fce749f8c9c79838401a44ece9593023939865b7580d94b32addd20cc248e43` |
| `sg2002_reCamera_0.2.4_emmc_recovery.zip` | `cc0b8f1ed1f5d0db259a72b873513718d024e33e55058f5e6346c0c36c5d3bd7` |
| `sg2002_reCamera_0.2.4_emmc_sd_compat.zip` | `4e045692fcaa334b1f4989394acb741fae59bd7dafbf7f87cc1cc61848f4df43` |
| `sg2002_reCamera_0.2.4_emmc_swu.zip` | `bc7cd3444d4e187bf48ec0b6e537cf56b3ebbeed4689e403623a93b38388f99e` |

- **rootfs 확인** (`debugfs`):
  - `/usr/bin/persond`: 19,216 B, RISC-V ELF
  - `/etc/openhw/persond.conf`: 796 B
  - `/etc/init.d/S97persond`: 321 B
  - `/usr/bin/daynight`: 14,816 B. `apply-f003.sh`가 dirclean했으므로 `a328164` 소스로 다시 빌드됐다
  - `/usr/share/openhw/models`: **없다**(의도: 검증을 통과한 모델이 없다)
- **이 이미지로 부팅하면:** persond가 model 노드를 만들 때 sscma-node가 모델 파일 오류로 응답한다. persond는 그 응답을 기록하고 계속 동작하지만 이벤트는 나지 않는다.

### 적용 스크립트 문제와 처리 (기록)
1. `apply-f004.sh`의 두 번째 `docker run`에 `builder` 사용자가 없어 `sudo: unknown user builder`로 실패했다 → `useradd` 줄을 넣었다.
2. 0002가 0001과 같은 `Config.in`을 고치기 때문에, 0001이 적용돼 있는지 역적용 시험으로는 판정이 안 됐다. 그래서 0001을 다시 적용하려다 `.rej`가 생기고, 새 파일(`openhw-daynight.mk` 등)에 내용이 두 번 붙었다.
   - 고친 것: `/work/src/.openhw-applied` 표시 파일로 적용 여부를 판정하고, `--no-backup-if-mismatch`를 쓴다.
   - 새 파일 4개는 패치 내용으로 다시 썼다. `status_led`·`PWM_2`가 1회씩이고 `Config.in`의 openhw 줄이 2개인 것을 확인했다.
3. **실수:** `.rej`/`.orig`를 지우면서 원래 저장소에 있던 `external/SensorSupportList/sensor.mk.orig`와 `sensor/cv182x/Makefile.orig`(git 추적 파일)까지 지웠다. 곧바로 `git show HEAD:<경로>`로 되살렸다. 이후 `git status`에는 의도한 변경만 남았다(Config.in·DTS·board init 수정, openhw 패키지 2개, sscma 패치, 표시 파일).

## 6. 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| F4-1 | 사람 감지 모델 | YOLOX-Nano(Apache-2.0)를 직접 변환 | Sophgo 모델은 라이선스 미확인이고 Seeed 것은 AGPL이다(지시) | Sophgo에 라이선스 서면 확인 / NanoDet-Plus(후처리 형식을 맞춰야 함) |
| F4-2 | 추론을 어디서 하나 | sscma-node model 노드 (`algorithm 3` YoloV5 형식에 맞춘 ONNX) | 카메라는 하나이고 sscma-node가 연다. 이미 있는 서비스를 쓰고 새 C++ 카메라 코드를 만들지 않는다 | 데몬이 cvi_mpi·cviruntime을 직접 쓰기(카메라를 독점하게 된다) |
| F4-3 | 이벤트 전송 | MQTT (이미지에 이미 있는 mosquitto 2.0.10·libmosquitto). 토픽 `openhw/v1/event`, QoS 1 | 새 서비스 의존이 없다 | HTTP POST (libcurl 필요) |
| F4-4 | LAN 수신 | 기본은 장치 안 로컬 브로커. `event_host`로 외부 브로커 지정 가능 | 이미지의 mosquitto는 리스너 설정이 없어 로컬 전용이다. 1883을 LAN에 익명으로 열면 sscma 제어 토픽까지 노출되므로, 보안 판단이 필요해 열지 않았다 | mosquitto에 인증 리스너 추가 (사용자 결정) |
| F4-5 | 영상 | sscma-node stream 노드 RTSP 554 `live`. **비밀번호가 설정돼 있을 때만** 만든다 | SDK에 이미 있다. 기본값 `admin/admin`은 쓰지 않는다 | WebSocket 8080 (camera 노드) |
| F4-6 | 이벤트 기본값 | 점수 ≥0.5, 3프레임, 퇴장 5초, 쿨다운 30초 | 오검출과 이벤트 폭주를 막는 보수적인 값 | 실측 뒤 조정 |
| F4-7 | 카메라 해상도·fps | 720p, 15fps | 추론 입력은 416이라 1080p는 불필요하다. 부하를 줄인다 | 1080p/30 |
| F4-8 | 검증을 통과하지 못한 모델 | 이미지에 넣지 않는다 | 틀린 결과를 내는 모델을 출하하지 않는다 | — |

## 7. 미확인 / 남은 일
- **모델:** F-004b(8절)에서 Transpose 앞 자르기로 1회 재변환했지만 **불합격**이었다. 모델 경로 **D**로 마감한다(모델 없이, bring-up 뒤로). 실제 원인은 Slice가 아니라 헤드 출력(obj 채널이 0)이다. 다음 시도는 orch·사용자가 결정한다.
- **HIL:** sscma-node가 persond 요청으로 노드를 실제로 만들고 시작하는지, RTSP 재생, 추론 FPS, 이벤트 지연.
- **Node-RED와 충돌:** 사용자가 Node-RED flow로 camera 노드를 따로 만들면 카메라가 겹친다. 지금 이미지에는 사용자 flow가 없다(`/home/recamera/.node-red/flows.json` 없음).
- **야간 IR 영상에서의 정확도:** COCO(가시광) 가중치라 성능이 떨어질 수 있다.

## 8. F-004b 원인 J 회피 재변환 (사용자 결정 2026-11-27, orch O-50, 같은 원인 4회째 · 1회만)

### 8.1 합격 기준 (변환 결과를 보기 전에 정함 · 결과를 본 뒤 바꾸지 않는다)

**입력 이미지 21장 (고정):**
- F-004와 같은 20장: `tpu-mlir/regression/dataset/COCO2017/*.jpg`를 이름순으로 정렬한 앞 20장(`000000000632.jpg` … `000000088970.jpg`).
- 사람 없는 이미지 1장: 같은 폴더의 `000000162130.jpg`(풀밭과 벤치, 사람 없음을 눈으로 확인). sha256 `688dbaa4b39c792ef94ad2f3b2b665e1b37bcb8aa03c838c17451f2fba75fee9`.
- 전처리는 F-004와 같다: 416 레터박스, 가운데 정렬, 0 채움.

**비교 대상:** 기준은 바꾼 sscma 형식 float ONNX(onnxruntime)이고, 비교 대상은 cvimodel(INT8, cv181x, tpu-mlir 호스트 모의 실행)이다.

**검출의 정의:** 레코드 score ≥ 0.5를 고르고, IoU 0.45로 NMS한 뒤 남은 박스. persond `min_score` 0.5와 같은 값이다.

| # | 항목 | 합격 조건 |
|---|---|---|
| K0 | 그래프 바꾸기 등가 (변환 전 확인, cvimodel 판정과 별개) | 21장에서 새 sscma ONNX와 F-004 sscma ONNX의 출력 최대 절대차 ≤ 1e-4 |
| K1 | 사람 판정 일치 (최고 점수 ≥ 0.5 여부) | 21장 중 19장 이상 (≥ 90%) |
| K2 | 최고 점수 차 (ONNX 최고 점수 ≥ 0.5인 사람 이미지) | 평균 ≤ 0.10, 그리고 이미지마다 ≤ 0.20 |
| K3 | 대응 박스 IoU (ONNX 검출마다 IoU가 가장 큰 cvimodel 검출) | 평균 ≥ 0.80 |
| K4 | 검출 수 | 21장 중 19장 이상에서 같고, 다른 이미지도 차이 ≤ 1 |
| K5 | 사람 없는 이미지 `000000162130.jpg` | cvimodel의 score ≥ 0.5 검출 0개 |

- K1~K5가 모두 맞아야 합격이다.
- K0이 틀리면 그래프 바꾸기 자체가 틀린 것이므로 변환하지 않고 고친다. 이것은 원인 J와 다른 원인이다.
- 판정은 `verify_cvimodel.py`의 종료 코드다(0 = 합격).
- F-004 때의 기준(점수 차 평균 ≤ 0.10, 일치 ≥ 90%, IoU ≥ 0.7)보다 엄격하다.

**바꾸는 그래프 (원인 J 회피):**
- YOLOX 마지막 `Transpose(1175 [1,85,3549] → output [1,3549,85])`를 지운다.
- 대신 `1175`를 **채널 축(axis 1)으로** 자른다: xy 0:2, wh 2:4, obj 4:5, person 5:6.
- 디코딩은 `[1,k,3549]` 배치로 한다. grid는 `[1,2,N]`, stride는 `[1,1,N]`이다.
- 결과를 axis 1로 Concat해 `[1,6,3549]`를 만들고, axis 2로 0 패딩해 `[1,6,10647]`로 늘린다.
- **맨 끝에서만** Transpose해 `output_sscma [1,10647,6]`을 만든다. sscma-node가 받는 모양은 그대로다.

### 8.2 결과 — **불합격 → 모델 경로 D로 마감 (5회째 없음)**

| 단계 | 명령 / 산출 | 종료 코드 | 결과 |
|---|---|---|---|
| 기준 커밋 | `2da6706` (8.1 기준 + `verify_cvimodel.py`) | — | 변환 전에 기록 |
| 그래프 바꾸기 | `yolox_to_sscma.py` 커밋 `7b6f254` | — | 원래 Transpose를 지우고 채널 축으로 자른 뒤 끝에서만 Transpose |
| K0 등가 | onnxruntime, 21장, 새 ONNX vs F-004 ONNX | 0 | **최대 절대차 0.000** (출력 `[1,10647,6]`) · `f004b-k0.log` |
| 변환 | `slot --label F-004b-model -- bash firmware/models/convert-yolox-person.sh` (`OUT_DIR=…/models-candidate`, deploy 시험 옵션은 빼서 원인 H를 피함, 커밋 `f92d506`) | **0** (130 s) | cvimodel sha256 `f9920f9e0e12b0dc4ea15cbe876b65698735cf41f1b212b50544ae4d690d02fe` (1,290,224 B) · `f004b-model-1.log` |
| 검증 | `verify_cvimodel.py … 20 …/000000162130.jpg` | **1** | **VERIFY FAILED** · `f004b-verify-1.log` |

**입력 해시:**
- 원본 `yolox_nano.onnx`: `c789161ed43c8269fcd4e67c67eeeb4e80c622da2eb296a20bc6007bd18a0b7d`.
- 새 sscma ONNX: `e475ee4e0e1fd44018662f8a697f30231279b385cf255c08b43690a3b628f010`.
- F-004 sscma ONNX: `b81424be9f5c68cdbd0413cef25dd96c4ed862ed1ec700a8f28af4e52a2086fc`.

**K 판정 (기준 그대로):**

| # | 값 | 판정 |
|---|---|---|
| K1 판정 일치 | 11/21 = 52.4 % | FAIL |
| K2 점수 차 (사람 이미지 10장) | 평균 0.842, 최대 0.925 | FAIL |
| K3 대응 박스 IoU (ONNX 검출 24개) | 평균 0.000 (cvimodel 검출 없음) | FAIL |
| K4 검출 수 같음 | 11/21, 최대 차 7 | FAIL |
| K5 사람 없는 이미지 | 검출 0 | ok |

ONNX 최고 점수가 0.66~0.93인 사람 이미지 10장에서도 cvimodel 최고 점수는 ≤ 0.009다. 이는 F-004의 실패 3회와 같은 모양이다.

**하강 단계 비교** (`firmware/models/stage_compare.py`, `000000085329.jpg`, float top MLIR vs cvimodel 호스트 모의 · `f004b-stages-4.log`):
- cvimodel 덤프는 층 묶음 때문에 헤드 `1158_Reshape`(stride 8, `[85,2704]`, Slice 앞)와 최종 출력만 남는다.
- tpu 단계 MLIR(`*_int8_sym_tpu.mlir`)은 가중치 npz 이름이 맞지 않아(`…_tpu_weights.npz` 없음) 실행되지 않아 비교에서 뺐다.

| 텐서 | float top | cvimodel | cos |
|---|---|---|---|
| 최종 col0·col1 (x, y) | 0~1.01 | 0~0.99 | **0.999** |
| 최종 col2·col3 (w, h) | max 1.34 / 1.31 | max 1.17 / 1.03 | 0.83 / 0.80 |
| 최종 col4 (score = obj·person) | max 0.932 | max 0.009 | **0.000** |
| 최종 col5 (person) | max 0.940 | max 0.561 | 0.45 |
| 헤드 ch4 obj (Slice 앞) | max 0.394 | **전부 0** | **0.000** |
| 헤드 ch5 person | max 0.591 | max 0.453 | 0.46 |
| 헤드 ch6~84 다른 클래스 | max 0.759 | max 0.340 | 0.22 |
| 헤드 ch0~3 reg | — | — | 0.51 / 0.46 / 0.92 / 0.86 |

**원인 다시 판정:**
- 이번에는 Slice가 맞는 채널을 집는다. x·y 열 cos가 0.999이고, 최종 열과 헤드 채널이 대응한다.
- 그러므로 F-004의 원인 J(Transpose 뒤 마지막 축 Slice)는 **틀린 판정**이었다.
- 실제로 틀어지는 곳은 **Slice 앞 YOLOX 헤드 출력**이다. cvimodel에서 obj(sigmoid) 채널이 전부 0이고, 클래스·reg 채널도 cos 0.2~0.9로 무너진다.
- F-004 실패 3(BF16)도 같은 모양이었으므로 INT8 보정표만의 문제는 아닐 수 있다. 헤드 쪽 sigmoid·Concat의 cv181x 하강이 의심되지만 **확인하지 않았다.** 층 묶음 때문에 덤프에 중간 층이 없다.
- 이 근거로 지시대로 **D로 마감**한다. 같은 계통의 5회째 변환은 돌리지 않는다.

**출하:**
- cvimodel `f9920f9e…`는 `…/openhw-tools/models-candidate/`에만 있다.
- `apply-f004.sh`가 읽는 `…/openhw-tools/models/`는 비어 있다. 그러므로 이미지에는 들어가지 않는다.
- 이미지는 F-004 그대로다(`out-f004`, 모델 없음, emmc.zip `82012afe…`).
- 합격하지 않았으므로 persond 모델 연결, 호스트 시험 재실행, 이미지 재빌드는 하지 않았다.
- 네트워크는 닫힘 기본을 그대로 유지한다.

**다음 시도를 한다면 (orch·사용자 결정, 하지 않음):**
1. 층 묶음 없이(`--debug`·`compare_all`) 헤드 층별로 비교해 처음 틀어지는 층을 찾는다.
2. 헤드 sigmoid·Concat 앞 층을 F32/BF16으로 두는 혼합 정밀도(`--quantize_table`)로 변환한다.
3. obj·cls sigmoid를 그래프 밖(persond 또는 후처리)으로 빼고 logit을 출력한다.
