"""Pointer real-surface gamut comparison."""

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

from color.gamut import (
    is_within_pointer_gamut,
    lab_gamut_coverage,
    lab_gamut_volume,
    pointer_gamut,
    pointer_gamut_published_xy_boundary,
    xy_gamut_coverage_from_xy,
)
from color.plot import plot_cie1931_diagram, plot_lines, plot_style, style_2d_axis

from _example_helpers import COLOURS, compute_example_boundaries, save_figure


def _plot_pointer_comparison(pointer, displays) -> None:
    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.1), constrained_layout=True)

        ax = axes[0]
        pointer_ab = pointer.projected_ab_boundary()
        plot_lines(
            (pointer_ab[:, 0], pointer_ab[:, 1]),
            ax=ax,
            labels=["Pointer"],
            colors=["black"],
            linewidth=1.6,
            grid=False,
        )
        for name in ("sRGB", "Rec.2020"):
            ab = displays[name].projected_ab_boundary()
            plot_lines(
                (ab[:, 0], ab[:, 1]),
                ax=ax,
                labels=[name],
                colors=[COLOURS[name]],
                linewidth=1.2,
                grid=False,
            )
        style_2d_axis(
            ax,
            title="Pointer Gamut and Display Projected Plane Gamuts",
            xlabel="a*",
            ylabel="b*",
            equal_aspect=True,
        )
        ax.set_aspect("equal", adjustable="box")
        ax.legend()

        ax = axes[1]
        plot_cie1931_diagram(
            ax=ax,
            show_background=True,
            background_samples=192,
            title="Pointer Gamut in CIE 1931 xy",
        )
        pointer_xy = pointer_gamut_published_xy_boundary()
        plot_lines(
            (pointer_xy[:, 0], pointer_xy[:, 1]),
            ax=ax,
            labels=["Pointer xy boundary"],
            colors=["black"],
            linewidth=1.6,
            grid=False,
        )
        for index, name in enumerate(("sRGB", "Rec.2020")):
            xy = displays[name].xy_boundary()
            plot_lines(
                (xy[:, 0], xy[:, 1]),
                ax=ax,
                labels=[f"{name} primary hull"],
                colors=[COLOURS[name]],
                linestyles=[("-", "-.")[index]],
                linewidth=1.2,
                grid=False,
            )
        ax.legend(fontsize=7, loc="upper right")

        save_figure(fig, "06_pointer_gamut_comparison.png")


def main() -> None:
    pointer = pointer_gamut()
    displays = compute_example_boundaries()

    print("=" * 20 + " Pointer gamut " + "=" * 20)
    print(f"L* levels: {pointer.L_values}")
    print(f"hue values: {pointer.hue_values[0]:.0f}..{pointer.hue_values[-1]:.0f} step {pointer.hue_values[1] - pointer.hue_values[0]:.0f}")
    print(f"whitepoint XYZ: {pointer.whitepoint_XYZ}")
    print(f"Pointer Lab volume: {lab_gamut_volume(pointer):.2f}")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", UserWarning)
        for name in ("sRGB", "RGBC", "Rec.2020"):
            coverage = lab_gamut_coverage(displays[name], pointer)
            print(f"{name:8s} covers Pointer Lab volume: {coverage:.3f}")
    if caught:
        print("Coverage warnings: display and Pointer boundaries use different whitepoints/grids.")
    pointer_xy = pointer_gamut_published_xy_boundary()
    for name in ("sRGB", "Rec.2020"):
        coverage = xy_gamut_coverage_from_xy(displays[name].xy_boundary(), pointer_xy)
        print(f"{name:8s} covers Pointer xy boundary area: {coverage:.3f}")

    vertices = pointer.to_XYZ().reshape(-1, 3)
    sample = vertices[[0, 120, -1]]
    print(f"Pointer sample inside flags: {is_within_pointer_gamut(sample, tolerance=1e-7)}")
    print(f"Black inside Pointer: {bool(is_within_pointer_gamut([0.0, 0.0, 0.0], tolerance=1e-7))}")

    _plot_pointer_comparison(pointer, displays)


if __name__ == "__main__":
    main()
