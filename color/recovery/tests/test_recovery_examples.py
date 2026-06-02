"""Run recovery examples."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "recovery"


def test_recovery_examples_run() -> None:
    """Recovery examples should run without interactive windows."""
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))

    runpy.run_path(
        str(_EXAMPLES / "example_01_reflectance_recovery.py"),
        run_name="__main__",
    )
