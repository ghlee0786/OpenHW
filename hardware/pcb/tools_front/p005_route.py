"""P-005 전면 마무리 배선 (시스템 파이썬): 지금 배선 전부를 장애물로 두고, 넷마다 끊긴 덩어리를 서로 잇는다.

assist_route.py 와 다른 점
- 출발 = 그 넷의 가장 작은 덩어리 구리 전체(패드 · 트랙 · 비아 중심), 도착 = 나머지 덩어리 전체 → 좁은 패드에서만 나오지 않아도 된다.
- 탐색 창 = 두 덩어리 둘레 margin(기본 10mm), 상한 cap(기본 600만).
- 같은 넷 비아 구리 안에서는 비아 중심 칸에서만 출발 · 도착(track_not_centered_on_via 방지).
규칙은 route.py 와 같다(간격 0.16 + 여유, 고속 둘레 0.30, In2 는 뒷면 고속선 아래 금지, 비아 금지 영역 · 외곽).

사용: python p005_route.py <geom-all.json> <out.json> <넷 정규식> [넷 정규식 ...]
  환경: P5_MARGIN(mm) · P5_CAP · P5_LAYERS(예 "0,3,2") · P5_WIDTHS(예 "0.2,0.15")
출력: {"routes":[{net, ok, tracks, vias}]} — apply_assist.py 형식.
"""
import json
import math
import os
import re
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).resolve().parent))
import route  # noqa: E402

BLOCKERS = {}  # 마지막 실패에서 닿는 구역을 둘러싼 넷 → 칸 수 (p005_rip.py 가 뜯을 후보로 쓴다)
LMAP = {"F.Cu": 0, "In1.Cu": 1, "GND": 1, "In2.Cu": 2, "GND_PWR": 2, "B.Cu": 3}
G = route.G


def mask_windows(pcb):
    """보드 파일의 *.Mask 채운 사각형(IR LED 열 창 — 드러난 구리) → [(층, x0, y0, x1, y1)]. 다른 넷이 지나가면 solder_mask_bridge."""
    txt = open(pcb, encoding="utf-8").read()
    out = []
    for m in re.finditer(r'\(gr_rect\s*\(start ([\d.-]+) ([\d.-]+)\)\s*\(end ([\d.-]+) ([\d.-]+)\).*?\(layer "([FB])\.Mask"\)', txt, re.S):
        x0, y0, x1, y1 = (float(m.group(i)) for i in range(1, 5))
        out.append((0 if m.group(5) == "F" else 3, min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)))
    return out


def load(geom):
    if os.environ.get("P5_NO_SILKTXT"):  # 참조 글자 둘레 비아 금지는 배선 중엔 뺀다 — 글자는 배선 뒤 다시 놓는다(silk.py refs, pcb O-105 발견)
        geom = dict(geom, keepouts=[k for k in geom["keepouts"] if not k["name"].startswith("SILKTXT_")])
    if os.environ.get("P5_NO_SILK"):  # 풋프린트 실크 선 둘레 비아 금지도 뺀다 — 덮인(tented) 비아 위 실크는 허용(O-110 ①), 선은 배선 뒤 silk.py 가 다시 다듬는다
        geom = dict(geom, keepouts=[k for k in geom["keepouts"] if not k["name"].startswith("SILK_")])
    B = route.Board(geom)
    if os.environ.get("P5_PCB"):  # 마스크 창: 그 층 트랙 금지 + 비아 금지(여유 0.1)
        for L, x0, y0, x1, y1 in mask_windows(os.environ["P5_PCB"]):
            r0, c0 = B.cell(x0 - 0.1, y0 - 0.1)
            r1, c1 = B.cell(x1 + 0.1, y1 + 0.1)
            B.hard[L, max(r0, 0):r1 + 1, max(c0, 0):c1 + 1] = True
            B.hardvia[max(r0, 0):r1 + 1, max(c0, 0):c1 + 1] = True
    if os.environ.get("P5_ZONES"):  # GND 아닌 구리 영역(IR 열 구리)은 그 넷의 구리 — 다른 넷이 지나가면 채움이 잘려 끊긴다(p005_zones.py)
        for z in json.load(open(os.environ["P5_ZONES"], encoding="utf-8")):
            if z["net"] in B.netid:
                for ln in z["layers"]:
                    B.raster_poly(LMAP[ln], z["outline"], B.netid[z["net"]])
    for t in geom["tracks"]:
        if t["net"] in B.netid:
            B.add_track(t["net"], LMAP[t["layer"]], tuple(t["a"]), tuple(t["b"]), t["w"])
    for v in geom["vias"]:
        if v["net"] in B.netid:
            B.add_via(v["net"], tuple(v["pos"]), {"dia": v["dia"], "drill": v["drill"]})
    return B


