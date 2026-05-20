from __future__ import annotations

import numpy as np
import pytest

from color.appearance import (
    CIECAM02Specification,
    CIECAM02ViewingConditions,
    CIECAM02_to_XYZ,
    VIEWING_CONDITIONS_CIECAM02,
    XYZ_to_CIECAM02,
)


EXAMPLE_XYZ = np.array([19.01, 20.0, 21.78])
EXAMPLE_WHITE = np.array([95.05, 100.0, 108.88])


def test_xyz_to_ciecam02_matches_colour_reference_example() -> None:
    specification = XYZ_to_CIECAM02(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=318.31, Y_b=20.0)

    assert specification.J == pytest.approx(41.7310911325, abs=1e-10)
    assert specification.C == pytest.approx(0.104707757171, abs=1e-10)
    assert specification.h == pytest.approx(219.048432658, abs=1e-9)
    assert specification.s == pytest.approx(2.36030537392, abs=1e-10)
    assert specification.Q == pytest.approx(195.371325966, abs=1e-10)
    assert specification.M == pytest.approx(0.108842175669, abs=1e-10)
    assert specification.H == pytest.approx(278.060735856, abs=1e-9)
    assert specification.HC is None


def test_ciecam02_to_xyz_roundtrips_jch() -> None:
    specification = XYZ_to_CIECAM02(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=318.31, Y_b=20.0)

    recovered = CIECAM02_to_XYZ(
        CIECAM02Specification(J=specification.J, C=specification.C, h=specification.h),
        EXAMPLE_WHITE,
        L_A=318.31,
        Y_b=20.0,
    )

    np.testing.assert_allclose(recovered, EXAMPLE_XYZ, atol=1e-10)


def test_ciecam02_to_xyz_accepts_m_instead_of_c() -> None:
    specification = XYZ_to_CIECAM02(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=318.31, Y_b=20.0)

    recovered = CIECAM02_to_XYZ(
        CIECAM02Specification(J=specification.J, M=specification.M, h=specification.h),
        EXAMPLE_WHITE,
        L_A=318.31,
        Y_b=20.0,
    )

    np.testing.assert_allclose(recovered, EXAMPLE_XYZ, atol=1e-10)


def test_viewing_conditions_container_is_accepted() -> None:
    conditions = CIECAM02ViewingConditions(
        XYZ_w=EXAMPLE_WHITE,
        L_A=318.31,
        Y_b=20.0,
        surround="Average",
    )

    direct = XYZ_to_CIECAM02(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=318.31, Y_b=20.0)
    packaged = XYZ_to_CIECAM02(EXAMPLE_XYZ, conditions)

    assert packaged.J == pytest.approx(direct.J)
    assert packaged.C == pytest.approx(direct.C)
    assert packaged.h == pytest.approx(direct.h)


@pytest.mark.parametrize("surround", ["Average", "Dim", "Dark"])
def test_named_surrounds_are_available(surround: str) -> None:
    specification = XYZ_to_CIECAM02(
        EXAMPLE_XYZ,
        EXAMPLE_WHITE,
        L_A=318.31,
        Y_b=20.0,
        surround=surround,
    )

    assert surround in VIEWING_CONDITIONS_CIECAM02
    assert np.isfinite(specification.J)
    assert np.isfinite(specification.C)
    assert np.isfinite(specification.h)


def test_batch_input_preserves_correlate_shapes() -> None:
    XYZ = np.array(
        [
            [19.01, 20.0, 21.78],
            [57.06, 43.06, 31.96],
        ]
    )

    specification = XYZ_to_CIECAM02(XYZ, EXAMPLE_WHITE, L_A=318.31, Y_b=20.0)

    assert np.asarray(specification.J).shape == (2,)
    assert np.asarray(specification.C).shape == (2,)
    assert np.asarray(specification.h).shape == (2,)

    recovered = CIECAM02_to_XYZ(
        CIECAM02Specification(J=specification.J, C=specification.C, h=specification.h),
        EXAMPLE_WHITE,
        L_A=318.31,
        Y_b=20.0,
    )
    np.testing.assert_allclose(recovered, XYZ, atol=1e-10)


def test_invalid_surround_raises() -> None:
    with pytest.raises(ValueError, match="surround"):
        XYZ_to_CIECAM02(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=318.31, Y_b=20.0, surround="Unknown")


@pytest.mark.parametrize(
    "XYZ",
    [
        [1.0, 2.0],
        [1.0, np.nan, 3.0],
    ],
)
def test_invalid_xyz_raises(XYZ: list[float]) -> None:
    with pytest.raises(ValueError, match="XYZ"):
        XYZ_to_CIECAM02(XYZ)


@pytest.mark.parametrize(
    "XYZ_w",
    [
        [95.0, 100.0],
        [95.0, 0.0, 108.0],
        [95.0, np.nan, 108.0],
    ],
)
def test_invalid_whitepoint_raises(XYZ_w: list[float]) -> None:
    with pytest.raises(ValueError, match="XYZ_w"):
        XYZ_to_CIECAM02(EXAMPLE_XYZ, XYZ_w)


def test_inverse_requires_j_h_and_c_or_m() -> None:
    with pytest.raises(ValueError, match="J"):
        CIECAM02_to_XYZ(CIECAM02Specification(C=1.0, h=20.0))

    with pytest.raises(ValueError, match="C or"):
        CIECAM02_to_XYZ(CIECAM02Specification(J=50.0, h=20.0))


def test_inverse_rejects_non_specification() -> None:
    with pytest.raises(ValueError, match="specification"):
        CIECAM02_to_XYZ({"J": 50.0, "C": 1.0, "h": 20.0})
