"""Multi-channel spectral distribution."""

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
from .distribution import SpectralDistribution
from .shape import SpectralShape


SpectralData = Mapping[str, np.ndarray]


class MultiSpectralDistribution:
    """Multi-channel spectral distribution."""

    def __init__(
        self,
        wavelengths: Sequence[float] | np.ndarray,
        values: Sequence[Sequence[float]] | np.ndarray,
        labels: Sequence[str],
        *,
        name: str = "",
        metadata: Mapping[str, Any] | None = None,
        fill_nan: float | None = None,
    ) -> None:
        wl = readonly_array(wavelengths, ndim=1, name="wavelengths")
        val = readonly_array(values, ndim=2, name="values")
        val, meta = apply_nan_policy(val, metadata, fill_nan=fill_nan)
        check_wavelengths(wl)
        label_tuple = tuple(labels)
        if wl.shape[0] != val.shape[0]:
            raise ValueError(
                "wavelength count must match values rows, "
                f"got {wl.shape[0]} and {val.shape[0]}"
            )
        if val.shape[1] != len(label_tuple):
            raise ValueError(
                "label count must match values columns, "
                f"got {len(label_tuple)} and {val.shape[1]}"
            )
        if len(set(label_tuple)) != len(label_tuple):
            raise ValueError("labels must be unique")

        self._wavelengths = wl
        self._values = val
        self.labels = label_tuple
        self.name = name
        self.metadata = meta

    @property
    def wavelengths(self) -> np.ndarray:
        """Distribution wavelength samples."""
        return self._wavelengths

    @property
    def values(self) -> np.ndarray:
        """Distribution values with shape ``(n_wavelengths, n_channels)``."""
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
        ys: Sequence[str],
        name: str = "",
        metadata: Mapping[str, Any] | None = None,
        fill_nan: float | None = None,
    ) -> "MultiSpectralDistribution":
        """Build a multi-channel distribution from a column mapping."""
        if x not in raw:
            raise ValueError(f"missing wavelength column {x!r}")
        missing = [label for label in ys if label not in raw]
        if missing:
            raise ValueError(f"missing value columns: {missing}")
        values = np.column_stack([raw[label] for label in ys])
        return cls(
            raw[x],
            values,
            tuple(ys),
            name=name,
            metadata=metadata,
            fill_nan=fill_nan,
        )

    def copy(self) -> "MultiSpectralDistribution":
        """Return an independent copy."""
        return MultiSpectralDistribution(
            self.wavelengths,
            self.values,
            self.labels,
            name=self.name,
            metadata=self.metadata,
        )

    def keys(self) -> tuple[str, ...]:
        """Return raw column keys matching :meth:`to_dict`."""
        return ("wavelength", *self.labels)

    def __getitem__(self, key: str) -> np.ndarray | SpectralDistribution:
        """Return a raw column or one channel by key."""
        if key == "wavelength":
            return self.wavelengths
        if key in self.labels:
            return self.channel(key)
        raise KeyError(f"unknown spectral column {key!r}")

    def to_dict(self) -> dict[str, np.ndarray]:
        """Return a raw column mapping."""
        result = {"wavelength": np.array(self.wavelengths, copy=True)}
        for index, label in enumerate(self.labels):
            result[label] = np.array(self.values[:, index], copy=True)
        return result

    def to_numpy(self) -> np.ndarray:
        """Return a ``(n, 1 + channels)`` wavelength/value array."""
        return np.column_stack((self.wavelengths, self.values))

    def to_pandas(self):
        """Return a pandas DataFrame with wavelength and channel columns."""
        try:
            import pandas as pd
        except ImportError as exc:  # pragma: no cover - depends on environment.
            raise ImportError("pandas is required for to_pandas()") from exc
        return pd.DataFrame(self.to_numpy(), columns=["wavelength", *self.labels])

    def channel(self, label: str) -> SpectralDistribution:
        """Return one channel as a single-channel distribution."""
        if label not in self.labels:
            raise KeyError(f"unknown spectral channel {label!r}")
        index = self.labels.index(label)
        metadata = dict(self.metadata)
        metadata["channel"] = label
        return SpectralDistribution(
            self.wavelengths,
            self.values[:, index],
            name=f"{self.name}:{label}" if self.name else label,
            metadata=metadata,
        )

    def interpolate(
        self,
        wavelengths: Sequence[float] | np.ndarray,
        *,
        method: Interpolator = "auto",
        bounds_error: bool = True,
        fill_value: float = np.nan,
    ) -> "MultiSpectralDistribution":
        """Return an interpolated multi-channel distribution."""
        target = target_wavelengths(wavelengths)
        values = interpolate_values(
            self.wavelengths,
            self.values,
            target,
            method=method,
            bounds_error=bounds_error,
            fill_value=fill_value,
        )
        return MultiSpectralDistribution(
            target,
            values,
            self.labels,
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
        """Return interpolated channel values at *wavelengths*."""
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
    ) -> "MultiSpectralDistribution":
        """Return this distribution sampled at *shape* wavelengths."""
        return self.interpolate(shape.wavelengths, method=method)

    def trim(self, shape: SpectralShape) -> "MultiSpectralDistribution":
        """Return source samples inside *shape* bounds."""
        mask = (self.wavelengths >= shape.start) & (self.wavelengths <= shape.end)
        if not np.any(mask):
            raise ValueError("shape does not overlap the distribution domain")
        return MultiSpectralDistribution(
            self.wavelengths[mask],
            self.values[mask, :],
            self.labels,
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
    ) -> "MultiSpectralDistribution":
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
        return MultiSpectralDistribution(
            target,
            values,
            self.labels,
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
    ) -> "MultiSpectralDistribution":
        """Return this distribution sampled at *shape* with extrapolation."""
        return self.extrapolate(
            shape,
            interpolator=interpolator,
            method=extrapolator,
            fill_value=fill_value,
            left=left,
            right=right,
        )

    def _binary_op(self, other: Any, op, op_name: str) -> "MultiSpectralDistribution":
        if isinstance(other, MultiSpectralDistribution):
            if not np.array_equal(self.wavelengths, other.wavelengths):
                raise ValueError(f"cannot {op_name} distributions on different domains")
            if self.labels != other.labels:
                raise ValueError(f"cannot {op_name} distributions with different labels")
            values = op(self.values, other.values)
        elif np.isscalar(other):
            values = op(self.values, other)
        else:
            return NotImplemented
        return MultiSpectralDistribution(
            self.wavelengths,
            values,
            self.labels,
            name=self.name,
            metadata=self.metadata,
        )

    def __add__(self, other: Any) -> "MultiSpectralDistribution":
        return self._binary_op(other, np.add, "add")

    def __radd__(self, other: Any) -> "MultiSpectralDistribution":
        return self.__add__(other)

    def __sub__(self, other: Any) -> "MultiSpectralDistribution":
        return self._binary_op(other, np.subtract, "subtract")

    def __rsub__(self, other: Any) -> "MultiSpectralDistribution":
        if np.isscalar(other):
            return MultiSpectralDistribution(
                self.wavelengths,
                np.subtract(other, self.values),
                self.labels,
                name=self.name,
                metadata=self.metadata,
            )
        return NotImplemented

    def __mul__(self, other: Any) -> "MultiSpectralDistribution":
        return self._binary_op(other, np.multiply, "multiply")

    def __rmul__(self, other: Any) -> "MultiSpectralDistribution":
        return self.__mul__(other)

    def __truediv__(self, other: Any) -> "MultiSpectralDistribution":
        return self._binary_op(other, np.divide, "divide")

    def __rtruediv__(self, other: Any) -> "MultiSpectralDistribution":
        if np.isscalar(other):
            return MultiSpectralDistribution(
                self.wavelengths,
                np.divide(other, self.values),
                self.labels,
                name=self.name,
                metadata=self.metadata,
            )
        return NotImplemented
