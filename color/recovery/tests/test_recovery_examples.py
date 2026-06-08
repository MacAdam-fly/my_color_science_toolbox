"""Run recovery examples."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "recovery"


@pytest.mark.examples
def test_recovery_examples_run() -> None:
    """Recovery examples should run without interactive windows."""
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))

    for filename in (
        "example_01_reflectance_recovery.py",
        "example_02_spectrum_recovery.py",
        "example_03_reflectance_library.py",
        "example_04_pca_reflectance_recovery.py",
        "example_05_pca_parameter_sweep.py",
        "example_06_dictionary_reflectance_recovery.py",
        "example_07_gaussian_spectrum_recovery.py",
        "example_08_multi_gaussian_spectrum_recovery.py",
        "example_09_auto_gaussian_spectrum_recovery.py",
        "example_10_reflectance_method_comparison.py",
    ):
        runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
