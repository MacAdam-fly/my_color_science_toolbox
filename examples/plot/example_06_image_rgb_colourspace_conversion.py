"""Compare an sRGB image with its Rec.2020 encoded RGB representation."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageOps

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.plot import plot_image, plot_style
from color.spaces import RGB_to_RGB


INPUT_PATH = Path(__file__).resolve().parent / "input_test_img" / "img1.jpg"


def _output_dir() -> Path:
    path = Path(__file__).resolve().parent / "output"
    path.mkdir(exist_ok=True)
    return path


def _read_srgb_image(path: Path) -> np.ndarray:
    """Read an image as encoded sRGB float values in [0, 1]."""
    image = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    return np.asarray(image, dtype=np.float64) / 255.0


def _write_preview_jpg(path: Path, image: np.ndarray) -> None:
    """Write clipped encoded RGB values as an 8-bit JPEG preview."""
    data = np.round(np.clip(image, 0.0, 1.0) * 255.0).astype(np.uint8)
    Image.fromarray(data).save(path, quality=95, subsampling=0)


def _save_comparison(original_srgb: np.ndarray, rec2020_rgb: np.ndarray, out: Path) -> None:
    """Save a side-by-side image comparison."""
    with plot_style("presentation", font_scale=0.75, line_scale=0.9):
        fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.0))
        plot_image(
            original_srgb,
            ax=axes[0],
            title="Original encoded sRGB",
            show_ticks=False,
        )
        plot_image(
            rec2020_rgb,
            ax=axes[1],
            title="Encoded Rec.2020 values as RGB preview",
            show_ticks=False,
        )
    path = out / "06_srgb_to_rec2020_image_comparison.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Comparison plot saved to {path}")


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"input image not found: {INPUT_PATH}")

    out = _output_dir()
    sRGB = _read_srgb_image(INPUT_PATH)
    rec2020 = RGB_to_RGB(sRGB, "sRGB", "Rec.2020")
    recovered_sRGB = RGB_to_RGB(rec2020, "Rec.2020", "sRGB")

    rec2020_preview_path = out / "06_rec2020_encoded_preview.jpg"
    _write_preview_jpg(rec2020_preview_path, rec2020)
    _save_comparison(sRGB, rec2020, out)

    print("Image RGB colourspace conversion")
    print(f"Input:  {INPUT_PATH}")
    print(f"Rec.2020 encoded preview: {rec2020_preview_path}")
    print(f"Image shape: {sRGB.shape}")
    print(f"Rec.2020 encoded value range: {np.min(rec2020):.6f} to {np.max(rec2020):.6f}")
    print(f"Rec.2020 channel clipping needed for preview: {np.mean((rec2020 < 0.0) | (rec2020 > 1.0)) * 100:.4f}%")
    print(f"sRGB -> Rec.2020 -> sRGB max error: {np.max(np.abs(recovered_sRGB - sRGB)):.8f}")
    print("Note: the Rec.2020 image is an encoded-value preview, not a colour-managed Rec.2020 display rendering.")


if __name__ == "__main__":
    main()
