"""Tests for RGB colour spaces."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np
import pytest

from color.spaces import (
    RGBColorSpace,
    RGB_COLORSPACES,
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    XYZ_to_sRGB,
    get_RGB_colourspace,
    list_RGB_colourspaces,
    sRGB_to_XYZ,
)


def test_registry_resolves_names_and_aliases():
    assert get_RGB_colourspace("sRGB").name == "sRGB"
    assert get_RGB_colourspace("srgb").name == "sRGB"
    assert get_RGB_colourspace("DisplayP3").name == "Display P3"
    assert get_RGB_colourspace("ITU-R BT.2020").name == "Rec.2020"
    assert get_RGB_colourspace("AdobeRGB1998").name == "Adobe RGB (1998)"

    names = list_RGB_colourspaces()
    assert "sRGB" in names
    assert "Display P3" in names
    assert "Rec.2020" in names


def test_registry_objects_are_read_only():
    assert isinstance(RGB_COLORSPACES, MappingProxyType)
    srgb = get_RGB_colourspace("sRGB")

    with pytest.raises(TypeError):
        RGB_COLORSPACES["custom"] = srgb  # type: ignore[index]
    with pytest.raises(ValueError):
        srgb.matrix_RGB_to_XYZ[0, 0] = 0.0
    with pytest.raises(ValueError):
        srgb.primaries[0, 0] = 0.0


def test_sRGB_to_XYZ_white():
    np.testing.assert_allclose(
        sRGB_to_XYZ([1.0, 1.0, 1.0]),
        get_RGB_colourspace("sRGB").matrix_RGB_to_XYZ @ np.ones(3),
        atol=1e-12,
    )


def test_sRGB_round_trip():
    RGB = np.array([
        [0.1, 0.2, 0.3],
        [0.8, 0.6, 0.4],
    ])

    XYZ = sRGB_to_XYZ(RGB)
    recovered = XYZ_to_sRGB(XYZ)

    assert XYZ.shape == RGB.shape
    np.testing.assert_allclose(recovered, RGB, atol=1e-12)


def test_linear_paths_match_matrix_multiplication():
    RGB = np.array([0.25, 0.5, 0.75])
    space = get_RGB_colourspace("Display P3")

    XYZ = RGB_to_XYZ(RGB, colourspace=space, apply_decoding=False)
    recovered = XYZ_to_RGB(XYZ, colourspace=space, apply_encoding=False)

    np.testing.assert_allclose(XYZ, RGB @ space.matrix_RGB_to_XYZ.T)
    np.testing.assert_allclose(recovered, RGB, atol=1e-12)


@pytest.mark.parametrize(
    "name",
    ["Display P3", "Rec.2020", "Adobe RGB (1998)", "DCI-P3"],
)
def test_rgb_spaces_white_round_trip(name):
    RGB = np.ones(3)

    XYZ = RGB_to_XYZ(RGB, colourspace=name)
    recovered = XYZ_to_RGB(XYZ, colourspace=name)

    assert XYZ.shape == (3,)
    np.testing.assert_allclose(recovered, RGB, atol=1e-12)


def test_RGB_to_RGB_matches_explicit_XYZ_path_without_adaptation():
    RGB = np.array([0.2, 0.4, 0.6])

    expected = XYZ_to_RGB(
        RGB_to_XYZ(RGB, colourspace="sRGB"),
        colourspace="Display P3",
    )
    result = RGB_to_RGB(RGB, "sRGB", "Display P3")

    np.testing.assert_allclose(result, expected, atol=1e-12)


def test_RGB_to_RGB_can_apply_chromatic_adaptation():
    RGB = np.ones(3)

    no_adaptation = RGB_to_RGB(RGB, "DCI-P3", "sRGB")
    adapted = RGB_to_RGB(RGB, "DCI-P3", "sRGB", chromatic_adaptation="Bradford")

    assert not np.allclose(adapted, no_adaptation)
    np.testing.assert_allclose(adapted, np.ones(3), atol=1e-4)


def test_RGB_to_RGB_preserves_batch_shape():
    RGB = np.ones((2, 3, 3)) * 0.5

    result = RGB_to_RGB(RGB, "sRGB", "Rec.2020")

    assert result.shape == RGB.shape


def test_RGB_to_RGB_rejects_unknown_adaptation_transform():
    with pytest.raises(ValueError, match="unknown chromatic adaptation transform"):
        RGB_to_RGB(
            [1.0, 1.0, 1.0],
            "DCI-P3",
            "sRGB",
            chromatic_adaptation="unknown",
        )


def test_batch_shape_preserved():
    RGB = np.ones((2, 3, 3)) * 0.5
    XYZ = RGB_to_XYZ(RGB, colourspace="Rec.709")
    recovered = XYZ_to_RGB(XYZ, colourspace="Rec.709")

    assert XYZ.shape == RGB.shape
    np.testing.assert_allclose(recovered, RGB, atol=1e-12)


def test_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="unknown RGB colour space"):
        get_RGB_colourspace("unknown")
    with pytest.raises(ValueError, match="3 values"):
        RGB_to_XYZ([1.0, 2.0])
    with pytest.raises(ValueError, match="finite"):
        XYZ_to_RGB([1.0, np.nan, 0.0])


def test_rejects_unknown_transfer():
    srgb = get_RGB_colourspace("sRGB")
    custom = RGBColorSpace(
        name="custom",
        aliases=(),
        primaries=srgb.primaries,
        white_xy=srgb.white_xy,
        white_name=srgb.white_name,
        transfer="unknown",
        matrix_RGB_to_XYZ=srgb.matrix_RGB_to_XYZ,
        matrix_XYZ_to_RGB=srgb.matrix_XYZ_to_RGB,
    )

    with pytest.raises(ValueError, match="unknown RGB transfer"):
        RGB_to_XYZ([1.0, 1.0, 1.0], colourspace=custom)
