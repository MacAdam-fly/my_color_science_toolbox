"""Run a small ZCAM appearance-model workflow."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.appearance import XYZ_to_ZCAM, ZCAMSpecification, ZCAM_to_XYZ


XYZ = np.array([185.0, 206.0, 163.0])
XYZ_W = np.array([256.0, 264.0, 202.0])
L_A = 264.0
Y_B = 100.0


def main() -> None:
    print("ZCAM appearance correlates for one absolute XYZ stimulus")
    print(f"XYZ: {XYZ}")
    print()
    print("surround       J          C          h          M          V")
    print("-------------------------------------------------------------")
    for surround in ("Average", "Dim", "Dark"):
        spec = XYZ_to_ZCAM(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B, surround=surround)
        print(
            f"{surround:<9}"
            f"{spec.J:10.4f}"
            f"{spec.C:11.6f}"
            f"{spec.h:11.4f}"
            f"{spec.M:11.6f}"
            f"{spec.V:11.4f}"
        )

    spec = XYZ_to_ZCAM(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B)
    recovered = ZCAM_to_XYZ(
        ZCAMSpecification(J=spec.J, C=spec.C, h=spec.h),
        XYZ_W,
        L_A=L_A,
        Y_b=Y_B,
    )
    print()
    print(f"Roundtrip XYZ: {recovered}")
    print(f"Roundtrip max error: {np.max(np.abs(recovered - XYZ)):.3e}")


if __name__ == "__main__":
    main()
