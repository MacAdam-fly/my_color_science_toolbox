"""Compare single and multi-Gaussian recovery for a two-peak spectrum."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import emission_to_XYZ
from color.plot import plot_bars, plot_lines, plot_style
from color.recovery import (
    GaussianRecoveryOptions,
    MultiGaussianRecoveryOptions,
    recover_spectrum_from_XYZ,
)
from color.recovery.parametric import multi_gaussian_spectrum
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


def _relative_error(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b) / np.linalg.norm(b))


def main() -> None:
    shape = SpectralShape(400, 700, 3)
    original = SpectralDistribution(
        shape.wavelengths,
        multi_gaussian_spectrum(
            shape.wavelengths,
            [0.9, 0.7],
            [440.0, 640.0],
            [22.0, 30.0],
        ),
        name="Original two-peak spectrum",
    )
    target_XYZ = emission_to_XYZ(original, shape=shape)
    single = recover_spectrum_from_XYZ(
        target_XYZ,
        method=GaussianRecoveryOptions(),
        shape=shape,
    )
    multi = recover_spectrum_from_XYZ(
        target_XYZ,
        method=MultiGaussianRecoveryOptions(n_components=2),
        shape=shape,
    )
    errors = {
        "single": _relative_error(emission_to_XYZ(single, shape=shape), target_XYZ),
        "multi": _relative_error(emission_to_XYZ(multi, shape=shape), target_XYZ),
    }

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("Relative closure errors:", errors)
    print("Multi-Gaussian parameters:", multi.metadata["gaussian_parameters"][0])

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.2))
        plot_lines(
            [
                (original.wavelengths, original.values),
                (single.wavelengths, single.values),
                (multi.wavelengths, multi.values),
            ],
            ax=axes[0],
            labels=["original", "single Gaussian", "multi Gaussian"],
            linestyles=["-", "--", ":"],
            linewidth=1.4,
            title="Two-Peak Spectrum Recovery",
            xlabel="Wavelength (nm)",
            ylabel="Relative spectral value",
        )
        plot_bars(
            list(errors.values()),
            ax=axes[1],
            labels=list(errors.keys()),
            title="XYZ Closure Error",
            ylabel="Relative error",
        )
        _save_figure(fig, "08_multi_gaussian_spectrum_recovery.png")


if __name__ == "__main__":
    main()