def components(B, net):
    """층별 연결 요소를 구멍(비아 · 관통 패드)에서 합친 덩어리 번호 배열 (4, ny, nx), 0 = 그 넷 구리 아님."""
    nid = B.netid[net]
    own = B.occ == nid
    lab = np.zeros(own.shape, np.int32)
    base = 0
    for L in range(4):
        l2, n2 = ndimage.label(own[L], structure=np.ones((3, 3)))
        lab[L] = np.where(l2 > 0, l2 + base, 0)
        base += n2
    parent = list(range(base + 1))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    hs = B.holes & own.all(axis=0)
    for r, c in zip(*np.nonzero(hs)):
        ids = [int(lab[L, r, c]) for L in range(4)]
        for a in ids[1:]:
            parent[find(a)] = find(ids[0])
    roots = np.array([find(i) for i in range(base + 1)])
    return roots[lab]


def via_noncenter(B, net):
    """같은 넷 비아 구리 중 중심 칸이 아닌 칸."""
    m = np.zeros((B.ny, B.nx), bool)
    cen = []
    for v in B.vias:
        if v["net"] == net:
            B.disc(m, v["pos"], v["dia"] / 2 + G, True)
            cen.append(B.cell(*v["pos"]))
    for r, c in cen:
        m[r, c] = False
    return m


def reach(B, starts_mask, passable, viaok, layers):
    """출발 칸에서 닿는 칸(층별 bool). 층 안은 8방향 연결, 층 바꿈은 viaok 칸에서."""
    st = np.ones((3, 3))
    reg = {L: np.zeros_like(viaok) for L in layers}
    seeds = {L: starts_mask[L] & passable[L] for L in layers}
    lab = {L: ndimage.label(passable[L], structure=st)[0] for L in layers}
    changed = True
    while changed:
        changed = False
        for L in layers:
            ids = np.unique(lab[L][seeds[L] & ~reg[L]])
            ids = ids[ids > 0]
            if len(ids):
                reg[L] |= np.isin(lab[L], ids)
                changed = True
        anyv = np.zeros_like(viaok)
        for L in layers:
            anyv |= reg[L]
        anyv &= viaok
        for L in layers:
            seeds[L] = anyv & passable[L]
    return reg


def widths_of(net):
    if os.environ.get("P5_WIDTHS"):
        return [float(x) for x in os.environ["P5_WIDTHS"].split(",")]
    nc = route.netclass(net)
    if nc["name"] == "Default":
        return [0.2, 0.15]
    if net == "/CORE_3V3":  # R-020: 최악 1.0A — 0.30mm 이상만(review V-006a)
        return [0.3]
    if nc["name"] == "PWR_LOGIC":
        return [0.3, 0.2]
    return [nc["track_width"], max(0.3, nc["track_width"] / 2), 0.3]


