"""Compute and plot dominant wavelength, complementary wavelength and purity."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.colorimetry import (
    analyze_chromaticity,
    colorimetric_purity,
    complementary_wavelength,
    dominant_wavelength,
    excitation_purity,
    xy_from_dominant_wavelength_pc,
)
from color.spectra import from_dataset


def _plot_sample(
    ax: plt.Axes,
    *,
    name: str,
    xy: np.ndarray,
    xy_n: np.ndarray,
    locus_xy: np.ndarray,
    sample_color: str,
) -> None:
    result = analyze_chromaticity(xy, xy_n=xy_n)
    wavelength = result.wavelength
    xy_wl = result.dominant_xy
    complementary = result.complementary_wavelength
    xy_comp = result.complementary_xy
    purity_e = excitation_purity(xy, xy_n=xy_n)
    reconstructed = (
        xy_from_dominant_wavelength_pc(
            result.wavelength,
            result.colorimetric_purity,
            xy_n=xy_n,
        )
        if np.isfinite(result.wavelength)
        else np.array([np.nan, np.nan])
    )

    closed_locus = np.vstack([locus_xy, locus_xy[0]])
    ax.plot(closed_locus[:, 0], closed_locus[:, 1], color="0.25", linewidth=1.4)
    ax.scatter(locus_xy[::40, 0], locus_xy[::40, 1], s=12, color="0.45", alpha=0.7)
    ax.scatter(*xy_n, s=45, color="black", label="D65 white")
    ax.scatter(*xy, s=55, color=sample_color, label="sample")
    if np.all(np.isfinite(reconstructed)):
        ax.scatter(
            *reconstructed,
            s=95,
            facecolors="none",
            edgecolors="black",
            linewidths=1.2,
            label="reconstructed",
        )

    if np.all(np.isfinite(xy_wl)):
        ax.plot(
            [xy_n[0], xy_wl[0]],
            [xy_n[1], xy_wl[1]],
            color=sample_color,
            linewidth=1.6,
            label="dominant ray",
        )
        ax.scatter(*xy_wl, s=55, color=sample_color, marker="x")
        ax.annotate(
            f"{wavelength:.1f} nm",
            xy=xy_wl,
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9,
        )

    if np.all(np.isfinite(xy_comp)) and not np.allclose(xy_comp, xy_wl, equal_nan=True):
        ax.plot(
            [xy_n[0], xy_comp[0]],
            [xy_n[1], xy_comp[1]],
            color="tab:purple",
            linewidth=1.4,
            linestyle="--",
            label="complementary ray",
        )
        ax.scatter(*xy_comp, s=55, color="tab:purple", marker="x")
        ax.annotate(
            f"{abs(wavelength):.1f} nm",
            xy=xy_comp,
            xytext=(8, -16),
            textcoords="offset points",
            fontsize=9,
        )

    if np.all(np.isfinite(xy_comp)):
        ax.scatter(*xy_comp, s=45, color="tab:blue", marker="+")
        ax.annotate(
            f"cw {complementary:.1f} nm",
            xy=xy_comp,
            xytext=(8, 8),
            textcoords="offset points",
            fontsize=9,
            color="tab:blue",
        )

    ax.set_title(f"{name}\nPe={purity_e:.3f}")
    ax.set_xlabel("CIE x")
    ax.set_ylabel("CIE y")
    ax.set_xlim(-0.02, 0.78)
    ax.set_ylim(-0.02, 0.86)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.3)


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    xy_n = np.array([0.3127, 0.3290], dtype=np.float64)
    samples = {
        "red region": np.array([0.54369557, 0.32107944]),
        "yellow-green region": np.array([0.36, 0.52]),
        "cyan-blue region": np.array([0.18, 0.22]),
        "deep blue region": np.array([0.16, 0.08]),
        "non-spectral purple region": np.array([0.37605506, 0.24452225]),
        "near white": xy_n.copy(),
    }
    sample_colors = {
        "red region": "tab:red",
        "yellow-green region": "tab:green",
        "cyan-blue region": "tab:cyan",
        "deep blue region": "tab:blue",
        "non-spectral purple region": "tab:purple",
        "near white": "black",
    }

    for name, xy in samples.items():
        result = analyze_chromaticity(xy, xy_n=xy_n)
        wavelength, xy_wl = dominant_wavelength(xy, xy_n=xy_n)
        complementary, xy_comp = complementary_wavelength(xy, xy_n=xy_n)
        purity_e = excitation_purity(xy, xy_n=xy_n)
        purity_c = colorimetric_purity(xy, xy_n=xy_n)

        print(f"{name}:")
        print("  xy:", np.round(xy, 6))
        print("  dominant wavelength:", np.round(wavelength, 6))
        print("  dominant intersection:", np.round(xy_wl, 6))
        print("  dominant region:", result.dominant_region)
        print("  complementary wavelength:", np.round(complementary, 6))
        print("  complementary intersection:", np.round(xy_comp, 6))
        print("  complementary region:", result.complementary_region)
        print("  excitation purity:", np.round(purity_e, 6))
        print("  colorimetric purity:", np.round(purity_c, 6))
        if np.isfinite(wavelength):
            reconstructed = xy_from_dominant_wavelength_pc(
                wavelength,
                purity_c,
                xy_n=xy_n,
            )
            error = np.linalg.norm(reconstructed - xy)
            print("  reconstructed from Pc:", np.round(reconstructed, 6))
            print("  reconstruction error:", f"{error:.3e}")

    locus = from_dataset("standard_observers.chromaticity_coordinates", "cie1931_chro_1nm")
    x_index = locus.labels.index("x")
    y_index = locus.labels.index("y")
    locus_xy = locus.values[:, (x_index, y_index)]

    fig, axes = plt.subplots(2, 3, figsize=(14, 9.5))
    for ax, name in zip(axes.ravel(), samples):
        _plot_sample(
            ax,
            name=name,
            xy=samples[name],
            xy_n=xy_n,
            locus_xy=locus_xy,
            sample_color=sample_colors[name],
        )

    legend_items = {}
    for ax in axes.ravel():
        handles, labels = ax.get_legend_handles_labels()
        legend_items.update(zip(labels, handles))
    fig.legend(legend_items.values(), legend_items.keys(), loc="lower center", ncol=4)
    fig.suptitle("Dominant and Complementary Wavelength on CIE 1931 xy")
    fig.tight_layout(rect=(0, 0.08, 1, 0.95))
    output_path = output_dir / "dominant_wavelength.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")


if __name__ == "__main__":
    main()
