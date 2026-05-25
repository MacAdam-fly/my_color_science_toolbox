"""Academy Spectral Similarity Index (SSI)."""

from __future__ import annotations

import numpy as np
from scipy.ndimage import convolve1d

from color.spectra import SpectralDistribution, SpectralShape


SPECTRAL_SHAPE_SSI = SpectralShape(375.0, 675.0, 1.0)
"""Academy SSI spectral sampling shape."""

_SPECTRAL_SHAPE_SSI_LARGE = SpectralShape(380.0, 670.0, 10.0)
_MATRIX_INTEGRATION: np.ndarray | None = None


def _safe_divide(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
    """Return ``numerator / denominator`` with zero where division is invalid."""
    return np.divide(
        numerator,
        denominator,
        out=np.zeros_like(numerator, dtype=np.float64),
        where=denominator != 0,
    )


def _integration_matrix() -> np.ndarray:
    """Return the cached 10 nm SSI integration matrix."""
    global _MATRIX_INTEGRATION  # noqa: PLW0603
    if _MATRIX_INTEGRATION is None:
        matrix = np.zeros(
            (len(_SPECTRAL_SHAPE_SSI_LARGE), len(SPECTRAL_SHAPE_SSI)),
            dtype=np.float64,
        )
        weights = np.array([0.5, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.5])
        for index in range(matrix.shape[0]):
            matrix[index, (10 * index) : (10 * index + weights.size)] = weights
        matrix.setflags(write=False)
        _MATRIX_INTEGRATION = matrix
    return _MATRIX_INTEGRATION


def _as_ssi_values(sd: SpectralDistribution, name: str) -> np.ndarray:
    """Return *sd* values aligned to the SSI shape."""
    if not isinstance(sd, SpectralDistribution):
        raise TypeError(f"{name} must be a SpectralDistribution")
    if not np.all(np.isfinite(sd.values)):
        raise ValueError(f"{name} values must be finite")
    return sd.extrapolate(
        SPECTRAL_SHAPE_SSI,
        interpolator="linear",
        method="fill",
        fill_value=0.0,
    ).values


def spectral_similarity_index(
    test: SpectralDistribution,
    reference: SpectralDistribution,
    *,
    round_result: bool = True,
) -> np.ndarray:
    """Return the Academy Spectral Similarity Index of two spectra."""
    matrix = _integration_matrix()
    test_values = matrix @ _as_ssi_values(test, "test")
    reference_values = matrix @ _as_ssi_values(reference, "reference")

    test_values = _safe_divide(test_values, np.array(np.sum(test_values)))
    reference_values = _safe_divide(
        reference_values,
        np.array(np.sum(reference_values)),
    )
    relative_difference = _safe_divide(
        test_values - reference_values,
        reference_values + 1.0 / 30.0,
    )

    weights = np.array(
        [
            4 / 15,
            22 / 45,
            32 / 45,
            40 / 45,
            44 / 45,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            11 / 15,
            3 / 15,
        ],
        dtype=np.float64,
    )
    weighted = relative_difference * weights
    smoothed = convolve1d(weighted, [0.22, 0.56, 0.22], mode="constant", cval=0)
    value = 100.0 - 32.0 * np.sqrt(np.sum(smoothed**2))
    return np.around(value) if round_result else value


__all__ = [
    "SPECTRAL_SHAPE_SSI",
    "spectral_similarity_index",
]
