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
        _COLORIMETRY_EXAMPLES / "example_end_to_end_smoke.py",
        _COLORIMETRY_EXAMPLES / "example_illuminant_a_xyz_comparison.py",
        _COLORIMETRY_EXAMPLES / "example_reflectance_color_card_xyz_lms.py",
        _COLORIMETRY_EXAMPLES / "example_emission_generators_xyz_lms.py",
        _COLORIMETRY_EXAMPLES / "example_photometry.py",
        _COLORIMETRY_EXAMPLES / "example_lightness.py",
        _COLORIMETRY_EXAMPLES / "example_lms_xyz_transformations.py",
        _COLORIMETRY_EXAMPLES / "example_dominant_wavelength.py",
        _COLORIMETRY_EXAMPLES / "example_temperature.py",
        _SPACES_EXAMPLES / "example_rgb_spaces.py",
    ]

    for path in example_paths:
        runpy.run_path(str(path), run_name="__main__")
