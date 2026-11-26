"""P-002 캐리어·전면 보드 외형 템플릿 생성기 (KiCad 10, 부품·넷 없음).

입력(이 저장소):
  hardware/pcb/rules/netclasses.json        넷클래스·보드 최소값
  hardware/pcb/rules/openhw-pcbway.kicad_dru 사용자 규칙
좌표: M-001/M-001b(mechanical/stack-reference.md) — 원점 O = 코어 중심, +Y 위, 단위 mm.
KiCad 좌표 변환: kx = 100 + x, ky = 100 - y  (두 보드 모두 F면 = +Z 쪽).
출력: outline/<board>/<board>.kicad_pcb · .kicad_pro · .kicad_dru
사용: python gen_templates.py
"""
import json
import math
import shutil
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES = HERE.parent / "rules"
NS = uuid.UUID("6f1d3c2e-9a51-4c47-8a77-0e5d2b6a0001")
OX, OY = 100.0, 100.0


def K(x, y):
    return f"{OX + x:.4f} {OY - y:.4f}"


def U(key):
    return str(uuid.uuid5(NS, key))


# ---------- 공통 형상 (M-001 §3.2, 단위 mm, O 기준) ----------
HALF = 20.0                      # 40 × 40 (K3)
STACK_HOLES = [(13, 13), (13, -13), (-13, 13), (-17, -17)]   # M1.6 (K6)
HOLE_D = 1.8                     # M1.6 통과 구멍 (ISO 273 중간)
HOLE_KO_D = 4.0                  # 나사 머리·스페이서 구리 금지 지름
ENCL_POS = [(17, 17), (17, -17), (-17, 17)]                 # 외함 고정 자리 (미확정 → 금지 영역만)

LAYERS = """	(layers
		(0 "F.Cu" signal)
		(4 "In1.Cu" power "GND")
		(6 "In2.Cu" power "GND_PWR")
		(2 "B.Cu" signal)
		(9 "F.Adhes" user "F.Adhesive")
		(11 "B.Adhes" user "B.Adhesive")
		(13 "F.Paste" user)
		(15 "B.Paste" user)
		(5 "F.SilkS" user "F.Silkscreen")
		(7 "B.SilkS" user "B.Silkscreen")
		(1 "F.Mask" user)
		(3 "B.Mask" user)
		(17 "Dwgs.User" user "User.Drawings")
		(19 "Cmts.User" user "User.Comments")
		(21 "Eco1.User" user "User.Eco1")
		(23 "Eco2.User" user "User.Eco2")
		(25 "Edge.Cuts" user)
		(27 "Margin" user)
		(31 "F.CrtYd" user "F.Courtyard")
		(29 "B.CrtYd" user "B.Courtyard")
		(35 "F.Fab" user)
		(33 "B.Fab" user)
		(39 "User.1" user "OH.Mech")
		(41 "User.2" user "OH.Height")
	)
"""


def setup(rules):
    m = rules["solder_mask_expansion"]
    web = rules["solder_mask_min_web"]
    return f"""	(setup
		(stackup
			(layer "F.SilkS" (type "Top Silk Screen"))
			(layer "F.Paste" (type "Top Solder Paste"))
			(layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.015) (material "LPI") (epsilon_r 3.5) (loss_tangent 0))
			(layer "F.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 1" (type "prepreg") (thickness 0.1855) (material "7628 RC46%") (epsilon_r 4.74) (loss_tangent 0.02))
			(layer "In1.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 2" (type "core") (thickness 1.03) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
			(layer "In2.Cu" (type "copper") (thickness 0.035))
			(layer "dielectric 3" (type "prepreg") (thickness 0.1855) (material "7628 RC46%") (epsilon_r 4.74) (loss_tangent 0.02))
			(layer "B.Cu" (type "copper") (thickness 0.035))
			(layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.015) (material "LPI") (epsilon_r 3.5) (loss_tangent 0))
			(layer "B.Paste" (type "Bottom Solder Paste"))
			(layer "B.SilkS" (type "Bottom Silk Screen"))
			(copper_finish "ENIG")
			(dielectric_constraints no)
		)
		(pad_to_mask_clearance {m})
		(solder_mask_min_width {web})
		(allow_soldermask_bridges_in_footprints no)
		(tenting front back)
		(aux_axis_origin {OX} {OY})
		(grid_origin {OX} {OY})
	)
"""


