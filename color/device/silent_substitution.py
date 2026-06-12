"""XYZ/LMS-silent melanopic substitution solvers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np
from scipy.optimize import linprog

from .responses import (
    LMS_RESPONSE_NAMES,
    XYZ_RESPONSE_NAMES,
    PrimaryResponseDisplay,
)


def _as_targets(value: Sequence[float] | np.ndarray, size: int) -> np.ndarray:
    """Return finite targets with final-axis length *size*."""
    targets = np.array(value, dtype=np.float64, copy=True)
    if targets.shape == () or targets.shape[-1] != size:
        raise ValueError(f"target_responses must have final-axis length {size}")
    if not np.all(np.isfinite(targets)):
        raise ValueError("target_responses must contain finite values")
    targets.setflags(write=False)
    return targets


def _bounds(value: tuple[float, float], count: int) -> list[tuple[float, float]]:
    """Return repeated finite scalar bounds."""
    lower, upper = _bounds_pair(value)
    return [(lower, upper)] * count


def _bounds_pair(value: tuple[float, float]) -> tuple[float, float]:
    """Return validated scalar bounds."""
    if len(value) != 2:
        raise ValueError("bounds must be a (lower, upper) pair")
    lower, upper = float(value[0]), float(value[1])
    if not np.isfinite(lower) or not np.isfinite(upper):
        raise ValueError("bounds must be finite")
    if lower > upper:
        raise ValueError("bounds lower value must not exceed upper value")
    return lower, upper


def _held_response_names(held: str) -> tuple[str, str, str]:
    """Return canonical held response names."""
    key = held.strip().lower()
    if key == "lms":
        return LMS_RESPONSE_NAMES
    if key == "xyz":
        return XYZ_RESPONSE_NAMES
    raise ValueError("held must be 'LMS' or 'XYZ'")


def _objective_vector(display: PrimaryResponseDisplay, objective: str) -> tuple[np.ndarray, str]:
    """Return the linprog objective vector and normalized objective name."""
    key = objective.strip().lower().replace("-", "_")
    mel = display.primary_responses[:, display.mel_index]
    if key == "maximize_mel":
        return -mel, key
    if key == "minimize_mel":
        return mel, key
    raise ValueError("objective must be 'maximize_mel' or 'minimize_mel'")


def _validate_display_for_silent_substitution(
    display: PrimaryResponseDisplay,
    held_names: tuple[str, str, str],
) -> tuple[int, int, int]:
    """Validate that a display can support the requested held response group."""
    if display.primary_count < len(held_names) + 1:
        raise ValueError("melanopic silent substitution requires at least four primaries")
    return display.response_indices(held_names)


@dataclass(frozen=True)
class SilentSubstitutionResult:
    """Result of one melanopic silent-substitution optimisation.

    Attributes
    ----------
    weights
        Solved primary weights.
    responses
        Full response vector produced by ``weights``.
    target_responses
        Requested held response targets.
    melanopic
        Melanopic response value from ``responses``.
    held
        Held response group, either ``"LMS"`` or ``"XYZ"``.
    objective
        Normalized objective name.
    residual
        Residual of the held response group.
    success
        Whether all optimizer calls reported success.
    """

    weights: np.ndarray
    responses: np.ndarray
    target_responses: np.ndarray
    melanopic: np.ndarray | np.float64 | float
    held: str
    objective: str
    residual: np.ndarray
    success: bool

    def __post_init__(self) -> None:
        for field_name in ("weights", "responses", "target_responses", "residual"):
            array = np.array(getattr(self, field_name), dtype=np.float64, copy=True)
            array.setflags(write=False)
            object.__setattr__(self, field_name, array)

        melanopic = np.array(self.melanopic, dtype=np.float64, copy=True)
        melanopic.setflags(write=False)
        object.__setattr__(self, "melanopic", melanopic[()] if melanopic.shape == () else melanopic)
        object.__setattr__(self, "held", str(self.held))
        object.__setattr__(self, "objective", str(self.objective))
        object.__setattr__(self, "success", bool(self.success))


def _error_index_text(flat_index: int | None) -> str:
    """Return optional flat-index text for batch errors."""
    return "" if flat_index is None else f" at flat index {flat_index}"


def _result_from_weights(
    display: PrimaryResponseDisplay,
    weights: np.ndarray,
    target: np.ndarray,
    *,
    held_indices: tuple[int, int, int],
    objective: str,
    held: str,
    bounds: tuple[float, float],
    tolerance: float,
    flat_index: int | None = None,
) -> SilentSubstitutionResult:
    """Build a result object and validate constraints."""
    lower, upper = _bounds_pair(bounds)
    if np.any(weights < lower - tolerance) or np.any(weights > upper + tolerance):
        raise ValueError(
            "solver returned weights outside the requested bounds"
            f"{_error_index_text(flat_index)}"
        )

    weights = np.asarray(weights, dtype=np.float64)
    weights = weights.copy()
    weights[np.abs(weights - lower) <= tolerance] = lower
    weights[np.abs(weights - upper) <= tolerance] = upper

    responses = display.responses_from_weights(weights)
    residual = responses[list(held_indices)] - target
    if np.max(np.abs(residual)) > tolerance:
        raise ValueError(
            "solver returned weights outside the requested response "
            f"tolerance{_error_index_text(flat_index)}"
        )

    return SilentSubstitutionResult(
        weights=weights,
        responses=responses,
        target_responses=target,
        melanopic=responses[display.mel_index],
        held=held,
        objective=objective,
        residual=residual,
        success=True,
    )


def _solve_silent_substitution_endpoint(
    display: PrimaryResponseDisplay,
    target: np.ndarray,
    *,
    held_indices: tuple[int, int, int],
    objective: str,
    held: str,
    bounds: tuple[float, float],
    tolerance: float,
    flat_index: int | None = None,
) -> SilentSubstitutionResult:
    """Solve one melanopic endpoint with linear programming."""
    c, resolved_objective = _objective_vector(display, objective)
    result = linprog(
        c=c,
        A_eq=display.primary_responses[:, list(held_indices)].T,
        b_eq=target,
        bounds=_bounds(bounds, display.primary_count),
        method="highs",
    )
    if not result.success:
        raise ValueError(
            f"target_responses{_error_index_text(flat_index)} is not feasible "
            f"for this display: {result.message}"
        )

    return _result_from_weights(
        display,
        np.asarray(result.x, dtype=np.float64),
        target,
        held_indices=held_indices,
        objective=resolved_objective,
        held=held,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )


def _t_interval_for_bounds(
    w0: np.ndarray,
    z: np.ndarray,
    *,
    bounds: tuple[float, float],
    tolerance: float,
    flat_index: int | None = None,
) -> tuple[float, float]:
    """Return the feasible scalar interval for ``w = w0 + t*z``."""
    lower, upper = _bounds_pair(bounds)
    t_min = -np.inf
    t_max = np.inf
    for weight, direction in zip(w0, z):
        if abs(direction) <= tolerance:
            if weight < lower - tolerance or weight > upper + tolerance:
                raise ValueError(
                    f"target_responses{_error_index_text(flat_index)} is not "
                    "feasible for this display"
                )
            continue

        lo = (lower - weight) / direction
        hi = (upper - weight) / direction
        if lo > hi:
            lo, hi = hi, lo
        t_min = max(t_min, lo)
        t_max = min(t_max, hi)

    if t_min > t_max + tolerance:
        raise ValueError(
            f"target_responses{_error_index_text(flat_index)} is not feasible "
            "for this display"
        )
    return t_min, t_max


def _first_bad_index(mask: np.ndarray) -> int:
    """Return the first flat index where *mask* is true."""
    return int(np.flatnonzero(mask)[0])


def _four_primary_geometry(
    display: PrimaryResponseDisplay,
    held_indices: tuple[int, int, int],
    *,
    tolerance: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray] | None:
    """Return held matrix, pseudoinverse and null direction for four primaries."""
    if display.primary_count != len(held_indices) + 1:
        return None

    held_matrix = display.primary_responses[:, list(held_indices)].T
    _, singular_values, vh = np.linalg.svd(held_matrix, full_matrices=True)
    scale = singular_values[0] if singular_values.size else 1.0
    rank_tolerance = max(
        tolerance,
        np.finfo(np.float64).eps * max(held_matrix.shape) * scale,
    )
    rank = int(np.sum(singular_values > rank_tolerance))
    if rank != len(held_indices):
        return None

    direction = vh[-1, :]
    direction_norm = np.linalg.norm(direction)
    if direction_norm <= rank_tolerance:
        return None
    direction = direction / direction_norm
    return held_matrix, np.linalg.pinv(held_matrix), direction


def _t_intervals_for_bounds(
    w0: np.ndarray,
    z: np.ndarray,
    *,
    bounds: tuple[float, float],
    tolerance: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Return feasible scalar intervals for batched ``w = w0 + t*z``."""
    lower, upper = _bounds_pair(bounds)
    count = w0.shape[0]
    t_min = np.full(count, -np.inf, dtype=np.float64)
    t_max = np.full(count, np.inf, dtype=np.float64)
    for index, direction in enumerate(z):
        weights = w0[:, index]
        if abs(direction) <= tolerance:
            bad = (weights < lower - tolerance) | (weights > upper + tolerance)
            if np.any(bad):
                bad_index = _first_bad_index(bad)
                raise ValueError(
                    f"target_responses at flat index {bad_index} is not "
                    "feasible for this display"
                )
            continue

        lo = (lower - weights) / direction
        hi = (upper - weights) / direction
        interval_low = np.minimum(lo, hi)
        interval_high = np.maximum(lo, hi)
        t_min = np.maximum(t_min, interval_low)
        t_max = np.minimum(t_max, interval_high)

    bad = t_min > t_max + tolerance
    if np.any(bad):
        bad_index = _first_bad_index(bad)
        raise ValueError(
            f"target_responses at flat index {bad_index} is not feasible "
            "for this display"
        )
    return t_min, t_max


