"""Recovery method option objects."""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import ClassVar, Sequence

import numpy as np

from .library import ReflectanceLibrary


class SpectrumRecoveryOption:
    """Marker base class for effective-spectrum recovery options."""


class ReflectanceRecoveryOption:
    """Marker base class for reflectance recovery options."""


@dataclass(frozen=True)
class BoundedLeastSquaresOptions(SpectrumRecoveryOption, ReflectanceRecoveryOption):
    """Options for bounded smooth least-squares recovery.

    Parameters
    ----------
    bounds:
        Lower and upper bounds for the recovered spectrum or reflectance.
        Use ``None`` to let the calling entry choose its domain default:
        spectrum recovery uses ``(0, inf)`` and reflectance recovery uses
        ``(0, 1)``.
    smoothness:
        Weight of the second-difference smoothness penalty. Larger values
        produce smoother curves, at the cost of less freedom to match sharp
        spectral structure.

    Returns
    -------
    BoundedLeastSquaresOptions
        Method options object accepted by spectrum and reflectance recovery.

    Notes
    -----
    This method has the most freedom and is useful as a baseline. It may fit
    target responses well while producing curves that do not look like real
    materials.

    Examples
    --------
    >>> BoundedLeastSquaresOptions(bounds=(0.0, 1.0), smoothness=1e-3).method_name
    'bounded_least_squares'
    """

    method_name: ClassVar[str] = "bounded_least_squares"
    bounds: tuple[float, float] | None = None
    smoothness: float = 1e-3


@dataclass(frozen=True)
class GaussianRecoveryOptions(SpectrumRecoveryOption):
    """Options for single-Gaussian effective-spectrum recovery.

    Parameters
    ----------
    amplitude_bounds:
        Bounds for the Gaussian amplitude.
    center_bounds:
        Optional bounds for the Gaussian centre wavelength in nanometres. When
        ``None``, the active spectral shape range is used.
    sigma_bounds:
        Bounds for the Gaussian standard deviation in nanometres.
    center_initials:
        Optional candidate centre wavelengths used as optimisation starting
        points. If omitted, the solver builds fallback starts; XYZ recovery can
        also add dominant-wavelength starts.
    error:
        Residual scaling mode. ``"relative"`` scales residuals by the target
        response magnitude; ``"absolute"`` uses raw response residuals.
    use_dominant_wavelength_initial:
        For ``recover_spectrum_from_XYZ(...)``, add dominant-wavelength based
        centre starts when chromaticity analysis is available. Generic response
        and LMS recovery do not use this automatically.
    whitepoint_xy:
        Whitepoint chromaticity used by dominant-wavelength analysis for XYZ
        recovery.

    Returns
    -------
    GaussianRecoveryOptions
        Method options object for ``method="gaussian"`` spectrum recovery.

    Notes
    -----
    This method is for effective spectrum recovery, not reflectance recovery. It
    is most appropriate for single-peak emission-like spectra.

    Examples
    --------
    >>> GaussianRecoveryOptions(sigma_bounds=(2.0, 80.0)).method_name
    'gaussian'
    """

    method_name: ClassVar[str] = "gaussian"
    amplitude_bounds: tuple[float, float] = (0.0, float("inf"))
    center_bounds: tuple[float, float] | None = None
    sigma_bounds: tuple[float, float] = (2.0, 120.0)
    center_initials: Sequence[float] | np.ndarray | None = None
    error: str = "relative"
    use_dominant_wavelength_initial: bool = True
    whitepoint_xy: Sequence[float] = (0.3127, 0.3290)