def line(key, a, b, layer, w=0.1):
    return f'\t(gr_line (start {K(*a)}) (end {K(*b)}) (stroke (width {w}) (type default)) (layer "{layer}") (uuid "{U(key)}"))\n'


def rect(key, x0, y0, x1, y1, layer, w=0.1):
    # 네 변을 선으로 그린다 (KiCad Y 반전 때문에 gr_rect start/end 순서 혼동을 피함)
    p = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return "".join(line(f"{key}/{i}", p[i], p[(i + 1) % 4], layer, w) for i in range(4))


def circle(key, c, d, layer, w=0.1):
    return (f'\t(gr_circle (center {K(*c)}) (end {K(c[0] + d / 2, c[1])}) (stroke (width {w}) (type default)) '
            f'(fill no) (layer "{layer}") (uuid "{U(key)}"))\n')


def text(key, s, at, layer, h=1.0):
    return (f'\t(gr_text "{s}" (at {K(*at)} 0) (layer "{layer}") (uuid "{U(key)}")\n'
            f'\t\t(effects (font (size {h} {h}) (thickness 0.15)) (justify left)))\n')


FP_LIB = "OpenHW_Mech"
FP_NAME = "MountingHole_M1.6_NPTH"


def fp_items(ref, key=None):
    """풋프린트 본문. key 가 있으면 보드용(uuid 포함), 없으면 라이브러리 .kicad_mod 용."""
    u = (lambda k: f' (uuid "{U(key + k)}")') if key else (lambda k: "")
    r = HOLE_KO_D / 2
    return f"""		(property "Reference" "{ref}" (at 0 -2.6 0) (layer "F.Fab"){u('/ref')}
			(effects (font (size 1 1) (thickness 0.15))))
		(property "Value" "M1.6" (at 0 2.6 0) (layer "F.Fab"){u('/val')}
			(effects (font (size 1 1) (thickness 0.15))))
		(attr exclude_from_pos_files exclude_from_bom)
		(fp_circle (center 0 0) (end {r} 0) (stroke (width 0.05) (type solid)) (fill no) (layer "F.CrtYd"){u('/cy')})
		(fp_circle (center 0 0) (end {r} 0) (stroke (width 0.05) (type solid)) (fill no) (layer "B.CrtYd"){u('/cyb')})
		(pad "" np_thru_hole circle (at 0 0) (size {HOLE_D} {HOLE_D}) (drill {HOLE_D}) (layers "*.Cu" "*.Mask"){u('/pad')})
"""


def hole(key, ref, c):
    return (f'\t(footprint "{FP_LIB}:{FP_NAME}"\n\t\t(layer "F.Cu")\n\t\t(uuid "{U(key)}")\n\t\t(at {K(*c)})\n'
            + fp_items(ref, key) + "\t)\n")


def write_lib():
    d = HERE / f"{FP_LIB}.pretty"
    d.mkdir(exist_ok=True)
    body = (f'(footprint "{FP_NAME}"\n\t(version 20250513)\n\t(generator "openhw_gen_templates")\n\t(layer "F.Cu")\n'
            f'\t(descr "M1.6 stack screw clearance hole {HOLE_D}mm NPTH, copper keepout {HOLE_KO_D}mm (P-002)")\n'
            + fp_items("REF**").replace("\t\t", "\t") + "\t(embedded_fonts no)\n)\n")
    (d / f"{FP_NAME}.kicad_mod").write_text(body, encoding="utf-8", newline="\n")


