"""Generate blackbody and daylight spectral data."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.generators import generate, list_generators
from color.generators.illuminants import blackbody_spd, daylight_spd
from color.spectra import from_columns


def main() -> None:
    print("Illuminant generators:", list_generators("illuminants"))

    wavelengths = np.arange(400, 701, 10.0)
    blackbody = blackbody_spd(temperature=6500, wavelength_nm=wavelengths)
    daylight = generate("illuminants", "daylight", cct=5000, wavelength_nm=wavelengths)

    blackbody_sd = from_columns(blackbody, y="radiance", name="blackbody 6500 K")
    daylight_sd = from_columns(daylight, y="spd", name="daylight 5000 K")

    print("Blackbody samples:", blackbody_sd.to_numpy().shape)
    print("Daylight samples:", daylight_sd.to_numpy().shape)
    print("D50 first values:", daylight_sd.values[:5])


if __name__ == "__main__":
    main()
