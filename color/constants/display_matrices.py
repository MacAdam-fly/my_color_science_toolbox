"""Display RGB colour-space conversion matrices."""

from __future__ import annotations

import numpy as np

SRGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ],
    dtype=float,
)

XYZ_TO_SRGB = np.linalg.inv(SRGB_TO_XYZ)

# BT.2020 (Rec.2020) RGB -> XYZ (D65)
REC2020_TO_XYZ = np.array(
    [
        [0.6369580483012914, 0.14461690358620832, 0.1688809751641721],
        [0.2627002120112671, 0.6779980715188708, 0.05930171646986196],
        [0.0, 0.028072693049087428, 1.060985057710791],
    ],
    dtype=float,
)
XYZ_TO_REC2020 = np.linalg.inv(REC2020_TO_XYZ)

# Adobe RGB (1998) RGB -> XYZ (D65)
ADOBE_RGB_TO_XYZ = np.array(
    [
        [0.5767309, 0.1855540, 0.1881852],
        [0.2973769, 0.6273491, 0.0752741],
        [0.0270343, 0.0706872, 0.9911085],
    ],
    dtype=float,
)
XYZ_TO_ADOBE_RGB = np.linalg.inv(ADOBE_RGB_TO_XYZ)

# Display P3 (P3-D65) RGB -> XYZ
DISPLAY_P3_TO_XYZ = np.array(
    [
        [0.4865709486482162, 0.26566769316909306, 0.1982172852343625],
        [0.2289745640697488, 0.6917385218365064, 0.079286914093745],
        [0.0, 0.04511338185890264, 1.043944368900976],
    ],
    dtype=float,
)
XYZ_TO_DISPLAY_P3 = np.linalg.inv(DISPLAY_P3_TO_XYZ)

# DCI-P3 (theatrical P3) RGB -> XYZ (approximate matrix for common use)
DCIP3_TO_XYZ = np.array(
    [
        [0.515102, 0.291965, 0.157153],
        [0.241182, 0.692236, 0.066581],
        [0.0, 0.041881, 0.784378],
    ],
    dtype=float,
)
XYZ_TO_DCIP3 = np.linalg.inv(DCIP3_TO_XYZ)

# Expose a small registry for common gamuts
COMMON_GAMUTS = {
    'sRGB': {'to_xyz': SRGB_TO_XYZ, 'from_xyz': XYZ_TO_SRGB},
    'Rec2020': {'to_xyz': REC2020_TO_XYZ, 'from_xyz': XYZ_TO_REC2020},
    'AdobeRGB1998': {'to_xyz': ADOBE_RGB_TO_XYZ, 'from_xyz': XYZ_TO_ADOBE_RGB},
    'DisplayP3': {'to_xyz': DISPLAY_P3_TO_XYZ, 'from_xyz': XYZ_TO_DISPLAY_P3},
    'DCI-P3': {'to_xyz': DCIP3_TO_XYZ, 'from_xyz': XYZ_TO_DCIP3},
}

# Standard primaries, white points and nominal gamma/transfer for common RGB spaces
# Values taken from common specifications / the user's provided table
RGB_GAMUT_METADATA = {
    'sRGB': {
        'white_xy': (0.3127, 0.3290),
        'white_name': 'D65',
        'primaries': {'R': (0.6400, 0.3300), 'G': (0.3000, 0.6000), 'B': (0.1500, 0.0600)},
        'gamma': '2.2'
    },
    'Rec.709': {
        'white_xy': (0.3127, 0.3290),
        'white_name': 'D65',
        'primaries': {'R': (0.6400, 0.3300), 'G': (0.3000, 0.6000), 'B': (0.1500, 0.0600)},
        'gamma': '2.4'
    },
    'DCI-P3': {
        'white_xy': (0.3140, 0.3510),
        'white_name': 'DCP white',
        'primaries': {'R': (0.6800, 0.3200), 'G': (0.2650, 0.6900), 'B': (0.1500, 0.0600)},
        'gamma': '2.6'
    },
    'DisplayP3': {
        'white_xy': (0.3127, 0.3290),
        'white_name': 'D65',
        'primaries': {'R': (0.6800, 0.3200), 'G': (0.2650, 0.6900), 'B': (0.1500, 0.0600)},
        'gamma': '2.2'
    },
    'AdobeRGB1998': {
        'white_xy': (0.3127, 0.3290),
        'white_name': 'D65',
        'primaries': {'R': (0.6400, 0.3300), 'G': (0.2100, 0.7100), 'B': (0.1500, 0.0600)},
        'gamma': '2.2'
    },
    'Rec.2020': {
        'white_xy': (0.3127, 0.3290),
        'white_name': 'D65',
        'primaries': {'R': (0.7080, 0.2920), 'G': (0.1700, 0.7970), 'B': (0.1310, 0.0460)},
        'gamma': '2.2'
    },
    'NTSC_1953': {
        'white_xy': (0.3101, 0.3162),
        'white_name': 'C',
        'primaries': {'R': (0.6700, 0.3300), 'G': (0.2100, 0.7100), 'B': (0.1400, 0.0800)},
        'gamma': '2.2'
    }
}

