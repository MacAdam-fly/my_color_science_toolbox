"""RGB and XYZ conversion helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.adaptation import chromatic_adaptation_XYZ
from color.utils.arrays import as_last_axis_triplets

from .colourspace import RGBColorSpace
from .registry import get_RGB_colourspace
from .transfer import decode_transfer, encode_transfer


def _white_xy_to_XYZ(white_xy: np.ndarray) -> np.ndarray:
    """Return a Y=100 XYZ whitepoint from xy chromaticity coordinates."""
    x, y = np.asarray(white_xy, dtype=np.float64)
    if y <= 0:
        raise ValueError("RGB colour-space whitepoint y must be positive")
    return np.array([100.0 * x / y, 100.0, 100.0 * (1.0 - x - y) / y], dtype=np.float64)


def RGB_to_XYZ(
    RGB: Sequence[float] | np.ndarray,
    *,
    colourspace: str | RGBColorSpace = "sRGB",
    apply_decoding: bool = True,
) -> np.ndarray:
    """Convert RGB values to CIE XYZ tristimulus values.

    Input values use the selected RGB colour-space encoding unless
    ``apply_decoding=False`` is passed. The result is XYZ in the numeric scale
    implied by the RGB matrix, typically the project Y=100 XYZ domain.

    Parameters
    ----------
    RGB
        RGB values with final axis ``(R, G, B)``.
    colourspace
        RGB colour-space name or object.
    apply_decoding
        Decode encoded RGB values to linear RGB before matrix conversion.

    Returns
    -------
    numpy.ndarray
        XYZ tristimulus values with final axis ``(X, Y, Z)``.

    Notes
    -----
    No clipping is applied. Values outside the RGB cube may appear during
    intermediate calculations.

    Examples
    --------
    >>> RGB_to_XYZ([0.4, 0.5, 0.6]).shape
    (3,)
    """
    rgb_space = get_RGB_colourspace(colourspace)
    rgb = as_last_axis_triplets(RGB, name="RGB")
    linear = decode_transfer(rgb, rgb_space.transfer) if apply_decoding else rgb
    return linear @ rgb_space.matrix_RGB_to_XYZ.T


def XYZ_to_RGB(
    XYZ: Sequence[float] | np.ndarray,
    *,
    colourspace: str | RGBColorSpace = "sRGB",
    apply_encoding: bool = True,
) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to RGB values.

    ``XYZ`` must use the numeric scale expected by the selected RGB matrix.
    The returned RGB is encoded by the colour-space transfer function unless
    ``apply_encoding=False`` is passed, in which case linear RGB is returned.

    Parameters
    ----------
    XYZ
        XYZ tristimulus values with final axis ``(X, Y, Z)``.
    colourspace
        RGB colour-space name or object.
    apply_encoding
        Encode linear RGB with the colour-space transfer function.

    Returns
    -------
    numpy.ndarray
        RGB values with final axis ``(R, G, B)``.

    Notes
    -----
    No clipping is applied; callers should clip explicitly for display or image
    output.

    Examples
    --------
    >>> XYZ_to_RGB([19.01, 20.0, 21.78]).shape
    (3,)
    """
    rgb_space = get_RGB_colourspace(colourspace)
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    linear = xyz @ rgb_space.matrix_XYZ_to_RGB.T
    return encode_transfer(linear, rgb_space.transfer) if apply_encoding else linear


def RGB_to_RGB(
    RGB: Sequence[float] | np.ndarray,
    source: str | RGBColorSpace,
    target: str | RGBColorSpace,
    *,
    apply_decoding: bool = True,
    apply_encoding: bool = True,
    chromatic_adaptation: str | None = None,
) -> np.ndarray:
    """Convert RGB values from one RGB colour space to another.

    By default, this is a stimulus-matching conversion through XYZ. If
    *chromatic_adaptation* is provided, source-white XYZ values are adapted to
    the target RGB colour-space white before encoding into the target space.

    Parameters
    ----------
    RGB
        Source RGB values with final axis ``(R, G, B)``.
    source
        Source RGB colour-space name or object.
    target
        Target RGB colour-space name or object.
    chromatic_adaptation
        Optional chromatic-adaptation transform name.

    Returns
    -------
    numpy.ndarray
        Target RGB values.

    Notes
    -----
    This is the RGB-specific route for explicit RGB-to-RGB whitepoint
    adaptation. The generic ``convert_color`` route intentionally does not
    perform hidden chromatic adaptation.

    Examples
    --------
    >>> RGB_to_RGB([0.4, 0.5, 0.6], "sRGB", "Display P3").shape
    (3,)
    """
    source_space = get_RGB_colourspace(source)
    target_space = get_RGB_colourspace(target)

    XYZ = RGB_to_XYZ(
        RGB,
        colourspace=source_space,
        apply_decoding=apply_decoding,
    )
    if chromatic_adaptation is not None:
        XYZ = chromatic_adaptation_XYZ(
            XYZ,
            source_white_XYZ=_white_xy_to_XYZ(source_space.white_xy),
            target_white_XYZ=_white_xy_to_XYZ(target_space.white_xy),
            transform=chromatic_adaptation,
        )

    return XYZ_to_RGB(
        XYZ,
        colourspace=target_space,
        apply_encoding=apply_encoding,
    )


def sRGB_to_XYZ(
    RGB: Sequence[float] | np.ndarray,
    *,
    apply_decoding: bool = True,
) -> np.ndarray:
    """Convert sRGB values to CIE XYZ tristimulus values.

    This is a convenience wrapper around ``RGB_to_XYZ(..., colourspace="sRGB")``.
    Encoded sRGB input is decoded by default and the XYZ result is in the
    project Y=100 domain.

    Parameters
    ----------
    RGB
        Encoded sRGB values with final axis ``(R, G, B)``.
    apply_decoding
        Decode sRGB values before matrix conversion.

    Returns
    -------
    numpy.ndarray
        XYZ tristimulus values on the project Y=100 scale.

    Notes
    -----
    No clipping is applied. This wrapper always uses the registered sRGB
    colour-space definition.

    Examples
    --------
    >>> sRGB_to_XYZ([0.4, 0.5, 0.6]).shape
    (3,)
    """
    return RGB_to_XYZ(RGB, colourspace="sRGB", apply_decoding=apply_decoding)


def XYZ_to_sRGB(
    XYZ: Sequence[float] | np.ndarray,
    *,
    apply_encoding: bool = True,
) -> np.ndarray:
    """Convert CIE XYZ tristimulus values to sRGB values.

    This is a convenience wrapper around ``XYZ_to_RGB(..., colourspace="sRGB")``.
    Input XYZ is expected in the project Y=100 domain and encoded sRGB is
    returned by default.

    Parameters
    ----------
    XYZ
        XYZ tristimulus values on the project Y=100 scale.
    apply_encoding
        Encode linear sRGB with the sRGB transfer function.

    Returns
    -------
    numpy.ndarray
        sRGB values with final axis ``(R, G, B)``.

    Notes
    -----
    No clipping is applied. Clip explicitly before image output when displayable
    encoded sRGB values are required.

    Examples
    --------
    >>> XYZ_to_sRGB([19.01, 20.0, 21.78]).shape
    (3,)
    """
    return XYZ_to_RGB(XYZ, colourspace="sRGB", apply_encoding=apply_encoding)


__all__ = [
    "RGB_to_XYZ",
    "XYZ_to_RGB",
    "RGB_to_RGB",
    "sRGB_to_XYZ",
    "XYZ_to_sRGB",
]
