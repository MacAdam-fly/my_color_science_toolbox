"""Validation helpers for space conversions."""

from __future__ import annotations

from typing import Iterable, Optional

from ..core.context import ColorContext


def validate_context(
    context: Optional[ColorContext],
    required_fields: Iterable[str],
    space_name: str,
) -> None:
    required = tuple(required_fields)
    if not required:
        return
    if context is None:
        raise ValueError(f"Missing context for {space_name}")
    missing = [field for field in required if getattr(context, field, None) is None]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"Missing context fields for {space_name}: {missing_list}")


def require_any(
    context: Optional[ColorContext],
    fields: Iterable[str],
    space_name: str,
    label: str,
) -> None:
    if context is None:
        raise ValueError(f"Missing context for {space_name}")
    if all(getattr(context, field, None) is None for field in fields):
        field_list = ", ".join(fields)
        raise ValueError(f"Missing {label} for {space_name}. Provide one of: {field_list}")
