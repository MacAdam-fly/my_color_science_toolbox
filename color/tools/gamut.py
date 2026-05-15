"""Gamut related helpers."""

from __future__ import annotations

from dataclasses import dataclass

from ..utils.gamut_Info_utils import GamutInfo


@dataclass
class GamutToolkit:
    """Facade for gamut loading and analysis."""

    def load(self, LCH_gamut_path: str) -> GamutInfo:
        return GamutInfo(LCH_gamut_path)
