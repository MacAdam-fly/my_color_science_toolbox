"""Projected plane-gamut and gamut-ring comparisons."""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from color.spaces import LCHab_to_Lab, SpaceSpec, convert_color, xyY_to_xy
from color.plot import (
    plot_cie1931_diagram,
    plot_style,
)

from _example_helpers import (
    COLOURS,
    compute_example_boundaries,
    save_figure,
)


def _slice_xy(boundary, L: float) -> np.ndarray:
    """Return the fixed-L* LCHab boundary slice projected to CIE xy."""
    xyY = convert_color(
        boundary.slice_L(L),
        SpaceSpec("LCHab", whitepoint_XYZ=boundary.whitepoint_XYZ),
        "xyY",
    )
    return xyY_to_xy(xyY)


def _plot_projection_comparison(boundaries) -> None:
    slice_L = 50.0
    with plot_style("journal_double"):
        fig = plt.figure(figsize=(11.8, 7.4), constrained_layout=False)
        grid = fig.add_gridspec(
            2,
            3,
            height_ratios=(1.0, 1.0),
            left=0.06,
            right=0.96,
            bottom=0.08,
            top=0.88,
            wspace=0.32,
            hspace=0.42,
        )

        ax_xy = fig.add_subplot(grid[0, 0])
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*", category=UserWarning)
            plot_cie1931_diagram(
                ax=ax_xy,
                show_background=True,
                background_samples=160,
                title="xy: primary chromaticity hull",
            )
        for index, (name, boundary) in enumerate(boundaries.items()):
            primary_xy = boundary.xy_boundary()
            ax_xy.plot(
                primary_xy[:, 0],
                primary_xy[:, 1],
                label=name,
                color=COLOURS[name],
                linestyle=("-", "--", "-.")[index],
                linewidth=1.2,
            )
        ax_xy.legend(fontsize=6, loc="upper right")

        ax_polar = fig.add_subplot(grid[0, 1], projection="polar")
        for name, boundary in boundaries.items():
            ax_polar.plot(
                np.radians(boundary.hue_values),
                boundary.projected_chroma_boundary(),
                label=name,
                color=COLOURS[name],
                linewidth=1.2,
            )
        ax_polar.set_title("LCHab polar: max C* over L*", pad=12)
        ax_polar.set_theta_zero_location("E")
        ax_polar.set_theta_direction(1)
        ax_polar.grid(True, alpha=0.25)
        ax_polar.legend(fontsize=6, loc="upper right", bbox_to_anchor=(1.2, 1.12))

        ax_projected = fig.add_subplot(grid[0, 2])
        for index, (name, boundary) in enumerate(boundaries.items()):
            projected_ab = boundary.projected_ab_boundary()
            ax_projected.plot(
                projected_ab[:, 0],
                projected_ab[:, 1],
                label=name,
                color=COLOURS[name],
                linestyle=("-", "--", "-.")[index],
                linewidth=1.2,
            )
        ax_projected.set_title("Lab a*b*: projected plane")
        ax_projected.set_xlabel("a*")
        ax_projected.set_ylabel("b*")
        ax_projected.set_aspect("equal", adjustable="box")
        ax_projected.grid(True, alpha=0.25)
        ax_projected.legend(fontsize=6)

        ax_slice_xy = fig.add_subplot(grid[1, 0])
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message=".*tight_layout.*", category=UserWarning)
            plot_cie1931_diagram(
                ax=ax_slice_xy,
                show_background=True,
                background_samples=160,
                title=f"xy: L* = {slice_L:g} slice trace",
            )
        for index, (name, boundary) in enumerate(boundaries.items()):
            xy = _slice_xy(boundary, slice_L)
            ax_slice_xy.plot(
                xy[:, 0],
                xy[:, 1],
                label=name,
                color=COLOURS[name],
                linestyle=("-", "--", "-.")[index],
                linewidth=1.2,
            )
        ax_slice_xy.legend(fontsize=6, loc="upper right")

        ax_slice_polar = fig.add_subplot(grid[1, 1], projection="polar")
        for name, boundary in boundaries.items():
            LCHab = boundary.slice_L(slice_L)
            ax_slice_polar.plot(
                np.radians(LCHab[:, 2]),
                LCHab[:, 1],
                label=name,
                color=COLOURS[name],
                linewidth=1.2,
            )
        ax_slice_polar.set_title(f"LCHab polar: L* = {slice_L:g}", pad=12)
        ax_slice_polar.set_theta_zero_location("E")
        ax_slice_polar.set_theta_direction(1)
        ax_slice_polar.grid(True, alpha=0.25)
        ax_slice_polar.legend(fontsize=6, loc="upper right", bbox_to_anchor=(1.2, 1.12))

        ax_slice_lab = fig.add_subplot(grid[1, 2])
        for index, (name, boundary) in enumerate(boundaries.items()):
            lab = LCHab_to_Lab(boundary.slice_L(slice_L))
            ax_slice_lab.plot(
                lab[:, 1],
                lab[:, 2],
                label=name,
                color=COLOURS[name],
                linestyle=("-", "--", "-.")[index],
                linewidth=1.2,
            )
        ax_slice_lab.set_title(f"Lab a*b*: L* = {slice_L:g}")
        ax_slice_lab.set_xlabel("a*")
        ax_slice_lab.set_ylabel("b*")
        ax_slice_lab.set_aspect("equal", adjustable="box")
        ax_slice_lab.grid(True, alpha=0.25)
        ax_slice_lab.legend(fontsize=6, loc="upper left", bbox_to_anchor=(1.02, 1.0))

        fig.suptitle("Gamut Boundary Views: Overall Projection and L* = 50 Slice", y=0.97)
        save_figure(fig, "04_projected_plane_comparison_subplots.png")


def _plot_gamut_rings(boundaries) -> None:
    L_steps = [25.0, 50.0, 75.0, 100.0]
    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.8), constrained_layout=True)
        for index, (ax, (name, boundary)) in enumerate(zip(axes, boundaries.items())):
            rings, steps = boundary.gamut_rings(L_steps)
            for ring, step in zip(rings, steps):
                ax.plot(ring[:, 0], ring[:, 1], label=f"L* <= {step:g}", linewidth=1.1)
            ax.set_title(name)
            ax.set_xlabel("a*")
            if index == 0:
                ax.set_ylabel("b*")
            else:
                ax.set_ylabel("")
            ax.set_aspect("equal", adjustable="box")
            ax.grid(True, alpha=0.25)
            ax.legend(fontsize=6)
        fig.suptitle("Cumulative Gamut Rings in Lab a*b*")
        save_figure(fig, "04_gamut_rings_comparison.png")


def main() -> None:
    boundaries = compute_example_boundaries()
    print("=" * 20 + " projected plane gamut " + "=" * 20)
    for name, boundary in boundaries.items():
        print(f"{name:8s} projected a*b* area: {boundary.projected_ab_area():10.2f}")
        print(f"{name:8s} final ring area: {boundary.ring_area():10.2f}")

    _plot_projection_comparison(boundaries)
    _plot_gamut_rings(boundaries)


if __name__ == "__main__":
    main()
