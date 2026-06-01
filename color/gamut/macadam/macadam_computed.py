"""Computed MacAdam optimal-colour limits."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.spatial import Delaunay

from color.colorimetry import XYZ_to_xyY
from color.colorimetry.lightness import Lstar_to_Y, Y_to_Lstar
from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_dataset,
)
from color.spaces.basic.lab import Lab_to_LCHab, XYZ_to_Lab
from color.utils.arrays import as_last_axis_triplets
from color.utils.names import canonical_method_name

from ..boundary import GamutBoundary, _as_1d_values, _convex_hull_polygon


SPECTRAL_SHAPE_COMPUTED_MACADAM = SpectralShape(400.0, 700.0, 2.0)
DEFAULT_COMPUTED_MACADAM_CMFS = "cie1931_xyz_1nm"
DEFAULT_COMPUTED_MACADAM_ILLUMINANT = "D65"
DEFAULT_COMPUTED_MACADAM_L_VALUES = np.arange(1.0, 101.0, 10.0)


def _as_shape(shape: SpectralShape | None) -> SpectralShape:
    """Return the spectral shape used for computed MacAdam limits."""
    return SPECTRAL_SHAPE_COMPUTED_MACADAM if shape is None else shape


def _load_cmfs(
    cmfs: str | MultiSpectralDistribution,
    shape: SpectralShape,
) -> MultiSpectralDistribution:
    """Return CMFs aligned to *shape*."""
    if isinstance(cmfs, MultiSpectralDistribution):
        return cmfs.align(shape)
    return from_dataset("standard_observers.cmfs", cmfs).align(shape)


def _load_illuminant(
    illuminant: str | SpectralDistribution,
    shape: SpectralShape,
) -> SpectralDistribution:
    """Return an illuminant SPD aligned to *shape*."""
    if isinstance(illuminant, SpectralDistribution):
        return illuminant.align(shape)
    if canonical_method_name(illuminant) == "e":
        return SpectralDistribution(
            shape.wavelengths,
            np.ones(len(shape), dtype=np.float64),
            name="CIE Illuminant E",
            metadata={"illuminant": "E"},
        )
    return from_dataset("illuminants", illuminant).align(shape)


def _validate_macadam_responses(cmfs: MultiSpectralDistribution) -> None:
    """Validate XYZ colour matching functions."""
    if cmfs.labels != ("X", "Y", "Z"):
        raise ValueError("cmfs labels must be ('X', 'Y', 'Z')")


def _cumulative_trapezoid(
    wavelengths: np.ndarray,
    values: np.ndarray,
) -> np.ndarray:
    """Return cumulative trapezoid integrals with a zero first element."""
    if wavelengths.ndim != 1 or values.ndim != 1:
        raise ValueError("wavelengths and values must be one-dimensional")
    if wavelengths.shape != values.shape:
        raise ValueError("wavelengths and values must have the same shape")
    if wavelengths.size < 2:
        raise ValueError("at least two wavelength samples are required")
    increments = 0.5 * (values[:-1] + values[1:]) * np.diff(wavelengths)
    return np.concatenate([[0.0], np.cumsum(increments)])


def _integral_at(
    wavelengths: np.ndarray,
    cumulative: np.ndarray,
    wavelength: float | np.ndarray,
) -> np.ndarray:
    """Interpolate a cumulative integral at arbitrary wavelengths."""
    return np.interp(wavelength, wavelengths, cumulative)


def _wavelength_at_integral(
    wavelengths: np.ndarray,
    cumulative_y: np.ndarray,
    target: float,
) -> float:
    """Return wavelength where cumulative Y integral reaches *target*."""
    return float(np.interp(target, cumulative_y, wavelengths))


def _as_L_values(
    L_values: Sequence[float] | np.ndarray | None,
    *,
    Y_values: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Return finite L* values, optionally derived from Y values."""
    if L_values is not None and Y_values is not None:
        raise ValueError("L_values and Y_values cannot both be provided")
    if Y_values is not None:
        Y_array = _as_1d_values(Y_values, name="Y_values")
        if np.any((Y_array < 0.0) | (Y_array > 100.0)):
            raise ValueError("Y_values must be in the [0, 100] range")
        return np.asarray(Y_to_Lstar(Y_array, Y_n=100.0), dtype=np.float64)
    if L_values is None:
        return _as_1d_values(DEFAULT_COMPUTED_MACADAM_L_VALUES, name="L_values")
    L_array = _as_1d_values(L_values, name="L_values")
    if np.any((L_array < 0.0) | (L_array > 100.0)):
        raise ValueError("L_values must be in the [0, 100] range")
    return L_array


