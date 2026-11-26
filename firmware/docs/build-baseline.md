# F-002 reCamera-OS 0.2.4 원본 기준 빌드

- 배정: orch t18r F-002 · 작성: firmware t18w · 레인 t-20261126-161240-92e6 · 날짜 2026-11-26
- **상태: 미완료.** 3번째와 4번째(-j4) 빌드가 모두 호스트 메모리 부족으로 멈췄다. Claude Code가 백그라운드 명령을 중단했고, 빌드 오류나 VM 안의 OOM은 아니다. 다시 시작은 지시를 받은 뒤 한다.
- 소스는 바꾸지 않았다. 빌드 산출물이 아직 없어 해시도 없다. 보드가 없어 **HIL은 미검증**이다. 빌드가 성공해도 실물 동작을 뜻하지 않는다.

## 호스트 환경

| 항목 | 값 |
|---|---|
| OS | Windows 11 Pro 10.0.26200 |
| Docker | Docker Desktop, client/server 29.2.1, WSL2 백엔드(`docker-desktop` 배포판). 작업 시작 때 꺼져 있어 켰다 |
| Docker 자원 | CPU 32, 메모리 31.2 GiB(VM 할당) |
| 호스트 메모리 | 총 64 GB. 3번째 시도 중단 직후 여유 약 3.3 GB, `vmmemWSL` 약 27 GB(다른 WSL 배포판 `gop-ha-b`와 다른 프로젝트 컨테이너 약 30개가 함께 씀) |
| 디스크 | C: 여유 147 GB(Docker VHDX 위치) · E: 여유 2.8 TB |
| 소스 위치 | Docker 이름 볼륨 `openhw-recamera-sdk` (`/work/src`) — 저장소 밖 |
| 로그·산출물 위치 | `C:/Users/gh/.local/share/openhw-tools/recamera-sdk/` (`clone.log`, `image.log`, `build-1~3.log`, `serial-1.log`) |

## 소스

| 항목 | 값 |
|---|---|
| 저장소 | https://github.com/Seeed-Studio/reCamera-OS |
| 태그 | 0.2.4 |
| 체크아웃한 커밋 | `01debc9967752448e29a745f37d29d80a4a41e37` (태그 0.2.4 커밋과 같음, `gh api .../git/ref/tags/0.2.4`로 확인) |
| 서브모듈 | 0.2.4가 고정한 커밋 그대로 받았다(`git submodule update --init --recursive --depth 1`) |
| 빌더 이미지 | `recamera-os-builder` — 0.2.4의 `.devcontainer/Dockerfile` 그대로(buildpack-deps:noble-curl 기반) |
| 대상 | `sg2002_recamera_emmc` |

## 명령

재현 스크립트는 `firmware/scripts/build-baseline.sh`이다. 단계별로 하나씩 돌리며, 무거운 단계는 모두 PC 공용 줄(`slot`)에 세웠다.

```
node harness/cli.js slot -- bash firmware/scripts/build-baseline.sh clone
node harness/cli.js slot -- bash firmware/scripts/build-baseline.sh image
node harness/cli.js slot --label F-002-build --timeout-min 180 -- bash firmware/scripts/build-baseline.sh build
node harness/cli.js slot --label F-002-serial --timeout-min 30 -- bash firmware/scripts/build-baseline.sh serial   # 실패 #2 대응
node harness/cli.js slot -- bash firmware/scripts/build-baseline.sh collect   # 아직 돌리지 않음
```

`build` 단계는 `docker_build.sh`의 내부 단계(submodule update → `make sg2002_recamera_emmc`)를 같은 이미지에서 그대로 돌린다. 다른 점은 소스를 바인드 마운트 대신 이름 볼륨에 둔 것과, `-it` 없이 비대화형으로 돌린 것뿐이다.

## 실행 기록

| # | 단계 | 시작(KST) | 소요 | 종료 코드 | 결과 |
|---|---|---|---|---|---|
| 0a | clone | 16:15 | 약 1분 | 0 | HEAD `01debc99` |
| 0b | image | 16:16 | 약 3분 | 0 | `recamera-os-builder:latest` |
| 1 | build | 16:19:51 | 907초 | **124** | `slot` 기본 제한 15분 초과로 중단(아래 원인 A) |
| 2 | build | 16:36 | 227초 | **2** | buildroot `wireless_tools` 링크 오류(아래 원인 B) |
| 2' | serial | 16:44 | 약 1분 | 0 | `wireless_tools`를 `-j1`로 먼저 빌드 |
| 3 | build | 16:46 | — | 없음(강제 종료) | 호스트 메모리 부족으로 Claude Code가 백그라운드 명령을 중단했다(아래 원인 C). 로그 마지막은 `ive` 샘플 링크(`sample_thresh_U16`) |
| 4 | build (`CPUSET=0-3`, nproc 4 = -j4, orch O-19) | 16:47:33 | 약 37분 | 없음(강제 종료) | 원인 C 2회째. 시작 때 VM `free -m` available 28,181MB. 17:25에는 VM used 25,437MB / available 5,832MB, 빌드 컨테이너 단독 21.37GiB였다. buildroot가 V8(`obj/deps/v8/... [1118/2096]`)과 ffmpeg를 함께 컴파일하던 중이다. VM `dmesg`에 oom 줄은 없다. slot과 bash가 끝난 뒤에도 컨테이너 `ab48b7011bc5`가 줄 밖에서 계속 돌아 `docker stop` 했다. 정지 뒤 VM available 28,221MB, 호스트 여유 6,951MB |

