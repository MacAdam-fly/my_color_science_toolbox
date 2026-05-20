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
    annotate_xy_points,
    example_output_dir,
    plot_xy_locus,
    print_xyY_table,
    xy_from_XYZ_rows,
)
from color.colorimetry import XYZ_to_xyY, emission_to_XYZ
from color.generators.illuminants import illuminant_a_spd
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

    fig, axes = plt.subplots(1, 3, figsize=(15.2, 4.8))

    ax = axes[0]
    ax.plot(dataset_a.wavelengths, dataset_a.values, label="dataset A", linewidth=2.0)
    ax.plot(formula_a.wavelengths, formula_a.values, "--", label="formula A")
    ax.set_title("CIE Illuminant A SPD")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    plot_xy_locus(ax, title="xy Agreement")
    annotate_xy_points(ax, xy_from_XYZ_rows(xyz_rows), labels, color="tab:orange")
    ax.legend(loc="upper right", fontsize=8)

    ax = axes[2]
    delta = np.array([xy_delta[0], xy_delta[1], y_delta])
    x = np.arange(3)
    ax.axhline(0.0, color="0.35", linewidth=1.0)
    ax.bar(x, delta, color=["tab:blue", "tab:blue", "tab:green"], alpha=0.8)
    ax.set_title("Formula - Dataset Difference")
    ax.set_xticks(x, ("Delta x", "Delta y", "Delta Y"))
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "04_illuminant_a_comparison.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
