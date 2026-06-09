"""Run generator examples as end-to-end generator checks."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "generators"
_EXAMPLE_FILENAMES = (
    "example_01_registry_and_illuminants.py",
    "example_02_ideal_spectra.py",
    "example_03_illuminant_a_comparison.py",
    "example_04_led_spectra.py",
)


@pytest.mark.examples
@pytest.mark.parametrize("filename", _EXAMPLE_FILENAMES)
def test_generator_examples_run(filename: str) -> None:
    """Generator examples should run without interactive windows."""
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))

    runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
