"""Tests for parameterized colour-space specifications."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np
import pytest

from color.spaces import (
    SpaceSpec,
    XYZ_to_RGB,
    convert_color,
    sRGB_to_XYZ,
    xyY_to_XYZ,
)


def test_space_spec_stores_read_only_parameters():
    spec = SpaceSpec("xyY", fallback_xy=(0.3127, 0.3290))

    assert spec.name == "xyY"
    assert isinstance(spec.parameters, MappingProxyType)
    assert spec.parameters["fallback_xy"] == (0.3127, 0.3290)
    with pytest.raises(TypeError):
        spec.parameters["fallback_xy"] = (0.0, 0.0)  # type: ignore[index]


def test_convert_accepts_space_spec_identity():
    XYZ = np.array([0.1, 0.2, 0.3])

    result = convert_color(XYZ, SpaceSpec("XYZ"), SpaceSpec("XYZ"))

    np.testing.assert_allclose(result, XYZ)
    assert result is not XYZ
    assert not np.shares_memory(result, XYZ)


def test_target_space_spec_parameters_apply_to_from_XYZ():
    XYZ = np.array([0.0, 0.0, 0.0])
    target = SpaceSpec("xyY", fallback_xy=(0.3127, 0.3290))

    np.testing.assert_allclose(
        convert_color(XYZ, "XYZ", target),
        [0.3127, 0.3290, 0.0],
    )


def test_source_space_spec_parameters_apply_to_to_XYZ():
    xyY = np.array([0.3127, 0.3290, 0.5])

    np.testing.assert_allclose(
        convert_color(xyY, SpaceSpec("xyY"), "XYZ"),
        xyY_to_XYZ(xyY),
    )


def test_source_space_spec_rejects_unsupported_to_XYZ_parameter():
    with pytest.raises(ValueError, match="unsupported conversion option"):
        convert_color(
            [0.3127, 0.3290, 1.0],
            SpaceSpec("xyY", fallback_xy=(0.0, 0.0)),
            "XYZ",
        )


def test_space_spec_parameters_override_common_options_for_target():
    XYZ = np.array([0.0, 0.0, 0.0])
    target = SpaceSpec("xyY", fallback_xy=(0.3127, 0.3290))

    np.testing.assert_allclose(
        convert_color(
            XYZ,
            "XYZ",
            target,
            fallback_xy=(0.0, 0.0),
        ),
        [0.3127, 0.3290, 0.0],
    )


def test_rgb_source_space_spec_parameters_apply_to_decoding():
    RGB = np.array([0.25, 0.5, 0.75])

    np.testing.assert_allclose(
        convert_color(RGB, SpaceSpec("sRGB", apply_decoding=False), "XYZ"),
        sRGB_to_XYZ(RGB, apply_decoding=False),
    )


def test_rgb_target_space_spec_parameters_apply_to_encoding():
    XYZ = np.array([0.2, 0.3, 0.4])

    np.testing.assert_allclose(
        convert_color(XYZ, "XYZ", SpaceSpec("sRGB", apply_encoding=False)),
        XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=False),
    )


def test_convert_rejects_chromatic_adaptation_in_space_spec():
    with pytest.raises(ValueError, match="chromatic_adaptation"):
        convert_color(
            [1.0, 1.0, 1.0],
            SpaceSpec("DCI-P3", chromatic_adaptation="Bradford"),
            "sRGB",
        )


def test_convert_accepts_space_spec_rgb_to_rgb():
    RGB = np.array([0.25, 0.5, 0.75])

    result = convert_color(
        RGB,
        SpaceSpec("sRGB", apply_decoding=False),
        SpaceSpec("Display P3", apply_encoding=False),
    )

    XYZ = sRGB_to_XYZ(RGB, apply_decoding=False)
    expected = XYZ_to_RGB(XYZ, colourspace="Display P3", apply_encoding=False)
    np.testing.assert_allclose(result, expected)
