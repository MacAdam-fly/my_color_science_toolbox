"""Shared color conversion context."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .types import ArrayLike


@dataclass
class ColorContext:
    """Holds optional parameters used by various color spaces."""

    white_point: Optional[ArrayLike] = None
    white_point_xyy: Optional[ArrayLike] = None
    background_xyz: Optional[ArrayLike] = None
    background_xyy: Optional[ArrayLike] = None
    reference_white_xyy: Optional[ArrayLike] = None
    adapting_luminance: Optional[float] = None
    surround: str = "AVERAGE"
    fov: Optional[int] = None
    extra: Dict[str, Any] = field(default_factory=dict)
