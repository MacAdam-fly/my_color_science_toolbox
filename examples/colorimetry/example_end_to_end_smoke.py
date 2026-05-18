"""End-to-end smoke checks for datasets, generators, spectra and colorimetry."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.colorimetry import (
    emission_to_lms,
    emission_to_xyz,
    reflectance_to_lms,
    reflectance_to_xyz,
)
from color.generators.ideal import equal_energy_spd
from color.spectra import SpectralDistribution, SpectralShape, from_columns, from_dataset


def main() -> None:
    shape = SpectralShape(400, 700, 5)

    cmfs = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm").align(shape)
    fundamentals = from_dataset(
        "standard_observers.cone_fundamentals",
        "cie2006_lms2_linE_1nm",
        fill_nan=0.0,
    ).align(shape)
    illuminant = from_dataset("illuminants", "D65").align(shape)

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

    xyz_reflectance = reflectance_to_xyz(
        perfect_reflector,
        illuminant,
        cmfs,
        shape=shape,
    )
    lms_reflectance = reflectance_to_lms(
        perfect_reflector,
        illuminant,
        fundamentals,
        shape=shape,
    )
    xyz_emission = emission_to_xyz(equal_energy, cmfs, shape=shape)
    lms_emission = emission_to_lms(equal_energy, fundamentals, shape=shape)

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
