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
    """Return MacAdam limits using published data or computed optimal colours."""
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
    """Return whether XYZ values are inside published or computed MacAdam limits."""
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
