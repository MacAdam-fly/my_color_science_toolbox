"""Tests for Academy Spectral Similarity Index."""

from __future__ import annotations

import numpy as np
import pytest

from color.generators.blackbody import blackbody_spd
from color.generators.ideal import gaussian_spd
from color.quality import spectral_similarity_index
from color.quality.ssi import SPECTRAL_SHAPE_SSI
from color.spectra import SpectralDistribution, from_D65_illuminant, from_columns


def test_spectral_shape_ssi() -> None:
    assert SPECTRAL_SHAPE_SSI.start == 375.0
    assert SPECTRAL_SHAPE_SSI.end == 675.0
    assert SPECTRAL_SHAPE_SSI.interval == 1.0
    assert len(SPECTRAL_SHAPE_SSI) == 301


def test_d65_against_itself_is_100() -> None:
    d65 = from_D65_illuminant()
    assert spectral_similarity_index(d65, d65) == 100
    assert spectral_similarity_index(d65, d65, round_result=False) == pytest.approx(100.0)


def test_round_result_controls_rounding() -> None:
    d65 = from_D65_illuminant()
    gaussian = from_columns(
        gaussian_spd(peak_wavelength=555, width=45, method="fwhm"),
        y="spd",
    )

    rounded = spectral_similarity_index(gaussian, d65)
    unrounded = spectral_similarity_index(gaussian, d65, round_result=False)

    assert rounded == np.around(unrounded)
    assert rounded != unrounded


@pytest.mark.parametrize(
    ("test_sd", "expected_rounded", "expected_float"),
    [
        (
            from_columns(
                blackbody_spd(temperature=2856),
                y="radiance",
                name="Blackbody 2856 K",
            ),
            47.0,
            46.630366450061324,
        ),
        (
            from_columns(
                blackbody_spd(temperature=6500),
                y="radiance",
                name="Blackbody 6500 K",
            ),
            92.0,
            91.7811974366554,
        ),
        (
            from_columns(
                gaussian_spd(peak_wavelength=555, width=45, method="fwhm"),
                y="spd",
                name="Gaussian 555 nm",
            ),
            -46.0,
            -45.56900447332998,
        ),
    ],
)
def test_matches_reference_values(
    test_sd: SpectralDistribution,
    expected_rounded: float,
    expected_float: float,
) -> None:
    reference = from_D65_illuminant()

    result = spectral_similarity_index(test_sd, reference)
    assert result == pytest.approx(expected_rounded)

    result_float = spectral_similarity_index(test_sd, reference, round_result=False)
    assert result_float == pytest.approx(expected_float)


def test_rejects_non_spectral_distribution() -> None:
    d65 = from_D65_illuminant()
    with pytest.raises(TypeError):
        spectral_similarity_index({"wavelength": [400, 500]}, d65)  # type: ignore[arg-type]


def test_rejects_non_finite_values() -> None:
    bad = SpectralDistribution([400, 500], [1.0, np.inf])
    d65 = from_D65_illuminant()
    with pytest.raises(ValueError, match="values must be finite"):
        spectral_similarity_index(bad, d65)