@dataclass(frozen=True)
class _IntegrationBasis:
    """Aligned spectral data and cumulative tristimulus integrals."""

    wavelengths: np.ndarray
    cumulative_X: np.ndarray
    cumulative_Y: np.ndarray
    cumulative_Z: np.ndarray
    whitepoint_XYZ: np.ndarray


def _integration_basis(
    *,
    cmfs: str | MultiSpectralDistribution,
    illuminant: str | SpectralDistribution,
    shape: SpectralShape | None,
) -> _IntegrationBasis:
    """Return cumulative MacAdam integration basis."""
    common_shape = _as_shape(shape)
    aligned_cmfs = _load_cmfs(cmfs, common_shape)
    aligned_illuminant = _load_illuminant(illuminant, common_shape)
    _validate_macadam_responses(aligned_cmfs)

    wavelengths = np.array(common_shape.wavelengths, dtype=np.float64, copy=True)
    weighted = aligned_cmfs.values * aligned_illuminant.values[:, np.newaxis]

    cumulative_X = _cumulative_trapezoid(wavelengths, weighted[:, 0])
    cumulative_Y = _cumulative_trapezoid(wavelengths, weighted[:, 1])
    cumulative_Z = _cumulative_trapezoid(wavelengths, weighted[:, 2])
    if cumulative_Y[-1] <= 0:
        raise ZeroDivisionError("illuminant and CMFs produce zero white Y integral")

    scale = 100.0 / cumulative_Y[-1]
    whitepoint = scale * np.array(
        [cumulative_X[-1], cumulative_Y[-1], cumulative_Z[-1]],
        dtype=np.float64,
    )
    return _IntegrationBasis(
        wavelengths=wavelengths,
        cumulative_X=scale * cumulative_X,
        cumulative_Y=scale * cumulative_Y,
        cumulative_Z=scale * cumulative_Z,
        whitepoint_XYZ=whitepoint,
    )


def _integral_XYZ_between(
    basis: _IntegrationBasis,
    start: float,
    end: float,
) -> np.ndarray:
    """Return XYZ integral over a wavelength interval."""
    values = np.array(
        [
            _integral_at(basis.wavelengths, basis.cumulative_X, end)
            - _integral_at(basis.wavelengths, basis.cumulative_X, start),
            _integral_at(basis.wavelengths, basis.cumulative_Y, end)
            - _integral_at(basis.wavelengths, basis.cumulative_Y, start),
            _integral_at(basis.wavelengths, basis.cumulative_Z, end)
            - _integral_at(basis.wavelengths, basis.cumulative_Z, start),
        ],
        dtype=np.float64,
    )
    return values


