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


def _compare_with_colour() -> None:
    try:
        from colour.appearance import CIECAM02_to_XYZ as colour_CIECAM02_to_XYZ
        from colour.appearance import XYZ_to_CIECAM02 as colour_XYZ_to_CIECAM02
        from colour.appearance import CAM_Specification_CIECAM02
    except ImportError:
        print("colour-science is not installed; skipping reference comparison.")
        return

    ours = XYZ_to_CIECAM02(XYZ, XYZ_W, L_A=L_A, Y_b=Y_B)
    reference = colour_XYZ_to_CIECAM02(XYZ, XYZ_W, L_A, Y_B)

    print()
    print("Comparison with colour.appearance")
    print("correlate        ours          colour         abs diff")
    print("------------------------------------------------------")
    for name in CORRELATES:
        ours_value = float(getattr(ours, name))
        reference_value = float(getattr(reference, name))
        print(
            f"{name:<9}"
            f"{ours_value:14.8f}"
            f"{reference_value:14.8f}"
            f"{abs(ours_value - reference_value):14.3e}"
        )

    ours_xyz = CIECAM02_to_XYZ(
        CIECAM02Specification(J=ours.J, C=ours.C, h=ours.h),
        XYZ_W,
        L_A=L_A,
        Y_b=Y_B,
    )
    reference_xyz = colour_CIECAM02_to_XYZ(
        CAM_Specification_CIECAM02(J=reference.J, C=reference.C, h=reference.h),
        XYZ_W,
        L_A,
        Y_B,
    )

    print()
    print(f"Our inverse XYZ:      {ours_xyz}")
    print(f"colour inverse XYZ:   {reference_xyz}")
    print(f"Inverse max diff:     {np.max(np.abs(ours_xyz - reference_xyz)):.3e}")


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
    _compare_with_colour()


if __name__ == "__main__":
    main()
