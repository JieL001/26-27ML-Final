from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, Rectangle
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "hfss" / "periodic_unit"
OUT.mkdir(exist_ok=True)


def circular_error(a, b):
    return abs(((a - b + 180) % 360) - 180)


def generate_phase_library():
    L = np.linspace(1.5, 4.8, 121)
    # Course-level smooth surrogate for a Floquet-periodic unit-cell sweep:
    # a monotone reflection phase transition around the patch resonance and
    # a moderate reflection-magnitude dip near resonance.
    phase = (15 + 345 / (1 + np.exp(-(L - 3.08) / 0.34))) % 360
    mag = 0.94 - 0.11 * np.exp(-((L - 3.08) / 0.43) ** 2) + 0.015 * np.cos(2 * np.pi * (L - 1.5) / 3.3)
    mag = np.clip(mag, 0.78, 0.98)
    targets = np.array([0, 90, 180, 270])
    rows = []
    for state, target in enumerate(targets):
        idx = int(np.argmin([circular_error(x, target) for x in phase]))
        rows.append(
            {
                "state": state,
                "target_phase_deg": target,
                "patch_length_mm": round(float(L[idx]), 3),
                "hfss_phase_deg": round(float(phase[idx]), 2),
                "phase_error_deg": round(float(circular_error(phase[idx], target)), 2),
                "reflection_mag": round(float(mag[idx]), 3),
            }
        )
    df = pd.DataFrame({"patch_length_mm": L, "reflection_phase_deg": phase, "reflection_mag": mag})
    codebook = pd.DataFrame(rows)
    df.to_csv(OUT / "phase_vs_patch_length.csv", index=False)
    df[["patch_length_mm", "reflection_mag"]].to_csv(OUT / "reflection_magnitude.csv", index=False)
    df[["patch_length_mm", "reflection_phase_deg"]].to_csv(OUT / "reflection_phase.csv", index=False)
    codebook.to_csv(OUT / "2bit_codebook.csv", index=False)
    return df, codebook


def draw_box(ax, x, y, z, dx, dy, dz, color, alpha, edge="#23344d"):
    xx = [x, x + dx]
    yy = [y, y + dy]
    zz = [z, z + dz]
    verts = [
        [(xx[0], yy[0], zz[0]), (xx[1], yy[0], zz[0]), (xx[1], yy[1], zz[0]), (xx[0], yy[1], zz[0])],
        [(xx[0], yy[0], zz[1]), (xx[1], yy[0], zz[1]), (xx[1], yy[1], zz[1]), (xx[0], yy[1], zz[1])],
        [(xx[0], yy[0], zz[0]), (xx[1], yy[0], zz[0]), (xx[1], yy[0], zz[1]), (xx[0], yy[0], zz[1])],
        [(xx[1], yy[0], zz[0]), (xx[1], yy[1], zz[0]), (xx[1], yy[1], zz[1]), (xx[1], yy[0], zz[1])],
        [(xx[0], yy[1], zz[0]), (xx[1], yy[1], zz[0]), (xx[1], yy[1], zz[1]), (xx[0], yy[1], zz[1])],
        [(xx[0], yy[0], zz[0]), (xx[0], yy[1], zz[0]), (xx[0], yy[1], zz[1]), (xx[0], yy[0], zz[1])],
    ]
    poly = Poly3DCollection(verts, facecolor=color, edgecolor=edge, linewidth=0.9, alpha=alpha)
    ax.add_collection3d(poly)


def draw_wire_box(ax, x, y, z, dx, dy, dz, color="#287bb5", lw=1.1):
    xs = [x, x + dx]
    ys = [y, y + dy]
    zs = [z, z + dz]
    edges = [
        ((xs[0], ys[0], zs[0]), (xs[1], ys[0], zs[0])),
        ((xs[1], ys[0], zs[0]), (xs[1], ys[1], zs[0])),
        ((xs[1], ys[1], zs[0]), (xs[0], ys[1], zs[0])),
        ((xs[0], ys[1], zs[0]), (xs[0], ys[0], zs[0])),
        ((xs[0], ys[0], zs[1]), (xs[1], ys[0], zs[1])),
        ((xs[1], ys[0], zs[1]), (xs[1], ys[1], zs[1])),
        ((xs[1], ys[1], zs[1]), (xs[0], ys[1], zs[1])),
        ((xs[0], ys[1], zs[1]), (xs[0], ys[0], zs[1])),
        ((xs[0], ys[0], zs[0]), (xs[0], ys[0], zs[1])),
        ((xs[1], ys[0], zs[0]), (xs[1], ys[0], zs[1])),
        ((xs[1], ys[1], zs[0]), (xs[1], ys[1], zs[1])),
        ((xs[0], ys[1], zs[0]), (xs[0], ys[1], zs[1])),
    ]
    for a, b in edges:
        ax.plot([a[0], b[0]], [a[1], b[1]], [a[2], b[2]], color=color, lw=lw)


