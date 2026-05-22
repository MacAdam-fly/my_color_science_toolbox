"""RGB transfer functions."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from color.utils.arrays import as_float_array


def _signed_power(value: np.ndarray, exponent: float) -> np.ndarray:
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
}


def decode_transfer(value, transfer: str) -> np.ndarray:
    """Decode encoded RGB values to linear RGB."""
    arr = as_float_array(value, name="RGB values")
    try:
        decode, _encode = _TRANSFER_FUNCTIONS[transfer]
    except KeyError as exc:
        raise ValueError(f"unknown RGB transfer function {transfer!r}") from exc
    return decode(arr)


def encode_transfer(value, transfer: str) -> np.ndarray:
    """Encode linear RGB values."""
    arr = as_float_array(value, name="RGB values")
    try:
        _decode, encode = _TRANSFER_FUNCTIONS[transfer]
    except KeyError as exc:
        raise ValueError(f"unknown RGB transfer function {transfer!r}") from exc
    return encode(arr)


def list_transfer_functions() -> tuple[str, ...]:
    """Return supported transfer function names."""
    return tuple(sorted(_TRANSFER_FUNCTIONS))


__all__ = [
    "decode_transfer",
    "encode_transfer",
    "list_transfer_functions",
]
