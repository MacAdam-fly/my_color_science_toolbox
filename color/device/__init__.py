"""Device-primary response and silent-substitution utilities."""

from __future__ import annotations

from .responses import PrimaryResponseDisplay
from .silent_substitution import melanopic_silent_range

__all__ = [
    "PrimaryResponseDisplay",  # primary response matrix display definition
]

__all__ += [
    "melanopic_silent_range",  # solve minimum and maximum XYZ/LMS-silent endpoints
]
