# F-002 reCamera-OS 0.2.4 원본 기준 빌드

- 배정: orch t18r F-002 · 작성: firmware t18w · 레인 t-20261126-161240-92e6 · 날짜 2026-11-26
- **상태: 빌드 성공 (종료 코드 0).** 9번째 시도에서 성공했다. 18:55:12에 시작해 20:27:47 KST에 끝났다(5,553초). 아래 산출물 6개를 모으고 sha256을 냈다.
- 소스는 바꾸지 않았다(DTS·드라이버·앱 모두). 바꾼 것은 빌드 실행 방식뿐이고, 아래 분기점 표에 적었다.
- 보드가 없어 **HIL은 미검증**이다. 빌드가 성공했다고 실물에서 동작한다는 뜻은 아니다. 굽기와 부팅은 하지 않았다.

## 호스트 환경

| 항목 | 값 |
|---|---|
| OS | Windows 11 Pro 10.0.26200 |
| Docker | Docker Desktop, client/server 29.2.1, WSL2 백엔드(`docker-desktop` 배포판, 커널 6.6.87.2-microsoft-standard-WSL2). 작업 시작 때 꺼져 있어 켰다 |
| Docker VM | CPU 32 · 메모리 31.2 GiB · 스왑 8 GiB. 빌드 직전 `wsl -d docker-desktop -- free -m`에서 available 약 28 GB |
| 호스트 메모리 | 총 64 GB. 여유가 3~7 GB까지 내려간다. `vmmemWSL` 약 27 GB 중 대부분은 VM 페이지 캐시다. 같은 시간에 다른 WSL 배포판과 다른 프로젝트 컨테이너 약 30개(합 약 1.5 GB)가 돌았다 |
| 디스크 | C: 여유 147 GB(Docker VHDX가 있는 곳) · E: 여유 2.8 TB. 빌드 볼륨은 36.85 GB를 쓴다 |
| 소스·중간 결과 | Docker 이름 볼륨 `openhw-recamera-sdk` (`/work/src`) — 저장소 밖 |
| 로그·산출물 | `C:/Users/gh/.local/share/openhw-tools/recamera-sdk/` — `clone.log`, `image.log`, `build-1~9.log`, `build-N.result`, `serial-1.log`, `dmesg-7.txt`, `run-build-5.sh`(hc 칸 실행기), `out-0.2.4/`(산출물) |

## 소스

| 항목 | 값 |
|---|---|
| 저장소 | https://github.com/Seeed-Studio/reCamera-OS |
| 태그 | 0.2.4 |
| 체크아웃한 커밋 | `01debc9967752448e29a745f37d29d80a4a41e37` (`gh api .../git/ref/tags/0.2.4`로 본 태그 커밋과 같다) |
| 서브모듈 | 0.2.4가 고정한 커밋 그대로(`git submodule update --init --recursive --depth 1`) |
| 빌더 이미지 | `recamera-os-builder` — 0.2.4의 `.devcontainer/Dockerfile`을 그대로 썼다(buildpack-deps:noble-curl 기반) |
| 대상 | `sg2002_recamera_emmc` |

## 성공한 명령 (재현)

재현 스크립트는 `firmware/scripts/build-baseline.sh`이다. 무거운 단계는 모두 PC 공용 줄(`slot`)에 세웠다. 빌드는 Claude 백그라운드 셸이 아니라 hc 칸 `openhw-fw-build`에서 일반 프로그램으로 돌렸다(orch O-29).

```
node harness/cli.js slot -- bash firmware/scripts/build-baseline.sh clone
node harness/cli.js slot -- bash firmware/scripts/build-baseline.sh image
node harness/cli.js slot --label F-002-serial --timeout-min 30 -- bash firmware/scripts/build-baseline.sh serial   # 원인 B 대응 (wireless_tools -j1 선빌드)
# hc run --bg --name openhw-fw-build --cwd <레인> --outlive-parent --no-notify -- "C:\Program Files\Git\bin\bash.exe" run-build-5.sh
#   그 안에서 실행:
CPUSET=0-3 MEM=16g JLEVEL=4 node harness/cli.js slot --label F-002 --timeout-min 240 -- "C:/Program Files/Git/bin/bash.exe" firmware/scripts/build-baseline.sh build
node harness/cli.js slot --label F-002-collect -- bash firmware/scripts/build-baseline.sh collect
```

- `build`는 `docker_build.sh` 안의 단계(submodule update → `make sg2002_recamera_emmc`)를 같은 이미지에서 그대로 돌린다. 원본과 다른 점은 네 가지다.
  - `docker run --cpuset-cpus 0-3 --memory 16g --memory-swap 16g`로 CPU와 메모리를 묶었다.
  - `make`에 `BR2_JLEVEL=4`를 붙였다.
  - 소스를 바인드 마운트 대신 이름 볼륨에 두었다.
  - `-it` 없이 비대화형으로 돌렸다.
