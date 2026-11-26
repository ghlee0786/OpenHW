"""P-003 회로도 → PCB 갱신 + 배치 (KiCad 10 pcbnew, 화면 없음).

- 넷리스트(hardware/schematic/<보드>/<보드>.net)의 부품을 라이브러리에서 읽어 넣는다.
  참조·값·회로도 경로(KIID path = 시트 tstamps + 심벌 tstamps)·DNP·넷을 넷리스트대로 붙인다.
  → GUI 「PCB 업데이트」와 같은 결과를 목표로 하고, kicad-cli DRC --schematic-parity 로 확인한다.
- 배치: layout-plan.md §3 좌표. 고정 부품은 지정 좌표, 나머지는 기준점 둘레를 0.25mm 나선으로 찾아
  courtyard 겹침(같은 면 +0.2) · 구멍 금지 원 · 부품 금지 영역 · 반대 면 관통 핀 · 외곽 안쪽을 모두 만족하는 첫 자리.
- 좌표: M-001 O 기준(+Y 위). KiCad = (100 + x, 100 − y).
- 배선은 하지 않는다(이 스크립트는 넷·배치까지).

사용: <KiCad>/bin/python.exe build_boards.py [carrier|front ...]
출력: hardware/schematic/<보드>/<보드>.kicad_pcb (P-002 템플릿 위에 다시 만든다: 템플릿의 외곽·구멍·적층은 유지)
"""
import math
import os
import re
import sys
from pathlib import Path

import pcbnew

ROOT = Path(__file__).resolve().parents[3]
STD = Path(r"C:\Users\gh\AppData\Local\Programs\KiCad\10.0\share\kicad\footprints")
LIBS = {"openhw": ROOT / "hardware/libraries/openhw.pretty", "OpenHW_Mech": ROOT / "hardware/pcb/lib/OpenHW_Mech.pretty"}
TEMPLATE = Path(r"C:\workspace_python\OpenHW\.harness-worktrees\t-20261126-163344-acdf\hardware\pcb\outline")  # P-002 022c364·ea8d1f6
MM = pcbnew.FromMM
HOLES = [(13, 13), (13, -13), (-13, 13), (-17, -17)]
HOLE_R = 2.0


def K(x, y):
    return pcbnew.VECTOR2I(MM(100 + x), MM(100 - y))


def O(v):
    return (pcbnew.ToMM(v.x) - 100, 100 - pcbnew.ToMM(v.y))


# ---------------- 넷리스트 (작은 s-식 파서) ----------------
def sexp(text):
    tok = re.findall(r'"(?:\\.|[^"\\])*"|\(|\)|[^\s()"]+', text)
    stack, cur = [], []
    for t in tok:
        if t == "(":
            stack.append(cur)
            cur = []
        elif t == ")":
            done = cur
            cur = stack.pop()
            cur.append(done)
        else:
            cur.append(t[1:-1].replace('\\"', '"').replace("\\\\", "\\") if t.startswith('"') else t)
    return cur[0]


def find(node, key):
    return [c for c in node if isinstance(c, list) and c and c[0] == key]


def one(node, key, default=None):
    r = find(node, key)
    return r[0] if r else default


def netlist(board):
    root = sexp((ROOT / f"hardware/schematic/{board}/{board}.net").read_text(encoding="utf-8"))
    comps = []
    for c in find(one(root, "components"), "comp"):
        props = {one(p, "name")[1]: (one(p, "value") or [None, ""])[1] for p in find(c, "property")}
        fields = {}
        for f in find(one(c, "fields") or [], "field"):
            name = one(f, "name")[1]
            if name != "Footprint":  # Datasheet·Description도 회로도 값(빈 값 포함)으로 맞춘다 — 회로도 일치 검사
                fields[name] = f[2] if len(f) > 2 and isinstance(f[2], str) else ""
        sp = one(c, "sheetpath")
        comps.append({
            "ref": one(c, "ref")[1], "value": one(c, "value")[1], "fp": one(c, "footprint")[1],
            "sheet": one(sp, "tstamps")[1], "uuid": one(c, "tstamps")[1], "dnp": "dnp" in props,
            "no_bom": "exclude_from_bom" in props, "fields": fields,
        })
    nets = []
    for n in find(one(root, "nets"), "net"):
        nets.append((one(n, "name")[1], [(one(nd, "ref")[1], one(nd, "pin")[1]) for nd in find(n, "node")]))
    return comps, nets


