"""Tests for standard Lab colour-difference formulas."""

from __future__ import annotations

import numpy as np
import pytest

from color.difference import (
    JND_CIE1976,
    delta_E_CIE1976,
    delta_E_CIE1994,
    delta_E_CIE2000,
    delta_E_CMC,
)

colour = pytest.importorskip("colour")


LAB_1 = np.array([50.0000, 2.6772, -79.7751], dtype=np.float64)
LAB_2 = np.array([50.0000, 0.0000, -82.7485], dtype=np.float64)
LAB_BATCH_1 = np.array(
    [
        [50.0000, 2.6772, -79.7751],
        [50.0000, 3.1571, -77.2803],
        [50.0000, 2.8361, -74.0200],
        [100.0000, 21.5721, 272.2282],
    ],
    dtype=np.float64,
)
LAB_BATCH_2 = np.array(
    [
        [50.0000, 0.0000, -82.7485],
        [50.0000, 0.0000, -82.7485],
        [50.0000, 0.0000, -82.7485],
        [100.0000, 426.6795, 72.3959],
    ],
    dtype=np.float64,
)


def assert_matches_colour(function, reference, *args, **kwargs):
    result = function(*args, **kwargs)
    expected = reference(*args, **kwargs)
    np.testing.assert_allclose(result, expected, rtol=1e-10, atol=1e-10)


def test_jnd_cie1976_constant():
    assert JND_CIE1976 == 2.3


def test_delta_e_cie1976_matches_colour():
    assert_matches_colour(
        delta_E_CIE1976,
        colour.difference.delta_E_CIE1976,
        LAB_BATCH_1,
        LAB_BATCH_2,
    )


def test_delta_e_cie1994_matches_colour():
    assert_matches_colour(
        delta_E_CIE1994,
        colour.difference.delta_E_CIE1994,
        LAB_BATCH_1,
        LAB_BATCH_2,
    )


def test_delta_e_cie1994_textiles_matches_colour():
    assert_matches_colour(
        delta_E_CIE1994,
        colour.difference.delta_E_CIE1994,
        LAB_BATCH_1,
        LAB_BATCH_2,
        textiles=True,
    )


def test_delta_e_cie2000_matches_colour():
    assert_matches_colour(
        delta_E_CIE2000,
        colour.difference.delta_E_CIE2000,
        LAB_BATCH_1,
        LAB_BATCH_2,
    )
    np.testing.assert_allclose(delta_E_CIE2000(LAB_1, LAB_2), 2.0425, atol=5e-5)


def test_delta_e_cie2000_textiles_matches_colour():
    assert_matches_colour(
        delta_E_CIE2000,
        colour.difference.delta_E_CIE2000,
        LAB_BATCH_1,
        LAB_BATCH_2,
        textiles=True,
    )


def test_delta_e_cmc_matches_colour():
    assert_matches_colour(
        delta_E_CMC,
        colour.difference.delta_E_CMC,
        LAB_BATCH_1,
        LAB_BATCH_2,
    )


def test_delta_e_cmc_l_1_c_1_matches_colour():
    assert_matches_colour(
        delta_E_CMC,
        colour.difference.delta_E_CMC,
        LAB_BATCH_1,
        LAB_BATCH_2,
        l=1,
        c=1,
    )


def test_single_point_returns_scalar():
    result = delta_E_CIE1976(LAB_1, LAB_2)
    assert np.isscalar(result)


def test_batch_and_broadcast_shapes():
    batch_result = delta_E_CIE2000(LAB_BATCH_1, LAB_BATCH_2)
    broadcast_result = delta_E_CIE2000(LAB_BATCH_1, LAB_2)

    assert batch_result.shape == (4,)
    assert broadcast_result.shape == (4,)
    np.testing.assert_allclose(
        broadcast_result,
        colour.difference.delta_E_CIE2000(LAB_BATCH_1, LAB_2),
        rtol=1e-10,
        atol=1e-10,
    )


@pytest.mark.parametrize(
    "bad_value",
    [
        [50.0, 2.0],
        [[50.0, 2.0], [51.0, 3.0]],
    ],
)
def test_invalid_shape_raises(bad_value):
    with pytest.raises(ValueError, match="3 values"):
        delta_E_CIE1976(bad_value, LAB_2)


def test_non_finite_input_raises():
    with pytest.raises(ValueError, match="finite"):
        delta_E_CIE1976([50.0, np.nan, 2.0], LAB_2)


def test_non_broadcastable_input_raises():
    with pytest.raises(ValueError, match="could not be broadcast"):
        delta_E_CIE1976(np.zeros((2, 3)), np.zeros((4, 3)))


def test_invalid_cmc_parameters_raise():
    with pytest.raises(ValueError, match="positive"):
        delta_E_CMC(LAB_1, LAB_2, l=0)
    with pytest.raises(ValueError, match="positive"):
        delta_E_CMC(LAB_1, LAB_2, c=0)
