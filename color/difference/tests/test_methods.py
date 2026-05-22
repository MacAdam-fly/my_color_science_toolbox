"""Tests for Delta E method dispatch."""

from __future__ import annotations

import numpy as np
import pytest

from color.difference import (
    DELTA_E_METHODS,
    delta_E,
    delta_E_CAM02LCD,
    delta_E_CAM02SCD,
    delta_E_CAM02UCS,
    delta_E_CAM16LCD,
    delta_E_CAM16SCD,
    delta_E_CAM16UCS,
    delta_E_CIE1976,
    delta_E_CIE1994,
    delta_E_CIE2000,
    delta_E_CMC,
    delta_E_Jzazbz,
    delta_E_Oklab,
)


LAB_BATCH_1 = np.array(
    [
        [50.0000, 2.6772, -79.7751],
        [50.0000, 3.1571, -77.2803],
    ],
    dtype=np.float64,
)
LAB_BATCH_2 = np.array(
    [
        [50.0000, 0.0000, -82.7485],
        [50.0000, 0.0000, -82.7485],
    ],
    dtype=np.float64,
)
JPAPBP_BATCH_1 = np.array(
    [
        [54.90433134, -0.08450395, -0.06854831],
        [62.12848174, 8.12165042, 22.44110157],
    ],
    dtype=np.float64,
)
JPAPBP_BATCH_2 = np.array(
    [
        [54.80352754, -3.96940084, -13.57591013],
        [60.02111984, 4.25010411, 18.10888174],
    ],
    dtype=np.float64,
)
OKLAB_BATCH_1 = np.array([[0.65, 0.12, -0.08], [0.72, -0.04, 0.10]], dtype=np.float64)
OKLAB_BATCH_2 = np.array([[0.58, 0.04, -0.11], [0.70, -0.01, 0.05]], dtype=np.float64)
JZAZBZ_BATCH_1 = np.array([[0.010, 0.018, -0.012], [0.015, -0.006, 0.008]], dtype=np.float64)
JZAZBZ_BATCH_2 = np.array([[0.012, 0.011, -0.018], [0.013, -0.004, 0.005]], dtype=np.float64)


@pytest.mark.parametrize(
    ("method", "function", "kwargs"),
    [
        ("CIE 1976", delta_E_CIE1976, {}),
        ("cie1976", delta_E_CIE1976, {}),
        ("CIE 1994", delta_E_CIE1994, {"textiles": True}),
        ("cie1994", delta_E_CIE1994, {"textiles": True}),
        ("CIE 2000", delta_E_CIE2000, {"textiles": True}),
        ("cie2000", delta_E_CIE2000, {"textiles": True}),
        ("CIEDE2000", delta_E_CIE2000, {"textiles": True}),
        ("CMC", delta_E_CMC, {"l": 1, "c": 1}),
        ("CAM02-UCS", delta_E_CAM02UCS, {}),
        ("CAM02UCS", delta_E_CAM02UCS, {}),
        ("CAM02-LCD", delta_E_CAM02LCD, {}),
        ("CAM02LCD", delta_E_CAM02LCD, {}),
        ("CAM02-SCD", delta_E_CAM02SCD, {}),
        ("CAM02SCD", delta_E_CAM02SCD, {}),
        ("CAM16-UCS", delta_E_CAM16UCS, {}),
        ("CAM16UCS", delta_E_CAM16UCS, {}),
        ("CAM16-LCD", delta_E_CAM16LCD, {}),
        ("CAM16LCD", delta_E_CAM16LCD, {}),
        ("CAM16-SCD", delta_E_CAM16SCD, {}),
        ("CAM16SCD", delta_E_CAM16SCD, {}),
        ("Oklab", delta_E_Oklab, {}),
        ("OKLab", delta_E_Oklab, {}),
        ("OKLAB", delta_E_Oklab, {}),
        ("Jzazbz", delta_E_Jzazbz, {}),
        ("JzAzBz", delta_E_Jzazbz, {}),
    ],
)
def test_delta_e_dispatch_and_aliases(method, function, kwargs):
    if method.startswith("CAM"):
        a = JPAPBP_BATCH_1
        b = JPAPBP_BATCH_2
    elif method.casefold().startswith("oklab"):
        a = OKLAB_BATCH_1
        b = OKLAB_BATCH_2
    elif method.casefold().startswith("jz"):
        a = JZAZBZ_BATCH_1
        b = JZAZBZ_BATCH_2
    else:
        a = LAB_BATCH_1
        b = LAB_BATCH_2
    np.testing.assert_allclose(
        delta_E(a, b, method=method, **kwargs),
        function(a, b, **kwargs),
    )


def test_dispatch_filters_unused_kwargs():
    np.testing.assert_allclose(
        delta_E(LAB_BATCH_1, LAB_BATCH_2, method="CIE 1976", textiles=True, l=1),
        delta_E_CIE1976(LAB_BATCH_1, LAB_BATCH_2),
    )


def test_delta_e_methods_registry_is_read_only():
    assert set(DELTA_E_METHODS) == {
        "CIE 1976",
        "CIE 1994",
        "CIE 2000",
        "CMC",
        "CAM02-UCS",
        "CAM02-LCD",
        "CAM02-SCD",
        "CAM16-UCS",
        "CAM16-LCD",
        "CAM16-SCD",
        "Oklab",
        "Jzazbz",
    }
    with pytest.raises(TypeError):
        DELTA_E_METHODS["Other"] = delta_E_CIE1976  # type: ignore[index]


def test_unknown_method_raises():
    with pytest.raises(ValueError, match="unknown delta E method"):
        delta_E(LAB_BATCH_1, LAB_BATCH_2, method="DIN99")