# ---------------- 배치 계획 (layout-plan.md §3) ----------------
# 고정: ref → (면, 회전°, (x, y) 풋프린트 원점) 또는 ('crt', 면, 입구, (x0, y0, x1, y1)) courtyard 목표
FIXED = {
    "carrier": {
        "J1": ("F", -90.0, (11.8, 0.0)),
        "J5": ("crt", "B", "-Y", (-12.0, -34.0, 7.09, -11.61)),
        "J2": ("crt", "B", "-Y", (8.41, -34.0, 20.0, -17.91)),
        "J4": ("crt", "B", "+Y", (-7.9, 2.4, 7.9, 20.19)),
        "J3": ("crt", "B", "-X", (-20.0, -5.37, -10.49, 5.37)),
        # GH 6P, M-002 K20 (−19.0…−13.5, −30.5…−19.0). 실제 courtyard 6.49×12.05가 구멍 (−17,−17) 금지 원에 0.28 걸려 −Y로 0.3 내림
        "J7": ("crt", "F", "-X", (-19.0, -30.8, -13.5, -19.3)),
    },
    "front": {
        "J1": ("B", 180.0, (0.0, 11.8)),
        "MH1": ("F", 0.0, (0.0, 0.0)),
        "J3": ("F", 0.0, (0.0, -12.0)),
        "D_IR_A1": ("F", 0.0, (-6.0, 16.0)),
        "D_IR_A2": ("F", 0.0, (6.0, 16.0)),
        # B1/B2 (DNP): M-001c (±9, −16.5)는 courtyard 6.09가 구멍 (13,−13) 금지 원과 겹쳐(거리 1.05 < 2.0) x를 ±7.5로 (대칭 유지)
        "D_IR_B1": ("F", 0.0, (-7.5, -16.5)),
        "D_IR_B2": ("F", 0.0, (7.5, -16.5)),
        # GH 6P, M-002 K20 (−19.0…−13.5, −15.0…−3.5). 구멍 (−17,−17) 금지 원에 0.28 걸려 +Y로 0.3 올림
        "J4": ("crt", "B", "-X", (-19.0, -14.7, -13.5, -3.2)),
        # J_ICR (M-001d x +15…+19, y ±3): GH 2P 자리 보류 — PicoBlade 53261-0271로 바뀔 예정(O-34, C-005), G2 실물 확인 전 확정 금지
        "J2": ("crt", "F", "-X", (13.6, -3.25, 19.95, 3.25)),
    },
}

