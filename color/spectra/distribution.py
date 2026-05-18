"""Single-channel spectral distribution."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from color.math import Extrapolator, Interpolator

from .base import (
    apply_nan_policy,
    check_wavelengths,
    extrapolate_values,
    interpolate_values,
    readonly_array,
    target_wavelengths,
)
from .shape import SpectralShape


SpectralData = Mapping[str, np.ndarray]


class SpectralDistribution:
    """Single-channel spectral distribution."""

    def __init__(
        self,
        wavelengths: Sequence[float] | np.ndarray,
        values: Sequence[float] | np.ndarray,
        *,
        name: str = "",
        metadata: Mapping[str, Any] | None = None,
        fill_nan: float | None = None,
    ) -> None:
        wl = readonly_array(wavelengths, ndim=1, name="wavelengths")
        val = readonly_array(values, ndim=1, name="values")
        val, meta = apply_nan_policy(val, metadata, fill_nan=fill_nan)
        check_wavelengths(wl)
        if wl.shape[0] != val.shape[0]:
            raise ValueError(
                "wavelengths and values must have the same length, "
                f"got {wl.shape[0]} and {val.shape[0]}"
            )

        self._wavelengths = wl
        self._values = val
        self.name = name
        self.metadata = meta

    @property
    def wavelengths(self) -> np.ndarray:
        """Distribution wavelength samples."""
        return self._wavelengths

    @property
    def values(self) -> np.ndarray:
        """Distribution values."""
        return self._values

    @property
    def domain(self) -> np.ndarray:
        """Alias for wavelength samples."""
        return self.wavelengths

    @property
    def range(self) -> np.ndarray:  # noqa: A003
        """Alias for distribution values."""
        return self.values

    @property
    def shape(self) -> SpectralShape:
        """Return a regular shape using the minimum sample interval."""
        intervals = np.diff(self.wavelengths)
        return SpectralShape(
            float(self.wavelengths[0]),
            float(self.wavelengths[-1]),
            float(intervals.min()) if intervals.size else 1.0,
        )

    @classmethod
    def from_columns(
        cls,
        raw: SpectralData,
        *,
        x: str = "wavelength",
        y: str = "value",
        name: str = "",
        metadata: Mapping[str, Any] | None = None,
        fill_nan: float | None = None,
    ) -> "SpectralDistribution":
        """Build a distribution from a column mapping."""
        if x not in raw:
            raise ValueError(f"missing wavelength column {x!r}")
        if y not in raw:
            raise ValueError(f"missing value column {y!r}")
        return cls(raw[x], raw[y], name=name, metadata=metadata, fill_nan=fill_nan)

    def copy(self) -> "SpectralDistribution":
        """Return an independent copy."""
        return SpectralDistribution(
            self.wavelengths,
            self.values,
            name=self.name,
            metadata=self.metadata,
        )

    def to_dict(self) -> dict[str, np.ndarray]:
        """Return a raw column mapping."""
        return {
            "wavelength": np.array(self.wavelengths, copy=True),
            "value": np.array(self.values, copy=True),
        }

    def to_numpy(self) -> np.ndarray:
        """Return a ``(n, 2)`` array with wavelength and value columns."""
        return np.column_stack((self.wavelengths, self.values))

    def to_pandas(self):
        """Return a pandas DataFrame with wavelength and value columns."""
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - depends on environment.
            raise ImportError("pandas is required for to_pandas()") from exc
        return pd.DataFrame(self.to_numpy(), columns=["wavelength", "value"])

    def interpolate(
        self,
        wavelengths: Sequence[float] | np.ndarray,
        *,
        method: Interpolator = "auto",
        bounds_error: bool = True,
        fill_value: float = np.nan,
    ) -> "SpectralDistribution":
        """Return an interpolated distribution."""
        target = target_wavelengths(wavelengths)
        values = interpolate_values(
            self.wavelengths,
            self.values,
            target,
            method=method,
            bounds_error=bounds_error,
            fill_value=fill_value,
        )
        return SpectralDistribution(
            target,
            values,
            name=self.name,
            metadata=self.metadata,
        )

    def sample(
        self,
        wavelengths: Sequence[float] | np.ndarray,
        *,
        method: Interpolator = "auto",
        bounds_error: bool = True,
        fill_value: float = np.nan,
    ) -> np.ndarray:
        """Return interpolated values at *wavelengths*."""
        return self.interpolate(
            wavelengths,
            method=method,
            bounds_error=bounds_error,
            fill_value=fill_value,
        ).values

    def __call__(
        self,
        wavelengths: Sequence[float] | np.ndarray,
        *,
        method: Interpolator = "auto",
        bounds_error: bool = True,
        fill_value: float = np.nan,
    ) -> np.ndarray:
        return self.sample(
            wavelengths,
            method=method,
            bounds_error=bounds_error,
            fill_value=fill_value,
        )

    def reshape(
        self,
        shape: SpectralShape,
        *,
        method: Interpolator = "auto",
    ) -> "SpectralDistribution":
        """Return this distribution sampled at *shape* wavelengths."""
        return self.interpolate(shape.wavelengths, method=method)

    def trim(self, shape: SpectralShape) -> "SpectralDistribution":
        """Return source samples inside *shape* bounds."""
        mask = (self.wavelengths >= shape.start) & (self.wavelengths <= shape.end)
        if not np.any(mask):
            raise ValueError("shape does not overlap the distribution domain")
        return SpectralDistribution(
            self.wavelengths[mask],
            self.values[mask],
            name=self.name,
            metadata=self.metadata,
        )

    def extrapolate(
        self,
        shape: SpectralShape,
        *,
        interpolator: Interpolator = "auto",
        method: Extrapolator = "fill",
        fill_value: float = np.nan,
        left: float | None = None,
        right: float | None = None,
    ) -> "SpectralDistribution":
        """Return this distribution sampled at *shape*, filling outside domain."""
        target = shape.wavelengths
        values = extrapolate_values(
            self.wavelengths,
            self.values,
            target,
            interpolator=interpolator,
            method=method,
            fill_value=fill_value,
            left=left,
            right=right,
        )
        return SpectralDistribution(
            target,
            values,
            name=self.name,
            metadata=self.metadata,
        )

    def align(
        self,
        shape: SpectralShape,
        *,
        interpolator: Interpolator = "auto",
        extrapolator: Extrapolator = "constant",
        fill_value: float = np.nan,
        left: float | None = None,
        right: float | None = None,
    ) -> "SpectralDistribution":
        """Return this distribution sampled at *shape* with extrapolation."""
        return self.extrapolate(
            shape,
            interpolator=interpolator,
            method=extrapolator,
            fill_value=fill_value,
            left=left,
            right=right,
        )

    def _binary_op(self, other: Any, op, op_name: str) -> "SpectralDistribution":
        if isinstance(other, SpectralDistribution):
            if not np.array_equal(self.wavelengths, other.wavelengths):
                raise ValueError(f"cannot {op_name} distributions on different domains")
            values = op(self.values, other.values)
        elif np.isscalar(other):
            values = op(self.values, other)
        else:
            return NotImplemented
        return SpectralDistribution(
            self.wavelengths,
            values,
            name=self.name,
            metadata=self.metadata,
        )

    def __add__(self, other: Any) -> "SpectralDistribution":
        return self._binary_op(other, np.add, "add")

    def __radd__(self, other: Any) -> "SpectralDistribution":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "SpectralDistribution":
        return self._binary_op(other, np.subtract, "subtract")

    def __rsub__(self, other: Any) -> "SpectralDistribution":
        if np.isscalar(other):
            return SpectralDistribution(
                self.wavelengths,
                np.subtract(other, self.values),
                name=self.name,
                metadata=self.metadata,
            )
        return NotImplemented

    def __mul__(self, other: Any) -> "SpectralDistribution":
        return self._binary_op(other, np.multiply, "multiply")

    def __rmul__(self, other: Any) -> "SpectralDistribution":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "SpectralDistribution":
        return self._binary_op(other, np.divide, "divide")

    def __rtruediv__(self, other: Any) -> "SpectralDistribution":
        if np.isscalar(other):
            return SpectralDistribution(
                self.wavelengths,
                np.divide(other, self.values),
                name=self.name,
                metadata=self.metadata,
            )
        return NotImplemented
