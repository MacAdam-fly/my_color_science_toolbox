"""Run gamut examples."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "gamut"


def test_gamut_examples_run():
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))
    for filename in (
        "example_01_display_primary_gamut.py",
        "example_02_lch_boundary_metrics.py",
        "example_03_gamut_solids_3d.py",
        "example_04_projected_plane_and_rings.py",
        "example_05_gamut_coverage.py",
        "example_06_pointer_gamut.py",
        "example_07_macadam_limits.py",
        "example_08_computed_macadam_limits.py",
        "example_09_gamut_analysis.py",
        "example_10_macadam_rgbc_solids.py",
        "example_11_custom_rgb_colourspace_gamut.py",
    ):
        runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
