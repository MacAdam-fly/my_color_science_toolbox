"""Run a small Hellwig2022 appearance-model workflow."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.appearance import Hellwig2022Specification, Hellwig2022_to_XYZ, XYZ_to_Hellwig2022
from color.appearance import XYZ_to_CIECAM16


XYZ = np.array([19.01, 20.0, 21.78])
XYZ_W = np.array([95.05, 100.0, 108.88])
L_A = 318.31
Y_B = 20.0


def main() -> None:
    print("Hellwig2022 appearance correlates for one XYZ stimulus")
    print(f"XYZ: {XYZ}")
    print()
    print("surround       J          C          h          M        J_HK")
    print("-------------------------------------------------------------")
    for surround in ("Average", "Dim", "Dark"):
        spec = XYZ_to_Hellwig2022(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B, surround=surround)
        print(
            f"{surround:<9}"
            f"{spec.J:10.4f}"
            f"{spec.C:11.6f}"
            f"{spec.h:11.4f}"
            f"{spec.M:11.6f}"
            f"{spec.J_HK:11.4f}"
        )

    hellwig = XYZ_to_Hellwig2022(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B)
    cam16 = XYZ_to_CIECAM16(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B)
    recovered = Hellwig2022_to_XYZ(
        Hellwig2022Specification(J=hellwig.J, C=hellwig.C, h=hellwig.h),
        XYZ_W,
        L_A=L_A,
        Y_b=Y_B,
    )
    print()
    print("Hellwig2022 vs CIECAM16 under the same viewing conditions")
    print(f"Hellwig2022 J/C/h: {hellwig.J:.6f}, {hellwig.C:.6f}, {hellwig.h:.6f}")
    print(f"CIECAM16    J/C/h: {cam16.J:.6f}, {cam16.C:.6f}, {cam16.h:.6f}")
    print()
    print(f"Roundtrip XYZ: {recovered}")
    print(f"Roundtrip max error: {np.max(np.abs(recovered - XYZ)):.3e}")


if __name__ == "__main__":
    main()
