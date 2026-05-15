"""Conversion router using the XYZ center."""

from __future__ import annotations

from typing import Optional

from ..core.context import ColorContext
from .registry import get_space
from .validation import validate_context


def convert(values, src: str, dst: str, context: Optional[ColorContext] = None):
    """Convert values between registered spaces using XYZ as the hub."""

    if context is None:
        context = ColorContext()
    src_space = get_space(src)
    dst_space = get_space(dst)
    validate_context(context, src_space.required_context, src_space.name)
    validate_context(context, dst_space.required_context, dst_space.name)
    xyz = src_space.to_xyz(values, context=context)
    return dst_space.from_xyz(xyz, context=context)
