"""Demonstrate LMS-silent and XYZ-silent melanopic substitution."""

from __future__ import annotations

from pathlib import Path
import sys

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.device import PrimaryResponseDisplay, melanopic_silent_range
from color.plot import plot_bars, plot_lines, plot_style, style_2d_axis


OUTPUT_DIR = Path(__file__).resolve().parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def _example_display() -> PrimaryResponseDisplay:
    """Return a synthetic RGBC response display with LMS, XYZ and mel columns."""
    return PrimaryResponseDisplay(
        [
            [0.70, 0.30, 0.02, 0.65, 0.31, 0.04, 0.10],
            [0.25, 0.80, 0.10, 0.30, 0.72, 0.08, 0.20],
            [0.05, 0.15, 0.70, 0.08, 0.12, 0.68, 0.65],
            [0.20, 0.55, 0.45, 0.28, 0.50, 0.35, 0.95],
        ],
        response_names=("l", "m", "s", "x", "y", "z", "mel"),
        primary_names=("R", "G", "B", "C"),
    )


def _melanopic_contrast(low: float, high: float) -> float:
    """Return Michelson-style melanopic contrast."""
    return (high - low) / (high + low)


def _print_result(label: str, low, high) -> None:
    """Print a compact result summary."""
    print(f"\n{label}")
    print(f"Low mel weights: {low.weights}")
    print(f"High mel weights: {high.weights}")
    print(f"Low residual: {low.residual}")
    print(f"High residual: {high.residual}")
    print(f"Low mel: {float(low.melanopic):.6f}")
    print(f"High mel: {float(high.melanopic):.6f}")
    print(f"Melanopic contrast: {_melanopic_contrast(float(low.melanopic), float(high.melanopic)):.6f}")


def _batch_weights() -> np.ndarray:
    """Return deterministic baseline weights for a small batch sweep."""
    return np.array([
        [0.25, 0.50, 0.25, 0.15],
        [0.30, 0.45, 0.25, 0.20],
        [0.35, 0.45, 0.30, 0.20],
        [0.40, 0.35, 0.30, 0.25],
        [0.45, 0.30, 0.25, 0.30],
        [0.50, 0.25, 0.20, 0.35],
    ])


def _add_residual_text(ax, low, high) -> None:
    """Annotate maximum absolute held-response residual."""
    residual = max(
        float(np.max(np.abs(low.residual))),
        float(np.max(np.abs(high.residual))),
    )
    ax.text(
        0.02,
        0.95,
        f"max |residual| = {residual:.1e}",
        transform=ax.transAxes,
        va="top",
        fontsize=8,
    )


def main() -> None:
    display = _example_display()
    baseline_weights = np.array([0.35, 0.45, 0.30, 0.20])
    target_LMS = display.LMS_from_weights(baseline_weights)
    target_XYZ = display.XYZ_from_weights(baseline_weights)

    low_lms, high_lms = melanopic_silent_range(display, target_LMS, held="LMS")
    low_xyz, high_xyz = melanopic_silent_range(display, target_XYZ, held="XYZ")

    batch_weights = _batch_weights()
    batch_targets = display.LMS_from_weights(batch_weights)
    batch_low, batch_high = melanopic_silent_range(display, batch_targets, held="LMS")
    batch_baseline_mel = display.melanopic_from_weights(batch_weights)

    print("Synthetic RGBC melanopic silent substitution")
    print(f"Baseline weights: {baseline_weights}")
    print(f"Target LMS: {target_LMS}")
    print(f"Target XYZ: {target_XYZ}")
    _print_result("LMS-silent endpoints", low_lms, high_lms)
    _print_result("XYZ-silent endpoints", low_xyz, high_xyz)
    print("\nBatch LMS-silent shapes")
    print(f"batch_low.weights.shape: {batch_low.weights.shape}")
    print(f"batch_high.responses.shape: {batch_high.responses.shape}")
    print(f"Batch melanopic contrast range: {_melanopic_contrast(float(np.min(batch_low.melanopic)), float(np.max(batch_high.melanopic))):.6f}")

    with plot_style("presentation", font_scale=0.62, line_scale=0.85):
        fig, axes = plt.subplots(2, 3, figsize=(15.0, 8.0))
        plot_bars(
            [baseline_weights, low_lms.weights, high_lms.weights],
            labels=display.primary_names,
            group_labels=("Baseline", "Low mel", "High mel"),
            ax=axes[0, 0],
            title="LMS-silent weights",
            ylabel="Weight",
        )
        plot_bars(
            [baseline_weights, low_xyz.weights, high_xyz.weights],
            labels=display.primary_names,
            group_labels=("Baseline", "Low mel", "High mel"),
            ax=axes[0, 1],
            title="XYZ-silent weights",
            ylabel="Weight",
        )

        baseline_mel = float(display.melanopic_from_weights(baseline_weights))
        plot_bars(
            [
                [float(low_lms.melanopic), baseline_mel, float(high_lms.melanopic)],
                [float(low_xyz.melanopic), baseline_mel, float(high_xyz.melanopic)],
            ],
            labels=("Low", "Baseline", "High"),
            group_labels=("LMS held", "XYZ held"),
            ax=axes[0, 2],
            title="Melanopic endpoints",
            ylabel="Mel response",
        )
        axes[0, 2].text(
            0.02,
            0.95,
            "contrast\n"
            f"LMS { _melanopic_contrast(float(low_lms.melanopic), float(high_lms.melanopic)):.3f}\n"
            f"XYZ { _melanopic_contrast(float(low_xyz.melanopic), float(high_xyz.melanopic)):.3f}",
            transform=axes[0, 2].transAxes,
            va="top",
            fontsize=8,
        )

        lms_low = display.LMS_from_weights(low_lms.weights)
        lms_high = display.LMS_from_weights(high_lms.weights)
        plot_bars(
            [target_LMS, lms_low, lms_high],
            labels=("L", "M", "S"),
            group_labels=("Target", "Low mel", "High mel"),
            ax=axes[1, 0],
            title="Held LMS responses",
            ylabel="Response",
        )
        _add_residual_text(axes[1, 0], low_lms, high_lms)

        xyz_low = display.XYZ_from_weights(low_xyz.weights)
        xyz_high = display.XYZ_from_weights(high_xyz.weights)
        plot_bars(
            [target_XYZ, xyz_low, xyz_high],
            labels=("X", "Y", "Z"),
            group_labels=("Target", "Low mel", "High mel"),
            ax=axes[1, 1],
            title="Held XYZ responses",
            ylabel="Response",
        )
        _add_residual_text(axes[1, 1], low_xyz, high_xyz)

        index = np.arange(batch_weights.shape[0])
        plot_lines(
            [
                (index, np.asarray(batch_low.melanopic)),
                (index, np.asarray(batch_baseline_mel)),
                (index, np.asarray(batch_high.melanopic)),
            ],
            labels=("Low mel", "Baseline", "High mel"),
            linestyles=("-", "--", "-"),
            ax=axes[1, 2],
            title="Batch LMS-silent melanopic range",
            xlabel="Baseline index",
            ylabel="Mel response",
        )
        axes[1, 2].fill_between(
            index,
            np.asarray(batch_low.melanopic),
            np.asarray(batch_high.melanopic),
            alpha=0.16,
        )
        style_2d_axis(axes[1, 2], grid=True)

        fig.tight_layout()
        output = OUTPUT_DIR / "01_melanopic_silent_substitution.png"
        fig.savefig(output, dpi=160)
        plt.close(fig)
    print(f"Plot saved to {output}")


if __name__ == "__main__":
    main()
