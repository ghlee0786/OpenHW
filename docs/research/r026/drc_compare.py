"""R-026 합격 판정: 기준 DRC json 과 SES 가져온 뒤 DRC json 을 비교한다.
python drc_compare.py <base-drc.json> <after-drc.json>
종료 코드 0 = 위반 수가 늘지 않았고(종류별로도 늘지 않음) 미연결이 줄었다 · 1 = 아님 · 2 = 입력 오류."""
import collections
import json
import sys

try:
    a, b = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:3])
except (IndexError, OSError, ValueError) as e:
    print("입력 오류:", e)
    sys.exit(2)


def stat(d):
    return (collections.Counter(v["type"] for v in d["violations"]), len(d["unconnected_items"]),
            len(d.get("schematic_parity", [])))


(va, ua, pa), (vb, ub, pb) = stat(a), stat(b)
grown = {k: (va.get(k, 0), n) for k, n in vb.items() if n > va.get(k, 0)}
print(f"위반 {sum(va.values())} -> {sum(vb.values())} · 미연결 {ua} -> {ub} · parity {pa} -> {pb}")
if grown:
    print("늘어난 위반 종류:", grown)
ok = not grown and sum(vb.values()) <= sum(va.values()) and ub < ua and pb <= pa
print("합격" if ok else "불합격")
sys.exit(0 if ok else 1)
