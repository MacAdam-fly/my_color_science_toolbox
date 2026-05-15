"""Color appearance model facades."""

from __future__ import annotations

from dataclasses import dataclass

from ..utils.CAM02 import Cam02


@dataclass
class ColorAppearanceToolkit:
    """Entry point for appearance-model calculations."""

    def cam02(self, *args, **kwargs) -> Cam02:
        return Cam02(*args, **kwargs)
