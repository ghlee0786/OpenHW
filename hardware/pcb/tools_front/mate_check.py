"""짝 커넥터 배치 판정 — 보드 파일 대상 (P-003).

1) 짝 BTB: 우리 보드 J1 패드(번호별 O 좌표)를 Seeed 원본(B301 = 캐리어, S401 = 전면)의 J1 패드와 60/60 대조.
2) DF30 (전면 J3 ↔ S401 J2): 센서 모듈 FPC가 S401과 반대쪽(−Y)으로 나가므로 모듈·DF30 전체가 광축 둘레로 180° 돈다.
   S401 J2 패드를 원점(광축) 기준 180° 돌린 상대 배치(커넥터 원점 기준)와 우리 J3 패드의 상대 배치를 번호별로 대조한다.
   위치(커넥터 원점의 절대 좌표)는 M-001c (0, −12.0)이고 S401 회전 위치 (0.02, −11.55)와 0.45 다르다 — 모듈 FPC 길이 판단은 mechanical.
사용: <KiCad>/bin/python.exe mate_check.py <B301> <S401> <carrier.kicad_pcb> <front.kicad_pcb>
종료 코드 0 = 모두 일치
"""
import sys

import pcbnew

TOL = 0.01


def mm(v):
    return pcbnew.ToMM(v)


def pads(board, ref, frame):
    fp = next(f for f in list(board.GetFootprints()) if f.GetReference() == ref)
    out = {}
    for p in fp.Pads():
        if p.GetNumber().isdigit():
            q = p.GetPosition()
            out[p.GetNumber()] = (mm(q.x) - frame[0], frame[1] - mm(q.y))
    o = fp.GetPosition()
    return out, (mm(o.x) - frame[0], frame[1] - mm(o.y)), fp.GetOrientationDegrees(), "B" if fp.IsFlipped() else "F"


def center(board):
    c = board.GetBoardEdgesBoundingBox().GetCenter()
    return (mm(c.x), mm(c.y))


def compare(a, b, label):
    keys = sorted(set(a) & set(b), key=int)
    bad = [k for k in keys if max(abs(a[k][0] - b[k][0]), abs(a[k][1] - b[k][1])) > TOL]
    worst = max(max(abs(a[k][0] - b[k][0]), abs(a[k][1] - b[k][1])) for k in keys)
    print(f"  {label}: {len(keys) - len(bad)}/{len(keys)} 일치 (최대 차 {worst:.4f} mm){' 불일치 ' + ','.join(bad[:8]) if bad else ''}")
    return not bad and len(keys) == len(a) == len(b)


def main():
    b301, s401, car, fro = (pcbnew.LoadBoard(p) for p in sys.argv[1:5])
    ok = True
    for name, ref_board, ours in (("캐리어 J1 ↔ B301 J1", b301, car), ("전면 J1 ↔ S401 J1", s401, fro)):
        rp, *_ = pads(ref_board, "J1", center(ref_board))
        op, pos, rot, side = pads(ours, "J1", (100.0, 100.0))
        print(f"== {name}: 우리 {side} {rot:+.0f}° O{tuple(round(v, 3) for v in pos)}")
        ok &= compare(rp, op, "패드 번호별 절대 좌표")
    # DF30
    sp, spos, srot, sside = pads(s401, "J2", center(s401))
    op, opos, orot, oside = pads(fro, "J3", (100.0, 100.0))
    print(f"== 전면 J3 DF30: 우리 {oside} {orot:+.0f}° O{tuple(round(v, 3) for v in opos)} | S401 J2 {sside} {srot:+.0f}° O{tuple(round(v, 3) for v in spos)}")
    rel_s = {k: (-(x - spos[0]), -(y - spos[1])) for k, (x, y) in sp.items()}  # 광축 둘레 180°
    rel_o = {k: (x - opos[0], y - opos[1]) for k, (x, y) in op.items()}
    ok &= compare(rel_s, rel_o, "S401을 180° 돌린 상대 배치")
    same = {k: (x - spos[0], y - spos[1]) for k, (x, y) in sp.items()}
    m = sum(1 for k in same if k in rel_o and max(abs(same[k][0] - rel_o[k][0]), abs(same[k][1] - rel_o[k][1])) <= TOL)
    print(f"  (대조) S401과 같은 방향(돌리지 않음)이면: {m}/{len(same)}")
    print("결과:", "일치" if ok else "불일치")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
