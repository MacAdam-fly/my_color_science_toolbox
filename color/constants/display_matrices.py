"""Display RGB colour-space constants."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any

import numpy as np


def _readonly_matrix(values: list[list[float]]) -> np.ndarray:
    """Return a read-only RGB-to-XYZ matrix using the Y=100 XYZ scale."""
    matrix = 100.0 * np.array(values, dtype=float)
    matrix.setflags(write=False)
    return matrix


def _readonly_inverse(matrix: np.ndarray) -> np.ndarray:
    """Return a read-only inverse matrix."""
    inverse = np.linalg.inv(matrix)
    inverse.setflags(write=False)
    return inverse


def _rgb_definition(
    *,
    name: str,
    aliases: tuple[str, ...],
    primaries: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    white_xy: tuple[float, float],
    white_name: str,
    transfer: str,
    matrix_RGB_to_XYZ: np.ndarray,
    reference: str,
) -> MappingProxyType[str, Any]:
    """Return an immutable RGB colour-space definition mapping."""
    return MappingProxyType(
        {
            "name": name,
            "aliases": aliases,
            "primaries": primaries,
            "white_xy": white_xy,
            "white_name": white_name,
            "transfer": transfer,
            "matrix_RGB_to_XYZ": matrix_RGB_to_XYZ,
            "matrix_XYZ_to_RGB": _readonly_inverse(matrix_RGB_to_XYZ),
            "reference": reference,
        }
    )


# sRGB, IEC 61966-2-1, D65.
SRGB_TO_XYZ = _readonly_matrix(
    [
        [0.4124, 0.3576, 0.1805],
        [0.2126, 0.7152, 0.0722],
        [0.0193, 0.1192, 0.9505],
    ]
)
XYZ_TO_SRGB = _readonly_inverse(SRGB_TO_XYZ)

# ITU-R BT.709, D65. Same primaries as sRGB but a different transfer function.
REC709_TO_XYZ = _readonly_matrix(
    [
        [0.41239079926595934, 0.357584339383878, 0.1804807884018343],
        [0.21263900587151027, 0.715168678767756, 0.07219231536073371],
        [0.01933081871559182, 0.11919477979462599, 0.9505321522496607],
    ]
)
XYZ_TO_REC709 = _readonly_inverse(REC709_TO_XYZ)

# ITU-R BT.2020 / Rec.2020, D65.
REC2020_TO_XYZ = _readonly_matrix(
    [
        [0.6369580483012914, 0.14461690358620832, 0.1688809751641721],
        [0.2627002120112671, 0.6779980715188708, 0.05930171646986196],
        [0.0, 0.028072693049087428, 1.060985057710791],
    ]
)
XYZ_TO_REC2020 = _readonly_inverse(REC2020_TO_XYZ)

# Adobe RGB (1998), D65.
ADOBE_RGB_TO_XYZ = _readonly_matrix(
    [
        [0.57667, 0.18556, 0.18823],
        [0.29734, 0.62736, 0.07529],
        [0.02703, 0.07069, 0.99134],
    ]
)
XYZ_TO_ADOBE_RGB = _readonly_inverse(ADOBE_RGB_TO_XYZ)

# Display P3 / P3-D65.
DISPLAY_P3_TO_XYZ = _readonly_matrix(
    [
        [0.4865709486482162, 0.26566769316909306, 0.1982172852343625],
        [0.2289745640697488, 0.6917385218365064, 0.079286914093745],
        [0.0, 0.04511338185890264, 1.043944368900976],
    ]
)
XYZ_TO_DISPLAY_P3 = _readonly_inverse(DISPLAY_P3_TO_XYZ)

# DCI-P3, theatrical white xy=(0.314, 0.351).
DCIP3_TO_XYZ = _readonly_matrix(
    [
        [0.4451698155645523, 0.2771344092067778, 0.17228266981556453],
        [0.2094916779127312, 0.7215952541610446, 0.06891306792622578],
        [0.0, 0.04706056005398175, 0.9073553943616049],
    ]
)
XYZ_TO_DCIP3 = _readonly_inverse(DCIP3_TO_XYZ)

# NTSC (1953), Illuminant C.
NTSC_1953_TO_XYZ = _readonly_matrix(
    [
        [0.6068638092693974, 0.17350728093347247, 0.20033488079528077],
        [0.2989030695782824, 0.5866198546593291, 0.11447707576238854],
        [0.0, 0.06609801177817278, 1.116151484519807],
    ]
)
XYZ_TO_NTSC_1953 = _readonly_inverse(NTSC_1953_TO_XYZ)


RGB_COLOURSPACE_DEFINITIONS = MappingProxyType(
    {
        "sRGB": _rgb_definition(
            name="sRGB",
            aliases=("srgb", "IEC 61966-2-1"),
            primaries=((0.6400, 0.3300), (0.3000, 0.6000), (0.1500, 0.0600)),
            white_xy=(0.3127, 0.3290),
            white_name="D65",
            transfer="srgb",
            matrix_RGB_to_XYZ=SRGB_TO_XYZ,
            reference="IEC 61966-2-1 / colour.models.RGB_COLOURSPACES['sRGB']",
        ),
        "Rec.709": _rgb_definition(
            name="Rec.709",
            aliases=("rec709", "BT.709", "ITU-R BT.709"),
            primaries=((0.6400, 0.3300), (0.3000, 0.6000), (0.1500, 0.0600)),
            white_xy=(0.3127, 0.3290),
            white_name="D65",
            transfer="bt709",
            matrix_RGB_to_XYZ=REC709_TO_XYZ,
            reference="ITU-R BT.709 / colour.models.RGB_COLOURSPACES['ITU-R BT.709']",
        ),
        "Display P3": _rgb_definition(
            name="Display P3",
            aliases=("display-p3", "DisplayP3", "P3-D65"),
            primaries=((0.6800, 0.3200), (0.2650, 0.6900), (0.1500, 0.0600)),
            white_xy=(0.3127, 0.3290),
            white_name="D65",
            transfer="srgb",
            matrix_RGB_to_XYZ=DISPLAY_P3_TO_XYZ,
            reference="Display P3 / colour.models.RGB_COLOURSPACES['Display P3']",
        ),
        "DCI-P3": _rgb_definition(
            name="DCI-P3",
            aliases=("dcip3", "DCI P3"),
            primaries=((0.6800, 0.3200), (0.2650, 0.6900), (0.1500, 0.0600)),
            white_xy=(0.3140, 0.3510),
            white_name="DCP white",
            transfer="gamma_2p6",
            matrix_RGB_to_XYZ=DCIP3_TO_XYZ,
            reference="DCI-P3 / colour.models.RGB_COLOURSPACES['DCI-P3']",
        ),
        "Rec.2020": _rgb_definition(
            name="Rec.2020",
            aliases=("rec2020", "BT.2020", "ITU-R BT.2020"),
            primaries=((0.7080, 0.2920), (0.1700, 0.7970), (0.1310, 0.0460)),
            white_xy=(0.3127, 0.3290),
            white_name="D65",
            transfer="bt2020",
            matrix_RGB_to_XYZ=REC2020_TO_XYZ,
            reference="ITU-R BT.2020 / colour.models.RGB_COLOURSPACES['ITU-R BT.2020']",
        ),
        "Adobe RGB (1998)": _rgb_definition(
            name="Adobe RGB (1998)",
            aliases=("adobe-rgb-1998", "AdobeRGB1998", "Adobe RGB"),
            primaries=((0.6400, 0.3300), (0.2100, 0.7100), (0.1500, 0.0600)),
            white_xy=(0.3127, 0.3290),
            white_name="D65",
            transfer="adobe_rgb_1998",
            matrix_RGB_to_XYZ=ADOBE_RGB_TO_XYZ,
            reference="Adobe RGB (1998) / colour.models.RGB_COLOURSPACES['Adobe RGB (1998)']",
        ),
        "NTSC (1953)": _rgb_definition(
            name="NTSC (1953)",
            aliases=("ntsc-1953", "NTSC_1953"),
            primaries=((0.6700, 0.3300), (0.2100, 0.7100), (0.1400, 0.0800)),
            white_xy=(0.31006, 0.31616),
            white_name="C",
            transfer="gamma_2p8",
            matrix_RGB_to_XYZ=NTSC_1953_TO_XYZ,
            reference="NTSC (1953) / colour.models.RGB_COLOURSPACES['NTSC (1953)']",
        ),
    }
)

# Backwards-compatible registry names with the new field structure.
RGB_GAMUT_METADATA = RGB_COLOURSPACE_DEFINITIONS

COMMON_GAMUTS = MappingProxyType(
    {
        "sRGB": {"to_xyz": SRGB_TO_XYZ, "from_xyz": XYZ_TO_SRGB},
        "Rec709": {"to_xyz": REC709_TO_XYZ, "from_xyz": XYZ_TO_REC709},
        "Rec2020": {"to_xyz": REC2020_TO_XYZ, "from_xyz": XYZ_TO_REC2020},
        "AdobeRGB1998": {"to_xyz": ADOBE_RGB_TO_XYZ, "from_xyz": XYZ_TO_ADOBE_RGB},
        "DisplayP3": {"to_xyz": DISPLAY_P3_TO_XYZ, "from_xyz": XYZ_TO_DISPLAY_P3},
        "DCI-P3": {"to_xyz": DCIP3_TO_XYZ, "from_xyz": XYZ_TO_DCIP3},
        "NTSC_1953": {"to_xyz": NTSC_1953_TO_XYZ, "from_xyz": XYZ_TO_NTSC_1953},
    }
)


__all__ = [
    "SRGB_TO_XYZ",
    "XYZ_TO_SRGB",
    "REC709_TO_XYZ",
    "XYZ_TO_REC709",
    "REC2020_TO_XYZ",
    "XYZ_TO_REC2020",
    "ADOBE_RGB_TO_XYZ",
    "XYZ_TO_ADOBE_RGB",
    "DISPLAY_P3_TO_XYZ",
    "XYZ_TO_DISPLAY_P3",
    "DCIP3_TO_XYZ",
    "XYZ_TO_DCIP3",
    "NTSC_1953_TO_XYZ",
    "XYZ_TO_NTSC_1953",
    "RGB_COLOURSPACE_DEFINITIONS",
    "RGB_GAMUT_METADATA",
    "COMMON_GAMUTS",
]
