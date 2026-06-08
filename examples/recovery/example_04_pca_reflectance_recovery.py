"""Compare bounded least-squares and PCA reflectance recovery."""

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
from color.recovery import (
    BoundedLeastSquaresOptions,
    PCAReflectanceOptions,
    load_reflectance_library,
    recover_reflectance_from_XYZ,
)
from color.spectra import from_columns, SpectralShape


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


def main() -> None:
    spectra_shape = SpectralShape(400, 700, 3)
    library = load_reflectance_library("munsell_matt", shape=spectra_shape)
    raw = get_color_card("macbeth")
    original = from_columns(raw, y="Foliage", name="Macbeth Foliage").align(spectra_shape)
    target_XYZ = reflectance_to_XYZ(original, illuminant="D65", shape=library.shape)

    bounded = recover_reflectance_from_XYZ(
        target_XYZ,
        method=BoundedLeastSquaresOptions(smoothness=1e-3),
        illuminant="D65",
        shape=library.shape,
    )
    pca = recover_reflectance_from_XYZ(
        target_XYZ,
        method=PCAReflectanceOptions(
            library=library,
            n_components=30,
            coefficient_regularization=1e-3,
        ),
        illuminant="D65",
    )

    bounded_closed = reflectance_to_XYZ(bounded, illuminant="D65", shape=library.shape)
    pca_closed = reflectance_to_XYZ(pca, illuminant="D65", shape=library.shape)

    print("Target XYZ:", np.round(target_XYZ, 6))
    print("Bounded least-squares closed XYZ:", np.round(bounded_closed, 6))
    print("PCA closed XYZ:", np.round(pca_closed, 6))
    print("Bounded least-squares error:", np.linalg.norm(bounded_closed - target_XYZ))
    print("PCA error:", np.linalg.norm(pca_closed - target_XYZ))
    print("PCA library datasets:", pca.metadata["library_datasets"])
    print("PCA library sample count:", pca.metadata["library_sample_count"])
    print("PCA components:", pca.metadata["n_components"])

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, ax = plt.subplots(figsize=(7.16, 4.2))
        plot_lines(
            [
                (original.wavelengths, original.values),
                (bounded.wavelengths, bounded.values),
                (pca.wavelengths, pca.values),
            ],
            ax=ax,
            labels=["original", "bounded least-squares", "PCA"],
            linestyles=["-", "--", ":"],
            linewidth=1.4,
            title="PCA Reflectance Recovery",
            xlabel="Wavelength (nm)",
            ylabel="Reflectance",
        )
        _save_figure(fig, "04_pca_reflectance_recovery.png")


if __name__ == "__main__":
    main()