- **이어 빌드였다.** 9번째 시도는 앞선 시도들이 볼륨에 남긴 중간 결과 위에서 이어 갔다. 빈 볼륨에서 처음부터 한 번에 끝까지 돌려 본 적은 없다. 앞 시도들의 차이는 병렬도와 같은 실행 조건뿐이고 소스와 설정은 같다.

## 산출물 (`out-0.2.4/`, 컨테이너 안 `output/sg2002_recamera_emmc/install/soc_sg2002_recamera_emmc/`)

| 파일 | 크기(바이트) | sha256 |
|---|---|---|
| `sg2002_reCamera_0.2.4_emmc.zip` | 151,383,454 | `cc46cb9b0bfcbe30e1a33b080ecca2823e43521e6af671c5a8628c7c1829df12` |
| `sg2002_reCamera_0.2.4_emmc_ota.zip` | 150,165,698 | `967340af3e639a5950d09c2dc65c689098aa74f409c2dcab23582813e9512457` |
| `sg2002_reCamera_0.2.4_emmc_recovery.zip` | 611,823 | `020acd1c70f8e5d3c33815bc2f9f9da4e65a5afd43cbf007e23842d52ebed256` |
| `sg2002_reCamera_0.2.4_emmc_sd_compat.zip` | 146,801,863 | `b7033ec235ebe7c8fe1719dbd23912a77ae780497e4f96956be18b94bd2ab6d7` |
| `sg2002_reCamera_0.2.4_emmc_swu.zip` | 146,794,696 | `febb57e4379dd3f5a4a87afeb31acec8e27025a1916c897356580e8195be49cc` |
| `upgrade.zip` | 151,383,454 | `cc46cb9b...` (emmc.zip과 같은 파일) |

- 빌드할 때마다 시각이 들어가므로 같은 소스로 다시 빌드해도 해시가 같다는 보장은 없다(재현성 미검증).
- Seeed가 배포한 0.2.4 이미지와 해시를 비교하지 않았다. 배포 파일을 받지 않았다.

## 실행 기록

| # | 단계 / 조건 | 시작(KST) | 소요 | 종료 코드 | 결과 |
|---|---|---|---|---|---|
| 0a | clone | 16:15 | 약 1분 | 0 | HEAD `01debc99` |
| 0b | image | 16:16 | 약 3분 | 0 | `recamera-os-builder:latest` |
| 1 | build, 제한 없음 | 16:19:51 | 907초 | **124** | 원인 A |
| 2 | build, 제한 없음 | 16:36 | 227초 | **2** | 원인 B |
| 2' | serial (`wireless_tools` -j1) | 16:44 | 약 1분 | 0 | 원인 B 조치 |
| 3 | build, 제한 없음, Claude 백그라운드 | 16:46 | — | 없음(강제 종료) | 원인 C |
| 4 | build `CPUSET=0-3`, Claude 백그라운드 | 16:47:33 | 약 37분 | 없음(강제 종료) | 원인 C. 남은 컨테이너 `ab48b701`을 직접 stop |
| 5 | build, hc 칸 t192 | 17:30 | 0초 | **1** | 원인 E |
| 6 | build `CPUSET=0-3 MEM=16g`, hc t193 | 17:31:48 | 346초 | **2** | 원인 D |
| 7 | build `CPUSET=0-1 MEM=16g`, hc t194 | 17:38:55 | 302초 | **2** | 원인 D. 원인을 고치지 못한 재시도였다(아래 설명) |
| 8 | build `CPUSET=0-3 MEM=16g JLEVEL=2`, hc t195 | 17:47:56 | 약 67분 | 없음(계획 중단) | OOM은 없었다(컨테이너 2.7 GiB). 속도가 느려 240분 제한을 넘길 것 같아 직접 멈췄다. `hc kill`로 docker CLI가 함께 끝나 남은 컨테이너는 없었다 |
| **9** | build `CPUSET=0-3 MEM=16g JLEVEL=4`, hc t196 | 18:55:12 | **5,553초** | **0** | `Run gen_md5sum` → `Success` |
| 10 | collect | 20:28 | 약 1분 | 0 | 위 산출물과 sha256 |

## 실패 원인 판정 (원인마다 따로 센다, 상한은 원인마다 3회)