def _batched_result_from_weights(
    display: PrimaryResponseDisplay,
    weights_flat: np.ndarray,
    targets_flat: np.ndarray,
    targets: np.ndarray,
    *,
    leading_shape: tuple[int, ...],
    held_indices: tuple[int, int, int],
    objective: str,
    held: str,
    bounds: tuple[float, float],
    tolerance: float,
) -> SilentSubstitutionResult:
    """Build a batched result object and validate constraints."""
    lower, upper = _bounds_pair(bounds)
    bad_bounds = np.any(
        (weights_flat < lower - tolerance) | (weights_flat > upper + tolerance),
        axis=1,
    )
    if np.any(bad_bounds):
        bad_index = _first_bad_index(bad_bounds)
        raise ValueError(
            "solver returned weights outside the requested bounds "
            f"at flat index {bad_index}"
        )

    weights_flat = np.array(weights_flat, dtype=np.float64, copy=True)
    weights_flat[np.abs(weights_flat - lower) <= tolerance] = lower
    weights_flat[np.abs(weights_flat - upper) <= tolerance] = upper

    responses_flat = display.responses_from_weights(weights_flat)
    residual_flat = responses_flat[:, list(held_indices)] - targets_flat
    bad_residual = np.any(np.abs(residual_flat) > tolerance, axis=1)
    if np.any(bad_residual):
        bad_index = _first_bad_index(bad_residual)
        raise ValueError(
            "solver returned weights outside the requested response "
            f"tolerance at flat index {bad_index}"
        )

    return SilentSubstitutionResult(
        weights=weights_flat.reshape(*leading_shape, display.primary_count),
        responses=responses_flat.reshape(*leading_shape, display.response_count),
        target_responses=targets,
        melanopic=responses_flat[:, display.mel_index].reshape(leading_shape),
        held=held,
        objective=objective,
        residual=residual_flat.reshape(*leading_shape, len(held_indices)),
        success=True,
    )


