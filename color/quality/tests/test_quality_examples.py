"""Integration tests for quality examples."""

from __future__ import annotations

import runpy
from pathlib import Path


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "quality"


def test_quality_examples_run() -> None:
    runpy.run_path(str(_EXAMPLES / "example_01_ssi.py"), run_name="__main__")
