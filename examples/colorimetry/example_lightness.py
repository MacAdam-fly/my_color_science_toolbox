"""Convert relative luminance Y to CIE 1976 L* and back."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.colorimetry import Lstar_to_Y, Y_to_Lstar


def main() -> None:
    Y = np.array([0.0, 1.0, 5.0, 18.0, 50.0, 100.0])
    Lstar = Y_to_Lstar(Y)
    Y_roundtrip = Lstar_to_Y(Lstar)

    print("Y:", np.round(Y, 6))
    print("L*:", np.round(Lstar, 6))
    print("Round-trip OK:", np.allclose(Y_roundtrip, Y))
    print("Y from L*:", np.round(Y_roundtrip, 6))


if __name__ == "__main__":
    main()
