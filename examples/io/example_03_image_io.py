"""Read, edit and write images with color.io."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.constants import D65_XYZ
from color.io import read_image, read_sRGB_image, save_figure, write_sRGB_image
from color.plot import plot_image, plot_style
from color.spaces import SpaceSpec, convert_color


INPUT_PATH = Path(__file__).resolve().parent / "input_image" / "test_img1.jpg"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
LIGHTNESS_FACTOR = 1.4


def _boost_lab_lightness(srgb: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    lab_spec = SpaceSpec("Lab", whitepoint_XYZ=D65_XYZ)
    lab = convert_color(srgb, "sRGB", lab_spec)
    edited_lab = np.array(lab, copy=True)

    raw_lightness = edited_lab[..., 0] * LIGHTNESS_FACTOR
    edited_lab[..., 0] = np.clip(raw_lightness, 0.0, 100.0)
    edited_srgb = convert_color(edited_lab, lab_spec, "sRGB")
    clipped_srgb = np.clip(edited_srgb, 0.0, 1.0)

    stats = {
        "mean_L_before": float(np.mean(lab[..., 0])),
        "mean_L_after": float(np.mean(edited_lab[..., 0])),
        "L_clipped_percent": float(np.mean(raw_lightness > 100.0) * 100.0),
        "rgb_clipped_percent": float(
            np.mean((edited_srgb < 0.0) | (edited_srgb > 1.0)) * 100.0
        ),
    }
    return clipped_srgb, stats


def _save_comparison(original: np.ndarray, edited: np.ndarray) -> Path:
    with plot_style("presentation", font_scale=0.72, line_scale=0.9):
        fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.1))
        plot_image(
            original,
            ax=axes[0],
            title="Original encoded sRGB",
            show_ticks=False,
            aspect="equal",
        )
        plot_image(
            edited,
            ax=axes[1],
            title=f"Lab(D65): L* x{LIGHTNESS_FACTOR}",
            show_ticks=False,
            aspect="equal",
        )
        fig.tight_layout()

    output_path = save_figure(
        OUTPUT_DIR / "03_image_lab_lightness_comparison.png",
        fig=fig,
        dpi=160,
        close=True,
    )
    return output_path


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"input image not found: {INPUT_PATH}")

    OUTPUT_DIR.mkdir(exist_ok=True)

    image_codes = read_image(INPUT_PATH, mode="RGB", as_float=False)
    image_float = read_image(INPUT_PATH, mode="RGB")
    srgb = read_sRGB_image(INPUT_PATH)
    edited_srgb, stats = _boost_lab_lightness(srgb)

    edited_path = write_sRGB_image(
        OUTPUT_DIR / "03_image_lab_lightness_x1p2.jpg",
        edited_srgb,
        quality=95,
        subsampling=0,
    )
    comparison_path = _save_comparison(srgb, edited_srgb)

    print("Image IO example")
    print(f"Input: {INPUT_PATH}")
    print(f"read_image(..., as_float=False): dtype={image_codes.dtype}, shape={image_codes.shape}")
    print(f"read_image(...): dtype={image_float.dtype}, range={image_float.min():.4f}-{image_float.max():.4f}")
    print(f"read_sRGB_image(...): dtype={srgb.dtype}, shape={srgb.shape}")
    print(f"Mean L*: {stats['mean_L_before']:.3f} -> {stats['mean_L_after']:.3f}")
    print(f"L* clipped at 100: {stats['L_clipped_percent']:.3f}%")
    print(f"sRGB channels clipped after Lab edit: {stats['rgb_clipped_percent']:.3f}%")
    print(f"Edited image: {edited_path}")
    print(f"Comparison figure: {comparison_path}")


if __name__ == "__main__":
    main()
