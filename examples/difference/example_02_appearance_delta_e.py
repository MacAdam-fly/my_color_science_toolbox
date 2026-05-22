"""Compare CAM02/CAM16 appearance-uniform colour differences."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.difference import (
    delta_E,
    delta_E_CAM02LCD,
    delta_E_CAM02SCD,
    delta_E_CAM02UCS,
    delta_E_CAM16LCD,
    delta_E_CAM16SCD,
    delta_E_CAM16UCS,
)
from color.spaces import SpaceSpec, convert_color


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
    cam02_ucs_reference = convert_color(SRGB_REFERENCE, "sRGB", "CAM02-UCS")
    cam02_ucs_sample = convert_color(SRGB_SAMPLE, "sRGB", "CAM02-UCS")
    cam02_lcd_reference = convert_color(SRGB_REFERENCE, "sRGB", "CAM02-LCD")
    cam02_lcd_sample = convert_color(SRGB_SAMPLE, "sRGB", "CAM02-LCD")
    cam02_scd_reference = convert_color(SRGB_REFERENCE, "sRGB", "CAM02-SCD")
    cam02_scd_sample = convert_color(SRGB_SAMPLE, "sRGB", "CAM02-SCD")

    cam16_ucs_reference = convert_color(SRGB_REFERENCE, "sRGB", "CAM16-UCS")
    cam16_ucs_sample = convert_color(SRGB_SAMPLE, "sRGB", "CAM16-UCS")
    cam16_lcd_reference = convert_color(SRGB_REFERENCE, "sRGB", "CAM16-LCD")
    cam16_lcd_sample = convert_color(SRGB_SAMPLE, "sRGB", "CAM16-LCD")
    cam16_scd_reference = convert_color(SRGB_REFERENCE, "sRGB", "CAM16-SCD")
    cam16_scd_sample = convert_color(SRGB_SAMPLE, "sRGB", "CAM16-SCD")

    print("CAM16-UCS reference coordinates:")
    print(np.round(cam16_ucs_reference, 6))
    print("CAM16-UCS sample coordinates:")
    print(np.round(cam16_ucs_sample, 6))
    print()

    print_table(
        "CAM02 appearance-uniform Delta E",
        [
            ("CAM02-UCS", delta_E_CAM02UCS(cam02_ucs_reference, cam02_ucs_sample)),
            ("CAM02-LCD", delta_E_CAM02LCD(cam02_lcd_reference, cam02_lcd_sample)),
            ("CAM02-SCD", delta_E_CAM02SCD(cam02_scd_reference, cam02_scd_sample)),
        ],
    )

    print_table(
        "CAM16 appearance-uniform Delta E",
        [
            ("CAM16-UCS", delta_E_CAM16UCS(cam16_ucs_reference, cam16_ucs_sample)),
            ("CAM16-LCD", delta_E_CAM16LCD(cam16_lcd_reference, cam16_lcd_sample)),
            ("CAM16-SCD", delta_E_CAM16SCD(cam16_scd_reference, cam16_scd_sample)),
            ("dispatch", delta_E(cam16_ucs_reference, cam16_ucs_sample, method="CAM16UCS")),
        ],
    )

    dim_cam16_spec = SpaceSpec("CAM16-UCS", surround="Dim")
    dim_reference = convert_color(SRGB_REFERENCE, "sRGB", dim_cam16_spec)
    dim_sample = convert_color(SRGB_SAMPLE, "sRGB", dim_cam16_spec)
    print_table(
        "Viewing conditions are selected during spaces conversion",
        [
            ("Average", delta_E_CAM16UCS(cam16_ucs_reference, cam16_ucs_sample)),
            ("Dim", delta_E_CAM16UCS(dim_reference, dim_sample)),
        ],
    )


if __name__ == "__main__":
    main()
