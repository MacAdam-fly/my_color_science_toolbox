"""Central registry for all color science datasets.

Provides lazy-loading, caching, and unified access to file-based and
computed datasets across all categories (illuminants, observers, etc.).

New data files placed in the ``data/`` tree are discovered automatically
via each category module's ``_register_*()`` function.  Computed datasets
(e.g. blackbody radiation, CIE D-series) are registered with a callable
that generates data on demand.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, List, Optional, Tuple

import numpy as np

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

SpectralDict = Dict[str, np.ndarray]
"""Standard return type: ``{'wavelength': array, ...}``."""


@dataclass(frozen=True)
class DatasetEntry:
    """Immutable descriptor for one dataset."""

    category: str
    """Top-level group: ``'illuminants'``, ``'standard_observers'``, etc."""
    name: str
    """Unique identifier within the category (usually the file stem)."""
    description: str
    """Short human-readable description."""
    source: str = ""
    """Origin of the data (paper, URL, etc.)."""
    file_path: Optional[str] = None
    """Absolute path to the backing file.  ``None`` for computed datasets."""
    computed: bool = False
    """``True`` if the data is generated or parsed by ``compute_fn``."""
    compute_fn: Optional[Callable[..., SpectralDict]] = None
    """Factory/parser that produces the dataset.  Required when *computed* is ``True``."""
    columns: Optional[Tuple[str, ...]] = None
    """Column names for the dataset.  Always takes highest priority, even over file headers."""
    read_options: Dict[str, Any] = field(default_factory=dict)
    """Options that control generic file reading: ``header``, ``sheet``, etc."""
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Descriptive metadata that does not affect loading behavior."""


# ---------------------------------------------------------------------------
# Global store
# ---------------------------------------------------------------------------

_REGISTRY: Dict[Tuple[str, str], DatasetEntry] = {}
_CACHE: Dict[Tuple[Any, ...], SpectralDict] = {}
_READ_OPTION_KEYS = frozenset({
    "header",
    "skiprows",
    "usecols",
    "sheet",
    "coerce_numeric",
})


# ---------------------------------------------------------------------------
# Registration helpers
# ---------------------------------------------------------------------------

def register(entry: DatasetEntry) -> None:
    """Add a dataset to the global registry.  Overwrites if already present."""
    unknown_options = set(entry.read_options) - _READ_OPTION_KEYS
    if unknown_options:
        valid = ", ".join(sorted(_READ_OPTION_KEYS))
        unknown = ", ".join(sorted(unknown_options))
        raise ValueError(
            f"Unknown read_options for dataset {entry.category!r}/{entry.name!r}: "
            f"{unknown}. Valid keys: {valid}"
        )
    _REGISTRY[(entry.category, entry.name)] = entry


