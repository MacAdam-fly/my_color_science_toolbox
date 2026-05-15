"""Tests for color.datasets.color_systems — color notation system loaders."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets.color_systems import get_color_system, list_color_systems


class TestListColorSystems:
    """Tests for list_color_systems()."""

    def test_returns_list(self):
        result = list_color_systems()
        assert isinstance(result, list)

    def test_contains_expected(self):
        result = list_color_systems()
        assert "munsell_srgb" in result


class TestMunsellSRGB:
    """Tests for RIT Munsell renotation data."""

    def test_returns_dict(self):
        data = get_color_system("munsell_srgb")
        assert isinstance(data, dict)

    def test_chip_count(self):
        data = get_color_system("munsell_srgb")
        first_col = list(data.keys())[0]
        assert len(data[first_col]) > 1600
