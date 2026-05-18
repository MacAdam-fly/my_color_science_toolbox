"""Compare extrapolation strategies."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.spectra import SpectralDistribution, SpectralShape


def main() -> None:
    sd = SpectralDistribution([400, 500, 600], [0.0, 1.0, 0.2], name="signal")
    shape = SpectralShape(350, 650, 50)

    constant = sd.align(shape, interpolator="linear", extrapolator="constant")
    linear = sd.align(shape, interpolator="linear", extrapolator="linear")
    filled = sd.extrapolate(
        shape,
        interpolator="linear",
        method="fill",
        fill_value=-1.0,
    )
    clamped = sd.align(
        shape,
        interpolator="linear",
        extrapolator="constant",
        left=0.0,
        right=0.0,
    )

    print("Wavelengths:", shape.wavelengths)
    print("Constant:", constant.values)
    print("Linear:", linear.values)
    print("Fill:", filled.values)
    print("Explicit left/right:", clamped.values)


if __name__ == "__main__":
    main()
