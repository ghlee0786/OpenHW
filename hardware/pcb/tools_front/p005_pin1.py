"""P-005 전면 (review V-006a #10): 1번 핀 실크 점(Ø0.4 채움)을 J2(CLA216 리드 납땜 패드 — 1번 = ICR_A 빨강(+))와 J4(JST GH 6P)에 넣는다.
실크 사본 라이브러리(hardware/pcb/lib/silk/front)와 보드의 그 부품에 같은 자리로 넣어 lib_footprint_mismatch 가 생기지 않게 한다
(사본은 실크만 고친다 — O-74b). 자리 = 1번 패드에서 몸체 중심 반대쪽 대각, 패드 가장자리에서 0.43(silk.py 의 1번 점과 같은 식).
사용: <KiCad>/bin/python.exe p005_pin1.py <board.kicad_pcb>
"""
import math
import sys
from pathlib import Path

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM
ROOT = Path(__file__).resolve().parents[3]
LIB = ROOT / "hardware/pcb/lib/silk/front"
R, W = 0.2, 0.15
OFF = 0.05 + 0.15 + R + 0.03
NL = chr(10)
CRNL = chr(13) + chr(10)
TAB = chr(9)


def dot_local(fp):
    """라이브러리 풋프린트(원점 · 0° · 앞면) 좌표에서 점 중심."""
    pads = [p for p in fp.Pads() if p.GetNumber().isdigit()]
    p1 = next(p for p in pads if p.GetNumber() == "1")
    cx = sum(TO(p.GetPosition().x) for p in pads) / len(pads)
    cy = sum(TO(p.GetPosition().y) for p in pads) / len(pads)
    px, py = TO(p1.GetPosition().x), TO(p1.GetPosition().y)
    bb = p1.GetBoundingBox()
    hw, hh = TO(bb.GetWidth()) / 2, TO(bb.GetHeight()) / 2
    ux = 1 if px >= cx else -1
    uy = 1 if py >= cy else -1
    return round(px + ux * (hw + OFF), 3), round(py + uy * (hh + OFF), 3)


def add_dot(fp, layer, x, y, ex, ey):
    s = pcbnew.PCB_SHAPE(fp, pcbnew.SHAPE_T_CIRCLE)
    s.SetLayer(layer)
    s.SetCenter(pcbnew.VECTOR2I(MM(x), MM(y)))
    s.SetEnd(pcbnew.VECTOR2I(MM(ex), MM(ey)))
    s.SetWidth(MM(W))
    s.SetFilled(True)
    fp.Add(s)


def has_dot(fp):
    return any(g.GetClass() == "PCB_SHAPE" and g.GetShape() == pcbnew.SHAPE_T_CIRCLE and g.IsFilled()
               and g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) for g in fp.GraphicalItems())


def lib_insert(libdir, name, lx, ly):
    """사본 파일에는 글자로 끼워 넣는다 — pcbnew.FootprintSave 는 파일 전체를 다시 써서 보드 부품과 달라진다(lib_footprint_mismatch)."""
    lp = Path(libdir) / (name + ".kicad_mod")
    raw = lp.read_bytes()
    eol = CRNL if CRNL.encode() in raw else NL
    t = raw.decode("utf-8").replace(CRNL, NL)
    lines = ["(fp_circle", TAB + f"(center {lx:.3f} {ly:.3f})", TAB + f"(end {lx + R - W / 2:.3f} {ly:.3f})",
             TAB + "(stroke", TAB + TAB + f"(width {W})", TAB + TAB + "(type solid)", TAB + ")",
             TAB + "(fill yes)", TAB + '(layer "F.SilkS")', ")"]
    blk = "".join(TAB + ln + NL for ln in lines)
    k = t.index(NL + TAB + "(pad ") + 1
    lp.write_bytes((t[:k] + blk + t[k:]).replace(NL, eol).encode("utf-8"))


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    for ref in ("J2", "J4"):
        fp = b.FindFootprintByReference(ref)
        nick, name = str(fp.GetFPID().GetLibNickname()), str(fp.GetFPID().GetLibItemName())
        libdir = str(LIB / (nick + ".pretty"))
        lf = pcbnew.FootprintLoad(libdir, name)
        if has_dot(lf) and has_dot(fp):
            print(ref, "이미 있음")
            continue
        lx, ly = dot_local(lf)
        if not has_dot(lf):
            lib_insert(libdir, name, lx, ly)
        # 보드 좌표: 라이브러리 좌표 → (뒤집힘) → 회전 → 이동. 1 · 2번 패드로 맞는 변환을 고른다.
        lp1 = next(p for p in lf.Pads() if p.GetNumber() == "1").GetPosition()
        bp1 = next(p for p in fp.Pads() if p.GetNumber() == "1").GetPosition()
        lq = next(p for p in lf.Pads() if p.GetNumber() == "2").GetPosition()
        bq = next(p for p in fp.Pads() if p.GetNumber() == "2").GetPosition()
        ang = math.radians(fp.GetOrientationDegrees())
        pos = fp.GetPosition()
        best = None
        for mx in (1, -1):
            for my in (1, -1):
                for sgn in (1, -1):
                    def tr(x, y, mx=mx, my=my, sgn=sgn):
                        x, y = x * mx, y * my
                        a = sgn * ang
                        return TO(pos.x) + x * math.cos(a) + y * math.sin(a), TO(pos.y) - x * math.sin(a) + y * math.cos(a)
                    e1, e2 = tr(TO(lp1.x), TO(lp1.y)), tr(TO(lq.x), TO(lq.y))
                    err = math.hypot(e1[0] - TO(bp1.x), e1[1] - TO(bp1.y)) + math.hypot(e2[0] - TO(bq.x), e2[1] - TO(bq.y))
                    if best is None or err < best[0]:
                        best = (err, tr)
        assert best[0] < 0.01, (ref, best[0])
        x, y = best[1](lx, ly)
        ex, ey = best[1](round(lx + R - W / 2, 3), ly)
        if not has_dot(fp):
            add_dot(fp, pcbnew.B_SilkS if fp.IsFlipped() else pcbnew.F_SilkS, x, y, ex, ey)
        print(f"{ref}: 1번 점 사본 좌표 ({lx:.3f},{ly:.3f}) → 보드 ({x:.3f},{y:.3f})")
    b.Save(sys.argv[1])


if __name__ == "__main__":
    main()
