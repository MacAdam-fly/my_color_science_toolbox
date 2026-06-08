"""Compare bounded least-squares, PCA, and dictionary reflectance recovery."""

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
from color.plot import plot_lines, plot_style
from color.recovery import load_reflectance_library, recover_reflectance_from_XYZ
from color.spectra import SpectralShape, from_columns


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


def _closed_error(reflectance, target_XYZ, shape) -> float:
    closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65", shape=shape)
    return float(np.linalg.norm(closed_XYZ - target_XYZ))


def main() -> None:
    shape = SpectralShape(400, 700, 10)
    library = load_reflectance_library("munsell_matt", shape=shape)
    raw = get_color_card("macbeth")
    original = from_columns(raw, y="Yellow", name="Macbeth Yellow").align(shape)
    target_XYZ = reflectance_to_XYZ(original, illuminant="D65", shape=shape)

    bounded = recover_reflectance_from_XYZ(
        target_XYZ,
        method="bounded_least_squares",
        illuminant="D65",
        shape=shape,
        smoothness=1e-3,
    )
    pca = recover_reflectance_from_XYZ(
        target_XYZ,
        method="pca",
        library=library,
        illuminant="D65",
        n_components=12,
        coefficient_regularization=1e-3,
    )
    dictionary = recover_reflectance_from_XYZ(
        target_XYZ,
        method="dictionary",
        library=library,
        illuminant="D65",
        dictionary_regularization=1e-6,
    )

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("Bounded least-squares error:", _closed_error(bounded, target_XYZ, shape))
    print("PCA error:", _closed_error(pca, target_XYZ, shape))
    print("Dictionary error:", _closed_error(dictionary, target_XYZ, shape))
    print("Dictionary library datasets:", dictionary.metadata["library_datasets"])
    print("Dictionary library sample count:", dictionary.metadata["library_sample_count"])
    print("Dictionary regularization:", dictionary.metadata["dictionary_regularization"])

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            [
                (original.wavelengths, original.values),
                (bounded.wavelengths, bounded.values),
                (pca.wavelengths, pca.values),
                (dictionary.wavelengths, dictionary.values),
            ],
            ax=ax,
            labels=["original", "bounded least-squares", "PCA", "dictionary"],
            linestyles=["-", "--", ":", "-."],
            linewidth=1.4,
            title="Dictionary Reflectance Recovery",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        _save_figure(fig, "06_dictionary_reflectance_recovery.png")


if __name__ == "__main__":
    main()
