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
from color.spectra import SpectralDistribution


def _normalised_sd(raw: dict[str, np.ndarray], y: str, name: str) -> SpectralDistribution:
    values = np.asarray(raw[y], dtype=np.float64)
    scale = np.max(values)
    if scale == 0:
        raise ValueError(f"{name} has no positive values to normalise")
    return SpectralDistribution(raw["wavelength"], values / scale, name=name)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

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

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))

    ax = axes[0]
    ax.plot(photopic.wavelengths, photopic.values, label="Photopic V(lambda)")
    ax.plot(scotopic.wavelengths, scotopic.values, label="Scotopic V'(lambda)")
    ax.set_title("Luminous Efficiency Functions")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative response")
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    x = np.arange(len(spectra))
    photopic_values = [photopic_luminous_efficacy(sd) for sd in spectra]
    scotopic_values = [scotopic_luminous_efficacy(sd) for sd in spectra]
    width = 0.35
    ax.bar(x - width / 2, photopic_values, width=width, label="Photopic")
    ax.bar(x + width / 2, scotopic_values, width=width, label="Scotopic")
    ax.set_title("Luminous Efficacy of Example Spectra")
    ax.set_xticks(x, [sd.name for sd in spectra], rotation=20, ha="right")
    ax.set_ylabel("lm/W")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "photometry.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
