from __future__ import annotations

import numpy as np
import pytest

from color.appearance import (
    VIEWING_CONDITIONS_ZCAM,
    XYZ_to_ZCAM,
    ZCAMSpecification,
    ZCAMViewingConditions,
    ZCAM_to_XYZ,
)


EXAMPLE_XYZ = np.array([185.0, 206.0, 163.0])
EXAMPLE_WHITE = np.array([256.0, 264.0, 202.0])


def test_xyz_to_zcam_matches_colour_reference_values() -> None:
    specification = XYZ_to_ZCAM(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=264.0, Y_b=100.0)

    assert specification.J == pytest.approx(92.250443780723629, abs=1e-12)
    assert specification.C == pytest.approx(3.0216926733329013, abs=1e-12)
    assert specification.h == pytest.approx(196.32457375575581, abs=1e-12)
    assert specification.s == pytest.approx(19.131955645510477, abs=1e-12)
    assert specification.Q == pytest.approx(321.34084639067481, abs=1e-12)
    assert specification.M == pytest.approx(10.525621789845429, abs=1e-12)
    assert specification.H == pytest.approx(237.61144426724456, abs=1e-12)
    assert specification.HC is None
    assert specification.V == pytest.approx(34.700677654154831, abs=1e-12)
    assert specification.K == pytest.approx(25.88359688970526, abs=1e-12)
    assert specification.W == pytest.approx(91.682172867401079, abs=1e-12)


def test_zcam_to_xyz_roundtrips_jch() -> None:
    specification = XYZ_to_ZCAM(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=264.0, Y_b=100.0)

    recovered = ZCAM_to_XYZ(
        ZCAMSpecification(J=specification.J, C=specification.C, h=specification.h),
        EXAMPLE_WHITE,
        L_A=264.0,
        Y_b=100.0,
    )

    np.testing.assert_allclose(recovered, EXAMPLE_XYZ, atol=1e-8)


def test_zcam_to_xyz_accepts_m_instead_of_c() -> None:
    specification = XYZ_to_ZCAM(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=264.0, Y_b=100.0)

    recovered = ZCAM_to_XYZ(
        ZCAMSpecification(J=specification.J, M=specification.M, h=specification.h),
        EXAMPLE_WHITE,
        L_A=264.0,
        Y_b=100.0,
    )

    np.testing.assert_allclose(recovered, EXAMPLE_XYZ, atol=1e-8)


def test_viewing_conditions_container_is_accepted() -> None:
    conditions = ZCAMViewingConditions(
        XYZ_w=EXAMPLE_WHITE,
        L_A=264.0,
        Y_b=100.0,
        surround="Average",
    )

    direct = XYZ_to_ZCAM(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=264.0, Y_b=100.0)
    packaged = XYZ_to_ZCAM(EXAMPLE_XYZ, conditions)

    assert packaged.J == pytest.approx(direct.J)
    assert packaged.C == pytest.approx(direct.C)
    assert packaged.h == pytest.approx(direct.h)


@pytest.mark.parametrize("surround", ["Average", "Dim", "Dark"])
def test_named_surrounds_are_available(surround: str) -> None:
    specification = XYZ_to_ZCAM(
        EXAMPLE_XYZ,
        EXAMPLE_WHITE,
        L_A=264.0,
        Y_b=100.0,
        surround=surround,
    )

    assert surround in VIEWING_CONDITIONS_ZCAM
    assert np.isfinite(specification.J)
    assert np.isfinite(specification.C)
    assert np.isfinite(specification.h)


def test_compute_h_false_skips_hue_quadrature() -> None:
    specification = XYZ_to_ZCAM(
        EXAMPLE_XYZ,
        EXAMPLE_WHITE,
        L_A=264.0,
        Y_b=100.0,
        compute_H=False,
    )

    assert np.isnan(specification.H)


def test_batch_input_preserves_correlate_shapes() -> None:
    XYZ = np.array(
        [
            [185.0, 206.0, 163.0],
            [150.0, 180.0, 210.0],
        ]
    )

    specification = XYZ_to_ZCAM(XYZ, EXAMPLE_WHITE, L_A=264.0, Y_b=100.0)

    for value in (
        specification.J,
        specification.C,
        specification.h,
        specification.s,
        specification.Q,
        specification.M,
        specification.H,
        specification.V,
        specification.K,
        specification.W,
    ):
        assert np.asarray(value).shape == (2,)

    recovered = ZCAM_to_XYZ(
        ZCAMSpecification(J=specification.J, C=specification.C, h=specification.h),
        EXAMPLE_WHITE,
        L_A=264.0,
        Y_b=100.0,
    )
    np.testing.assert_allclose(recovered, XYZ, atol=1e-8)


def test_invalid_surround_raises() -> None:
    with pytest.raises(ValueError, match="surround"):
        XYZ_to_ZCAM(EXAMPLE_XYZ, EXAMPLE_WHITE, L_A=264.0, Y_b=100.0, surround="Unknown")


@pytest.mark.parametrize(
    "XYZ",
    [
        [1.0, 2.0],
        [1.0, np.nan, 3.0],
    ],
)
def test_invalid_xyz_raises(XYZ: list[float]) -> None:
    with pytest.raises(ValueError, match="XYZ"):
        XYZ_to_ZCAM(XYZ)


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
        XYZ_to_ZCAM(EXAMPLE_XYZ, XYZ_w)


def test_inverse_requires_j_h_and_c_or_m() -> None:
    with pytest.raises(ValueError, match="J"):
        ZCAM_to_XYZ(ZCAMSpecification(C=1.0, h=20.0))

    with pytest.raises(ValueError, match="C or"):
        ZCAM_to_XYZ(ZCAMSpecification(J=50.0, h=20.0))


def test_inverse_rejects_non_specification() -> None:
    with pytest.raises(ValueError, match="specification"):
        ZCAM_to_XYZ({"J": 50.0, "C": 1.0, "h": 20.0})
