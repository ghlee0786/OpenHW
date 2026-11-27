"""진단: 한 패드에서 폭 w 로 닿을 수 있는 영역(층별)을 그림으로. 사용: python reach_dbg.py <geom-all.json> <ref> <num> <out.png> [w] [반경mm]"""
import json, sys, math
import numpy as np
from scipy import ndimage
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, __import__("os").path.dirname(__import__("os").path.abspath(__file__)))
import route, finish_route as F
geom = json.load(open(sys.argv[1], encoding="utf-8"))
ref, num, outp = sys.argv[2], sys.argv[3], sys.argv[4]
w = float(sys.argv[5]) if len(sys.argv) > 5 else 0.15
rad = float(sys.argv[6]) if len(sys.argv) > 6 else 5.0
geom["keepouts"] = [k for k in geom["keepouts"] if not k["name"].startswith("SILKTXT_")]
if __import__("os").environ.get("HARD_ONLY") == "1":
    import rr_finish
    geom["tracks"] = [t for t in geom["tracks"] if not rr_finish.is_soft(t["net"])]
    geom["vias"] = [v for v in geom["vias"] if not rr_finish.is_soft(v["net"])]
B = route.Board(geom)
for t in geom["tracks"]:
    if t["net"] in B.netid: B.add_track(t["net"], F.LMAP[t["layer"]], tuple(t["a"]), tuple(t["b"]), t["w"])
for v in geom["vias"]:
    if v["net"] in B.netid: B.add_via(v["net"], tuple(v["pos"]), {"dia": v["dia"], "drill": v["drill"]})
p = next(q for q in B.pads if q["ref"] == ref and q["num"] == num)
net = p["net"]; nid = B.netid[net]
pr, pc = B.cell(*p["pos"]); k = int(rad / route.G)
win = (max(pr-k,0), min(pr+k,B.ny-1), max(pc-k,0), min(pc+k,B.nx-1))
layers = [0, 3, 2]
passable, viaok = B.free_maps(win, {nid}, w/2, 0.325, layers)
H, W = viaok.shape
# 닿는 영역: 층별 라벨 + 비아로 합치기(반복)
reach = {L: np.zeros((H, W), bool) for L in layers}
L0 = route.LAYERS.index(p["layers"][0])
lab0, _ = ndimage.label(passable[L0], structure=np.ones((3,3)))
r_, c_ = pr - win[0], pc - win[2]
seed = set(np.unique(lab0[max(r_-6,0):r_+7, max(c_-20,0):c_+21])) - {0}
reach[L0] = np.isin(lab0, list(seed))
for _ in range(6):
    for L in layers:
        for L2 in layers:
            if L == L2: continue
            vv = reach[L] & viaok & passable[L2]
            if vv.any():
                lab, _ = ndimage.label(passable[L2], structure=np.ones((3,3)))
                ids = set(np.unique(lab[vv])) - {0}
                reach[L2] |= np.isin(lab, list(ids))
fig, axs = plt.subplots(1, 4, figsize=(28, 8))
ext = (B.x0 + win[2]*route.G, B.x0 + win[3]*route.G, B.y0 + win[1]*route.G, B.y0 + win[0]*route.G)
for ax, L in zip(axs, layers):
    occ = B.occ[L][win[0]:win[1]+1, win[2]:win[3]+1]
    img = np.zeros((H, W, 3)); img[...] = 1.0
    img[occ != 0] = (0.75, 0.75, 0.75); img[occ == nid] = (0.2, 0.8, 0.2)
    hs = np.isin(occ, list(B.hs_ids)); img[hs] = (1.0, 0.6, 0.6)
    img[passable[L] & (occ == 0)] = (0.85, 0.92, 1.0)
    img[reach[L] ] = (0.3, 0.5, 1.0)
    ax.imshow(img, extent=ext, interpolation="nearest"); ax.set_title(f"{route.LAYERS[L]} {net} w={w} (파랑=닿음, 하늘=지날 수 있음, 회색=다른 넷, 분홍=고속)")
    ax.plot(*p["pos"], "r+", ms=14)
axs[3].imshow(viaok, extent=ext, cmap="Greens", interpolation="nearest"); axs[3].set_title("viaok"); axs[3].plot(*p["pos"], "r+", ms=14)
plt.tight_layout(); plt.savefig(outp, dpi=70); print("saved", outp, {route.LAYERS[L]: int(reach[L].sum()) for L in layers})
