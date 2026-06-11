"""CAM02-UCS, CAM02-LCD and CAM02-SCD colour-space helpers."""

from __future__ import annotations

from types import MappingProxyType
from typing import Sequence

import numpy as np

from color.appearance import (
    CIECAM02Specification,
    CIECAM02_to_XYZ,
    InductionFactors_CIECAM02,
    XYZ_to_CIECAM02,
)

from ._cam_ucs import Coefficients_UCS_Luo2006, JMh_to_UCS, UCS_to_JMh
from ..node import ColorSpaceNode


COEFFICIENTS_UCS_LUO2006 = MappingProxyType(
    {
        "CAM02-UCS": Coefficients_UCS_Luo2006(K_L=1.0, c_1=0.007, c_2=0.0228),
        "CAM02-LCD": Coefficients_UCS_Luo2006(K_L=0.77, c_1=0.007, c_2=0.0053),
        "CAM02-SCD": Coefficients_UCS_Luo2006(K_L=1.24, c_1=0.007, c_2=0.0363),
    }
)


def JMh_CIECAM02_to_CAM02UCS(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 ``J, M, h`` correlates to CAM02-UCS ``J', a', b'``.

    The input is already in CIECAM02 appearance-correlate space; viewing
    conditions are not used by this helper. Use ``XYZ_to_CAM02UCS`` when
    starting from XYZ values.

    Parameters
    ----------
    JMh
        CIECAM02 correlates with final axis ``(J, M, h)``.

    Returns
    -------
    numpy.ndarray
        CAM02-UCS values with final axis ``(J', a', b')``.

    Notes
    -----
    This helper only applies the Luo 2006 UCS transform and does not run the
    CIECAM02 appearance model.
    """
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-UCS"])


def CAM02UCS_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-UCS ``J', a', b'`` coordinates to CIECAM02 ``J, M, h``.

    The returned final axis is ``J, M, h`` with hue in degrees. Converting those
    correlates back to XYZ still requires the same CIECAM02 viewing conditions.

    Parameters
    ----------
    Jpapbp
        CAM02-UCS values with final axis ``(J', a', b')``.

    Returns
    -------
    numpy.ndarray
        CIECAM02 correlates with final axis ``(J, M, h)``.

    Notes
    -----
    This is the inverse Luo 2006 UCS transform, not the inverse CIECAM02 model.
    """
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-UCS"])


def JMh_CIECAM02_to_CAM02LCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 ``J, M, h`` correlates to CAM02-LCD ``J', a', b'``.

    Notes
    -----
    CAM02-LCD uses the same input/output axes as CAM02-UCS but with the
    large-colour-difference Luo 2006 coefficient set.
    """
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-LCD"])


def CAM02LCD_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-LCD ``J', a', b'`` coordinates to CIECAM02 ``J, M, h``.

    Notes
    -----
    This is the inverse large-colour-difference coefficient transform.
    """
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-LCD"])


def JMh_CIECAM02_to_CAM02SCD(JMh: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CIECAM02 ``J, M, h`` correlates to CAM02-SCD ``J', a', b'``.

    Notes
    -----
    CAM02-SCD uses the same input/output axes as CAM02-UCS but with the
    small-colour-difference Luo 2006 coefficient set.
    """
    return JMh_to_UCS(JMh, COEFFICIENTS_UCS_LUO2006["CAM02-SCD"])


def CAM02SCD_to_JMh_CIECAM02(Jpapbp: Sequence[float] | np.ndarray) -> np.ndarray:
    """Convert CAM02-SCD ``J', a', b'`` coordinates to CIECAM02 ``J, M, h``.

    Notes
    -----
    This is the inverse small-colour-difference coefficient transform.
    """
    return UCS_to_JMh(Jpapbp, COEFFICIENTS_UCS_LUO2006["CAM02-SCD"])


def _XYZ_to_CAM02(
    XYZ: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to a CAM02 uniform colour space."""
    spec = XYZ_to_CIECAM02(
        XYZ,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )
    JMh = np.stack((spec.J, spec.M, spec.h), axis=-1)
    return converter(JMh)


def _CAM02_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    converter,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert a CAM02 uniform colour space to XYZ values."""
    JMh = converter(Jpapbp)
    return CIECAM02_to_XYZ(
        CIECAM02Specification(J=JMh[..., 0], M=JMh[..., 1], h=JMh[..., 2]),
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM02UCS(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM02-UCS coordinates.

    ``XYZ``, ``XYZ_w`` and ``Y_b`` must use one consistent luminance scale,
    normally the project Y=100 domain. The viewing-condition parameters are
    passed directly to CIECAM02; no implicit chromatic adaptation is performed.

    Parameters
    ----------
    XYZ
        XYZ tristimulus values with final axis ``(X, Y, Z)``.
    XYZ_w, L_A, Y_b, surround
        CIECAM02 viewing-condition parameters.
    discount_illuminant
        Passed directly to the CIECAM02 model.

    Returns
    -------
    numpy.ndarray
        CAM02-UCS values with final axis ``(J', a', b')``.

    Notes
    -----
    Adapt XYZ explicitly before calling this function if the intended reference
    whitepoint differs from ``XYZ_w``.

    Examples
    --------
    >>> XYZ_to_CAM02UCS([19.01, 20.0, 21.78]).shape
    (3,)
    """
    return _XYZ_to_CAM02(
        XYZ,
        JMh_CIECAM02_to_CAM02UCS,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM02UCS_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM02-UCS coordinates to XYZ values.

    Use the same CIECAM02 viewing conditions that were used for the forward
    conversion. The returned XYZ values use the reference domain implied by
    ``XYZ_w`` and ``Y_b``.

    Parameters
    ----------
    Jpapbp
        CAM02-UCS values with final axis ``(J', a', b')``.
    XYZ_w, L_A, Y_b, surround
        CIECAM02 viewing-condition parameters.
    discount_illuminant
        Passed directly to the CIECAM02 inverse model.

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
    >>> CAM02UCS_to_XYZ([50.0, 1.0, 2.0]).shape
    (3,)
    """
    return _CAM02_to_XYZ(
        Jpapbp,
        CAM02UCS_to_JMh_CIECAM02,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM02LCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM02-LCD coordinates.

    CAM02-LCD uses the Luo 2006 large-colour-difference coefficients. Viewing
    conditions and XYZ reference-domain rules match ``XYZ_to_CAM02UCS``.

    Notes
    -----
    The output final axis is ``(J', a', b')``. Use matching LCD inverse
    functions for round-trips.
    """
    return _XYZ_to_CAM02(
        XYZ,
        JMh_CIECAM02_to_CAM02LCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM02LCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM02-LCD coordinates to XYZ values.

    Use the same viewing conditions as the forward CAM02-LCD conversion to
    preserve round-trip consistency.

    Notes
    -----
    The input final axis is ``(J', a', b')`` and the output final axis is
    ``(X, Y, Z)``.
    """
    return _CAM02_to_XYZ(
        Jpapbp,
        CAM02LCD_to_JMh_CIECAM02,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def XYZ_to_CAM02SCD(
    XYZ: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert XYZ values to CAM02-SCD coordinates.

    CAM02-SCD uses the Luo 2006 small-colour-difference coefficients. Viewing
    conditions and XYZ reference-domain rules match ``XYZ_to_CAM02UCS``.

    Notes
    -----
    The output final axis is ``(J', a', b')``. Use matching SCD inverse
    functions for round-trips.
    """
    return _XYZ_to_CAM02(
        XYZ,
        JMh_CIECAM02_to_CAM02SCD,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


def CAM02SCD_to_XYZ(
    Jpapbp: Sequence[float] | np.ndarray,
    *,
    XYZ_w=None,
    L_A=None,
    Y_b=None,
    surround: str | InductionFactors_CIECAM02 | None = None,
    discount_illuminant: bool | None = None,
) -> np.ndarray:
    """Convert CAM02-SCD coordinates to XYZ values.

    Use the same viewing conditions as the forward CAM02-SCD conversion to
    preserve round-trip consistency.

    Notes
    -----
    The input final axis is ``(J', a', b')`` and the output final axis is
    ``(X, Y, Z)``.
    """
    return _CAM02_to_XYZ(
        Jpapbp,
        CAM02SCD_to_JMh_CIECAM02,
        XYZ_w=XYZ_w,
        L_A=L_A,
        Y_b=Y_b,
        surround=surround,
        discount_illuminant=discount_illuminant,
    )


SPACE_NODES = (
    ColorSpaceNode(
        name="CAM02-UCS",
        aliases=("CAM02UCS", "CAM02 UCS"),
        to_XYZ=CAM02UCS_to_XYZ,
        from_XYZ=XYZ_to_CAM02UCS,
        family="CAM02",
    ),
    ColorSpaceNode(
        name="CAM02-LCD",
        aliases=("CAM02LCD", "CAM02 LCD"),
        to_XYZ=CAM02LCD_to_XYZ,
        from_XYZ=XYZ_to_CAM02LCD,
        family="CAM02",
    ),
    ColorSpaceNode(
        name="CAM02-SCD",
        aliases=("CAM02SCD", "CAM02 SCD"),
        to_XYZ=CAM02SCD_to_XYZ,
        from_XYZ=XYZ_to_CAM02SCD,
        family="CAM02",
    ),
)


__all__ = [
    "Coefficients_UCS_Luo2006",
    "COEFFICIENTS_UCS_LUO2006",
    "JMh_CIECAM02_to_CAM02UCS",
    "CAM02UCS_to_JMh_CIECAM02",
    "JMh_CIECAM02_to_CAM02LCD",
    "CAM02LCD_to_JMh_CIECAM02",
    "JMh_CIECAM02_to_CAM02SCD",
    "CAM02SCD_to_JMh_CIECAM02",
    "XYZ_to_CAM02UCS",
    "CAM02UCS_to_XYZ",
    "XYZ_to_CAM02LCD",
    "CAM02LCD_to_XYZ",
    "XYZ_to_CAM02SCD",
    "CAM02SCD_to_XYZ",
    "SPACE_NODES",
]
