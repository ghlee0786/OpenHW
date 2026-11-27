"""캐리어 J1 왼쪽 줄 윗 묶음(핀 14~24, 신호 6개 연속) 탈출 다시 박기 (KiCad pcbnew, GUI 닫고) — O-114 E.

이 묶음 서쪽은 MDI RX 쌍(RXN x 107.76, F.Cu)이 바로 옆을 내려가 SDIO 묶음의 '먼 줄'(x 107.70)을 쓸 수 없다.
비아 한 줄에 6개(0.66 간격)는 비껴 선 탈출선이 옆 비아에 0.09~0.11 로 붙어 불가(계산) → 두 줄을 좁게 엇갈린다:
  A 줄 x 108.70 (핀 14 · 18 · 22) — 자기 패드 끝(x 108.9)에 0.05 걸침, 이웃 패드(0.25 폭 둥근 사각, 0.5 피치)와 0.175
  B 줄 x 108.25 (핀 16 · 20 · 24) — RXN 트랙 가장자리(107.835)와 0.165, A 줄 비아와 0.173, B 탈출선은 A 비아 사이 0.175
탈출선(트랙)–RXN 트랙 0.335 ≥ 0.30(hs_track_spacing). 구멍 간격 0.47 ≥ 0.45. 판정은 뒤의 kicad-cli DRC.
사용: <KiCad>/bin/python.exe c005_fanout2.py <carrier.kicad_pcb>
"""
import sys

import pcbnew

MM = pcbnew.FromMM
W, VD, VH, PADX, XA, XB = 0.15, 0.50, 0.20, 109.8, 108.70, 108.25
PINS = [("/USB_DET", 95.75, XA), ("/I2C1_SDA", 96.25, XB), ("/I2C1_SCL", 96.75, XA),
        ("/SPARE1", 97.25, XB), ("/IR_LED_EN", 97.75, XA), ("/STATUS_LED", 98.25, XB)]

b = pcbnew.LoadBoard(sys.argv[1])
rip = {n for n, _, _ in PINS}
nd = 0
for t in list(b.GetTracks()):
    if t.GetNetname() in rip:
        b.Delete(t)
        nd += 1
for net, y, x in PINS:
    t = pcbnew.PCB_TRACK(b)
    t.SetStart(pcbnew.VECTOR2I(MM(PADX), MM(y)))
    t.SetEnd(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetWidth(MM(W))
    t.SetLayer(pcbnew.F_Cu)
    t.SetNet(b.FindNet(net))
    t.SetLocked(True)
    b.Add(t)
    v = pcbnew.PCB_VIA(b)
    v.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    v.SetWidth(MM(VD))
    v.SetDrill(MM(VH))
    v.SetNet(b.FindNet(net))
    v.SetLocked(True)
    b.Add(v)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
b.Save(sys.argv[1])
print(f"지움 {nd} · 비아 {[(n, x, y) for n, y, x in PINS]}")