@dataclass(frozen=True)
class MultiGaussianRecoveryOptions(SpectrumRecoveryOption):
    """Options for multi-Gaussian effective-spectrum recovery.

    Parameters
    ----------
    amplitude_bounds:
        Bounds for each Gaussian amplitude.
    center_bounds:
        Optional bounds for Gaussian centre wavelengths in nanometres. When
        ``None``, the active spectral shape range is used.
    sigma_bounds:
        Bounds for each Gaussian standard deviation in nanometres.
    center_initials:
        Optional candidate centre wavelengths used to build multi-component
        starting points.
    error:
        Residual scaling mode. ``"relative"`` scales residuals by the target
        response magnitude; ``"absolute"`` uses raw response residuals.
    n_components:
        Number of Gaussian components. The v1 implementation supports ``2`` or
        ``3`` components.
    use_dominant_wavelength_initial:
        For ``recover_spectrum_from_XYZ(...)``, use chromaticity analysis to
        bias starts toward spectral or complementary-wavelength directions.
    whitepoint_xy:
        Whitepoint chromaticity used by dominant-wavelength analysis for XYZ
        recovery.

    Returns
    -------
    MultiGaussianRecoveryOptions
        Method options object for ``method="multi_gaussian"`` spectrum recovery.

    Notes
    -----
    This method is useful for effective spectra with multiple peaks, including
    purple or complementary-wavelength targets that a single Gaussian cannot
    express well.

    Examples
    --------
    >>> MultiGaussianRecoveryOptions(n_components=2).method_name
    'multi_gaussian'
    """

    method_name: ClassVar[str] = "multi_gaussian"
    amplitude_bounds: tuple[float, float] = (0.0, float("inf"))
    center_bounds: tuple[float, float] | None = None
    sigma_bounds: tuple[float, float] = (2.0, 120.0)
    center_initials: Sequence[float] | np.ndarray | None = None
    error: str = "relative"
    n_components: int = 2
    use_dominant_wavelength_initial: bool = True
    whitepoint_xy: Sequence[float] = (0.3127, 0.3290)


@dataclass(frozen=True)
class AutoGaussianRecoveryOptions(SpectrumRecoveryOption):
    """Options for automatic single/multi-Gaussian recovery.

    ``auto_gaussian`` is a strategy option, not a separate spectral model. For
    XYZ recovery it uses chromaticity analysis to choose single Gaussian for
    spectral-dominant colours and multi Gaussian for purple, complementary, or
    near-white targets. Generic response and LMS recovery fall back to the
    multi-Gaussian path.

    Parameters
    ----------
    amplitude_bounds:
        Bounds for Gaussian amplitudes.
    center_bounds:
        Optional bounds for centre wavelengths in nanometres. When ``None``,
        the active spectral shape range is used.
    sigma_bounds:
        Bounds for Gaussian standard deviations in nanometres.
    center_initials:
        Optional candidate centre wavelengths used as optimisation starts.
    error:
        Residual scaling mode, ``"relative"`` or ``"absolute"``.
    n_components:
        Number of components for the selected multi-Gaussian path. The v1
        implementation supports ``2`` or ``3`` components.
    use_dominant_wavelength_initial:
        Enable dominant-wavelength based model selection and centre starts for
        XYZ recovery.
    whitepoint_xy:
        Whitepoint chromaticity used by dominant-wavelength analysis.

    Returns
    -------
    AutoGaussianRecoveryOptions
        Strategy options object for automatic Gaussian spectrum recovery.

    Notes
    -----
    ``auto_gaussian`` is a dispatcher over the Gaussian models. It is not a new
    spectral basis and does not apply to reflectance recovery.

    Examples
    --------
    >>> AutoGaussianRecoveryOptions(n_components=2).method_name
    'auto_gaussian'
    """

    method_name: ClassVar[str] = "auto_gaussian"
    amplitude_bounds: tuple[float, float] = (0.0, float("inf"))
    center_bounds: tuple[float, float] | None = None
    sigma_bounds: tuple[float, float] = (2.0, 120.0)
    center_initials: Sequence[float] | np.ndarray | None = None
    error: str = "relative"
    n_components: int = 2
    use_dominant_wavelength_initial: bool = True
    whitepoint_xy: Sequence[float] = (0.3127, 0.3290)


@dataclass(frozen=True)
class Burns2019RecoveryOptions(ReflectanceRecoveryOption):
    """Options for Burns 2019 Method 3 reflectance recovery.

    Parameters
    ----------
    bounds:
        Reflectance bounds. Burns 2019 Method 3 currently supports only
        ``(0, 1)`` because the implementation uses the ``tanh`` variable
        transform for bounded object reflectance.
    max_iterations:
        Maximum Newton iterations per target colour.
    tolerance:
        Convergence tolerance for the Newton solve and closure residual.

    Returns
    -------
    Burns2019RecoveryOptions
        Method options object for Burns 2019 reflectance recovery.

    Notes
    -----
    Burns 2019 is database-free and keeps reflectance inside ``(0, 1)`` through
    a variable transform. It can still fail for targets near feasibility
    boundaries.

    Examples
    --------
    >>> Burns2019RecoveryOptions().method_name
    'burns2019'
    """

    method_name: ClassVar[str] = "burns2019"
    bounds: tuple[float, float] = (0.0, 1.0)
    max_iterations: int = 50
    tolerance: float = 1e-8