def route_net(B, net, margin, cap, layers, log):
    out_t, out_v = [], []
    nc = route.netclass(net)
    vtype = route.VIA_PWR if nc["name"].startswith("PWR_") and nc["name"] != "PWR_LOGIC" else route.VIA
    own = {B.netid[net]}
    tried = set()
    while True:
        comp = components(B, net)
        ids, cnt = np.unique(comp[comp > 0], return_counts=True)
        # 구멍 없는 In1 조각(비아 자리 표시)은 덩어리로 세지 않는다
        ids = [int(i) for i in ids if (comp[[0, 2, 3]] == i).any()]
        if len(ids) <= 1:
            return True, out_t, out_v
        sizes = {i: int((comp == i).sum()) for i in ids}
        order = [i for i in sorted(ids, key=lambda i: sizes[i]) if i not in tried]
        if not order:
            return False, out_t, out_v
        src = order[0]
        nonc = via_noncenter(B, net)
        got = None
        for w in widths_of(net):
            sm = (comp == src)
            tm = (comp > 0) & ~sm
            rs = np.nonzero(sm.any(axis=0))
            # 창: 출발 덩어리 bbox + 가장 가까운 도착 칸
            sr0, sr1, sc0, sc1 = rs[0].min(), rs[0].max(), rs[1].min(), rs[1].max()
            tr, tc = np.nonzero(tm[[0, 2, 3]].any(axis=0))
            cr, cc = (sr0 + sr1) // 2, (sc0 + sc1) // 2
            k = int(np.argmin((tr - cr) ** 2 + (tc - cc) ** 2))
            win = B.window([(sr0, sc0), (sr1, sc1), (int(tr[k]), int(tc[k]))], margin)
            r0, r1, c0, c1 = win
            passable, viaok = B.free_maps(win, own, w / 2, vtype["dia"] / 2, layers)
            sl = (slice(r0, r1 + 1), slice(c0, c1 + 1))
            starts, targets = set(), set()
            for L in layers:
                a = sm[L][sl] & passable[L] & ~nonc[sl]
                starts |= {(L, int(r), int(c)) for r, c in zip(*np.nonzero(a))}
                b = tm[L][sl] & ~nonc[sl]
                targets |= {(L, int(r), int(c)) for r, c in zip(*np.nonzero(b))}
            log(f"  {net} w={w} 덩어리 {len(ids)} 출발 {len(starts)} 도착 {len(targets)} 창 {(r1 - r0 + 1, c1 - c0 + 1)}")
            if not starts or not targets:
                continue
            smask = {L: sm[L][sl] & ~nonc[sl] for L in layers}
            reg = reach(B, smask, passable, viaok, layers)
            if not any((reg[L] & tm[L][sl] & ~nonc[sl]).any() for L in layers):
                # 막힘 진단: 닿는 구역 둘레의 다른 넷
                names = {v: k for k, v in B.netid.items()}
                blk = {}
                for L in layers:
                    ring = ndimage.binary_dilation(reg[L], iterations=int((route.CLR + w + 0.15) / G)) & ~reg[L]
                    o = B.occ[L][sl]
                    ids_, cn = np.unique(o[ring & (o != 0) & (o != B.netid[net])], return_counts=True)
                    for i_, c_ in zip(ids_, cn):
                        blk[names.get(int(i_), str(int(i_)))] = blk.get(names.get(int(i_), str(int(i_))), 0) + int(c_)
                area = sum(int(reg[L].sum()) for L in layers)
                log(f"    닿지 않음(w={w}): 닿는 칸 {area} · 둘레 넷 {sorted(blk.items(), key=lambda kv: -kv[1])[:8]}")
                if area < 40000:  # 작은 덩어리 쪽(갇힌 쪽) 둘레만 후보로
                    for k_, v_ in blk.items():
                        BLOCKERS[k_] = BLOCKERS.get(k_, 0) + v_
                continue
            tm2 = np.zeros(viaok.shape, bool)
            for _, r_, c_ in targets:
                tm2[r_, c_] = True
            hmap = ndimage.distance_transform_edt(~tm2).astype(np.float32)
            path = B.astar(win, starts, targets, passable, viaok, layers, cap=cap, hmap=hmap)
            if path:
                got = (w, path, win)
                break
        if not got:
            tried.add(src)
            log(f"  {net}: 덩어리 {src}(칸 {sizes[src]}) 경로 없음")
            if len(tried) >= len(ids):
                return False, out_t, out_v
            continue
        tried.clear()
        w, path, (r0, _, c0, _) = got
        segs = B.corners([(L, r + r0, c + c0, d) for L, r, c, d in path])
        for kk, (L, cells) in enumerate(segs):
            pts = [B.xy(*p) for p in cells]
            for a, b_ in zip(pts[:-1], pts[1:]):
                B.add_track(net, L, a, b_, w)
                out_t.append({"layer": route.LAYERS[L], "a": list(a), "b": list(b_), "w": w})
            if kk < len(segs) - 1:
                B.add_via(net, pts[-1], vtype)
                out_v.append({"pos": list(pts[-1]), "dia": vtype["dia"], "drill": vtype["drill"]})


def main():
    geom = json.load(open(sys.argv[1], encoding="utf-8"))
    pats = [re.compile(p) for p in sys.argv[3:]]
    margin = float(os.environ.get("P5_MARGIN", "10"))
    cap = int(os.environ.get("P5_CAP", "6000000"))
    layers = [int(x) for x in os.environ.get("P5_LAYERS", "0,3,2").split(",")]
    B = load(geom)

    def log(s):
        print(s, flush=True)
    out = []
    for pat in pats:
        for net in [n for n in B.netid if pat.fullmatch(n)]:
            if net == "/GND":
                continue
            ok, tr, vi = route_net(B, net, margin, cap, layers, log)
            log(f"{net}: {'이음' if ok else '실패'} · 트랙 {len(tr)} · 비아 {len(vi)}")
            if tr or vi or not ok:
                out.append({"net": net, "ok": bool(tr or vi), "done": ok, "tracks": tr, "vias": vi})
            json.dump({"routes": out}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump({"routes": out}, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
