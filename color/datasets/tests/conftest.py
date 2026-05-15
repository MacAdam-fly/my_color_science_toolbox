"""Shared fixtures for the datasets test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path so ``import color`` works.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


@pytest.fixture(scope="session")
def data_root() -> Path:
    """Absolute path to the ``color/data/`` directory."""
    return _PROJECT_ROOT / "color" / "data"
