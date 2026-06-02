"""Compare static and formula-generated CIE Illuminant A with xyY."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _plot_helpers import (
    example_output_dir,
    print_xyY_table,
    xy_from_XYZ_rows,
)
from color.colorimetry import XYZ_to_xyY, emission_to_XYZ
from color.generators.illuminants import illuminant_a_spd
from color.plot import (
    plot_bars,
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_lines,
    plot_style,
)
from color.spectra import SpectralShape, from_columns, from_dataset


def main() -> None:
    output_dir = example_output_dir()
    shape = SpectralShape(360, 780, 1)
    dataset_a = from_dataset("illuminants", "A").align(shape)
    formula_a = from_columns(
        illuminant_a_spd(wavelength_nm=shape.wavelengths),
        y="spd",
        name="formula A",
    )

    xyz_dataset = emission_to_XYZ(dataset_a, shape=shape)
    xyz_formula = emission_to_XYZ(formula_a, shape=shape)
    xyz_rows = np.vstack([xyz_dataset, xyz_formula])
    labels = ["Dataset A", "Formula A"]
    xyy = XYZ_to_xyY(xyz_rows)
    xy_delta = xyy[1, :2] - xyy[0, :2]
    y_delta = xyy[1, 2] - xyy[0, 2]

    print_xyY_table("CIE Illuminant A comparison", labels, xyz_rows)
    print("Formula - dataset xy:", np.round(xy_delta, 10))
    print("Formula - dataset Y:", np.round(y_delta, 10))

    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 3, figsize=(15.2, 4.8))

        ax = axes[0]
        plot_lines(
            [
                (dataset_a.wavelengths, dataset_a.values),
                (formula_a.wavelengths, formula_a.values),
            ],
            ax=ax,
            labels=["dataset A", "formula A"],
            linestyles=["-", "--"],
            linewidth=2.0,
            title="CIE Illuminant A SPD",
            xlabel="Wavelength (nm)",
            ylabel="Relative SPD",
        )

        ax = axes[1]
        plot_cie1931_diagram(ax=ax, title="xy Agreement")
        plot_chromaticity_points(
            xy_from_XYZ_rows(xyz_rows),
            ax=ax,
            labels=labels,
            color="tab:orange",
        )
        ax.legend(loc="upper right", fontsize=8)

        ax = axes[2]
        delta = np.array([xy_delta[0], xy_delta[1], y_delta])
        ax.axhline(0.0, color="0.35", linewidth=1.0)
        plot_bars(
            delta,
            ax=ax,
            labels=("Delta x", "Delta y", "Delta Y"),
            colors="tab:blue",
            title="Formula - Dataset Difference",
        )

        fig.tight_layout()
        output_path = output_dir / "04_illuminant_a_comparison.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
