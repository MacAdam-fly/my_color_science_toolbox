from __future__ import annotations

import runpy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.examples
def test_appearance_examples_run() -> None:
    runpy.run_path(str(ROOT / "examples" / "appearance" / "example_01_ciecam02.py"), run_name="__main__")
    runpy.run_path(str(ROOT / "examples" / "appearance" / "example_02_ciecam16.py"), run_name="__main__")