| 원인 | 횟수 | 근거 | 판정 | 조치 |
|---|---|---|---|---|
| A. slot 시간 제한 | 1 | `build-1.log` 8043행 `[pilot] slot: ... ran past 15 min — stopping it` | 빌드 오류가 아니다. `slot`의 기본 제한이 15분이다 | `--timeout-min 180`, 이후 240 |
| B. wireless_tools 병렬 경합 | 1 | `build-2.log` 20531–20540행 `/usr/bin/ld: iwmulticall.o: Relocations in generic ELF (EM: 243)` → `file in wrong format` → `.stamp_target_installed] Error 2`. 141개 패키지 가운데 이 패키지만 `.stamp_built`가 `.stamp_configured`보다 이르다 | 병렬 실행 중 RISC-V 오브젝트를 설치 단계에서 호스트 `gcc`가 다시 링크했다 | `wireless_tools-dirclean wireless_tools`를 `-j1`로 먼저 빌드. 이후 다시 나지 않았다 |
| C. 호스트 메모리 압박으로 Claude Code가 명령을 끝냄 | 2 | Claude Code 알림 "stopped because the system is running low on memory". 4번째 시도 때 컨테이너 21.37 GiB, VM available 5,832 MB, VM `dmesg`에 OOM 없음 | 빌드 오류가 아니다. 무거운 명령을 Claude 백그라운드 셸에서 돌린 실행 방식이 문제였다 | 빌드를 hc 칸에서 일반 프로그램으로 돌렸다(O-29). 이후 Claude가 끝낸 것은 대기 명령 하나뿐이었고, 빌드는 계속 돌았다(orch 판단에 따라 횟수에 넣지 않음) |
| D. 컨테이너 메모리 상한 초과(OOM) | 2 | VM `dmesg`(`dmesg-7.txt`): `Memory cgroup out of memory: Killed process ... (cc1plus) ... anon-rss:795432kB`, `memory: usage 16777216kB, limit 16777216kB`. 로그 `g++: fatal error: Killed signal terminated program cc1plus`. nodejs(V8)를 컴파일하던 중이었다 | buildroot의 `package/Makefile.in`은 `BR2_JLEVEL=0`일 때 `PARALLEL_JOBS = 1 + getconf _NPROCESSORS_ONLN`이다. `getconf`는 cpuset을 무시한다(컨테이너 안 `nproc`=2, `getconf`=32). 그래서 nodejs가 `ninja JOBS=33`으로 돌았고, cc1plus 하나가 약 0.8 GB를 써서 16 GB를 넘었다. **7번째 시도(CPUSET 0-1)는 이 원인을 바꾸지 못했다** — 근본 원인을 찾기 전의 재시도였다 | `make`에 `BR2_JLEVEL=N`을 붙였다. 명령줄 변수는 MAKEFLAGS로 하위 make에 넘어가 `.config` 값을 덮는다(작은 Makefile로 확인: 넘기면 2, 넘기지 않으면 33). 8·9번째 시도에서는 OOM이 없었다 |
| E. hc 칸의 실행 환경 | 1 | `build-5.log`: "The command 'docker' could not be found in this WSL 2 distro". `date`도 없었다 | Git `usr/bin/bash.exe`로 띄우자 PATH가 비었고, `bash`가 기본 WSL 배포판(다른 프로젝트용)의 bash로 잡혔다. 그 배포판에서는 스크립트가 `docker`를 찾지 못하고 바로 끝났으며, 바뀐 것은 없다 | Git `bin/bash.exe`를 쓰고, 공용 줄 명령에 bash 전체 경로를 넣었다 |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | 소스 위치 | Docker 이름 볼륨 | `docker_build.sh`는 소스를 바인드 마운트한다. NTFS는 대소문자를 구분하지 않고 심볼릭 링크와 권한이 달라 buildroot가 깨질 위험이 있고 느리다. 저장소 밖에 둔다는 조건도 맞춘다 | `docker_build.sh`를 그대로 실행(Git Bash 바인드). 전용 WSL 배포판 |
| B2 | 비대화형 | `-it` 없이 같은 내부 단계 | `slot` 아래에는 TTY가 없다 | — |
| B3 | wireless_tools 경합 | 그 패키지만 `-j1`로 먼저 빌드 | 소스와 Makefile을 바꾸지 않는 가장 작은 조치다 | 전체를 `BR2_JLEVEL=1`로 |
| B4 | 실행 주체 | hc 칸에서 일반 프로그램으로(orch O-29) | Claude 백그라운드 셸은 호스트 메모리 압박 때 강제로 끝난다 | 사용자 셸 |
| B5 | 메모리 상한 | `--memory 16g --memory-swap 16g`(O-29) | VM과 호스트를 보호하고, 초과는 OOM으로 판정할 수 있다 | 12g |
| B6 | 병렬도 | `CPUSET=0-3`(SDK `NPROC`=4) + `BR2_JLEVEL=4` | `nproc`과 `getconf`가 달라 두 곳을 모두 정해야 한다. JLEVEL 2는 컨테이너 2.7 GiB로 안전했지만 V8에만 2시간 넘게 걸려 240분 제한을 넘길 위험이 있었다. 4로 올린 뒤에도 OOM은 없었다 | `BR2_JLEVEL=2`(느림) |

## 남은 일 / 미검증
- HIL: 보드를 받은 뒤 `*_recovery.zip`이나 USB 굽기로 부팅, 콘솔, 이더넷, 카메라를 확인해야 한다(F-003 이후).
- 빈 볼륨에서 처음부터 한 번에 빌드하는 것, 같은 해시가 다시 나오는지: 확인하지 않았다.
- 볼륨 `openhw-recamera-sdk`(36.85 GB)는 F-003 이어 빌드를 위해 그대로 두었다.

## 하네스 관찰 (bug_report: off라 기록만 남김)
- `slot`이 시간 제한으로 명령을 끝낼 때 자식 `docker run` 컨테이너는 끝나지 않는다. 그래서 PC 공용 줄 밖에서 작업이 계속 돌았다(1·3·4번째 시도).
