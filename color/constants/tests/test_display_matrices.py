"""Tests for RGB colour-space constants."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np
from colour.models import RGB_COLOURSPACES

from color.constants.display_matrices import (
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


_REFERENCE_NAMES = {
    "sRGB": "sRGB",
    "Rec.709": "ITU-R BT.709",
    "Display P3": "Display P3",
    "DCI-P3": "DCI-P3",
    "Rec.2020": "ITU-R BT.2020",
    "Adobe RGB (1998)": "Adobe RGB (1998)",
    "NTSC (1953)": "NTSC (1953)",
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


def test_primaries_and_whitepoints_match_colour():
    for local_name, colour_name in _REFERENCE_NAMES.items():
        definition = RGB_COLOURSPACE_DEFINITIONS[local_name]
        reference = RGB_COLOURSPACES[colour_name]

        np.testing.assert_allclose(
            np.asarray(definition["primaries"], dtype=float),
            reference.primaries,
            atol=1e-12,
        )
        np.testing.assert_allclose(
            np.asarray(definition["white_xy"], dtype=float),
            reference.whitepoint,
            atol=1e-12,
        )


def test_rgb_to_xyz_matrices_match_colour():
    matrix_pairs = {
        "sRGB": SRGB_TO_XYZ,
        "Display P3": DISPLAY_P3_TO_XYZ,
        "DCI-P3": DCIP3_TO_XYZ,
        "Rec.2020": REC2020_TO_XYZ,
        "Adobe RGB (1998)": ADOBE_RGB_TO_XYZ,
        "Rec.709": REC709_TO_XYZ,
    }

    for local_name, matrix in matrix_pairs.items():
        colour_name = _REFERENCE_NAMES[local_name]
        np.testing.assert_allclose(
            matrix,
            100.0 * RGB_COLOURSPACES[colour_name].matrix_RGB_to_XYZ,
            atol=1e-12,
        )


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
