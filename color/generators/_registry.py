"""Registry for formula-generated color science data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Hashable, List, Optional, Tuple

import numpy as np

from color.utils.names import canonicalize_resource_name as canonicalize_name


GeneratedDict = Dict[str, np.ndarray]
"""Standard generated-data return type."""


@dataclass(frozen=True)
class GeneratorEntry:
    """Immutable descriptor for one data generator."""

    category: str
    name: str
    description: str
    generate_fn: Callable[..., GeneratedDict]
    parameters: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)


_REGISTRY: Dict[Tuple[str, str], GeneratorEntry] = {}
_CANONICAL_CATEGORY_INDEX: Dict[str, str] = {}
_CANONICAL_INDEX: Dict[Tuple[str, str], Tuple[str, str]] = {}
_CACHE: Dict[Tuple[Any, ...], GeneratedDict] = {}


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

    return key


def _resolve_category(category: str) -> Optional[str]:
    """Resolve exact or canonical category name to a registered category."""
    if category in _CANONICAL_CATEGORY_INDEX.values():
        return category

    return _CANONICAL_CATEGORY_INDEX.get(canonicalize_name(category))


def register(entry: GeneratorEntry) -> None:
    """Add a generator to the global registry."""
    key = (entry.category, entry.name)
    canonical_category = canonicalize_name(entry.category)
    existing_category = _CANONICAL_CATEGORY_INDEX.get(canonical_category)
    if existing_category is not None and existing_category != entry.category:
        raise ValueError(
            f"Canonical generator category collision for {entry.category!r}: "
            f"already used by {existing_category!r}"
        )

    canonical_key = _canonical_key(entry.category, entry.name)
    existing_key = _CANONICAL_INDEX.get(canonical_key)
    if existing_key is not None and existing_key != key:
        raise ValueError(
            f"Canonical generator name collision for {entry.category!r}/{entry.name!r}: "
            f"already used by {existing_key[0]!r}/{existing_key[1]!r}"
        )

    _REGISTRY[key] = entry
    _CANONICAL_CATEGORY_INDEX[canonical_category] = entry.category
    _CANONICAL_INDEX[canonical_key] = key


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
    """Build a cache key from generator identity and call parameters."""
    return (
        category,
        name,
        *(
            (k, _make_hashable(v))
            for k, v in sorted(kwargs.items(), key=lambda item: item[0])
        ),
    )


def _readonly_copy(data: GeneratedDict) -> GeneratedDict:
    """Return a read-only copy so callers cannot mutate cached arrays."""
    result: GeneratedDict = {}
    for key, value in data.items():
        arr = np.array(value, copy=True)
        arr.setflags(write=False)
        result[key] = arr
    return result


def generate(category: str, name: str, **kwargs: Any) -> GeneratedDict:
    """Generate data by category/name and cache the result."""
    if not isinstance(category, str):
        raise AssertionError(f"category must be str, got {type(category)}")
    if not isinstance(name, str):
        raise AssertionError(f"name must be str, got {type(name)}")

    key = _resolve_key(category, name)
    entry = _REGISTRY.get(key)
    if entry is None:
        resolved_category = _resolve_category(category) or category
        available = [n for c, n in _REGISTRY if c == resolved_category]
        raise KeyError(
            f"No generator {name!r} in category {category!r}. "
            f"Available: {available}"
        )

    category, name = key
    cache_key = _make_cache_key(category, name, kwargs)
    if cache_key not in _CACHE:
        _CACHE[cache_key] = entry.generate_fn(**kwargs)
    return _readonly_copy(_CACHE[cache_key])


def describe(category: str, name: str) -> GeneratorEntry:
    """Return the metadata entry for a generator."""
    key = _resolve_key(category, name)
    entry = _REGISTRY.get(key)
    if entry is None:
        raise KeyError(f"No generator {name!r} in category {category!r}")
    return entry


def list_generators(category: Optional[str] = None) -> List[str]:
    """List registered generator names, optionally filtered by category."""
    if category is not None:
        resolved_category = _resolve_category(category)
        if resolved_category is None:
            return []
        return sorted(n for c, n in _REGISTRY if c == resolved_category)
    return sorted({n for _, n in _REGISTRY})


def list_categories() -> List[str]:
    """Return all registered generator category names."""
    return sorted({c for c, _ in _REGISTRY})


def clear_cache(category: Optional[str] = None, name: Optional[str] = None) -> int:
    """Clear cached generated data and return the number of entries removed."""
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
