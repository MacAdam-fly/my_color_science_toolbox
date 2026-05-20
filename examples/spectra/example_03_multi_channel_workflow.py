"""Work with multi-channel spectral objects."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.datasets import get_color_card
from color.spectra import SpectralShape, from_columns, from_dataset


def main() -> None:
    cmfs = from_dataset("standard_observers.cmfs", "CIE 1931 XYZ 1 nm")
    coarse_cmfs = cmfs.reshape(SpectralShape(400, 700, 25), method="linear")
    y_bar = coarse_cmfs.channel("Y")

    print("CMF object:", type(cmfs).__name__)
    print("CMF labels:", cmfs.labels)
    print("Coarse CMF values shape:", coarse_cmfs.values.shape)
    print("Y-bar samples at 450/550/650 nm:", np.round(y_bar([450, 550, 650]), 6))

    raw = get_color_card("pmc")
    patch_names = ("Caucasian", "Carrot", "Blue Sky")
    pmc = from_columns(
        raw,
        x="wavelength",
        ys=patch_names,
        name="PMC selected patches",
        metadata={"dataset": "pmc", "quantity": "spectral_reflectance"},
    )
    pmc_1nm = pmc.reshape(
        SpectralShape(float(pmc.wavelengths[0]), float(pmc.wavelengths[-1]), 1.0),
        method="pchip",
    )
    blue_sky = pmc_1nm.channel("Blue Sky")

    print("\nPMC labels:", pmc.labels)
    print("PMC source shape:", pmc.values.shape)
    print("PMC 1 nm shape:", pmc_1nm.values.shape)
    print("Blue Sky channel type:", type(blue_sky).__name__)
    print("Blue Sky sample at 500 nm:", np.round(blue_sky([500.0], method="pchip")[0], 5))


if __name__ == "__main__":
    main()
