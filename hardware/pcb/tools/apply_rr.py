"""rr_finish.py 결과 적용 (KiCad pcbnew, GUI 닫고): soft 넷의 트랙 · 비아를 모두 지우고 결과의 것으로 바꾼다 + 고정 넷에 더한 것.
넣기 전에 끝이 뜬 조각(뜯긴 뒤 남은 그루터기)과 길이 0 조각을 기하로 가지치기한다.
사용: <KiCad>/bin/python.exe apply_rr.py <board.kicad_pcb> <rr.json>
"""
import json
import math
import sys
from collections import Counter

import pcbnew

MM = pcbnew.FromMM
LAY = {"F.Cu": pcbnew.F_Cu, "In1.Cu": pcbnew.In1_Cu, "In2.Cu": pcbnew.In2_Cu, "B.Cu": pcbnew.B_Cu}


def pt_seg(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - a[0] - t * dx, p[1] - a[1] - t * dy)


def prune(b, tracks, vias):
    pads = {}
    for fp in b.GetFootprints():
        for p in fp.Pads():
            pads.setdefault(p.GetNetname(), []).append(p)
    tracks = [t for t in tracks if math.dist(t["a"], t["b"]) > 1e-4]
    n0 = len(tracks) + len(vias)
    while True:
        by = {}
        for t in tracks:
            by.setdefault(t["net"], []).append(t)
        vby = {}
        for v in vias:
            vby.setdefault(v["net"], []).append(v)
        ends = Counter()
        for t in tracks:
            for e in ("a", "b"):
                ends[(t["net"], t["layer"], round(t[e][0], 3), round(t[e][1], 3))] += 1

        def attached(t, e):
            p = t[e]
            if ends[(t["net"], t["layer"], round(p[0], 3), round(p[1], 3))] > 1:
                return True
            if any(math.dist(p, v["pos"]) <= v["dia"] / 2 for v in vby.get(t["net"], [])):
                return True
            q = pcbnew.VECTOR2I(MM(p[0]), MM(p[1]))
            if any(pd.IsOnLayer(LAY[t["layer"]]) and pd.HitTest(q) for pd in pads.get(t["net"], [])):
                return True
            other = t["b"] if e == "a" else t["a"]
            # 몸통 붙음(T 자): 끝점을 나눠 가진 이웃 조각은 빼고 본다 — 짧은 조각이 이웃 몸통에 붙은 것으로 보이는 것 방지
            return any(o is not t and o["layer"] == t["layer"] and pt_seg(p, o["a"], o["b"]) <= o["w"] / 2
                       and min(math.dist(other, o["a"]), math.dist(other, o["b"])) > 1e-3 for o in by[t["net"]])
        keep = [t for t in tracks if attached(t, "a") and attached(t, "b")]
        kv = []
        for v in vias:
            n = sum(1 for t in by.get(v["net"], []) for e in ("a", "b") if math.dist(t[e], v["pos"]) <= v["dia"] / 2)
            q = pcbnew.VECTOR2I(MM(v["pos"][0]), MM(v["pos"][1]))
            if n >= 2 or (n >= 1 and any(pd.HitTest(q) for pd in pads.get(v["net"], []))):
                kv.append(v)
        if len(keep) == len(tracks) and len(kv) == len(vias):
            break
        tracks, vias = keep, kv
    print(f"가지치기: {n0 - len(tracks) - len(vias)}개 뺌")
    return tracks, vias


b = pcbnew.LoadBoard(sys.argv[1])
d = json.load(open(sys.argv[2], encoding="utf-8"))
soft = set(d["soft_nets"])
nd = 0
for t in list(b.GetTracks()):
    if t.GetNetname() in soft:
        b.Delete(t)
        nd += 1
# 가지치기는 KiCad 자체 연결 판정을 쓰는 kprune.py 가 한다(여기 기하 가지치기는 살아 있는 연결까지 잘라 미연결을 늘렸다)
tracks = [t for t in d["soft_tracks"] if math.dist(t["a"], t["b"]) > 1e-4]
vias = d["soft_vias"]
for t in tracks + d["hard_add_tracks"]:
    s = pcbnew.PCB_TRACK(b)
    s.SetStart(pcbnew.VECTOR2I(MM(t["a"][0]), MM(t["a"][1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(t["b"][0]), MM(t["b"][1])))
    s.SetWidth(MM(t["w"]))
    s.SetLayer(LAY[t["layer"]])
    s.SetNet(b.FindNet(t["net"]))
    b.Add(s)
for v in vias + d["hard_add_vias"]:
    s = pcbnew.PCB_VIA(b)
    s.SetPosition(pcbnew.VECTOR2I(MM(v["pos"][0]), MM(v["pos"][1])))
    s.SetWidth(MM(v["dia"]))
    s.SetDrill(MM(v["drill"]))
    s.SetNet(b.FindNet(v["net"]))
    b.Add(s)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print(f"지움 {nd} · 넣음 트랙 {len(tracks) + len(d['hard_add_tracks'])} · 비아 {len(vias) + len(d['hard_add_vias'])}")
