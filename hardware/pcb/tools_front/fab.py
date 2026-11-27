"""P-004 준비 (KiCad pcbnew): aux(드릴/좌표) 원점을 보드 외곽 왼쪽 아래로 두고(R-010 #4 · review vd001-format §3 — Gerber 외곽 최소 (0,0)),
PCBWay 열 이름의 면별 CPL <보드>-top-pos.csv · <보드>-bottom-pos.csv 를 쓴다(R-010 #5 · S3). STEP 은 내보낼 때 --user-origin 으로 코어 중심(100,100)을 명시한다.

CPL (PCBWay 표본 Centroid 열 이름, 단위 mm — 표본은 mil 이라 머리글 아래 'Units: mm' 을 따로 적지 않고 파일 이름과 README 에 적는다):
  Designator, Footprint, Mid X, Mid Y, Ref X, Ref Y, Pad X, Pad Y, TB, Rotation, Comment
  - Mid = 풋프린트 원점(KiCad 자리), Ref = Mid, Pad = 1번 패드 중심. 원점 = 보드 왼쪽 아래, +Y 위.
  - 회전: KiCad 값 그대로, 윗면에서 본 각도 0~360(뒷면도 윗면 시점, X 미러 없음 — R-010 S9: 보정 없음, 생산 전 확인).
  - 실장 SMD 만(THT 전용 · 보드 전용 · 시험점 · DNP 제외). 혼합(SMD+THT 다리) USB-C 는 SMD 로 넣는다(make_pcbway_bom 의 HYBRID 와 같음).
사용: <KiCad>/bin/python.exe fab.py <board.kicad_pcb> <출력 폴더> <보드 이름>
"""
import csv
import re
import sys
from pathlib import Path

import pcbnew

TO = pcbnew.ToMM


def main():
    path, out, name = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
    b = pcbnew.LoadBoard(path)
    eb = b.GetBoardEdgesBoundingBox()
    org = pcbnew.VECTOR2I(eb.GetLeft(), eb.GetBottom())
    ds = b.GetDesignSettings()
    ds.SetAuxOrigin(org)
    b.Save(path)
    ox, oy = TO(org.x), TO(org.y)
    out.mkdir(parents=True, exist_ok=True)
    rows = {"top": [], "bottom": []}
    skipped = []
    for fp in b.GetFootprints():
        ref = fp.GetReference()
        attr = fp.GetAttributes()
        smd = bool(attr & pcbnew.FP_SMD)
        if fp.IsBoardOnly() or re.fullmatch(r"TP\d+", ref) or fp.IsDNP() or not smd:
            skipped.append(ref)
            continue
        side = "bottom" if fp.IsFlipped() else "top"
        p = fp.GetPosition()
        pads = [q for q in fp.Pads() if q.GetNumber() == "1"] or list(fp.Pads())
        pp = pads[0].GetPosition()
        mx, my = round(TO(p.x) - ox, 4), round(oy - TO(p.y), 4)
        rows[side].append([ref, fp.GetFPID().GetUniStringLibItemName(), mx, my, mx, my,
                           round(TO(pp.x) - ox, 4), round(oy - TO(pp.y), 4), "T" if side == "top" else "B",
                           round(fp.GetOrientationDegrees() % 360, 2), fp.GetValue()])
    head = ["Designator", "Footprint", "Mid X", "Mid Y", "Ref X", "Ref Y", "Pad X", "Pad Y", "TB", "Rotation", "Comment"]
    for side, rs in rows.items():
        rs.sort(key=lambda r: (re.match(r"[A-Z_]+", r[0]).group(0), int(re.search(r"\d+$", r[0]).group(0))))
        with open(out / f"{name}-{side}-pos.csv", "w", encoding="ascii", errors="replace", newline="") as f:
            w = csv.writer(f)
            w.writerow(head)
            w.writerows(rs)
    print(f"{name}: 원점 ({ox:.3f}, {oy:.3f}) · CPL 윗면 {len(rows['top'])} · 뒷면 {len(rows['bottom'])} · 뺀 것 {len(skipped)} {sorted(skipped)}")


if __name__ == "__main__":
    main()