# 자유 배치: ref 접두·정확 이름 → (면, 기준점, 입구(커넥터면)). 위에서부터 먼저 놓는다.
FREE = {
    "carrier": [
        # 보드 간 GH 6P (−X, 입구 −X), 디버그 UART(뒷면 −X), 버튼·표시 LED(뒷면 +X)
        ("J6", "B", (-16.5, -11.0), "-X"),
        ("SW1", "B", (14.5, -6.0), None), ("SW2", "B", (14.5, 4.0), None),
        ("D4", "B", (14.5, -10.5), None), ("D5", "B", (14.5, 8.0), None),
        ("D3", "B", (17.5, -14.5), None), ("D6", "B", (17.5, 9.0), None),
        # 전원 입력 사슬 (윗면, DC 잭 위 연장부) → eFuse → 벅 → J1 5V 핀(13.8, 0.25…−1.25)
        ("F1", "F", (16.0, -31.5), None), ("Q1", "F", (14.0, -26.0), None), ("D1", "F", (9.5, -31.5), None),
        ("D2", "F", (4.0, -31.0), None), ("U2", "F", (6.0, -24.5), None), ("C1", "F", (-4.0, -30.0), None),
        ("C2", "F", (-0.5, -24.0), None), ("C3", "F", (-12.5, -31.5), None), ("C4", "F", (-12.5, -28.0), None),
        ("U1", "F", (6.0, -15.0), None), ("L1", "F", (12.0, -16.5), None), ("C7", "F", (17.5, -9.0), None),
        ("C8", "F", (17.5, -4.5), None), ("C20", "F", (17.5, -13.0), None), ("C19", "F", (3.0, -12.5), None),
        ("D7", "F", (17.5, 2.5), None),  # C-004: 5V_SYS TVS — J1 5V 핀(13.8, 0.25…−1.25) 옆
        ("C11", "F", (-1.0, -15.5), None),
        # USB (J1 1·3번 → 뒷면 USB-C −X): ESD·CC 저항은 USB-C 다리 안쪽 윗면
        ("U3", "F", (-8.5, 2.0), None),
        # microSD ESD·전원 스위치 (J4 뒷면 +Y 가운데)
        ("U4", "F", (-2.0, 10.0), None), ("U5", "F", (2.5, 10.0), None), ("Q2", "F", (-14.0, -6.0), None),
        ("Q3", "F", (-11.0, -9.0), None), ("Q4", "F", (4.0, 6.0), None),
        ("C17", "B", (-14.0, -26.0), None), ("R18", "B", (-14.0, -22.0), None),
        ("C", "F", (2.0, -5.0), None), ("R", "F", (0.0, 0.0), None), ("TP", "B", (12.0, 12.0), None),
    ],
    "front": [
        ("J2", "F", (16.8, 0.0), "-X"),
        ("U3", "F", (-17.0, 0.0), None), ("Q4", "F", (-17.0, 4.5), None),
        # A 스트링 드라이버: 뒷면 −X 위쪽 / B 스트링: 뒷면 +X 아래쪽
        ("U4", "B", (-15.5, 2.0), None), ("L1", "B", (-15.5, 8.5), None), ("D1", "B", (-15.5, -3.0), None),
        ("R13", "B", (-10.0, 3.0), None), ("C14", "B", (-10.0, 6.0), None), ("C15", "B", (-11.0, 0.0), None),
        ("U5", "B", (15.5, -9.0), None), ("L2", "B", (15.5, -15.5), None), ("D2", "B", (10.0, -18.0), None),
        ("R14", "B", (10.0, -9.0), None), ("C16", "B", (10.0, -12.0), None), ("C17", "B", (11.0, -6.5), None),
        ("U2", "B", (15.5, 0.0), None), ("U1", "B", (-6.0, 4.0), None), ("X1", "B", (3.0, -12.0), None),
        ("Q6", "B", (-4.0, -12.0), None), ("D3", "B", (-7.0, -11.0), None),  # C-004: CAM_1V8 스위치·RESET 쇼트키 (DF30 아래)
        ("R8", "B", (5.5, -12.0), None), ("Q1", "B", (-4.0, -4.0), None), ("Q2", "B", (4.0, -4.0), None),
        ("Q3", "B", (-8.0, -8.0), None), ("Q5", "B", (8.0, -8.0), None),
        ("C", "B", (0.0, -7.0), None), ("R", "B", (0.0, 0.0), None), ("TP", "B", (0.0, -18.0), None),
    ],
}

