"""CAM16-UCS, CAM16-LCD and CAM16-SCD colour-space helpers."""

from __future__ import annotations

from types import MappingProxyType
from typing import Sequence

import numpy as np

from color.appearance import (
    CIECAM16Specification,
    CIECAM16_to_XYZ,
    InductionFactors_CIECAM16,
    XYZ_to_CIECAM16,
)

from ._cam_ucs import Coefficients_UCS_Luo2006, JMh_to_UCS, UCS_to_JMh
from ..node import ColorSpaceNode


COEFFICIENTS_UCS_LI2017 = MappingProxyType(
    {
        "CAM16-UCS": Coefficients_UCS_Luo2006(K_L=1.0, c_1=0.007, c_2=0.0228),
        "CAM16-LCD": Coefficients_UCS_Luo2006(K_L=0.77, c_1=0.007, c_2=0.0053),
        "CAM16-SCD": Coefficients_UCS_Luo2006(K_L=1.24, c_1=0.007, c_2=0.0363),
    }
)


def JMh_CIECAM16_to_CAM16UCS(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM16 ``J, M, h`` correlates to CAM16-UCS ``J', a', b'``.

    The input is already in CIECAM16 appearance-correlate space; viewing
    conditions are not used by this helper. Use ``XYZ_to_CAM16UCS`` when
    starting from XYZ values.

    Parameters
    ----------
    JMh
        CIECAM16 correlates with final axis ``(J, M, h)``.

    Returns
    -------
    numpy.ndarray
        CAM16-UCS values with final axis ``(J', a', b')``.

    Notes
    -----
    This helper only applies the Li 2017 UCS transform and does not run the
    CIECAM16 appearance model.
    """
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LI2017["CAM16-UCS"])


def CAM16UCS_to_JMh_CIECAM16(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM16-UCS ``J', a', b'`` coordinates to CIECAM16 ``J, M, h``.

    The returned final axis is ``J, M, h`` with hue in degrees. Converting those
    correlates back to XYZ still requires the same CIECAM16 viewing conditions.

    Parameters
    ----------
    Jpapbp
        CAM16-UCS values with final axis ``(J', a', b')``.

    Returns
    -------
    numpy.ndarray
        CIECAM16 correlates with final axis ``(J, M, h)``.

    Notes
    -----
    This is the inverse Li 2017 UCS transform, not the inverse CIECAM16 model.
    """
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LI2017["CAM16-UCS"])


def JMh_CIECAM16_to_CAM16LCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM16 ``J, M, h`` correlates to CAM16-LCD ``J', a', b'``.

    Notes
    -----
    CAM16-LCD uses the same input/output axes as CAM16-UCS but with the
    large-colour-difference Li 2017 coefficient set.
    """
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LI2017["CAM16-LCD"])


def CAM16LCD_to_JMh_CIECAM16(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM16-LCD ``J', a', b'`` coordinates to CIECAM16 ``J, M, h``.

    Notes
    -----
    This is the inverse large-colour-difference coefficient transform.
    """
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LI2017["CAM16-LCD"])


def JMh_CIECAM16_to_CAM16SCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM16 ``J, M, h`` correlates to CAM16-SCD ``J', a', b'``.

    Notes
    -----
    CAM16-SCD uses the same input/output axes as CAM16-UCS but with the
    small-colour-difference Li 2017 coefficient set.
    """
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LI2017["CAM16-SCD"])


def CAM16SCD_to_JMh_CIECAM16(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM16-SCD ``J', a', b'`` coordinates to CIECAM16 ``J, M, h``.

    Notes
    -----
    This is the inverse small-colour-difference coefficient transform.
    """
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LI2017["CAM16-SCD"])


