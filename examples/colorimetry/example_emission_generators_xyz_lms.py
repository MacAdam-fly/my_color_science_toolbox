"""Convert generated self-luminous spectra to XYZ and LMS."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import emission_to_LMS, emission_to_XYZ
from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.generators.illuminants import daylight_spd
from color.generators.leds import multi_led_spd
from color.spectra import SpectralDistribution, SpectralShape, from_columns, from_dataset


def _normalised_sd(raw: dict[str, np.ndarray], y: str, name: str) -> SpectralDistribution:
    values = np.asarray(raw[y], dtype=np.float64)
    scale = np.max(values)
    if scale == 0:
        raise ValueError(f"{name} has no positive values to normalise")
    return SpectralDistribution(raw["wavelength"], values / scale, name=name)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    shape = SpectralShape(400, 700, 5)
    spectra = [
        _normalised_sd(
            blackbody_spd(temperature=6500),
            "radiance",
            "Blackbody 6500 K",
        ),
        _normalised_sd(daylight_spd(cct=6500), "spd", "CIE D daylight 6500 K"),
        _normalised_sd(
            gaussian_spd(peak_wavelength=555, width=35, method="fwhm"),
            "spd",
            "Ideal Gaussian 555 nm",
        ),
        _normalised_sd(
            multi_led_spd(
                peak_wavelengths=(457, 530, 615),
                half_spectral_widths=(20, 30, 20),
                peak_power_ratios=(0.731, 1.0, 1.66),
            ),
            "spd",
            "RGB LED mixture",
        ),
    ]
    spectra = [sd.align(shape) for sd in spectra]

    fundamentals = from_dataset(
        "standard_observers.cone_fundamentals",
        "cie2006_lms2_linE_1nm",
        fill_nan=0.0,
    ).align(shape)

    xyz = np.vstack([emission_to_XYZ(sd, shape=shape) for sd in spectra])
    lms = np.vstack(
        [
            emission_to_LMS(sd, fundamentals=fundamentals, shape=shape)
            for sd in spectra
        ]
    )
    names = [sd.name for sd in spectra]

    print("Generated emission spectra:")
    for name, xyz_row, lms_row in zip(names, xyz, lms):
        print(f"{name}: XYZ={np.round(xyz_row, 4)} LMS={np.round(lms_row, 4)}")

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

    ax = axes[0]
    for sd in spectra:
        ax.plot(sd.wavelengths, sd.values, label=sd.name)
    ax.set_title("Normalised Emission Spectra")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Relative SPD")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    x = np.arange(len(names))
    width = 0.24
    ax = axes[1]
    for offset, label in zip((-width, 0, width), ("X", "Y", "Z")):
        ax.bar(x + offset, xyz[:, ("X", "Y", "Z").index(label)], width, label=label)
    ax.set_title("Emission to XYZ")
    ax.set_xticks(x, names, rotation=25, ha="right")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    ax = axes[2]
    for offset, label in zip((-width, 0, width), fundamentals.labels):
        ax.bar(x + offset, lms[:, fundamentals.labels.index(label)], width, label=label)
    ax.set_title("Emission to LMS")
    ax.set_xticks(x, names, rotation=25, ha="right")
    ax.legend()
    ax.grid(True, axis="y", alpha=0.3)

    fig.tight_layout()
    output_path = output_dir / "emission_generators_xyz_lms.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