def _optimal_colour_XYZ_for_L(
    basis: _IntegrationBasis,
    L: float,
) -> np.ndarray:
    """Return Type 1 and Type 2 optimal-colour XYZ rows for one L*."""
    Y = float(Lstar_to_Y(L, Y_n=100.0))
    if Y <= 1e-12:
        return np.zeros((1, 3), dtype=np.float64)
    if 100.0 - Y <= 1e-12:
        return basis.whitepoint_XYZ.reshape(1, 3)

    reflected_Y = Y
    absorbed_Y = 100.0 - Y
    full_XYZ = basis.whitepoint_XYZ
    rows: list[np.ndarray] = []

    for start_index, start in enumerate(basis.wavelengths):
        start_Y = basis.cumulative_Y[start_index]

        type_1_target = start_Y + reflected_Y
        if type_1_target <= 100.0 + 1e-10:
            end = _wavelength_at_integral(
                basis.wavelengths,
                basis.cumulative_Y,
                min(type_1_target, 100.0),
            )
            rows.append(_integral_XYZ_between(basis, float(start), end))

        type_2_target = start_Y + absorbed_Y
        if type_2_target <= 100.0 + 1e-10:
            end = _wavelength_at_integral(
                basis.wavelengths,
                basis.cumulative_Y,
                min(type_2_target, 100.0),
            )
            absorbed_XYZ = _integral_XYZ_between(basis, float(start), end)
            rows.append(full_XYZ - absorbed_XYZ)

    if not rows:
        return np.empty((0, 3), dtype=np.float64)
    XYZ = np.vstack(rows)
    XYZ[np.abs(XYZ) < 1e-12] = 0.0
    return np.unique(np.round(XYZ, 12), axis=0)


def _optimal_colour_XYZ_for_L_values(
    basis: _IntegrationBasis,
    L_values: np.ndarray,
) -> np.ndarray:
    """Return optimal-colour XYZ rows for all L* values."""
    rows = [_optimal_colour_XYZ_for_L(basis, float(L)) for L in L_values]
    rows = [row for row in rows if row.size]
    if not rows:
        return np.empty((0, 3), dtype=np.float64)
    XYZ = np.vstack(rows)
    if not np.all(np.isfinite(XYZ)):
        raise ValueError("computed MacAdam XYZ values must be finite")
    return XYZ


def _computed_data_from_XYZ(
    XYZ: np.ndarray,
    *,
    whitepoint_XYZ: np.ndarray,
) -> dict[str, np.ndarray]:
    """Return MacAdam data columns derived from XYZ rows."""
    white_xy = XYZ_to_xyY(whitepoint_XYZ)[..., :2]
    xyY = XYZ_to_xyY(XYZ, fallback_xy=white_xy)
    Lab = XYZ_to_Lab(XYZ, whitepoint_XYZ=whitepoint_XYZ)
    LCHab = Lab_to_LCHab(Lab)
    return {
        "x": xyY[:, 0],
        "y": xyY[:, 1],
        "Y": XYZ[:, 1],
        "X": XYZ[:, 0],
        "Z": XYZ[:, 2],
        "L": Lab[:, 0],
        "a": Lab[:, 1],
        "b": Lab[:, 2],
        "C": LCHab[:, 1],
        "h": LCHab[:, 2],
    }


def _resample_chroma_by_hue(
    h: np.ndarray,
    C: np.ndarray,
    hue_values: np.ndarray,
) -> np.ndarray:
    """Return a nearest-envelope chroma sampled at target hues."""
    if h.size == 0:
        return np.zeros_like(hue_values, dtype=np.float64)
    h = np.mod(h, 360.0)
    C = np.asarray(C, dtype=np.float64)
    result = np.empty_like(hue_values, dtype=np.float64)
    if hue_values.size > 1:
        diffs = np.diff(np.sort(np.unique(np.mod(hue_values, 360.0))))
        half_width = max(float(np.min(diffs)) / 2.0 if diffs.size else 1.0, 0.5)
    else:
        half_width = 1.0

    for index, hue in enumerate(np.mod(hue_values, 360.0)):
        distance = np.abs(((h - hue + 180.0) % 360.0) - 180.0)
        mask = distance <= half_width
        if np.any(mask):
            result[index] = float(np.max(C[mask]))
        else:
            result[index] = float(C[np.argmin(distance)])
    return result


