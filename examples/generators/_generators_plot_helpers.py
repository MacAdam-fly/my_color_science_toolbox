"""Shared helpers for generator examples."""

from __future__ import annotations

from pathlib import Path


def example_output_dir() -> Path:
    """Return the output directory for generator examples."""
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_figure(fig, filename: str) -> Path:
    """Save *fig* under the generator example output directory."""
    import matplotlib.pyplot as plt

    output_path = example_output_dir() / filename
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")
    return output_path
