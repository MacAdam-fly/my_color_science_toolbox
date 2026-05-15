"""Minimal CAM02 conversion using QMh output."""

from color.core import ColorContext
from color.constants.illuminants import D65_XYZ
from color.spaces import convert


def main() -> None:
    context = ColorContext(
        white_point=D65_XYZ,
        background_xyz=D65_XYZ,
        adapting_luminance=100.0,
        surround="AVERAGE",
    )

    xyz = [19.01, 20.0, 21.78]
    qmh = convert(xyz, "xyz", "cam02", context=context)
    xyz_round = convert(qmh, "cam02", "xyz", context=context)

    print("XYZ -> CAM02 QMh:", qmh)
    print("CAM02 QMh -> XYZ:", xyz_round) 


if __name__ == "__main__":
    main()
