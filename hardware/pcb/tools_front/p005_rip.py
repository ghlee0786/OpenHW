"""P-005 전면: 막힌 넷을 이웃 저속 넷 뜯고 다시 깔기로 잇는다 (시스템 파이썬, 보드는 바꾸지 않음).

넷 N 이 막혔으면: 닿는 구역을 둘러싼 넷 가운데 뜯어도 되는 넷 X(저속 · 잠금 아님)를 하나(안 되면 둘) 골라
  X 의 트랙 · 비아를 모두 뺀 판에서 N 을 먼저 잇고 → 그 위에 X 를 패드부터 다시 잇는다. 둘 다 끝까지 이어질 때만 받아들인다.
잠금(뜯지 않음): 고속 CSI(CAM_RX0_*) · GND · 전원 굵은 선(VIN · 12V_IR) · IR LED 열 패드 넷(IRA_* · IRB_*) + 환경 P5_LOCK 정규식.

사용: python p005_rip.py <geom-all.json> <out.json> <넷 정규식> [...]
출력: {"replace": {넷: {"tracks": [...], "vias": [...]}}} — 그 넷의 트랙 · 비아 전체를 이것으로 바꾼다(p005_apply.py).
"""
import itertools
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import p005_route as pr  # noqa: E402

LOCK = re.compile(os.environ.get("P5_LOCK", r"/(CAM_RX0_.*|GND|VIN|12V_IR|IR[AB]_.*)"))
RL = {"F.Cu": "F.Cu", "In1.Cu": "In1.Cu", "In2.Cu": "In2.Cu", "GND_PWR": "In2.Cu", "B.Cu": "B.Cu", "GND": "In1.Cu"}


def log(s):
    print(s, flush=True)


def quiet(s):
    pass


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    pats = [re.compile(p) for p in sys.argv[3:]]
    margin = float(os.environ.get("P5_MARGIN", "10"))
    cap = int(os.environ.get("P5_CAP", "3000000"))
    layers = [int(x) for x in os.environ.get("P5_LAYERS", "0,3,2").split(",")]
    maxk = int(os.environ.get("P5_RIPK", "2"))
    tracks = [dict(t, layer=RL[t["layer"]]) for t in geom["tracks"]]
    vias = [dict(v) for v in geom["vias"]]
    touched = set()

    def build(skip=()):
        g = dict(geom, tracks=[t for t in tracks if t["net"] not in skip], vias=[v for v in vias if v["net"] not in skip])
        return pr.load(g)

    def commit(net, tr, vi, replace=False):
        nonlocal tracks, vias
        if replace:
            tracks = [t for t in tracks if t["net"] != net]
            vias = [v for v in vias if v["net"] != net]
        tracks += [dict(t, net=net) for t in tr]
        vias += [dict(v, net=net) for v in vi]
        touched.add(net)

    def save():
        rep = {n: {"tracks": [t for t in tracks if t["net"] == n], "vias": [v for v in vias if v["net"] == n]} for n in sorted(touched)}
        json.dump({"replace": rep}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def ncomp(B_, net):
        comp = pr.components(B_, net)
        return len([i for i in pr.np.unique(comp[comp > 0]) if (comp[[0, 2, 3]] == i).any()])

    B = build()
    nets = [n for pat in pats for n in B.netid if pat.fullmatch(n) and n != "/GND"]
    left = []
    for net in nets:
        B = build()
        pr.BLOCKERS.clear()
        ok, tr, vi = pr.route_net(B, net, margin, cap, layers, quiet)
        if tr or vi:
            commit(net, tr, vi)
            save()
        if ok:
            log(f"{net}: 바로 이음 (트랙 {len(tr)} · 비아 {len(vi)})")
            continue
        base_n = ncomp(B, net)
        base_x = {}
        log(f"{net}: 덩어리 {base_n} 남음 (바로 이은 트랙 {len(tr)})")
        cands = [n for n, _ in sorted(pr.BLOCKERS.items(), key=lambda kv: -kv[1]) if n.startswith("/") and not LOCK.fullmatch(n) and n != net]
        if os.environ.get("P5_CANDS"):  # 후보를 손으로 지정(쉼표)
            cands = [c for c in os.environ["P5_CANDS"].split(",") if c != net]
        log(f"{net}: 막힘 — 뜯을 후보 {cands}")
        done = False
        for k in range(1, maxk + 1):
            for combo in itertools.combinations(cands[:6], k):
                for x in combo:
                    if x not in base_x:
                        base_x[x] = ncomp(build(), x)
                B = build(skip=set(combo))
                ok1, t1, v1 = pr.route_net(B, net, margin, cap, layers, quiet)
                n1 = ncomp(B, net)
                if n1 >= base_n:
                    continue
                res = []
                good = True
                for x in combo:
                    ok2, t2, v2 = pr.route_net(B, x, margin, cap, layers, quiet)
                    if not ok2 and ncomp(B, x) > base_x[x]:  # 뜯은 넷이 원래보다 더 끊기면 버림
                        good = False
                        log(f"   {combo} 뜯음: {net} 덩어리 {base_n}→{n1}, {x} 다시 못 깖")
                        break
                    res.append((x, t2, v2))
                if not good:
                    continue
                commit(net, t1, v1)
                for x, t2, v2 in res:
                    commit(x, t2, v2, replace=True)
                log(f"{net}: {combo} 뜯고 다시 깔아 덩어리 {base_n}→{n1}")
                save()
                base_n = n1
                done = n1 <= 1
                if done:
                    break
            if done:
                break
        if not done:
            left.append(net)
            log(f"{net}: 실패")
    save()
    log(f"남은 넷 {left}")


if __name__ == "__main__":
    main()
