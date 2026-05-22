"""Compare standard Lab colour-difference formulas."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.constants import D65_XYZ
from color.difference import (
    delta_E,
    delta_E_CIE1976,
    delta_E_CIE1994,
    delta_E_CIE2000,
    delta_E_CMC,
)
from color.spaces import SpaceSpec, convert_color


LAB_REFERENCE = np.array(
    [
        [50.0000, 2.6772, -79.7751],
        [50.0000, 3.1571, -77.2803],
        [50.0000, 2.8361, -74.0200],
    ],
    dtype=np.float64,
)
LAB_SAMPLE = np.array(
    [
        [50.0000, 0.0000, -82.7485],
        [50.0000, 0.0000, -82.7485],
        [50.0000, 0.0000, -82.7485],
    ],
    dtype=np.float64,
)

SRGB_REFERENCE = np.array(
    [
        [0.72, 0.12, 0.10],
        [0.12, 0.54, 0.18],
        [0.14, 0.24, 0.82],
    ],
    dtype=np.float64,
)
SRGB_SAMPLE = np.array(
    [
        [0.75, 0.15, 0.12],
        [0.10, 0.50, 0.22],
        [0.18, 0.28, 0.78],
    ],
    dtype=np.float64,
)


def print_table(title: str, rows: list[tuple[str, np.ndarray]]) -> None:
    print(title)
    for name, values in rows:
        print(f"{name:>10}: {np.round(values, 6)}")
    print()


def main() -> None:
    print_table(
        "Delta E for Lab coordinates that are already in the same Lab space",
        [
            ("CIE 1976", delta_E_CIE1976(LAB_REFERENCE, LAB_SAMPLE)),
            ("CIE 1994", delta_E_CIE1994(LAB_REFERENCE, LAB_SAMPLE)),
            ("CIE 2000", delta_E_CIE2000(LAB_REFERENCE, LAB_SAMPLE)),
            ("CMC 2:1", delta_E_CMC(LAB_REFERENCE, LAB_SAMPLE)),
            ("CMC 1:1", delta_E_CMC(LAB_REFERENCE, LAB_SAMPLE, l=1, c=1)),
        ],
    )

    lab_spec = SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ)
    lab_from_srgb_reference = convert_color(SRGB_REFERENCE, "sRGB", lab_spec)
    lab_from_srgb_sample = convert_color(SRGB_SAMPLE, "sRGB", lab_spec)

    print("sRGB samples converted to D65 Lab before colour-difference calculation")
    print("Reference Lab:")
    print(np.round(lab_from_srgb_reference, 6))
    print("Sample Lab:")
    print(np.round(lab_from_srgb_sample, 6))
    print()

    print_table(
        "Delta E after explicit sRGB -> Lab conversion",
        [
            ("CIE 1976", delta_E(lab_from_srgb_reference, lab_from_srgb_sample, method="CIE 1976")),
            ("CIE 1994", delta_E(lab_from_srgb_reference, lab_from_srgb_sample, method="CIE 1994")),
            ("CIE 2000", delta_E(lab_from_srgb_reference, lab_from_srgb_sample, method="CIEDE2000")),
            ("CMC 2:1", delta_E(lab_from_srgb_reference, lab_from_srgb_sample, method="CMC")),
        ],
    )


if __name__ == "__main__":
    main()
