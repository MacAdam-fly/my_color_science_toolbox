"""Conversion helpers for spectral objects."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from .distribution import SpectralDistribution
from .multi_distribution import MultiSpectralDistribution


SpectralData = Mapping[str, np.ndarray]


def from_columns(
    raw: SpectralData,
    *,
    x: str = "wavelength",
    y: str | None = None,
    ys: Sequence[str] | None = None,
    name: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> SpectralDistribution | MultiSpectralDistribution:
    """Build a spectral object from a raw column mapping."""
    if y is not None and ys is not None:
        raise ValueError("provide either y or ys, not both")
    if y is None and ys is None:
        raise ValueError("provide y or ys")
    if y is not None:
        return SpectralDistribution.from_columns(
            raw,
            x=x,
            y=y,
            name=name,
            metadata=metadata,
        )
    assert ys is not None
    return MultiSpectralDistribution.from_columns(
        raw,
        x=x,
        ys=ys,
        name=name,
        metadata=metadata,
    )


def from_dataset(
    category: str,
    name: str,
    **kwargs: Any,
) -> SpectralDistribution | MultiSpectralDistribution:
    """Build a spectral object from a registered static dataset."""
    from color.datasets import describe, get

    raw = get(category, name, **kwargs)
    entry = describe(category, name)
    if "wavelength" not in raw:
        raise ValueError(
            f"Dataset {entry.category!r}/{entry.name!r} has no wavelength column"
        )

    labels = tuple(label for label in raw if label != "wavelength")
    if not labels:
        raise ValueError(
            f"Dataset {entry.category!r}/{entry.name!r} has no spectral value columns"
        )

    object_name = entry.name
    metadata = dict(entry.metadata)
    metadata.setdefault("dataset_category", entry.category)
    metadata.setdefault("dataset_name", entry.name)
    if len(labels) == 1:
        return SpectralDistribution.from_columns(
            raw,
            x="wavelength",
            y=labels[0],
            name=object_name,
            metadata=metadata,
        )

    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=labels,
        name=object_name,
        metadata=metadata,
    )