## 실패 원인 판정 (원인마다 따로 센다)

| 원인 | 횟수 | 근거 | 판정 | 조치 |
|---|---|---|---|---|
| A. slot 시간 제한 | 1 | `build-1.log` 8043행 `[pilot] slot: ... ran past 15 min — stopping it` | 빌드 오류 아님. `slot` 기본 제한이 15분 | `--timeout-min 180`. **부작용:** slot이 bash만 끝내서 빌더 컨테이너는 줄 밖에서 계속 돌았다 → 직접 `docker stop` |
| B. wireless_tools 병렬 빌드 경합 | 1 | `build-2.log` 20531–20540행: `/usr/bin/ld: iwmulticall.o: Relocations in generic ELF (EM: 243)` → `file in wrong format` → `make[3]: *** [...wireless_tools-30.pre9/.stamp_target_installed] Error 2`. 141개 패키지 중 이 패키지만 `.stamp_built`(07:39:13)가 `.stamp_configured`(07:39:36)보다 이르다. SDK `build/Makefile` 600행은 buildroot를 `make -j${NPROC}`(32)로 돌리고, `.config`는 `BR2_PER_PACKAGE_DIRECTORIES=y`이다 | RISC-V 오브젝트(EM 243)를 설치 단계에서 호스트 `gcc`가 다시 링크했다. 병렬 실행 중 `iwmulticall.o`가 다시 만들어져 생긴 경합으로 판정 | 소스는 그대로 두고 `wireless_tools-dirclean wireless_tools`를 `-j1`로 먼저 빌드했다(종료 코드 0). 3번째 시도에서는 이 지점을 넘었다 |
| C. 호스트 메모리 부족 | **2** (3·4번째 시도) | 4번째 시도: -j4인데도 V8 컴파일 단계에서 빌드 컨테이너가 21.37GiB까지 커졌다. VM은 31.2GiB 한도 안이라 OOM은 없었지만, VM 메모리(vmmemWSL)가 늘면서 호스트 여유가 줄어 Claude Code가 명령을 중단했다. 3번째 시도의 근거는 다음과 같다: | Claude Code 알림: "stopped because the system is running low on memory". 직후 여유 3.3 GB / 64 GB, `vmmemWSL` 27 GB | 빌드 오류 아님. 다른 프로젝트의 WSL 배포판과 컨테이너가 같은 VM 메모리를 쓰고 있음 | 다시 시작하지 않았다. 줄 밖에 남은 빌더 컨테이너는 직접 `docker stop` 했다 |

## 다시 시작하는 방법 (지시 후)
- 볼륨에 빌드 중간 결과가 남아 있어 `build` 단계는 이어서 진행된다.
- 메모리를 확보하려면 다음 두 가지 중 하나가 필요하다. Docker Desktop `.wslconfig`의 메모리 상한이나 다른 프로젝트 컨테이너 정리는 사용자가 정할 일이다.
  - 빌드 병렬도를 낮춰 다시 시작한다. 예: `docker run --cpus`나 `NPROC` 제한. 이 경우 내부 명령이 원본과 달라지므로 분기점으로 기록한다.
  - 다른 작업이 적은 시간에 다시 시작한다.
- 성공하면 `collect` 단계를 돌린다. 이 단계는 `*_emmc.zip`, `*_ota.zip`, `*_recovery.zip`, `*_sd_compat.zip`을 위 로그 폴더의 `out-0.2.4/`에 복사하고 sha256을 출력한다.

## 산출물

| 파일 | 크기 | sha256 |
|---|---|---|
| (아직 없음) | — | — |

## 분기점·선택·이유·차선책

| # | 분기점 | 선택 | 이유 | 차선책 |
|---|---|---|---|---|
| B1 | 소스 위치 | Docker 이름 볼륨 | `docker_build.sh`는 소스 폴더를 바인드 마운트한다. Windows NTFS는 대소문자를 구분하지 않고 심볼릭 링크와 권한이 달라 buildroot가 깨질 위험이 있고 느리다. 저장소 밖 조건도 맞는다 | 바인드 마운트로 `docker_build.sh`를 그대로 실행(Git Bash). 또는 전용 WSL 배포판 |
| B2 | 비대화형 실행 | `-it` 없이 같은 내부 단계 | `slot` 아래에는 TTY가 없다 | — |
| B3 | wireless_tools 경합 | 그 패키지만 `-j1`로 먼저 빌드 | 소스와 SDK Makefile을 바꾸지 않는 가장 작은 조치다 | buildroot 전체를 `-j1`로(느림) |
| B4 | 메모리 부족 뒤 | 다시 시작하지 않고 보고 | 메모리가 여전히 부족할 수 있다. 다시 시작은 지시를 받고 한다 | 병렬도를 낮춰 다시 시작 |

## 하네스 관찰 (bug_report: off라 기록만 남김)
- `slot`이 시간 제한으로 명령을 끝낼 때 자식 `docker run` 컨테이너는 끝나지 않는다. 그 결과 PC 공용 줄 밖에서 작업이 계속 돈다.