# 부품 금지 영역: (면, (x0, y0, x1, y1), 허용 ref 목록)
ZONES = {
    "carrier": [],
    "front": [
        ("F", (-12.2, -7.95, 12.2, 7.95), {"MH1"}),            # 스페이서 프레임 (M-001d §3.6)
        ("F", (-3.8, -14.4, 3.8, -9.6), {"J3", "MH1"}),        # DF30 자리
        ("B", (-10.0, 8.0, 10.0, 16.0), {"J1"}),               # 방열판 J1 창
        ("B", (-9.5, 16.5, 9.5, 19.5), set()),                 # K21 TP_A 노출 구리 패드 (M-002 3f7ceee §8)
        ("B", (-12.0, -19.5, -6.0, -13.5), set()),             # K21 TP_B1
        ("B", (6.0, -19.5, 12.0, -13.5), set()),               # K21 TP_B2
    ],
}
# 외함 고정 자리(구멍 없이 금지 원만, 지름 미정) — 캐리어는 (+17,−17)을 뺀다 (M-002 K19)
ENCL = {"carrier": [(17, 17), (-17, 17)], "front": [(17, 17), (17, -17), (-17, 17)]}
OUTLINE = {"carrier": (-20.0, -34.0, 20.0, 20.0), "front": (-20.0, -20.0, 20.0, 20.0)}


def load_fp(fpid):
    lib, name = fpid.split(":", 1)
    path = LIBS.get(lib, STD / f"{lib}.pretty")
    fp = pcbnew.FootprintLoad(str(path), name)
    if fp is None:
        raise SystemExit(f"풋프린트 없음: {fpid}")
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def place(fp, side, rot, pos):
    fp.SetPosition(K(*pos))
    if side == "B" and not fp.IsFlipped():
        fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
    fp.SetOrientationDegrees(rot)


def crt_box(fp):
    layer = pcbnew.B_CrtYd if fp.IsFlipped() else pcbnew.F_CrtYd
    sh = fp.GetCourtyard(layer)
    bb = sh.BBox() if sh.OutlineCount() else fp.GetBoundingBox(False)
    (x0, y1), (x1, y0) = O(bb.GetOrigin()), O(bb.GetEnd())
    return (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1))


def opening(fp):
    """입구 방향: 패드 무게중심 → courtyard 중심 방향(O 좌표)."""
    sig = [O(p.GetPosition()) for p in fp.Pads() if p.GetNumber().isdigit()]
    mp = [O(p.GetPosition()) for p in fp.Pads() if p.GetNumber() == "MP"]
    if mp and fp.GetFPID().GetUniStringLibItemName().startswith("JST_"):
        # JST 측면 진입형: 신호 패드(뒤) → 고정 탭 MP(입구 쪽)
        (ax, ay), (bx, by) = [(sum(q[0] for q in s) / len(s), sum(q[1] for q in s) / len(s)) for s in (sig, mp)]
        dx, dy = bx - ax, by - ay
        return ("+X" if dx > 0 else "-X") if abs(dx) > abs(dy) else ("+Y" if dy > 0 else "-Y")
    b = crt_box(fp)
    cx, cy = (b[0] + b[2]) / 2, (b[1] + b[3]) / 2
    ps = [O(p.GetPosition()) for p in fp.Pads()]
    px, py = sum(p[0] for p in ps) / len(ps), sum(p[1] for p in ps) / len(ps)
    dx, dy = cx - px, cy - py
    return ("+X" if dx > 0 else "-X") if abs(dx) > abs(dy) else ("+Y" if dy > 0 else "-Y")


def tht_boxes(fp):
    out = []
    for p in fp.Pads():
        if p.GetAttribute() in (pcbnew.PAD_ATTRIB_PTH, pcbnew.PAD_ATTRIB_NPTH):
            bb = p.GetBoundingBox()
            (x0, y1), (x1, y0) = O(bb.GetOrigin()), O(bb.GetEnd())
            out.append((min(x0, x1) - 0.3, min(y0, y1) - 0.3, max(x0, x1) + 0.3, max(y0, y1) + 0.3))
    return out


def ov(a, b, g=0.0):
    return a[0] < b[2] + g and b[0] < a[2] + g and a[1] < b[3] + g and b[1] < a[3] + g


