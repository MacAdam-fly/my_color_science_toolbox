"""Run dataset examples as end-to-end dataset checks."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest


_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "datasets"


@pytest.mark.examples
def test_dataset_examples_run() -> None:
    """Run all dataset examples without interactive plotting."""
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))

    for filename in (
        "example_01_illuminants.py",
        "example_02_color_cards.py",
        "example_03_standard_observers.py",
        "example_04_gamut_data.py",
        "example_05_color_systems.py",
        "example_06_custom_data.py",
        "example_07_uef_reflectance_spectra.py",
    ):
        runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
