"""Tests for RGB display and imaging standard constants."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np

from color.constants.display_standards import (
    ADOBE_RGB_TO_XYZ,
    COMMON_GAMUTS,
    DCIP3_TO_XYZ,
    DISPLAY_P3_TO_XYZ,
    REC2020_TO_XYZ,
    REC709_TO_XYZ,
    RGB_COLOURSPACE_DEFINITIONS,
    RGB_GAMUT_METADATA,
    SRGB_TO_XYZ,
)


_REFERENCE_PRIMARIES_AND_WHITEPOINTS = {
    "sRGB": (((0.6400, 0.3300), (0.3000, 0.6000), (0.1500, 0.0600)), (0.3127, 0.3290)),
    "Rec.709": (((0.6400, 0.3300), (0.3000, 0.6000), (0.1500, 0.0600)), (0.3127, 0.3290)),
    "Display P3": (((0.6800, 0.3200), (0.2650, 0.6900), (0.1500, 0.0600)), (0.3127, 0.3290)),
    "DCI-P3": (((0.6800, 0.3200), (0.2650, 0.6900), (0.1500, 0.0600)), (0.3140, 0.3510)),
    "Rec.2020": (((0.7080, 0.2920), (0.1700, 0.7970), (0.1310, 0.0460)), (0.3127, 0.3290)),
    "Adobe RGB (1998)": (((0.6400, 0.3300), (0.2100, 0.7100), (0.1500, 0.0600)), (0.3127, 0.3290)),
    "NTSC (1953)": (((0.6700, 0.3300), (0.2100, 0.7100), (0.1400, 0.0800)), (0.31006, 0.31616)),
}


def test_rgb_definitions_are_immutable_mapping():
    assert isinstance(RGB_COLOURSPACE_DEFINITIONS, MappingProxyType)
    assert RGB_GAMUT_METADATA is RGB_COLOURSPACE_DEFINITIONS

    for definition in RGB_COLOURSPACE_DEFINITIONS.values():
        assert isinstance(definition, MappingProxyType)
        assert "gamma" not in definition


def test_rgb_definitions_have_required_fields():
    required_fields = {
        "name",
        "aliases",
        "primaries",
        "white_xy",
        "white_name",
        "transfer",
        "matrix_RGB_to_XYZ",
        "matrix_XYZ_to_RGB",
        "reference",
    }

    for definition in RGB_COLOURSPACE_DEFINITIONS.values():
        assert required_fields <= set(definition)
        assert np.asarray(definition["primaries"], dtype=float).shape == (3, 2)
        assert np.asarray(definition["white_xy"], dtype=float).shape == (2,)
        assert definition["matrix_RGB_to_XYZ"].shape == (3, 3)
        assert definition["matrix_XYZ_to_RGB"].shape == (3, 3)
        assert definition["transfer"]


def test_primaries_and_whitepoints_match_reference_values():
    for local_name, (primaries, white_xy) in _REFERENCE_PRIMARIES_AND_WHITEPOINTS.items():
        definition = RGB_COLOURSPACE_DEFINITIONS[local_name]

        np.testing.assert_allclose(
            np.asarray(definition["primaries"], dtype=float),
            np.asarray(primaries, dtype=float),
            atol=1e-12,
        )
        np.testing.assert_allclose(
            np.asarray(definition["white_xy"], dtype=float),
            np.asarray(white_xy, dtype=float),
            atol=1e-12,
        )


def test_rgb_to_xyz_matrices_match_reference_values():
    reference_matrices = {
        "sRGB": SRGB_TO_XYZ,
        "Display P3": DISPLAY_P3_TO_XYZ,
        "DCI-P3": DCIP3_TO_XYZ,
        "Rec.2020": REC2020_TO_XYZ,
        "Adobe RGB (1998)": ADOBE_RGB_TO_XYZ,
        "Rec.709": REC709_TO_XYZ,
    }

    np.testing.assert_allclose(reference_matrices["sRGB"], [
        [41.24, 35.76, 18.05],
        [21.26, 71.52, 7.22],
        [1.93, 11.92, 95.05],
    ])
    np.testing.assert_allclose(reference_matrices["Display P3"], [
        [48.65709486482162, 26.566769316909306, 19.82172852343625],
        [22.89745640697488, 69.17385218365064, 7.9286914093745],
        [0.0, 4.511338185890264, 104.3944368900976],
    ])
    np.testing.assert_allclose(reference_matrices["DCI-P3"], [
        [44.51698155645523, 27.71344092067778, 17.228266981556453],
        [20.94916779127312, 72.15952541610446, 6.891306792622578],
        [0.0, 4.706056005398175, 90.73553943616049],
    ])
    np.testing.assert_allclose(reference_matrices["Rec.2020"], [
        [63.69580483012914, 14.461690358620832, 16.88809751641721],
        [26.27002120112671, 67.79980715188708, 5.930171646986196],
        [0.0, 2.807269304908743, 106.0985057710791],
    ])
    np.testing.assert_allclose(reference_matrices["Adobe RGB (1998)"], [
        [57.667, 18.556, 18.823],
        [29.734, 62.736, 7.529],
        [2.703, 7.069, 99.134],
    ])
    np.testing.assert_allclose(reference_matrices["Rec.709"], [
        [41.239079926595934, 35.7584339383878, 18.04807884018343],
        [21.263900587151027, 71.5168678767756, 7.219231536073371],
        [1.933081871559182, 11.919477979462599, 95.05321522496607],
    ])


def test_dcip3_matrix_matches_theatrical_white():
    white_xyz = DCIP3_TO_XYZ @ np.ones(3)
    white_xy = white_xyz[:2] / np.sum(white_xyz)

    np.testing.assert_allclose(white_xy, [0.314, 0.351], atol=1e-12)
    assert not np.allclose(white_xy, [0.3457, 0.3585], atol=1e-3)


def test_rgb_matrices_round_trip_to_identity():
    for definition in RGB_COLOURSPACE_DEFINITIONS.values():
        to_xyz = definition["matrix_RGB_to_XYZ"]
        from_xyz = definition["matrix_XYZ_to_RGB"]

        np.testing.assert_allclose(from_xyz @ to_xyz, np.identity(3), atol=1e-12)
        np.testing.assert_allclose(to_xyz @ from_xyz, np.identity(3), atol=1e-12)


def test_common_gamuts_compatibility_registry_uses_new_matrices():
    assert COMMON_GAMUTS["sRGB"]["to_xyz"] is SRGB_TO_XYZ
    assert COMMON_GAMUTS["Rec709"]["to_xyz"] is REC709_TO_XYZ
    assert COMMON_GAMUTS["Rec2020"]["to_xyz"] is REC2020_TO_XYZ
    assert COMMON_GAMUTS["DisplayP3"]["to_xyz"] is DISPLAY_P3_TO_XYZ
    assert COMMON_GAMUTS["DCI-P3"]["to_xyz"] is DCIP3_TO_XYZ
