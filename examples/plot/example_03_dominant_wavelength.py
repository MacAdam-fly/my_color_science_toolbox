"""Compose dominant-wavelength analysis using low-level color.plot primitives."""

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

from color.colorimetry.dominant import analyze_chromaticity
from color.plot import plot_chromaticity_points, plot_cie1931_diagram, plot_segments


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {path}")


def main() -> None:
    sample_xy = np.array([0.54369557, 0.32107944])
    white_xy = np.array([0.3127, 0.3290])
    analysis = analyze_chromaticity(sample_xy, xy_n=white_xy)

    fig, ax = plot_cie1931_diagram(
        title="Dominant Wavelength Analysis Composed From Primitives",
        show_background=True,
        background_samples=192,
        whitepoint_xy=None,
        show_wavelength_labels=True,
    )
    plot_segments(
        [
            [[white_xy, sample_xy], [sample_xy, analysis.dominant_xy]],
            [[white_xy, analysis.complementary_xy]],
        ],
        ax=ax,
        labels=("dominant direction", "complementary direction"),
        colors=("tab:red", "tab:purple"),
        linestyles=("-", "--"),
        grid=False,
    )
    plot_chromaticity_points(
        [white_xy, sample_xy, analysis.dominant_xy, analysis.complementary_xy],
        ax=ax,
        labels=(
            "white",
            "sample",
            f"{analysis.wavelength:.1f} nm",
            f"{analysis.complementary_wavelength:.1f} nm",
        ),
        color="black",
        sizes=28,
    )
    ax.legend(loc="upper right", fontsize=8)
    ax.text(
        0.03,
        0.06,
        f"Pe={analysis.excitation_purity:.3f}\nPc={analysis.colorimetric_purity:.3f}",
        transform=ax.transAxes,
        fontsize=9,
        bbox={"facecolor": "white", "alpha": 0.75, "edgecolor": "none"},
    )
    _save(fig, _output_dir() / "03_dominant_wavelength_composed.png")


if __name__ == "__main__":
    main()
