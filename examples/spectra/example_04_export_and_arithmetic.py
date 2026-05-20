"""Export spectral objects and use explicit alignment before arithmetic."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.spectra import SpectralDistribution, SpectralShape, from_dataset


def main() -> None:
    d65 = from_dataset("illuminants", "D65")
    subset = d65.reshape(SpectralShape(400, 700, 20))

    raw = subset.to_dict()
    array = subset.to_numpy()
    frame = subset.to_pandas()

    print("Export formats")
    print("  dict keys:", list(raw.keys()))
    print("  numpy shape:", array.shape)
    print("  pandas columns:", list(frame.columns))
    print("  first pandas row:", frame.iloc[0].to_dict())

    scaled = subset * 0.5
    shifted = scaled + 1.0
    print("\nScalar arithmetic")
    print("  scaled first values:", np.round(scaled.values[:3], 5))
    print("  shifted first values:", np.round(shifted.values[:3], 5))

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
    try:
        illuminant_like * reflectance
    except ValueError as error:
        print("\nObject arithmetic requires matching domains:")
        print(" ", error)

    aligned_illuminant = illuminant_like.reshape(shape, method="linear")
    aligned_reflectance = reflectance.reshape(shape, method="linear")
    reflected = aligned_illuminant * aligned_reflectance

    print("Aligned domain:", reflected.domain)
    print("Reflected signal:", np.round(reflected.range, 5))


if __name__ == "__main__":
    main()
