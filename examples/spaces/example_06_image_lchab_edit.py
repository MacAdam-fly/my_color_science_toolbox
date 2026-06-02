"""Apply an LCHab lightness/chroma edit to an sRGB image."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

from color.constants import D65_XYZ
from color.plot import plot_image
from color.spaces import SpaceSpec, convert_color

from _spaces_plot_helpers import output_dir


INPUT_PATH = Path(__file__).resolve().parent / "input_test_img" / "img1.jpg"
LIGHTNESS_FACTOR = 1.2
CHROMA_FACTOR = 1.2


def _read_srgb_image(path: Path) -> np.ndarray:
    """Read an image as encoded sRGB float values in [0, 1]."""
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return np.asarray(image, dtype=np.float64) / 255.0


def _write_srgb_jpg(path: Path, image: np.ndarray) -> None:
    """Write encoded sRGB float values as an 8-bit JPEG image."""
    encoded = np.clip(image, 0.0, 1.0)
    data = np.round(encoded * 255.0).astype(np.uint8)
    Image.fromarray(data).save(path, quality=95, subsampling=0)


def _boost_lchab(sRGB: np.ndarray) -> tuple[np.ndarray, dict[str, float]]:
    """Boost L* and C_ab in LCHab(D65), then convert back to sRGB."""
    lchab_spec = SpaceSpec("LCHab", whitepoint_XYZ=D65_XYZ)
    lchab = convert_color(sRGB, "sRGB", lchab_spec)
    edited_lchab = np.array(lchab, copy=True)

    raw_lightness = edited_lchab[..., 0] * LIGHTNESS_FACTOR
    edited_lchab[..., 0] = np.clip(raw_lightness, 0.0, 100.0)
    edited_lchab[..., 1] = np.maximum(edited_lchab[..., 1] * CHROMA_FACTOR, 0.0)

    edited_sRGB = convert_color(edited_lchab, lchab_spec, "sRGB")
    clipped_sRGB = np.clip(edited_sRGB, 0.0, 1.0)

    stats = {
        "lightness_clipped_percent": float(np.mean(raw_lightness > 100.0) * 100.0),
        "rgb_channel_clipped_percent": float(
            np.mean((edited_sRGB < 0.0) | (edited_sRGB > 1.0)) * 100.0
        ),
        "mean_L_before": float(np.mean(lchab[..., 0])),
        "mean_L_after": float(np.mean(edited_lchab[..., 0])),
        "mean_C_before": float(np.mean(lchab[..., 1])),
        "mean_C_after": float(np.mean(edited_lchab[..., 1])),
    }
    return clipped_sRGB, stats


def _save_comparison_plot(original: np.ndarray, edited: np.ndarray, out: Path) -> None:
    """Save a side-by-side comparison figure."""
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.0))
    for ax, image, title in (
        (axes[0], original, "Original sRGB"),
        (axes[1], edited, "LCHab edit: L* x1.2, C x1.2"),
    ):
        plot_image(
            np.clip(image, 0.0, 1.0),
            ax=ax,
            title=title,
            show_ticks=False,
            aspect="equal",
        )
    fig.tight_layout()
    path = out / "06_image_lchab_boost_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Comparison plot saved to {path}")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"input image not found: {INPUT_PATH}")

    out = output_dir()
    sRGB = _read_srgb_image(INPUT_PATH)
    edited_sRGB, stats = _boost_lchab(sRGB)

    output_path = out / "06_image_lchab_boost.jpg"
    _write_srgb_jpg(output_path, edited_sRGB)
    _save_comparison_plot(sRGB, edited_sRGB, out)

    print("Image LCHab edit")
    print(f"Input:  {INPUT_PATH}")
    print(f"Output: {output_path}")
    print(f"Image shape: {sRGB.shape}")
    print(f"L* factor: {LIGHTNESS_FACTOR}")
    print(f"C_ab factor: {CHROMA_FACTOR}")
    print(f"Mean L*: {stats['mean_L_before']:.3f} -> {stats['mean_L_after']:.3f}")
    print(f"Mean C_ab: {stats['mean_C_before']:.3f} -> {stats['mean_C_after']:.3f}")
    print(f"L* values clipped at 100: {stats['lightness_clipped_percent']:.3f}%")
    print(f"sRGB channels clipped after conversion: {stats['rgb_channel_clipped_percent']:.3f}%")


if __name__ == "__main__":
    main()
