"""End-to-end smoke checks for datasets, generators, spectra and colorimetry."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.colorimetry import (
    emission_to_LMS,
    emission_to_XYZ,
    reflectance_to_LMS,
    reflectance_to_XYZ,
)
from color.generators.ideal import equal_energy_spd
from color.spectra import SpectralDistribution, SpectralShape, from_columns


def main() -> None:
    shape = SpectralShape(400, 700, 5)

    perfect_reflector = SpectralDistribution(
        shape.wavelengths,
        np.ones(len(shape)),
        name="perfect reflector",
    )
    equal_energy = from_columns(
        equal_energy_spd(wavelength_nm=shape.wavelengths),
        y="spd",
        name="equal energy",
    )

    xyz_reflectance = reflectance_to_XYZ(
        perfect_reflector,
        shape=shape,
    )
    lms_reflectance = reflectance_to_LMS(
        perfect_reflector,
        shape=shape,
    )
    
    xyz_emission = emission_to_XYZ(equal_energy, shape=shape)
    lms_emission = emission_to_LMS(equal_energy, shape=shape)

    assert xyz_reflectance.shape == (3,)
    assert lms_reflectance.shape == (3,)
    assert xyz_emission.shape == (3,)
    assert lms_emission.shape == (3,)
    assert np.isclose(xyz_reflectance[1], 100.0)
    assert np.all(np.isfinite(xyz_reflectance))
    assert np.all(np.isfinite(lms_reflectance))
    assert np.all(np.isfinite(xyz_emission))
    assert np.all(np.isfinite(lms_emission))

    print("End-to-end smoke checks passed.")
    print("Perfect reflector XYZ under D65:", np.round(xyz_reflectance, 6))
    print("Perfect reflector LMS under D65:", np.round(lms_reflectance, 6))
    print("Equal-energy emission XYZ:", np.round(xyz_emission, 6))
    print("Equal-energy emission LMS:", np.round(lms_emission, 6))


if __name__ == "__main__":
    main()
