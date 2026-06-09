"""Run spectra examples as end-to-end integration checks."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest


_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "spectra"
_EXAMPLE_PATHS = (
    _EXAMPLES / "example_01_create_spectral_objects.py",
    _EXAMPLES / "example_02_sampling_interpolation_alignment.py",
    _EXAMPLES / "example_03_multi_channel_workflow.py",
    _EXAMPLES / "example_04_export_and_arithmetic.py",
    _EXAMPLES / "example_05_visualization_cases.py",
)


@pytest.mark.examples
@pytest.mark.parametrize("path", _EXAMPLE_PATHS, ids=lambda path: path.name)
def test_spectra_examples_run(path: Path):
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))

    runpy.run_path(str(path), run_name="__main__")
