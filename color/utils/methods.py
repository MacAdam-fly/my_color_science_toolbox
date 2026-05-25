"""Shared helpers for method registries and dispatch."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from typing import Any

from .names import canonical_method_name


def build_method_index(method_aliases: Mapping[str, tuple[str, ...]]) -> dict[str, str]:
    """Return a canonical lookup index for method names and aliases."""
    method_index: dict[str, str] = {}
    for name, aliases in method_aliases.items():
        for alias in (name, *aliases):
            method_index[canonical_method_name(alias)] = name
    return method_index


def resolve_method(
    method: str,
    method_index: Mapping[str, str],
    methods: Mapping[str, Callable[..., Any]],
) -> tuple[str, Callable[..., Any]]:
    """Resolve *method* to a canonical name and function."""
    key = canonical_method_name(method)
    if key not in method_index:
        available = ", ".join(methods)
        raise ValueError(f"unknown method {method!r}. Available: {available}")

    canonical_name = method_index[key]
    return canonical_name, methods[canonical_name]


def filter_kwargs(function: Callable[..., Any], kwargs: Mapping[str, Any]) -> dict[str, Any]:
    """Return keyword arguments accepted by *function*."""
    signature = inspect.signature(function)
    return {key: value for key, value in kwargs.items() if key in signature.parameters}


__all__ = [
    "canonical_method_name",
    "build_method_index",
    "resolve_method",
    "filter_kwargs",
]
