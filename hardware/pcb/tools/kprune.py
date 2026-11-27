"""KiCad 자체 연결 판정으로 가지치기 (KiCad pcbnew, GUI 닫고): 끝이 뜬 트랙 · 비아(저속 · 전원 넷)를 더 없을 때까지 지운다.
고속 쌍 · GND 는 지우지 않는다. 끝에 넷별 미연결 수를 출력한다. 사용: kprune.py <board.kicad_pcb> [nosave]
"""
import collections
import sys

import pcbnew

KEEP = ("EPHY", "/USB_DP", "/USB_DN", "CAM_RX", "/GND")
b = pcbnew.LoadBoard(sys.argv[1])
tot = 0
while True:
    b.BuildConnectivity()
    conn = b.GetConnectivity()
    kill = []
    for t in b.GetTracks():
        n = t.GetNetname()
        if any(k in n for k in KEEP):
            continue
        if t.GetClass() == "PCB_VIA":
            its = [i for i in conn.GetConnectedItems(t) if i.Type() in (pcbnew.PCB_TRACE_T, pcbnew.PCB_ARC_T, pcbnew.PCB_PAD_T)]
            if len(its) < 2:
                kill.append(t)
        elif conn.TestTrackEndpointDangling(t, True):
            kill.append(t)
    if not kill:
        break
    for t in kill:
        b.Delete(t)
    tot += len(kill)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.BuildConnectivity()
conn = b.GetConnectivity()
un = collections.Counter()
for net in b.GetNetInfo().NetsByName():
    name = str(net)
    code = b.GetNetcodeFromNetname(name)
    if code <= 0:
        continue
    k = conn.GetNetClusterCount(code) if hasattr(conn, "GetNetClusterCount") else 0
    if k > 1:
        un[name] = k - 1
if len(sys.argv) < 3:
    b.Save(sys.argv[1])
print("pruned", tot, "· unconnected(total)", conn.GetUnconnectedCount(True), dict(un))
