"""실크 정리 (V-005 RQ-10~13, B9 · orch O-64~O-66). 배선 적용(route_apply.py) 뒤 보드 파일에 돌린다.

1) 극성 표시 추가: IR LED(D_IR_*) 캐소드 패드 바깥에 실크 선, X1 1번 패드 옆에 점 (B9/H1).
2) 실크 선폭 0.12 → 0.15 (RQ-10).
3) 실크 선을 마스크 개구에서 0.15, 외곽에서 0.30 안 부분은 잘라 낸다 (RQ-11 · RQ-12; DRU 는 낮추지 않는다).
4) 참조 지정자를 실크로 (RQ-13): 글자 1.0 · 획 0.2, 방향 0°/90° 두 가지. 조건 = 같은 면 courtyard 밖(몸체 아래 숨김 0),
   다른 실크(선 · 글자)와 0.15, 마스크 개구와 0.15, 외곽 0.30. 시험점 · 커넥터 · 극성 부품 먼저. 자리가 없으면 Fab 에 두고 목록으로 남긴다.
사용: <KiCad>/bin/python.exe silk.py <board.kicad_pcb> <보고 json>
"""
import json
import math
import re
import sys

import pcbnew

sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import thermal  # noqa: E402  (K21 열 패드 사각형)

MM, TO = pcbnew.FromMM, pcbnew.ToMM
W = 0.15          # 실크 선폭 (RQ-10)
CLR_MASK = 0.15   # 실크–마스크 개구 (DRU fab_silk_to_pad)
CLR_EDGE = 0.30   # 실크–외곽 (O-66)
CLR_SILK = 0.15   # 실크–실크
TXT_H, TXT_T = 1.0, 0.2
SILK = {"F": pcbnew.F_SilkS, "B": pcbnew.B_SilkS}
MASK = {"F": pcbnew.F_Mask, "B": pcbnew.B_Mask}
CRT = {"F": pcbnew.F_CrtYd, "B": pcbnew.B_CrtYd}
FAB = {"F": pcbnew.F_Fab, "B": pcbnew.B_Fab}
ERR = MM(0.005)


def V(x, y):
    return pcbnew.VECTOR2I(MM(x), MM(y))


def side_of(fp):
    return "B" if fp.IsFlipped() else "F"


def mask_openings(b, s):
    ps = pcbnew.SHAPE_POLY_SET()
    L = MASK[s]
    for fp in b.GetFootprints():
        for p in fp.Pads():
            if p.IsOnLayer(L):
                p.TransformShapeToPolygon(ps, L, p.GetSolderMaskExpansion(L), ERR, pcbnew.ERROR_OUTSIDE)
    for d in b.GetDrawings():
        if d.GetLayer() == L:
            d.TransformShapeToPolygon(ps, L, 0, ERR, pcbnew.ERROR_OUTSIDE)
    # V-005b RQ-14: 비아는 텐팅이어도 장애물(구멍 위 인쇄 불량 — PCBWay 'avoid overlapping with vias') → 비아 구리 링 전체
    cu = pcbnew.F_Cu if s == "F" else pcbnew.B_Cu
    for t in b.GetTracks():
        if t.GetClass() == "PCB_VIA":
            t.TransformShapeToPolygon(ps, cu, 0, ERR, pcbnew.ERROR_OUTSIDE)
    ps.Simplify()
    return ps


def silk_items(b, s):
    out = []
    for fp in b.GetFootprints():
        for g in fp.GraphicalItems():
            if g.GetClass() == "PCB_SHAPE" and g.GetLayer() == SILK[s]:
                out.append((fp, g))
    for d in b.GetDrawings():
        if d.GetClass() == "PCB_SHAPE" and d.GetLayer() == SILK[s]:
            out.append((None, d))
    return out


def add_shape(parent, b, layer, kind, a, c, width, filled=False):
    sh = pcbnew.PCB_SHAPE(parent if parent else b, kind)
    sh.SetLayer(layer)
    sh.SetWidth(MM(width))
    if kind == pcbnew.SHAPE_T_CIRCLE:
        sh.SetCenter(V(*a))
        sh.SetEnd(V(*c))
    else:
        sh.SetStart(V(*a))
        sh.SetEnd(V(*c))
    sh.SetFilled(filled)
    (parent if parent else b).Add(sh)
    return sh


