"""Recover effective spectra from XYZ and LMS responses."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import emission_to_LMS, emission_to_XYZ
from color.generators.ideal import gaussian_spd
from color.plot import plot_lines, plot_style
from color.recovery import (
    BoundedLeastSquaresOptions,
    recover_spectrum_from_LMS,
    recover_spectrum_from_XYZ,
)
from color.spectra import SpectralShape, from_columns


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
    shape = SpectralShape(400, 700, 1)
    raw = gaussian_spd(
        wavelength_nm=shape.wavelengths,
        peak_wavelength=545,
        width=35,
        method="normal",
    )
    original = from_columns(raw, y="spd", name="Gaussian effective spectrum")
    target_XYZ = emission_to_XYZ(original, shape=shape)
    target_LMS = emission_to_LMS(original, shape=shape)

    recovered_XYZ = recover_spectrum_from_XYZ(
        target_XYZ,
        shape=shape,
        method=BoundedLeastSquaresOptions(smoothness=1e-3),
    )
    recovered_LMS = recover_spectrum_from_LMS(
        target_LMS,
        shape=shape,
        method=BoundedLeastSquaresOptions(smoothness=1e-3),
    )

    closed_XYZ = emission_to_XYZ(recovered_XYZ, shape=shape)
    closed_LMS = emission_to_LMS(recovered_LMS, shape=shape)

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("Recovered spectrum closed XYZ:", np.round(closed_XYZ, 6))
    print("XYZ recovery error:", np.linalg.norm(closed_XYZ - target_XYZ))
    print("Target LMS:", np.round(target_LMS, 6))
    print("Recovered spectrum closed LMS:", np.round(closed_LMS, 6))
    print("LMS recovery error:", np.linalg.norm(closed_LMS - target_LMS))

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            [
                (original.wavelengths, original.values),
                (recovered_XYZ.wavelengths, recovered_XYZ.values),
                (recovered_LMS.wavelengths, recovered_LMS.values),
            ],
            ax=ax,
            labels=["original", "recovered from XYZ", "recovered from LMS"],
            linestyles=["-", "--", ":"],
            linewidth=1.4,
            title="Effective Spectrum Recovery",
            xlabel="Wavelength (nm)",
            ylabel="Relative spectral value",
        )
        _save_figure(fig, "02_spectrum_recovery.png")


if __name__ == "__main__":
    main()
