"""Integration tests for quality examples."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "quality"
_EXAMPLE_FILENAMES = ("example_01_ssi.py",)


@pytest.mark.examples
@pytest.mark.parametrize("filename", _EXAMPLE_FILENAMES)
def test_quality_examples_run(filename: str) -> None:
    runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
