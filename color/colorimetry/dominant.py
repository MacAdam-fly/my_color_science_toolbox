"""Dominant wavelength, complementary wavelength and purity in CIE xy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple, Sequence, Union

import numpy as np

from color.spectra import MultiSpectralDistribution, from_dataset
from color.utils.arrays import as_last_axis_pairs


LocusSource = Union[str, MultiSpectralDistribution]
DEFAULT_LOCUS = "cie1931_chro_1nm"
DEFAULT_WHITEPOINT_XY = (0.3127, 0.3290)
_EPSILON = 1e-12


class _Intersection(NamedTuple):
    wavelength: float
    xy: np.ndarray
    is_purple: bool
    t: float


@dataclass(frozen=True)
class ChromaticityAnalysis:
    """Complete dominant-wavelength and purity analysis in CIE xy.

    Parameters
    ----------
    wavelength
        Dominant wavelength. Negative values use the project convention for
        non-spectral purple directions: the absolute value is the
        complementary spectral wavelength.
    dominant_xy
        Boundary point used for dominant-wavelength and excitation-purity
        geometry.
    complementary_wavelength
        Complementary wavelength using the same signed convention.
    complementary_xy
        Opposite-side boundary point.
    dominant_region, complementary_region
        Region labels such as ``"spectral"``, ``"purple"`` or
        ``"undefined"``.
    excitation_purity, colorimetric_purity
        Purity values for the analysed chromaticity.

    Returns
    -------
    ChromaticityAnalysis
        Frozen dataclass returned by ``analyze_chromaticity``.

    Notes
    -----
    The object is returned by ``analyze_chromaticity`` and is only about
    two-dimensional CIE xy geometry. It does not contain luminance.

    Examples
    --------
    >>> result = analyze_chromaticity([0.45, 0.40])
    >>> result.dominant_region in {"spectral", "purple", "undefined"}
    True
    """

    wavelength: float | np.ndarray
    dominant_xy: np.ndarray
    complementary_wavelength: float | np.ndarray
    complementary_xy: np.ndarray
    dominant_region: str | np.ndarray
    complementary_region: str | np.ndarray
    excitation_purity: float | np.ndarray
    colorimetric_purity: float | np.ndarray


def _load_locus(
    locus: LocusSource,
) -> tuple[np.ndarray, np.ndarray]:
    """Return locus wavelengths and xy coordinates."""
    locus_sd = (
        from_dataset("standard_observers.chromaticity_coordinates", locus)
        if isinstance(locus, str)
        else locus
    )
    if not isinstance(locus_sd, MultiSpectralDistribution):
        raise ValueError("locus must be a MultiSpectralDistribution or dataset name")
    if "x" not in locus_sd.labels or "y" not in locus_sd.labels:
        raise ValueError("locus must contain 'x' and 'y' channels")

    x_index = locus_sd.labels.index("x")
    y_index = locus_sd.labels.index("y")
    xy = locus_sd.values[:, (x_index, y_index)]
    return locus_sd.wavelengths, xy


def _intersect_line_segments(
    p1: np.ndarray,
    p2: np.ndarray,
    q1: np.ndarray,
    q2: np.ndarray,
) -> tuple[float, float, np.ndarray] | None:
    """Return intersection parameters for line ``p1->p2`` and segment ``q1->q2``."""
    r = p2 - p1
    s = q2 - q1
    denominator = r[0] * s[1] - r[1] * s[0]
    if abs(denominator) <= _EPSILON:
        return None

    qp = q1 - p1
    t = (qp[0] * s[1] - qp[1] * s[0]) / denominator
    u = (qp[0] * r[1] - qp[1] * r[0]) / denominator
    if t < _EPSILON or u < -_EPSILON or u > 1.0 + _EPSILON:
        return None
    point = p1 + t * r
    return t, float(np.clip(u, 0.0, 1.0)), point


def _closest_spectral_locus_wavelength(
    xy: np.ndarray,
    xy_n: np.ndarray,
    wavelengths: np.ndarray,
    locus_xy: np.ndarray,
    *,
    inverse: bool = False,
    include_purple: bool = True,
) -> _Intersection | None:
    """Return nearest intersection between a whitepoint ray and the spectral locus."""
    direction = xy_n - xy if inverse else xy - xy_n
    if np.linalg.norm(direction) <= _EPSILON:
        return None

    p1 = xy_n
    p2 = xy_n + direction
    best: _Intersection | None = None
    segment_count = len(locus_xy) if include_purple else len(locus_xy) - 1

    for index in range(segment_count):
        is_purple = index == len(locus_xy) - 1
        q1 = locus_xy[index]
        q2 = locus_xy[0] if is_purple else locus_xy[index + 1]
        intersection = _intersect_line_segments(p1, p2, q1, q2)
        if intersection is None:
            continue

        t, u, point = intersection
        if is_purple:
            wavelength = np.nan
        else:
            wavelength = wavelengths[index] + u * (wavelengths[index + 1] - wavelengths[index])

        candidate = _Intersection(float(wavelength), point, is_purple, t)
        if best is None or candidate.t < best.t:
            best = candidate

    return best


def _dominant_single(
    xy: np.ndarray,
    xy_n: np.ndarray,
    wavelengths: np.ndarray,
    locus_xy: np.ndarray,
    *,
    inverse: bool,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Return dominant or complementary wavelength data for one xy pair."""
    if np.allclose(xy, xy_n):
        nan_xy = np.array([np.nan, np.nan], dtype=np.float64)
        return np.nan, nan_xy, nan_xy

    first = _closest_spectral_locus_wavelength(
        xy,
        xy_n,
        wavelengths,
        locus_xy,
        inverse=inverse,
        include_purple=True,
    )
    if first is None:
        nan_xy = np.array([np.nan, np.nan], dtype=np.float64)
        return np.nan, nan_xy, nan_xy

    if not first.is_purple:
        return first.wavelength, first.xy, first.xy

    second = _closest_spectral_locus_wavelength(
        xy,
        xy_n,
        wavelengths,
        locus_xy,
        inverse=not inverse,
        include_purple=False,
    )
    if second is None:
        nan_xy = np.array([np.nan, np.nan], dtype=np.float64)
        return np.nan, first.xy, nan_xy

    return -second.wavelength, first.xy, second.xy


