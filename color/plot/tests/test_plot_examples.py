"""Integration tests for plot examples."""

from __future__ import annotations

import runpy
from pathlib import Path


_EXAMPLES = Path(__file__).resolve().parents[3] / "examples" / "plot"


def test_plot_examples_run() -> None:
    runpy.run_path(str(_EXAMPLES / "example_01_plot_overview.py"), run_name="__main__")
    runpy.run_path(str(_EXAMPLES / "example_02_temperature_visualization.py"), run_name="__main__")
