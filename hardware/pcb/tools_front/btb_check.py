"""짝 BTB 면·방향 판정 (P-003, V-003 지시).

우리 라이브러리 풋프린트(openhw.pretty)를 계획한 면·회전·위치에 놓았을 때 패드 번호별 좌표가
코어와 실제로 짝을 이루는 Seeed 원본 보드(B301 POE 베이스 = 코어 J2 짝, S401 센서 보드 = 코어 J1 짝)의
J1 패드와 코어 기준 좌표(M-001 원점 O, +Y 위, F면이 +Z)에서 일치하는지 60/60 전수 대조한다.

원본 보드 → O: 보드 외곽 bbox 중심 = 코어 중심(원본 30x30 = 코어 30x30), x_O = x - cx, y_O = cy - y.
우리 보드 → O: KiCad (100,100) = O (P-002 템플릿), x_O = x - 100, y_O = 100 - y.
F면이 뒤집힌(B.Cu) 패드도 좌표는 위(+Z)에서 본 값이라 같은 식을 쓴다.

사용: <KiCad>/bin/python.exe btb_check.py <B301.kicad_pcb> <S401.kicad_pcb> <openhw.pretty>
종료 코드 0 = 두 짝 모두 60/60 일치(허용 0.01mm), 1 = 불일치
"""
import sys

import pcbnew

TOL = 0.01
PLAN = {
    # 보드: (원본, 우리 풋프린트, 면, 회전°, O 기준 위치)
    "carrier": ("B301", "BTB_ST-BTB-058060-A_2x30_P0.5mm", "F", -90.0, (11.8, 0.0)),
    "front": ("S401", "BTB_ST-BTB-058060-B_2x30_P0.5mm", "B", 180.0, (0.0, 11.8)),
}


def mm(v):
    return pcbnew.ToMM(v)


def ref_pads(path):
    b = pcbnew.LoadBoard(path)
    bb = b.GetBoardEdgesBoundingBox()
    cx, cy = mm(bb.GetCenter().x), mm(bb.GetCenter().y)
    fp = next(f for f in b.GetFootprints() if f.GetReference() == "J1")
    pads = {}
    for p in fp.Pads():
        q = p.GetPosition()
        pads.setdefault(p.GetNumber(), []).append((round(mm(q.x) - cx, 4), round(cy - mm(q.y), 4), p.GetNetname()))
    side = "B" if fp.IsFlipped() else "F"
    return pads, side, fp.GetOrientationDegrees(), (mm(fp.GetPosition().x) - cx, cy - mm(fp.GetPosition().y))


def our_pads(lib, name, side, rot, pos):
    board = pcbnew.BOARD()
    fp = pcbnew.FootprintLoad(lib, name)
    board.Add(fp)
    fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(100 + pos[0]), pcbnew.FromMM(100 - pos[1])))
    if side == "B":
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(rot)
    pads = {}
    for p in fp.Pads():
        q = p.GetPosition()
        pads.setdefault(p.GetNumber(), []).append((round(mm(q.x) - 100, 4), round(100 - mm(q.y), 4)))
    return pads


def main():
    b301, s401, lib = sys.argv[1:4]
    refs = {"B301": ref_pads(b301), "S401": ref_pads(s401)}
    ok_all = True
    for board, (src, name, side, rot, pos) in PLAN.items():
        rp, rside, rrot, rpos = refs[src]
        op = our_pads(lib, name, side, rot, pos)
        print(f"== {board}: ours {name} {side} {rot:+.0f}° at O{pos} | {src} J1 {rside} {rrot:+.0f}° at O({rpos[0]:.3f},{rpos[1]:.3f})")
        sig = [n for n in rp if n and n.isdigit()]
        match, worst = 0, 0.0
        for n in sorted(sig, key=int):
            a, b = rp[n][0], op.get(n, [None])[0]
            if b is None:
                print(f"  pad {n}: 우리 풋프린트에 없음")
                continue
            d = max(abs(a[0] - b[0]), abs(a[1] - b[1]))
            worst = max(worst, d)
            if d <= TOL:
                match += 1
            else:
                print(f"  pad {n}: 원본 ({a[0]:.3f},{a[1]:.3f}) 우리 ({b[0]:.3f},{b[1]:.3f}) 차 {d:.3f}")
        # 위치결정 구멍(번호 없는 NPTH)
        holes_r = sorted((x, y) for x, y, _ in rp.get("", []))
        holes_o = sorted(op.get("", []))
        hole_ok = len(holes_r) == len(holes_o) and all(
            max(abs(a[0] - b[0]), abs(a[1] - b[1])) <= TOL for a, b in zip(holes_r, holes_o))
        p1 = op["1"][0]
        print(f"  신호 패드 일치 {match}/{len(sig)} (최대 차 {worst:.4f} mm) · 위치결정 구멍 {'일치' if hole_ok else '불일치'} {holes_o}")
        print(f"  1번 패드 O({p1[0]:.3f},{p1[1]:.3f}) · 원본 1번 넷 {rp['1'][0][2]!r} · 2번 넷 {rp['2'][0][2]!r}")
        ok_all &= match == len(sig) == 60 and hole_ok
        # 대조: 반대 면에 두면 어떻게 되는가 (V-003: F.Cu면 전부 어긋남)
        if side == "B":
            for r in (0, 90, 180, -90):
                alt = our_pads(lib, name, "F", r, pos)
                m = sum(1 for n in sig if n in alt and max(abs(rp[n][0][0] - alt[n][0][0]), abs(rp[n][0][1] - alt[n][0][1])) <= TOL)
                print(f"  (대조) F면 {r:+d}°: {m}/60")
    print("결과:", "일치" if ok_all else "불일치")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
