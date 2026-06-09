"""Tests for Stockman/Rider individual cone fundamentals."""

from __future__ import annotations

import numpy as np
import pytest

from color.datasets.standard_observers import (
    get_cie2006_lms_2degree_fundamentals,
    get_cie2006_lms_10degree_fundamentals,
)
from color.individual_cone_fundamentals import (
    asano2016_model_components,
    generate_asano2016_individual_cone_fundamentals,
    generate_stockman_rider_2023_individual_cone_fundamentals,
    stockman_rider_2023_model_components,
)
from color.individual_cone_fundamentals.stockman_rider_2023 import (
    cone_absorbance_spectra,
    lens_density_spectrum,
    macular_density_spectrum,
)


def _stack(raw):
    return np.column_stack((raw["l"], raw["m"], raw["s"]))


EXPECTED_COMPONENT_KEYS = {
    "wavelength",
    "photopigment_absorbance",
    "photopigment_od",
    "retinal_absorptance",
    "macular_density",
    "lens_density",
    "prereceptoral_density",
    "corneal_quantal",
    "corneal_energy",
}


def _assert_component_shapes(components, n_wavelengths):
    assert set(components) == EXPECTED_COMPONENT_KEYS
    assert components["wavelength"].shape == (n_wavelengths,)
    for key in (
        "photopigment_absorbance",
        "retinal_absorptance",
        "corneal_quantal",
        "corneal_energy",
    ):
        assert components[key].shape == (n_wavelengths, 3)
        assert np.isfinite(components[key]).all()
    assert components["photopigment_od"].shape == (3,)
    assert np.isfinite(components["photopigment_od"]).all()
    for key in ("macular_density", "lens_density", "prereceptoral_density"):
        assert components[key].shape == (n_wavelengths,)
        assert np.isfinite(components[key]).all()


def test_macular_and_lens_templates_are_standard_scaled():
    macular = macular_density_spectrum(np.array([460.0]))
    lens = lens_density_spectrum(np.array([400.0]))
    np.testing.assert_allclose(macular["optical_density"], [0.350], atol=5e-5)
    np.testing.assert_allclose(lens["optical_density"], [1.7649], atol=5e-5)


def test_top_level_api_excludes_stockman_rider_intermediate_templates():
    import color.individual_cone_fundamentals as icf

    assert "macular_density_spectrum" not in icf.__all__
    assert "lens_density_spectrum" not in icf.__all__
    assert "cone_absorbance_spectra" not in icf.__all__


def test_top_level_api_includes_model_components():
    import color.individual_cone_fundamentals as icf

    assert "stockman_rider_2023_model_components" in icf.__all__
    assert "asano2016_model_components" in icf.__all__


def test_cone_absorbance_templates_peak_at_one():
    raw = cone_absorbance_spectra()
    values = _stack(raw)
    np.testing.assert_allclose(values.max(axis=0), [1.0, 1.0, 1.0], atol=1e-12)
    assert set(raw) == {"wavelength", "l", "m", "s"}


def test_generate_standard_observers_shape_and_normalisation():
    for observer_degree in (2, 10):
        raw = generate_stockman_rider_2023_individual_cone_fundamentals(
            observer_degree=observer_degree
        )
        values = _stack(raw)
        assert raw["wavelength"].shape == (491,)
        assert values.shape == (491, 3)
        assert np.isfinite(values).all()
        np.testing.assert_allclose(values.max(axis=0), [1.0, 1.0, 1.0])


def test_stockman_rider_components_match_final_lms():
    components = stockman_rider_2023_model_components(
        l_shift_nm=2.0,
        m_shift_nm=-1.0,
        photopigment_od=(0.45, 0.52, 0.38),
        macular_density_460=0.5,
        lens_density_400=1.5,
    )
    raw = generate_stockman_rider_2023_individual_cone_fundamentals(
        l_shift_nm=2.0,
        m_shift_nm=-1.0,
        photopigment_od=(0.45, 0.52, 0.38),
        macular_density_460=0.5,
        lens_density_400=1.5,
    )
    _assert_component_shapes(components, 491)
    np.testing.assert_allclose(components["corneal_energy"], _stack(raw))