def _dominant_array(
    xy: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray,
    locus: LocusSource,
    *,
    inverse: bool,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, bool]:
    """Vectorise dominant-wavelength computation over the last xy axis."""
    xy_arr = as_last_axis_pairs(xy, name="xy")
    xy_n_arr = as_last_axis_pairs(xy_n, name="xy_n")
    xy_n_broadcast = np.broadcast_to(xy_n_arr, xy_arr.shape)
    wavelengths, locus_xy = _load_locus(locus)

    input_was_single = xy_arr.shape == (2,)
    flat_xy = xy_arr.reshape(-1, 2)
    flat_xy_n = xy_n_broadcast.reshape(-1, 2)
    wavelength_result = np.empty(flat_xy.shape[0], dtype=np.float64)
    xy_wl_result = np.empty((flat_xy.shape[0], 2), dtype=np.float64)
    xy_cwl_result = np.empty((flat_xy.shape[0], 2), dtype=np.float64)

    for index, (xy_item, xy_n_item) in enumerate(zip(flat_xy, flat_xy_n)):
        wavelength, xy_wl, xy_cwl = _dominant_single(
            xy_item,
            xy_n_item,
            wavelengths,
            locus_xy,
            inverse=inverse,
        )
        wavelength_result[index] = wavelength
        xy_wl_result[index] = xy_wl
        xy_cwl_result[index] = xy_cwl

    output_shape = xy_arr.shape[:-1]
    return (
        wavelength_result.reshape(output_shape),
        xy_wl_result.reshape((*output_shape, 2)),
        xy_cwl_result.reshape((*output_shape, 2)),
        input_was_single,
    )


def _region_from_wavelength(wavelength: np.ndarray) -> np.ndarray:
    """Return locus region labels from signed wavelength convention."""
    return np.where(
        np.isnan(wavelength),
        "undefined",
        np.where(wavelength < 0, "purple", "spectral"),
    )


