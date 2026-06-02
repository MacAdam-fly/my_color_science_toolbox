"""Shared path helpers for colour-space examples."""

from __future__ import annotations

from pathlib import Path


def output_dir() -> Path:
    """Return the spaces example output directory."""
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path