def test_stockman_rider_components_reflect_individual_density_parameters():
    standard = stockman_rider_2023_model_components()
    dense = stockman_rider_2023_model_components(
        macular_density_460=0.5,
        lens_density_400=1.5,
    )
    assert not np.allclose(standard["macular_density"], dense["macular_density"])
    assert not np.allclose(standard["lens_density"], dense["lens_density"])


def test_generated_2degree_matches_cie2006_linear_energy():
    generated = generate_stockman_rider_2023_individual_cone_fundamentals(
        observer_degree=2
    )
    reference = get_cie2006_lms_2degree_fundamentals(interval_nm=1, energy="linE")
    mask = (generated["wavelength"] >= 400) & (generated["wavelength"] <= 830)
    values = _stack({key: value[mask] for key, value in generated.items()})
    ref_mask = (reference["wavelength"] >= 400) & (reference["wavelength"] <= 830)
    ref_values = _stack({key: value[ref_mask] for key, value in reference.items()})
    finite = np.isfinite(ref_values)
    np.testing.assert_allclose(values[finite], ref_values[finite], atol=2.0e-2)
    assert np.mean(np.abs(values[finite] - ref_values[finite])) < 2.5e-3


def test_generated_10degree_matches_cie2006_linear_energy():
    generated = generate_stockman_rider_2023_individual_cone_fundamentals(
        observer_degree=10
    )
    reference = get_cie2006_lms_10degree_fundamentals(interval_nm=1, energy="linE")
    mask = (generated["wavelength"] >= 400) & (generated["wavelength"] <= 830)
    values = _stack({key: value[mask] for key, value in generated.items()})
    ref_mask = (reference["wavelength"] >= 400) & (reference["wavelength"] <= 830)
    ref_values = _stack({key: value[ref_mask] for key, value in reference.items()})
    finite = np.isfinite(ref_values)
    np.testing.assert_allclose(values[finite], ref_values[finite], atol=2.0e-2)
    assert np.mean(np.abs(values[finite] - ref_values[finite])) < 2.5e-3


def test_individual_parameters_change_result():
    standard = generate_stockman_rider_2023_individual_cone_fundamentals()
    shifted = generate_stockman_rider_2023_individual_cone_fundamentals(
        l_shift_nm=2.0,
        m_shift_nm=-1.0,
        photopigment_od=(0.45, 0.52, 0.38),
        macular_density_460=0.5,
        lens_density_400=1.5,
    )
    assert not np.allclose(_stack(standard), _stack(shifted))


def test_l_template_options_are_available():
    ser = generate_stockman_rider_2023_individual_cone_fundamentals(l_template="ser180")
    ala = generate_stockman_rider_2023_individual_cone_fundamentals(l_template="ala180")
    mean = generate_stockman_rider_2023_individual_cone_fundamentals(l_template="mean")
    assert not np.allclose(ser["l"], ala["l"])
    assert not np.allclose(mean["l"], ser["l"])


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"observer_degree": 5}, "observer_degree"),
        ({"photopigment_od": (0.5, 0.5)}, "photopigment_od"),
        ({"photopigment_od": (0.5, -0.1, 0.4)}, "photopigment_od"),
        ({"macular_density_460": -0.1}, "macular_density_460"),
        ({"lens_density_400": -0.1}, "lens_density_400"),
        ({"l_template": "unknown"}, "l_template"),
        ({"wavelength_nm": [500, 400]}, "strictly increasing"),
        ({"wavelength_nm": [350, 400]}, "360-850"),
    ],
)
def test_invalid_inputs_raise(kwargs, match):
    with pytest.raises(ValueError, match=match):
        generate_stockman_rider_2023_individual_cone_fundamentals(**kwargs)


def test_asano2016_default_shape_and_normalisation():
    raw = generate_asano2016_individual_cone_fundamentals()
    values = _stack(raw)
    assert raw["wavelength"].shape == (89,)
    assert values.shape == (89, 3)
    assert np.isfinite(values).all()
    np.testing.assert_allclose(values.max(axis=0), [1.0, 1.0, 1.0])