def _four_primary_silent_range(
    display: PrimaryResponseDisplay,
    target: np.ndarray,
    *,
    held_indices: tuple[int, int, int],
    held: str,
    bounds: tuple[float, float],
    tolerance: float,
    flat_index: int | None = None,
) -> tuple[SilentSubstitutionResult, SilentSubstitutionResult] | None:
    """Return low/high endpoints with the four-primary nullspace fast path."""
    geometry = _four_primary_geometry(
        display,
        held_indices,
        tolerance=tolerance,
    )
    if geometry is None:
        return None
    held_matrix, held_pinv, direction = geometry

    particular = held_pinv @ target
    if np.max(np.abs(held_matrix @ particular - target)) > tolerance:
        return None

    t_min, t_max = _t_interval_for_bounds(
        particular,
        direction,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )
    mel_slope = display.primary_responses[:, display.mel_index] @ direction
    low_t, high_t = (t_min, t_max) if mel_slope >= 0 else (t_max, t_min)

    low = _result_from_weights(
        display,
        particular + low_t * direction,
        target,
        held_indices=held_indices,
        objective="minimize_mel",
        held=held,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )
    high = _result_from_weights(
        display,
        particular + high_t * direction,
        target,
        held_indices=held_indices,
        objective="maximize_mel",
        held=held,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )
    return low, high