def _points_on_segments(
    points: np.ndarray,
    q1: np.ndarray,
    q2: np.ndarray,
) -> np.ndarray:
    """Return whether points lie on any line segment q1->q2."""
    segment = q2 - q1
    length_sq = np.sum(segment * segment, axis=-1)
    valid_segment = length_sq > _EPSILON
    vector = points[:, None, :] - q1[None, :, :]
    cross = vector[..., 0] * segment[None, :, 1] - vector[..., 1] * segment[None, :, 0]
    dot = vector[..., 0] * segment[None, :, 0] + vector[..., 1] * segment[None, :, 1]
    on_line = np.abs(cross) <= _EPSILON
    within = (dot >= -_EPSILON) & (dot <= length_sq[None, :] + _EPSILON)
    return np.any(on_line & within & valid_segment[None, :], axis=-1)


def _points_in_closed_locus(points: np.ndarray, locus_xy: np.ndarray) -> np.ndarray:
    """Return whether flattened xy points are inside the closed chromaticity locus."""
    closed = np.vstack([locus_xy, locus_xy[0]])
    q1 = closed[:-1]
    q2 = closed[1:]
    on_boundary = _points_on_segments(points, q1, q2)

    x = points[:, 0]
    y = points[:, 1]
    x1 = q1[:, 0]
    y1 = q1[:, 1]
    x2 = q2[:, 0]
    y2 = q2[:, 1]
    y_between = (y1[None, :] > y[:, None]) != (y2[None, :] > y[:, None])
    x_intersection = np.full((points.shape[0], q1.shape[0]), np.nan, dtype=np.float64)
    np.divide(
        (x2 - x1)[None, :] * (y[:, None] - y1[None, :]),
        (y2 - y1)[None, :],
        out=x_intersection,
        where=y_between,
    )
    x_intersection = x_intersection + x1[None, :]
    crossings = y_between & (x[:, None] < x_intersection)
    inside = np.count_nonzero(crossings, axis=-1) % 2 == 1
    return inside | on_boundary


def _validate_unit_interval(value: np.ndarray, *, name: str) -> None:
    """Validate a finite array in the closed unit interval."""
    if not np.all(np.isfinite(value)):
        raise ValueError(f"{name} must be finite")
    if np.any((value < 0.0) | (value > 1.0)):
        raise ValueError(f"{name} must be in the [0, 1] interval")


def _interpolate_locus_xy(
    wavelength: np.ndarray,
    wavelengths: np.ndarray,
    locus_xy: np.ndarray,
) -> np.ndarray:
    """Return linearly interpolated spectral-locus xy coordinates."""
    if not np.all(np.isfinite(wavelength)):
        raise ValueError("wavelength must be finite")
    if np.any((wavelength < wavelengths[0]) | (wavelength > wavelengths[-1])):
        raise ValueError(
            f"abs(wavelength) must be in the locus range "
            f"[{wavelengths[0]}, {wavelengths[-1]}]"
        )
    return np.stack(
        [
            np.interp(wavelength, wavelengths, locus_xy[:, 0]),
            np.interp(wavelength, wavelengths, locus_xy[:, 1]),
        ],
        axis=-1,
    )