def computed_macadam_limits_XYZ(
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_COMPUTED_MACADAM_CMFS,
    illuminant: str | SpectralDistribution = DEFAULT_COMPUTED_MACADAM_ILLUMINANT,
    shape: SpectralShape | None = None,
    L_values: Sequence[float] | np.ndarray | None = None,
    Y_values: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """Return computed MacAdam optimal-colour vertices as XYZ rows."""
    basis = _integration_basis(cmfs=cmfs, illuminant=illuminant, shape=shape)
    L_array = _as_L_values(L_values, Y_values=Y_values)
    return _optimal_colour_XYZ_for_L_values(basis, L_array)


def computed_macadam_limits_data(
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_COMPUTED_MACADAM_CMFS,
    illuminant: str | SpectralDistribution = DEFAULT_COMPUTED_MACADAM_ILLUMINANT,
    shape: SpectralShape | None = None,
    L_values: Sequence[float] | np.ndarray | None = None,
    Y_values: Sequence[float] | np.ndarray | None = None,
) -> dict[str, np.ndarray]:
    """Return computed MacAdam optimal-colour data columns."""
    basis = _integration_basis(cmfs=cmfs, illuminant=illuminant, shape=shape)
    L_array = _as_L_values(L_values, Y_values=Y_values)
    XYZ = _optimal_colour_XYZ_for_L_values(basis, L_array)
    return _computed_data_from_XYZ(XYZ, whitepoint_XYZ=basis.whitepoint_XYZ)


@dataclass(frozen=True)
class ComputedMacAdamLimitsBoundary(GamutBoundary):
    """Computed MacAdam optimal-colour boundary."""

    vertices_XYZ: np.ndarray | None = None
    cmfs: str = DEFAULT_COMPUTED_MACADAM_CMFS
    illuminant: str = DEFAULT_COMPUTED_MACADAM_ILLUMINANT

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.vertices_XYZ is None:
            raise ValueError("vertices_XYZ is required")
        vertices = np.array(self.vertices_XYZ, dtype=np.float64, copy=True)
        if vertices.ndim != 2 or vertices.shape[1] != 3:
            raise ValueError("vertices_XYZ must have shape (n, 3)")
        if vertices.shape[0] < 1:
            raise ValueError("vertices_XYZ must contain at least one vertex")
        if not np.all(np.isfinite(vertices)):
            raise ValueError("vertices_XYZ must be finite")
        vertices.setflags(write=False)
        object.__setattr__(self, "vertices_XYZ", vertices)

    def xy_boundary(self) -> np.ndarray:
        """Return the xy convex hull of computed optimal-colour vertices."""
        from color.colorimetry import XYZ_to_xy

        positive = np.sum(self.vertices_XYZ, axis=1) > 1e-12
        if np.count_nonzero(positive) < 3:
            return np.array([[0.0, 0.0], [0.0, 0.0]], dtype=np.float64)
        return _convex_hull_polygon(XYZ_to_xy(self.vertices_XYZ[positive]))


def _inside_computed_macadam_mesh(
    XYZ: Sequence[float] | np.ndarray,
    *,
    triangulation: Delaunay,
    tolerance: float,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside a computed MacAdam mesh."""
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    inside = triangulation.find_simplex(xyz.reshape(-1, 3), tol=tolerance) >= 0
    inside = inside.reshape(xyz.shape[:-1])
    return inside[()] if inside.shape == () else inside


def is_within_computed_macadam_limits(
    XYZ: Sequence[float] | np.ndarray,
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_COMPUTED_MACADAM_CMFS,
    illuminant: str | SpectralDistribution = DEFAULT_COMPUTED_MACADAM_ILLUMINANT,
    shape: SpectralShape | None = None,
    L_values: Sequence[float] | np.ndarray | None = None,
    Y_values: Sequence[float] | np.ndarray | None = None,
    tolerance: float = 1e-9,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside computed MacAdam limits."""
    vertices = computed_macadam_limits_XYZ(
        cmfs=cmfs,
        illuminant=illuminant,
        shape=shape,
        L_values=L_values,
        Y_values=Y_values,
    )
    xyz = as_last_axis_triplets(XYZ, name="XYZ")
    flat = xyz.reshape(-1, 3)
    black_hits = np.linalg.norm(flat, axis=1) <= tolerance
    vertex_hits = np.any(
        np.linalg.norm(flat[:, np.newaxis, :] - vertices[np.newaxis, :, :], axis=-1)
        <= tolerance,
        axis=1,
    )
    if np.linalg.matrix_rank(vertices - vertices[0]) < 3:
        inside = np.logical_or(vertex_hits, black_hits).reshape(xyz.shape[:-1])
        return inside[()] if inside.shape == () else inside
    triangulation = Delaunay(vertices)
    inside = np.asarray(_inside_computed_macadam_mesh(
        XYZ,
        triangulation=triangulation,
        tolerance=tolerance,
    )).reshape(-1)
    inside = np.logical_or.reduce((inside, vertex_hits, black_hits)).reshape(xyz.shape[:-1])
    return inside[()] if inside.shape == () else inside


def computed_macadam_limits(
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_COMPUTED_MACADAM_CMFS,
    illuminant: str | SpectralDistribution = DEFAULT_COMPUTED_MACADAM_ILLUMINANT,
    shape: SpectralShape | None = None,
    L_values: Sequence[float] | np.ndarray = np.arange(0.0, 101.0, 1.0),
    hue_values: Sequence[float] | np.ndarray = np.arange(0.0, 361.0, 1.0),
    C_upper: float = 300.0,
    iterations: int = 14,
    tolerance: float = 1e-9,
) -> ComputedMacAdamLimitsBoundary:
    """Return computed MacAdam limits as a regular LCHab boundary."""
    L_array = _as_1d_values(L_values, name="L_values")
    if np.any((L_array < 0.0) | (L_array > 100.0)):
        raise ValueError("L_values must be in the [0, 100] range")
    hue_array = _as_1d_values(hue_values, name="hue_values")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    C_upper = float(C_upper)
    if not np.isfinite(C_upper) or C_upper <= 0:
        raise ValueError("C_upper must be a finite positive value")
    if int(iterations) != iterations or iterations <= 0:
        raise ValueError("iterations must be a positive integer")

    basis = _integration_basis(cmfs=cmfs, illuminant=illuminant, shape=shape)
    C_max = np.empty((L_array.size, hue_array.size), dtype=np.float64)
    vertices = []
    for L_index, L in enumerate(L_array):
        XYZ = _optimal_colour_XYZ_for_L(basis, float(L))
        vertices.append(XYZ)
        data = _computed_data_from_XYZ(XYZ, whitepoint_XYZ=basis.whitepoint_XYZ)
        C_max[L_index, :] = _resample_chroma_by_hue(data["h"], data["C"], hue_array)
    C_max = np.minimum(C_max, C_upper)
    vertices_XYZ = np.vstack(vertices)

    return ComputedMacAdamLimitsBoundary(
        C_max=C_max,
        L_values=L_array,
        hue_values=hue_array,
        whitepoint_XYZ=basis.whitepoint_XYZ,
        primaries=None,
        vertices_XYZ=vertices_XYZ,
        cmfs=cmfs if isinstance(cmfs, str) else cmfs.name,
        illuminant=illuminant if isinstance(illuminant, str) else illuminant.name,
    )


__all__ = [
    "SPECTRAL_SHAPE_COMPUTED_MACADAM",
    "DEFAULT_COMPUTED_MACADAM_CMFS",
    "DEFAULT_COMPUTED_MACADAM_ILLUMINANT",
    "DEFAULT_COMPUTED_MACADAM_L_VALUES",
    "ComputedMacAdamLimitsBoundary",
    "computed_macadam_limits_XYZ",
    "computed_macadam_limits_data",
    "computed_macadam_limits",
    "is_within_computed_macadam_limits",
]