def test_asano2016_components_match_final_lms():
    components = asano2016_model_components(
        age=45,
        field_size_degree=4,
        lens_density_deviation=10.0,
        macular_density_deviation=-5.0,
        photopigment_shift_nm=(2.0, -1.0, 0.0),
    )
    raw = generate_asano2016_individual_cone_fundamentals(
        age=45,
        field_size_degree=4,
        lens_density_deviation=10.0,
        macular_density_deviation=-5.0,
        photopigment_shift_nm=(2.0, -1.0, 0.0),
    )
    _assert_component_shapes(components, 89)
    np.testing.assert_allclose(components["corneal_energy"], _stack(raw))


def test_asano2016_components_reflect_observer_parameters():
    standard = asano2016_model_components()
    older = asano2016_model_components(age=70)
    wide = asano2016_model_components(field_size_degree=10)
    shifted = asano2016_model_components(photopigment_shift_nm=(5.0, 0.0, 0.0))

    assert not np.allclose(standard["lens_density"], older["lens_density"])
    assert not np.allclose(standard["macular_density"], wide["macular_density"])
    assert not np.allclose(
        standard["photopigment_absorbance"][:, 0],
        shifted["photopigment_absorbance"][:, 0],
    )


def test_asano2016_zero_deviations_match_cie2006_average_observers():
    for field_size, getter in (
        (2.0, get_cie2006_lms_2degree_fundamentals),
        (10.0, get_cie2006_lms_10degree_fundamentals),
    ):
        generated = generate_asano2016_individual_cone_fundamentals(
            field_size_degree=field_size,
        )
        reference = getter(interval_nm=5, energy="linE")
        values = _stack(generated)
        ref_values = _stack(reference)
        finite = np.isfinite(ref_values)
        np.testing.assert_allclose(values[finite], ref_values[finite], atol=1.0e-2)
        assert np.mean(np.abs(values[finite] - ref_values[finite])) < 1.0e-3


def test_asano2016_individual_parameters_change_expected_regions():
    standard = generate_asano2016_individual_cone_fundamentals()
    dense_lens = generate_asano2016_individual_cone_fundamentals(
        lens_density_deviation=50.0,
    )
    dense_macular = generate_asano2016_individual_cone_fundamentals(
        macular_density_deviation=50.0,
    )
    shifted_l = generate_asano2016_individual_cone_fundamentals(
        photopigment_shift_nm=(5.0, 0.0, 0.0),
    )

    short = standard["wavelength"] <= 430.0
    blue_peak_tail = (standard["wavelength"] >= 445.0) & (standard["wavelength"] <= 465.0)
    assert dense_lens["s"][short].mean() < standard["s"][short].mean()
    assert dense_macular["s"][blue_peak_tail].mean() < standard["s"][blue_peak_tail].mean()
    assert shifted_l["wavelength"][np.argmax(shifted_l["l"])] > standard["wavelength"][
        np.argmax(standard["l"])
    ]


@pytest.mark.parametrize(
    "kwargs, match",
    [
        ({"age": 0}, "age"),
        ({"field_size_degree": 0}, "field_size_degree"),
        ({"lens_density_deviation": -101}, "lens_density_deviation"),
        ({"macular_density_deviation": -101}, "macular_density_deviation"),
        ({"photopigment_od_deviation": (0.0, 0.0)}, "photopigment_od_deviation"),
        (
            {"photopigment_od_deviation": (0.0, -101.0, 0.0)},
            "photopigment_od_deviation",
        ),
        ({"photopigment_shift_nm": (0.0, 0.0)}, "photopigment_shift_nm"),
        ({"wavelength_nm": [500, 400]}, "strictly increasing"),
        ({"wavelength_nm": [380, 400]}, "390-830"),
    ],
)
def test_asano2016_invalid_inputs_raise(kwargs, match):
    with pytest.raises(ValueError, match=match):
        generate_asano2016_individual_cone_fundamentals(**kwargs)