def _boundary_xy_from_wavelength(
    wavelength: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray,
    locus: LocusSource,
) -> tuple[np.ndarray, np.ndarray, bool]:
    """Return boundary xy coordinates for signed dominant wavelengths."""
    wavelength_arr = np.asarray(wavelength, dtype=np.float64)
    if not np.all(np.isfinite(wavelength_arr)):
        raise ValueError("wavelength must be finite")

    xy_n_arr = as_last_axis_pairs(xy_n, name="xy_n")
    wavelengths, locus_xy = _load_locus(locus)
    abs_wavelength = np.abs(wavelength_arr)
    spectral_xy = _interpolate_locus_xy(abs_wavelength, wavelengths, locus_xy)

    input_was_single = wavelength_arr.shape == ()
    broadcast_shape = np.broadcast_shapes(wavelength_arr.shape, xy_n_arr.shape[:-1])
    wavelength_broadcast = np.broadcast_to(wavelength_arr, broadcast_shape)
    spectral_xy_broadcast = np.broadcast_to(spectral_xy, (*broadcast_shape, 2))
    xy_n_broadcast = np.broadcast_to(xy_n_arr, (*broadcast_shape, 2))
    boundary_xy = spectral_xy_broadcast.copy()

    negative_mask = wavelength_broadcast < 0.0
    flat_boundary = boundary_xy.reshape(-1, 2)
    flat_spectral = spectral_xy_broadcast.reshape(-1, 2)
    flat_xy_n = xy_n_broadcast.reshape(-1, 2)
    flat_negative = negative_mask.reshape(-1)

    for index, is_negative in enumerate(flat_negative):
        if not is_negative:
            continue
        purple = _closest_spectral_locus_wavelength(
            flat_spectral[index],
            flat_xy_n[index],
            wavelengths,
            locus_xy,
            inverse=True,
            include_purple=True,
        )
        if purple is None or not purple.is_purple:
            raise ValueError("negative wavelength direction does not intersect the purple line")
        flat_boundary[index] = purple.xy

    return boundary_xy, xy_n_broadcast, input_was_single