def polarity_marks(b, edge, log, dots):
    for fp in b.GetFootprints():
        ref, s = fp.GetReference(), side_of(fp)
        pads = {p.GetNumber(): p for p in fp.Pads()}
        if ref.startswith("D_IR"):
            cath = [p for p in fp.Pads() if p.GetNumber() == "1"]
            anode = [p for p in fp.Pads() if p.GetNumber() == "2"]
            bb = cath[0].GetBoundingBox()
            for p in cath[1:]:
                bb.Merge(p.GetBoundingBox())
            ab = anode[0].GetBoundingBox()
            for p in anode[1:]:
                ab.Merge(p.GetBoundingBox())
            x0, y0, x1, y1 = TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom())
            dx = TO(bb.GetCenter().x - ab.GetCenter().x)
            dy = TO(bb.GetCenter().y - ab.GetCenter().y)
            off = 0.05 + CLR_MASK + W / 2 + 0.03
            if abs(dy) >= abs(dx):   # 캐소드가 애노드 위/아래 → 캐소드 바깥 변에 가로선
                y = y1 + off if dy > 0 else y0 - off
                a, c = (x0, y), (x1, y)
            else:
                x = x1 + off if dx > 0 else x0 - off
                a, c = (x, y0), (x, y1)
            add_shape(fp, b, SILK[s], pcbnew.SHAPE_T_SEGMENT, a, c, W)
            log["marks"].append({"ref": ref, "kind": "캐소드 선", "a": [round(v, 3) for v in a], "b": [round(v, 3) for v in c]})
        elif ref in dots and "1" in pads:
            p1 = pads["1"]
            bb = p1.GetBoundingBox()
            cx, cy = TO(fp.GetPosition().x), TO(fp.GetPosition().y)
            px, py = TO(p1.GetPosition().x), TO(p1.GetPosition().y)
            hw, hh = TO(bb.GetWidth()) / 2, TO(bb.GetHeight()) / 2
            r = 0.2
            off = 0.05 + CLR_MASK + r + 0.03
            # 1번 패드에서 몸체 중심 반대 방향(대각)으로
            ux = 1 if px >= cx else -1
            uy = 1 if py >= cy else -1
            ctr = (px + ux * (hw + off), py + uy * (hh + off))
            add_shape(fp, b, SILK[s], pcbnew.SHAPE_T_CIRCLE, ctr, (ctr[0] + r - W / 2, ctr[1]), W, filled=True)
            log["marks"].append({"ref": ref, "kind": "1번 점 Ø0.4", "at": [round(v, 3) for v in ctr]})


def edge_dist(edge, x, y):
    return min(x - edge[0], edge[2] - x, y - edge[1], edge[3] - y)


