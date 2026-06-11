"""Spectral sampling domains."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SpectralShape:
    """Regular wavelength sampling domain.

    Parameters
    ----------
    start, end
        Inclusive wavelength bounds, usually in nanometres.
    interval
        Positive sampling interval.

    Returns
    -------
    SpectralShape
        Immutable regular sampling descriptor.

    Notes
    -----
    ``wavelengths`` includes the end value, appending it when the interval
    does not land exactly on ``end``.

    Examples
    --------
    >>> SpectralShape(400, 700, 10).wavelengths.shape
    (31,)
    """

    start: float
    end: float
    interval: float

    def __post_init__(self) -> None:
        if not np.isfinite([self.start, self.end, self.interval]).all():
            raise ValueError("SpectralShape values must be finite")
        if self.start >= self.end:
            raise ValueError("SpectralShape start must be less than end")
        if self.interval <= 0:
            raise ValueError("SpectralShape interval must be positive")

    @property
    def wavelengths(self) -> np.ndarray:
        """Return shape wavelengths, appending the end value when unaligned."""
        values = np.arange(
            self.start,
            self.end + self.interval * 0.5,
            self.interval,
            dtype=np.float64,
        )
        if values[-1] > self.end and not np.isclose(values[-1], self.end):
            values = values[:-1]
        if not np.isclose(values[-1], self.end):
            values = np.append(values, self.end)
        values.setflags(write=False)
        return values

    def __len__(self) -> int:
        return int(self.wavelengths.size)

    def __contains__(self, wavelength: object) -> bool:
        try:
            value = float(wavelength)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return False
        return bool(np.any(np.isclose(self.wavelengths, value)))