def xy_from_dominant_wavelength_pe(
    wavelength: Sequence[float] | np.ndarray,
    excitation_purity: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> np.ndarray:
    """Return CIE xy from signed dominant wavelength and excitation purity.

    Parameters
    ----------
    wavelength
        Dominant wavelength in nanometres. Negative values indicate a purple
        direction whose absolute value is the complementary spectral
        wavelength.
    excitation_purity
        Geometric purity in the closed interval ``[0, 1]``.
    xy_n
        Reference white chromaticity. Defaults to D65.
    locus
        Spectral-locus dataset name or ``MultiSpectralDistribution``.

    Returns
    -------
    ndarray
        xy coordinates with final-axis shape ``(..., 2)``.

    Notes
    -----
    This is the inverse of the excitation-purity construction from whitepoint
    to spectral or purple boundary.

    Examples
    --------
    >>> xy_from_dominant_wavelength_pe(580.0, 0.5).shape
    (2,)
    """
    purity = np.asarray(excitation_purity, dtype=np.float64)
    _validate_unit_interval(purity, name="excitation_purity")
    boundary_xy, xy_n_arr, input_was_single = _boundary_xy_from_wavelength(
        wavelength,
        xy_n,
        locus,
    )
    broadcast_shape = np.broadcast_shapes(boundary_xy.shape[:-1], purity.shape)
    boundary_broadcast = np.broadcast_to(boundary_xy, (*broadcast_shape, 2))
    xy_n_broadcast = np.broadcast_to(xy_n_arr, (*broadcast_shape, 2))
    purity_broadcast = np.broadcast_to(purity, broadcast_shape)
    xy = xy_n_broadcast + purity_broadcast[..., None] * (
        boundary_broadcast - xy_n_broadcast
    )
    if input_was_single and purity.shape == () and xy_n_arr.shape == (2,):
        return xy.reshape(2)
    return xy


def xy_from_dominant_wavelength_pc(
    wavelength: Sequence[float] | np.ndarray,
    colorimetric_purity: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> np.ndarray:
    """Return CIE xy from signed dominant wavelength and colorimetric purity.

    Notes
    -----
    This uses the project signed-wavelength convention: negative wavelengths
    represent purple-line directions through their complementary spectral
    wavelength. ``colorimetric_purity`` must be in ``[0, 1]``.
    """
    purity = np.asarray(colorimetric_purity, dtype=np.float64)
    _validate_unit_interval(purity, name="colorimetric_purity")
    boundary_xy, xy_n_arr, input_was_single = _boundary_xy_from_wavelength(
        wavelength,
        xy_n,
        locus,
    )
    broadcast_shape = np.broadcast_shapes(boundary_xy.shape[:-1], purity.shape)
    boundary_broadcast = np.broadcast_to(boundary_xy, (*broadcast_shape, 2))
    xy_n_broadcast = np.broadcast_to(xy_n_arr, (*broadcast_shape, 2))
    purity_broadcast = np.broadcast_to(purity, broadcast_shape)
    boundary_y = boundary_broadcast[..., 1]
    white_y = xy_n_broadcast[..., 1]
    denominator = boundary_y - purity_broadcast * (boundary_y - white_y)
    if np.any(np.abs(denominator) <= _EPSILON):
        raise ValueError("colorimetric_purity conversion denominator is too close to zero")
    excitation = purity_broadcast * white_y / denominator
    xy = xy_n_broadcast + excitation[..., None] * (
        boundary_broadcast - xy_n_broadcast
    )
    if input_was_single and purity.shape == () and xy_n_arr.shape == (2,):
        return xy.reshape(2)
    return xy


def is_inside_chromaticity_locus(
    xy: Sequence[float] | np.ndarray,
    locus: LocusSource = DEFAULT_LOCUS,
) -> bool | np.ndarray:
    """Return whether CIE xy coordinates are inside the closed chromaticity locus.

    Parameters
    ----------
    xy
        xy coordinates with final-axis shape ``(..., 2)``.
    locus
        Spectral-locus dataset name or ``MultiSpectralDistribution``.

    Returns
    -------
    bool or ndarray
        Boolean for single input, otherwise an array matching the leading
        input shape.

    Notes
    -----
    The test closes the spectral locus with the purple line.

    Examples
    --------
    >>> is_inside_chromaticity_locus([0.3127, 0.3290])
    True
    """
    xy_arr = as_last_axis_pairs(xy, name="xy")
    _wavelengths, locus_xy = _load_locus(locus)
    input_was_single = xy_arr.shape == (2,)
    inside = _points_in_closed_locus(xy_arr.reshape(-1, 2), locus_xy).reshape(
        xy_arr.shape[:-1]
    )
    if input_was_single:
        return bool(inside)
    return inside


def dominant_wavelength(
    xy: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> tuple[float | np.ndarray, np.ndarray]:
    """Return dominant wavelength and dominant-side boundary coordinates.

    Parameters
    ----------
    xy
        xy coordinates with final-axis shape ``(..., 2)``.
    xy_n
        Reference white chromaticity. Defaults to D65.
    locus
        Spectral-locus dataset name or ``MultiSpectralDistribution``.

    Returns
    -------
    wavelength, xy_boundary
        Dominant wavelength and the corresponding boundary coordinates.

    Notes
    -----
    Negative wavelength values indicate a non-spectral purple direction; the
    absolute value is the complementary spectral wavelength.

    Examples
    --------
    >>> wavelength, boundary = dominant_wavelength([0.45, 0.40])
    >>> boundary.shape
    (2,)
    """
    wavelength, xy_wl, xy_cwl, single = _dominant_array(
        xy,
        xy_n,
        locus,
        inverse=False,
    )
    if single:
        return float(wavelength), xy_wl
    return wavelength, xy_wl


def complementary_wavelength(
    xy: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> tuple[float | np.ndarray, np.ndarray]:
    """Return complementary wavelength and opposite-side boundary coordinates.

    Notes
    -----
    The same signed-wavelength convention as ``dominant_wavelength`` is used.
    This function traces the ray in the opposite direction from the
    whitepoint.
    """
    wavelength, xy_wl, xy_cwl, single = _dominant_array(
        xy,
        xy_n,
        locus,
        inverse=True,
    )
    if single:
        return float(wavelength), xy_wl
    return wavelength, xy_wl


def excitation_purity(
    xy: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> float | np.ndarray:
    """Return excitation purity for CIE xy coordinates.

    Notes
    -----
    Excitation purity is the geometric ratio from the whitepoint to ``xy``
    relative to the distance from the whitepoint to the boundary point on the
    same ray.
    """
    xy_arr = as_last_axis_pairs(xy, name="xy")
    xy_n_arr = np.broadcast_to(as_last_axis_pairs(xy_n, name="xy_n"), xy_arr.shape)
    _wavelength, xy_wl = dominant_wavelength(xy_arr, xy_n_arr, locus)

    numerator = np.linalg.norm(xy_arr - xy_n_arr, axis=-1)
    denominator = np.linalg.norm(xy_wl - xy_n_arr, axis=-1)
    purity = np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=np.float64),
        where=denominator > _EPSILON,
    )
    if xy_arr.shape == (2,):
        return float(purity)
    return purity


def colorimetric_purity(
    xy: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> float | np.ndarray:
    """Return colorimetric purity for CIE xy coordinates.

    Notes
    -----
    Colorimetric purity adjusts excitation purity by the target and boundary
    ``y`` chromaticity coordinates.
    """
    xy_arr = as_last_axis_pairs(xy, name="xy")
    _wavelength, xy_wl = dominant_wavelength(xy_arr, xy_n, locus)
    purity_e = np.asarray(excitation_purity(xy_arr, xy_n, locus), dtype=np.float64)
    numerator = purity_e * xy_wl[..., 1]
    valid = np.isfinite(numerator) & (np.abs(xy_arr[..., 1]) > _EPSILON)
    purity_c = np.divide(
        numerator,
        xy_arr[..., 1],
        out=np.zeros_like(purity_e, dtype=np.float64),
        where=valid,
    )
    if xy_arr.shape == (2,):
        return float(purity_c)
    return purity_c


def analyze_chromaticity(
    xy: Sequence[float] | np.ndarray,
    xy_n: Sequence[float] | np.ndarray = DEFAULT_WHITEPOINT_XY,
    locus: LocusSource = DEFAULT_LOCUS,
) -> ChromaticityAnalysis:
    """Return dominant, complementary and purity information for CIE xy.

    Parameters
    ----------
    xy
        xy coordinates with final-axis shape ``(..., 2)``.
    xy_n
        Reference white chromaticity. Defaults to D65.
    locus
        Spectral-locus dataset name or ``MultiSpectralDistribution``.

    Returns
    -------
    ChromaticityAnalysis
        Semantic result containing dominant and complementary wavelengths,
        boundary points, region labels and purity values.

    Notes
    -----
    The analysis is purely chromaticity geometry. It does not consider
    luminance. Region labels distinguish ordinary spectral intersections,
    purple-line intersections and undefined whitepoint cases.

    Examples
    --------
    >>> result = analyze_chromaticity([0.45, 0.40])
    >>> result.dominant_xy.shape
    (2,)
    """
    wavelength, dominant_xy, complementary_xy, single = _dominant_array(
        xy,
        xy_n,
        locus,
        inverse=False,
    )
    complementary, complementary_intersection, _unused, _single = _dominant_array(
        xy,
        xy_n,
        locus,
        inverse=True,
    )
    dominant_region = _region_from_wavelength(wavelength)
    complementary_region = _region_from_wavelength(complementary)
    purity_e = excitation_purity(xy, xy_n, locus)
    purity_c = colorimetric_purity(xy, xy_n, locus)

    if single:
        return ChromaticityAnalysis(
            wavelength=float(wavelength),
            dominant_xy=dominant_xy,
            complementary_wavelength=float(complementary),
            complementary_xy=complementary_intersection,
            dominant_region=str(dominant_region),
            complementary_region=str(complementary_region),
            excitation_purity=float(purity_e),
            colorimetric_purity=float(purity_c),
        )
    return ChromaticityAnalysis(
        wavelength=wavelength,
        dominant_xy=dominant_xy,
        complementary_wavelength=complementary,
        complementary_xy=complementary_intersection,
        dominant_region=dominant_region,
        complementary_region=complementary_region,
        excitation_purity=purity_e,
        colorimetric_purity=purity_c,
    )


__all__ = [
    "DEFAULT_LOCUS",
    "DEFAULT_WHITEPOINT_XY",
    "ChromaticityAnalysis",
    "analyze_chromaticity",
    "is_inside_chromaticity_locus",
    "dominant_wavelength",
    "complementary_wavelength",
    "excitation_purity",
    "colorimetric_purity",
    "xy_from_dominant_wavelength_pe",
    "xy_from_dominant_wavelength_pc",
]
