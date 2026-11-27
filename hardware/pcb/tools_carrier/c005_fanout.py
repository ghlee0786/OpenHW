"""캐리어 J1(BTB 0.5 피치) 왼쪽 줄 규칙적 탈출 (KiCad pcbnew, GUI 닫고) — O-114 E 작은 비아(0.50/0.20, 규칙 영역 J1_ESC 안).

차례대로 깔면 앞 핀의 탈출선 · 비아가 옆 핀 자리를 먹어 마지막 몇 핀이 갇힌다(SDIO_D1 · UPGRAD_KEY · STATUS_LED). 그래서 연속한 신호 핀 묶음은
'가까운 줄(x 108.45) / 먼 줄(x 107.70)' 엇갈림 무늬로 핀 정면에 비아를 먼저 박고(잠금), 그 넷의 나머지는 비아에서 다시 잇는다.
  간격: 먼 줄 핀의 0.15 선이 가까운 줄 비아 사이를 지남 = 0.5 − 0.25 − 0.075 = 0.175 ≥ 0.16 · 비아–이웃 패드 0.20 · 비아끼리 ≥ 0.40.
같이 하는 일: 묶음 넷의 기존 트랙 · 비아 삭제, EFUSE 부품 맞바꿈(C9 ↔ R6: U2.12 DVDT 는 서쪽, U2.11 ILIM 은 동쪽 — 서로 넘지 않게).
사용: <KiCad>/bin/python.exe c005_fanout.py <carrier.kicad_pcb>
"""
import sys

import pcbnew

MM = pcbnew.FromMM
PADX, NEAR, FAR = 109.8, 108.45, 107.70
VIA = (0.50, 0.20)
W = 0.15
# 핀 y → (넷, 줄)
BLOCK = {
    97.75: ("/IR_LED_EN", "near"),
    100.75: ("/nRESET", "near"), 101.25: ("/UPGRAD_KEY", "far"), 101.75: ("/SD0_PWR_EN", "near"), 102.25: ("/SDIO_D3", "far"),
    102.75: ("/SDIO_D2", "near"), 103.25: ("/SDIO_D1", "far"), 103.75: ("/SDIO_D0", "near"), 104.25: ("/SDIO_CMD", "far"),
}
# 핀 24 STATUS_LED: 정면은 핀 22(IR) 비아가 0.5 위라 0.70 떨어진 (108.45, 98.45)로 꺾어 내린다
SPECIAL = {"/STATUS_LED": ([(109.8, 98.25), (108.8, 98.25), (108.6, 98.45), (108.45, 98.45)], (108.45, 98.45))}
SWAP = ("C9", "R6")
RIP = sorted({n for n, _ in BLOCK.values()} | set(SPECIAL) | {"/EFUSE_DVDT", "/EFUSE_ILIM"})

b = pcbnew.LoadBoard(sys.argv[1])
nd = 0
for t in list(b.GetTracks()):
    if t.GetNetname() in RIP:
        b.Delete(t)
        nd += 1


def track(net, a, c):
    s = pcbnew.PCB_TRACK(b)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]), MM(a[1])))
    s.SetEnd(pcbnew.VECTOR2I(MM(c[0]), MM(c[1])))
    s.SetWidth(MM(W))
    s.SetLayer(pcbnew.F_Cu)
    s.SetNet(b.FindNet(net))
    s.SetLocked(True)
    b.Add(s)


def via(net, p):
    s = pcbnew.PCB_VIA(b)
    s.SetPosition(pcbnew.VECTOR2I(MM(p[0]), MM(p[1])))
    s.SetWidth(MM(VIA[0]))
    s.SetDrill(MM(VIA[1]))
    s.SetNet(b.FindNet(net))
    s.SetLocked(True)
    b.Add(s)


for y, (net, col) in BLOCK.items():
    x = NEAR if col == "near" else FAR
    track(net, (PADX, y), (x, y))
    via(net, (x, y))
for net, (pts, vp) in SPECIAL.items():
    for a, c in zip(pts[:-1], pts[1:]):
        track(net, a, c)
    via(net, vp)
fps = {fp.GetReference(): fp for fp in b.GetFootprints()}
a, c = fps[SWAP[0]], fps[SWAP[1]]
pa, pc = a.GetPosition(), c.GetPosition()
oa, oc = a.GetOrientationDegrees(), c.GetOrientationDegrees()
print(f"맞바꿈 {SWAP[0]} ({pcbnew.ToMM(pa.x):.3f},{pcbnew.ToMM(pa.y):.3f},{oa}) <-> {SWAP[1]} ({pcbnew.ToMM(pc.x):.3f},{pcbnew.ToMM(pc.y):.3f},{oc})")
a.SetPosition(pc)
a.SetOrientationDegrees(oc)
c.SetPosition(pa)
c.SetOrientationDegrees(oa)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print(f"지움 {nd} · 탈출 비아 {len(BLOCK) + len(SPECIAL)} · 뜯은 넷 {RIP}")
