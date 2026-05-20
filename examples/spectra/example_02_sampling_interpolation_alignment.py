"""Sample, interpolate, trim, extrapolate and align spectral signals."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.spectra import SpectralDistribution, SpectralShape


def main() -> None:
    signal = SpectralDistribution(
        [400, 450, 500, 550, 600, 650, 700],
        [0.00, 0.12, 0.80, 0.92, 0.35, 0.10, 0.03],
        name="peaked signal",
    )
    targets = np.array([425, 475, 525, 575, 625], dtype=np.float64)

    print("domain alias:", signal.domain)
    print("range alias:", signal.range)
    print("sample([450, 550]):", signal.sample([450, 550], method="linear"))
    print("__call__([450, 550]):", signal([450, 550], method="auto"))

    print("\nInterpolation methods:")
    for method in ("nearest", "linear", "pchip", "sprague"):
        print(f"{method:>8}:", np.round(signal.sample(targets, method=method), 5))

    try:
        signal.interpolate([350, 450])
    except ValueError as error:
        print("\nDefault interpolation rejects out-of-domain samples:")
        print(" ", error)

    relaxed = signal.interpolate(
        [350, 400, 450, 725],
        bounds_error=False,
        fill_value=-1.0,
    )
    print("\ninterpolate(..., bounds_error=False, fill_value=-1):")
    print(np.column_stack((relaxed.wavelengths, relaxed.values)))

    reshape_shape = SpectralShape(400, 700, 25)
    trim_shape = SpectralShape(450, 600, 50)
    extrapolate_shape = SpectralShape(350, 750, 50)

    reshaped = signal.reshape(reshape_shape, method="pchip")
    trimmed = signal.trim(trim_shape)
    constant = signal.align(extrapolate_shape, interpolator="linear", extrapolator="constant")
    linear = signal.align(extrapolate_shape, interpolator="linear", extrapolator="linear")
    filled = signal.extrapolate(
        extrapolate_shape,
        interpolator="linear",
        method="fill",
        fill_value=0.0,
    )

    print("\nreshape shape:", reshaped.to_numpy().shape)
    print("trim domain:", trimmed.domain)
    print("constant extrapolation:", np.round(constant.values[[0, -1]], 5))
    print("linear extrapolation:", np.round(linear.values[[0, -1]], 5))
    print("fill extrapolation:", np.round(filled.values[[0, -1]], 5))


if __name__ == "__main__":
    main()
