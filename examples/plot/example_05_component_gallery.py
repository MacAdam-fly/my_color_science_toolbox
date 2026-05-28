"""Small gallery for plot components not covered by the overview example."""

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

from color.constants import D50_XYZ, D65_XYZ
from color.plot import (
    chromaticity_background_image,
    colour_cycle,
    plot_arrows,
    plot_bars,
    plot_image,
    plot_labels,
    plot_points,
    plot_segments,
    plot_style,
    plot_swatch_grid,
    preview_sRGB_from_XYZ,
    set_axis_limits_from_data,
)


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _swatch_grid_from_xyz(out: Path) -> None:
    xyz_samples = np.array(
        [
            D65_XYZ,
            D50_XYZ,
            [35.0, 24.0, 6.0],
            [18.0, 22.0, 70.0],
        ],
        dtype=np.float64,
    )
    dimmed_xyz_samples = xyz_samples * 0.35

    preview = preview_sRGB_from_XYZ(xyz_samples)
    dimmed_preview = preview_sRGB_from_XYZ(dimmed_xyz_samples)
    preview_from_y1 = preview_sRGB_from_XYZ(xyz_samples / 100.0, white_Y=1.0)

    fig, _ax = plot_swatch_grid(
        (
            ("Y=100 XYZ", preview),
            ("dimmed XYZ", dimmed_preview),
            ("Y=1 input", preview_from_y1),
        ),
        title="sRGB Preview Grid from XYZ",
    )
    _save(fig, out / "05_swatch_grid_from_xyz.png")


def _bar_component(out: Path) -> None:
    values = np.array(
        [
            [1.2, 2.8, 1.6, 3.4],
            [1.6, 2.1, 2.4, 2.8],
        ],
        dtype=np.float64,
    )
    colours = colour_cycle("journal")
    journal_colours = tuple(next(colours) for _ in range(2))
    with plot_style("journal"):
        fig, _ax = plot_bars(
            values,
            labels=("sample A", "sample B", "sample C", "sample D"),
            group_labels=("metric 1", "metric 2"),
            colors=journal_colours,
            title="Grouped Bar Primitive with Journal Style",
            ylabel="relative value",
        )
    _save(fig, out / "05_bars_journal_style.png")


def _axis_limits_and_annotations(out: Path) -> None:
    points = np.array(
        [
            [0.18, 0.22],
            [0.30, 0.50],
            [0.52, 0.40],
            [0.43, 0.16],
        ],
        dtype=np.float64,
    )
    labels = ("A", "B", "C", "D")
    segments = np.array(
        [
            [[0.18, 0.22], [0.30, 0.50]],
            [[0.30, 0.50], [0.52, 0.40]],
            [[0.52, 0.40], [0.43, 0.16]],
        ],
        dtype=np.float64,
    )
    arrow_starts = points[:-1]
    arrow_ends = points[1:]

    fig, ax = plot_points(
        points,
        colors="tab:blue",
        sizes=48,
        title="Composed Points, Segments, Arrows and Labels",
        xlabel="x",
        ylabel="y",
        legend=False,
    )
    plot_segments(segments, ax=ax, colors="0.45", linewidth=1.2, grid=False, legend=False)
    plot_arrows(
        arrow_starts,
        arrow_ends,
        ax=ax,
        color="tab:orange",
        linewidth=1.1,
        mutation_scale=12.0,
        grid=False,
    )
    plot_labels(
        points,
        labels,
        ax=ax,
        offset=(6.0, 6.0),
        fontsize=9,
        bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "0.8", "alpha": 0.9},
        grid=False,
    )
    set_axis_limits_from_data(ax, np.concatenate([points, segments.reshape(-1, 2)], axis=0), padding=0.18)
    _save(fig, out / "05_axis_limits_and_annotations.png")


def main() -> None:
    out = _output_dir()
    _swatch_grid_from_xyz(out)
    _bar_component(out)
    _axis_limits_and_annotations(out)


if __name__ == "__main__":
    main()
