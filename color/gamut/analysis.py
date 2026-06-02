"""High-level gamut analysis summaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence
import warnings

import numpy as np

from .boundary import GamutBoundary, compute_LCH_gamut_boundary
from .coverage import (
    lab_gamut_coverage,
    lab_gamut_volume,
    xy_gamut_area_from_xy,
    xy_gamut_coverage_from_xy,
)
from .macadam import macadam_limits
from .pointer import pointer_gamut
from .primaries import DisplayPrimaries


@dataclass(frozen=True)
class GamutAnalysis:
    """Summary metrics for one gamut boundary."""

    name: str
    boundary: GamutBoundary
    xy_area: float
    xy_coverage_rec2020: float
    xy_coverage_pointer: float
    xy_coverage_macadam_d65: float
    lab_volume: float
    projected_ab_area: float
    ring_area: float
    volume_coverage_rec2020: float
    volume_coverage_pointer: float
    volume_coverage_macadam_d65: float
    warnings: tuple[str, ...]


def _name_from_gamut(gamut: str | DisplayPrimaries | GamutBoundary, name: str | None) -> str:
    """Return a human-readable analysis name."""
    if name is not None:
        return str(name)
    if isinstance(gamut, str):
        return gamut
    if isinstance(gamut, DisplayPrimaries):
        return "+".join(gamut.names or ())
    return gamut.__class__.__name__


def _as_boundary(
    gamut: str | DisplayPrimaries | GamutBoundary,
    *,
    L_values: Sequence[float] | np.ndarray,
    hue_values: Sequence[float] | np.ndarray,
    C_upper: float,
    iterations: int,
) -> GamutBoundary:
    """Return a gamut boundary from a supported analysis input."""
    if isinstance(gamut, GamutBoundary):
        return gamut
    return compute_LCH_gamut_boundary(
        gamut,
        L_values=L_values,
        hue_values=hue_values,
        C_upper=C_upper,
        iterations=iterations,
    )


def _record_warning_call(warning_messages: list[str], function, *args, **kwargs):
    """Call *function*, record emitted warnings, then re-emit them."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", UserWarning)
        result = function(*args, **kwargs)
    for item in caught:
        message = str(item.message)
        warning_messages.append(message)
        warnings.warn(message, item.category, stacklevel=3)
    return result


def _default_macadam_d65_boundary(
    *,
    L_values: Sequence[float] | np.ndarray,
    hue_values: Sequence[float] | np.ndarray,
    C_upper: float,
    iterations: int,
) -> GamutBoundary:
    """Return the default D65 MacAdam reference boundary.

    Plain ``macadam_limits("D65")`` uses the cached A/C/D65 MacAdam data via
    ``source="auto"``.  This avoids the longer computed route during routine
    analysis and keeps the reference stable.  The cached tables were generated
    from the computed MacAdam method, then this call resamples them onto the
    requested ``L_values`` and ``hue_values`` grid.  Forcing
    ``source="computed"`` is useful for custom CMFs, illuminants or spectral
    shapes, but a coarse computed grid can differ noticeably from the cached
    reference.
    """
    return macadam_limits(
        "D65",
        L_values=L_values,
        hue_values=hue_values,
        C_upper=C_upper,
        iterations=iterations,
    )


def analyze_gamut(
    gamut: str | DisplayPrimaries | GamutBoundary,
    *,
    name: str | None = None,
    L_values: Sequence[float] | np.ndarray = np.arange(0.0, 101.0, 5.0),
    hue_values: Sequence[float] | np.ndarray = np.arange(0.0, 361.0, 5.0),
    C_upper: float = 300.0,
    iterations: int = 10,
    rec2020_boundary: GamutBoundary | None = None,
    pointer_boundary: GamutBoundary | None = None,
    macadam_d65_boundary: GamutBoundary | None = None,
) -> GamutAnalysis:
    """Return a high-level analysis summary for a gamut."""
    boundary = _as_boundary(
        gamut,
        L_values=L_values,
        hue_values=hue_values,
        C_upper=C_upper,
        iterations=iterations,
    )
    rec2020 = (
        compute_LCH_gamut_boundary(
            "Rec.2020",
            L_values=L_values,
            hue_values=hue_values,
            C_upper=C_upper,
            iterations=iterations,
        )
        if rec2020_boundary is None
        else rec2020_boundary
    )
    pointer = pointer_gamut() if pointer_boundary is None else pointer_boundary
    macadam_d65 = (
        _default_macadam_d65_boundary(
            L_values=L_values,
            hue_values=hue_values,
            C_upper=C_upper,
            iterations=iterations,
        )
        if macadam_d65_boundary is None
        else macadam_d65_boundary
    )

    xy_boundary = boundary.xy_boundary()
    warning_messages: list[str] = []

    volume_coverage_rec2020 = _record_warning_call(
        warning_messages,
        lab_gamut_coverage,
        boundary,
        rec2020,
    )
    volume_coverage_pointer = _record_warning_call(
        warning_messages,
        lab_gamut_coverage,
        boundary,
        pointer,
    )
    volume_coverage_macadam_d65 = _record_warning_call(
        warning_messages,
        lab_gamut_coverage,
        boundary,
        macadam_d65,
    )

    return GamutAnalysis(
        name=_name_from_gamut(gamut, name),
        boundary=boundary,
        xy_area=xy_gamut_area_from_xy(xy_boundary),
        xy_coverage_rec2020=xy_gamut_coverage_from_xy(
            xy_boundary,
            rec2020.xy_boundary(),
        ),
        xy_coverage_pointer=xy_gamut_coverage_from_xy(
            xy_boundary,
            pointer.xy_boundary(),
        ),
        xy_coverage_macadam_d65=xy_gamut_coverage_from_xy(
            xy_boundary,
            macadam_d65.xy_boundary(),
        ),
        lab_volume=lab_gamut_volume(boundary),
        projected_ab_area=boundary.projected_ab_area(),
        ring_area=boundary.ring_area(),
        volume_coverage_rec2020=float(volume_coverage_rec2020),
        volume_coverage_pointer=float(volume_coverage_pointer),
        volume_coverage_macadam_d65=float(volume_coverage_macadam_d65),
        warnings=tuple(warning_messages),
    )


__all__ = [
    "GamutAnalysis",
    "analyze_gamut",
]
