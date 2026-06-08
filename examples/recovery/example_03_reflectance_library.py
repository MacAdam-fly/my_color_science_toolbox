"""Load reflectance libraries for future basis and dictionary recovery."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt

from color.datasets import list_reflectance_spectra
from color.plot import plot_lines, plot_style
from color.recovery import load_reflectance_library


def _output_dir() -> Path:
    output = Path(__file__).resolve().parent / "output"
    output.mkdir(exist_ok=True)
    return output


def _save_figure(fig, filename: str) -> Path:
    output_path = _output_dir() / filename
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")
    return output_path


def _representative_indices(count: int, n: int = 6) -> list[int]:
    if count <= n:
        return list(range(count))
    return [round(i * (count - 1) / (n - 1)) for i in range(n)]


def main() -> None:
    default_library = load_reflectance_library()
    # all_uef_library = load_reflectance_library("all_uef")
    mixed_library = load_reflectance_library(("munsell_matt", "agfa_it872"))

    print("Registered UEF reflectance datasets:")
    print(", ".join(list_reflectance_spectra()))
    print()
    print("Default library datasets:", default_library.metadata["datasets"])
    print("Default matrix shape:", default_library.reflectances.shape)
    # print("all_uef sample count:", all_uef_library.metadata["sample_count"])
    print("Mixed library sample counts:", mixed_library.metadata["sample_counts"])
    print("First default labels:", default_library.labels[:5])

    indices = _representative_indices(default_library.reflectances.shape[0], n=6)
    series = [
        (default_library.wavelengths, default_library.reflectances[index])
        for index in indices
    ]
    labels = [default_library.labels[index] for index in indices]

    with plot_style("presentation", font_scale=0.75, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            series,
            ax=ax,
            labels=labels,
            linewidth=1.3,
            title="Reflectance Library Samples",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        _save_figure(fig, "03_reflectance_library_samples.png")


if __name__ == "__main__":
    main()
