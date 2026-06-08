"""Image file readers and writers."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np


def _as_srgb_image_array(image: Any, *, name: str = "image") -> np.ndarray:
    array = np.asarray(image, dtype=np.float64)
    if array.ndim != 3 or array.shape[-1] != 3:
        raise ValueError(f"{name} must have shape (height, width, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def read_sRGB_image(
    path: str | PathLike[str],
    *,
    apply_exif: bool = True,
) -> np.ndarray:
    """Read an image as encoded sRGB float values in ``[0, 1]``."""
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("Pillow is required for read_sRGB_image()") from exc

    image = Image.open(path)
    if apply_exif:
        image = ImageOps.exif_transpose(image)
    rgb = image.convert("RGB")
    return np.asarray(rgb, dtype=np.float64) / 255.0


def write_sRGB_image(
    path: str | PathLike[str],
    image: Any,
    *,
    clip: bool = True,
    quality: int = 95,
    **save_kwargs: Any,
) -> Path:
    """Write encoded sRGB float values to an 8-bit image file."""
    try:
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("Pillow is required for write_sRGB_image()") from exc

    array = _as_srgb_image_array(image)
    if clip:
        array = np.clip(array, 0.0, 1.0)
    elif np.any((array < 0.0) | (array > 1.0)):
        raise ValueError("image values must be in [0, 1] when clip=False")

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image_u8 = np.round(array * 255.0).astype(np.uint8)
    pil_image = Image.fromarray(image_u8)
    pil_image.save(output, quality=quality, **save_kwargs)
    return output


__all__ = ["read_sRGB_image", "write_sRGB_image"]
