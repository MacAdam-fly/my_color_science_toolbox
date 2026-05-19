"""Compare static and formula-generated CIE Illuminant A in XYZ."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import XYZ_to_xyY, emission_to_XYZ
from color.generators.illuminants import illuminant_a_spd
from color.spectra import SpectralShape, from_columns, from_dataset


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    shape = SpectralShape(360, 780, 1)
    dataset_a = from_dataset("illuminants", "A").align(shape)
    formula_a = from_columns(
        illuminant_a_spd(wavelength_nm=shape.wavelengths),
        y="spd",
        name="formula A",
    )

    xyz_dataset = emission_to_XYZ(dataset_a, shape=shape)
    xyz_formula = emission_to_XYZ(formula_a, shape=shape)
    difference = xyz_formula - xyz_dataset
    xyy_dataset = XYZ_to_xyY(xyz_dataset)
    xyy_formula = XYZ_to_xyY(xyz_formula)

    print("CIE Illuminant A emission XYZ")
    print("Dataset:", np.round(xyz_dataset, 6))
    print("Formula:", np.round(xyz_formula, 6))
    print("Formula - dataset:", np.round(difference, 9))
    print("Dataset xyY:", np.round(xyy_dataset, 6))
    print("Formula xyY:", np.round(xyy_formula, 6))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))

    ax = axes[0]
    ax.plot(dataset_a.wavelengths, dataset_a.values, label="dataset A", linewidth=2.0)
    ax.plot(formula_a.wavelengths, formula_a.values, "--", label="formula A")
    ax.set_title("CIE Illuminant A SPD")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    x = np.arange(3)
    ax.bar(x - 0.18, xyz_dataset, width=0.36, label="dataset")
    ax.bar(x + 0.18, xyz_formula, width=0.36, label="formula")
    ax.set_title("Emission XYZ Comparison")
    ax.set_xticks(x, ("X", "Y", "Z"))
    ax.set_ylabel("Integrated response")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "illuminant_a_xyz_comparison.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
