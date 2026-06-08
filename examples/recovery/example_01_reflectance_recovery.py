"""Recover bounded smooth reflectance spectra from XYZ and xyY values."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import XYZ_to_xyY, reflectance_to_XYZ
from color.datasets.color_cards import get_color_card
from color.plot import plot_lines, plot_style
from color.recovery import (
    BoundedLeastSquaresOptions,
    Burns2019RecoveryOptions,
    recover_reflectance_from_XYZ,
    recover_reflectance_from_xyY,
)
from color.spectra import from_columns


def _output_dir() -> Path:
    output = Path(__file__).resolve().parent / "output"
    output.mkdir(exist_ok=True)
    return output


def _save_figure(fig, filename: str) -> Path:
    output_path = _output_dir() / filename
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")
    return output_path


def main() -> None:
    raw = get_color_card("macbeth")
    original = from_columns(raw, y="Blue Sky", name="Macbeth Blue Sky")
    target_XYZ = reflectance_to_XYZ(original, illuminant="D65")
    target_xyY = XYZ_to_xyY(target_XYZ)

    recovered_XYZ = recover_reflectance_from_XYZ(
        target_XYZ,
        method=BoundedLeastSquaresOptions(smoothness=1e-3),
        illuminant="D65",
    )
    recovered_xyY = recover_reflectance_from_xyY(
        target_xyY,
        method=BoundedLeastSquaresOptions(smoothness=1e-3),
        illuminant="D65",
    )
    recovered_burns = recover_reflectance_from_XYZ(
        target_XYZ,
        method=Burns2019RecoveryOptions(),
        illuminant="D65",
    )

    closed_XYZ = reflectance_to_XYZ(recovered_XYZ, illuminant="D65")
    closed_xyY_XYZ = reflectance_to_XYZ(recovered_xyY, illuminant="D65")
    closed_burns_XYZ = reflectance_to_XYZ(recovered_burns, illuminant="D65")

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("Recovered-from-XYZ closed XYZ:", np.round(closed_XYZ, 6))
    print("Recovered-from-xyY closed XYZ:", np.round(closed_xyY_XYZ, 6))
    print("Burns 2019 closed XYZ:", np.round(closed_burns_XYZ, 6))
    print("XYZ recovery error:", np.linalg.norm(closed_XYZ - target_XYZ))
    print("xyY recovery error:", np.linalg.norm(closed_xyY_XYZ - target_XYZ))
    print("Burns 2019 recovery error:", np.linalg.norm(closed_burns_XYZ - target_XYZ))
    print("Burns 2019 transform:", recovered_burns.metadata["reflectance_transform"])

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            [
                (original.wavelengths, original.values),
                (recovered_XYZ.wavelengths, recovered_XYZ.values),
                (recovered_xyY.wavelengths, recovered_xyY.values),
                (recovered_burns.wavelengths, recovered_burns.values),
            ],
            ax=ax,
            labels=["original", "recovered from XYZ", "recovered from xyY", "Burns 2019"],
            linestyles=["-", "--", ":", "-."],
            linewidth=1.4,
            title="Reflectance Recovery",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        _save_figure(fig, "01_reflectance_recovery.png")


if __name__ == "__main__":
    main()
