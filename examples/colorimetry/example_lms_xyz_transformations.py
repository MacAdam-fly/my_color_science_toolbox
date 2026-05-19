"""Convert CIE 2006 LMS values to XYZ and back."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.colorimetry import LMS_to_XYZ, XYZ_to_LMS


def main() -> None:
    LMS = np.array([
        [0.2, 0.3, 0.4],
        [0.5, 0.4, 0.1],
    ])

    XYZ = LMS_to_XYZ(LMS, observer=2)
    LMS_roundtrip = XYZ_to_LMS(XYZ, observer=2)

    print("LMS:")
    print(np.round(LMS, 6))
    print("XYZ:")
    print(np.round(XYZ, 6))
    print("Round-trip OK:", np.allclose(LMS_roundtrip, LMS))


if __name__ == "__main__":
    main()