def hits_hole(r, extra=()):
    for hx, hy in list(HOLES) + list(extra):
        nx, ny = min(max(hx, r[0]), r[2]), min(max(hy, r[1]), r[3])
        if (nx - hx) ** 2 + (ny - hy) ** 2 < HOLE_R ** 2:
            return True
    return False


class Placer:
    def __init__(self, board_name):
        self.name = board_name
        self.box = OUTLINE[board_name]
        self.placed = []  # (ref, side, crt, tht_boxes)

    def legal(self, ref, fp, side, edge_ok):
        c = crt_box(fp)
        inset = -0.6 if edge_ok else 0.3
        if c[0] < self.box[0] + inset or c[1] < self.box[1] + inset or c[2] > self.box[2] - inset or c[3] > self.box[3] - inset:
            return False
        if hits_hole(c, ENCL[self.name]):
            return False
        if not self.pads_off_edge(fp):
            return False
        for zs, zr, allow in ZONES[self.name]:
            if zs == side and ref not in allow and ov(c, zr):
                return False
        mine = tht_boxes(fp)
        for r2, s2, c2, t2 in self.placed:
            if s2 == side and ov(c, c2, 0.2):
                return False
            if s2 != side and any(ov(c, t) for t in t2):
                return False
            if mine and s2 != side and any(ov(m, c2) for m in mine):
                return False
        return True

    def commit(self, ref, fp, side):
        self.placed.append((ref, side, crt_box(fp), tht_boxes(fp)))
        # 반대 면에도 courtyard가 있으면(예: MH1 뒷면 나사 머리 23.1×3.3) 그 면에도 등록
        other = pcbnew.F_CrtYd if fp.IsFlipped() else pcbnew.B_CrtYd
        sh = fp.GetCourtyard(other)
        if sh.OutlineCount():
            bb = sh.BBox()
            (x0, y1), (x1, y0) = O(bb.GetOrigin()), O(bb.GetEnd())
            self.placed.append((ref, "F" if side == "B" else "B", (min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), []))

    def pads_off_edge(self, fp, gap=0.40):
        for p in fp.Pads():
            if p.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                continue
            bb = p.GetBoundingBox()
            (x0, y1), (x1, y0) = O(bb.GetOrigin()), O(bb.GetEnd())
            if min(x0, x1) < self.box[0] + gap or max(x0, x1) > self.box[2] - gap or \
                    min(y0, y1) < self.box[1] + gap or max(y0, y1) > self.box[3] - gap:
                return False
        return True

    def free(self, ref, fp, side, anchor, want_open=None, rmax=30.0):
        rots = (0.0, 90.0, 180.0, -90.0)
        r = 0.0
        while r <= rmax:
            n = max(1, int(2 * math.pi * r / 0.25)) if r else 1
            for i in range(n):
                a = 2 * math.pi * i / n
                pos = (anchor[0] + r * math.cos(a), anchor[1] + r * math.sin(a))
                for rot in rots:
                    place(fp, side, rot, pos)
                    if want_open and opening(fp) != want_open:
                        continue
                    if self.legal(ref, fp, side, edge_ok=bool(want_open)):
                        self.commit(ref, fp, side)
                        return True
            r += 0.25
        return False

    def crt_target(self, ref, fp, side, want_open, target):
        for rot in (0.0, 90.0, 180.0, -90.0):
            place(fp, side, rot, (0, 0))
            if opening(fp) != want_open:
                continue
            c = crt_box(fp)
            if abs((c[2] - c[0]) - (target[2] - target[0])) > 1.2 or abs((c[3] - c[1]) - (target[3] - target[1])) > 1.2:
                continue
            # 입구 쪽 변을 목표 변에 맞추고, 다른 축은 가운데를 맞춘다
            tx = target[0] - c[0] if want_open == "-X" else target[2] - c[2] if want_open == "+X" else \
                (target[0] + target[2]) / 2 - (c[0] + c[2]) / 2
            ty = target[1] - c[1] if want_open == "-Y" else target[3] - c[3] if want_open == "+Y" else \
                (target[1] + target[3]) / 2 - (c[1] + c[3]) / 2
            place(fp, side, rot, (tx, ty))
            got = crt_box(fp)
            print(f"  {ref}: courtyard 목표 {tuple(round(v, 2) for v in target)} → 실제 {tuple(round(v, 2) for v in got)}")
            self.commit(ref, fp, side)
            return True
        raise SystemExit(f"{ref}: 입구 {want_open}·크기를 맞추는 회전 없음")


