"""Freerouting 연동 (P-003, O-51): 저속 신호만 자동 배선. KiCad GUI 없이 pcbnew 파이썬으로 DSN 내보내기·SES 가져오기.

고정(잠금 → DSN 에서 protect, Freerouting 이 옮기지 않음):
  - 고속 차동 넷클래스(CSI_100·MDI_100·USB_90) 트랙·비아 — 쌍·꼬임·순서 잇기(USB 테스트점) 포함
  - 전원 넷클래스(PWR_12V_IN·PWR_5V·PWR_12V_IR·PWR_LOGIC) 트랙·비아
  - IR 열 패드 구간 넷(LED 애노드: IRA_SET·IRA_M·IRB_SET·IRB_M) 트랙·비아, GND 비아(면 연결)
나머지(저속 신호) 트랙은 잠그지 않는다 — Freerouting 이 다시 놓거나 그대로 쓴다.
자동 배선 결과를 최적이라 주장하지 않는다. 판정은 kicad-cli DRC(--schematic-parity) 종료 코드.

사용:
  <KiCad>/bin/python.exe freeroute.py export <board.kicad_pcb> <out.dsn> <fixed-list.txt> [all]   (all = 기존 배선 전부 고정)
  <KiCad>/bin/python.exe freeroute.py import <board.kicad_pcb> <in.ses>
"""
import fnmatch
import json
import sys
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[3]
NC = json.loads((ROOT / "hardware/pcb/rules/netclasses.json").read_text(encoding="utf-8"))
FIXED_CLASSES = {"CSI_100", "MDI_100", "USB_90", "PWR_12V_IN", "PWR_5V", "PWR_12V_IR", "PWR_LOGIC"}
FIXED_NETS = {"/IRA_SET", "/IRA_M", "/IRB_SET", "/IRB_M"}


def netclass(net):
    name = net.lstrip("/")
    best = None
    for p in NC["patterns"]:
        if fnmatch.fnmatchcase(net, p["pattern"]) or fnmatch.fnmatchcase(name, p["pattern"]):
            c = next(c for c in NC["classes"] if c["name"] == p["netclass"])
            if best is None or c.get("priority", 99) < best.get("priority", 99):
                best = c
    return (best or NC["classes"][0])["name"]


def export(board_path, dsn, listing, lock_all=False):
    b = pcbnew.LoadBoard(board_path)
    fixed = {}
    n_lock = n_free = 0
    for t in b.GetTracks():
        net = t.GetNetname()
        is_via = t.Type() == pcbnew.PCB_VIA_T
        # lock_all (orch: 남은 미연결만 Freerouting 재투입): 스크립트 배선 전부 고정, 미연결만 Freerouting 이 잇는다
        lock = lock_all or netclass(net) in FIXED_CLASSES or net in FIXED_NETS or (net == "/GND" and is_via)
        t.SetLocked(lock)
        if lock:
            fixed[net] = fixed.get(net, 0) + 1
            n_lock += 1
        else:
            n_free += 1
    b.Save(board_path)
    b = pcbnew.LoadBoard(board_path)
    ok = pcbnew.ExportSpecctraDSN(b, dsn)
    Path(listing).write_text("고정(잠금) 트랙·비아 수 — 넷별\n" + "\n".join(f"{n}\t{c}" for n, c in sorted(fixed.items())) + "\n",
                             encoding="utf-8")
    print(f"DSN {dsn} ok={ok} · 고정 {n_lock} · 자유 {n_free} · 고정 넷 {len(fixed)}")


def import_(board_path, ses):
    b = pcbnew.LoadBoard(board_path)
    ok = pcbnew.ImportSpecctraSES(b, ses)
    pcbnew.ZONE_FILLER(b).Fill(b.Zones())
    b.Save(board_path)
    print(f"SES {ses} ok={ok} · 트랙·비아 {len(b.GetTracks())}")


if __name__ == "__main__":
    if sys.argv[1] == "export":
        export(sys.argv[2], sys.argv[3], sys.argv[4], len(sys.argv) > 5 and sys.argv[5] == "all")
    else:
        import_(sys.argv[2], sys.argv[3])
