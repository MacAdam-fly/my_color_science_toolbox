"""Shared helpers for dataset examples."""

from __future__ import annotations

from pathlib import Path


def example_output_dir() -> Path:
    """Return the shared output directory for dataset examples."""
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_figure(fig, filename: str, *, suptitle_top: float = 0.93) -> Path:
    """Save *fig* into the dataset output directory.

    If a figure has a suptitle, reserve vertical space for it before saving.
    The journal plot styles use larger titles than older examples, so a plain
    tight layout can otherwise push the suptitle into the top row of axes.
    """
    import matplotlib.pyplot as plt

    output_path = example_output_dir() / filename
    if getattr(fig, "_suptitle", None) is not None:
        fig.tight_layout(rect=(0.0, 0.0, 1.0, suptitle_top))
    else:
        fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")
    return output_path
