"""Tests for generic colour-space conversion entry point."""

from __future__ import annotations

import numpy as np
import pytest

from color.spaces import (
    RGB_to_RGB,
    RGB_to_XYZ,
    XYZ_to_RGB,
    XYZ_to_xyY,
    convert_color,
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