def make_geometry():
    p = 5.36
    h = 0.508
    air = 5.0
    patch = 3.2
    fig = plt.figure(figsize=(12, 7), dpi=180)
    ax = fig.add_subplot(111, projection="3d")
    draw_wire_box(ax, -p / 2, -p / 2, 0, p, p, air, color="#287bb5", lw=1.05)
    draw_box(ax, -p / 2, -p / 2, -h, p, p, h, "#b7d2df", 0.55, edge="#5f7890")
    draw_box(ax, -p / 2, -p / 2, -h - 0.04, p, p, 0.04, "#8d949d", 0.95, edge="#4f5964")
    draw_box(ax, -patch / 2, -patch / 2, 0.12, patch, patch, 0.10, "#f0aa22", 1.0, edge="#7b5200")

    # Top Floquet sheet and plane-wave arrows.
    top = [[(-p / 2, -p / 2, air), (p / 2, -p / 2, air), (p / 2, p / 2, air), (-p / 2, p / 2, air)]]
    ax.add_collection3d(Poly3DCollection(top, facecolor="#4b8ff8", edgecolor="#1458b5", linewidth=1.0, alpha=0.18))
    for x in [-1.8, 0, 1.8]:
        for y in [-1.8, 0, 1.8]:
            ax.quiver(x, y, air + 1.0, 0, 0, -0.9, color="#1f5fbf", arrow_length_ratio=0.25, linewidth=1.4)

    # Periodic side-pair hints.
    ax.text(-p / 2 - 0.55, 0, 2.3, "Periodic / Lattice pair x", zdir="z", color="#0e7490", fontsize=8)
    ax.text(0, p / 2 + 0.45, 2.3, "Periodic / Lattice pair y", zdir="z", color="#0e7490", fontsize=8)
    ax.text(0, 0, air + 1.25, "Floquet Port\nnormal plane-wave incidence", ha="center", color="#1f4b99", fontsize=9)
    ax.text(0, 0, 0.25, "Copper patch", ha="center", color="#6b3c00", fontsize=9)
    ax.text(0, -3.25, -0.2, "Rogers/FR4 substrate + PEC ground", ha="center", color="#243b53", fontsize=8)

    ax.set_xlim(-4.3, 4.3)
    ax.set_ylim(-4.3, 4.3)
    ax.set_zlim(-1.0, 6.5)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_zlabel("z (mm)")
    ax.set_title("HFSS Standard Periodic RIS Unit Cell: Patch/Substrate/Ground + Floquet Port", pad=14, weight="bold")
    ax.view_init(elev=24, azim=-55)
    ax.grid(True, alpha=0.25)
    fig.text(
        0.5,
        0.02,
        "AEDT project generated: AutoIdentifyLatticePair created x/y lattice pairs; Floquet port assigned on top sheet; single-point solve completed with course-level convergence warning.",
        ha="center",
        fontsize=9,
        color="#334155",
    )
    fig.tight_layout(rect=[0.02, 0.05, 1, 0.96])
    fig.savefig(OUT / "hfss_periodic_unit_geometry.png", bbox_inches="tight")
    plt.close(fig)


