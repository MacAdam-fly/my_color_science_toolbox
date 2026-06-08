"""Tests for spectral IO helpers."""

from __future__ import annotations

import numpy as np
import pytest

from color.io import (
    read_spectral_csv,
    read_spectral_excel,
    read_spectral_json,
    spectral_from_dataframe,
    spectral_to_dataframe,
    write_spectral_csv,
    write_spectral_excel,
    write_spectral_json,
)
from color.spectra import MultiSpectralDistribution, SpectralDistribution


def _single() -> SpectralDistribution:
    return SpectralDistribution(
        [400.0, 500.0, 600.0],
        [0.1, 0.8, 0.2],
        name="single",
        metadata={"source": "test"},
    )


def _multi() -> MultiSpectralDistribution:
    return MultiSpectralDistribution(
        [400.0, 500.0, 600.0],
        [[0.1, 0.0], [0.8, 0.4], [0.2, 0.9]],
        ("A", "B"),
        name="multi",
        metadata={"source": "test"},
    )


def test_spectral_to_dataframe_and_from_dataframe_single() -> None:
    spectral = _single()
    frame = spectral_to_dataframe(spectral)

    result = spectral_from_dataframe(frame, name="roundtrip")

    assert isinstance(result, SpectralDistribution)
    assert result.name == "roundtrip"
    assert np.allclose(result.wavelengths, spectral.wavelengths)
    assert np.allclose(result.values, spectral.values)


def test_spectral_to_dataframe_and_from_dataframe_multi() -> None:
    spectral = _multi()
    frame = spectral_to_dataframe(spectral)

    result = spectral_from_dataframe(frame)

    assert isinstance(result, MultiSpectralDistribution)
    assert result.labels == spectral.labels
    assert np.allclose(result.wavelengths, spectral.wavelengths)
    assert np.allclose(result.values, spectral.values)


def test_csv_roundtrip_single(tmp_path) -> None:
    spectral = _single()
    path = write_spectral_csv(tmp_path / "single.csv", spectral)

    result = read_spectral_csv(path)

    assert path.exists()
    assert isinstance(result, SpectralDistribution)
    assert np.allclose(result.wavelengths, spectral.wavelengths)
    assert np.allclose(result.values, spectral.values)


def test_csv_roundtrip_multi(tmp_path) -> None:
    spectral = _multi()
    path = write_spectral_csv(tmp_path / "multi.csv", spectral)

    result = read_spectral_csv(path, ys=("A", "B"))

    assert isinstance(result, MultiSpectralDistribution)
    assert result.labels == spectral.labels
    assert np.allclose(result.values, spectral.values)


def test_excel_roundtrip_multi(tmp_path) -> None:
    spectral = _multi()
    path = write_spectral_excel(tmp_path / "multi.xlsx", spectral)

    result = read_spectral_excel(path, sheet_name="spectra")

    assert isinstance(result, MultiSpectralDistribution)
    assert result.labels == spectral.labels
    assert np.allclose(result.values, spectral.values)


def test_json_roundtrip_single_preserves_metadata(tmp_path) -> None:
    spectral = _single()
    path = write_spectral_json(tmp_path / "single.json", spectral)

    result = read_spectral_json(path)

    assert isinstance(result, SpectralDistribution)
    assert result.name == spectral.name
    assert result.metadata == spectral.metadata
    assert np.allclose(result.values, spectral.values)


def test_json_roundtrip_multi_preserves_labels(tmp_path) -> None:
    spectral = _multi()
    path = write_spectral_json(tmp_path / "multi.json", spectral)

    result = read_spectral_json(path)

    assert isinstance(result, MultiSpectralDistribution)
    assert result.name == spectral.name
    assert result.labels == spectral.labels
    assert np.allclose(result.values, spectral.values)


def test_spectral_from_dataframe_rejects_ambiguous_channel_selection() -> None:
    frame = spectral_to_dataframe(_multi())

    with pytest.raises(ValueError, match="either y or ys"):
        spectral_from_dataframe(frame, y="A", ys=("A", "B"))


def test_spectral_from_dataframe_rejects_missing_wavelength() -> None:
    frame = spectral_to_dataframe(_single()).drop(columns=["wavelength"])

    with pytest.raises(ValueError, match="missing wavelength"):
        spectral_from_dataframe(frame)
