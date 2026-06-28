"""RGB transfer functions."""

from __future__ import annotations

from collections.abc import Callable
from typing import Tuple, Union

import numpy as np

from color.utils.arrays import as_float_array
from color.utils.names import canonical_method_name

RGBTransfer = Union[str, Tuple[str, Union[float, Tuple[float, float, float]]]]


def _signed_power(value: np.ndarray, exponent: float | np.ndarray) -> np.ndarray:
    """Apply a sign-preserving power function."""
    return np.sign(value) * np.abs(value) ** exponent


def _linear(value: np.ndarray) -> np.ndarray:
    return value


def _srgb_decode(value: np.ndarray) -> np.ndarray:
    magnitude = np.abs(value)
    decoded = np.where(
        magnitude <= 0.04045,
        magnitude / 12.92,
        ((magnitude + 0.055) / 1.055) ** 2.4,
    )
    return np.sign(value) * decoded


def _srgb_encode(value: np.ndarray) -> np.ndarray:
    magnitude = np.abs(value)
    encoded = np.where(
        magnitude <= 0.0031308,
        12.92 * magnitude,
        1.055 * magnitude ** (1.0 / 2.4) - 0.055,
    )
    return np.sign(value) * encoded


def _gamma_decode(exponent: float) -> Callable[[np.ndarray], np.ndarray]:
    def decode(value: np.ndarray) -> np.ndarray:
        return _signed_power(value, exponent)

    return decode


def _gamma_encode(exponent: float) -> Callable[[np.ndarray], np.ndarray]:
    def encode(value: np.ndarray) -> np.ndarray:
        return _signed_power(value, 1.0 / exponent)

    return encode


def _bt709_decode(value: np.ndarray) -> np.ndarray:
    magnitude = np.abs(value)
    decoded = np.where(
        magnitude < 0.081,
        magnitude / 4.5,
        ((magnitude + 0.099) / 1.099) ** (1.0 / 0.45),
    )
    return np.sign(value) * decoded


def _bt709_encode(value: np.ndarray) -> np.ndarray:
    magnitude = np.abs(value)
    encoded = np.where(
        magnitude < 0.018,
        4.5 * magnitude,
        1.099 * magnitude**0.45 - 0.099,
    )
    return np.sign(value) * encoded


_BT2020_ALPHA = 1.09929682680944
_BT2020_BETA = 0.018053968510807


def _bt2020_decode(value: np.ndarray) -> np.ndarray:
    magnitude = np.abs(value)
    threshold = 4.5 * _BT2020_BETA
    decoded = np.where(
        magnitude < threshold,
        magnitude / 4.5,
        ((magnitude + (_BT2020_ALPHA - 1.0)) / _BT2020_ALPHA) ** (1.0 / 0.45),
    )
    return np.sign(value) * decoded


def _bt2020_encode(value: np.ndarray) -> np.ndarray:
    magnitude = np.abs(value)
    encoded = np.where(
        magnitude < _BT2020_BETA,
        4.5 * magnitude,
        _BT2020_ALPHA * magnitude**0.45 - (_BT2020_ALPHA - 1.0),
    )
    return np.sign(value) * encoded


_ADOBE_RGB_GAMMA = 563.0 / 256.0
_PROPHOTO_RGB_EXPONENT = 1.8
_PROPHOTO_RGB_LINEAR_THRESHOLD = 1.0 / 512.0
_PROPHOTO_RGB_ENCODED_THRESHOLD = 16.0 / 512.0


def _prophoto_rgb_decode(value: np.ndarray) -> np.ndarray:
    decoded = np.empty_like(value, dtype=np.float64)
    low = value < _PROPHOTO_RGB_ENCODED_THRESHOLD
    decoded[low] = value[low] / 16.0
    decoded[~low] = value[~low] ** _PROPHOTO_RGB_EXPONENT
    return decoded


def _prophoto_rgb_encode(value: np.ndarray) -> np.ndarray:
    encoded = np.empty_like(value, dtype=np.float64)
    low = value < _PROPHOTO_RGB_LINEAR_THRESHOLD
    encoded[low] = 16.0 * value[low]
    encoded[~low] = value[~low] ** (1.0 / _PROPHOTO_RGB_EXPONENT)
    return encoded

