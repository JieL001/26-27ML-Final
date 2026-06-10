from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "hfss" / "periodic_unit" / "hfss_periodic_unit_geometry.png"


def iso_rect(cx, cy, w, d, sx=0.55, sy=0.32):
    hw, hd = w / 2, d / 2
    pts3 = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    return [(cx + x + sx * y, cy + sy * y) for x, y in pts3]


def add_poly(ax, pts, fc, ec, lw=1.4, alpha=1.0):
    patch = Polygon(pts, closed=True, facecolor=fc, edgecolor=ec, linewidth=lw, alpha=alpha, joinstyle="round")
    ax.add_patch(patch)
    return patch


fig, ax = plt.subplots(figsize=(12, 7), dpi=180)
ax.set_xlim(0, 12)
ax.set_ylim(0, 7)
ax.axis("off")

cx, cy = 5.8, 2.45
ground = iso_rect(cx, cy, 5.0, 3.8)
substrate = iso_rect(cx, cy + 0.45, 5.0, 3.8)
patch = iso_rect(cx, cy + 0.86, 2.7, 2.1)
top = iso_rect(cx, cy + 4.3, 5.0, 3.8)

add_poly(ax, ground, "#8f99a3", "#4b5563", 1.4, 0.95)
add_poly(ax, substrate, "#bfe0ef", "#4f7890", 1.4, 0.85)
add_poly(ax, patch, "#f4a51c", "#8a4f00", 1.8, 1.0)
add_poly(ax, top, "#7db7ff", "#1f66c2", 1.2, 0.17)

for p0, p1 in zip(substrate, top):
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#2c7fb8", lw=1.0, alpha=0.78)
for i in range(4):
    x0, y0 = top[i]
    x1, y1 = top[(i + 1) % 4]
    ax.plot([x0, x1], [y0, y1], color="#1f66c2", lw=1.2, linestyle="--", alpha=0.75)

for x in [4.7, 5.8, 6.9]:
    ax.add_patch(FancyArrowPatch((x, 6.2), (x, 4.95), arrowstyle="-|>", mutation_scale=14, lw=1.8, color="#1f5fbf"))

ax.text(6.05, 6.32, "Floquet Port: normal plane-wave incidence", ha="center", va="bottom", fontsize=12, weight="bold", color="#1f4b99")
ax.text(7.96, 4.45, "Periodic boundary / Lattice pair x", rotation=-58, fontsize=9, color="#0e7490", weight="bold")
ax.text(3.15, 4.25, "Periodic boundary / Lattice pair y", rotation=58, fontsize=9, color="#0e7490", weight="bold")
ax.text(5.8, 3.53, "Copper patch\nphase state set by L", ha="center", va="center", fontsize=11, weight="bold", color="#5f3300")
ax.text(5.8, 2.83, "Dielectric substrate", ha="center", va="center", fontsize=10, color="#1f3b4d")
ax.text(5.8, 2.15, "PEC / copper ground", ha="center", va="center", fontsize=10, color="#27313f")

param = (
    "28 GHz setup\n"
    "p = 5.36 mm (~lambda0/2)\n"
    "h = 0.508 mm\n"
    "L sweep = 1.5-4.8 mm\n"
    "Output: Gamma=|Gamma|e^{jphi}"
)
ax.text(0.7, 3.95, param, fontsize=11, color="#172554", va="top", bbox=dict(boxstyle="round,pad=0.5", fc="#eef4ff", ec="#9eb3d8"))

evidence = (
    "AEDT run evidence: AutoIdentifyLatticePair created x/y lattice pairs; "
    "Floquet port assigned on top sheet; single-point solve completed."
)
ax.text(6.05, 0.48, evidence, ha="center", fontsize=9.2, color="#475569")

fig.tight_layout()
fig.savefig(OUT, bbox_inches="tight")
plt.close(fig)
print(f"saved {OUT}")
