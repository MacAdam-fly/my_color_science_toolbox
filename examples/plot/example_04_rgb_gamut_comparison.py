"""Compose RGB gamut comparison using low-level color.plot primitives."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.colorimetry import XYZ_to_xy
from color.plot import (
    plot_arrows,
    plot_cie1931_diagram,
    plot_labels,
    plot_points,
    plot_polygons,
)
from color.spaces import RGB_to_XYZ, get_RGB_colourspace


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _right_boundary_at_y(polygon: np.ndarray, y: float) -> np.ndarray:
    """Return the rightmost intersection between a horizontal line and a polygon."""
    intersections = []
    closed = np.vstack([polygon, polygon[0]])
    for start, end in zip(closed[:-1], closed[1:]):
        y0, y1 = start[1], end[1]
        if y < min(y0, y1) or y > max(y0, y1) or np.isclose(y0, y1):
            continue
        t = (y - y0) / (y1 - y0)
        if 0.0 <= t <= 1.0:
            x = start[0] + t * (end[0] - start[0])
            intersections.append(x)
    if not intersections:
        raise ValueError("label y position does not intersect the gamut polygon")
    return np.array([max(intersections), y])


def main() -> None:
    names = ("sRGB", "Display P3", "Rec.2020", "DCI-P3")
    colors = ("tab:blue", "tab:green", "tab:red", "tab:purple")
    label_x = 0.78
    label_y_positions = {
        "sRGB": 0.50,
        "Display P3": 0.56,
        "Rec.2020": 0.62,
        "DCI-P3": 0.68,
    }
    labels = []
    primary_points = []
    white_points = []
    polygons = []

    for name in names:
        space = get_RGB_colourspace(name)
        primaries_XYZ = RGB_to_XYZ(
            np.identity(3),
            colourspace=space,
            apply_decoding=False,
        )
        primaries_xy = XYZ_to_xy(primaries_XYZ)
        polygons.append(primaries_xy)
        labels.append(space.name)
        primary_points.append(primaries_xy)
        white_points.append(space.white_xy)

    fig, ax = plot_cie1931_diagram(
        title="RGB Gamut Comparison Composed From Primitives",
        show_background=True,
        background_samples=192,
        whitepoint_xy=None,
        show_wavelength_labels=True,
    )
    plot_polygons(
        polygons,
        ax=ax,
        labels=labels,
        edgecolors=colors,
        fill=False,
        linewidth=1.8,
        grid=False,
    )
    for primaries, white, color in zip(primary_points, white_points, colors):
        plot_points(primaries, ax=ax, colors=color, sizes=28, grid=False)
        plot_points([white], ax=ax, colors=color, markers="x", sizes=55, grid=False)
    for name, primaries, color in zip(labels, primary_points, colors):
        label_y = label_y_positions[name]
        target = _right_boundary_at_y(primaries, label_y)
        start = np.array([label_x - 0.02, label_y])
        plot_arrows(
            start,
            target,
            ax=ax,
            color=color,
            linewidth=1.0,
            mutation_scale=10.0,
            grid=False,
            alpha=0.75,
        )
        plot_labels(
            [[label_x, label_y]],
            [name],
            ax=ax,
            offset=(0, 0),
            fontsize=8,
            grid=False,
            bbox={"facecolor": "white", "alpha": 0.72, "edgecolor": "none", "pad": 1.5},
            color=color,
            ha="left",
            va="center",
        )
    ax.legend(loc="upper right", fontsize=8)
    _save(fig, _output_dir() / "04_rgb_gamut_comparison_composed.png")


if __name__ == "__main__":
    main()
