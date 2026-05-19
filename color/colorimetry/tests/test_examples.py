"""Run colorimetry examples as end-to-end integration checks."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "colorimetry"


def test_colorimetry_examples_run():
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))

    example_paths = [
        _EXAMPLES / "example_end_to_end_smoke.py",
        _EXAMPLES / "example_illuminant_a_xyz_comparison.py",
        _EXAMPLES / "example_reflectance_color_card_xyz_lms.py",
        _EXAMPLES / "example_emission_generators_xyz_lms.py",
        _EXAMPLES / "example_photometry.py",
        _EXAMPLES / "example_lightness.py",
        _EXAMPLES / "example_lms_xyz_transformations.py",
    ]

    for path in example_paths:
        runpy.run_path(str(path), run_name="__main__")
