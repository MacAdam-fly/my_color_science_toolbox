"""Demonstrate auto Gaussian strategy selection for XYZ spectrum recovery."""

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
from color.recovery.parametric import gaussian_spectrum, multi_gaussian_spectrum
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


def _targets(shape: SpectralShape) -> list[SpectralDistribution]:
    return [
        SpectralDistribution(
            shape.wavelengths,
            gaussian_spectrum(shape.wavelengths, 1.0, 530.0, 30.0),
            name="spectral dominant target",
        ),
        SpectralDistribution(
            shape.wavelengths,
            multi_gaussian_spectrum(shape.wavelengths, [0.9, 0.7], [440.0, 640.0], [22.0, 30.0]),
            name="purple direction target",
        ),
        SpectralDistribution(
            shape.wavelengths,
            np.ones_like(shape.wavelengths),
            name="E target",
        ),
    ]


def main() -> None:
    shape = SpectralShape(400, 700, 3)
    originals = _targets(shape)
    recovered = []
    for original in originals:
        target_XYZ = emission_to_XYZ(original, shape=shape)
        spectrum = recover_spectrum_from_XYZ(
            target_XYZ,
            method="auto_gaussian",
            shape=shape,
            n_components=3,
        )
        recovered.append(spectrum)
        print(original.name)
        print("  selected:", spectrum.metadata["selected_parametric_method"])
        print("  reason:", spectrum.metadata.get("selection_reason"))
        print("  dominant region:", spectrum.metadata.get("dominant_region"))

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.8), sharey=True)
        for ax, original, spectrum in zip(axes, originals, recovered):
            selected = spectrum.metadata["selected_parametric_method"]
            plot_lines(
                [
                    (original.wavelengths, original.values),
                    (spectrum.wavelengths, spectrum.values),
                ],
                ax=ax,
                labels=["target", selected],
                linestyles=["-", "--"],
                linewidth=1.3,
                title=selected.replace("_", " "),
                xlabel="Wavelength (nm)",
                ylabel="Relative spectral value",
            )
        _save_figure(fig, "09_auto_gaussian_spectrum_recovery.png")


if __name__ == "__main__":
    main()
