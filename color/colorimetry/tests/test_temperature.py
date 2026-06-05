"""Tests for correlated colour temperature helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.colorimetry import (
    CCT_Duv_to_xy,
    CCT_to_mired,
    CCT_to_uv,
    CCT_to_xy,
    CCT_to_xy_CIE_D,
    TemperatureAnalysis,
    XYZ_to_uv1960,
    analyze_temperature,
    mired_to_CCT,
    uv1960_to_xy,
    uv_to_CCT,
    xy_to_CCT,
    xy_to_CCT_Duv,
    xy_to_uv1960,
)
from color.colorimetry.temperature import (
    CCT_to_uv_Ohno2013,
    CCT_to_uv_Robertson1968,
    planckian_table_Ohno2013,
    uv_to_CCT_Ohno2013,
    uv_to_CCT_Robertson1968,
    xy_to_CCT_McCamy1992,
)


def test_CCT_to_mired():
    assert CCT_to_mired(6500.0) == pytest.approx(153.8461538)


def test_mired_to_CCT():
    assert mired_to_CCT(153.8461538) == pytest.approx(6500.0, abs=1e-5)


def test_xy_to_CCT_McCamy1992():
    assert xy_to_CCT_McCamy1992([0.31270, 0.32900]) == pytest.approx(6505.0806)


def test_CCT_to_xy_CIE_D():
    np.testing.assert_allclose(
        CCT_to_xy_CIE_D(6504.38938305),
        [0.3127077, 0.3291128],
        atol=5e-7,
    )


def test_dispatch_helpers_match_direct_functions():
    xy = [0.31270, 0.32900]
    cct = 6504.38938305

    assert xy_to_CCT(xy, method="mccamy1992") == pytest.approx(
        xy_to_CCT_McCamy1992(xy)
    )
    np.testing.assert_allclose(CCT_to_xy(cct, method="cie_d"), CCT_to_xy_CIE_D(cct))
    np.testing.assert_allclose(CCT_to_xy(cct, method="daylight"), CCT_to_xy_CIE_D(cct))


def test_batch_input_preserves_shape():
    cct = np.array([5000.0, 6504.38938305, 7500.0])
    xy = CCT_to_xy_CIE_D(cct)
    recovered = xy_to_CCT_McCamy1992(xy)

    assert xy.shape == (3, 2)
    assert recovered.shape == (3,)


def test_xy_to_uv1960_and_back_round_trip():
    xy = np.array([
        [0.31270, 0.32900],
        [0.34567, 0.35850],
    ])
    uv = xy_to_uv1960(xy)
    recovered = uv1960_to_xy(uv)

    assert uv.shape == (2, 2)
    np.testing.assert_allclose(recovered, xy, atol=1e-12)


def test_XYZ_to_uv1960_matches_xy_path():
    XYZ = np.array([0.95047, 1.0, 1.08883])
    xy = np.array([XYZ[0] / np.sum(XYZ), XYZ[1] / np.sum(XYZ)])

    np.testing.assert_allclose(XYZ_to_uv1960(XYZ), xy_to_uv1960(xy), atol=1e-12)


def test_uv_to_CCT_Robertson1968_colour_example():
    cct_duv = uv_to_CCT_Robertson1968([0.1978, 0.3122])

    assert cct_duv[0] == pytest.approx(6500.0, abs=20.0)
    assert cct_duv[1] == pytest.approx(0.0032, abs=5e-4)


def test_CCT_to_uv_Robertson1968_colour_example():
    np.testing.assert_allclose(
        CCT_to_uv_Robertson1968([6503.49, 0.00320598]),
        [0.1978, 0.3122],
        atol=5e-4,
    )


def test_robertson_round_trip():
    uv = np.array([
        [0.1978, 0.3122],
        [0.217331111111111, 0.328426666666667],
    ])
    cct_duv = uv_to_CCT_Robertson1968(uv)
    recovered = CCT_to_uv_Robertson1968(cct_duv)

    assert cct_duv.shape == (2, 2)
    assert recovered.shape == (2, 2)
    np.testing.assert_allclose(recovered, uv, atol=1e-6)


def test_CCT_Duv_dispatch_helpers_match_direct_functions():
    uv = [0.1978, 0.3122]
    cct_duv = [6503.49, 0.00320598]
    xy = uv1960_to_xy(uv)

    np.testing.assert_allclose(
        uv_to_CCT(uv, method="robertson1968"),
        uv_to_CCT_Robertson1968(uv),
    )
    np.testing.assert_allclose(
        CCT_to_uv(cct_duv, method="robertson1968"),
        CCT_to_uv_Robertson1968(cct_duv),
    )
    np.testing.assert_allclose(
        xy_to_CCT_Duv(xy, method="robertson1968"),
        uv_to_CCT_Robertson1968(uv),
    )


def test_planckian_table_Ohno2013_is_monotonic():
    table = planckian_table_Ohno2013(start=5000.0, end=6000.0, spacing=1.01)

    assert table.shape[1] == 3
    assert table[0, 0] == pytest.approx(5000.0)
    assert table[-1, 0] == pytest.approx(6000.0)
    assert np.all(np.diff(table[:, 0]) > 0)
    assert np.all(np.isfinite(table))


def test_uv_to_CCT_Ohno2013_colour_example():
    cct_duv = uv_to_CCT_Ohno2013([0.1978, 0.3122])

    assert cct_duv[0] == pytest.approx(6507.47, abs=5.0)
    assert cct_duv[1] == pytest.approx(0.003223, abs=5e-5)


def test_CCT_to_uv_Ohno2013_colour_example():
    np.testing.assert_allclose(
        CCT_to_uv_Ohno2013([6507.47, 0.003223]),
        [0.1978, 0.3122],
        atol=5e-5,
    )


def test_ohno_round_trip():
    uv = np.array([
        [0.1978, 0.3122],
        [0.217331111111111, 0.328426666666667],
    ])
    cct_duv = uv_to_CCT_Ohno2013(uv)
    recovered = CCT_to_uv_Ohno2013(cct_duv)

    assert cct_duv.shape == (2, 2)
    assert recovered.shape == (2, 2)
    np.testing.assert_allclose(recovered, uv, atol=5e-5)


def test_CCT_Duv_dispatch_helpers_accept_ohno():
    uv = [0.1978, 0.3122]
    cct_duv = [6507.47, 0.003223]
    xy = uv1960_to_xy(uv)

    np.testing.assert_allclose(
        uv_to_CCT(uv, method="ohno2013"),
        uv_to_CCT_Ohno2013(uv),
    )
    np.testing.assert_allclose(
        CCT_to_uv(cct_duv, method="ohno2013"),
        CCT_to_uv_Ohno2013(cct_duv),
    )
    np.testing.assert_allclose(
        xy_to_CCT_Duv(xy, method="ohno2013"),
        uv_to_CCT_Ohno2013(uv),
    )


def test_CCT_Duv_to_xy_matches_explicit_uv_path():
    cct_duv = np.array([
        [6503.49, 0.00320598],
        [6507.47, 0.003223],
    ])

    np.testing.assert_allclose(
        CCT_Duv_to_xy(cct_duv[0], method="robertson1968"),
        uv1960_to_xy(CCT_to_uv(cct_duv[0], method="robertson1968")),
    )
    np.testing.assert_allclose(
        CCT_Duv_to_xy(cct_duv, method="ohno2013"),
        uv1960_to_xy(CCT_to_uv(cct_duv, method="ohno2013")),
    )


def test_analyze_temperature_returns_semantic_result():
    xy = uv1960_to_xy([0.1978, 0.3122])
    result = analyze_temperature(xy, method="ohno2013")

    assert isinstance(result, TemperatureAnalysis)
    assert result.CCT == pytest.approx(6507.47, abs=5.0)
    assert result.Duv == pytest.approx(0.003223, abs=5e-5)
    assert result.method == "ohno2013"
    assert result.locus == "planckian"
    np.testing.assert_allclose(result.uv, [0.1978, 0.3122], atol=1e-12)
    np.testing.assert_allclose(result.xy, xy, atol=5e-5)


def test_analyze_temperature_preserves_batch_shape():
    xy = uv1960_to_xy(np.array([
        [0.1978, 0.3122],
        [0.217331111111111, 0.328426666666667],
    ]))
    result = analyze_temperature(xy, method="robertson1968")

    assert result.CCT.shape == (2,)
    assert result.Duv.shape == (2,)
    assert result.xy.shape == (2, 2)
    assert result.uv.shape == (2, 2)


def test_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="CCT must be finite"):
        CCT_to_mired(np.nan)
    with pytest.raises(ValueError, match="mired must be finite"):
        mired_to_CCT(np.inf)
    with pytest.raises(ValueError, match="CCT must be non-zero"):
        CCT_to_mired(0.0)
    with pytest.raises(ValueError, match="mired must be non-zero"):
        mired_to_CCT(0.0)
    with pytest.raises(ValueError, match="2 values"):
        xy_to_CCT_McCamy1992([0.3, 0.3, 0.4])
    with pytest.raises(ValueError, match="zero denominator"):
        xy_to_CCT_McCamy1992([0.3, 0.1858])
    with pytest.raises(ValueError, match=r"\[4000, 25000\]"):
        CCT_to_xy_CIE_D(3000.0)
    with pytest.raises(ValueError, match="method"):
        xy_to_CCT([0.3, 0.3], method="unknown")
    with pytest.raises(ValueError, match="method"):
        CCT_to_xy(6500.0, method="unknown")
    with pytest.raises(ValueError, match="2 values"):
        xy_to_uv1960([0.3, 0.3, 0.4])
    with pytest.raises(ValueError, match="zero denominator"):
        uv1960_to_xy([2.0, 1.0])
    with pytest.raises(ValueError, match="3 values"):
        XYZ_to_uv1960([1.0, 1.0])
    with pytest.raises(ValueError, match="method"):
        uv_to_CCT([0.2, 0.3], method="unknown")
    with pytest.raises(ValueError, match="method"):
        CCT_to_uv([6500.0, 0.0], method="unknown")
    with pytest.raises(ValueError, match="method"):
        CCT_Duv_to_xy([6500.0, 0.0], method="unknown")
    with pytest.raises(ValueError, match="finite"):
        uv_to_CCT_Robertson1968([np.nan, 0.3])
    with pytest.raises(ValueError, match="finite"):
        uv_to_CCT_Ohno2013([np.nan, 0.3])
    with pytest.raises(ValueError, match="positive"):
        CCT_to_uv_Ohno2013([0.0, 0.0])
    with pytest.raises(ValueError, match="greater than 1"):
        planckian_table_Ohno2013(spacing=1.0)
