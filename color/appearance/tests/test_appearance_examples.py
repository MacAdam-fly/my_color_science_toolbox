from __future__ import annotations

import runpy
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = ROOT / "examples" / "appearance"
_EXAMPLE_PATHS = (
    _EXAMPLES / "example_01_ciecam02.py",
    _EXAMPLES / "example_02_ciecam16.py",
)


@pytest.mark.examples
@pytest.mark.parametrize("path", _EXAMPLE_PATHS, ids=lambda path: path.name)
def test_appearance_examples_run(path: Path) -> None:
    runpy.run_path(str(path), run_name="__main__")
