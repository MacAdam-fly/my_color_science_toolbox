"""Shared helpers for name canonicalisation."""

from __future__ import annotations

import re


def canonicalize_name(value: str) -> str:
    """Return a delimiter-insensitive ASCII lookup key.

    This base rule casefolds and keeps only ASCII letters and digits. It is
    suitable for methods and simple option names, but not for data resource
    names where decimal sampling intervals carry meaning.
    """
    key = value.strip().casefold()
    return re.sub(r"[^a-z0-9]+", "", key)


def canonicalize_resource_name(value: str) -> str:
    """Return a canonical lookup key for data resource identifiers.

    Resource names preserve important scientific spelling distinctions before
    applying the base rule: ``0.1`` becomes ``0p1``, ``λ`` becomes
    ``lambda`` and ``°`` becomes ``degree``.
    """
    key = value.strip().casefold()
    key = key.replace("\u00b0", "degree")
    key = key.replace("\u03bb", "lambda")
    key = re.sub(r"(?<=\d)\.(?=\d)", "p", key)
    return canonicalize_name(key)


def canonical_method_name(value: str) -> str:
    """Return a canonical lookup key for method and option names."""
    return canonicalize_name(value)


__all__ = [
    "canonicalize_name",
    "canonicalize_resource_name",
    "canonical_method_name",
]