FP_TABLE = f"""(fp_lib_table
	(version 7)
	(lib (name "{FP_LIB}") (type "KiCad") (uri "${{KIPRJMOD}}/../{FP_LIB}.pretty") (options "") (descr "OpenHW mechanical (P-002)"))
)
"""


def keepout(key, name, c, d, n=24):
    pts = " ".join(f"(xy {K(c[0] + d / 2 * math.cos(2 * math.pi * i / n), c[1] + d / 2 * math.sin(2 * math.pi * i / n))})"
                   for i in range(n))
    return f"""	(zone (net 0) (net_name "") (layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu") (uuid "{U(key)}") (name "{name}") (hatch edge 0.5)
		(connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)
		(keepout (tracks not_allowed) (vias not_allowed) (pads allowed) (copperpour not_allowed) (footprints allowed))
		(placement (enabled no) (sheetname ""))
		(fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
		(polygon (pts {pts}))
	)
"""


def common(board, rules):
    s = rect(f"{board}/edge", -HALF, -HALF, HALF, HALF, "Edge.Cuts", 0.1)
    for i, c in enumerate(STACK_HOLES, 1):
        s += hole(f"{board}/H{i}", f"H{i}", c)
        s += keepout(f"{board}/KO_H{i}", f"KO_H{i}", c, HOLE_KO_D)
    for i, c in enumerate(ENCL_POS, 1):
        s += keepout(f"{board}/KO_E{i}", f"KO_ENCL{i}", c, HOLE_KO_D)
        s += circle(f"{board}/E{i}", c, HOLE_KO_D, "User.1")
    s += rect(f"{board}/core", -15, -15, 15, 15, "User.1")
    s += text(f"{board}/t_core", "CORE 30x30", (-14.5, -14.0), "User.1")
    s += rect(f"{board}/ffc", 15, -15, 20, 15, "User.1")
    s += text(f"{board}/t_ffc", "FFC", (15.5, 0), "User.1")
    s += text(f"{board}/t_o", "O(0,0)", (0.5, -1.5), "User.1", 0.8)
    s += line(f"{board}/ox", (-1, 0), (1, 0), "User.1", 0.05) + line(f"{board}/oy", (0, -1), (0, 1), "User.1", 0.05)
    return s


def carrier():
    s = ""
    # 코어 J2(아랫면 소켓)와 짝인 플러그 A — 캐리어 윗면, 몸체 bbox (M-001 §2.1)
    s += rect("c/j2", 9.20, -8.85, 14.40, 8.85, "User.1")
    s += text("c/t_j2", "J2 MATE A", (9.4, 9.6), "User.1")
    # 높이 제한: 코어 아래 캐리어 윗면 부품 ≤6.2 (btb_h 8.0, M-001b)
    s += rect("c/hmax", -15, -15, 15, 15, "User.2")
    s += text("c/t_hmax", "TOP H<=6.2 (btb 8.0)", (-14.5, 13.5), "User.2")
    return s


def front():
    s = ""
    # 코어 J1(윗면 플러그)과 짝인 소켓 B — 전면 아랫면, 몸체 bbox
    s += rect("f/j1", -8.85, 9.19, 8.85, 14.41, "User.1")
    s += text("f/t_j1", "J1 MATE B (BOTTOM)", (-8.6, 15.5), "User.1")
    # 방열판 J1 창 20x8 (0,+12) — 창 밖 아랫면 부품 ≤5.2
    s += rect("f/win", -10, 8, 10, 16, "User.2")
    s += rect("f/hmax", -18, -18, 18, 18, "User.2")
    s += text("f/t_hmax", "BOTTOM H<=5.2 outside J1 window", (-17.5, -17.0), "User.2")
    # 광축 위 부품 자리값 (전면 윗면): DF30 7x3, 모듈 12x12, CLA216 16x16, 홀더 나사 (±10,0)
    s += rect("f/df30", -3.5, -1.5, 3.5, 1.5, "User.1")
    s += rect("f/smod", -6, -6, 6, 6, "User.1")
    s += rect("f/holder", -8, -8, 8, 8, "User.1")
    s += text("f/t_opt", "DF30/BXF4677/CLA216 (placeholder)", (-7.8, -9.2), "User.1", 0.8)
    for i, x in enumerate((10, -10)):
        s += circle(f"f/hs{i}", (x, 0), 1.8, "User.1")
    # IR LED 후보 영역 (윗면, 높이 ≤2.5)
    s += rect("f/irn", -10.5, 12, 10.5, 19, "User.2")
    s += rect("f/irs", -10.5, -19, 10.5, -12, "User.2")
    s += text("f/t_irn", "IR N TOP H<=2.5", (-10.3, 18.0), "User.2", 0.8)
    s += text("f/t_irs", "IR S TOP H<=2.5", (-10.3, -13.0), "User.2", 0.8)
    # 조도센서 후보 (−17, 0)
    s += circle("f/ltr", (-17, 0), 2.0, "User.1")
    s += text("f/t_ltr", "LTR", (-18.5, 1.8), "User.1", 0.8)
    return s


