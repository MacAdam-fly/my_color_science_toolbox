"""Plot photopic and scotopic LEFs and compare luminous efficacy."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import (
    photopic_luminous_efficacy,
    photopic_luminous_efficiency_function,
    scotopic_luminous_efficacy,
    scotopic_luminous_efficiency_function,
)
from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.generators.illuminants import daylight_spd
from color.plot import plot_bars, plot_lines, plot_style
from color.spectra import SpectralDistribution
from _plot_helpers import example_output_dir


def _normalised_sd(raw: dict[str, np.ndarray], y: str, name: str) -> SpectralDistribution:
    values = np.asarray(raw[y], dtype=np.float64)
    scale = np.max(values)
    if scale == 0:
        raise ValueError(f"{name} has no positive values to normalise")
    return SpectralDistribution(raw["wavelength"], values / scale, name=name)


def main() -> None:
    output_dir = example_output_dir()

    photopic = photopic_luminous_efficiency_function(name="cie2008_v10_linE_1nm")
    scotopic = scotopic_luminous_efficiency_function()

    spectra = [
        _normalised_sd(blackbody_spd(temperature=2856), "radiance", "Blackbody 2856 K"),
        _normalised_sd(daylight_spd(cct=6500), "spd", "Daylight 6500 K"),
        _normalised_sd(
            gaussian_spd(peak_wavelength=507, width=30, method="fwhm"),
            "spd",
            "Gaussian 507 nm",
        ),
    ]

    print("Luminous efficacy comparison")
    for sd in spectra:
        photopic_eta = photopic_luminous_efficacy(sd)
        scotopic_eta = scotopic_luminous_efficacy(sd)
        print(
            f"{sd.name}: photopic={photopic_eta:.3f} lm/W, "
            f"scotopic={scotopic_eta:.3f} lm/W"
        )

    with plot_style("journal_double"):
        fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

        ax = axes[0]
        plot_lines(
            [
                (photopic.wavelengths, photopic.values),
                (scotopic.wavelengths, scotopic.values),
            ],
            ax=ax,
            labels=["Photopic V(lambda)", "Scotopic V'(lambda)"],
            title="Luminous Efficiency Functions",
            xlabel="Wavelength (nm)",
            ylabel="Relative response",
        )

        ax = axes[1]
        photopic_values = [photopic_luminous_efficacy(sd) for sd in spectra]
        scotopic_values = [scotopic_luminous_efficacy(sd) for sd in spectra]
        plot_bars(
            [photopic_values, scotopic_values],
            ax=ax,
            labels=[sd.name for sd in spectra],
            group_labels=["Photopic", "Scotopic"],
            title="Luminous Efficacy of Example Spectra",
            ylabel="lm/W",
        )
        ax.tick_params(axis="x", labelrotation=20)

        fig.tight_layout()
        output_path = output_dir / "06_photometry.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
