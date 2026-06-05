"""Compare default plotting style with presentation scaling variants."""

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

from color.plot import plot_lines, plot_points, plot_style
from color.plot import add_panel_labels


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _draw_panel(ax) -> None:
    x = np.linspace(0.0, 1.0, 120)
    y_1 = np.exp(-0.5 * ((x - 0.35) / 0.11) ** 2)
    y_2 = 0.75 * np.exp(-0.5 * ((x - 0.62) / 0.15) ** 2)
    points = np.array(
        [
            [0.20, 0.30],
            [0.42, 0.72],
            [0.68, 0.48],
            [0.86, 0.22],
        ],
        dtype=np.float64,
    )
    plot_lines(
        [(x, y_1), (x, y_2)],
        ax=ax,
        labels=("curve A", "curve B"),
        xlabel="x",
        ylabel="value",
    )
    plot_points(
        points,
        ax=ax,
        labels=("samples",),
        colors=("black",),
        sizes=28,
        grid=False,
        legend=False,
    )


def main() -> None:
    out = _output_dir()

    fig, axes = plt.subplots(2, 2, figsize=(8.8, 5.8))
    axes = axes.ravel()
    _draw_panel(axes[0])
    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        _draw_panel(axes[1])
    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        _draw_panel(axes[2])
    with plot_style("presentation"):
        _draw_panel(axes[3])

    add_panel_labels(axes, labels=("a", "b", "c", "d"), x=-0.10, y=1.03)

    _save(fig, out / "07_plot_style_comparison.png")


if __name__ == "__main__":
    main()