@dataclass(frozen=True)
class Meng2015RecoveryOptions(ReflectanceRecoveryOption):
    """Options for Meng et al. 2015 reflectance recovery.

    Parameters
    ----------
    bounds:
        Lower and upper bounds for reflectance values. The optimisation treats
        the target XYZ match as an equality constraint and searches for the
        smoothest feasible bounded reflectance.

    Returns
    -------
    Meng2015RecoveryOptions
        Method options object for Meng 2015 reflectance recovery.

    Notes
    -----
    Meng 2015 is database-free and strongly prioritises exact target closure.
    If the target is infeasible under the selected bounds and sampling, the
    optimisation can fail.

    Examples
    --------
    >>> Meng2015RecoveryOptions().method_name
    'meng2015'
    """

    method_name: ClassVar[str] = "meng2015"
    bounds: tuple[float, float] = (0.0, 1.0)


@dataclass(frozen=True)
class PCAReflectanceOptions(ReflectanceRecoveryOption):
    """Options for PCA reflectance recovery.

    Parameters
    ----------
    library:
        Explicit ``ReflectanceLibrary`` used to learn the PCA basis. This is
        required; recovery entries do not auto-load a library because the
        library is a modelling prior.
    bounds:
        Bounds applied to the reconstructed reflectance
        ``mean_reflectance + basis @ coefficients``.
    n_components:
        Number of PCA components used for reconstruction.
    coefficient_regularization:
        L2 penalty on normalised PCA coefficients. Larger values keep the
        solution closer to the library mean and reduce extreme coefficient use.

    Returns
    -------
    PCAReflectanceOptions
        Method options object for PCA reflectance recovery.

    Notes
    -----
    PCA restricts recovery to a low-dimensional library-derived subspace. This
    can produce material-like curves, but it can also increase XYZ closure error
    when the target is outside the library prior.

    Examples
    --------
    >>> PCAReflectanceOptions(n_components=8).method_name
    'pca'
    """

    method_name: ClassVar[str] = "pca"
    library: ReflectanceLibrary | None = None
    bounds: tuple[float, float] = (0.0, 1.0)
    n_components: int = 8
    coefficient_regularization: float = 1e-3


@dataclass(frozen=True)
class DictionaryReflectanceOptions(ReflectanceRecoveryOption):
    """Options for convex dictionary reflectance recovery.

    Parameters
    ----------
    library:
        Explicit ``ReflectanceLibrary`` used as dictionary atoms. This is
        required; recovery entries do not auto-load a library because the
        library is a modelling prior.
    regularization:
        Small L2 penalty on dictionary weights. This stabilises the convex
        optimisation but does not make the solution sparse.
    top_k:
        Number of nearest library samples, measured in response space, used as
        candidate atoms for the convex solve. Use ``None`` to optimise over the
        full library.

    Returns
    -------
    DictionaryReflectanceOptions
        Method options object for convex dictionary reflectance recovery.

    Notes
    -----
    Dictionary recovery returns a convex combination of library samples. The
    regularization stabilises weights but is not a sparsity penalty.

    Examples
    --------
    >>> DictionaryReflectanceOptions(top_k=120).method_name
    'dictionary'
    """

    method_name: ClassVar[str] = "dictionary"
    library: ReflectanceLibrary | None = None
    regularization: float = 1e-6
    top_k: int | None = 120


def option_values(option: object) -> dict:
    """Return dataclass field values for a recovery option object."""
    return {field.name: getattr(option, field.name) for field in fields(option)}


__all__ = [
    "SpectrumRecoveryOption",
    "ReflectanceRecoveryOption",
    "BoundedLeastSquaresOptions",
    "GaussianRecoveryOptions",
    "MultiGaussianRecoveryOptions",
    "AutoGaussianRecoveryOptions",
    "Burns2019RecoveryOptions",
    "Meng2015RecoveryOptions",
    "PCAReflectanceOptions",
    "DictionaryReflectanceOptions",
    "option_values",
]
