#!/usr/bin/env bash
# F-002 reCamera-OS 원본 기준 빌드 (수정 없음).
# docker_build.sh 와 같은 이미지(.devcontainer/Dockerfile)·같은 내부 단계(submodule update --depth 1 → make <target>)를
# 쓰되, 소스는 Windows 바인드 마운트(NTFS: 대소문자 무시·심볼릭 링크 문제) 대신 Docker 이름 볼륨에 둔다.
# 사용: bash firmware/scripts/build-baseline.sh [step]   step = all|clone|image|build|collect (기본 all)
set -euo pipefail
export MSYS_NO_PATHCONV=1

TAG="${TAG:-0.2.4}"
TARGET="${TARGET:-sg2002_recamera_emmc}"
REPO="https://github.com/Seeed-Studio/reCamera-OS.git"
VOL="${VOL:-openhw-recamera-sdk}"
IMAGE="recamera-os-builder"
OUT_DIR="${OUT_DIR:-$HOME/.local/share/openhw-tools/recamera-sdk/out-$TAG}"
command -v cygpath >/dev/null && OUT_DIR="$(cygpath -m "$OUT_DIR")"   # Docker -v 용 Windows 경로
STEP="${1:-all}"
# CPUSET: 빌드 컨테이너가 쓸 CPU. SDK Makefile 은 NPROC := $(shell nproc) 이라 cpuset 으로 -j 가 정해진다(소스 수정 없음).
CPU_OPT=()
[ -n "${CPUSET:-}" ] && CPU_OPT=(--cpuset-cpus "$CPUSET")
# MEM: 빌드 컨테이너 메모리 상한(orch O-29). 넘으면 컨테이너가 OOM(137)으로 끝난다.
[ -n "${MEM:-}" ] && CPU_OPT+=(--memory "$MEM" --memory-swap "$MEM")
# JLEVEL: buildroot 패키지별 병렬도. .config 의 BR2_JLEVEL=0 은 getconf _NPROCESSORS_ONLN(cpuset 무시, 32)+1 이라
# nodejs(V8) 가 ninja -j33 으로 돈다(원인 D). make 명령줄 변수는 MAKEFLAGS 로 하위 make 에 넘어가 .config 값을 덮는다.
MAKE_VARS=""
[ -n "${JLEVEL:-}" ] && MAKE_VARS="BR2_JLEVEL=$JLEVEL"

clone() {
  docker volume create "$VOL" >/dev/null
  docker run --rm -v "$VOL":/work buildpack-deps:noble-scm bash -c "
    set -e
    if [ ! -d /work/src/.git ]; then git clone --branch $TAG --depth 1 $REPO /work/src; fi
    chown -R 1000:1000 /work
    cd /work/src && git -c safe.directory=/work/src rev-parse HEAD"
}

image() {
  # Dockerfile 은 COPY 가 없어 빈 컨텍스트로 빌드할 수 있다.
  docker run --rm -v "$VOL":/work buildpack-deps:noble-scm cat /work/src/.devcontainer/Dockerfile \
    | docker build -t "$IMAGE" -
}

build() {
  docker run --rm "${CPU_OPT[@]}" -v "$VOL":/work --workdir /work/src -e HOME=/work/home "$IMAGE" bash -c '
    set -e
    id builder >/dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash builder
    mkdir -p /work/home && chown -R 1000:1000 /work/home
    cat > /tmp/inner.sh <<EOF
#!/bin/bash
set -e
git config --global --add safe.directory "*"
echo ">>> 1. Git submodule update..."
git submodule update --init --recursive --depth 1
echo ">>> 2. make '"$TARGET $MAKE_VARS"'"
make '"$TARGET $MAKE_VARS"'
EOF
    chmod +x /tmp/inner.sh
    sudo -E -u builder HOME=/work/home /tmp/inner.sh'
}

# SDK 는 buildroot 를 make -j$(nproc) 로 돌린다. wireless_tools 의 Makefile 은 병렬에 안전하지 않아
# 설치 단계에서 RISC-V 오브젝트를 호스트 gcc 로 다시 링크하다 실패했다(build-baseline.md 실패 기록 #2).
# 소스는 바꾸지 않고, 그 패키지만 지우고 -j 없이 먼저 빌드한 뒤 build 를 다시 돌린다.
serial_pkgs() {
  docker run --rm -v "$VOL":/work --workdir /work/src/output/$TARGET/buildroot-2021.05 "$IMAGE" bash -c '
    set -e
    id builder >/dev/null 2>&1 || useradd -m -u 1000 -s /bin/bash builder
    O=$(ls -d output/cvitek_*)
    sudo -u builder HOME=/work/home make -j1 O=$O wireless_tools-dirclean wireless_tools'
}

collect() {
  mkdir -p "$OUT_DIR"
  docker run --rm -v "$VOL":/work -v "$OUT_DIR":/out "$IMAGE" bash -c "
    set -e
    d=\$(ls -d /work/src/output/$TARGET/install/soc_* | head -1)
    cp \$d/*.zip /out/
    cd /out && ls -l *.zip && sha256sum *.zip"
}

case "$STEP" in
  clone) clone ;; image) image ;; build) build ;; serial) serial_pkgs ;; collect) collect ;;
  all) clone; image; build; collect ;;
  *) echo "unknown step: $STEP" >&2; exit 2 ;;
esac
