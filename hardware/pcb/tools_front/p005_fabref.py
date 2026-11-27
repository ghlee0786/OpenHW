"""P-005 전면 (review V-006a #13): 조립도용 Fab 참조 지정자 `${REFERENCE}` 가 없는 openhw 풋프린트 4종에 Fab 글자를 넣는다.

lib   : 원본(hardware/libraries/openhw.pretty)과 전면 실크 사본(hardware/pcb/lib/silk/front/openhw.pretty)에 같은 글자를 넣고
        사본 SOURCES.tsv 의 원본 sha256 을 고친다 (시스템 파이썬).   사용: python p005_fabref.py lib
board : 보드의 그 풋프린트들에 같은 글자를 넣는다 (KiCad pcbnew).      사용: <KiCad>/bin/python.exe p005_fabref.py board <board.kicad_pcb>
글자: 풋프린트 원점, 크기 0.5 · 획 0.08, F.Fab (뒷면 부품이면 뒤집힐 때 B.Fab).
"""
import hashlib
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAMES = ["CLA216_ICR_SolderPads_1x02_P2.54mm", "Everlight_ALS-PT19_1.7x0.8mm", "Lite-On_LTR-329ALS-01_2x2mm_P1.2mm", "Vishay_VSMA1085600_3.4x3.4mm"]
SIZE, THICK = 0.5, 0.08
BLOCK = ('\t(fp_text user "${REFERENCE}"\n\t\t(at 0 0 0)\n\t\t(layer "F.Fab")\n\t\t(effects\n\t\t\t(font\n'
         f'\t\t\t\t(size {SIZE} {SIZE})\n\t\t\t\t(thickness {THICK})\n\t\t\t)\n\t\t)\n\t)\n')


def lib():
    src = ROOT / "hardware/libraries/openhw.pretty"
    cpy = ROOT / "hardware/pcb/lib/silk/front/openhw.pretty"
    tsv = ROOT / "hardware/pcb/lib/silk/front/SOURCES.tsv"
    rows = tsv.read_text(encoding="utf-8")
    for n in NAMES:
        for d in (src, cpy):
            p = d / f"{n}.kicad_mod"
            raw = p.read_bytes()
            eol = b"\r\n" if b"\r\n" in raw else b"\n"
            t = raw.decode("utf-8").replace("\r\n", "\n")
            if '"${REFERENCE}"' in t:
                continue
            m = re.search(r"\n\t\(pad ", t)
            t = t[:m.start() + 1] + BLOCK + t[m.start() + 1:]
            p.write_bytes(t.replace("\n", eol.decode()).encode("utf-8"))
        sha = hashlib.sha256((src / f"{n}.kicad_mod").read_bytes()).hexdigest()
        rows, k = re.subn(rf"(openhw\.pretty/{re.escape(n)}\.kicad_mod\topenhw:{re.escape(n)}\t)[0-9a-f]{{64}}", rf"\g<1>{sha}", rows)
        print(n, "sha", sha[:12], "행", k)
    tsv.write_text(rows, encoding="utf-8", newline="\n")


def board(path):
    import pcbnew
    b = pcbnew.LoadBoard(path)
    n = 0
    for fp in b.GetFootprints():
        if str(fp.GetFPID().GetLibItemName()) not in NAMES:
            continue
        if any(g.GetClass() == "PCB_TEXT" and g.GetText() == "${REFERENCE}" for g in fp.GraphicalItems()):
            continue
        t = pcbnew.PCB_TEXT(fp)
        t.SetText("${REFERENCE}")
        t.SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
        t.SetPosition(fp.GetPosition())
        t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(SIZE), pcbnew.FromMM(SIZE)))
        t.SetTextThickness(pcbnew.FromMM(THICK))
        t.SetTextAngleDegrees(fp.GetOrientationDegrees())
        t.SetMirrored(fp.IsFlipped())
        fp.Add(t)
        n += 1
        print("Fab 참조:", fp.GetReference())
    b.Save(path)
    print("넣음", n)


if __name__ == "__main__":
    if sys.argv[1] == "lib":
        lib()
    else:
        board(sys.argv[2])
