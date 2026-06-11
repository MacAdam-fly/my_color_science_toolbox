"""Central registry for static color science datasets.

Provides lazy-loading, caching, and unified access to static file-backed
datasets across all categories (illuminants, observers, etc.).

New data files placed in the ``data/`` tree are discovered automatically
via each category module's ``_register_*()`` function.  Special static files
that cannot use the generic CSV/XLS/XLSX readers can provide ``parser_fn``.
Formula-generated data belongs in :mod:`color.generators`, not here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, List, Optional, Tuple

import numpy as np

from color.utils.names import canonicalize_resource_name as canonicalize_name

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

SpectralDict = Dict[str, np.ndarray]
"""Standard return type: ``{'wavelength': array, ...}``."""


@dataclass(frozen=True)
class DatasetEntry:
    """Immutable descriptor for one registered static dataset.

    Parameters
    ----------
    category, name
        Registry category and category-local dataset name. Both are resolved
        with resource-name canonicalisation.
    description, source
        Human-readable description and provenance.
    file_path
        Backing static CSV/XLS/XLSX file path.
    parser_fn
        Optional parser for special static file formats. It receives
        ``file_path`` as its first argument.
    columns
        Explicit column names. These take priority over file headers.
    read_options
        Generic reader options such as ``header``, ``skiprows``, ``usecols``,
        ``sheet`` and ``coerce_numeric``.
    metadata
        Descriptive metadata. It does not affect loading behavior.

    Notes
    -----
    ``DatasetEntry`` describes static data only. Formula-generated data should
    be implemented in ``color.generators`` instead of being hidden in
    ``parser_fn`` or ``metadata``.
    """

    category: str
    """Top-level group: ``'illuminants'``, ``'standard_observers'``, etc."""
    name: str
    """Unique identifier within the category (usually the file stem)."""
    description: str
    """Short human-readable description."""
    source: str = ""
    """Origin of the data (paper, URL, etc.)."""
    file_path: Optional[str] = None
    """Absolute path to the backing static file."""
    parser_fn: Optional[Callable[..., SpectralDict]] = None
    """Custom parser for special static files; receives ``file_path`` first."""
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
_CANONICAL_CATEGORY_INDEX: Dict[str, str] = {}
_CANONICAL_INDEX: Dict[Tuple[str, str], Tuple[str, str]] = {}
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

def _canonical_key(category: str, name: str) -> Tuple[str, str]:
    """Return the canonical registry key for *category* and *name*."""
    return canonicalize_name(category), canonicalize_name(name)


def _resolve_key(category: str, name: str) -> Tuple[str, str]:
    """Resolve exact or canonical category/name pair to a registered key."""
    key = (category, name)
    if key in _REGISTRY:
        return key

    canonical_key = _canonical_key(category, name)
    resolved = _CANONICAL_INDEX.get(canonical_key)
    if resolved is not None:
        return resolved

    resolved_category = _resolve_category(category)
    if resolved_category is not None and resolved_category != category:
        key = (resolved_category, name)
        if key in _REGISTRY:
            return key

        canonical_key = _canonical_key(resolved_category, name)
        resolved = _CANONICAL_INDEX.get(canonical_key)
        if resolved is not None:
            return resolved

    return key


def _resolve_category(category: str) -> Optional[str]:
    """Resolve exact or canonical category name to a registered category."""
    if category in _CANONICAL_CATEGORY_INDEX.values():
        return category

    return _CANONICAL_CATEGORY_INDEX.get(canonicalize_name(category))


def register(entry: DatasetEntry) -> None:
    """Register a static dataset entry.

    Parameters
    ----------
    entry
        Dataset descriptor to add to the global registry.

    Returns
    -------
    None

    Notes
    -----
    Registration checks canonical category/name collisions. ``read_options``
    is validated against the supported generic reader keys; descriptive
    metadata must stay in ``metadata`` and cannot control file reading.
    """
    unknown_options = set(entry.read_options) - _READ_OPTION_KEYS
    if unknown_options:
        valid = ", ".join(sorted(_READ_OPTION_KEYS))
        unknown = ", ".join(sorted(unknown_options))
        raise ValueError(
            f"Unknown read_options for dataset {entry.category!r}/{entry.name!r}: "
            f"{unknown}. Valid keys: {valid}"
        )
    key = (entry.category, entry.name)
    canonical_category = canonicalize_name(entry.category)
    existing_category = _CANONICAL_CATEGORY_INDEX.get(canonical_category)
    if existing_category is not None and existing_category != entry.category:
        raise ValueError(
            f"Canonical category name collision for {entry.category!r}: "
            f"already used by {existing_category!r}"
        )

    canonical_key = _canonical_key(entry.category, entry.name)
    existing_key = _CANONICAL_INDEX.get(canonical_key)
    if existing_key is not None and existing_key != key:
        raise ValueError(
            f"Canonical dataset name collision for {entry.category!r}/{entry.name!r}: "
            f"already used by {existing_key[0]!r}/{existing_key[1]!r}"
        )

    _REGISTRY[key] = entry
    _CANONICAL_CATEGORY_INDEX[canonical_category] = entry.category
    _CANONICAL_INDEX[canonical_key] = key


def register_category_alias(alias: str, category: str) -> None:
    """Register *alias* as an alternate spelling for an existing category."""
    resolved_category = _resolve_category(category) or category
    canonical_alias = canonicalize_name(alias)
    existing_category = _CANONICAL_CATEGORY_INDEX.get(canonical_alias)
    if existing_category is not None and existing_category != resolved_category:
        raise ValueError(
            f"Canonical category alias collision for {alias!r}: "
            f"already used by {existing_category!r}"
        )
    _CANONICAL_CATEGORY_INDEX[canonical_alias] = resolved_category


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
    """Load a registered static dataset as raw read-only arrays.

    Parameters
    ----------
    category, name
        Registered category and dataset name. Resource-name canonicalisation
        makes minor spelling differences, separators and ``0.1``/``0p1``
        resource tokens resolvable.
    **kwargs
        Extra parameters forwarded to a custom ``parser_fn`` or generic Excel
        reader, for example ``sheet=...``.

    Returns
    -------
    dict[str, ndarray]
        Raw column mapping. Arrays are read-only copies; copy an array before
        editing it.

    Notes
    -----
    Results are lazy-loaded, cached after first read, and cached per
    call-parameter set. This function does not wrap data as
    ``SpectralDistribution`` objects; use ``color.spectra`` for object
    wrappers, interpolation and arithmetic.

    Examples
    --------
    >>> d65 = get("illuminants", "D65")
    >>> "wavelength" in d65
    True
    """
    from ._utils import attest

    attest(isinstance(category, str), f"category must be str, got {type(category)}")
    attest(isinstance(name, str), f"name must be str, got {type(name)}")

    key = _resolve_key(category, name)
    entry = _REGISTRY.get(key)
    if entry is None:
        resolved_category = _resolve_category(category) or category
        available = [n for c, n in _REGISTRY if c == resolved_category]
        raise KeyError(
            f"No dataset {name!r} in category {category!r}. "
            f"Available: {available}"
        )

    category, name = key
    cache_key = _make_cache_key(category, name, kwargs)

    if cache_key not in _CACHE:
        if entry.parser_fn is not None:
            if entry.file_path is None:
                raise RuntimeError(f"Dataset {name!r} has parser_fn but no file_path")
            _CACHE[cache_key] = entry.parser_fn(entry.file_path, **kwargs)
        else:
            _CACHE[cache_key] = _read_file(entry, **kwargs)
    return _readonly_copy(_CACHE[cache_key])


def list_datasets(category: Optional[str] = None) -> List[str]:
    """List registered dataset names.

    Parameters
    ----------
    category
        Optional category filter. Category aliases are accepted.

    Returns
    -------
    list[str]
        Sorted dataset names. When ``category`` is unknown an empty list is
        returned.
    """
    if category is not None:
        resolved_category = _resolve_category(category)
        if resolved_category is None:
            return []
        return sorted(n for c, n in _REGISTRY if c == resolved_category)
    return sorted({n for _, n in _REGISTRY})


def list_categories() -> List[str]:
    """Return all registered dataset category names."""
    return sorted({c for c, _ in _REGISTRY})


def clear_cache(category: Optional[str] = None, name: Optional[str] = None) -> int:
    """Clear cached dataset contents and return the number of entries removed.

    Parameters
    ----------
    category
        If given, clear only cache entries in this category.
    name
        If given with *category*, clear only cache entries for that dataset
        name.  Passing *name* without *category* is ambiguous and raises
        ``ValueError``.

    Returns
    -------
    int
        Number of cached call-parameter entries removed.

    Notes
    -----
    Clearing cache does not unregister datasets. It only forces the next
    ``get(...)`` call to re-read the backing file or parser output.
    """
    if name is not None and category is None:
        raise ValueError("name can only be used together with category")

    if category is not None and name is not None:
        category, name = _resolve_key(category, name)
    elif category is not None:
        category = _resolve_category(category) or category

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
    """Return a dataset entry without loading the backing data."""
    key = _resolve_key(category, name)
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
