"""Create spectral objects from datasets, column mappings and arrays."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_columns,
    from_dataset,
)


def main() -> None:
    d65 = from_dataset("illuminants", "D65")
    cmfs = from_dataset("standard_observers.cmfs", "CIE 1931 XYZ 1 nm")

    raw_single = {
        "wavelength": np.array([400.0, 500.0, 600.0]),
        "reflectance": np.array([0.12, 0.45, 0.31]),
    }
    reflectance = from_columns(raw_single, y="reflectance", name="sample reflectance")

    raw_multi = {
        "wavelength": np.array([400.0, 500.0, 600.0]),
        "R": np.array([0.8, 0.5, 0.2]),
        "G": np.array([0.1, 0.7, 0.3]),
        "B": np.array([0.0, 0.2, 0.9]),
    }
    sensitivities = from_columns(
        raw_multi,
        ys=("R", "G", "B"),
        name="RGB sensitivities",
    )

    direct_sd = SpectralDistribution(
        [400, 500, 600],
        [0.0, 1.0, 0.2],
        name="direct single-channel signal",
    )
    direct_msd = MultiSpectralDistribution(
        [400, 500, 600],
        [[0.1, 0.0], [0.8, 0.4], [0.2, 0.9]],
        ("A", "B"),
        name="direct multi-channel signal",
    )

    print("from_dataset single:", type(d65).__name__, d65.name, d65.values.shape)
    print("from_dataset multi:", type(cmfs).__name__, cmfs.labels, cmfs.values.shape)
    print("from_columns y=... returns:", type(reflectance).__name__)
    print("from_columns ys=(...) returns:", type(sensitivities).__name__, sensitivities.labels)
    print("Direct objects:", type(direct_sd).__name__, type(direct_msd).__name__)

    visible_shape = SpectralShape(400, 700, 10)
    d65_visible = d65.reshape(visible_shape)
    print("D65 reshaped first rows:")
    for wavelength, value in zip(d65_visible.wavelengths[:4], d65_visible.values[:4]):
        print(f"  {wavelength:.0f} nm -> {value:.4f}")


if __name__ == "__main__":
    main()