def clip_lines(b, s, openings, edge, log, apply=True):
    cut = removed = 0
    drop = []
    infl = pcbnew.SHAPE_POLY_SET(openings)
    infl.Inflate(MM(CLR_MASK), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
    for fp, g in silk_items(b, s):
        if apply and 0 < g.GetWidth() < MM(W):
            g.SetWidth(MM(W))
            log["widened"] += 1
        w = TO(g.GetWidth())

        def ok(x, y):
            if edge_dist(edge, x, y) < CLR_EDGE + w / 2:
                return False
            return openings.SquaredDistance(V(x, y)) >= MM(CLR_MASK + w / 2) ** 2

        k = g.GetShape()
        if k == pcbnew.SHAPE_T_SEGMENT:
            ax, ay, bx, by = TO(g.GetStart().x), TO(g.GetStart().y), TO(g.GetEnd().x), TO(g.GetEnd().y)
            pts = [(ax, ay), (bx, by)]
        elif k == pcbnew.SHAPE_T_RECTANGLE and not g.IsSolidFill():
            x0, y0, x1, y1 = TO(g.GetStart().x), TO(g.GetStart().y), TO(g.GetEnd().x), TO(g.GetEnd().y)
            pts = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        elif k == pcbnew.SHAPE_T_ARC:
            c = g.GetCenter()
            cx, cy = TO(c.x), TO(c.y)
            rr = TO(g.GetRadius())
            a0 = math.atan2(TO(g.GetStart().y) - cy, TO(g.GetStart().x) - cx)
            sweep = math.radians(g.GetArcAngle().AsDegrees())
            n = max(4, int(abs(sweep) * rr / 0.1))
            pts = [(cx + rr * math.cos(a0 + sweep * i / n), cy + rr * math.sin(a0 + sweep * i / n)) for i in range(n + 1)]
        elif k == pcbnew.SHAPE_T_CIRCLE and not g.IsSolidFill():
            c = g.GetCenter()
            cx, cy = TO(c.x), TO(c.y)
            rr = TO(g.GetRadius()) + (0 if not g.IsSolidFill() else 0)
            if g.IsSolidFill():   # 점(1번 핀 등): 잘라 낼 수 없어 통째로 판정
                if edge_dist(edge, cx, cy) < CLR_EDGE + rr + w / 2 or \
                        openings.SquaredDistance(V(cx, cy)) < MM(CLR_MASK + rr + w / 2) ** 2:
                    log["dots_fail"].append({"ref": fp.GetReference() if fp else "-", "at": [round(cx, 3), round(cy, 3)]})
                continue
            n = max(8, int(2 * math.pi * rr / 0.1))
            pts = [(cx + rr * math.cos(2 * math.pi * i / n), cy + rr * math.sin(2 * math.pi * i / n)) for i in range(n + 1)]
        elif k == pcbnew.SHAPE_T_POLY or (k == pcbnew.SHAPE_T_CIRCLE and g.IsSolidFill()):
            # 채운 1번 핀 삼각형 · 점: 잘라 내지 않고, 걸리면 0.1 단계로 최대 1.2mm 옮겨 자리를 찾는다(표시 유지)
            def bad_now():
                ps = pcbnew.SHAPE_POLY_SET()
                g.TransformShapeToPolygon(ps, g.GetLayer(), MM(w / 2) if k == pcbnew.SHAPE_T_CIRCLE else 0, ERR, pcbnew.ERROR_OUTSIDE)
                pb = ps.BBox()
                if min(TO(pb.GetLeft()) - edge[0], edge[2] - TO(pb.GetRight()), TO(pb.GetTop()) - edge[1], edge[3] - TO(pb.GetBottom())) < CLR_EDGE:
                    return True
                ps.BooleanIntersection(infl)
                return ps.OutlineCount() > 0
            moved = None
            if bad_now() and not apply:
                log.setdefault("conflicts", []).append({"ref": fp.GetReference() if fp else "-", "side": s, "shape": "채운 표시"})
                continue
            if bad_now():
                for d in [i / 10 for i in range(1, 13)]:
                    for ux, uy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                        dv = V(ux * d, uy * d)
                        g.Move(dv)
                        if not bad_now():
                            moved = (ux * d, uy * d)
                            break
                        g.Move(V(-ux * d, -uy * d))
                    if moved:
                        break
                log["marks_moved"].append({"ref": fp.GetReference() if fp else "-", "shape": "삼각" if k == pcbnew.SHAPE_T_POLY else "점",
                                           "moved_mm": [round(moved[0], 2), round(moved[1], 2)] if moved else None})
            continue
        else:
            log["other_shapes"].append({"ref": fp.GetReference() if fp else "-", "shape": int(k)})
            continue
        # 꼭짓점 사이를 0.02 간격으로 표본 → 조건을 만족하는 연속 구간만 선분으로 남긴다
        samp = []
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            n = max(1, int(math.hypot(x1 - x0, y1 - y0) / 0.02))
            samp += [(x0 + i / n * (x1 - x0), y0 + i / n * (y1 - y0)) for i in range(n)]
        samp.append(pts[-1])
        flags = [ok(x, y) for x, y in samp]
        if all(flags):
            continue
        if not apply:  # 판정만 (보드 단계: 풋프린트 그림은 사본 라이브러리에서만 고친다 — O-74b)
            log.setdefault("conflicts", []).append({"ref": fp.GetReference() if fp else "-", "side": s,
                                                    "at": [round(samp[flags.index(False)][0], 3), round(samp[flags.index(False)][1], 3)]})
            continue
        runs, cur = [], []
        for q, f in zip(samp, flags):
            if f:
                cur.append(q)
            else:
                if len(cur) > 1:
                    runs.append(cur)
                cur = []
        if len(cur) > 1:
            runs.append(cur)
        cut += 1
        layer = g.GetLayer()
        pieces = []
        for run in runs:
            simp = [run[0]]
            for i in range(1, len(run) - 1):
                (x0, y0), (x1, y1), (x2, y2) = simp[-1], run[i], run[i + 1]
                if abs((x1 - x0) * (y2 - y0) - (y1 - y0) * (x2 - x0)) > 1e-4:
                    simp.append(run[i])
            simp.append(run[-1])
            pieces += [(a2, c2) for a2, c2 in zip(simp[:-1], simp[1:]) if math.hypot(c2[0] - a2[0], c2[1] - a2[1]) >= 0.05]
        # 남는 조각이 없으면 지운다(Fab 로 옮기면 실크 밖 그림이 원본과 달라짐 — O-74b). 지우기는 반복이 끝난 뒤 한꺼번에(swig)
        if not pieces:
            drop.append((fp, g))
            removed += 1
            continue
        if k == pcbnew.SHAPE_T_SEGMENT:
            g.SetStart(V(*pieces[0][0]))
            g.SetEnd(V(*pieces[0][1]))
            rest = pieces[1:]
        else:
            drop.append((fp, g))
            rest = pieces
        for a2, c2 in rest:
            add_shape(fp, b, layer, pcbnew.SHAPE_T_SEGMENT, a2, c2, w)
    # 지우기는 호출한 쪽이 모든 판정이 끝난 뒤에(Remove 뒤에는 보드 반복 객체가 swig 에서 깨진다)
    log.setdefault("drop", []).extend(drop)
    log["clipped"][s] = log["clipped"].get(s, 0) + cut
    log.setdefault("to_fab", {})[s] = log.setdefault("to_fab", {}).get(s, 0) + removed


def rect_poly(x0, y0, x1, y1):
    ps = pcbnew.SHAPE_POLY_SET()
    ps.NewOutline()
    for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1)):
        ps.Append(MM(x), MM(y))
    return ps