def _four_primary_silent_range_batch(
    display: PrimaryResponseDisplay,
    targets: np.ndarray,
    *,
    held_indices: tuple[int, int, int],
    held: str,
    bounds: tuple[float, float],
    tolerance: float,
) -> tuple[SilentSubstitutionResult, SilentSubstitutionResult] | None:
    """Return batched low/high endpoints with the four-primary fast path."""
    geometry = _four_primary_geometry(
        display,
        held_indices,
        tolerance=tolerance,
    )
    if geometry is None:
        return None

    held_matrix, held_pinv, direction = geometry
    leading_shape = targets.shape[:-1]
    flat_targets = targets.reshape(-1, targets.shape[-1])
    particular = flat_targets @ held_pinv.T
    residual = particular @ held_matrix.T - flat_targets
    if np.max(np.abs(residual)) > tolerance:
        return None

    t_min, t_max = _t_intervals_for_bounds(
        particular,
        direction,
        bounds=bounds,
        tolerance=tolerance,
    )
    mel_slope = display.primary_responses[:, display.mel_index] @ direction
    low_t, high_t = (t_min, t_max) if mel_slope >= 0 else (t_max, t_min)
    low_weights = particular + low_t[:, None] * direction
    high_weights = particular + high_t[:, None] * direction

    low = _batched_result_from_weights(
        display,
        low_weights,
        flat_targets,
        targets,
        leading_shape=leading_shape,
        held_indices=held_indices,
        objective="minimize_mel",
        held=held,
        bounds=bounds,
        tolerance=tolerance,
    )
    high = _batched_result_from_weights(
        display,
        high_weights,
        flat_targets,
        targets,
        leading_shape=leading_shape,
        held_indices=held_indices,
        objective="maximize_mel",
        held=held,
        bounds=bounds,
        tolerance=tolerance,
    )
    return low, high


