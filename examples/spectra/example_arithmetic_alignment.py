"""Align two spectral objects before arithmetic."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralDistribution, SpectralShape


def main() -> None:
    illuminant_like = SpectralDistribution(
        [400, 500, 600, 700],
        [0.4, 1.0, 0.8, 0.2],
        name="relative illuminant",
    )
    reflectance = SpectralDistribution(
        [420, 520, 620],
        [0.1, 0.7, 0.4],
        name="reflectance",
    )

    shape = SpectralShape(420, 620, 20)
    aligned_illuminant = illuminant_like.reshape(shape, method="linear")
    aligned_reflectance = reflectance.reshape(shape, method="linear")
    reflected = aligned_illuminant * aligned_reflectance

    print("Aligned domain:", reflected.domain)
    print("Reflected signal:", reflected.range)


if __name__ == "__main__":
    main()
