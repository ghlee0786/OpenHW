"""보드별 실크 사본 라이브러리 (V-005 RQ-10~15, orch O-74 · O-74b).

보드 프로젝트의 fp-lib-table 이 쓰는 라이브러리 별칭(Resistor_SMD · openhw 등)을 pcb 소유 사본 폴더
hardware/pcb/lib/silk/<보드>/<별칭>.pretty 로 돌린다. 사본에는 그 보드가 쓰는 풋프린트만 두고 실크만 고친다
(패드 · 구멍 · 실크 밖 그림은 원본 그대로 — review E4 가 SOURCES.tsv 의 원본과 기계 대조). FPID 가 그대로라 회로도 일치 0,
보드 부품은 사본과 같아 lib_footprint_mismatch 0.

1단계 (종류별, 자리와 무관):  silk_lib.py <보드>
  - 실크 선폭 0.15, 자기 패드 마스크 개구에서 0.15 안 실크 자르기, 채운 1번 표시는 걸리면 옮김
  - 극성: IR LED 캐소드 선, 1번 점(발진기 · PicoBlade · DF30)
2단계 (자리별, 그 보드에 한 개뿐인 종류만):  silk_lib.py <보드> <board.kicad_pcb>
  - 외곽 0.30 · 이웃 부품 패드 개구 0.15 안 실크를 배치된 자리 기준으로 잘라 사본에 저장
  - 같은 종류가 여러 개인데 자리마다 잘라야 하면 고치지 않고 목록(silk-lib-<보드>.json)에 남긴다 (O-74 ③)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

import pcbnew

sys.path.insert(0, str(Path(__file__).resolve().parent))
import silk  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
STD = Path(r"C:\Users\gh\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints")
SRC = {"openhw": ROOT / "hardware/libraries/openhw.pretty", "OpenHW_Mech": ROOT / "hardware/pcb/lib/OpenHW_Mech.pretty"}
DOTS = ("Oscillator_SMD_SiT_PQFN-4Pin", "Molex_PicoBlade_53261-0271", "Hirose_DF30FC-24DS")  # RQ-15 · B9 1번 점
FAR = (-1e6, -1e6, 1e6, 1e6)
IO = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)


# 지울 실크 도형 표시용 선폭. swig 에서 FOOTPRINT.Remove 는 이후 객체를 깨뜨리므로(P-003 실측) graft() 가 그 도형을 빼고 옮긴다
DROP_W = pcbnew.FromMM(0.0111)


def top_blocks(t):
    """풋프린트 파일의 최상위 자식 블록 (시작, 끝) — 시작은 앞 공백 포함."""
    out, depth, j = [], 0, t.index("(") + 1
    start = None
    while j < len(t):
        ch = t[j]
        if ch == "(":
            if depth == 0:
                k = j
                while k > 0 and t[k - 1] in " \t\r\n":
                    k -= 1
                start = k
            depth += 1
        elif ch == ")":
            if depth == 0:
                break
            depth -= 1
            if depth == 0:
                out.append((start, j + 1))
        j += 1
    return out


def is_silk(blk):
    s = blk.lstrip()
    return s.startswith(("(fp_line", "(fp_arc", "(fp_circle", "(fp_rect", "(fp_poly")) and \
        ('(layer "F.SilkS")' in blk or '(layer "B.SilkS")' in blk)


def graft(saved, src):
    """원본 파일 글자는 그대로 두고 실크 도형 블록만 저장본(고친 것)의 실크 블록으로 바꾼다 — 패드 · 구멍 · 실크 밖 그림은 원본과 글자까지 같다
    (O-74b · review E4). 지울 표시(선폭 0.0111)는 넣지 않는다."""
    ts = open(saved, encoding="utf-8").read()
    new = [ts[a:b] for a, b in top_blocks(ts) if is_silk(ts[a:b]) and "(width 0.0111)" not in ts[a:b]]
    to = open(src, encoding="utf-8").read()
    bl = top_blocks(to)
    silk_bl = [(a, b) for a, b in bl if is_silk(to[a:b])]
    if silk_bl:
        at = silk_bl[0][0]
    else:
        at = next(a for a, b in bl if to[a:b].lstrip().startswith("(pad"))
    out, i = [], 0
    for a, b in silk_bl:
        out.append(to[i:a])
        if a == at:
            out.append("".join(new))
        i = b
    if not silk_bl:
        out.append(to[:at] + "".join(new))
        i = at
    out.append(to[i:])
    open(saved, "w", encoding="utf-8", newline="").write("".join(out))


# M-007 (mechanical cdce9bd §1): 대체 3D 모델 — 원점 · 회전 · 오프셋 0, 배율 1. 같은 풋프린트를 쓰는 모든 부품에 붙는다
MODELS = ("USB_C_Receptacle_HRO_TYPE-C-31-M-12", "RJ45_Hanrun_HR911105A_Horizontal", "L_Bourns_SRP7028A_7.3x6.6mm",
          "SOT-523", "Oscillator_SMD_SiT_PQFN-4Pin_2.0x1.6mm")


def set_model(path, name):
    """사본의 (model "...") 경로를 저장소 mechanical/models 의 대체 모델로 바꾼다(없으면 블록을 더한다). 모델은 그림이 아니라 E4 대조 밖."""
    if name not in MODELS or not (ROOT / "mechanical/models" / f"{name}.step").exists():
        return
    uri = "${KIPRJMOD}/../../../mechanical/models/" + f"{name}.step"
    t = open(path, encoding="utf-8").read()
    blk = (f'\t(model "{uri}"\n\t\t(offset\n\t\t\t(xyz 0 0 0)\n\t\t)\n\t\t(scale\n\t\t\t(xyz 1 1 1)\n\t\t)\n'
           f'\t\t(rotate\n\t\t\t(xyz 0 0 0)\n\t\t)\n\t)\n')
    i = t.find("\t(model ")
    if i >= 0:
        j, depth = i + 1, 0
        while True:
            depth += t[j] == "("
            depth -= t[j] == ")"
            j += 1
            if depth == 0:
                break
        t = t[:i] + blk.rstrip("\n") + t[j:]
    else:
        k = t.rstrip().rfind(")")
        t = t[:k] + blk + t[k:]
    open(path, "w", encoding="utf-8", newline="").write(t)


def src_path(lib):
    return SRC.get(lib, STD / f"{lib}.pretty")


def out_dir(board):
    return ROOT / "hardware/pcb/lib/silk" / board


def used_fpids(board):
    t = open(ROOT / f"hardware/schematic/{board}/{board}.net", encoding="utf-8").read()
    ids = set(re.findall(r'\(footprint "([^"]+:[^"]+)"\)', t))
    ids.add("OpenHW_Mech:MountingHole_M1.6_NPTH")  # 회로도에 없는 보드 전용(템플릿 장착 구멍)
    return sorted(ids)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def fix_types(board):
    od = out_dir(board)
    rows, log = [], {"marks": [], "widened": 0, "clipped": {}, "to_fab": {}, "dots_fail": [], "other_shapes": [], "marks_moved": [],
                     "refs_silk": [], "refs_fab_only": []}
    for fpid in used_fpids(board):
        lib, name = fpid.split(":", 1)
        sp = src_path(lib) / f"{name}.kicad_mod"
        b = pcbnew.BOARD()
        b.GetDesignSettings().m_SolderMaskExpansion = pcbnew.FromMM(0.05)  # 두 보드 설정과 같게(마스크 개구 = 패드 + 0.05)
        fp = pcbnew.FootprintLoad(str(src_path(lib)), name)
        if fp is None:
            raise SystemExit(f"원본 없음: {fpid}")
        fp.SetFPID(pcbnew.LIB_ID(lib, name))
        fp.SetReference("D_IR_1" if name.startswith("Vishay_VSMA") else "REF")
        b.Add(fp)
        dots = {"REF"} if name.startswith(DOTS) else set()
        silk.polarity_marks(b, FAR, log, dots)
        for s in ("F", "B"):
            silk.clip_lines(b, s, silk.mask_openings(b, s), FAR, log)
        fp.SetReference("REF")
        for _, g in log.pop("drop", []):
            g.SetWidth(DROP_W)
        lp = od / f"{lib}.pretty"
        lp.mkdir(parents=True, exist_ok=True)
        IO.FootprintSave(str(lp), fp)
        graft(lp / f"{name}.kicad_mod", sp)
        set_model(lp / f"{name}.kicad_mod", name)
        src = f"{lib}:{name}" if lib in SRC else "${KICAD10_FOOTPRINT_DIR}/" + f"{lib}.pretty/{name}.kicad_mod"
        rows.append((f"{lib}.pretty/{name}.kicad_mod", src, sha(sp)))
    # O-74b: copy = 사본 파일(이 폴더 기준), source = 원본(KiCad 10.0.8 표준 또는 프로젝트 라이브러리:이름), sha256 = 원본 파일
    with open(od / "SOURCES.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("copy\tsource\tsha256\n")
        for c_, s_, h in rows:
            f.write(f"{c_}\t{s_}\t{h}\n")
    print(f"{board}: 실크 사본 {len(rows)}종 · 폭 0.15로 {log['widened']} · 자름 {log['clipped']} · 지운 실크 {log['to_fab']} · "
          f"표시 {len(log['marks'])} · 옮긴 표시 {len(log['marks_moved'])}")
    return log


def fix_places(board, pcb_path):
    od = out_dir(board)
    b = pcbnew.LoadBoard(pcb_path)
    eb = b.GetBoardEdgesBoundingBox()
    edge = (silk.TO(eb.GetLeft()), silk.TO(eb.GetTop()), silk.TO(eb.GetRight()), silk.TO(eb.GetBottom()))
    count = {}
    for fp in b.GetFootprints():
        k = fp.GetFPIDAsString()
        count[k] = count.get(k, 0) + 1
    res = {"saved": [], "multi_left": []}
    for s in ("F", "B"):
        op = silk.mask_openings(b, s)
        for fp in list(b.GetFootprints()):
            if silk.side_of(fp) != s:
                continue
            # 이 부품 실크만 담은 임시 판정: 걸리는 실크가 있는지
            log = {"marks": [], "widened": 0, "clipped": {}, "to_fab": {}, "dots_fail": [], "other_shapes": [], "marks_moved": []}
            tmp = pcbnew.BOARD()
            c = pcbnew.Cast_to_FOOTPRINT(fp.Duplicate(False))
            tmp.Add(c)
            silk.clip_lines(tmp, s, op, edge, log)
            for _, g in log.pop("drop", []):
                g.SetWidth(DROP_W)
            if not log["clipped"].get(s) and not log["marks_moved"]:
                continue
            k = fp.GetFPIDAsString()
            if count[k] > 1:
                res["multi_left"].append({"ref": fp.GetReference(), "fpid": k, "side": s})
                continue
            lib = k.split(":", 1)[0]
            IO.FootprintSave(str(od / f"{lib}.pretty"), c)
            nm = k.split(":", 1)[1]
            graft(od / f"{lib}.pretty" / f"{nm}.kicad_mod", src_path(lib) / f"{nm}.kicad_mod")
            res["saved"].append({"ref": fp.GetReference(), "fpid": k})
    json.dump(res, open(ROOT / f"hardware/pcb/route/silk-lib-{board}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{board}: 자리별 사본 {len(res['saved'])} {[r['ref'] for r in res['saved']]} · 여러 개라 못 고침 {len(res['multi_left'])} "
          f"{[r['ref'] for r in res['multi_left']]}")


if __name__ == "__main__":
    if len(sys.argv) == 2:
        fix_types(sys.argv[1])
    else:
        fix_places(sys.argv[1], sys.argv[2])
