"""R-026: Freerouting DSN에 프로젝트 규칙을 넣는다 (보드 사본에서만 실행 — 원본 보드 금지).

export <board.kicad_pcb> <out.dsn> <mode>
    mode=hs  : 고속(CSI_100·MDI_100·USB_90)·전원(PWR_*) 넷클래스, IR 열 넷, GND 비아를 잠근다 (fix).
               나머지 저속 트랙은 풀어 둔다 (pcb freeroute.py 와 같은 잠금 범위).
    mode=all : 기존 트랙·비아를 전부 잠근다 (미연결만 잇게 함).
    잠근 뒤 pcbnew.ExportSpecctraDSN 으로 DSN 을 만들고, KiCad 내보내기가 빠뜨리는 규칙을 DSN 에 넣는다.
      - 고속 넷클래스 class rule clearance 200 -> 300   (DRU hs_track_spacing 0.30)
      - boundary 안쪽 0.2mm 폭 keepout 띠(모든 층)
        (DRU fab_copper_to_edge 0.40, Freerouting 은 boundary 를 class 간격 0.20 으로만 띄운다)
import <board.kicad_pcb> <in.ses> [base-drc.json]
    pcbnew.ImportSpecctraSES -> 고정 대상 넷의 새 배선 제거 -> (base-drc.json 을 주면 기준 신호 미연결 넷 밖의
    새 배선도 제거) -> 면 다시 채우기 -> 저장.
"""
import fnmatch
import json
import re
import sys
from pathlib import Path

import pcbnew

HS = {"CSI_100", "MDI_100", "USB_90"}
FIXED_CLASSES = HS | {"PWR_12V_IN", "PWR_5V", "PWR_12V_IR", "PWR_LOGIC"}
FIXED_NETS = {"/IRA_SET", "/IRA_M", "/IRB_SET", "/IRB_M"}
EDGE_EXTRA = 200  # um: DRU 가장자리 0.40 - Freerouting 이 이미 지키는 class 간격 0.20


def lock(b, mode):
    n_lock = n_free = 0
    for t in b.GetTracks():
        net = t.GetNetname()
        is_via = t.Type() == pcbnew.PCB_VIA_T
        cls = t.GetNet().GetNetClassName() if t.GetNet() else ""
        lk = mode == "all" or cls in FIXED_CLASSES or net in FIXED_NETS or (net == "/GND" and is_via)
        t.SetLocked(lk)
        n_lock += lk
        n_free += not lk
    return n_lock, n_free


def patch_dsn(text):
    """KiCad DSN 내보내기에 빠진 프로젝트 규칙을 넣는다. 바꾼 항목 수를 함께 돌려준다."""
    n_hs = 0
    out, cur = [], None
    for line in text.split("\n"):
        m = re.match(r"\s*\(class (\S+)", line)
        if m:
            cur = m.group(1)
        if cur in HS and line.strip() == "(clearance 200)":
            line = line.replace("(clearance 200)", "(clearance 300)")
            n_hs += 1
            cur = None
        out.append(line)
    text = "\n".join(out)
    # GND_PWR: 보드 층 형식이 power 라 DSN 에 면 전용으로 나가지만 기존 신호 트랙이 있다 -> signal 로
    text, n_pwr = re.subn(r"(\(layer GND_PWR\s*\(type )power\)", r"\1signal)", text)
    # 가장자리: boundary 다각형(사각형)을 따라 EDGE_EXTRA 폭 keepout 띠를 모든 층에 둔다
    m = re.search(r"\(boundary\s*\(path pcb 0\s+([-\d.\s]+)\)", text)
    n_edge = 0
    if m:
        v = [float(x) for x in m.group(1).split()]
        xs, ys = v[0::2], v[1::2]
        x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
        e = EDGE_EXTRA
        strips = [(x0, y0, x1, y0 + e), (x0, y1 - e, x1, y1), (x0, y0, x0 + e, y1), (x1 - e, y0, x1, y1)]
        layers = re.findall(r"\(layer (\S+)\s*\(type (?:signal|power)\)", text)
        ko = "".join(f'    (keepout "r026_edge" (rect {L} {a:g} {b:g} {c:g} {d:g}))\n'
                     for L in layers for a, b, c, d in strips)
        n_edge = len(layers) * 4
        i = text.index("(boundary")
        text = text[:i] + ko.lstrip() + "    " + text[i:]
    return text, n_hs, n_pwr, n_edge


