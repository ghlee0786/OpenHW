"""DRC 기반 정리 (KiCad pcbnew, GUI 닫고): DRC json 의 단락 · 간격 · 끝이 뜬 트랙/비아 위반에 든 '저속 넷' 트랙 · 비아를 지운다.
끝이 뜬 트랙은 그 그루터기를 갈림 · 패드 · 비아에 닿을 때까지 따라가며 함께 지운다(DRC 를 여러 번 돌리지 않게).
고속 쌍(CSI/MDI/USB) · GND 는 지우지 않는다. 지운 수를 출력(0 이면 끝). 사용: drc_clean.py <board> <drc.json> [types]
"""
import json
import sys

import pcbnew

TYPES = set((sys.argv[3] if len(sys.argv) > 3 else "track_dangling,via_dangling,shorting_items,clearance,solder_mask_bridge,hole_clearance").split(","))
KEEP = ("EPHY", "/USB_DP", "/USB_DN", "CAM_RX", "/GND")  # USB_D 로 걸면 /USB_DET 까지 걸린다
b = pcbnew.LoadBoard(sys.argv[1])
d = json.load(open(sys.argv[2], encoding="utf-8"))
ids, dang = set(), set()
for v in d["violations"]:
    if v["type"] in TYPES:
        for it in v["items"]:
            ids.add(it["uuid"])
            if v["type"] == "track_dangling":
                dang.add(it["uuid"])
tracks = [t for t in b.GetTracks() if not any(k in t.GetNetname() for k in KEEP) and not t.IsLocked()]  # 잠근 것(미리 박은 탈출 비아 등)은 안 지운다
pads = {}
for fp in b.GetFootprints():
    for p in fp.Pads():
        pads.setdefault(p.GetNetCode(), []).append(p)
bynet = {}
for t in tracks:
    bynet.setdefault(t.GetNetCode(), []).append(t)
dead = set()


def anchored(t, q):
    """끝점 q 가 t 말고 다른 것(패드 · 비아 · 다른 트랙)에 닿아 있나."""
    for p in pads.get(t.GetNetCode(), []):
        if p.IsOnLayer(t.GetLayer()) and p.HitTest(q):
            return True, None
    hits = []
    for o in bynet[t.GetNetCode()]:
        if o is t or id(o) in dead:
            continue
        if o.GetClass() == "PCB_VIA":
            if o.HitTest(q):
                return True, None
        elif o.GetLayer() == t.GetLayer() and o.HitTest(q):
            hits.append(o)
    if len(hits) == 1 and (hits[0].GetStart() == q or hits[0].GetEnd() == q):
        return False, hits[0]   # 이웃 조각 하나와만 끝점으로 이어짐 → 그루터기의 다음 조각
    return bool(hits), None


n = 0
for t in tracks:
    u = t.m_Uuid.AsString()
    if u not in ids or id(t) in dead:
        continue
    dead.add(id(t))
    n += 1
    if u in dang and t.GetClass() == "PCB_TRACK":
        for q0 in (t.GetStart(), t.GetEnd()):
            cur, q = t, q0
            while True:
                ok, nxt = anchored(cur, q)
                if ok or nxt is None:
                    break
                dead.add(id(nxt))
                n += 1
                q = nxt.GetEnd() if nxt.GetStart() == q else nxt.GetStart()
                cur = nxt
for t in tracks:
    if id(t) in dead:
        b.Delete(t)
if n:
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])
print("deleted", n)
