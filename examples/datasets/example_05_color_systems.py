"""Load Munsell renotation data and inspect its colour-system columns."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _datasets_plot_helpers import save_figure
from color.datasets import get_color_system, list_color_systems
from color.plot import plot_bars, plot_points, plot_style


def main() -> None:
    print("Available color systems:", list_color_systems())

    munsell = get_color_system("munsell_srgb")
    print("\nMunsell sRGB data type:", type(munsell))
    print("\nMunsell sRGB data keys:", munsell.keys())

    columns = list(munsell.keys())
    n_chips = len(munsell["file_order"])
    print(f"\nMunsell sRGB: {n_chips} chips, {len(columns)} columns")
    print(f"  Columns: {columns}")

    y_luminance = munsell["Y"]
    chrom_x = munsell["x"]
    chrom_y = munsell["y"]
    srgb = np.clip(np.stack([munsell["R"], munsell["G"], munsell["B"]], axis=1), 0.0, 1.0)

    print(f"\n  Y range: [{y_luminance.min():.2f}, {y_luminance.max():.2f}]")
    print(f"  x range: [{chrom_x.min():.4f}, {chrom_x.max():.4f}]")
    print(f"  y range: [{chrom_y.min():.4f}, {chrom_y.max():.4f}]")

    valid = (
        (munsell["R"] >= 0)
        & (munsell["R"] <= 1)
        & (munsell["G"] >= 0)
        & (munsell["G"] <= 1)
        & (munsell["B"] >= 0)
        & (munsell["B"] <= 1)
    )
    hist_counts, hist_edges = np.histogram(y_luminance, bins=50)
    hist_centres = 0.5 * (hist_edges[:-1] + hist_edges[1:])

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(1, 3, figsize=(16, 5))

        xy = np.column_stack([chrom_x, chrom_y])
        plot_points(
            xy,
            ax=axes[0],
            sizes=2,
            c=srgb,
            alpha=0.6,
            title=f"Munsell Chromaticity ({n_chips} chips)",
            xlabel="x (Illuminant C)",
            ylabel="y (Illuminant C)",
        )
        axes[0].set_aspect("equal", adjustable="box")

        plot_bars(
            hist_counts,
            ax=axes[1],
            labels=[f"{value:.0f}" if index % 10 == 0 else "" for index, value in enumerate(hist_centres)],
            colors="steelblue",
            title="Munsell Luminance Distribution",
            xlabel="Y bin",
            ylabel="Count",
        )

        plot_points(
            xy[valid],
            ax=axes[2],
            sizes=2,
            c=srgb[valid],
            alpha=0.6,
            title=f"Munsell in sRGB Gamut ({valid.sum()} chips)",
            xlabel="x",
            ylabel="y",
        )
        axes[2].set_aspect("equal", adjustable="box")

        save_figure(fig, "05_color_systems.png")


if __name__ == "__main__":
    main()
