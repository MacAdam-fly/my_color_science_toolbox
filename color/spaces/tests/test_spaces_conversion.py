"""Tests for generic colour-space conversion entry point."""

from __future__ import annotations

import warnings

import numpy as np
import pytest

from color.constants import D50_XYZ, D65_XYZ
from color.spaces import (
    ConversionPath,
    RGB_to_RGB,
    RGB_to_XYZ,
    SpaceSpec,
    XYZ_to_RGB,
    XYZ_to_xyY,
    convert_color,
    describe_conversion_path,
    xyY_to_XYZ,
)


def test_convert_XYZ_to_xyY():
    XYZ = np.array([95.047, 100.0, 108.883])

    np.testing.assert_allclose(
        convert_color(XYZ, "XYZ", "xyY"),
        XYZ_to_xyY(XYZ),
    )


def test_convert_xyY_to_XYZ():
    xyY = np.array([0.31272661, 0.32902313, 100.0])

    np.testing.assert_allclose(
        convert_color(xyY, "xyY", "XYZ"),
        xyY_to_XYZ(xyY),
    )


def test_convert_identity_returns_numeric_copy():
    XYZ = np.array([10.0, 20.0, 30.0])

    result = convert_color(XYZ, "XYZ", "XYZ")

    np.testing.assert_allclose(result, XYZ)
    assert result is not XYZ
    assert not np.shares_memory(result, XYZ)


def test_convert_passes_supported_options():
    result = convert_color(
        [0.0, 0.0, 0.0],
        "XYZ",
        "xyY",
        fallback_xy=(0.3127, 0.3290),
    )

    np.testing.assert_allclose(result, [0.3127, 0.3290, 0.0])


def test_convert_rejects_unsupported_options():
    with pytest.raises(ValueError, match="unsupported conversion option"):
        convert_color([0.3127, 0.3290, 1.0], "xyY", "XYZ", fallback_xy=(0.0, 0.0))


def test_convert_RGB_to_XYZ():
    RGB = np.array([0.2, 0.4, 0.6])

    np.testing.assert_allclose(
        convert_color(RGB, "sRGB", "XYZ"),
        RGB_to_XYZ(RGB, colourspace="sRGB"),
    )


def test_convert_XYZ_to_RGB():
    XYZ = np.array([20.0, 30.0, 40.0])

    np.testing.assert_allclose(
        convert_color(XYZ, "XYZ", "sRGB"),
        XYZ_to_RGB(XYZ, colourspace="sRGB"),
    )


def test_convert_RGB_to_RGB_uses_no_adaptation_route():
    RGB = np.array([0.2, 0.4, 0.6])

    np.testing.assert_allclose(
        convert_color(RGB, "sRGB", "Display P3"),
        RGB_to_RGB(RGB, "sRGB", "Display P3", chromatic_adaptation=None),
    )


def test_convert_RGB_to_xyY():
    RGB = np.array([0.2, 0.4, 0.6])

    np.testing.assert_allclose(
        convert_color(RGB, "sRGB", "xyY"),
        XYZ_to_xyY(RGB_to_XYZ(RGB, colourspace="sRGB")),
    )


def test_convert_xyY_to_RGB():
    xyY = np.array([0.31272661, 0.32902313, 100.0])

    np.testing.assert_allclose(
        convert_color(xyY, "xyY", "sRGB"),
        XYZ_to_RGB(xyY_to_XYZ(xyY), colourspace="sRGB"),
    )


def test_convert_rejects_chromatic_adaptation_option():
    with pytest.raises(ValueError, match="chromatic_adaptation"):
        convert_color(
            [1.0, 1.0, 1.0],
            "DCI-P3",
            "sRGB",
            chromatic_adaptation="Bradford",
        )


def test_convert_rejects_unregistered_paths():
    with pytest.raises(ValueError, match="unknown colour-space node"):
        convert_color([1.0, 1.0, 1.0], "unknown", "xyY")


def test_convert_warns_when_XYZ_reference_is_unknown_for_D65_referred_target():
    XYZ = np.array([20.0, 30.0, 40.0])

    with pytest.warns(UserWarning, match="D65-referred XYZ"):
        result = convert_color(XYZ, "XYZ", "Oklab")

    assert result.shape == (3,)
    assert np.all(np.isfinite(result))


