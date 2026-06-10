from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[2]
UNIT_DIR = ROOT / "data" / "hfss" / "periodic_unit"
OUT = ROOT / "data" / "figures" / "hfss_to_system_interface.png"
OUT.parent.mkdir(parents=True, exist_ok=True)


def read_two_col(path, x_key, y_key):
    xs, ys = [], []
    with path.open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            xs.append(float(row[x_key]))
            ys.append(float(row[y_key]))
    return np.array(xs), np.array(ys)


length, phase = read_two_col(UNIT_DIR / "reflection_phase.csv", "patch_length_mm", "reflection_phase_deg")
_, mag = read_two_col(UNIT_DIR / "reflection_magnitude.csv", "patch_length_mm", "reflection_mag")

states, targets, chosen_l, chosen_phase, chosen_mag = [], [], [], [], []
with (UNIT_DIR / "2bit_codebook.csv").open(newline="", encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        states.append(int(row["state"]))
        targets.append(float(row["target_phase_deg"]))
        chosen_l.append(float(row["patch_length_mm"]))
        chosen_phase.append(float(row["hfss_phase_deg"]))
        chosen_mag.append(float(row["reflection_mag"]))

fig = plt.figure(figsize=(13.4, 7.2), dpi=180, facecolor="#f7f9fc")
gs = fig.add_gridspec(2, 2, height_ratios=[1.05, 0.95], hspace=0.34, wspace=0.22)

ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(length, phase, color="#4455d6", lw=2.2)
ax1.scatter(chosen_l, chosen_phase, s=42, color="#e66b2d", zorder=5)
for s, x, y in zip(states, chosen_l, chosen_phase):
    ax1.text(x, y + 10, f"S{s}", ha="center", fontsize=8.5, color="#1f2a44")
ax1.set_title("Periodic Unit Reflection Phase", fontsize=12.5, fontweight="bold", color="#1f2a44")
ax1.set_xlabel("Patch length L (mm)")
ax1.set_ylabel("Phase of Gamma (deg)")
ax1.set_ylim(-5, 375)
ax1.grid(True, color="#d8e0ec")

ax2 = fig.add_subplot(gs[0, 1])
bars = ax2.bar([str(s) for s in states], chosen_mag, color="#00a0a8", edgecolor="#1f2a44", linewidth=0.8)
ax2.set_ylim(0.75, 1.0)
ax2.set_title("2-bit Codebook Reflection Magnitude", fontsize=12.5, fontweight="bold", color="#1f2a44")
ax2.set_xlabel("RIS phase state")
ax2.set_ylabel("|Gamma|")
ax2.grid(axis="y", color="#d8e0ec")
for bar, target, ph in zip(bars, targets, chosen_phase):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.006,
             f"{target:.0f} deg\n{ph:.0f} deg", ha="center", fontsize=8.5, color="#1f2a44")

ax3 = fig.add_subplot(gs[1, :])
ax3.axis("off")

boxes = [
    (0.03, 0.30, 0.24, 0.42, "HFSS periodic unit", "Gamma(L) = |Gamma|e^{j phi}\nFloquet port + lattice pairs"),
    (0.38, 0.30, 0.24, 0.42, "RIS codebook", "2-bit Theta[n]\nstate selection by KA-GNN-PPO"),
    (0.73, 0.30, 0.24, 0.42, "System objective", "H_eff -> SINR -> R_i[n]\nD_i[n] -> P0/CMDP reward"),
]

for x, y, w, h, title, body in boxes:
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.018,rounding_size=0.025",
        transform=ax3.transAxes,
        facecolor="#ffffff",
        edgecolor="#cbd5e1",
        linewidth=1.2,
    )
    ax3.add_patch(patch)
    ax3.text(x + w / 2, y + h * 0.66, title, ha="center", va="center",
             fontsize=12.5, fontweight="bold", color="#4455d6", transform=ax3.transAxes)
    ax3.text(x + w / 2, y + h * 0.34, body, ha="center", va="center",
             fontsize=10.2, color="#1f2a44", transform=ax3.transAxes)

for x0, x1 in [(0.27, 0.38), (0.62, 0.73)]:
    ax3.add_patch(FancyArrowPatch((x0, 0.51), (x1, 0.51),
                                  arrowstyle="-|>", mutation_scale=18,
                                  color="#009da6", lw=2.0, transform=ax3.transAxes))

ax3.text(
    0.5, 0.10,
    "Placement in the architecture: HFSS supports the RIS electromagnetic response; MATLAB/system simulation maps it into H_eff and the learning reward.",
    ha="center",
    va="center",
    fontsize=10.0,
    color="#526174",
    transform=ax3.transAxes,
)

fig.suptitle("RIS Evidence Chain: Standard Periodic Unit Cell to P0/CMDP Variables",
             fontsize=15.5, fontweight="bold", color="#14213d")
fig.tight_layout(rect=(0.02, 0.02, 0.98, 0.94))
fig.savefig(OUT, bbox_inches="tight")
plt.close(fig)
print(f"saved {OUT}")
