"""Tests for RGB colour spaces."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np
import pytest

from color.gamut import (
    DisplayPrimaries,
    analyze_gamut,
    compute_LCH_gamut_boundary,
)
from color.spaces import (
    RGBColorSpace,
    RGB_colourspace_from_primaries_XYZ,
    RGB_colourspace_from_primaries_xy,
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    XYZ_to_sRGB,
    convert_color,
    get_RGB_colourspace,
    list_RGB_colourspaces,
    register_RGB_colourspace,
    sRGB_to_XYZ,
)
from color.constants import D65_XYZ
from color.spaces.rgb import RGB_COLORSPACES
from color.spaces.rgb.transfer import decode_transfer, encode_transfer


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
        D65_XYZ,
        atol=3e-2,
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


def test_custom_rgb_from_primaries_xy_reproduces_sRGB_matrix():
    srgb = get_RGB_colourspace("sRGB")

    custom = RGB_colourspace_from_primaries_xy(
        "Test xy sRGB",
        srgb.primaries,
        whitepoint_xy=srgb.white_xy,
        transfer="sRGB",
    )

    np.testing.assert_allclose(custom.matrix_RGB_to_XYZ, srgb.matrix_RGB_to_XYZ, atol=5e-3)
    np.testing.assert_allclose(custom.matrix_XYZ_to_RGB, srgb.matrix_XYZ_to_RGB, atol=5e-6)
    assert custom.transfer == "srgb"


def test_custom_rgb_from_primaries_XYZ_preserves_measured_primaries():
    srgb = get_RGB_colourspace("sRGB")
    primaries_XYZ = srgb.matrix_RGB_to_XYZ.T

    custom = RGB_colourspace_from_primaries_XYZ(
        "Test measured sRGB",
        primaries_XYZ,
        transfer=("gamma", 2.2),
    )

    np.testing.assert_allclose(custom.matrix_RGB_to_XYZ.T, primaries_XYZ)
    np.testing.assert_allclose(
        RGB_to_XYZ([1.0, 1.0, 1.0], colourspace=custom),
        np.sum(primaries_XYZ, axis=0),
    )


def test_custom_rgb_from_primaries_XYZ_warns_for_non_Y100_whitepoint():
    srgb = get_RGB_colourspace("sRGB")

    with pytest.warns(UserWarning, match="whitepoint Y is not 100"):
        RGB_colourspace_from_primaries_XYZ(
            "Test measured scaled",
            srgb.matrix_RGB_to_XYZ.T * 2.0,
        )


def test_custom_rgb_round_trip_with_dynamic_gamma():
    srgb = get_RGB_colourspace("sRGB")
    custom = RGB_colourspace_from_primaries_xy(
        "Test gamma RGB",
        srgb.primaries,
        whitepoint_xy=srgb.white_xy,
        transfer=("gamma", (2.2, 2.3, 2.1)),
    )
    RGB = np.array([0.25, 0.5, 0.75])

    XYZ = RGB_to_XYZ(RGB, colourspace=custom)
    recovered = XYZ_to_RGB(XYZ, colourspace=custom)

    np.testing.assert_allclose(recovered, RGB, atol=1e-12)


def test_dynamic_gamma_transfer_matches_channel_power():
    RGB = np.array([[0.25, 0.5, 0.75], [-0.25, -0.5, -0.75]])
    gamma = np.array([2.2, 2.3, 2.1])

    decoded = decode_transfer(RGB, ("gamma", tuple(gamma)))
    expected = np.sign(RGB) * np.abs(RGB) ** gamma

    np.testing.assert_allclose(decoded, expected)
    np.testing.assert_allclose(encode_transfer(decoded, ("gamma", tuple(gamma))), RGB)


def test_custom_rgb_rejects_invalid_definitions_and_transfer():
    srgb = get_RGB_colourspace("sRGB")

    with pytest.raises(ValueError, match="primaries_xy must have shape"):
        RGB_colourspace_from_primaries_xy("bad", [[0.1, 0.2]], whitepoint_xy=srgb.white_xy)
    with pytest.raises(ValueError, match="singular"):
        RGB_colourspace_from_primaries_xy(
            "bad singular",
            [[0.3, 0.3], [0.3, 0.3], [0.3, 0.3]],
            whitepoint_xy=srgb.white_xy,
        )
    with pytest.raises(ValueError, match="primaries_XYZ must have shape"):
        RGB_colourspace_from_primaries_XYZ("bad XYZ", [[1.0, 2.0, 3.0]])
    with pytest.raises(ValueError, match="gamma exponent"):
        RGB_colourspace_from_primaries_xy(
            "bad gamma",
            srgb.primaries,
            whitepoint_xy=srgb.white_xy,
            transfer=("gamma", -2.2),
        )
    with pytest.raises(ValueError, match="per-channel gamma"):
        RGB_colourspace_from_primaries_xy(
            "bad channel gamma",
            srgb.primaries,
            whitepoint_xy=srgb.white_xy,
            transfer=("gamma", (2.2, 2.3)),
        )


def test_register_custom_rgb_colourspace_and_route_through_spaces_and_gamut():
    srgb = get_RGB_colourspace("sRGB")
    custom = RGB_colourspace_from_primaries_xy(
        "Test Custom Display",
        srgb.primaries,
        whitepoint_xy=srgb.white_xy,
        transfer=("gamma", (2.2, 2.3, 2.1)),
        aliases=("TestCustomDisplay",),
    )
    register_RGB_colourspace(custom, overwrite=True)

    assert get_RGB_colourspace("TestCustomDisplay").name == "Test Custom Display"
    assert "Test Custom Display" in list_RGB_colourspaces()

    primaries = DisplayPrimaries.from_RGB_colourspace("Test Custom Display")
    np.testing.assert_allclose(primaries.primaries_XYZ, custom.matrix_RGB_to_XYZ.T)

    Lab = convert_color([0.4, 0.5, 0.6], "Test Custom Display", "Lab")
    assert Lab.shape == (3,)
    assert np.all(np.isfinite(Lab))

    boundary = compute_LCH_gamut_boundary(
        "Test Custom Display",
        L_values=[0.0, 50.0, 100.0],
        hue_values=[0.0, 120.0, 240.0, 360.0],
        C_upper=220.0,
        iterations=4,
    )
    assert boundary.C_max.shape == (3, 4)

    with pytest.warns(UserWarning):
        analysis = analyze_gamut(
            "Test Custom Display",
            L_values=[0.0, 50.0, 100.0],
            hue_values=[0.0, 120.0, 240.0, 360.0],
            C_upper=220.0,
            iterations=4,
        )
    assert np.isfinite(analysis.xy_area)


def test_register_custom_rgb_colourspace_rejects_conflicts_and_supports_overwrite():
    srgb = get_RGB_colourspace("sRGB")
    custom = RGB_colourspace_from_primaries_xy(
        "Test Replaceable RGB",
        srgb.primaries,
        whitepoint_xy=srgb.white_xy,
    )
    register_RGB_colourspace(custom, overwrite=True)

    with pytest.raises(ValueError, match="already registered"):
        register_RGB_colourspace(custom)

    replacement = RGB_colourspace_from_primaries_xy(
        "Test Replaceable RGB",
        srgb.primaries,
        whitepoint_xy=srgb.white_xy,
        aliases=("TestReplaceableRGB2",),
    )
    register_RGB_colourspace(replacement, overwrite=True)
    assert get_RGB_colourspace("TestReplaceableRGB2").name == "Test Replaceable RGB"

    with pytest.raises(ValueError, match="standard RGB colour space"):
        register_RGB_colourspace(
            RGB_colourspace_from_primaries_xy(
                "sRGB",
                srgb.primaries,
                whitepoint_xy=srgb.white_xy,
            )
        )
    with pytest.raises(ValueError, match="standard colour space"):
        register_RGB_colourspace(
            RGB_colourspace_from_primaries_xy(
                "Test Alias Conflict",
                srgb.primaries,
                whitepoint_xy=srgb.white_xy,
                aliases=("sRGB",),
            )
        )