def export(board_path, dsn, mode):
    b = pcbnew.LoadBoard(board_path)
    n_lock, n_free = lock(b, mode)
    b.Save(board_path)
    b = pcbnew.LoadBoard(board_path)
    # DRU 조건용 규칙 구역(DP_BRK·DP_TUNE·DP_TWIST·K_* — 아무것도 금지하지 않음)은 KiCad 가 DSN keepout 으로 내보내
    # Freerouting 에 장애물이 된다. 메모리에서만 빼고 내보낸다(보드 파일에는 남음 — DRC 에 필요).
    cond = [z for z in b.Zones() if z.GetIsRuleArea() and not (
        z.GetDoNotAllowTracks() or z.GetDoNotAllowVias() or z.GetDoNotAllowPads() or z.GetDoNotAllowZoneFills()
        or z.GetDoNotAllowFootprints())]
    for z in cond:
        b.Remove(z)
    print(f"조건용 규칙 구역 제외 {len(cond)}")
    ok = pcbnew.ExportSpecctraDSN(b, dsn)
    raw = Path(dsn).read_text(encoding="utf-8")
    Path(dsn + ".orig").write_text(raw, encoding="utf-8")
    new, n_hs, n_pwr, n_edge = patch_dsn(raw)
    Path(dsn).write_text(new, encoding="utf-8")
    print(f"DSN {dsn} ok={ok} mode={mode} 고정 {n_lock} 자유 {n_free} · 고속 class 간격 300: {n_hs} · GND_PWR signal: {n_pwr} · 가장자리 keepout: {n_edge}")
    return 0 if ok and n_hs >= 1 else 1


def import_(board_path, ses, keep_nets=None):
    b = pcbnew.LoadBoard(board_path)
    # ImportSpecctraSES 는 잠기지 않은 트랙·비아를 지우고 SES 의 fix 배선은 다시 넣지 않는다 -> 기존 배선을 모두
    # 잠가 두고 가져온 뒤, 원래 잠금 상태로 되돌린다. 새 배선은 UUID 로 가린다.
    orig = {}
    for t in b.GetTracks():
        orig[t.m_Uuid.AsString()] = t.IsLocked()
        t.SetLocked(True)
    ok = pcbnew.ImportSpecctraSES(b, ses)
    new = [t for t in b.GetTracks() if t.m_Uuid.AsString() not in orig]
    # 저속 넷만: Freerouting 이 고정 대상 넷(고속·전원·IR 열)에 새로 놓은 트랙·비아는 지운다.
    # 넷클래스 폭·쌍·층 규칙을 Freerouting 이 지키지 못하기 때문.
    # keep_nets(기준 DRC 에서 신호 미연결이 있던 넷)를 주면, 그 밖의 넷에 덧놓인 새 배선(중복)도 지운다.
    drop = [t for t in new if t.GetNet() and (
        t.GetNet().GetNetClassName() in FIXED_CLASSES or t.GetNetname() in FIXED_NETS
        or (keep_nets is not None and t.GetNetname() not in keep_nets))]
    for t in drop:
        b.Remove(t)
    kept = 0
    for t in b.GetTracks():
        u = t.m_Uuid.AsString()
        if u in orig:
            kept += 1
            t.SetLocked(orig[u])
    n_locked = sum(t.IsLocked() for t in b.GetTracks())
    print(f"기존 트랙·비아 {len(orig)} 중 유지 {kept} · 새 배선 {len(new)} 중 제거 {len(drop)}")
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(board_path)
    print(f"SES {ses} ok={ok} 트랙·비아 {len(b.GetTracks())} · 잠김 {n_locked} · 고정 대상 넷 새 배선 제거 {len(drop)}")
    return 0 if ok else 1


if __name__ == "__main__":
    if sys.argv[1] == "export":
        sys.exit(export(sys.argv[2], sys.argv[3], sys.argv[4]))
    keep = None
    if len(sys.argv) > 4:  # 기준 DRC json: 신호 미연결(구역 아닌 항목)의 넷만 새 배선을 남긴다
        d = json.loads(Path(sys.argv[4]).read_text(encoding="utf-8"))
        keep = {re.search(r"\[([^\]]+)\]", u["items"][0]["description"]).group(1) for u in d["unconnected_items"]
                if not any(i["description"].startswith("구역") for i in u["items"])}
        print(f"새 배선을 남길 넷 {len(keep)}")
    sys.exit(import_(sys.argv[2], sys.argv[3], keep))
