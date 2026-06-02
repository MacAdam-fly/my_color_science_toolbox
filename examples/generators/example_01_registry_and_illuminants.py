"""Demonstrate generator registry access and common illuminant generators."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.generators import generate, list_generators
from color.generators.blackbody import blackbody_spd
from color.generators.illuminants import daylight_spd, illuminant_a_spd
from color.spectra import from_columns


def main() -> None:
    print("Blackbody generators:", list_generators("blackbody"))
    print("Illuminant generators:", list_generators("illuminants"))

    wavelengths = np.arange(400, 701, 10.0)

    blackbody = blackbody_spd(temperature=6500, wavelength_nm=wavelengths)
    blackbody_generated = generate(
        "blackbody",
        "blackbody_spd",
        temperature=6500,
        wavelength_nm=wavelengths,
    )

    illuminant_a = illuminant_a_spd(wavelength_nm=wavelengths)
    illuminant_a_generated = generate("illuminants", "A", wavelength_nm=wavelengths)

    daylight = daylight_spd(cct=5000, wavelength_nm=wavelengths)
    daylight_generated = generate(
        "illuminants",
        "cie_d_daylight",
        cct=5000,
        wavelength_nm=wavelengths,
    )

    blackbody_sd = from_columns(blackbody, y="radiance", name="blackbody 6500 K")
    blackbody_generated_sd = from_columns(
        blackbody_generated,
        y="radiance",
        name="blackbody 6500 K (generated)",
    )

    illuminant_a_sd = from_columns(illuminant_a, y="spd", name="CIE Illuminant A")
    illuminant_a_generated_sd = from_columns(
        illuminant_a_generated,
        y="spd",
        name="CIE Illuminant A (generated)",
    )

    daylight_sd = from_columns(daylight, y="spd", name="daylight 5000 K")
    daylight_generated_sd = from_columns(
        daylight_generated,
        y="spd",
        name="daylight 5000 K (generated)",
    )

    print("Blackbody samples:", blackbody_sd.to_numpy().shape)
    print("Generated blackbody samples:", blackbody_generated_sd.to_numpy().shape)

    print("Illuminant A samples:", illuminant_a_sd.to_numpy().shape)
    print("Generated Illuminant A samples:", illuminant_a_generated_sd.to_numpy().shape)

    print("Daylight samples:", daylight_sd.to_numpy().shape)
    print("Generated daylight samples:", daylight_generated_sd.to_numpy().shape)

    print("Daylight 5000 K first values:", daylight_sd.values[:5])


if __name__ == "__main__":
    main()
