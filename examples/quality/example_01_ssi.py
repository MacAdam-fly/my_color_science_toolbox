"""Demonstrate Academy Spectral Similarity Index (SSI)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.generators.leds import multi_led_spd
from color.quality import spectral_similarity_index
from color.spectra import from_D65_illuminant, from_columns


def _spectra():
    wavelengths = np.arange(360.0, 781.0, 1.0)
    return {
        "D65": from_D65_illuminant(),
        "three-peak LED": from_columns(
            multi_led_spd(
                wavelength_nm=wavelengths,
                peak_wavelengths=(455, 535, 615),
                half_spectral_widths=(18, 28, 22),
                peak_power_ratios=(1.0, 0.85, 0.65),
            ),
            y="spd",
            name="Three-peak LED",
        ),
        "Gaussian 555 nm": from_columns(
            gaussian_spd(
                wavelength_nm=wavelengths,
                peak_wavelength=555,
                width=45,
                method="fwhm",
            ),
            y="spd",
            name="Gaussian 555 nm",
        ),
        "Blackbody 6500 K": from_columns(
            blackbody_spd(wavelength_nm=wavelengths, temperature=6500),
            y="radiance",
            name="Blackbody 6500 K",
        ),
    }


def main() -> None:
    spectra = _spectra()
    reference = spectra["D65"]

    print("Academy Spectral Similarity Index (SSI)")
    print("Reference: CIE Standard Illuminant D65")
    print()
    print("source                 rounded    unrounded")
    print("-------------------------------------------")
    for name, sd in spectra.items():
        rounded = spectral_similarity_index(sd, reference)
        unrounded = spectral_similarity_index(sd, reference, round_result=False)
        print(f"{name:<22}{float(rounded):9.0f}{float(unrounded):14.6f}")

    print()
    print("SSI compares spectral similarity only; it is not CRI, TM-30 or CQS.")


if __name__ == "__main__":
    main()
