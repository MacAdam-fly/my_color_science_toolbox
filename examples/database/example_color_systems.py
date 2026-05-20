"""Color systems: Munsell renotation data."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import matplotlib.pyplot as plt

from color.datasets import get_color_system, list_color_systems


def main() -> None:
    # --- 1. List available color systems ---
    print("Available color systems:", list_color_systems())

    # --- 2. Munsell renotation data ---
    munsell = get_color_system("munsell_srgb")
    # 查看数据结构
    print("\nMunsell sRGB data type:", type(munsell))
    print("\nMunsell sRGB data keys:", munsell.keys())
    cols = list(munsell.keys())
    n_chips = len(munsell["file_order"])
    print(f"\nMunsell sRGB: {n_chips} chips, {len(cols)} columns")
    print(f"  Columns: {cols}")

    # Column structure (from real_sRGB.xls):
    # file_order, h, V, C     — Munsell notation (h is string array : ['10RP', '10RP', '10RP', '2.5R', '2.5R', ...])
    # x, y, Y                 — Illuminant C chromaticity
    # X_C, Y_C, Z_C           — XYZ under Illuminant C
    # X_D65, Y_D65, Z_D65    — XYZ under D65 (CAT2002)
    # R, G, B                 — Analog sRGB [0, 1]
    # dR, dG, dB              — 8-bit digital sRGB [0, 255]


    lab_l = munsell["Y"]  # Use Y as lightness proxy
    chrom_x = munsell["x"]
    chrom_y = munsell["y"]
    srgb_r = munsell["R"]
    srgb_g = munsell["G"]
    srgb_b = munsell["B"]

    print(f"\n  Y range: [{lab_l.min():.2f}, {lab_l.max():.2f}]")
    print(f"  x range: [{chrom_x.min():.4f}, {chrom_x.max():.4f}]")
    print(f"  y range: [{chrom_y.min():.4f}, {chrom_y.max():.4f}]")

    # --- 3. Plot ---
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # (a) Chromaticity diagram with Munsell chips colored by sRGB
    ax = axes[0]
    colors = np.clip(np.stack([srgb_r, srgb_g, srgb_b], axis=1), 0, 1)
    ax.scatter(chrom_x, chrom_y, s=2, c=colors, alpha=0.6)
    ax.set_xlabel("x (Illuminant C)")
    ax.set_ylabel("y (Illuminant C)")
    ax.set_title(f"Munsell Chromaticity ({n_chips} chips)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # (b) Y (lightness) distribution
    ax = axes[1]
    ax.hist(lab_l, bins=50, color="steelblue", edgecolor="white")
    ax.set_xlabel("Y (luminance)")
    ax.set_ylabel("Count")
    ax.set_title("Munsell Luminance Distribution")
    ax.grid(True, alpha=0.3)

    # (c) sRGB gamut in chromaticity
    ax = axes[2]
    # Only plot chips with valid sRGB (not clipped)
    valid = (srgb_r >= 0) & (srgb_r <= 1) & (srgb_g >= 0) & (srgb_g <= 1) & (srgb_b >= 0) & (srgb_b <= 1)
    ax.scatter(chrom_x[valid], chrom_y[valid], s=2, c=colors[valid], alpha=0.6)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"Munsell in sRGB Gamut ({valid.sum()} chips)")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = Path(__file__).resolve().parent / 'output' / "color_systems.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"\nPlot saved to {out}")


if __name__ == "__main__":
    main()
