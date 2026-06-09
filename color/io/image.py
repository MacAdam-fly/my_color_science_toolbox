"""Image file readers and writers."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any

import numpy as np


def _validate_image_shape(array: np.ndarray, *, name: str = "image") -> np.ndarray:
    if array.ndim == 2:
        return array
    if array.ndim == 3 and array.shape[-1] in (1, 3, 4):
        if array.shape[-1] == 1:
            return array[..., 0]
        return array
    raise ValueError(
        f"{name} must have shape (height, width), "
        "(height, width, 1), (height, width, 3), or (height, width, 4)"
    )


def _normalise_image_array(
    array: np.ndarray,
    *,
    dtype: Any | None = None,
) -> np.ndarray:
    target_dtype = np.float64 if dtype is None else dtype
    if np.issubdtype(array.dtype, np.bool_):
        return array.astype(target_dtype)
    if np.issubdtype(array.dtype, np.integer):
        info = np.iinfo(array.dtype)
        return (array.astype(target_dtype) / float(info.max)).astype(target_dtype)
    if np.issubdtype(array.dtype, np.floating):
        if not np.all(np.isfinite(array)):
            raise ValueError("image must contain only finite values")
        return array.astype(target_dtype)
    raise ValueError(f"unsupported image dtype {array.dtype}")


def _quantise_float_image(
    array: np.ndarray,
    *,
    bit_depth: int,
    clip: bool,
) -> np.ndarray:
    if bit_depth not in (8, 16):
        raise ValueError("bit_depth must be 8, 16, or None")
    if not np.all(np.isfinite(array)):
        raise ValueError("image must contain only finite values")
    if clip:
        array = np.clip(array, 0.0, 1.0)
    elif np.any((array < 0.0) | (array > 1.0)):
        raise ValueError("floating image values must be in [0, 1] when clip=False")

    max_value = (1 << bit_depth) - 1
    dtype = np.uint8 if bit_depth == 8 else np.uint16
    return np.round(array * float(max_value)).astype(dtype)


def _prepare_image_for_write(
    image: Any,
    *,
    bit_depth: int | None,
    clip: bool,
) -> np.ndarray:
    array = _validate_image_shape(np.asarray(image))
    if np.issubdtype(array.dtype, np.floating):
        target_bit_depth = 8 if bit_depth is None else bit_depth
        return _quantise_float_image(array.astype(np.float64), bit_depth=target_bit_depth, clip=clip)

    if np.issubdtype(array.dtype, np.bool_):
        return _quantise_float_image(array.astype(np.float64), bit_depth=8 if bit_depth is None else bit_depth, clip=True)

    if not np.issubdtype(array.dtype, np.integer):
        raise ValueError(f"unsupported image dtype {array.dtype}")

    if np.issubdtype(array.dtype, np.signedinteger) and np.any(array < 0):
        raise ValueError("integer image values must be non-negative")

    if bit_depth is None:
        return np.array(array, copy=True)
    if bit_depth not in (8, 16):
        raise ValueError("bit_depth must be 8, 16, or None")

    max_value = (1 << bit_depth) - 1
    if clip:
        array = np.clip(array, 0, max_value)
    elif np.any(array > max_value):
        raise ValueError(f"integer image values exceed {bit_depth}-bit range")
    dtype = np.uint8 if bit_depth == 8 else np.uint16
    return array.astype(dtype)


def _as_srgb_image_array(image: Any, *, name: str = "image") -> np.ndarray:
    array = np.asarray(image, dtype=np.float64)
    if array.ndim != 3 or array.shape[-1] != 3:
        raise ValueError(f"{name} must have shape (height, width, 3)")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def read_image(
    path: str | PathLike[str],
    *,
    mode: str | None = None,
    apply_exif: bool = True,
    as_float: bool = True,
    dtype: Any | None = None,
) -> np.ndarray:
    """Read an image as a NumPy array.

    Integer images are normalised to ``[0, 1]`` when ``as_float=True``.  Set
    ``as_float=False`` to keep the stored integer codes.
    """
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("Pillow is required for read_image()") from exc

    image = Image.open(path)
    if apply_exif:
        image = ImageOps.exif_transpose(image)
    if mode is not None:
        image = image.convert(mode)
    array = _validate_image_shape(np.asarray(image))
    if as_float:
        return _normalise_image_array(array, dtype=dtype)
    if dtype is not None:
        return array.astype(dtype)
    return np.array(array, copy=True)


def write_image(
    path: str | PathLike[str],
    image: Any,
    *,
    bit_depth: int | None = None,
    clip: bool = True,
    quality: int | None = None,
    **write_kwargs: Any,
) -> Path:
    """Write a NumPy image array to disk.

    Floating images are interpreted as normalised ``[0, 1]`` values and are
    quantised to 8-bit by default. Integer images keep their dtype when
    ``bit_depth=None``.
    """
    try:
        import imageio.v3 as iio
    except ImportError as exc:  # pragma: no cover - depends on environment.
        raise ImportError("imageio is required for write_image()") from exc

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    array = _prepare_image_for_write(image, bit_depth=bit_depth, clip=clip)
    if quality is not None:
        write_kwargs.setdefault("quality", quality)
    iio.imwrite(output, array, **write_kwargs)
    return output


def read_sRGB_image(
    path: str | PathLike[str],
    *,
    apply_exif: bool = True,
) -> np.ndarray:
    """Read an image as encoded sRGB float values in ``[0, 1]``."""
    return read_image(path, mode="RGB", apply_exif=apply_exif, as_float=True)


def write_sRGB_image(
    path: str | PathLike[str],
    image: Any,
    *,
    clip: bool = True,
    quality: int = 95,
    **save_kwargs: Any,
) -> Path:
    """Write encoded sRGB float values to an 8-bit image file."""
    array = _as_srgb_image_array(image)
    output = Path(path)
    if output.suffix.lower() in {".jpg", ".jpeg"}:
        save_kwargs.setdefault("quality", quality)
    return write_image(output, array, bit_depth=8, clip=clip, **save_kwargs)


__all__ = ["read_image", "write_image", "read_sRGB_image", "write_sRGB_image"]