def register_computed(
    category: str,
    name: str,
    compute_fn: Callable[..., SpectralDict],
    description: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """Shorthand for registering a computed (formula-generated) dataset."""
    register(DatasetEntry(
        category=category,
        name=name,
        description=description,
        computed=True,
        compute_fn=compute_fn,
        metadata=metadata or {},
    ))


# ---------------------------------------------------------------------------
# Cache helpers
# ---------------------------------------------------------------------------

def _make_hashable(value: Any) -> Hashable:
    """Convert common mutable values into stable cache-key fragments."""
    if isinstance(value, np.ndarray):
        return ("ndarray", value.dtype.str, value.shape, value.tobytes())
    if isinstance(value, dict):
        return (
            "dict",
            tuple(
                (k, _make_hashable(v))
                for k, v in sorted(value.items(), key=lambda item: repr(item[0]))
            ),
        )
    if isinstance(value, (list, tuple)):
        return (type(value).__name__, tuple(_make_hashable(v) for v in value))
    if isinstance(value, set):
        return ("set", tuple(sorted((_make_hashable(v) for v in value), key=repr)))
    try:
        hash(value)
    except TypeError:
        return (type(value).__name__, repr(value))
    return value


def _make_cache_key(category: str, name: str, kwargs: Dict[str, Any]) -> Tuple[Any, ...]:
    """Build a cache key from dataset identity and call parameters."""
    return (
        category,
        name,
        *(
            (k, _make_hashable(v))
            for k, v in sorted(kwargs.items(), key=lambda item: item[0])
        ),
    )


def _readonly_copy(data: SpectralDict) -> SpectralDict:
    """Return a read-only copy so callers cannot mutate cached arrays."""
    result: SpectralDict = {}
    for key, value in data.items():
        arr = np.array(value, copy=True)
        arr.setflags(write=False)
        result[key] = arr
    return result


# ---------------------------------------------------------------------------
# Lookup
# ---------------------------------------------------------------------------

def get(category: str, name: str, **kwargs: Any) -> SpectralDict:
    """Return dataset contents (lazy-loaded and cached).

    Results are cached after first read and returned as read-only copies.
    File-based datasets are cached per call-parameter set (e.g. sheet name).
    For computed datasets the *kwargs* are forwarded to the compute function
    and the result is cached under ``(category, name, *sorted(kwargs))``.
    """
    from ._utils import attest

    attest(isinstance(category, str), f"category must be str, got {type(category)}")
    attest(isinstance(name, str), f"name must be str, got {type(name)}")

    key = (category, name)
    entry = _REGISTRY.get(key)
    if entry is None:
        available = [n for c, n in _REGISTRY if c == category]
        raise KeyError(
            f"No dataset {name!r} in category {category!r}. "
            f"Available: {available}"
        )

    cache_key = _make_cache_key(category, name, kwargs)

    if entry.computed:
        if cache_key not in _CACHE:
            if entry.compute_fn is None:
                raise RuntimeError(f"Computed dataset {name!r} has no compute_fn")
            _CACHE[cache_key] = entry.compute_fn(**kwargs)
        return _readonly_copy(_CACHE[cache_key])

    if cache_key not in _CACHE:
        _CACHE[cache_key] = _read_file(entry, **kwargs)
    return _readonly_copy(_CACHE[cache_key])


def list_datasets(category: Optional[str] = None) -> List[str]:
    """List registered dataset names, optionally filtered by category."""
    if category is not None:
        return sorted(n for c, n in _REGISTRY if c == category)
    return sorted({n for _, n in _REGISTRY})


def list_categories() -> List[str]:
    """Return all registered category names."""
    return sorted({c for c, _ in _REGISTRY})


def clear_cache(category: Optional[str] = None, name: Optional[str] = None) -> int:
    """Clear cached dataset contents and return the number of entries removed.

    Parameters
    ----------
    category : str, optional
        If given, clear only cache entries in this category.
    name : str, optional
        If given with *category*, clear only cache entries for that dataset
        name.  Passing *name* without *category* is ambiguous and raises
        ``ValueError``.
    """
    if name is not None and category is None:
        raise ValueError("name can only be used together with category")

    keys_to_remove = []
    for key in _CACHE:
        key_category = key[0]
        key_name = key[1]
        if category is not None and key_category != category:
            continue
        if name is not None and key_name != name:
            continue
        keys_to_remove.append(key)

    for key in keys_to_remove:
        del _CACHE[key]

    return len(keys_to_remove)


def describe(category: str, name: str) -> DatasetEntry:
    """Return the metadata entry for a dataset without loading it."""
    key = (category, name)
    entry = _REGISTRY.get(key)
    if entry is None:
        raise KeyError(f"No dataset {name!r} in category {category!r}")
    return entry


def search(keyword: str) -> List[DatasetEntry]:
    """Search registered datasets by keyword in name or description."""
    kw = keyword.lower()
    return [
        e for e in _REGISTRY.values()
        if kw in e.name.lower() or kw in e.description.lower()
    ]


# ---------------------------------------------------------------------------
# Internal file reader
# ---------------------------------------------------------------------------

def _fix_generic_columns(data: SpectralDict, entry: DatasetEntry) -> SpectralDict:
    """Replace auto-generated generic column names with filename-pattern inference.

    Only applies to standard_observers entries where no explicit ``columns``
    was set and the file had no detectable header.
    """
    cols = list(data.keys())
    needs_fix = any(
        isinstance(c, (int, np.integer)) or (isinstance(c, float) and np.isnan(c))
        or (isinstance(c, str) and c.startswith("col"))
        or (isinstance(c, str) and c == "value" and cols[0] == "wavelength")
        for c in cols
    )
    if not needs_fix or not entry.category.startswith("standard_observers."):
        return data
    from .standard_observers import _infer_col_names
    new_names = _infer_col_names(entry.name, len(cols))
    return {str(new_names[i]): data[old] for i, old in enumerate(cols)}


def _read_file(entry: DatasetEntry, **kwargs: Any) -> SpectralDict:
    """Dispatch to the correct reader based on file extension."""
    from ._utils import read_csv, read_xlsx, read_xls

    if entry.file_path is None:
        raise RuntimeError(f"Dataset {entry.name!r} has no file_path")

    path = entry.file_path
    options = entry.read_options
    ext = path.rsplit(".", 1)[-1].lower()
    names = entry.columns if entry.columns is not None else options.get("names")

    if ext == "csv":
        data = read_csv(
            path,
            usecols=options.get("usecols"),
            names=names,
            header=options.get("header", False),
            skiprows=options.get("skiprows", 0),
            coerce_numeric=options.get("coerce_numeric", False),
        )
    elif ext == "xlsx":
        data = read_xlsx(
            path,
            sheet=kwargs.get("sheet", options.get("sheet", 0)),
            usecols=options.get("usecols"),
            names=names,
            header=options.get("header", False),
            skiprows=options.get("skiprows", 0),
            coerce_numeric=options.get("coerce_numeric", False),
        )
    elif ext == "xls":
        data = read_xls(
            path,
            sheet=kwargs.get("sheet", options.get("sheet", 0)),
            usecols=options.get("usecols"),
            names=names,
            header=options.get("header", False),
            skiprows=options.get("skiprows", 0),
            coerce_numeric=options.get("coerce_numeric", False),
        )
    else:
        raise ValueError(f"Unsupported file format: .{ext}")

    return _fix_generic_columns(data, entry)
