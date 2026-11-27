"""진단 그림: 구역의 층별 패드 · 트랙 · 비아(넷 이름 붙임). 사용: python plot_area.py <geom-all.json> <out.png> x0 y0 x1 y1"""
import json, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Circle
g = json.load(open(sys.argv[1], encoding="utf-8"))
x0, y0, x1, y1 = map(float, sys.argv[3:7])
LN = {"GND": "In1.Cu", "GND_PWR": "In2.Cu"}
fig, axs = plt.subplots(1, 3, figsize=(30, 30 * (y1 - y0) / (x1 - x0) / 3 + 1))
hs = ("EPHY", "/USB_DP", "/USB_DN")
for ax, L in zip(axs, ("F.Cu", "In2.Cu", "B.Cu")):
    for p in g["pads"]:
        if not (x0 - 2 < p["pos"][0] < x1 + 2 and y0 - 2 < p["pos"][1] < y1 + 2): continue
        for poly in p["polys"].get(L, []):
            ax.add_patch(Polygon(poly, closed=True, color="#999" if p["net"] == "/GND" else "#e88", alpha=0.7, lw=0))
        if L in p["layers"]:
            ax.text(p["pos"][0], p["pos"][1], f'{p["ref"]}.{p["num"]}\n{p["net"].lstrip("/")[:10]}', fontsize=5, ha="center", va="center")
    for t in g["tracks"]:
        if LN.get(t["layer"], t["layer"]) != L: continue
        col = "#c0c" if any(k in t["net"] for k in hs) else "#888" if t["net"] == "/GND" else "#06c" if "12V" in t["net"] or "5V" in t["net"] else "#080"
        ax.plot([t["a"][0], t["b"][0]], [t["a"][1], t["b"][1]], color=col, lw=t["w"] * 72 * 30 / (x1 - x0) / 3 / 2.2, alpha=0.6, solid_capstyle="round")
        mx, my = (t["a"][0] + t["b"][0]) / 2, (t["a"][1] + t["b"][1]) / 2
        if x0 < mx < x1 and y0 < my < y1 and abs(t["a"][0] - t["b"][0]) + abs(t["a"][1] - t["b"][1]) > 1.2:
            ax.text(mx, my, t["net"].lstrip("/")[:9], fontsize=4.5, color="k")
    for v in g["vias"]:
        ax.add_patch(Circle(v["pos"], v["dia"] / 2, color="#444" if v["net"] == "/GND" else "#f80", alpha=0.8, lw=0))
    ax.set_xlim(x0, x1); ax.set_ylim(y1, y0); ax.set_aspect("equal"); ax.set_title(L); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig(sys.argv[2], dpi=55); print("saved", sys.argv[2])
