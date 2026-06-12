"""Run device examples."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

import pytest


_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "device"
_EXAMPLE_FILENAMES = (
    "example_01_melanopic_silent_substitution.py",
)


@pytest.mark.examples
@pytest.mark.parametrize("filename", _EXAMPLE_FILENAMES)
def test_device_examples_run(filename: str):
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))
    runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
