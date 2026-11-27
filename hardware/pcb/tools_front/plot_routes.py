"""배선 결과 그림(검토용): 패드·트랙·비아를 층 색으로. 사용: python plot_routes.py <geom.json> <routes.json> <out.png> [x0 y0 x1 y1 (KiCad mm)] [넷 부분문자열]"""
import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon

geom = json.load(open(sys.argv[1], encoding="utf-8"))
rts = json.load(open(sys.argv[2], encoding="utf-8"))
box = [float(v) for v in sys.argv[4:8]] if len(sys.argv) >= 8 else geom["edge"]
flt = sys.argv[8] if len(sys.argv) >= 9 else ""
col = {"F.Cu": "#d03030", "B.Cu": "#3050d0", "In2.Cu": "#d0a020", "In1.Cu": "#20a040"}
fig, ax = plt.subplots(figsize=(12, 12 * (box[3] - box[1]) / (box[2] - box[0])))
for p in geom["pads"]:
    for ln, polys in p["polys"].items():
        if ln not in ("F.Cu", "B.Cu"):
            continue
        for poly in polys:
            ax.add_patch(Polygon(poly, closed=True, fc=col[ln], alpha=0.25, ec="none"))
    if box[0] <= p["pos"][0] <= box[2] and box[1] <= p["pos"][1] <= box[3] and (box != geom["edge"]):
        ax.text(p["pos"][0], p["pos"][1], f"{p['ref']}.{p['num']}\n{p['net'].lstrip('/')[-10:]}", fontsize=5, ha="center")
for t in rts["tracks"]:
    if flt and flt not in t["net"]:
        continue
    ax.plot([t["a"][0], t["b"][0]], [t["a"][1], t["b"][1]], color=col[t["layer"]], lw=t["w"] * 72 * 12 / (box[2] - box[0]) / 25.4 * 25.4 / 1.0 * 0.04 * (box[2] - box[0]) / 1.0 if False else max(0.6, 300 * t["w"] / (box[2] - box[0])), solid_capstyle="round", alpha=0.9)
for v in rts["vias"]:
    if flt and flt not in v["net"]:
        continue
    ax.add_patch(Circle(v["pos"], v["dia"] / 2, fc="#909090", ec="k", lw=0.3))
ax.set_xlim(box[0], box[2])
ax.set_ylim(box[3], box[1])
ax.set_aspect("equal")
ax.grid(True, lw=0.2)
fig.savefig(sys.argv[3], dpi=110, bbox_inches="tight")
print("saved", sys.argv[3])
