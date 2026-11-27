#!/usr/bin/env python3
"""F-007 ① RTSP 수신 · 녹화 · FPS/끊김 측정 (PC 쪽, 표준 라이브러리 + ffprobe/ffmpeg).

  rtsp_check.py probe  <URL|파일> [--seconds 20 (첫 패킷부터)] [--expect-fps 15] [--max-gap 0.5]
      비디오 패킷 pts 로 FPS · 최대 간격을 재고, 실시간 수신 비율(pts 길이 ÷ 실제 걸린 시간)을 본다.
      판정(종료 코드 0 = 합격): FPS ≥ 0.9 × expect · 최대 간격 ≤ max-gap · (URL 이면) 실시간 비율 ≥ 0.9
      1 = 기준 불합격, 2 = 수신 실패(패킷 0 · ffprobe 오류)
  rtsp_check.py record <URL> <출력.mkv> [--seconds 60]      재인코딩 없이 녹화(-c copy)
  rtsp_check.py latency <URL> <출력.png>
      프레임 1장을 받은 PC 시각을 파일 이름 옆 .txt 에 남긴다. 카메라가 PC 화면의 ms 시계를 찍게 하고
      사진 속 시계와 비교한다(사람 눈 — verifiable 아니오).
근거: 절차서 bringup-checklist.md 3-2(720p 15fps, persond cam_fps=15) · 1-9(RTSP 부하).
비밀번호가 든 URL 은 출력에서 가린다(D-003 #30 — rtsp_pass 는 시험 동안만).
ffprobe/ffmpeg 위치: --ffmpeg-dir <bin 폴더> (하위 명령 앞) 또는 환경 변수 OPENHW_FFMPEG_DIR, 없으면 PATH.
  예) python rtsp_check.py --ffmpeg-dir <ffmpeg bin 폴더> probe x.mkv
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import threading
import time


def mask(url):
    return re.sub(r"//([^:/@]+):[^@]*@", r"//\1:***@", url)


FFMPEG_DIR = os.environ.get("OPENHW_FFMPEG_DIR", "")   # --ffmpeg-dir 가 덮어쓴다


def tool(name):
    # PATH 를 바꾸지 않고 격리 설치한 ffmpeg 를 쓰도록 폴더를 먼저 본다 (F-008)
    p = shutil.which(name, path=FFMPEG_DIR) if FFMPEG_DIR else shutil.which(name)
    if not p:
        sys.exit(f"{name} 없음 — --ffmpeg-dir 또는 OPENHW_FFMPEG_DIR 로 ffmpeg bin 폴더를 준다 (지금: {FFMPEG_DIR or 'PATH'})")
    return p


def is_url(s):
    return "://" in s


def probe(a):
    # 패킷이 올 때마다 PC 시각을 함께 적는다. 실시간 비율은 첫 패킷부터 잰다(ffprobe 스트림 분석 시간 제외).
    cmd = [tool("ffprobe"), "-v", "error"]
    if a.src.startswith("rtsp://"):
        cmd += ["-rtsp_transport", "tcp"]
    cmd += ["-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", a.src]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    first = [None]
    # 첫 패킷 뒤 seconds 동안 받고 끊는다. 첫 패킷이 20초 안에 안 오면 끊는다
    killer = threading.Timer(a.seconds + 20, proc.kill)
    killer.start()
    pts, arr = [], []
    for line in proc.stdout:
        x = line.strip().rstrip(",")
        if not re.fullmatch(r"-?[0-9.]+", x):
            continue
        now = time.monotonic()
        if first[0] is None:
            first[0] = now
            killer.cancel()
            killer = threading.Timer(a.seconds, proc.kill)
            killer.start()
        pts.append(float(x))
        arr.append(now)
    killer.cancel()
    proc.wait()
    err = proc.stderr.read()
    if len(pts) < 2:
        print(f"FAIL 패킷 {len(pts)}개 — {err.strip()[:300]}")
        return 2
    wall = arr[-1] - arr[0]
    pts.sort()
    span = pts[-1] - pts[0]
    fps = (len(pts) - 1) / span if span > 0 else 0.0
    gap = max(b - a_ for a_, b in zip(pts, pts[1:]))
    ok = fps >= 0.9 * a.expect_fps and gap <= a.max_gap
    line = f"src={mask(a.src)} packets={len(pts)} span={span:.2f}s fps={fps:.2f} (기대 {a.expect_fps}) max_gap={gap:.3f}s"
    if is_url(a.src):
        rt = span / wall if wall > 0 else 0.0
        ok = ok and rt >= 0.9
        line += f" realtime={rt:.2f} (pts 길이/첫 패킷부터 실제 {wall:.1f}s)"
    print(("PASS " if ok else "FAIL ") + line)
    return 0 if ok else 1


def record(a):
    cmd = [tool("ffmpeg"), "-v", "error", "-y"]
    if a.src.startswith("rtsp://"):
        cmd += ["-rtsp_transport", "tcp"]
    cmd += ["-i", a.src, "-t", str(a.seconds), "-c", "copy", a.out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(("PASS " if r.returncode == 0 else "FAIL ") + f"record {mask(a.src)} → {a.out} rc={r.returncode} {r.stderr.strip()[:300]}")
    return 0 if r.returncode == 0 else 2


def latency(a):
    cmd = [tool("ffmpeg"), "-v", "error", "-y"]
    if a.src.startswith("rtsp://"):
        cmd += ["-rtsp_transport", "tcp"]
    cmd += ["-i", a.src, "-frames:v", "1", a.out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    t = time.time()
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(t)) + f".{int(t * 1000) % 1000:03d}"
    with open(a.out + ".txt", "w", encoding="utf-8") as f:
        f.write(f"pc_received={stamp}\n")
    print(f"{'PASS' if r.returncode == 0 else 'FAIL'} 프레임 {a.out} · PC 수신 {stamp} — 사진 속 시계와 비교(사람 눈)")
    return 0 if r.returncode == 0 else 2


def main():
    global FFMPEG_DIR
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ffmpeg-dir", default=FFMPEG_DIR, help="ffprobe/ffmpeg 가 든 bin 폴더 (기본: OPENHW_FFMPEG_DIR, 없으면 PATH)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("probe")
    p.add_argument("src")
    p.add_argument("--seconds", type=int, default=20)
    p.add_argument("--expect-fps", type=float, default=15.0)
    p.add_argument("--max-gap", type=float, default=0.5)
    p = sub.add_parser("record")
    p.add_argument("src")
    p.add_argument("out")
    p.add_argument("--seconds", type=int, default=60)
    p = sub.add_parser("latency")
    p.add_argument("src")
    p.add_argument("out")
    a = ap.parse_args()
    FFMPEG_DIR = a.ffmpeg_dir
    return {"probe": probe, "record": record, "latency": latency}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
