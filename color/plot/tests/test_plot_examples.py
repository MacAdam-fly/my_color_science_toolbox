"""Integration tests for plot examples."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "plot"
_EXAMPLE_FILENAMES = (
    "example_01_plot_overview.py",
    "example_02_cct_loci.py",
    "example_03_dominant_wavelength.py",
    "example_04_rgb_gamut_comparison.py",
    "example_05_component_gallery.py",
    "example_06_image_rgb_colourspace_conversion.py",
    "example_07_plot_style_comparison.py",
    "example_08_3d_primitives.py",
)


@pytest.mark.examples
@pytest.mark.parametrize("filename", _EXAMPLE_FILENAMES)
def test_plot_examples_run(filename: str) -> None:
    runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
