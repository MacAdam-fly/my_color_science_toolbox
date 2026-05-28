"""Overview of low-level plotting primitives from color.plot."""

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

from color.plot import (
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_cie1960_ucs_diagram,
    plot_cie1976_ucs_diagram,
    plot_lines,
    plot_points,
    plot_swatch_strip,
)


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def _save_chromaticity_comparison(plotter, *, output_dir: Path, stem: str, title: str) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.6))
    plotter(ax=axes[0], title="No background", show_background=False)
    plotter(
        ax=axes[1],
        title="Approximate sRGB background",
        show_background=True,
        background_samples=160,
        background_alpha=1.0,
    )
    plotter(
        ax=axes[2],
        title="Background + wavelength labels",
        show_background=True,
        background_samples=160,
        background_alpha=1.0,
        show_wavelength_labels=True,
    )
    fig.suptitle(title)
    _save(fig, output_dir / f"{stem}_comparison.png")


def main() -> None:
    out = _output_dir()

    x = np.linspace(380.0, 780.0, 160)
    blue_peak = np.exp(-0.5 * ((x - 460.0) / 24.0) ** 2)
    green_peak = 0.7 * np.exp(-0.5 * ((x - 540.0) / 32.0) ** 2)
    red_peak = 0.9 * np.exp(-0.5 * ((x - 620.0) / 36.0) ** 2)
    fig, _ax = plot_lines(
        [(x, blue_peak), (x, green_peak), (x, red_peak)],
        labels=("blue component", "green component", "red component"),
        colors=("tab:blue", "tab:green", "tab:red"),
        title="Generic Line Primitive",
        xlabel="x",
        ylabel="relative value",
    )
    _save(fig, out / "01_lines.png")

    point_groups = (
        np.array([[0.30, 0.33], [0.36, 0.38], [0.42, 0.35]]),
        np.array([[0.18, 0.20], [0.22, 0.27], [0.28, 0.24]]),
    )
    fig, _ax = plot_points(
        point_groups,
        labels=("group A", "group B"),
        colors=("tab:orange", "tab:purple"),
        title="Generic Point Primitive",
        xlabel="x",
        ylabel="y",
    )
    _save(fig, out / "01_points.png")

    _save_chromaticity_comparison(
        plot_cie1931_diagram,
        output_dir=out,
        stem="01_cie1931_xy",
        title="CIE 1931 xy",
    )
    _save_chromaticity_comparison(
        plot_cie1960_ucs_diagram,
        output_dir=out,
        stem="01_cie1960_uv",
        title="CIE 1960 UCS uv",
    )
    _save_chromaticity_comparison(
        plot_cie1976_ucs_diagram,
        output_dir=out,
        stem="01_cie1976_upvp",
        title="CIE 1976 UCS u'v'",
    )

    fig, ax = plot_cie1931_diagram(show_background=True, background_samples=192)
    plot_chromaticity_points(
        [[0.3127, 0.3290], [0.3457, 0.3585], [0.2990, 0.3149]],
        ax=ax,
        labels=("D65", "D50", "D75"),
        color="black",
    )
    _save(fig, out / "01_chromaticity_points.png")

    fig, _ax = plot_swatch_strip(
        [[0.9, 0.15, 0.10], [0.15, 0.65, 0.25], [0.10, 0.35, 0.90]],
        labels=("sample 1", "sample 2", "sample 3"),
        title="sRGB Preview Swatches",
    )
    _save(fig, out / "01_swatch_strip.png")


if __name__ == "__main__":
    main()
