"""MacAdam gamut public semantic layer."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.spectra import MultiSpectralDistribution, SpectralDistribution, SpectralShape
from color.utils.names import canonical_method_name

from .macadam_computed import (
    ComputedMacAdamLimitsBoundary,
    DEFAULT_COMPUTED_MACADAM_CMFS,
    computed_macadam_limits,
    computed_macadam_limits_data,
    computed_macadam_limits_XYZ,
    is_within_computed_macadam_limits,
)
from .macadam_published import (
    MacAdamLimitsBoundary,
    is_within_macadam_limits as _published_is_within_macadam_limits,
    macadam_limits as _published_macadam_limits,
    macadam_limits_XYZ,
    macadam_limits_data,
    macadam_limits_published_xy_boundary,
)


_PUBLISHED_ILLUMINANTS = {"a", "c", "d65"}
_SOURCE_ALIASES = {
    "auto": "auto",
    "published": "published",
    "static": "published",
    "data": "published",
    "computed": "computed",
    "compute": "computed",
}


def _resolve_source(source: str) -> str:
    """Return the canonical MacAdam source policy."""
    key = canonical_method_name(source)
    resolved = _SOURCE_ALIASES.get(key)
    if resolved is None:
        raise ValueError("source must be 'auto', 'published' or 'computed'")
    return resolved


def _is_published_illuminant(illuminant: str | SpectralDistribution) -> bool:
    """Return whether *illuminant* can use a cached MacAdam table."""
    return isinstance(illuminant, str) and canonical_method_name(illuminant) in _PUBLISHED_ILLUMINANTS


def _uses_computed_options(
    *,
    cmfs: str | MultiSpectralDistribution | None,
    shape: SpectralShape | None,
) -> bool:
    """Return whether any computed-only option was requested."""
    return cmfs is not None or shape is not None


def _select_source(
    illuminant: str | SpectralDistribution,
    *,
    cmfs: str | MultiSpectralDistribution | None,
    shape: SpectralShape | None,
    source: str,
) -> str:
    """Return the implementation source for a MacAdam request."""
    resolved = _resolve_source(source)
    computed_options = _uses_computed_options(
        cmfs=cmfs,
        shape=shape,
    )
    if resolved == "published":
        if not _is_published_illuminant(illuminant):
            raise ValueError("source='published' requires illuminant 'A', 'C' or 'D65'")
        if computed_options:
            raise ValueError(
                "source='published' does not accept cmfs or shape"
            )
        return "published"
    if resolved == "computed":
        return "computed"
    return "published" if _is_published_illuminant(illuminant) and not computed_options else "computed"


def macadam_limits(
    illuminant: str | SpectralDistribution = "D65",
    *,
    cmfs: str | MultiSpectralDistribution | None = None,
    shape: SpectralShape | None = None,
    source: str = "auto",
    L_values: Sequence[float] | np.ndarray = np.arange(0.0, 101.0, 1.0),
    hue_values: Sequence[float] | np.ndarray = np.arange(0.0, 361.0, 1.0),
    C_upper: float = 300.0,
    iterations: int = 14,
    tolerance: float = 1e-9,
) -> MacAdamLimitsBoundary | ComputedMacAdamLimitsBoundary:
    """Return MacAdam optimal-colour limits with source dispatch.

    Parameters
    ----------
    illuminant
        Illuminant name or SPD. Published data is available for ``"A"``,
        ``"C"`` and ``"D65"``.
    cmfs, shape
        Computed-route options. Supplying either option forces computed
        MacAdam limits when ``source="auto"``.
    source
        ``"auto"``, ``"published"`` or ``"computed"``.
    L_values, hue_values, C_upper, iterations
        Resampling parameters for the returned ``GamutBoundary``.
    tolerance
        Inside-test tolerance used by the resampling route.

    Returns
    -------
    MacAdamLimitsBoundary or ComputedMacAdamLimitsBoundary
        Regular LCHab boundary for the selected MacAdam source.

    Notes
    -----
    ``source="auto"`` uses cached published A/C/D65 data when possible and
    falls back to computed optimal colours for custom CMFs, illuminants or
    spectral shapes. This is a theoretical object-colour limit, not a display
    gamut and not the visible-spectrum volume.

    Examples
    --------
    >>> boundary = macadam_limits("D65", L_values=[0, 50, 100], hue_values=[0, 180, 360])
    >>> boundary.C_max.shape
    (3, 3)
    """
    selected = _select_source(
        illuminant,
        cmfs=cmfs,
        shape=shape,
        source=source,
    )
    if selected == "published":
        return _published_macadam_limits(
            illuminant,  # type: ignore[arg-type]
            L_values=L_values,
            hue_values=hue_values,
            C_upper=C_upper,
            iterations=iterations,
            tolerance=tolerance,
        )
    return computed_macadam_limits(
        cmfs=DEFAULT_COMPUTED_MACADAM_CMFS if cmfs is None else cmfs,
        illuminant=illuminant,
        shape=shape,
        L_values=L_values,
        hue_values=hue_values,
        C_upper=C_upper,
        iterations=iterations,
        tolerance=tolerance,
    )


def is_within_macadam_limits(
    XYZ: Sequence[float] | np.ndarray,
    illuminant: str | SpectralDistribution = "D65",
    *,
    cmfs: str | MultiSpectralDistribution | None = None,
    shape: SpectralShape | None = None,
    source: str = "auto",
    tolerance: float = 1e-9,
) -> np.ndarray | np.bool_:
    """Return whether XYZ values are inside MacAdam optimal-colour limits.

    Parameters
    ----------
    XYZ
        XYZ values with final-axis shape ``(..., 3)`` in project ``Y=100``
        scale.
    illuminant
        Illuminant name or SPD.
    cmfs, shape, source
        Same source-dispatch options as ``macadam_limits``.
    tolerance
        Non-negative inside-test tolerance.

    Returns
    -------
    bool or ndarray
        Inside mask matching the leading shape of ``XYZ``.

    Notes
    -----
    For published A/C/D65 data this tests against cached optimal-colour
    vertices. For computed sources it uses the computed optimal-colour solid.

    Examples
    --------
    >>> bool(is_within_macadam_limits([0.0, 0.0, 0.0], "D65")) in {True, False}
    True
    """
    selected = _select_source(
        illuminant,
        cmfs=cmfs,
        shape=shape,
        source=source,
    )
    if selected == "published":
        return _published_is_within_macadam_limits(
            XYZ,
            illuminant,  # type: ignore[arg-type]
            tolerance=tolerance,
        )
    return is_within_computed_macadam_limits(
        XYZ,
        cmfs=DEFAULT_COMPUTED_MACADAM_CMFS if cmfs is None else cmfs,
        illuminant=illuminant,
        shape=shape,
        tolerance=tolerance,
    )


__all__ = [
    "MacAdamLimitsBoundary",  # cached MacAdam GamutBoundary subtype
    "macadam_limits",  # return MacAdam limits with automatic source dispatch
    "is_within_macadam_limits",  # test XYZ values inside dispatched MacAdam limits
    "macadam_limits_published_xy_boundary",  # return published MacAdam xy boundary
]

__all__ += [
    "macadam_limits_data",  # return cached MacAdam raw dataset columns
    "macadam_limits_XYZ",  # return cached MacAdam XYZ mesh vertices
]

__all__ += [
    "ComputedMacAdamLimitsBoundary",  # computed MacAdam GamutBoundary subtype
    "computed_macadam_limits",  # compute MacAdam limits from CMFs and an illuminant
    "is_within_computed_macadam_limits",  # test XYZ values inside computed MacAdam limits
    "computed_macadam_limits_XYZ",  # return computed MacAdam XYZ mesh vertices
    "computed_macadam_limits_data",  # return computed MacAdam data columns
]
