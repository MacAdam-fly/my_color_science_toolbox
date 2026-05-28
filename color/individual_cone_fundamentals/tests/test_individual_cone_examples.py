"""Run individual cone fundamental examples."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path


_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLES = _ROOT / "examples" / "individual_cone_fundamentals"


def test_individual_cone_fundamental_examples_run():
    if str(_EXAMPLES) not in sys.path:
        sys.path.insert(0, str(_EXAMPLES))
    runpy.run_path(
        str(_EXAMPLES / "example_01_stockman_rider_2023.py"),
        run_name="__main__",
    )
