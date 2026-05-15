"""Complementary color helpers."""

from __future__ import annotations

from dataclasses import dataclass


def opposite_hue(hue_deg: float) -> float:
    return (float(hue_deg) + 180.0) % 360.0


@dataclass
class ComplementaryToolkit:
    """Placeholder entry point for complementary-color logic."""

    @staticmethod
    def opposite_hue(hue_deg: float) -> float:
        return opposite_hue(hue_deg)
