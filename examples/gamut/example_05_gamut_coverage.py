"""xy area and Lab volume coverage comparisons."""

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

from color.gamut import (
    lab_gamut_coverage,
    lab_gamut_volume,
    xy_gamut_coverage,
)
from color.gamut.coverage import xy_gamut_area
from color.plot import plot_style

from _example_helpers import compute_example_boundaries, rgbc_primaries, save_figure


def _coverage_matrix(names, objects, coverage_fn) -> np.ndarray:
    """Return directional coverage matrix: row covers column."""
    matrix = np.empty((len(names), len(names)), dtype=np.float64)
    for row, test_name in enumerate(names):
        for column, reference_name in enumerate(names):
            matrix[row, column] = coverage_fn(objects[test_name], objects[reference_name])
    return matrix


def _print_matrix(title: str, names, matrix: np.ndarray) -> None:
    """Print a compact coverage matrix."""
    print("\n" + title)
    print("test \\ reference".ljust(16) + "".join(name.rjust(10) for name in names))
    for name, row in zip(names, matrix):
        print(name.ljust(16) + "".join(f"{value:10.3f}" for value in row))


def _plot_matrix(ax, title: str, names, matrix: np.ndarray) -> None:
    """Plot a coverage matrix heatmap."""
    image = ax.imshow(matrix, vmin=0.0, vmax=1.0, cmap="viridis")
    ax.set_title(title)
    ax.set_xticks(np.arange(len(names)), labels=names, rotation=30, ha="right")
    ax.set_yticks(np.arange(len(names)), labels=names)
    ax.set_xlabel("reference gamut")
    ax.set_ylabel("test gamut")
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            value = matrix[row, column]
            color = "white" if value < 0.5 else "black"
            ax.text(column, row, f"{value:.2f}", ha="center", va="center", color=color, fontsize=7)
    return image


def main() -> None:
    names = ("sRGB", "RGBC", "Rec.2020")
    primaries = {
        "sRGB": "sRGB",
        "RGBC": rgbc_primaries(),
        "Rec.2020": "Rec.2020",
    }
    boundaries = compute_example_boundaries()

    xy_matrix = _coverage_matrix(names, primaries, xy_gamut_coverage)
    lab_matrix = _coverage_matrix(names, boundaries, lab_gamut_coverage)

    print("=" * 20 + " gamut coverage " + "=" * 20)
    for name in names:
        print(f"{name:8s} xy area: {xy_gamut_area(primaries[name]):.6f}")
        print(f"{name:8s} Lab volume: {lab_gamut_volume(boundaries[name]):.2f}")
    _print_matrix("xy area coverage: test covers reference", names, xy_matrix)
    _print_matrix("Lab volume coverage: test covers reference", names, lab_matrix)

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(1, 2, figsize=(7.16, 3.2), constrained_layout=True)
        image = _plot_matrix(axes[0], "xy area coverage", names, xy_matrix)
        _plot_matrix(axes[1], "Lab volume coverage", names, lab_matrix)
        fig.colorbar(image, ax=axes, shrink=0.82, label="coverage")
        fig.suptitle("Directional Gamut Coverage")
        save_figure(fig, "05_gamut_coverage_matrices.png")


if __name__ == "__main__":
    main()
