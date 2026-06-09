"""Run IO examples as end-to-end integration checks."""

from __future__ import annotations

import runpy
from pathlib import Path

import pytest


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "io"
_EXAMPLE_FILENAMES = (
    "example_01_figure_export.py",
    "example_02_spectral_data_io.py",
    "example_03_image_io.py",
)


@pytest.mark.examples
@pytest.mark.parametrize("filename", _EXAMPLE_FILENAMES)
def test_io_examples_run(filename: str) -> None:
    runpy.run_path(str(_EXAMPLES / filename), run_name="__main__")
