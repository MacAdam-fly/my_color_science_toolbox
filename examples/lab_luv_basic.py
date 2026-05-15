"""Minimal Lab/Luv conversions via XYZ."""

from color_agent.core import ColorContext
from color_agent.constants.illuminants import D65_XYZ
from color_agent.spaces import convert


def main() -> None:
    context = ColorContext(white_point=D65_XYZ)

    lab = [41.24, 21.26, 1.93]
    xyz = convert(lab, "lab", "xyz", context=context)
    lab_round = convert(xyz, "xyz", "lab", context=context)

    luv = convert(xyz, "xyz", "luv", context=context)
    xyz_round = convert(luv, "luv", "xyz", context=context)

    print("Lab -> XYZ:", xyz)
    print("XYZ -> Lab:", lab_round)
    print("XYZ -> Luv:", luv)
    print("Luv -> XYZ:", xyz_round)


if __name__ == "__main__":
    main()