def _melanopic_silent_range_one(
    display: PrimaryResponseDisplay,
    target: np.ndarray,
    *,
    held_indices: tuple[int, int, int],
    held: str,
    bounds: tuple[float, float],
    tolerance: float,
    flat_index: int | None = None,
) -> tuple[SilentSubstitutionResult, SilentSubstitutionResult]:
    """Return low/high endpoints for one target."""
    fast_result = _four_primary_silent_range(
        display,
        target,
        held_indices=held_indices,
        held=held,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )
    if fast_result is not None:
        return fast_result

    low = _solve_silent_substitution_endpoint(
        display,
        target,
        held_indices=held_indices,
        objective="minimize_mel",
        held=held,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )
    high = _solve_silent_substitution_endpoint(
        display,
        target,
        held_indices=held_indices,
        objective="maximize_mel",
        held=held,
        bounds=bounds,
        tolerance=tolerance,
        flat_index=flat_index,
    )
    return low, high


def _combine_results(
    results: list[SilentSubstitutionResult],
    *,
    targets: np.ndarray,
    leading_shape: tuple[int, ...],
    display: PrimaryResponseDisplay,
    held_size: int,
    objective: str,
    held: str,
) -> SilentSubstitutionResult:
    """Combine one-point results into a batched result object."""
    weights = np.stack([result.weights for result in results]).reshape(*leading_shape, display.primary_count)
    responses = np.stack([result.responses for result in results]).reshape(*leading_shape, display.response_count)
    melanopic = np.stack([np.asarray(result.melanopic) for result in results]).reshape(leading_shape)
    residual = np.stack([result.residual for result in results]).reshape(*leading_shape, held_size)
    return SilentSubstitutionResult(
        weights=weights,
        responses=responses,
        target_responses=targets,
        melanopic=melanopic,
        held=held,
        objective=objective,
        residual=residual,
        success=all(result.success for result in results),
    )


def melanopic_silent_range(
    display: PrimaryResponseDisplay,
    target_responses: Sequence[float] | np.ndarray,
    *,
    held: str = "LMS",
    bounds: tuple[float, float] = (0.0, 1.0),
    tolerance: float = 1e-9,
) -> tuple[SilentSubstitutionResult, SilentSubstitutionResult]:
    """Return minimum and maximum melanopic silent-substitution endpoints."""
    if not isinstance(display, PrimaryResponseDisplay):
        raise ValueError("display must be a PrimaryResponseDisplay")
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")

    held_key = held.strip().upper()
    held_names = _held_response_names(held)
    held_indices = _validate_display_for_silent_substitution(display, held_names)
    targets = _as_targets(target_responses, len(held_indices))
    _bounds_pair(bounds)

    if targets.ndim == 1:
        return _melanopic_silent_range_one(
            display,
            targets,
            held_indices=held_indices,
            held=held_key,
            bounds=bounds,
            tolerance=tolerance,
        )

    fast_result = _four_primary_silent_range_batch(
        display,
        targets,
        held_indices=held_indices,
        held=held_key,
        bounds=bounds,
        tolerance=tolerance,
    )
    if fast_result is not None:
        return fast_result

    leading_shape = targets.shape[:-1]
    flat_targets = targets.reshape(-1, targets.shape[-1])
    pairs = [
        _melanopic_silent_range_one(
            display,
            target,
            held_indices=held_indices,
            held=held_key,
            bounds=bounds,
            tolerance=tolerance,
            flat_index=index,
        )
        for index, target in enumerate(flat_targets)
    ]
    lows = [pair[0] for pair in pairs]
    highs = [pair[1] for pair in pairs]
    minimum = _combine_results(
        lows,
        targets=targets,
        leading_shape=leading_shape,
        display=display,
        held_size=len(held_indices),
        objective="minimize_mel",
        held=held_key,
    )
    maximum = _combine_results(
        highs,
        targets=targets,
        leading_shape=leading_shape,
        display=display,
        held_size=len(held_indices),
        objective="maximize_mel",
        held=held_key,
    )
    return minimum, maximum


__all__ = [
    "SilentSubstitutionResult",
    "melanopic_silent_range",
]
