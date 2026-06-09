"""Tests for image IO helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.io import read_image, read_sRGB_image, write_image, write_sRGB_image


def test_read_image_can_keep_integer_codes(tmp_path) -> None:
    image = np.array(
        [
            [[0, 64, 128], [192, 255, 25]],
            [[51, 102, 153], [204, 76, 0]],
        ],
        dtype=np.uint8,
    )

    path = write_image(tmp_path / "codes.png", image)
    result = read_image(path, as_float=False)

    assert path.exists()
    assert result.dtype == np.uint8
    assert np.array_equal(result, image)


def test_read_image_normalises_integer_codes(tmp_path) -> None:
    image = np.array([[[0, 128, 255]]], dtype=np.uint8)

    path = write_image(tmp_path / "normalised.png", image)
    result = read_image(path)

    assert result.dtype == np.float64
    assert np.allclose(result[0, 0], [0.0, 128.0 / 255.0, 1.0])


def test_write_image_can_quantise_float_to_16_bit_grayscale(tmp_path) -> None:
    image = np.array([[0.0, 0.5, 1.0]], dtype=np.float64)

    path = write_image(tmp_path / "gray16.tiff", image, bit_depth=16)
    result = read_image(path, as_float=False)

    assert result.dtype == np.uint16
    assert np.array_equal(result, np.array([[0, 32768, 65535]], dtype=np.uint16))


def test_srgb_image_roundtrip_png(tmp_path) -> None:
    image = np.array(
        [
            [[0.0, 0.25, 0.5], [0.75, 1.0, 0.1]],
            [[0.2, 0.4, 0.6], [0.8, 0.3, 0.0]],
        ],
        dtype=np.float64,
    )

    path = write_sRGB_image(tmp_path / "image.png", image)
    result = read_sRGB_image(path)

    assert path.exists()
    assert result.shape == image.shape
    assert np.allclose(result, image, atol=0.5 / 255.0)


def test_write_srgb_image_clips_by_default(tmp_path) -> None:
    image = np.array([[[1.2, -0.1, 0.5]]], dtype=np.float64)

    path = write_sRGB_image(tmp_path / "clipped.png", image)
    result = read_sRGB_image(path)

    assert np.allclose(result[0, 0], [1.0, 0.0, 0.5], atol=0.5 / 255.0)


def test_write_srgb_image_can_reject_out_of_range_values(tmp_path) -> None:
    image = np.array([[[1.2, 0.0, 0.5]]], dtype=np.float64)

    with pytest.raises(ValueError, match=r"\[0, 1\]"):
        write_sRGB_image(tmp_path / "invalid.png", image, clip=False)


def test_write_srgb_image_rejects_invalid_shape(tmp_path) -> None:
    with pytest.raises(ValueError, match="shape"):
        write_sRGB_image(tmp_path / "invalid.png", np.zeros((2, 2)))


def test_write_srgb_image_rejects_non_finite_values(tmp_path) -> None:
    image = np.array([[[np.nan, 0.0, 0.5]]], dtype=np.float64)

    with pytest.raises(ValueError, match="finite"):
        write_sRGB_image(tmp_path / "invalid.png", image)
