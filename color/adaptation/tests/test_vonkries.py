"""Tests for Von Kries style chromatic adaptation."""

from __future__ import annotations

from types import MappingProxyType

import numpy as np
import pytest

from color.adaptation import (
    CAT_BRADFORD,
    CHROMATIC_ADAPTATION_TRANSFORMS,
    chromatic_adaptation_XYZ,
    matrix_chromatic_adaptation_von_kries,
)
from color.constants import D50_XYZ, D65_XYZ


def _normalise_whitepoint(XYZ: np.ndarray) -> np.ndarray:
    return np.asarray(XYZ, dtype=np.float64) / XYZ[1]


def test_transforms_are_read_only_and_registered():
    assert isinstance(CHROMATIC_ADAPTATION_TRANSFORMS, MappingProxyType)
    assert set(CHROMATIC_ADAPTATION_TRANSFORMS) == {
        "Von Kries",
        "Bradford",
        "CAT02",
        "CAT16",
    }

    with pytest.raises(ValueError):
        CAT_BRADFORD[0, 0] = 0.0


@pytest.mark.parametrize("transform", ["Von Kries", "Bradford", "CAT02", "CAT16"])
def test_supported_transforms_return_finite_matrices(transform):
    matrix = matrix_chromatic_adaptation_von_kries(
        D65_XYZ,
        D50_XYZ,
        transform=transform,
    )

    assert matrix.shape == (3, 3)
    assert np.all(np.isfinite(matrix))


def test_bradford_matrix_matches_colour_reference():
    colour = pytest.importorskip("colour")
    source_white = _normalise_whitepoint(D65_XYZ)
    target_white = _normalise_whitepoint(D50_XYZ)

    expected = colour.adaptation.matrix_chromatic_adaptation_VonKries(
        source_white,
        target_white,
        transform="Bradford",
    )
    actual = matrix_chromatic_adaptation_von_kries(
        source_white,
        target_white,
        transform="Bradford",
    )

    np.testing.assert_allclose(actual, expected, atol=1e-12)


def test_transform_none_returns_identity_and_copy():
    XYZ = np.array([0.2, 0.3, 0.4])

    matrix = matrix_chromatic_adaptation_von_kries(
        D65_XYZ,
        D50_XYZ,
        transform=None,
    )
    adapted = chromatic_adaptation_XYZ(
        XYZ,
        D65_XYZ,
        D50_XYZ,
        transform=None,
    )

    np.testing.assert_allclose(matrix, np.identity(3))
    np.testing.assert_allclose(adapted, XYZ)
    assert adapted is not XYZ
    assert not np.shares_memory(adapted, XYZ)


def test_same_whitepoint_is_identity():
    matrix = matrix_chromatic_adaptation_von_kries(
        D65_XYZ,
        D65_XYZ,
        transform="CAT02",
    )

    np.testing.assert_allclose(matrix, np.identity(3), atol=1e-12)


def test_chromatic_adaptation_supports_batch_shape():
    XYZ = np.array([
        [0.2, 0.3, 0.4],
        [0.5, 0.4, 0.2],
    ])

    adapted = chromatic_adaptation_XYZ(
        XYZ,
        _normalise_whitepoint(D65_XYZ),
        _normalise_whitepoint(D50_XYZ),
        transform="Bradford",
    )

    assert adapted.shape == XYZ.shape
    assert np.all(np.isfinite(adapted))


def test_round_trip_recovers_XYZ():
    XYZ = np.array([
        [0.2, 0.3, 0.4],
        [0.5, 0.4, 0.2],
    ])
    source = _normalise_whitepoint(D65_XYZ)
    target = _normalise_whitepoint(D50_XYZ)

    adapted = chromatic_adaptation_XYZ(XYZ, source, target, transform="CAT16")
    recovered = chromatic_adaptation_XYZ(adapted, target, source, transform="CAT16")

    np.testing.assert_allclose(recovered, XYZ, atol=1e-12)


@pytest.mark.parametrize(
    ("source_white", "target_white", "message"),
    [
        ([1.0, 1.0], D50_XYZ, "exactly 3 values"),
        ([1.0, np.nan, 1.0], D50_XYZ, "finite"),
        ([1.0, 0.0, 1.0], D50_XYZ, "positive"),
        (D65_XYZ, [1.0, -1.0, 1.0], "positive"),
    ],
)
def test_invalid_whitepoints_raise(source_white, target_white, message):
    with pytest.raises(ValueError, match=message):
        matrix_chromatic_adaptation_von_kries(source_white, target_white)


def test_invalid_XYZ_raises():
    with pytest.raises(ValueError, match="3 values"):
        chromatic_adaptation_XYZ([0.1, 0.2], D65_XYZ, D50_XYZ)

    with pytest.raises(ValueError, match="finite"):
        chromatic_adaptation_XYZ([0.1, np.nan, 0.2], D65_XYZ, D50_XYZ)


def test_unknown_transform_raises():
    with pytest.raises(ValueError, match="unknown chromatic adaptation transform"):
        matrix_chromatic_adaptation_von_kries(
            D65_XYZ,
            D50_XYZ,
            transform="unknown",
        )
