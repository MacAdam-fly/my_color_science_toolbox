"""Recover a single-peak effective spectrum with Gaussian recovery."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import emission_to_XYZ
from color.plot import plot_lines, plot_style
from color.recovery import recover_spectrum_from_XYZ
from color.recovery.parametric import gaussian_spectrum
from color.spectra import SpectralDistribution, SpectralShape


def _output_dir() -> Path:
    output = Path(__file__).resolve().parent / "output"
    output.mkdir(exist_ok=True)
    return output


def _save_figure(fig, filename: str) -> None:
    output_path = _output_dir() / filename
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


def main() -> None:
    shape = SpectralShape(400, 700, 3)
    original = SpectralDistribution(
        shape.wavelengths,
        gaussian_spectrum(shape.wavelengths, 1.2, 540.0, 25.0),
        name="Original single Gaussian",
    )
    target_XYZ = emission_to_XYZ(original, shape=shape)
    recovered = recover_spectrum_from_XYZ(
        target_XYZ,
        method="gaussian",
        shape=shape,
    )
    closed_XYZ = emission_to_XYZ(recovered, shape=shape)

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("Closed XYZ:", np.round(closed_XYZ, 6))
    print("Relative closure error:", np.linalg.norm(closed_XYZ - target_XYZ) / np.linalg.norm(target_XYZ))
    print("Gaussian parameters:", recovered.metadata["gaussian_parameters"][0])
    print("Dominant region:", recovered.metadata.get("dominant_region"))
    print("Dominant wavelength initial used:", recovered.metadata.get("dominant_wavelength_initial_used"))

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            [
                (original.wavelengths, original.values),
                (recovered.wavelengths, recovered.values),
            ],
            ax=ax,
            labels=["original", "gaussian recovery"],
            linestyles=["-", "--"],
            linewidth=1.4,
            title="Single Gaussian Spectrum Recovery",
            xlabel="Wavelength (nm)",
            ylabel="Relative spectral value",
        )
        _save_figure(fig, "07_gaussian_spectrum_recovery.png")


if __name__ == "__main__":
    main()