def test_convert_warns_when_explicit_non_D65_source_feeds_D65_referred_target():
    XYZ = np.array([20.0, 30.0, 40.0])

    with pytest.warns(UserWarning, match="non-D65 reference whitepoint"):
        result = convert_color(
            XYZ,
            SpaceSpec("XYZ", whitepoint_XYZ=D50_XYZ),
            "Oklab",
        )

    assert result.shape == (3,)


def test_convert_warns_when_D65_chromaticity_uses_nonstandard_Y_scale():
    Lab = np.array([50.0, 20.0, -10.0])

    with pytest.warns(UserWarning, match="D65 chromaticity.*Y=100"):
        result = convert_color(
            Lab,
            SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ / 10.0),
            "Oklab",
        )

    assert result.shape == (3,)


def test_convert_accepts_explicit_D65_source_for_D65_referred_target_without_warning():
    XYZ = np.array([20.0, 30.0, 40.0])

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        result = convert_color(
            XYZ,
            SpaceSpec("XYZ", whitepoint_XYZ=D65_XYZ),
            "Oklab",
        )

    assert result.shape == (3,)
    assert len(record) == 0


def test_convert_warns_when_non_D65_RGB_feeds_D65_referred_target():
    RGB = np.array([0.2, 0.4, 0.6])

    with pytest.warns(UserWarning, match="DCI-P3"):
        result = convert_color(RGB, "DCI-P3", "Oklab")

    assert result.shape == (3,)


def test_convert_warns_when_D65_referred_source_feeds_non_D65_target():
    Oklab = np.array([0.5, 0.1, -0.2])

    with pytest.warns(UserWarning, match="non-D65 reference whitepoint"):
        result = convert_color(
            Oklab,
            "Oklab",
            SpaceSpec("Lab", whitepoint_XYZ=D50_XYZ),
        )

    assert result.shape == (3,)


def test_describe_conversion_path_warns_for_D65_reference_risk():
    with pytest.warns(UserWarning, match="non-D65 reference whitepoint"):
        path = describe_conversion_path(
            SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
            "Oklch",
        )

    assert [node.name for node in path.nodes] == ["LCHab", "Lab", "XYZ", "Oklab", "Oklch"]


def test_describe_conversion_path_RGB_to_RGB():
    path = describe_conversion_path("sRGB", "Display P3")

    assert isinstance(path, ConversionPath)
    assert [node.name for node in path.nodes] == ["sRGB", "XYZ", "Display P3"]
    assert [node.kind for node in path.nodes] == ["rgb", "hub", "rgb"]
    assert [edge.operation for edge in path.edges] == ["decode", "encode"]
    assert "chromatic_adaptation=None" in path.edges[0].description


def test_describe_conversion_path_with_derived_source():
    path = describe_conversion_path("JzCzhz", "Lab")

    assert [node.name for node in path.nodes] == ["JzCzhz", "Jzazbz", "XYZ", "Lab"]
    assert [edge.operation for edge in path.edges] == [
        "to_parent",
        "to_XYZ",
        "from_XYZ",
    ]


def test_describe_conversion_path_with_spacespec_parameters():
    path = describe_conversion_path(
        SpaceSpec("LCHab", whitepoint_XYZ=D50_XYZ),
        SpaceSpec("Luv", whitepoint_XYZ=D65_XYZ),
    )

    assert [node.name for node in path.nodes] == ["LCHab", "Lab", "XYZ", "Luv"]
    assert [edge.operation for edge in path.edges] == [
        "to_parent",
        "to_XYZ",
        "from_XYZ",
    ]


def test_describe_conversion_path_identity():
    path = describe_conversion_path("XYZ", "XYZ")

    assert [node.name for node in path.nodes] == ["XYZ"]
    assert [edge.operation for edge in path.edges] == ["identity"]


def test_describe_conversion_path_rejects_chromatic_adaptation():
    with pytest.raises(ValueError, match="chromatic_adaptation"):
        describe_conversion_path("DCI-P3", "sRGB", chromatic_adaptation="Bradford")


def test_describe_conversion_path_rejects_unregistered_paths():
    with pytest.raises(ValueError, match="unknown colour-space node"):
        describe_conversion_path("unknown", "xyY")
