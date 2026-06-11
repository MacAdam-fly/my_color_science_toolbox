"""Reflectance library loading for recovery methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Sequence

import numpy as np

from color.datasets import get_reflectance_spectrum, list_reflectance_spectra
from color.spectra import MultiSpectralDistribution, SpectralShape, from_columns


DEFAULT_REFLECTANCE_LIBRARY_DATASETS = ("munsell_matt",)
DEFAULT_REFLECTANCE_LIBRARY_SHAPE = SpectralShape(400.0, 700.0, 5.0)


@dataclass(frozen=True)
class ReflectanceLibrary:
    """Aligned reflectance sample matrix for recovery algorithms.

    Parameters
    ----------
    wavelengths
        One-dimensional wavelength grid in nanometres.
    reflectances
        Reflectance matrix with shape ``(n_samples, n_wavelengths)``.
    labels
        Unique sample labels.
    sources
        Source dataset name for each sample.
    shape
        Common spectral shape used for alignment.
    metadata
        Library provenance and sample-count metadata.

    Returns
    -------
    ReflectanceLibrary
        Immutable reflectance library object.

    Notes
    -----
    Libraries are modelling priors for PCA and dictionary recovery. Choosing a
    library changes the solution family and can increase XYZ closure error when
    the target is far from the library distribution.

    Examples
    --------
    >>> library = load_reflectance_library("munsell_matt")
    >>> library.reflectances.shape[0] == len(library.labels)
    True
    """

    wavelengths: np.ndarray
    reflectances: np.ndarray
    labels: tuple[str, ...]
    sources: tuple[str, ...]
    shape: SpectralShape
    metadata: Mapping[str, Any]

    def __post_init__(self) -> None:
        wavelengths = np.asarray(self.wavelengths, dtype=np.float64)
        reflectances = np.asarray(self.reflectances, dtype=np.float64)
        if wavelengths.ndim != 1:
            raise ValueError("wavelengths must be a one-dimensional array")
        if reflectances.ndim != 2:
            raise ValueError("reflectances must be a two-dimensional array")
        if reflectances.shape[1] != wavelengths.size:
            raise ValueError(
                "reflectances columns must match wavelength count, "
                f"got {reflectances.shape[1]} and {wavelengths.size}"
            )
        if reflectances.shape[0] != len(self.labels):
            raise ValueError(
                "labels length must match sample count, "
                f"got {len(self.labels)} and {reflectances.shape[0]}"
            )
        if reflectances.shape[0] != len(self.sources):
            raise ValueError(
                "sources length must match sample count, "
                f"got {len(self.sources)} and {reflectances.shape[0]}"
            )
        if len(set(self.labels)) != len(self.labels):
            raise ValueError("labels must be unique")
        if not np.isfinite(wavelengths).all():
            raise ValueError("wavelengths must be finite")
        if not np.isfinite(reflectances).all():
            raise ValueError("reflectances must be finite")
        if np.any(reflectances < 0.0):
            raise ValueError("reflectances must be non-negative")

        wavelengths.setflags(write=False)
        reflectances.setflags(write=False)
        object.__setattr__(self, "wavelengths", wavelengths)
        object.__setattr__(self, "reflectances", reflectances)
        object.__setattr__(self, "labels", tuple(self.labels))
        object.__setattr__(self, "sources", tuple(self.sources))
        object.__setattr__(self, "metadata", dict(self.metadata))


def _normalise_datasets(datasets: str | Sequence[str]) -> tuple[str, ...]:
    """Return concrete UEF reflectance dataset names."""
    if isinstance(datasets, str):
        if datasets == "all":
            raise ValueError(
                "datasets='all' is not supported; use 'all_uef' or explicit names"
            )
        if datasets == "all_uef":
            return tuple(list_reflectance_spectra())
        return (datasets,)

    names = tuple(datasets)
    if not names:
        raise ValueError("datasets must not be empty")
    if any(not isinstance(name, str) for name in names):
        raise ValueError("datasets must contain dataset names as strings")
    if any(name in {"all", "all_uef"} for name in names):
        raise ValueError(
            "special dataset presets must be passed as a single string"
        )
    return names


def _as_shape(shape: SpectralShape | None) -> SpectralShape:
    """Return a concrete spectral shape."""
    if shape is None:
        return DEFAULT_REFLECTANCE_LIBRARY_SHAPE
    if not isinstance(shape, SpectralShape):
        raise ValueError("shape must be a SpectralShape instance or None")
    return shape


def _load_dataset(name: str, shape: SpectralShape) -> MultiSpectralDistribution:
    """Load one UEF reflectance dataset as an aligned spectral object."""
    try:
        raw = get_reflectance_spectrum(name)
    except KeyError as exc:
        raise ValueError(f"unknown reflectance dataset {name!r}") from exc
    labels = tuple(label for label in raw if label != "wavelength")
    if not labels:
        raise ValueError(f"reflectance dataset {name!r} has no sample columns")
    spectral = from_columns(
        raw,
        ys=labels,
        name=name,
        metadata={"reflectance_dataset": name},
    )
    if not isinstance(spectral, MultiSpectralDistribution):
        raise ValueError(f"reflectance dataset {name!r} must be multi-channel")
    return spectral.align(shape)


def _source_labels(source: str, labels: Iterable[str]) -> tuple[str, ...]:
    """Return globally unique labels for one source dataset."""
    return tuple(f"{source}:{label}" for label in labels)


def load_reflectance_library(
    datasets: str | Sequence[str] = DEFAULT_REFLECTANCE_LIBRARY_DATASETS,
    *,
    shape: SpectralShape | None = None,
) -> ReflectanceLibrary:
    """Load UEF reflectance spectra as an aligned sample matrix.

    Parameters
    ----------
    datasets:
        Dataset name, sequence of dataset names, or ``"all_uef"``.
    shape:
        Common wavelength sampling domain. ``None`` uses
        ``SpectralShape(400, 700, 5)``.

    Returns
    -------
    ReflectanceLibrary
        Read-only reflectance sample matrix and associated labels.

    Notes
    -----
    The default dataset is ``"munsell_matt"``. Passing ``"all_uef"`` expands to
    the currently registered UEF reflectance spectra only; it is not a global
    future-proof ``all datasets`` selector.

    Examples
    --------
    >>> library = load_reflectance_library()
    >>> library.metadata["datasets"]
    ('munsell_matt',)
    """
    concrete_shape = _as_shape(shape)
    names = _normalise_datasets(datasets)

    reflectance_blocks: list[np.ndarray] = []
    labels: list[str] = []
    sources: list[str] = []
    sample_counts: dict[str, int] = {}

    for name in names:
        aligned = _load_dataset(name, concrete_shape)
        values = np.asarray(aligned.values, dtype=np.float64).T
        if not np.isfinite(values).all():
            raise ValueError(f"reflectance dataset {name!r} contains non-finite values")
        if np.any(values < 0.0):
            raise ValueError(f"reflectance dataset {name!r} contains negative values")
        reflectance_blocks.append(values)
        source_labels = _source_labels(name, aligned.labels)
        labels.extend(source_labels)
        sources.extend([name] * len(aligned.labels))
        sample_counts[name] = len(aligned.labels)

    reflectances = np.vstack(reflectance_blocks)
    metadata = {
        "datasets": names,
        "source_preset": "all_uef" if datasets == "all_uef" else None,
        "sample_counts": sample_counts,
        "sample_count": int(reflectances.shape[0]),
        "wavelength_count": int(reflectances.shape[1]),
        "shape": concrete_shape,
    }
    return ReflectanceLibrary(
        wavelengths=concrete_shape.wavelengths,
        reflectances=reflectances,
        labels=tuple(labels),
        sources=tuple(sources),
        shape=concrete_shape,
        metadata=metadata,
    )


__all__ = [
    "DEFAULT_REFLECTANCE_LIBRARY_DATASETS",
    "DEFAULT_REFLECTANCE_LIBRARY_SHAPE",
    "ReflectanceLibrary",
    "load_reflectance_library",
]
