"""Run a small CIECAM02 appearance-model workflow."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.appearance import CIECAM02Specification, CIECAM02_to_XYZ, XYZ_to_CIECAM02


XYZ = np.array([19.01, 20.0, 21.78])
XYZ_W = np.array([95.05, 100.0, 108.88])
L_A = 318.31
Y_B = 20.0
CORRELATES = ("J", "C", "h", "s", "Q", "M", "H")


def main() -> None:
    print("CIECAM02 appearance correlates for one XYZ stimulus")
    print(f"XYZ: {XYZ}")
    print()
    print("surround       J          C          h          M          s")
    print("-------------------------------------------------------------")
    for surround in ("Average", "Dim", "Dark"):
        spec = XYZ_to_CIECAM02(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B, surround=surround)
        print(
            f"{surround:<9}"
            f"{spec.J:10.4f}"
            f"{spec.C:11.6f}"
            f"{spec.h:11.4f}"
            f"{spec.M:11.6f}"
            f"{spec.s:11.4f}"
        )

    spec = XYZ_to_CIECAM02(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B)
    recovered = CIECAM02_to_XYZ(
        CIECAM02Specification(J=spec.J, C=spec.C, h=spec.h),
        XYZ_W,
        L_A=L_A,
        Y_b=Y_B,
    )
    print()
    print(f"Roundtrip XYZ: {recovered}")
    print(f"Roundtrip max error: {np.max(np.abs(recovered - XYZ)):.3e}")


if __name__ == "__main__":
    main()
