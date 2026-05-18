"""Convert image-like XYZ arrays to xyY and xy chromaticity."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.colorimetry import XYZ_to_xy, XYZ_to_xyY, xyY_to_XYZ


def main() -> None:
    XYZ = np.array([
        [
            [95.047, 100.0, 108.883],
            [41.24, 21.26, 1.93],
        ],
        [
            [10.0, 20.0, 30.0],
            [0.1, 0.2, 0.3],
        ],
    ])

    xyY = XYZ_to_xyY(XYZ)
    xy = XYZ_to_xy(XYZ)
    XYZ_roundtrip = xyY_to_XYZ(xyY)

    print("XYZ shape:", XYZ.shape)
    print("xyY shape:", xyY.shape)
    print("xy shape:", xy.shape)
    print("Round-trip OK:", np.allclose(XYZ_roundtrip, XYZ))
    print("First pixel XYZ:", np.round(XYZ[0, 0], 6))
    print("First pixel xyY:", np.round(xyY[0, 0], 6))
    print("First pixel xy:", np.round(xy[0, 0], 6))


if __name__ == "__main__":
    main()
