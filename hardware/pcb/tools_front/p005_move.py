"""P-005 전면: 부품 옮기기 (KiCad pcbnew) — O-105 A(막힌 구역 부품 재배치). 커넥터 · 장착 구멍 · 잠긴 부품은 거부.
사용: <KiCad>/bin/python.exe p005_move.py <board.kicad_pcb> <ref> <x mm> <y mm> <회전 도>
"""
import sys

import pcbnew

MM, TO = pcbnew.FromMM, pcbnew.ToMM


def main():
    b = pcbnew.LoadBoard(sys.argv[1])
    ref, x, y, rot = sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
    fp = b.FindFootprintByReference(ref)
    if fp.IsLocked() or ref[0] in "JH" or ref.startswith("MH"):
        print("거부: 고정 부품", ref)
        sys.exit(2)
    p0 = fp.GetPosition()
    print(f"{ref}: ({TO(p0.x):.3f},{TO(p0.y):.3f}) {fp.GetOrientationDegrees():.0f}° → ({x:.3f},{y:.3f}) {rot:.0f}°")
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    fp.SetOrientationDegrees(rot)
    for p in fp.Pads():
        print("  ", p.GetNumber(), p.GetNetname(), round(TO(p.GetPosition().x), 3), round(TO(p.GetPosition().y), 3))
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(sys.argv[1])


if __name__ == "__main__":
    main()