def hits(r, obst):
    t = pcbnew.SHAPE_POLY_SET(r)
    t.BooleanIntersection(obst)
    return t.OutlineCount() > 0


def prio(ref):
    k = re.match(r"[A-Z_]+", ref).group(0)
    order = ["TP", "J", "D_IR", "D", "LED", "U", "Q", "X", "SW", "F", "L", "C", "R", "H", "MH", "B"]
    return (order.index(k) if k in order else len(order), ref)


def place_refs(b, edge, log):
    obst = {}
    crt = {}
    for s in ("F", "B"):
        o = pcbnew.SHAPE_POLY_SET(mask_openings(b, s))
        o.Inflate(MM(CLR_MASK), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
        si = pcbnew.SHAPE_POLY_SET()
        for fp, g in silk_items(b, s):
            g.TransformShapeToPolygon(si, g.GetLayer(), MM(CLR_SILK), ERR, pcbnew.ERROR_OUTSIDE)
        o.BooleanAdd(si)
        # IR LED 열 구리(K21 노출 패드 = 뒷면 마스크 개구, 열 비아 자리)는 배선 단계에서 생긴다 — 두 면 모두 글자 금지(+0.3)
        board = "front" if any(f.GetReference().startswith("D_IR") for f in b.GetFootprints()) else "carrier"
        for _, tp in thermal.TP[board]:
            x0, y0, x1, y1 = thermal.rectK(tp)
            o.BooleanAdd(rect_poly(x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3))
        obst[s] = o
        c = pcbnew.SHAPE_POLY_SET()
        for fp in b.GetFootprints():
            cs = fp.GetCourtyard(CRT[s])
            if cs.OutlineCount():
                c.BooleanAdd(cs)
        crt[s] = c
    fps = sorted(b.GetFootprints(), key=lambda f: prio(f.GetReference()))
    for fp in fps:
        ref, s = fp.GetReference(), side_of(fp)
        t = fp.Reference()
        t.SetLayer(SILK[s])
        t.SetVisible(True)
        t.SetTextSize(pcbnew.VECTOR2I(MM(TXT_H), MM(TXT_H)))
        t.SetTextThickness(MM(TXT_T))
        t.SetMirrored(s == "B")
        t.SetKeepUpright(False)
        cs = fp.GetCourtyard(CRT[s])
        bb = cs.BBox() if cs.OutlineCount() else fp.GetBoundingBox(False)
        bx0, by0, bx1, by1 = TO(bb.GetLeft()), TO(bb.GetTop()), TO(bb.GetRight()), TO(bb.GetBottom())
        bcx, bcy = (bx0 + bx1) / 2, (by0 + by1) / 2
        done = False
        for gap in (0.15, 0.4, 0.8, 1.2, 1.8, 2.5):
            for ang in (0.0, 90.0):
                t.SetTextAngleDegrees(ang)
                t.SetPosition(V(bcx, bcy))
                tb = t.GetBoundingBox()
                tw, th = TO(tb.GetWidth()), TO(tb.GetHeight())
                cands = []
                for sl in (0.0, -0.5, 0.5, -1.0, 1.0, -1.5, 1.5, -2.0, 2.0, -2.5, 2.5):
                    cands += [(bcx + sl, by0 - gap - th / 2), (bcx + sl, by1 + gap + th / 2),
                              (bx0 - gap - tw / 2, bcy + sl), (bx1 + gap + tw / 2, bcy + sl)]
                for x, y in cands:
                    t.SetPosition(V(x, y))
                    tb = t.GetBoundingBox()
                    x0, y0, x1, y1 = TO(tb.GetLeft()), TO(tb.GetTop()), TO(tb.GetRight()), TO(tb.GetBottom())
                    if min(x0 - edge[0], edge[2] - x1, y0 - edge[1], edge[3] - y1) < CLR_EDGE:
                        continue
                    r = rect_poly(x0, y0, x1, y1)
                    if hits(r, crt[s]) or hits(r, obst[s]):
                        continue
                    done = True
                    break
                if done:
                    break
            if done:
                break
        if done:
            tb = t.GetBoundingBox()
            o = pcbnew.SHAPE_POLY_SET()
            o.NewOutline()
            for xx, yy in ((tb.GetLeft(), tb.GetTop()), (tb.GetRight(), tb.GetTop()), (tb.GetRight(), tb.GetBottom()), (tb.GetLeft(), tb.GetBottom())):
                o.Append(xx, yy)
            o.Inflate(MM(CLR_SILK), pcbnew.CORNER_STRATEGY_CHAMFER_ALL_CORNERS, ERR)
            obst[s].BooleanAdd(o)
            log["refs_silk"].append({"ref": ref, "side": s, "angle": t.GetTextAngleDegrees(),
                                     "at": [round(TO(t.GetPosition().x), 3), round(TO(t.GetPosition().y), 3)]})
        else:
            t.SetLayer(FAB[s])
            t.SetTextAngleDegrees(0.0)
            t.SetPosition(fp.GetPosition())
            log["refs_fab_only"].append(ref)


def check_texts(b, edge, log):
    """실크 글자(참조 지정자) bbox + 0.15 가 마스크 개구 · 비아에 닿거나 외곽 0.30 안이면 충돌로 적는다."""
    for s in ("F", "B"):
        o = pcbnew.SHAPE_POLY_SET(mask_openings(b, s))
        o.Inflate(MM(CLR_MASK), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, ERR)
        for fp in b.GetFootprints():
            t = fp.Reference()
            if t.GetLayer() != SILK[s]:
                continue
            tb = t.GetBoundingBox()
            x0, y0, x1, y1 = TO(tb.GetLeft()), TO(tb.GetTop()), TO(tb.GetRight()), TO(tb.GetBottom())
            if min(x0 - edge[0], edge[2] - x1, y0 - edge[1], edge[3] - y1) < CLR_EDGE or hits(rect_poly(x0, y0, x1, y1), o):
                log.setdefault("conflicts", []).append({"ref": fp.GetReference(), "side": s, "text": True})


def main():
    """mode refs: 배선 전에 참조 지정자를 실크에 놓고 저장(route_export 가 글자 둘레를 비아 금지로 내보낸다).
    mode check: 배선 뒤 실크 선 · 글자의 남은 충돌(비아 · 외곽 · 이웃 패드)만 판정 — 보드는 바꾸지 않는다.
    극성 표시 · 선폭 · 자기 패드 둘레 자르기는 silk_lib.py(보드별 사본 라이브러리)에서 한다(풋프린트 그림을 바꾸면 lib_footprint_mismatch, O-74)."""
    path, rep = sys.argv[1], sys.argv[2]
    mode = sys.argv[3] if len(sys.argv) > 3 else "refs"
    b = pcbnew.LoadBoard(path)
    eb = b.GetBoardEdgesBoundingBox()
    edge = (TO(eb.GetLeft()), TO(eb.GetTop()), TO(eb.GetRight()), TO(eb.GetBottom()))
    log = {"marks": [], "widened": 0, "clipped": {}, "dots_fail": [], "other_shapes": [], "marks_moved": [], "refs_silk": [], "refs_fab_only": []}
    if mode == "refs":
        place_refs(b, edge, log)
        b.Save(path)
    else:
        for s in ("F", "B"):
            clip_lines(b, s, mask_openings(b, s), edge, log, apply=False)
        check_texts(b, edge, log)
        log["refs_silk"] = [fp.GetReference() for fp in b.GetFootprints() if fp.Reference().GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS)]
        log["refs_fab_only"] = sorted(fp.GetReference() for fp in b.GetFootprints() if fp.Reference().GetLayer() not in (pcbnew.F_SilkS, pcbnew.B_SilkS))
    json.dump(log, open(rep, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"실크 {mode}: 남은 실크 충돌 {len(log.get('conflicts', []))} · 참조 실크 {len(log['refs_silk'])} · Fab 만 {len(log['refs_fab_only'])} {log['refs_fab_only']}")


if __name__ == "__main__":
    main()
