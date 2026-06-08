"""Integration tests for plot examples."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "plot"


@pytest.mark.examples
def test_plot_examples_run() -> None:
    runpy.run_path(str(_EXAMPLES / "example_01_plot_overview.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_02_cct_loci.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_03_dominant_wavelength.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_04_rgb_gamut_comparison.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_05_component_gallery.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_06_image_rgb_colourspace_conversion.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_07_plot_style_comparison.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_08_3d_primitives.py"), run_name="__main__")
