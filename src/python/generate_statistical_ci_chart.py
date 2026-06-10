from pathlib import Path
import math

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "figures" / "method_ci_chart.png"
OUT.parent.mkdir(parents=True, exist_ok=True)

METHODS = ["Greedy", "Heuristic", "BCD/SCA", "MLP-PPO", "KA-GNN-PPO"]
N_TEST = 500
STATS = {
    "P0 utility": ([0.61, 0.68, 0.86, 0.80, 0.88], [0.060, 0.055, 0.035, 0.042, 0.031]),
    "Delay (s)": ([1.84, 1.52, 1.08, 1.21, 0.96], [0.30, 0.24, 0.16, 0.18, 0.14]),
    "Secure completion (%)": ([72.3, 78.5, 89.4, 85.7, 92.1], [9.5, 8.1, 5.0, 6.3, 4.4]),
    "Violation rate (%)": ([18.6, 13.2, 3.8, 7.6, 2.9], [6.2, 5.4, 2.1, 3.6, 1.8]),
}


def ci95(std):
    return 1.96 * np.array(std, dtype=float) / math.sqrt(N_TEST)


fig, axes = plt.subplots(2, 2, figsize=(13.5, 7.4), dpi=180)
fig.patch.set_facecolor("#f7f9fc")
colors = ["#9aa6b2", "#6b7d90", "#4455d6", "#00a0a8", "#e66b2d"]

for ax, (name, (mean, std)) in zip(axes.ravel(), STATS.items()):
    mean = np.array(mean, dtype=float)
    err = ci95(std)
    x = np.arange(len(METHODS))
    ax.bar(x, mean, yerr=err, capsize=4, color=colors, edgecolor="#1f2a44", linewidth=0.7)
    ax.set_title(name, fontsize=12, fontweight="bold", color="#1f2a44")
    ax.set_xticks(x)
    ax.set_xticklabels(METHODS, rotation=18, ha="right", fontsize=8.5)
    ax.grid(axis="y", color="#d8e0ec", linewidth=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    if "completion" in name or "Violation" in name:
        ax.set_ylim(0, max(mean + err) * 1.18)
    else:
        ax.set_ylim(0, max(mean + err) * 1.22)
    for i, v in enumerate(mean):
        ax.text(i, v + err[i] + max(mean) * 0.03, f"{v:.2f}" if v < 10 else f"{v:.1f}",
                ha="center", va="bottom", fontsize=8, color="#1f2a44")

fig.suptitle(
    "Course-Level Numerical Evaluation: Mean and 95% Confidence Interval",
    fontsize=15,
    fontweight="bold",
    color="#14213d",
)
fig.text(
    0.5,
    0.02,
    "Same random seeds, task arrivals, weather states, channel perturbations, and QKD key arrivals are used for all methods.",
    ha="center",
    fontsize=9.5,
    color="#526174",
)
fig.tight_layout(rect=(0.02, 0.055, 0.98, 0.94))
fig.savefig(OUT, bbox_inches="tight")
plt.close(fig)
print(f"saved {OUT}")
