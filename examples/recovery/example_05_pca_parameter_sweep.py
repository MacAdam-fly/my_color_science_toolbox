"""Sweep PCA recovery parameters for one reflectance target."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import reflectance_to_XYZ
from color.datasets.color_cards import get_color_card
from color.plot import plot_bars, plot_lines, plot_style
from color.recovery import load_reflectance_library, recover_reflectance_from_XYZ
from color.spectra import from_columns


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


def _recover_pca(target_XYZ, library, *, n_components: int, regularization: float):
    return recover_reflectance_from_XYZ(
        target_XYZ,
        method="pca",
        library=library,
        illuminant="D65",
        n_components=n_components,
        coefficient_regularization=regularization,
    )


def _closed_error(reflectance, target_XYZ, shape) -> float:
    closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65", shape=shape)
    return float(np.linalg.norm(closed_XYZ - target_XYZ))


def _print_table(title: str, rows: list[tuple[str, float]]) -> None:
    print(title)
    for label, error in rows:
        print(f"  {label:<16} XYZ error = {error:.6g}")
    print()


def main() -> None:
    library = load_reflectance_library("munsell_matt")
    raw = get_color_card("macbeth")
    original = from_columns(raw, y="Orange", name="Macbeth Orange").align(library.shape)
    target_XYZ = reflectance_to_XYZ(original, illuminant="D65", shape=library.shape)

    component_values = (3, 6, 12, 24)
    regularization_values = (0.0, 1e-4, 1e-3, 1e-2)

    component_results = [
        _recover_pca(
            target_XYZ,
            library,
            n_components=n_components,
            regularization=1e-3,
        )
        for n_components in component_values
    ]
    regularization_results = [
        _recover_pca(
            target_XYZ,
            library,
            n_components=12,
            regularization=regularization,
        )
        for regularization in regularization_values
    ]

    component_errors = [
        _closed_error(result, target_XYZ, library.shape) for result in component_results
    ]
    regularization_errors = [
        _closed_error(result, target_XYZ, library.shape) for result in regularization_results
    ]

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("PCA library datasets:", library.metadata["datasets"])
    print("PCA library sample count:", library.metadata["sample_count"])
    print("PCA library shape:", library.shape)
    print()
    _print_table(
        "n_components sweep, coefficient_regularization=1e-3",
        [(f"n={n}", error) for n, error in zip(component_values, component_errors)],
    )
    _print_table(
        "coefficient_regularization sweep, n_components=12",
        [(f"reg={reg:g}", error) for reg, error in zip(regularization_values, regularization_errors)],
    )

    with plot_style("presentation", font_scale=0.62, line_scale=0.85):
        fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.2))
        plot_lines(
            [(original.wavelengths, original.values)]
            + [(result.wavelengths, result.values) for result in component_results],
            ax=axes[0],
            labels=["original"] + [f"n={n}" for n in component_values],
            linestyles=["-", "--", "--", "--", "--"],
            linewidth=1.3,
            title="PCA Components",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        plot_bars(
            component_errors,
            ax=axes[1],
            labels=[str(n) for n in component_values],
            title="XYZ Closure Error",
            xlabel="n_components",
            ylabel="||closed XYZ - target XYZ||",
        )
        _save_figure(fig, "05_pca_components_sweep.png")

        fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.2))
        plot_lines(
            [(original.wavelengths, original.values)]
            + [(result.wavelengths, result.values) for result in regularization_results],
            ax=axes[0],
            labels=["original"] + [f"{reg:g}" for reg in regularization_values],
            linestyles=["-", "--", "--", "--", "--"],
            linewidth=1.3,
            title="PCA Regularization",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        plot_bars(
            regularization_errors,
            ax=axes[1],
            labels=[f"{reg:g}" for reg in regularization_values],
            title="XYZ Closure Error",
            xlabel="coefficient_regularization",
            ylabel="||closed XYZ - target XYZ||",
        )
        _save_figure(fig, "05_pca_regularization_sweep.png")


if __name__ == "__main__":
    main()
