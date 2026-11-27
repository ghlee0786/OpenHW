"""P-005 전면: CSI D1 쌍 손질 (KiCad pcbnew). 쌍 안 길이 차는 그대로 0 (P · N 에 같은 변형).

dedup : 같은 넷 · 층에서 양 끝이 같은(0.5µm 안) 겹친 트랙을 하나만 남긴다(p005_viafix 초판이 비아 접합점에 겹쳐 넣은 선).
m1    : D1 쌍 비아 2개를 뒷면 대각 방향으로 (+0.70, −0.70) 옮긴다 → 뒷면 대각(1.07 · 1.20, KiCad 가 비결합으로 셈)이 0.07 · 0.21 로 줄고
        앞면 대각이 그만큼 길어진다(앞면 대각은 결합으로 셈). 넷 길이는 그대로.
m2    : D1 앞면 ㄱ자 꺾임(y 95.37 가로 → x 98.67 세로)의 45° 모따기를 c=1.0 키운다 → P · N 둘 다 0.586 짧아진다
        (D1 이 CLK 보다 KiCad 계산으로 0.29 길어 D0 와 skew 1.19 > 1.0 이던 것).
사용: <KiCad>/bin/python.exe p005_csi.py <board.kicad_pcb> dedup|m1|m2 [...]
"""
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM
TOL = 0.0006


def near(p, x, y):
    return abs(TO(p.x) - x) < TOL and abs(TO(p.y) - y) < TOL


def find(b, net, layer, a, c=None, kind="PCB_TRACK"):
    out = []
    for t in b.GetTracks():
        if t.GetClass() != kind or t.GetNetname() != net:
            continue
        if kind == "PCB_VIA":
            if near(t.GetPosition(), *a):
                out.append(t)
        elif b.GetLayerName(t.GetLayer()) == layer and near(t.GetStart(), *a) and near(t.GetEnd(), *c):
            out.append(t)
    return out


def setp(t, which, x, y):
    (t.SetStart if which == "a" else t.SetEnd)(pcbnew.VECTOR2I(MM(x), MM(y)))


def dedup(b):
    seen, n = {}, 0
    for t in list(b.GetTracks()):
        if t.GetClass() != "PCB_TRACK":
            continue
        e = sorted([(round(TO(t.GetStart().x), 3), round(TO(t.GetStart().y), 3)), (round(TO(t.GetEnd().x), 3), round(TO(t.GetEnd().y), 3))])
        k = (t.GetNetCode(), t.GetLayer(), tuple(e), t.GetWidth())
        if k in seen:
            b.Delete(t)
            n += 1
        else:
            seen[k] = t
    print("겹친 트랙 지움", n)


def m1(b):
    v = (0.70, -0.70)
    P, N = "/CAM_RX0_1P", "/CAM_RX0_1N"
    jp, jn = (101.0869, 94.8869), (101.3131, 95.1131)      # 접합점(대각 끝 = 비아로 가는 짧은 선 시작)
    vp, vn = (100.8818, 94.6818), (101.5182, 95.3182)      # 비아
    n = 0
    for net, j, via, bdiag_a, fdiag_b in ((P, jp, vp, (101.84, 94.1337), (100.603, 95.3708)), (N, jn, vn, (102.16, 94.2663), (100.7355, 95.6908))):
        j2, via2 = (j[0] + v[0], j[1] + v[1]), (via[0] + v[0], via[1] + v[1])
        for t in find(b, net, "B.Cu", bdiag_a, j):       # 뒷면 대각: 끝을 새 접합점으로
            setp(t, "b", *j2); n += 1
        for lay in ("B.Cu", "F.Cu"):                      # 비아로 가는 짧은 선(방향 둘 다)
            for t in find(b, net, lay, j, via):
                setp(t, "a", *j2); setp(t, "b", *via2); n += 1
            for t in find(b, net, lay, via, j):
                setp(t, "a", *via2); setp(t, "b", *j2); n += 1
        for t in find(b, net, "F.Cu", j, fdiag_b):        # 앞면 대각: 시작을 새 접합점으로
            setp(t, "a", *j2); n += 1
        for t in find(b, net, None, via, kind="PCB_VIA"):
            t.SetPosition(pcbnew.VECTOR2I(MM(via2[0]), MM(via2[1]))); n += 1
    print("m1 바꾼 항목", n, "(기대 12: 쌍마다 뒷면 대각 1 · 짧은 선 2 · 앞면 대각 1 · 비아 1 = 5 … 겹친 선 있으면 더)")


def m2(b):
    c = 1.0
    n = 0
    for net, hx0, hx1, hy, vx, vy0, vy1 in (("/CAM_RX0_1P", 100.603, 99.0473, 95.3708, 98.6708, 95.7473, 97.303),
                                            ("/CAM_RX0_1N", 100.7355, 99.1799, 95.6908, 98.9908, 95.8799, 97.4355)):
        for t in find(b, net, "F.Cu", (hx0, hy), (hx1, hy)):       # 가로: 끝을 c 만큼 당김
            setp(t, "b", hx1 + c, hy); n += 1
        for t in find(b, net, "F.Cu", (hx1, hy), (vx, vy0)):       # 45° 모따기
            setp(t, "a", hx1 + c, hy); setp(t, "b", vx, vy0 + c); n += 1
        for t in find(b, net, "F.Cu", (vx, vy0), (vx, vy1)):       # 세로: 시작을 c 만큼 내림
            setp(t, "a", vx, vy0 + c); n += 1
    print("m2 바꾼 항목", n, "(기대 6)")


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    for op in sys.argv[2:]:
        {"dedup": dedup, "m1": m1, "m2": m2}[op](b)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])


if __name__ == "__main__":
    main()
