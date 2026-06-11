"""Conversion helpers for spectral objects."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from .distribution import SpectralDistribution
from .multi_distribution import MultiSpectralDistribution


SpectralData = Mapping[str, np.ndarray]


def _display_interval(interval_nm: float) -> str:
    """Return a compact interval label for object names."""
    interval = float(interval_nm)
    if interval.is_integer():
        return str(int(interval))
    return str(interval)


def _standard_observer_metadata(
    category: str,
    stem: str,
    *,
    standard: str,
    observer_degree: int,
    interval_nm: float,
    energy: str | None = None,
) -> dict[str, Any]:
    """Build spectral object metadata from the registered dataset entry."""
    from color.datasets import describe

    entry = describe(f"standard_observers.{category}", stem)
    metadata = dict(entry.metadata)
    metadata.setdefault("dataset_category", entry.category)
    metadata.setdefault("dataset_name", entry.name)
    metadata["standard"] = standard
    metadata["observer_degree"] = observer_degree
    metadata["interval_nm"] = float(interval_nm)
    if energy is not None:
        metadata["energy"] = energy
    return metadata


def _dataset_metadata(category: str, name: str) -> dict[str, Any]:
    """Build spectral object metadata from a registered dataset entry."""
    from color.datasets import describe

    entry = describe(category, name)
    metadata = dict(entry.metadata)
    metadata.setdefault("dataset_category", entry.category)
    metadata.setdefault("dataset_name", entry.name)
    return metadata


def from_columns(
    raw: SpectralData,
    *,
    x: str = "wavelength",
    y: str | None = None,
    ys: Sequence[str] | None = None,
    name: str = "",
    metadata: Mapping[str, Any] | None = None,
    fill_nan: float | None = None,
) -> SpectralDistribution | MultiSpectralDistribution:
    """Build a spectral object from a raw column mapping.

    Parameters
    ----------
    raw
        Mapping from column names to arrays, typically returned by
        ``color.datasets`` or ``color.generators``.
    x
        Wavelength column name.
    y, ys
        Single value column or multiple channel columns. Provide exactly one.
    name, metadata
        Optional object name and metadata.
    fill_nan
        Optional replacement value for non-finite samples.

    Returns
    -------
    SpectralDistribution or MultiSpectralDistribution
        Single-channel object when ``y`` is supplied; multi-channel object when
        ``ys`` is supplied.

    Notes
    -----
    This is the main boundary from raw dictionaries into the spectra object
    layer. It does not read files and does not perform colorimetric
    integration.
    """
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
            fill_nan=fill_nan,
        )
    if ys is None:
        raise ValueError("provide y or ys")
    return MultiSpectralDistribution.from_columns(
        raw,
        x=x,
        ys=ys,
        name=name,
        metadata=metadata,
        fill_nan=fill_nan,
    )


def from_dataset(
    category: str,
    name: str,
    *,
    fill_nan: float | None = None,
    **kwargs: Any,
) -> SpectralDistribution | MultiSpectralDistribution:
    """Build a spectral object from a registered static dataset.

    Parameters
    ----------
    category, name
        Dataset registry category and name.
    fill_nan
        Optional replacement value for non-finite samples.
    **kwargs
        Passed through to ``color.datasets.get``.

    Returns
    -------
    SpectralDistribution or MultiSpectralDistribution
        Object type inferred from the number of non-wavelength columns.

    Notes
    -----
    ``color.datasets.get`` itself still returns a raw ``dict``. This function
    only loads and wraps that data into immutable spectra objects.
    """
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
            fill_nan=fill_nan,
        )

    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=labels,
        name=object_name,
        metadata=metadata,
        fill_nan=fill_nan,
    )


def from_D65_illuminant() -> SpectralDistribution:
    """Return CIE standard illuminant D65 as a spectral distribution.

    Returns
    -------
    SpectralDistribution
        Single-channel spectral object with wavelength samples and ``spd``
        values from the registered D65 illuminant dataset.

    Notes
    -----
    This is a convenience wrapper around ``color.datasets``. It preserves the
    dataset values and metadata; it does not normalise the illuminant for
    tristimulus integration.

    Examples
    --------
    >>> d65 = from_D65_illuminant()
    >>> d65.keys()
    ('wavelength', 'value')
    """
    from color.datasets.illuminants import get_D65_illuminant

    raw = get_D65_illuminant()
    metadata = _dataset_metadata("illuminants", "D65")
    metadata["standard"] = "CIE Standard Illuminant D65"
    return SpectralDistribution.from_columns(
        raw,
        x="wavelength",
        y="spd",
        name="CIE Standard Illuminant D65",
        metadata=metadata,
    )


def from_cie1931_xyz_cmfs(interval_nm: float = 1) -> MultiSpectralDistribution:
    """Return CIE 1931 2-degree XYZ CMFs as a multispectral object.

    Parameters
    ----------
    interval_nm
        Source sampling interval in nanometres.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("X", "Y", "Z")``.

    Notes
    -----
    ``interval_nm`` selects an existing source file sampling interval. It does
    not resample; use ``reshape`` or ``align`` on the returned object for new
    wavelength grids.
    """
    from color.datasets.standard_observers import (
        _cie1931_xyz_cmfs_stem,
        get_cie1931_xyz_cmfs,
    )

    stem = _cie1931_xyz_cmfs_stem(interval_nm)
    raw = get_cie1931_xyz_cmfs(interval_nm=interval_nm)
    interval = _display_interval(interval_nm)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("X", "Y", "Z"),
        name=f"CIE 1931 XYZ CMFs {interval} nm",
        metadata=_standard_observer_metadata(
            "cmfs",
            stem,
            standard="CIE 1931 XYZ CMFs",
            observer_degree=2,
            interval_nm=interval_nm,
        ),
    )


def from_cie1964_xyz_cmfs(interval_nm: float = 1) -> MultiSpectralDistribution:
    """Return CIE 1964 10-degree XYZ CMFs as a multispectral object.

    Parameters
    ----------
    interval_nm
        Source sampling interval in nanometres.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("X", "Y", "Z")``.

    Notes
    -----
    ``interval_nm`` selects an existing source file sampling interval.
    """
    from color.datasets.standard_observers import (
        _cie1964_xyz_cmfs_stem,
        get_cie1964_xyz_cmfs,
    )

    stem = _cie1964_xyz_cmfs_stem(interval_nm)
    raw = get_cie1964_xyz_cmfs(interval_nm=interval_nm)
    interval = _display_interval(interval_nm)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("X", "Y", "Z"),
        name=f"CIE 1964 XYZ CMFs {interval} nm",
        metadata=_standard_observer_metadata(
            "cmfs",
            stem,
            standard="CIE 1964 XYZ CMFs",
            observer_degree=10,
            interval_nm=interval_nm,
        ),
    )


def from_cie2012_xyz_2degree_cmfs(
    interval_nm: float = 1,
) -> MultiSpectralDistribution:
    """Return CIE 2012 2-degree XYZ CMFs as a multispectral object.

    Parameters
    ----------
    interval_nm
        Source sampling interval in nanometres.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("X", "Y", "Z")``.

    Notes
    -----
    ``interval_nm`` selects an existing source file sampling interval.
    """
    from color.datasets.standard_observers import (
        _cie2012_xyz_cmfs_stem,
        get_cie2012_xyz_2degree_cmfs,
    )

    stem = _cie2012_xyz_cmfs_stem(2, interval_nm)
    raw = get_cie2012_xyz_2degree_cmfs(interval_nm=interval_nm)
    interval = _display_interval(interval_nm)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("X", "Y", "Z"),
        name=f"CIE 2012 2-degree XYZ CMFs {interval} nm",
        metadata=_standard_observer_metadata(
            "cmfs",
            stem,
            standard="CIE 2012 XYZ CMFs",
            observer_degree=2,
            interval_nm=interval_nm,
        ),
    )


def from_cie2012_xyz_10degree_cmfs(
    interval_nm: float = 1,
) -> MultiSpectralDistribution:
    """Return CIE 2012 10-degree XYZ CMFs as a multispectral object.

    Parameters
    ----------
    interval_nm
        Source sampling interval in nanometres.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("X", "Y", "Z")``.

    Notes
    -----
    ``interval_nm`` selects an existing source file sampling interval.
    """
    from color.datasets.standard_observers import (
        _cie2012_xyz_cmfs_stem,
        get_cie2012_xyz_10degree_cmfs,
    )

    stem = _cie2012_xyz_cmfs_stem(10, interval_nm)
    raw = get_cie2012_xyz_10degree_cmfs(interval_nm=interval_nm)
    interval = _display_interval(interval_nm)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("X", "Y", "Z"),
        name=f"CIE 2012 10-degree XYZ CMFs {interval} nm",
        metadata=_standard_observer_metadata(
            "cmfs",
            stem,
            standard="CIE 2012 XYZ CMFs",
            observer_degree=10,
            interval_nm=interval_nm,
        ),
    )


def from_cie2006_lms_2degree_fundamentals(
    interval_nm: float = 1,
    energy: str = "linE",
    fill_nan: float | None = 0.0,
) -> MultiSpectralDistribution:
    """Return CIE 2006 2-degree LMS fundamentals as a multispectral object.

    Parameters
    ----------
    interval_nm
        Source sampling interval in nanometres.
    energy
        Dataset energy form, e.g. ``"linE"``, ``"logE"`` or ``"logQ"``.
    fill_nan
        Replacement value for non-finite table entries.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("l", "m", "s")``.

    Notes
    -----
    Defaults use ``energy="linE"`` and ``fill_nan=0.0`` so blank long-wave
    S-cone table values behave as zero response during integration.
    """
    from color.datasets.standard_observers import (
        _cie2006_lms_fundamentals_stem,
        _energy_token,
        get_cie2006_lms_2degree_fundamentals,
    )

    energy_token = _energy_token(energy)
    stem = _cie2006_lms_fundamentals_stem(2, interval_nm, energy_token)
    raw = get_cie2006_lms_2degree_fundamentals(
        interval_nm=interval_nm,
        energy=energy_token,
    )
    interval = _display_interval(interval_nm)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("l", "m", "s"),
        name=f"CIE 2006 2-degree LMS fundamentals {energy_token} {interval} nm",
        metadata=_standard_observer_metadata(
            "cone_fundamentals",
            stem,
            standard="CIE 2006 LMS fundamentals",
            observer_degree=2,
            interval_nm=interval_nm,
            energy=energy_token,
        ),
        fill_nan=fill_nan,
    )


def from_cie2006_lms_10degree_fundamentals(
    interval_nm: float = 1,
    energy: str = "linE",
    fill_nan: float | None = 0.0,
) -> MultiSpectralDistribution:
    """Return CIE 2006 10-degree LMS fundamentals as a multispectral object.

    Parameters
    ----------
    interval_nm
        Source sampling interval in nanometres.
    energy
        Dataset energy form, e.g. ``"linE"``, ``"logE"`` or ``"logQ"``.
    fill_nan
        Replacement value for non-finite table entries.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("l", "m", "s")``.

    Notes
    -----
    Defaults use ``energy="linE"`` and ``fill_nan=0.0``.
    """
    from color.datasets.standard_observers import (
        _cie2006_lms_fundamentals_stem,
        _energy_token,
        get_cie2006_lms_10degree_fundamentals,
    )

    energy_token = _energy_token(energy)
    stem = _cie2006_lms_fundamentals_stem(10, interval_nm, energy_token)
    raw = get_cie2006_lms_10degree_fundamentals(
        interval_nm=interval_nm,
        energy=energy_token,
    )
    interval = _display_interval(interval_nm)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("l", "m", "s"),
        name=f"CIE 2006 10-degree LMS fundamentals {energy_token} {interval} nm",
        metadata=_standard_observer_metadata(
            "cone_fundamentals",
            stem,
            standard="CIE 2006 LMS fundamentals",
            observer_degree=10,
            interval_nm=interval_nm,
            energy=energy_token,
        ),
        fill_nan=fill_nan,
    )


def _from_individual_cone_generator(
    generator_name: str,
    display_name: str,
    kwargs: dict[str, Any],
) -> MultiSpectralDistribution:
    """Wrap a registered individual LMS generator as a multispectral object."""
    from color.generators import describe, generate_individual_cone_fundamental

    raw = generate_individual_cone_fundamental(generator_name, **kwargs)
    entry = describe("individual_cone_fundamentals", generator_name)
    metadata = dict(entry.metadata)
    metadata.setdefault("generator_category", entry.category)
    metadata.setdefault("generator_name", entry.name)
    metadata["parameters"] = dict(kwargs)
    return MultiSpectralDistribution.from_columns(
        raw,
        x="wavelength",
        ys=("l", "m", "s"),
        name=display_name,
        metadata=metadata,
    )


def from_stockman_rider_2023_individual_cone_fundamentals(
    **kwargs: Any,
) -> MultiSpectralDistribution:
    """Return Stockman/Rider 2023 individual LMS fundamentals.

    Parameters
    ----------
    **kwargs
        Passed to the registered Stockman/Rider individual cone generator.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("l", "m", "s")``.

    Notes
    -----
    This wraps the registered generator output as a
    ``MultiSpectralDistribution`` with labels ``("l", "m", "s")``.
    """
    return _from_individual_cone_generator(
        "stockman_rider_2023",
        "Stockman/Rider 2023 individual LMS fundamentals",
        dict(kwargs),
    )


def from_asano2016_individual_cone_fundamentals(
    **kwargs: Any,
) -> MultiSpectralDistribution:
    """Return Asano et al. 2016 individual LMS fundamentals.

    Parameters
    ----------
    **kwargs
        Passed to the registered Asano 2016 individual observer generator.

    Returns
    -------
    MultiSpectralDistribution
        Object with labels ``("l", "m", "s")``.

    Notes
    -----
    This wraps the registered generator output as a
    ``MultiSpectralDistribution`` with labels ``("l", "m", "s")``.
    """
    return _from_individual_cone_generator(
        "asano2016",
        "Asano et al. 2016 individual LMS fundamentals",
        dict(kwargs),
    )
