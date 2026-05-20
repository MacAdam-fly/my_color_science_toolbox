"""Shared plotting helpers for spectra examples."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def example_output_dir() -> Path:
    """Return the shared output directory for spectra examples."""
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)
    return output_dir


def save_figure(fig: plt.Figure, filename: str) -> Path:
    """Save *fig* into the spectra output directory."""
    output_path = example_output_dir() / filename
    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)
    print(f"Plot saved to {output_path}")
    return output_path


def style_spectral_axis(
    ax: plt.Axes,
    *,
    title: str,
    ylabel: str = "Value",
) -> None:
    """Apply common spectral-plot axis styling."""
    ax.set_title(title)
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
