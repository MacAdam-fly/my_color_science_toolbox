"""Convert relative luminance Y to CIE 1976 L* and back."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import Lstar_to_Y, Y_to_Lstar
from color.plot import plot_labels, plot_lines, plot_points, plot_style
from _plot_helpers import example_output_dir


def main() -> None:
    output_dir = example_output_dir()

    Y = np.array([0.0, 1.0, 5.0, 18.0, 50.0, 100.0])
    Lstar = Y_to_Lstar(Y)
    Y_roundtrip = Lstar_to_Y(Lstar)

    print("Y:", np.round(Y, 6))
    print("L*:", np.round(Lstar, 6))
    print("Round-trip OK:", np.allclose(Y_roundtrip, Y))
    print("Y from L*:", np.round(Y_roundtrip, 6))

    dense_Y = np.linspace(0.0, 100.0, 256)
    dense_Lstar = Y_to_Lstar(dense_Y)

    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, ax = plt.subplots(figsize=(7.2, 4.8))
        plot_lines(
            (dense_Y, dense_Lstar),
            ax=ax,
            colors="tab:blue",
            linewidth=2.0,
            title="CIE 1976 Lightness",
            xlabel="Relative luminance Y",
            ylabel="L*",
        )
        points = np.column_stack([Y, Lstar])
        plot_points(points, ax=ax, colors="tab:orange", sizes=48)
        plot_labels(points, [f"{value:g}" for value in Y], ax=ax, grid=False)

        fig.tight_layout()
        output_path = output_dir / "07_lightness.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
