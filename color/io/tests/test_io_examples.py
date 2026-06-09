"""Run IO examples as end-to-end integration checks."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "io"


@pytest.mark.examples
def test_io_examples_run() -> None:
    runpy.run_path(str(_EXAMPLES / "example_01_figure_export.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_02_spectral_data_io.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_03_image_io.py"), run_name="__main__")