def _XYZ_to_CAM16(
    XYZ: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to a CAM16 uniform colour space."""
    spec = XYZ_to_CIECAM16(
        XYZ,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )
    JMh = np.stack((spec.J, spec.M, spec.h), axis=-1)
    return converter(JMh)


def _CAM16_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert a CAM16 uniform colour space to XYZ values."""
    JMh = converter(Jpapbp)
    return CIECAM16_to_XYZ(
        CIECAM16Specification(J=JMh[..., 0], M=JMh[..., 1], h=JMh[..., 2]),
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM16UCS(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM16-UCS coordinates.

    ``XYZ``, ``XYZ_w`` and ``Y_b`` must use one consistent luminance scale,
    normally the project Y=100 domain. The viewing-condition parameters are
    passed directly to CIECAM16; no implicit chromatic adaptation is performed.

    Parameters
    ----------
    XYZ
        XYZ tristimulus values with final axis ``(X, Y, Z)``.
    XYZ_w, L_A, Y_b, surround
        CIECAM16 viewing-condition parameters.
    discount_illuminant
        Passed directly to the CIECAM16 model.

    Returns
    -------
    numpy.ndarray
        CAM16-UCS values with final axis ``(J', a', b')``.

    Notes
    -----
    Adapt XYZ explicitly before calling this function if the intended reference
    whitepoint differs from ``XYZ_w``.

    Examples
    --------
    >>> XYZ_to_CAM16UCS([19.01, 20.0, 21.78]).shape
    (3,)
    """
    return _XYZ_to_CAM16(
        XYZ,
        JMh_CIECAM16_to_CAM16UCS,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM16UCS_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM16-UCS coordinates to XYZ values.

    Use the same CIECAM16 viewing conditions that were used for the forward
    conversion. The returned XYZ values use the reference domain implied by
    ``XYZ_w`` and ``Y_b``.

    Parameters
    ----------
    Jpapbp
        CAM16-UCS values with final axis ``(J', a', b')``.
    XYZ_w, L_A, Y_b, surround
        CIECAM16 viewing-condition parameters.
    discount_illuminant
        Passed directly to the CIECAM16 inverse model.

    Returns
    -------
    numpy.ndarray
        XYZ tristimulus values with final axis ``(X, Y, Z)``.

    Notes
    -----
    The viewing-condition parameters are part of the colour-space definition for
    a round-trip; changing them changes the inverse interpretation.

    Examples
    --------
    >>> CAM16UCS_to_XYZ([50.0, 1.0, 2.0]).shape
    (3,)
    """
    return _CAM16_to_XYZ(
        Jpapbp,
        CAM16UCS_to_JMh_CIECAM16,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM16LCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM16-LCD coordinates.

    CAM16-LCD uses the Li 2017 large-colour-difference coefficients. Viewing
    conditions and XYZ reference-domain rules match ``XYZ_to_CAM16UCS``.

    Notes
    -----
    The output final axis is ``(J', a', b')``. Use matching LCD inverse
    functions for round-trips.
    """
    return _XYZ_to_CAM16(
        XYZ,
        JMh_CIECAM16_to_CAM16LCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM16LCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM16-LCD coordinates to XYZ values.

    Use the same viewing conditions as the forward CAM16-LCD conversion to
    preserve round-trip consistency.

    Notes
    -----
    The input final axis is ``(J', a', b')`` and the output final axis is
    ``(X, Y, Z)``.
    """
    return _CAM16_to_XYZ(
        Jpapbp,
        CAM16LCD_to_JMh_CIECAM16,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM16SCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM16-SCD coordinates.

    CAM16-SCD uses the Li 2017 small-colour-difference coefficients. Viewing
    conditions and XYZ reference-domain rules match ``XYZ_to_CAM16UCS``.

    Notes
    -----
    The output final axis is ``(J', a', b')``. Use matching SCD inverse
    functions for round-trips.
    """
    return _XYZ_to_CAM16(
        XYZ,
        JMh_CIECAM16_to_CAM16SCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM16SCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM16 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM16-SCD coordinates to XYZ values.

    Use the same viewing conditions as the forward CAM16-SCD conversion to
    preserve round-trip consistency.

    Notes
    -----
    The input final axis is ``(J', a', b')`` and the output final axis is
    ``(X, Y, Z)``.
    """
    return _CAM16_to_XYZ(
        Jpapbp,
        CAM16SCD_to_JMh_CIECAM16,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


SPACE_NODES = (
    ColorSpaceNode(
        name="CAM16-UCS",
        aliases=("CAM16UCS", "CAM16 UCS"),
        to_XYZ=CAM16UCS_to_XYZ,
        from_XYZ=XYZ_to_CAM16UCS,
        family="CAM16",
    ),
    ColorSpaceNode(
        name="CAM16-LCD",
        aliases=("CAM16LCD", "CAM16 LCD"),
        to_XYZ=CAM16LCD_to_XYZ,
        from_XYZ=XYZ_to_CAM16LCD,
        family="CAM16",
    ),
    ColorSpaceNode(
        name="CAM16-SCD",
        aliases=("CAM16SCD", "CAM16 SCD"),
        to_XYZ=CAM16SCD_to_XYZ,
        from_XYZ=XYZ_to_CAM16SCD,
        family="CAM16",
    ),
)


__all__ = [
    "COEFFICIENTS_UCS_LI2017",
    "JMh_CIECAM16_to_CAM16UCS",
    "CAM16UCS_to_JMh_CIECAM16",
    "JMh_CIECAM16_to_CAM16LCD",
    "CAM16LCD_to_JMh_CIECAM16",
    "JMh_CIECAM16_to_CAM16SCD",
    "CAM16SCD_to_JMh_CIECAM16",
    "XYZ_to_CAM16UCS",
    "CAM16UCS_to_XYZ",
    "XYZ_to_CAM16LCD",
    "CAM16LCD_to_XYZ",
    "XYZ_to_CAM16SCD",
    "CAM16SCD_to_XYZ",
    "SPACE_NODES",
]