_TRANSFER_FUNCTIONS: dict[str, tuple[Callable[[np.ndarray], np.ndarray], Callable[[np.ndarray], np.ndarray]]] = {
    "linear": (_linear, _linear),
    "srgb": (_srgb_decode, _srgb_encode),
    "gamma_2p6": (_gamma_decode(2.6), _gamma_encode(2.6)),
    "gamma_2p8": (_gamma_decode(2.8), _gamma_encode(2.8)),
    "adobe_rgb_1998": (
        _gamma_decode(_ADOBE_RGB_GAMMA),
        _gamma_encode(_ADOBE_RGB_GAMMA),
    ),
    "bt709": (_bt709_decode, _bt709_encode),
    "bt2020": (_bt2020_decode, _bt2020_encode),
    "prophoto_rgb": (_prophoto_rgb_decode, _prophoto_rgb_encode),
}

_TRANSFER_NAME_INDEX = {
    canonical_method_name(name): name for name in _TRANSFER_FUNCTIONS
}
_TRANSFER_NAME_INDEX.update(
    {
        canonical_method_name("ProPhoto RGB"): "prophoto_rgb",
        canonical_method_name("ROMM RGB"): "prophoto_rgb",
    }
)


def _gamma_exponents(exponent: float | tuple[float, ...] | list[float] | np.ndarray) -> float | tuple[float, float, float]:
    """Validate and normalise scalar or per-channel gamma exponents."""
    arr = np.asarray(exponent, dtype=np.float64)
    if arr.shape == ():
        value = float(arr)
        if not np.isfinite(value) or value <= 0:
            raise ValueError("gamma exponent must be finite and positive")
        return value

    if arr.shape != (3,):
        raise ValueError("per-channel gamma exponent must have 3 values")
    if not np.all(np.isfinite(arr)) or np.any(arr <= 0):
        raise ValueError("gamma exponents must be finite and positive")
    return tuple(float(value) for value in arr)


def normalize_transfer(transfer: RGBTransfer) -> RGBTransfer:
    """Return a validated transfer description.

    Named transfer functions are returned as their canonical string key.
    Dynamic gamma transfer functions are returned as ``("gamma", exponent)``.
    """
    if isinstance(transfer, str):
        key = canonical_method_name(transfer)
        try:
            return _TRANSFER_NAME_INDEX[key]
        except KeyError as exc:
            raise ValueError(f"unknown RGB transfer function {transfer!r}") from exc

    if not isinstance(transfer, tuple) or len(transfer) != 2:
        raise ValueError("RGB transfer must be a known name or ('gamma', exponent)")

    kind, exponent = transfer
    if canonical_method_name(kind) != "gamma":
        raise ValueError("only dynamic ('gamma', exponent) transfer tuples are supported")
    return ("gamma", _gamma_exponents(exponent))


def _dynamic_gamma_decode(value: np.ndarray, exponent: float | tuple[float, float, float]) -> np.ndarray:
    if isinstance(exponent, tuple):
        if value.shape[-1:] != (3,):
            raise ValueError("per-channel gamma transfer requires RGB values with last axis size 3")
        return _signed_power(value, np.asarray(exponent, dtype=np.float64))
    return _signed_power(value, exponent)


def _dynamic_gamma_encode(value: np.ndarray, exponent: float | tuple[float, float, float]) -> np.ndarray:
    if isinstance(exponent, tuple):
        if value.shape[-1:] != (3,):
            raise ValueError("per-channel gamma transfer requires RGB values with last axis size 3")
        return _signed_power(value, 1.0 / np.asarray(exponent, dtype=np.float64))
    return _signed_power(value, 1.0 / exponent)


def decode_transfer(value, transfer: RGBTransfer) -> np.ndarray:
    """Decode encoded RGB values to linear RGB."""
    arr = as_float_array(value, name="RGB values")
    transfer = normalize_transfer(transfer)
    if isinstance(transfer, tuple):
        return _dynamic_gamma_decode(arr, transfer[1])
    decode, _encode = _TRANSFER_FUNCTIONS[transfer]
    return decode(arr)


def encode_transfer(value, transfer: RGBTransfer) -> np.ndarray:
    """Encode linear RGB values."""
    arr = as_float_array(value, name="RGB values")
    transfer = normalize_transfer(transfer)
    if isinstance(transfer, tuple):
        return _dynamic_gamma_encode(arr, transfer[1])
    _decode, encode = _TRANSFER_FUNCTIONS[transfer]
    return encode(arr)


def list_transfer_functions() -> tuple[str, ...]:
    """Return supported transfer function names."""
    return tuple(sorted(_TRANSFER_FUNCTIONS))


__all__ = [
    "decode_transfer",
    "encode_transfer",
    "list_transfer_functions",
    "normalize_transfer",
]