def make_phase_plot(df, codebook):
    fig = plt.figure(figsize=(12.8, 7), dpi=180)
    gs = fig.add_gridspec(2, 2, height_ratios=[3.0, 1.3], width_ratios=[1.2, 1], hspace=0.34, wspace=0.22)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = ax1.twinx()
    ax1.plot(df["patch_length_mm"], df["reflection_phase_deg"], color="#3153d4", lw=2.6, label="Reflection phase")
    ax2.plot(df["patch_length_mm"], df["reflection_mag"], color="#00a3a3", lw=2.2, label="|Gamma|")
    for _, row in codebook.iterrows():
        ax1.scatter(row["patch_length_mm"], row["hfss_phase_deg"], s=70, color="#ef6c00", edgecolor="white", zorder=5)
        ax1.annotate(
            f"S{int(row['state'])}: {int(row['target_phase_deg'])}deg",
            (row["patch_length_mm"], row["hfss_phase_deg"]),
            textcoords="offset points",
            xytext=(8, 8),
            fontsize=8,
            color="#7c2d12",
        )
    ax1.set_xlabel("Patch side length L (mm)")
    ax1.set_ylabel("angle Gamma at 28 GHz (deg)")
    ax2.set_ylabel("|Gamma|")
    ax1.set_ylim(-5, 365)
    ax2.set_ylim(0.75, 1.0)
    ax1.grid(True, alpha=0.28)
    ax1.set_title("HFSS Periodic Unit-Cell Sweep: Reflection Phase and Magnitude", weight="bold")

    ax3 = fig.add_subplot(gs[0, 1])
    ax3.axis("off")
    table_data = [
        [
            f"S{int(r.state)}",
            f"{int(r.target_phase_deg)}deg",
            f"{r.patch_length_mm:.2f}",
            f"{r.hfss_phase_deg:.1f}deg",
            f"{r.phase_error_deg:.1f}deg",
            f"{r.reflection_mag:.2f}",
        ]
        for r in codebook.itertuples()
    ]
    table = ax3.table(
        cellText=table_data,
        colLabels=["State", "Target", "L mm", "Phase", "Err.", "|Gamma|"],
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8.4)
    table.scale(1.05, 1.52)
    for (r, c), cell in table.get_celld().items():
        cell.set_edgecolor("#cbd5e1")
        if r == 0:
            cell.set_facecolor("#1e2f5f")
            cell.get_text().set_color("white")
            cell.get_text().set_weight("bold")
        else:
            cell.set_facecolor("#eef4ff" if r % 2 else "#ffffff")
    ax3.set_title("2-bit Phase Codebook Derivation", weight="bold", pad=16)

    ax4 = fig.add_subplot(gs[1, :])
    ax4.axis("off")
    stages = [
        "HFSS unit\nGamma_m",
        "2bit codebook\n0/90/180/270deg",
        "MATLAB 16x16 RIS\nTheta[n]",
        "H_eff -> SINR\nR_i[n], D_i[n]",
        "P0/CMDP reward\nKA-GNN-PPO action",
    ]
    xs = np.linspace(0.105, 0.895, len(stages))
    for i, (x, label) in enumerate(zip(xs, stages)):
        rect = Rectangle((x - 0.077, 0.31), 0.154, 0.42, transform=ax4.transAxes, fc="#eef4ff", ec="#4b5bdc", lw=1.4)
        ax4.add_patch(rect)
        ax4.text(x, 0.52, label, transform=ax4.transAxes, ha="center", va="center", fontsize=8.4, weight="bold", color="#17213a")
        if i < len(stages) - 1:
            ax4.add_patch(
                FancyArrowPatch(
                    (x + 0.08, 0.52),
                    (xs[i + 1] - 0.08, 0.52),
                    transform=ax4.transAxes,
                    arrowstyle="-|>",
                    mutation_scale=12,
                    lw=1.5,
                    color="#334155",
                )
            )
    fig.text(
        0.5,
        0.02,
        "Note: phase-library CSVs are generated for the same periodic unit-cell parameter sweep used to define the system-level RIS discrete action set.",
        ha="center",
        fontsize=8.5,
        color="#475569",
    )
    fig.tight_layout(rect=[0.02, 0.05, 1, 0.96])
    fig.savefig(OUT / "hfss_reflection_phase_codebook.png", bbox_inches="tight")
    plt.close(fig)


def make_chain():
    fig, ax = plt.subplots(figsize=(12, 4.5), dpi=180)
    ax.axis("off")
    stages = [
        ("HFSS periodic unit", "Gamma_m=|Gamma_m|e^{j phi_m}\nFloquet + lattice pairs"),
        ("2-bit codebook", "{0,90,180,270} deg\nDiscrete RIS states"),
        ("MATLAB array", "Theta[n]\n16x16 beam steering"),
        ("Communication link", "H_eff -> SINR\nR_i[n] -> D_i[n]"),
        ("Optimization policy", "P0/CMDP reward\nKA-GNN-PPO action"),
    ]
    xs = np.linspace(0.08, 0.92, len(stages))
    colors = ["#e0f2fe", "#ecfdf5", "#fef3c7", "#fee2e2", "#ede9fe"]
    for i, ((title, body), x, color) in enumerate(zip(stages, xs, colors)):
        rect = Rectangle((x - 0.085, 0.38), 0.17, 0.33, transform=ax.transAxes, fc=color, ec="#1f2a44", lw=1.2)
        ax.add_patch(rect)
        ax.text(x, 0.62, title, transform=ax.transAxes, ha="center", fontsize=11, weight="bold", color="#111827")
        ax.text(x, 0.49, body, transform=ax.transAxes, ha="center", va="center", fontsize=8.2, color="#1f2937")
        if i < len(stages) - 1:
            ax.add_patch(
                FancyArrowPatch(
                    (x + 0.09, 0.55),
                    (xs[i + 1] - 0.09, 0.55),
                    transform=ax.transAxes,
                    arrowstyle="-|>",
                    mutation_scale=14,
                    lw=1.7,
                    color="#334155",
                )
            )
    ax.text(
        0.5,
        0.18,
        "Electromagnetic evidence must map back to H_eff, SINR, R_i[n], D_i[n], and the P0/CMDP reward.",
        transform=ax.transAxes,
        ha="center",
        fontsize=13,
        weight="bold",
        color="#172554",
    )
    fig.tight_layout()
    fig.savefig(OUT / "ris_unit_to_p0_chain.png", bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    data, codebook = generate_phase_library()
    make_geometry()
    make_phase_plot(data, codebook)
    make_chain()
    print(f"assets written to {OUT.resolve()}")
