"""Cached MacAdam optimal colour stimuli limits."""

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

from color.gamut import (
    is_within_macadam_limits,
    lab_gamut_coverage,
    lab_gamut_volume,
    macadam_limits,
    macadam_limits_published_xy_boundary,
    pointer_gamut,
)
from color.plot import plot_cie1931_diagram, plot_style

from _example_helpers import COLOURS, compute_example_boundaries, save_figure


def _plot_macadam_comparison(macadam_d65, pointer, displays) -> None:
    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 2, figsize=(8.6, 4.1), constrained_layout=True)

        ax = axes[0]
        plot_cie1931_diagram(
            ax=ax,
            show_background=True,
            background_samples=192,
            title="MacAdam Published xy Limits",
        )
        for illuminant, color in (("A", "#D55E00"), ("C", "#0072B2"), ("D65", "#009E73")):
            xy = macadam_limits_published_xy_boundary(illuminant)
            ax.plot(xy[:, 0], xy[:, 1], linewidth=1.4, color=color, label=f"MacAdam {illuminant}")
        ax.legend(fontsize=7, loc="upper right")

        ax = axes[1]
        for name in ("sRGB", "Rec.2020"):
            ab = displays[name].projected_ab_boundary()
            ax.plot(ab[:, 0], ab[:, 1], color=COLOURS[name], linewidth=1.1, label=name)
        pointer_ab = pointer.projected_ab_boundary()
        ax.plot(pointer_ab[:, 0], pointer_ab[:, 1], color="black", linewidth=1.2, label="Pointer")
        macadam_ab = macadam_d65.projected_ab_boundary()
        ax.plot(macadam_ab[:, 0], macadam_ab[:, 1], color="#009E73", linewidth=1.5, label="MacAdam D65")
        ax.set_title("Projected Lab a*b* Boundaries")
        ax.set_xlabel("a*")
        ax.set_ylabel("b*")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, alpha=0.25)
        ax.legend(fontsize=7)

        save_figure(fig, "07_macadam_limits_comparison.png")


def main() -> None:
    displays = compute_example_boundaries()
    pointer = pointer_gamut()
    macadam_d65 = macadam_limits(
        "D65",
        L_values=np.arange(0.0, 101.0, 5.0),
        hue_values=np.arange(0.0, 361.0, 5.0),
        C_upper=300.0,
        iterations=10,
    )

    print("=" * 20 + " MacAdam limits " + "=" * 20)
    print(f"D65 published vertices: {macadam_d65.vertices_XYZ.shape[0]}")

    print(f"MacAdam D65 Lab volume: {lab_gamut_volume(macadam_d65):.2f}")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", UserWarning)
        for name in ("sRGB", "Rec.2020"):
            coverage = lab_gamut_coverage(displays[name], macadam_d65)
            print(f"{name:8s} covers MacAdam D65 Lab volume: {coverage:.3f}")
        pointer_coverage = lab_gamut_coverage(pointer, macadam_d65)
        print(f"{'Pointer':8s} covers MacAdam D65 Lab volume: {pointer_coverage:.3f}")
    if caught:
        print("Coverage warnings: some boundaries use different whitepoints or grids.")

    samples = np.vstack((macadam_d65.vertices_XYZ[[0, 20, -1]], [[0.0, 0.0, 0.0]]))
    print(f"Sample inside MacAdam D65: {is_within_macadam_limits(samples, 'D65', tolerance=1e-7)}")

    _plot_macadam_comparison(macadam_d65, pointer, displays)


if __name__ == "__main__":
    main()
