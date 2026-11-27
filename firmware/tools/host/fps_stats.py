#!/usr/bin/env python3
"""F-007 ③ 추론 FPS · 단계별 시간 집계 (절차서 4-4 양식).

입력: event_log.py record --topic sscma/v0/recamera/node/out/openhw_person 으로 받은 JSONL
      (한 줄 = {"rx": PC 수신 epoch, "msg": sscma 응답}). sscma-node model.cpp: invoke 메시지
      data.count(누적 번호) · data.perf [[pre, inf, post] ms] (L76 · L251).
  fps_stats.py <invoke.jsonl> [--cam-fps 15] [--min-fps 0]
출력: FPS(count 증가 ÷ 수신 시간) · MQTT 누락(count 건너뜀) · perf 단계별 평균/p50/p95/최대 · 카메라 대비 비율
판정: 목표 수치가 근거 문서에 없다(절차서 4-4) → 기본은 기록만(종료 0). --min-fps 를 주면 그보다 낮을 때 1.
      invoke 0건 · count 2건 미만이면 2.
"""
import argparse
import json
import statistics
import sys


def pct(v, q):
    v = sorted(v)
    return v[min(len(v) - 1, int(round(q * (len(v) - 1))))]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--cam-fps", type=float, default=15.0)
    ap.add_argument("--min-fps", type=float, default=0.0)
    a = ap.parse_args()
    rows = []
    with open(a.file, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            m = r.get("msg", r)
            if isinstance(m, dict) and m.get("name") == "invoke" and isinstance(m.get("data"), dict) and "count" in m["data"]:
                rows.append((float(r.get("rx", 0)), int(m["data"]["count"]), m["data"].get("perf") or []))
    if len(rows) < 2:
        print(f"FAIL invoke {len(rows)}건 — 모델 노드가 결과를 내지 않음(절차서 4-2)")
        return 2
    rows.sort()
    dc = rows[-1][1] - rows[0][1]
    dt = rows[-1][0] - rows[0][0]
    if dc <= 0 or dt <= 0:
        print(f"FAIL count/시간 증가 없음 (count {rows[0][1]}→{rows[-1][1]}, {dt:.1f}s)")
        return 2
    fps = dc / dt
    lost = dc - (len(rows) - 1)
    stages = {"pre": [], "inf": [], "post": []}
    for _, _, perf in rows:
        if perf and isinstance(perf[0], list) and len(perf[0]) >= 3:
            for k, v in zip(stages, perf[0][:3]):
                stages[k].append(float(v))
    print(f"invoke {len(rows)}건 · {dt:.1f}s · count {rows[0][1]}→{rows[-1][1]} · FPS {fps:.2f} · 카메라 {a.cam_fps:g}fps 대비 {fps / a.cam_fps:.0%} · MQTT 누락 {lost}")
    for k, v in stages.items():
        if v:
            print(f"perf {k}: 평균 {statistics.mean(v):.1f} · p50 {pct(v, .5):.1f} · p95 {pct(v, .95):.1f} · 최대 {max(v):.1f} ms (n={len(v)})")
    if not stages["inf"]:
        print("perf 없음 — 이 sscma-node 응답에 data.perf 가 없다")
    if a.min_fps and fps < a.min_fps:
        print(f"FAIL FPS {fps:.2f} < {a.min_fps}")
        return 1
    print("PASS 기록" + (f" (FPS ≥ {a.min_fps})" if a.min_fps else " (목표 수치 없음)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
