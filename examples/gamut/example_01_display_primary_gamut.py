"""Primary feasibility and primary-weight solving examples."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.gamut import DisplayPrimaries, is_within_primary_gamut, solve_primary_weights

from _example_helpers import rgbc_primaries


def main() -> None:
    sample_XYZ = np.array([20.0, 50.0, 10.0])
    print("=" * 20 + " primary feasibility " + "=" * 20)
    for name in ("sRGB", "Display P3", "Rec.2020"):
        primaries = DisplayPrimaries.from_RGB_colourspace(name)
        inside = is_within_primary_gamut(sample_XYZ, primaries)
        weights = solve_primary_weights(sample_XYZ, primaries)
        print(f"{name:10s} sample inside: {inside}, weights: {np.round(weights, 4)}")

    rgbc = rgbc_primaries()
    weights = np.array(
        [
            [0.2, 0.4, 0.6, 0.8],
            [0.8, 0.2, 0.4, 0.3],
        ],
        dtype=np.float64,
    )
    XYZ_batch = weights @ rgbc.primaries_XYZ
    inside = is_within_primary_gamut(XYZ_batch, rgbc)
    solved = solve_primary_weights(XYZ_batch[0], rgbc)

    print("=" * 20 + " multi-primary display " + "=" * 20)
    print("RGBC generated XYZ batch:")
    print(np.round(XYZ_batch, 4))
    print("RGBC batch inside:", inside)
    print("One feasible RGBC weight solution:", np.round(solved, 4))
    print("Original first weight vector:", weights[0])
    print("Multi-primary solutions are usually non-unique; linprog returns one feasible solution.")


if __name__ == "__main__":
    main()
