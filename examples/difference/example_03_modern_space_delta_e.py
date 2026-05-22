"""Compare Oklab and Jzazbz coordinate distances."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.difference import delta_E, delta_E_Jzazbz, delta_E_Oklab
from color.spaces import convert_color


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
    oklab_reference = convert_color(SRGB_REFERENCE, "sRGB", "Oklab")
    oklab_sample = convert_color(SRGB_SAMPLE, "sRGB", "Oklab")
    jzazbz_reference = convert_color(SRGB_REFERENCE, "sRGB", "Jzazbz")
    jzazbz_sample = convert_color(SRGB_SAMPLE, "sRGB", "Jzazbz")

    print("Oklab and Jzazbz Delta E are direct coordinate distances")
    print("Oklab reference coordinates:")
    print(np.round(oklab_reference, 6))
    print("Jzazbz reference coordinates:")
    print(np.round(jzazbz_reference, 6))
    print()

    print_table(
        "Modern-space coordinate distances",
        [
            ("Oklab", delta_E_Oklab(oklab_reference, oklab_sample)),
            ("Jzazbz", delta_E_Jzazbz(jzazbz_reference, jzazbz_sample)),
            ("dispatch", delta_E(oklab_reference, oklab_sample, method="OKLAB")),
        ],
    )

    print("These values are not CIE Delta E standards; they are distances in their own spaces.")


if __name__ == "__main__":
    main()
