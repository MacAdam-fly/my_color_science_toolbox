"""Load Pointer real-surface colour gamut data."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _datasets_plot_helpers import save_figure
from color.datasets.gamut_data import get_gamut_data, list_gamut_data
from color.plot import plot_lines, plot_style


def main() -> None:
    print("Available gamut data:", list_gamut_data())

    pointer = get_gamut_data("pointer")
    print(f"\nPointer gamut: {len(pointer['L'])} boundary points")
    print(f"  Columns: {list(pointer.keys())}")
    print(f"  L* levels: {sorted(set(pointer['L'].tolist()))}")
    print(
        f"  Reference white: Xn={pointer['Xn'][0]:.2f}, "
        f"Yn={pointer['Yn'][0]:.2f}, Zn={pointer['Zn'][0]:.2f}"
    )

    p50 = get_gamut_data("pointer", L=50)
    print(f"\n  L*=50: {len(p50['L'])} hue angles, C* range [{p50['C'].min():.1f}, {p50['C'].max():.1f}]")

    with plot_style("journal_double"):
        fig = plt.figure(figsize=(16, 5))
        ax_ab = fig.add_subplot(1, 3, 1)
        ax_polar = fig.add_subplot(1, 3, 2, projection="polar")
        ax_xy = fig.add_subplot(1, 3, 3)

        l_values = sorted(set(pointer["L"].tolist()))
        plot_lines(
            [
                (pointer["a"][pointer["L"] == L], pointer["b"][pointer["L"] == L])
                for L in l_values
            ],
            ax=ax_ab,
            labels=[f"L*={int(L)}" for L in l_values],
            linewidth=0.8,
            title="Pointer Gamut Boundary in a*b*",
            xlabel="a*",
            ylabel="b*",
        )
        ax_ab.set_aspect("equal", adjustable="box")
        ax_ab.legend(fontsize=7)

        plot_lines(
            (np.deg2rad(p50["hab"]), p50["C"]),
            ax=ax_polar,
            colors="steelblue",
            linewidth=1.0,
            title="C* vs hue angle at L*=50",
            grid=True,
            legend=False,
        )
        ax_polar.set_theta_zero_location("N")
        ax_polar.set_theta_direction(-1)

        plot_lines(
            [
                (pointer["x"][pointer["L"] == L], pointer["y"][pointer["L"] == L])
                for L in l_values
            ],
            ax=ax_xy,
            labels=[f"L*={int(L)}" for L in l_values],
            linewidth=0.8,
            title="Pointer Gamut Chromaticity",
            xlabel="x",
            ylabel="y",
        )
        ax_xy.set_aspect("equal", adjustable="box")
        ax_xy.legend(fontsize=7)

        save_figure(fig, "04_gamut_data.png")


if __name__ == "__main__":
    main()
