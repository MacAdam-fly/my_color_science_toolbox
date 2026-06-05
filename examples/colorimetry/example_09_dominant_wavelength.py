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
from color.plot import (
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_labels,
    plot_points,
    plot_segments,
    plot_style,
)


def _plot_sample(
    ax: plt.Axes,
    *,
    name: str,
    xy: np.ndarray,
    xy_n: np.ndarray,
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

    plot_cie1931_diagram(ax=ax, title="", whitepoint_xy=xy_n)
    plot_chromaticity_points(
        xy,
        ax=ax,
        labels=["sample"],
        color=sample_color,
    )
    if np.all(np.isfinite(reconstructed)):
        plot_points(
            reconstructed,
            ax=ax,
            labels=["reconstructed"],
            sizes=95,
            facecolors="none",
            edgecolors="black",
            linewidths=1.2,
        )

    if np.all(np.isfinite(xy_wl)):
        plot_segments(
            np.array([[xy_n, xy_wl]]),
            ax=ax,
            labels=["dominant ray"],
            color=sample_color,
            linewidth=1.6,
        )
        plot_points(xy_wl, ax=ax, colors=sample_color, markers="x", sizes=55)
        plot_labels(xy_wl, [f"{wavelength:.1f} nm"], ax=ax, grid=False)

    if np.all(np.isfinite(xy_comp)) and not np.allclose(xy_comp, xy_wl, equal_nan=True):
        plot_segments(
            np.array([[xy_n, xy_comp]]),
            ax=ax,
            labels=["complementary ray"],
            colors="tab:purple",
            linewidth=1.4,
            linestyles="--",
        )
        plot_points(xy_comp, ax=ax, colors="tab:purple", markers="x", sizes=55)
        plot_labels(
            xy_comp,
            [f"{abs(wavelength):.1f} nm"],
            ax=ax,
            offset=(8, -16),
            grid=False,
        )

    if np.all(np.isfinite(xy_comp)):
        plot_points(xy_comp, ax=ax, colors="tab:blue", markers="+", sizes=45)
        plot_labels(
            xy_comp,
            [f"cw {complementary:.1f} nm"],
            ax=ax,
            offset=(8, 8),
            color="tab:blue",
            grid=False,
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

    with plot_style("presentation", font_scale=0.65, line_scale=0.85):
        fig, axes = plt.subplots(2, 3, figsize=(14, 9.5))
        for ax, name in zip(axes.ravel(), samples):
            _plot_sample(
                ax,
                name=name,
                xy=samples[name],
                xy_n=xy_n,
                sample_color=sample_colors[name],
            )

        legend_items = {}
        for ax in axes.ravel():
            handles, labels = ax.get_legend_handles_labels()
            legend_items.update(zip(labels, handles))
        fig.legend(legend_items.values(), legend_items.keys(), loc="lower center", ncol=4)
        fig.suptitle("Dominant and Complementary Wavelength on CIE 1931 xy")
        fig.tight_layout(rect=(0, 0.08, 1, 0.95))
        output_path = output_dir / "09_dominant_wavelength.png"
        fig.savefig(output_path, dpi=150)
        plt.close(fig)
    print(f"Plot saved to {output_path}")

    # test the analyze_chromaticity function with a non-standard xy sample
    test_xy = np.array([0.31, 0.33])  # D65
    analysis = analyze_chromaticity(test_xy, xy_n=xy_n)
    print(analysis)


if __name__ == "__main__":
    main()
