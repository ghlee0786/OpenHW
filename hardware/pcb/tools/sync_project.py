"""hardware/pcb/rules/netclasses.json → hardware/schematic/<보드>/<보드>.kicad_pro 의 board·net_settings 절 동기화 (O-30: 이 파일은 pcb 소유).

다른 절(meta 등)은 그대로 둔다. 사용: python sync_project.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NC = json.loads((ROOT / "hardware/pcb/rules/netclasses.json").read_text(encoding="utf-8"))


def classes():
    out = []
    for c in NC["classes"]:
        out.append({
            "bus_width": 12, "clearance": c["clearance"], "diff_pair_gap": c["diff_pair_gap"],
            "diff_pair_via_gap": c["diff_pair_via_gap"], "diff_pair_width": c["diff_pair_width"],
            "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": c["name"],
            "pcb_color": "rgba(0, 0, 0, 0.000)", "priority": c.get("priority", 2147483647),
            "schematic_color": "rgba(0, 0, 0, 0.000)", "track_width": c["track_width"],
            "via_diameter": c["via_diameter"], "via_drill": c["via_drill"], "wire_width": 6,
        })
    return out


for board in ("carrier", "front"):
    p = ROOT / f"hardware/schematic/{board}/{board}.kicad_pro"
    d = json.loads(p.read_text(encoding="utf-8"))
    ns = d.setdefault("net_settings", {})
    ns["classes"] = classes()
    ns["netclass_patterns"] = NC["patterns"]
    ns.setdefault("meta", {"version": 5})
    ds = d.setdefault("board", {}).setdefault("design_settings", {})
    ds["rules"] = NC["board_rules"]
    ds["track_widths"] = [0.0, 0.15, 0.20, 0.30, 0.60, 1.00, 1.50]
    ds["via_dimensions"] = [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.65, "drill": 0.30}, {"diameter": 0.80, "drill": 0.40}]
    ds["diff_pair_dimensions"] = [{"gap": 0.0, "via_gap": 0.0, "width": 0.0},
                                  {"gap": 0.16, "via_gap": 0.25, "width": 0.15},
                                  {"gap": 0.16, "via_gap": 0.25, "width": 0.20}]
    p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print("synced", p.relative_to(ROOT))
    # 규칙: 공통 openhw-pcbway.kicad_dru + 보드별 extra-<보드>.kicad_dru → <보드>.kicad_dru
    dru = (ROOT / "hardware/pcb/rules/openhw-pcbway.kicad_dru").read_text(encoding="utf-8")
    extra = ROOT / f"hardware/pcb/rules/extra-{board}.kicad_dru"
    if extra.exists():
        dru += extra.read_text(encoding="utf-8")
    (ROOT / f"hardware/schematic/{board}/{board}.kicad_dru").write_text(dru, encoding="utf-8", newline="\n")
    print("rules", f"hardware/schematic/{board}/{board}.kicad_dru", "(+extra)" if extra.exists() else "")
