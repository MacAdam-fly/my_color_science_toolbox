"""Compare reflectance recovery methods for three Macbeth colour patches."""

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
from color.recovery import (
    BoundedLeastSquaresOptions,
    Burns2019RecoveryOptions,
    DictionaryReflectanceOptions,
    Meng2015RecoveryOptions,
    PCAReflectanceOptions,
    load_reflectance_library,
    recover_reflectance_from_XYZ,
)
from color.spectra import SpectralShape, from_columns


PATCHES = ("Blue Sky", "Foliage", "Moderate Red")
METHOD_LABELS = {
    "bounded_least_squares": "bounded LS",
    "burns2019": "Burns 2019",
    "meng2015": "Meng 2015",
    "pca": "PCA",
    "dictionary": "dictionary",
}


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


def _roughness(values: np.ndarray) -> float:
    return float(np.linalg.norm(np.diff(np.asarray(values, dtype=np.float64), n=2)))


def _recover_methods(target_XYZ: np.ndarray, shape: SpectralShape, library) -> dict[str, object]:
    return {
        "bounded_least_squares": recover_reflectance_from_XYZ(
            target_XYZ,
            method=BoundedLeastSquaresOptions(smoothness=1e-3),
            illuminant="D65",
            shape=shape,
        ),
        "burns2019": recover_reflectance_from_XYZ(
            target_XYZ,
            method=Burns2019RecoveryOptions(),
            illuminant="D65",
            shape=shape,
        ),
        "meng2015": recover_reflectance_from_XYZ(
            target_XYZ,
            method=Meng2015RecoveryOptions(),
            illuminant="D65",
            shape=shape,
        ),
        "pca": recover_reflectance_from_XYZ(
            target_XYZ,
            method=PCAReflectanceOptions(
                library=library,
                n_components=40,
                coefficient_regularization=1e-3,
            ),
            illuminant="D65",
        ),
        "dictionary": recover_reflectance_from_XYZ(
            target_XYZ,
            method=DictionaryReflectanceOptions(
                library=library,
                regularization=1e-6,
                top_k=120,
            ),
            illuminant="D65",
        ),
    }


def main() -> None:
    shape = SpectralShape(400, 700, 5)
    library = load_reflectance_library("munsell_matt", shape=shape)
    raw = get_color_card("macbeth")

    print("Reflectance library datasets:", library.metadata["datasets"])
    print("Reflectance library samples:", library.metadata["sample_count"])
    print("Dictionary candidate atoms per target: 600")

    originals = {}
    recovered_by_patch = {}
    closure_errors = []
    roughness_values = []

    for patch in PATCHES:
        original = from_columns(raw, y=patch, name=f"Macbeth {patch}").align(shape)
        target_XYZ = reflectance_to_XYZ(original, illuminant="D65", shape=shape)
        recovered = _recover_methods(target_XYZ, shape, library)

        originals[patch] = original
        recovered_by_patch[patch] = recovered

        patch_errors = []
        patch_roughness = []
        print(f"\n{patch}")
        print("  Target XYZ:", np.round(target_XYZ, 6))
        for method, reflectance in recovered.items():
            closed_XYZ = reflectance_to_XYZ(reflectance, illuminant="D65", shape=shape)
            error = float(np.linalg.norm(closed_XYZ - target_XYZ))
            roughness = _roughness(reflectance.values)
            patch_errors.append(error)
            patch_roughness.append(roughness)
            print(
                "  "
                f"{METHOD_LABELS[method]:>12}: "
                f"error={error:.6g}, "
                f"min={np.min(reflectance.values):.6g}, "
                f"max={np.max(reflectance.values):.6g}, "
                f"roughness={roughness:.6g}"
            )
            if method in {"pca", "dictionary"}:
                print(
                    "  "
                    f"{METHOD_LABELS[method]:>12}: "
                    f"library samples={reflectance.metadata['library_sample_count']}"
                )
        closure_errors.append(patch_errors)
        roughness_values.append(patch_roughness)

    method_names = tuple(METHOD_LABELS)
    method_labels = [METHOD_LABELS[name] for name in method_names]

    with plot_style("presentation", font_scale=0.55, line_scale=0.8):
        fig, axes = plt.subplots(1, 3, figsize=(11.5, 4.0), sharey=True)
        for ax, patch in zip(axes, PATCHES):
            original = originals[patch]
            recovered = recovered_by_patch[patch]
            series = [(original.wavelengths, original.values)]
            labels = ["original"]
            linestyles = ["-"]
            for method in method_names:
                reflectance = recovered[method]
                series.append((reflectance.wavelengths, reflectance.values))
                labels.append(METHOD_LABELS[method])
                linestyles.append("--")
            plot_lines(
                series,
                ax=ax,
                labels=labels,
                linestyles=linestyles,
                linewidth=1.1,
                title=patch,
                xlabel="Wavelength (nm)",
                ylabel="Reflectance",
                legend=False,
            )
        axes[-1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        _save_figure(fig, "10_reflectance_method_curves.png")

        fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.0))
        error_values = np.maximum(np.asarray(closure_errors, dtype=np.float64).T, 1e-12)
        roughness_array = np.asarray(roughness_values, dtype=np.float64).T
        plot_bars(
            error_values,
            ax=axes[0],
            labels=PATCHES,
            group_labels=method_labels,
            title="XYZ Closure Error",
            ylabel="L2 error",
            legend=False,
        )
        axes[0].set_yscale("log")
        plot_bars(
            roughness_array,
            ax=axes[1],
            labels=PATCHES,
            group_labels=method_labels,
            title="Curve Roughness",
            ylabel="Second-difference norm",
            legend=False,
        )
        axes[1].legend(loc="center left", bbox_to_anchor=(1.02, 0.5))
        _save_figure(fig, "10_reflectance_method_metrics.png")



if __name__ == "__main__":
    main()