def build(board_name):
    comps, nets = netlist(board_name)
    out = ROOT / f"hardware/schematic/{board_name}/{board_name}.kicad_pcb"
    board = pcbnew.LoadBoard(str(TEMPLATE / board_name / f"{board_name}.kicad_pcb"))
    # 템플릿 장착 구멍은 회로도에 없는 보드 전용 부품 (도형을 지우기 전에 처리해야 swig 형 변환이 깨지지 않는다)
    for fp in list(board.GetFootprints()):
        fp.SetBoardOnly(True)
    # 외함 고정 금지 원: 템플릿 KO_ENCL 중 이 보드에 없는 자리는 지운다 (캐리어 (+17,−17), M-002 K19)
    for z in list(board.Zones()):
        if z.GetZoneName().startswith("KO_ENCL"):
            c = O(z.GetBoundingBox().GetCenter())
            if not any(abs(c[0] - ex) < 0.5 and abs(c[1] - ey) < 0.5 for ex, ey in ENCL[board_name]):
                board.Delete(z)

    # 템플릿 표시(User.1/User.2)와 외곽은 다시 그린다 (캐리어 외곽은 layout-plan 1안 40×54, M-002 결과 대기)
    for d in list(board.GetDrawings()):
        if d.GetLayer() in (pcbnew.User_1, pcbnew.User_2) or d.GetLayer() == pcbnew.Edge_Cuts:
            board.Delete(d)  # Remove 는 swig 형 변환을 깨뜨린다(P-003 시험)
    x0, y0, x1, y1 = OUTLINE[board_name]
    pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    for i in range(4):
        s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(K(*pts[i]))
        s.SetEnd(K(*pts[(i + 1) % 4]))
        s.SetLayer(pcbnew.Edge_Cuts)
        s.SetWidth(MM(0.1))
        board.Add(s)
    for zs, (a, b, c, d), _ in ZONES[board_name]:
        for p, q in (((a, b), (c, b)), ((c, b), (c, d)), ((c, d), (a, d)), ((a, d), (a, b))):
            s = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
            s.SetStart(K(*p))
            s.SetEnd(K(*q))
            s.SetLayer(pcbnew.User_2)
            s.SetWidth(MM(0.1))
            board.Add(s)

    netinfo = {}
    for name, _ in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netinfo[name] = ni
    pinnet = {(r, p): n for n, nodes in nets for r, p in nodes}

    pl = Placer(board_name)
    fps = {}
    for c in comps:
        fp = load_fp(c["fp"])
        fp.SetReference(c["ref"])
        fp.SetValue(c["value"])
        path = pcbnew.KIID_PATH(c["sheet"].rstrip("/") + "/" + c["uuid"])
        fp.SetPath(path)
        fp.SetDNP(c["dnp"])
        fp.SetExcludedFromBOM(c["no_bom"])
        for k, v in c["fields"].items():
            fp.SetField(k, v)
            f = fp.GetField(k)
            if f:
                f.SetVisible(False)
                f.SetLayer(pcbnew.F_Fab)
        if "DF30" in c["fp"]:
            # 0.4mm 피치: 마스크 확장 0.025 → 패드 사이 웹 0.12 ≥ PCBWay 댐 4mil(0.10) (P-001 §2 #6)
            fp.SetLocalSolderMaskMargin(MM(0.025))
        board.Add(fp)
        for pad in fp.Pads():
            n = pinnet.get((c["ref"], pad.GetNumber()))
            if n:
                pad.SetNet(netinfo[n])
        fps[c["ref"]] = fp

    missing = []
    for ref, spec in FIXED[board_name].items():
        fp = fps[ref]
        if spec[0] == "crt":
            pl.crt_target(ref, fp, spec[1], spec[2], spec[3])
        else:
            place(fp, spec[0], spec[1], spec[2])
            pl.commit(ref, fp, spec[0])
    done = set(FIXED[board_name])

    def put(ref, side, anchor, want=None):
        if not pl.free(ref, fps[ref], side, anchor, want):
            missing.append(ref)
            place(fps[ref], side, 0.0, (40.0 + len(missing) * 3, 0.0))  # 보드 밖에 둔다 → DRC가 잡는다
        done.add(ref)

    # 1) 이름을 정한 부품(IC·커넥터·전력 부품)은 계획 좌표 둘레에
    prefix_rules = {}
    for key, side, anchor, want in FREE[board_name]:
        if key in fps:
            if key not in done:
                put(key, side, anchor, want)
        else:
            prefix_rules[key] = (side, anchor)

    # 2) 나머지(C·R·D·Q·TP…)는 연결 기반: 이미 놓인 부품과 공유하는 넷 중 패드가 가장 적은(가장 구체적인) 넷의
    #    놓인 패드 중심을 기준점으로, 그 패드 주인의 면에 둔다. 테스트점(TP)은 접근이 쉬운 계획 면(뒷면)에 둔다.
    nets_of = {r: {p.GetNetname() for p in fps[r].Pads() if p.GetNetname()} for r in fps}
    skip = {"/GND", "GND"}

    def anchor_for(ref):
        best = None
        for n in nets_of[ref] - skip:
            placed = [(O(p.GetPosition()), fps[r2].IsFlipped()) for r2 in done if r2 in fps and n in nets_of[r2]
                      for p in fps[r2].Pads() if p.GetNetname() == n]
            if placed and (best is None or len(placed) < len(best)):
                best = placed
        if not best:
            return None
        x = sum(p[0][0] for p in best) / len(best)
        y = sum(p[0][1] for p in best) / len(best)
        side = "B" if sum(1 for p in best if p[1]) * 2 > len(best) else "F"
        return (x, y), side, len(best)

    todo = [r for r in fps if r not in done]
    while todo:
        scored = [(anchor_for(r), r) for r in todo]
        with_a = [(a[2], r, a) for a, r in scored if a]
        if not with_a:
            break
        _, ref, (pos, side, _) = min(with_a)
        key = re.match(r"[A-Z_]+", ref).group(0)
        if key == "TP" and key in prefix_rules:
            side = prefix_rules[key][0]
        put(ref, side, pos)
        todo.remove(ref)
    for ref in todo:  # 놓인 부품과 연결이 없는 부품은 접두 규칙 기준점으로
        key = re.match(r"[A-Z_]+", ref).group(0)
        if key in prefix_rules:
            put(ref, *prefix_rules[key])
    # 참조 지정자는 조립도(Fab)로 — 40×40·40×54 밀집 배치에서 실크 글자 겹침을 없앤다. 극성·1번 핀 실크 표시는 풋프린트 그대로
    for fp in fps.values():
        fp.Reference().SetLayer(pcbnew.B_Fab if fp.IsFlipped() else pcbnew.F_Fab)
    left = [r for r in fps if r not in done]
    for i, ref in enumerate(left):
        place(fps[ref], "F", 0.0, (40.0, -20.0 + 3 * i))
    board.Save(str(out))
    print(f"{board_name}: 부품 {len(comps)} · 넷 {len(nets)} · 자리 못 찾음 {missing} · 규칙 없음 {left} → {out.relative_to(ROOT)}")
    return not missing and not left


if __name__ == "__main__":
    names = sys.argv[1:] or ["carrier", "front"]
    ok = all([build(n) for n in names])
    sys.exit(0 if ok else 1)
