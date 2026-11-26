#!/usr/bin/env python3
"""F-007 ② MQTT 이벤트 기록기 · 검사기 (PC 쪽, 표준 라이브러리 + mosquitto_sub).

장치의 1883 은 루프백 전용이다(D-003 #30). 그래서 PC 에서는 ssh 로 장치 안 mosquitto_sub 출력을 받는다:
  ssh root@<장치> "mosquitto_sub -h 127.0.0.1 -t openhw/v1/event -v" | event_log.py record --stdin -o ev.jsonl
브로커에 직접 닿는 경우(시험 · event_host 를 PC 로 둔 경우):
  event_log.py record -o ev.jsonl [--host 127.0.0.1 --port 1883 --topic openhw/v1/event] [--seconds 600]
같은 기록기로 sscma invoke 도 받을 수 있다(fps_stats.py 입력): --topic sscma/v0/recamera/node/out/openhw_person

record: 한 줄 = {"rx": PC 수신 epoch 초, "topic": ..., "msg": JSON(파싱 실패면 "raw")}
check : event_log.py check ev.jsonl [--cooldown-ms 30000] [--min-score 0.5]
  위반 = 필드 누락 · 모르는 event · 등장 중 등장 · 없는데 퇴장 · 등장 사이 < 쿨다운 · ts 역행 · 등장 score < min · count < 1
  종료 코드 = 위반 수(최대 100), 이벤트 0건이면 2. 근거: f004-person-event.md 3절(이벤트 JSON · enter 3프레임 · leave 5s · cooldown 30s)
"""
import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
import threading
import time

FIELDS = ("event", "ts", "device", "mode", "score", "count", "resolution", "boxes")


def parse_line(line):
    line = line.rstrip("\r\n")
    if not line:
        return None
    topic, _, payload = line.partition(" ") if not line.startswith("{") else ("", "", line)
    try:
        msg = json.loads(payload)
    except ValueError:
        msg = {"raw": payload}
    return {"rx": round(time.time(), 3), "topic": topic, "msg": msg}


def record(a):
    if a.stdin:
        src = sys.stdin
        proc = None
    else:
        exe = shutil.which("mosquitto_sub")
        if not exe:
            sys.exit("mosquitto_sub 없음 — mosquitto-clients 설치 또는 --stdin(ssh 파이프) 사용")
        proc = subprocess.Popen([exe, "-h", a.host, "-p", str(a.port), "-t", a.topic, "-v"],
                                stdout=subprocess.PIPE, text=True, encoding="utf-8")
        src = proc.stdout
    end = time.monotonic() + a.seconds if a.seconds else None
    if proc and a.seconds:   # 메시지가 안 와도 끝나게: 시간이 되면 mosquitto_sub 를 끊어 읽기를 풀어 준다
        threading.Timer(a.seconds, proc.terminate).start()
    n = 0
    with open(a.out, "a", encoding="utf-8") as f:
        try:
            for line in src:
                rec = parse_line(line)
                if rec:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    f.flush()
                    n += 1
                if end and time.monotonic() >= end:
                    break
        except KeyboardInterrupt:
            pass
        finally:
            if proc:
                proc.terminate()
    print(f"기록 {n}줄 → {a.out}")
    return 0


def ts_ms(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp() * 1000.0


def check(a):
    evs = []
    with open(a.file, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                m = r.get("msg", r)
                if isinstance(m, dict) and "event" in m:
                    evs.append(m)
    if not evs:
        print("FAIL 이벤트 0건")
        return 2
    bad = []
    present, last_enter, last_ts, pairs, enter_at = False, None, None, [], None
    for i, e in enumerate(evs, 1):
        miss = [k for k in FIELDS if k not in e]
        if miss:
            bad.append(f"#{i} 필드 누락 {miss}")
            continue
        try:
            t = ts_ms(e["ts"])
        except ValueError:
            bad.append(f"#{i} ts 형식 {e['ts']!r}")
            continue
        if last_ts is not None and t < last_ts:
            bad.append(f"#{i} ts 역행 {e['ts']}")
        last_ts = t
        if e["event"] == "person_enter":
            if present:
                bad.append(f"#{i} 등장 중 등장 {e['ts']}")
            if last_enter is not None and t - last_enter < a.cooldown_ms:
                bad.append(f"#{i} 쿨다운 위반 {(t - last_enter) / 1000:.1f}s < {a.cooldown_ms / 1000:.0f}s")
            if e["score"] < a.min_score:
                bad.append(f"#{i} 등장 score {e['score']} < {a.min_score}")
            if e["count"] < 1:
                bad.append(f"#{i} 등장 count {e['count']}")
            present, last_enter, enter_at = True, t, t
        elif e["event"] == "person_leave":
            if not present:
                bad.append(f"#{i} 없는데 퇴장 {e['ts']}")
            else:
                pairs.append((t - enter_at) / 1000)
            present = False
        else:
            bad.append(f"#{i} 모르는 event {e['event']!r}")
    for b in bad:
        print("FAIL", b)
    modes = sorted({str(e.get("mode")) for e in evs})   # 필드가 빠진 이벤트는 "None"
    stay = f" 머문 시간 {min(pairs):.1f}~{max(pairs):.1f}s" if pairs else ""
    print(f"이벤트 {len(evs)}건 · 등장/퇴장 짝 {len(pairs)}{stay} · 끝 상태 {'등장 중' if present else '없음'} · mode {modes} · 위반 {len(bad)}")
    return min(len(bad), 100)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("record")
    p.add_argument("-o", "--out", required=True)
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=1883)
    p.add_argument("--topic", default="openhw/v1/event")
    p.add_argument("--seconds", type=float, default=0)
    p = sub.add_parser("check")
    p.add_argument("file")
    p.add_argument("--cooldown-ms", type=float, default=30000)
    p.add_argument("--min-score", type=float, default=0.5)
    a = ap.parse_args()
    return record(a) if a.cmd == "record" else check(a)


if __name__ == "__main__":
    sys.exit(main())
