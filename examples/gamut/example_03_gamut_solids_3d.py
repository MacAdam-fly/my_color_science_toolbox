"""3D Lab colour-solid comparisons for display-primary gamuts."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from color.plot import (
    plot_3d_surface,
    plot_3d_wireframe,
    plot_style,
)

from _example_helpers import compute_example_boundaries, save_figure


def _set_lab_solid_axes(ax, *, ab_limit: float) -> None:
    """Set consistent Lab colour-solid axes."""
    ax.set_xlim(-ab_limit, ab_limit)
    ax.set_ylim(-ab_limit, ab_limit)
    ax.set_zlim(0.0, 100.0)
    ax.set_box_aspect((1.0, 1.0, 0.78))
    ax.set_xlabel("a*", labelpad=1.5)
    ax.set_ylabel("b*", labelpad=1.5)
    ax.set_zlabel("L*", labelpad=6.0)
    ax.tick_params(axis="both", which="major", pad=0)


def main() -> None:
    boundaries = compute_example_boundaries()
    ab_limit = max(
        float(np.max(np.abs(boundary.to_Lab()[..., 1:3])))
        for boundary in boundaries.values()
    ) * 1.08

    print("=" * 20 + " 3D colour-solid metrics " + "=" * 20)
    for name, boundary in boundaries.items():
        print(f"{name:8s} Lab volume: {boundary.lab_volume():10.2f}")
        print(f"{name:8s} projected a*b* area: {boundary.projected_ab_area():10.2f}")

    with plot_style("journal_double"):
        fig = plt.figure(figsize=(11.6, 4.4))
        for index, (name, boundary) in enumerate(boundaries.items(), start=1):
            ax = fig.add_subplot(1, 3, index, projection="3d")
            lab = boundary.to_Lab()
            a_grid = lab[..., 1]
            b_grid = lab[..., 2]
            L_grid = lab[..., 0]
            plot_3d_surface(
                a_grid,
                b_grid,
                L_grid,
                ax=ax,
                cmap="viridis",
                alpha=0.76,
                linewidth=0.0,
                title=f"{name}\nV={boundary.lab_volume():.0f}",
                xlabel="a*",
                ylabel="b*",
                zlabel="L*",
                view=(22.0, -48.0),
                grid=False,
            )
            plot_3d_wireframe(
                a_grid,
                b_grid,
                L_grid,
                ax=ax,
                color="0.2",
                linewidth=0.28,
                rstride=4,
                cstride=8,
                grid=False,
            )
            _set_lab_solid_axes(ax, ab_limit=ab_limit)
        fig.subplots_adjust(left=0.02, right=0.96, bottom=0.04, top=0.86, wspace=0.18)
        save_figure(fig, "03_lab_colour_solids_3d.png")


if __name__ == "__main__":
    main()
