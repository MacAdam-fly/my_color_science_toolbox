"""Run colorimetry examples as end-to-end integration checks."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[3]
_COLORIMETRY_EXAMPLES = _ROOT / "examples" / "colorimetry"
_SPACES_EXAMPLES = _ROOT / "examples" / "spaces"


def test_colorimetry_examples_run():
    for directory in (_COLORIMETRY_EXAMPLES, _SPACES_EXAMPLES):
        if str(directory) not in sys.path:
            sys.path.insert(0, str(directory))

    example_paths = [
        _COLORIMETRY_EXAMPLES / "example_01_spectral_conversion_overview.py",
        _COLORIMETRY_EXAMPLES / "example_02_reflectance_color_cards.py",
        _COLORIMETRY_EXAMPLES / "example_03_emission_spectra.py",
        _COLORIMETRY_EXAMPLES / "example_04_illuminant_a_comparison.py",
        _COLORIMETRY_EXAMPLES / "example_05_chromaticity_arrays.py",
        _COLORIMETRY_EXAMPLES / "example_06_photometry.py",
        _COLORIMETRY_EXAMPLES / "example_07_lightness.py",
        _COLORIMETRY_EXAMPLES / "example_08_lms_xyz_transformations.py",
        _COLORIMETRY_EXAMPLES / "example_09_dominant_wavelength.py",
        _COLORIMETRY_EXAMPLES / "example_10_temperature.py",
        _SPACES_EXAMPLES / "example_01_rgb_colourspace_conversion.py",
        _SPACES_EXAMPLES / "example_02_colourspace_chain.py",
        _SPACES_EXAMPLES / "example_03_cam02_uniform_spaces.py",
    ]

    for path in example_paths:
        runpy.run_path(str(path), run_name="__main__")