def pcb(board, rules, body):
    return ("(kicad_pcb\n\t(version 20250513)\n\t(generator \"openhw_gen_templates\")\n\t(generator_version \"10.0\")\n"
            "\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper \"A4\")\n"
            f"\t(title_block\n\t\t(title \"OpenHW {board} outline template\")\n\t\t(date \"2026-11-26\")\n\t\t(rev \"P-002\")\n\t)\n"
            + LAYERS + setup(rules) + "\t(net 0 \"\")\n" + common(board, rules) + body + ")\n")


def project(board, nc):
    classes = []
    for c in nc["classes"]:
        d = {
            "bus_width": 12, "clearance": c["clearance"], "diff_pair_gap": c["diff_pair_gap"],
            "diff_pair_via_gap": c["diff_pair_via_gap"], "diff_pair_width": c["diff_pair_width"],
            "line_style": 0, "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": c["name"],
            "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
            "track_width": c["track_width"], "via_diameter": c["via_diameter"], "via_drill": c["via_drill"],
            "wire_width": 6,
        }
        d["priority"] = c.get("priority", 2147483647)
        classes.append(d)
    return {
        "board": {
            "design_settings": {
                "rules": nc["board_rules"],
                "track_widths": [0.0, 0.15, 0.20, 0.30, 0.60, 1.00, 1.50],
                "via_dimensions": [{"diameter": 0.0, "drill": 0.0}, {"diameter": 0.65, "drill": 0.30},
                                   {"diameter": 0.80, "drill": 0.40}],
                "diff_pair_dimensions": [{"gap": 0.0, "via_gap": 0.0, "width": 0.0},
                                         {"gap": 0.16, "via_gap": 0.25, "width": 0.15},
                                         {"gap": 0.16, "via_gap": 0.25, "width": 0.20}],
            }
        },
        "meta": {"filename": f"{board}.kicad_pro", "version": 3},
        "net_settings": {
            "classes": classes,
            "meta": {"version": 5},
            "net_colors": None,
            "netclass_assignments": None,
            "netclass_patterns": nc["patterns"],
        },
    }


def main():
    nc = json.loads((RULES / "netclasses.json").read_text(encoding="utf-8"))
    write_lib()
    for board, body in (("carrier", carrier()), ("front", front())):
        d = HERE / board
        d.mkdir(exist_ok=True)
        (d / f"{board}.kicad_pcb").write_text(pcb(board, nc, body), encoding="utf-8", newline="\n")
        (d / f"{board}.kicad_pro").write_text(json.dumps(project(board, nc), indent=2, ensure_ascii=False) + "\n",
                                              encoding="utf-8", newline="\n")
        shutil.copyfile(RULES / "openhw-pcbway.kicad_dru", d / f"{board}.kicad_dru")
        (d / "fp-lib-table").write_text(FP_TABLE, encoding="utf-8", newline="\n")
        print("wrote", d)


if __name__ == "__main__":
    main()
