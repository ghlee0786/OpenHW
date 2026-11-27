"""G-002 손 배선 보조 (시스템 파이썬): 지금 보드의 배선 전부를 장애물로 두고, DRC 미연결 항목을 하나씩 잇는 경로를 계산한다.
보드는 바꾸지 않는다 — 결과 JSON(트랙 · 비아)을 GUI 에서 IPC(add_tracks · add_via)로 넣는다. 규칙은 배선기(route.py)와 같다
(간격 0.16+여유, 고속 넷 둘레 0.30, In2 는 뒷면 고속선 아래 금지, 비아 금지 영역 · 외곽).

사용: python assist_route.py <geom-all.json> <drc.json> <board 이름> <out.json> [넷 거르기 정규식]
  geom-all.json = route_export.py <pcb> <json> all
"""
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route  # noqa: E402

LMAP = {"F.Cu": 0, "In1.Cu": 1, "GND": 1, "In2.Cu": 2, "GND_PWR": 2, "B.Cu": 3}


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    drc = json.load(open(sys.argv[2], encoding="utf-8"))
    board = sys.argv[3]
    pat = re.compile(sys.argv[5]) if len(sys.argv) > 5 else None
    B = route.Board(geom)
    for t in geom["tracks"]:
        if t["net"] in B.netid:
            B.add_track(t["net"], LMAP[t["layer"]], tuple(t["a"]), tuple(t["b"]), t["w"])
    for v in geom["vias"]:
        if v["net"] in B.netid:
            B.add_via(v["net"], tuple(v["pos"]), {"dia": v["dia"], "drill": v["drill"]})
    n0t, n0v = len(B.tracks), len(B.vias)
    out, skipped = [], []
    for u in drc["unconnected_items"]:
        it = u["items"]
        nets = [re.search(r"\[(/[^\]]+)\]", x["description"]) for x in it]
        if not all(nets) or nets[0].group(1) != nets[1].group(1):
            skipped.append([x["description"] for x in it])
            continue
        net = nets[0].group(1)
        if net == "/GND" or (pat and not pat.search(net)):
            skipped.append([x["description"] for x in it])
            continue
        # 출발 = 패드 항목(없으면 첫 항목 자리), 도착 = 그 넷의 다른 구리 중 둘째 항목 자리에 가장 가까운 덩어리 — 간단히 둘째 항목 둘레 칸
        src = next((x for x in it if "패드" in x["description"] or "Pad" in x["description"]), it[0])
        dst = it[1] if src is it[0] else it[0]
        sp = next((p for p in B.pads if p["net"] == net and math.dist(p["pos"], (src["pos"]["x"], src["pos"]["y"])) < 0.05), None)
        nc = route.netclass(net)
        widths = [nc["track_width"]] + ([0.15] if nc["name"] == "Default" else [max(0.3, nc["track_width"] / 2)])
        vtype = route.VIA_PWR if nc["name"].startswith("PWR_") and nc["name"] != "PWR_LOGIC" else route.VIA
        dpos = (dst["pos"]["x"], dst["pos"]["y"])
        own = {B.netid[net]}
        got = None
        for w in widths:
            starts_xy = [tuple(sp["pos"])] if sp else [(src["pos"]["x"], src["pos"]["y"])]
            r0c = B.cell(*starts_xy[0])
            r1c = B.cell(*dpos)
            win = B.window([r0c, r1c], 6.0)
            passable, viaok = B.free_maps(win, own, w / 2, vtype["dia"] / 2, [0, 3, 2])
            wr0, wr1, wc0, wc1 = win
            if sp:
                cells = set()
                for L_, polys in sp["polys"].items():
                    m = route.np.zeros((B.ny, B.nx), bool)
                    for poly in polys:
                        B.raster_poly_mask(m, poly)
                    rs, cs = route.np.nonzero(m)
                    cells |= {(LMAP[L_], r - wr0, c - wc0) for r, c in zip(rs, cs) if wr0 <= r <= wr1 and wc0 <= c <= wc1}
                starts = {s for s in cells if s[0] in passable and passable[s[0]][s[1], s[2]]}
            else:
                starts = {(L, r0c[0] - wr0, r0c[1] - wc0) for L in (0, 3, 2)}
            # 도착: 둘째 항목 자리 둘레 0.3mm 안의 같은 넷 구리 칸(모든 층)
            k = int(0.3 / route.G)
            targets = set()
            for L in (0, 3, 2):
                sub = B.occ[L, max(r1c[0] - k, wr0):r1c[0] + k + 1, max(r1c[1] - k, wc0):r1c[1] + k + 1]
                rs, cs = route.np.nonzero(sub == B.netid[net])
                targets |= {(L, max(r1c[0] - k, wr0) + r - wr0, max(r1c[1] - k, wc0) + c - wc0) for r, c in zip(rs, cs)}
            targets = {t_ for t_ in targets if 0 <= t_[1] <= wr1 - wr0 and 0 <= t_[2] <= wc1 - wc0}
            if not starts or not targets:
                continue
            path = B.astar(win, starts, targets, passable, viaok, [0, 3, 2], cap=3_000_000)
            if path:
                got = (w, path, win)
                break
        if not got:
            out.append({"net": net, "from": src["description"], "to": dst["description"], "ok": False})
            continue
        w, path, (wr0, _, wc0, _) = got
        segs = B.corners([(L, r + wr0, c + wc0, d) for L, r, c, d in path])
        tr, vi = [], []
        for kk, (L, cells) in enumerate(segs):
            pts = [B.xy(*p) for p in cells]
            for a, b_ in zip(pts[:-1], pts[1:]):
                B.add_track(net, L, a, b_, w)
                tr.append({"layer": route.LAYERS[L], "a": list(a), "b": list(b_), "w": w})
            if kk < len(segs) - 1:
                B.add_via(net, pts[-1], vtype)
                vi.append({"pos": list(pts[-1]), "dia": vtype["dia"], "drill": vtype["drill"]})
        out.append({"net": net, "from": src["description"], "to": dst["description"], "ok": True, "tracks": tr, "vias": vi})
    json.dump({"routes": out, "skipped": skipped}, open(sys.argv[4], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"손 배선 보조: 미연결 {len(drc['unconnected_items'])} · 계산 성공 {sum(1 for o in out if o['ok'])} · 실패 {sum(1 for o in out if not o['ok'])} · 건너뜀(GND·넷 다름) {len(skipped)}")


if __name__ == "__main__":
    main()
