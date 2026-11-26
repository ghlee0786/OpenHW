#!/usr/bin/env python3
"""F-007 ④ 12V 입력 전류 기록 CSV 집계 (절차서 1-9, lead #10).

  current_csv.py <기록.csv> [--window-min 30] [--limit 1.9] [--adapter 2.08] [--time-col 이름] [--current-col 이름]
CSV: 첫 줄 머리글. 시간 열(초 숫자 또는 ISO 시각 "2026-11-27 10:00:00")과 전류 열(A 또는 mA).
  열 이름을 안 주면 시간 = time/timestamp/t/시간/시각, 전류 = current/curr/amp/i/전류 가 들어간 첫 열.
  단위: 머리글에 mA 가 있으면 mA, 아니면 A(값 중앙값이 50 넘으면 mA 로 보고 알린다).
출력: 전체 평균 · 피크(표본 최대) · 30분 이동 창 평균의 최댓값 · 표본 간격
판정(종료 코드): 0 = 30분 창 평균 최댓값 ≤ limit(1.9A) · 1 = 넘음(→ 12V 3A급 어댑터 교체, 구매는 사용자 지시)
                2 = 기록이 창보다 짧음 · 형식 오류
  피크가 adapter(GST25A12 2.08A)를 넘으면 경고로 적는다(판정은 평균 — 계약 v1.10 3.2절 ≈1.84A).
"""
import argparse
import bisect
import csv
import datetime as dt
import statistics
import sys

TIME_KEYS = ("time", "timestamp", "시간", "시각")
CUR_KEYS = ("current", "curr", "amp", "전류")


def pick(head, want, keys, exact=("t", "i")):
    if want:
        if want not in head:
            sys.exit(f"열 {want!r} 없음: {head}")
        return want
    for h in head:
        hl = h.lower().strip()
        if hl in exact or any(k in hl for k in keys):
            return h
    sys.exit(f"열을 못 찾음({keys}): {head}")


def to_sec(v):
    try:
        return float(v)
    except ValueError:
        return dt.datetime.fromisoformat(v.strip()).timestamp()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--window-min", type=float, default=30)
    ap.add_argument("--limit", type=float, default=1.9)
    ap.add_argument("--adapter", type=float, default=2.08)
    ap.add_argument("--time-col")
    ap.add_argument("--current-col")
    a = ap.parse_args()
    with open(a.file, newline="", encoding="utf-8-sig") as f:
        rd = csv.DictReader(f)
        head = rd.fieldnames or []
        tc = pick(head, a.time_col, TIME_KEYS)
        cc = pick([h for h in head if h != tc], a.current_col, CUR_KEYS, exact=("i",))   # 시간 열 제외 (timestamp 의 "amp")
        pts = []
        for r in rd:
            try:
                pts.append((to_sec(r[tc]), float(r[cc])))
            except (ValueError, TypeError, KeyError):
                continue
    if len(pts) < 2:
        print(f"FAIL 표본 {len(pts)}개 — 형식 확인 (시간 열 {tc!r}, 전류 열 {cc!r})")
        return 2
    pts.sort()
    ma = "ma" in cc.lower()
    if not ma and statistics.median(v for _, v in pts) > 50:
        ma = True
        print("알림: 값이 커서 mA 로 본다")
    if ma:
        pts = [(t, v / 1000.0) for t, v in pts]
    dur = pts[-1][0] - pts[0][0]
    win = a.window_min * 60
    steps = [b[0] - x[0] for x, b in zip(pts, pts[1:])]
    mean = statistics.mean(v for _, v in pts)
    peak_t, peak = max(pts, key=lambda p: p[1])
    print(f"표본 {len(pts)} · 길이 {dur / 60:.1f}분 · 간격 중앙값 {statistics.median(steps):.2f}s · 전체 평균 {mean:.3f}A · 피크 {peak:.3f}A (t={peak_t - pts[0][0]:.1f}s)")
    if peak > a.adapter:
        print(f"경고: 피크 {peak:.3f}A > 어댑터 {a.adapter}A (순간값 — 판정은 평균)")
    if dur < win:
        print(f"FAIL 기록 {dur / 60:.1f}분 < 창 {a.window_min:g}분 — 다시 기록")
        return 2
    # 시간 가중 이동 평균(사다리꼴 적분): 표본 i 에서 시작해 win 이상 지난 첫 표본 j 까지의 평균
    ts = [t for t, _ in pts]
    acc = [0.0]
    for x, b in zip(pts, pts[1:]):
        acc.append(acc[-1] + (x[1] + b[1]) / 2 * (b[0] - x[0]))
    best, best_t = 0.0, 0.0
    for i in range(len(pts)):
        j = bisect.bisect_left(ts, ts[i] + win)
        if j >= len(pts):
            break
        m = (acc[j] - acc[i]) / (ts[j] - ts[i])
        if m > best:
            best, best_t = m, ts[i] - ts[0]
    ok = best <= a.limit
    print(f"{'PASS' if ok else 'FAIL'} {a.window_min:g}분 창 평균 최댓값 {best:.3f}A (시작 t={best_t:.0f}s) {'≤' if ok else '>'} {a.limit}A"
          + ("" if ok else " → 12V 3A급 어댑터 교체 (구매는 사용자 지시 — 대기 목록)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
