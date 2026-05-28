"""Tests for color.spectra core objects."""

from __future__ import annotations

import numpy as np
import pytest

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_D65_illuminant,
    from_cie1931_xyz_cmfs,
    from_cie1964_xyz_cmfs,
    from_cie2006_lms_2degree_fundamentals,
    from_cie2006_lms_10degree_fundamentals,
    from_cie2012_xyz_2degree_cmfs,
    from_cie2012_xyz_10degree_cmfs,
    from_columns,
    from_dataset,
    from_individual_cone_fundamentals,
)


class TestSpectralShape:
    """Tests for SpectralShape."""

    def test_valid_construction(self):
        shape = SpectralShape(400, 410, 5)
        np.testing.assert_array_equal(shape.wavelengths, [400, 405, 410])
        assert len(shape) == 3
        assert 405 in shape
        assert 406 not in shape

    def test_rejects_invalid_bounds(self):
        with pytest.raises(ValueError, match="start must be less"):
            SpectralShape(410, 400, 5)

    def test_rejects_non_positive_interval(self):
        with pytest.raises(ValueError, match="interval must be positive"):
            SpectralShape(400, 410, 0)

    def test_includes_unaligned_end(self):
        shape = SpectralShape(400, 406, 5)
        np.testing.assert_array_equal(shape.wavelengths, [400, 405, 406])


class TestSpectralDistribution:
    """Tests for SpectralDistribution."""

    def test_constructs_readonly_arrays(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2], name="test")
        assert sd.name == "test"
        assert sd.wavelengths.flags.writeable is False
        assert sd.values.flags.writeable is False

    def test_fill_nan(self):
        sd = SpectralDistribution([400, 500], [0.1, np.nan], fill_nan=0.0)
        np.testing.assert_allclose(sd.values, [0.1, 0.0])
        assert sd.values.flags.writeable is False
        assert sd.metadata["nan_policy"] == "fill"
        assert sd.metadata["nan_fill_value"] == 0.0

    def test_fill_nan_rejects_non_finite_value(self):
        with pytest.raises(ValueError, match="fill_nan must be finite"):
            SpectralDistribution([400, 500], [0.1, np.nan], fill_nan=np.nan)

    def test_domain_range_aliases(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2])
        assert sd.domain is sd.wavelengths
        assert sd.range is sd.values
        assert sd.domain.flags.writeable is False
        assert sd.range.flags.writeable is False

    def test_rejects_length_mismatch(self):
        with pytest.raises(ValueError, match="same length"):
            SpectralDistribution([400, 500], [0.1])

    def test_rejects_unsorted_wavelengths(self):
        with pytest.raises(ValueError, match="strictly increasing"):
            SpectralDistribution([500, 400], [0.1, 0.2])

    def test_from_columns(self):
        raw = {
            "wavelength": np.array([400, 500]),
            "spd": np.array([0.1, 0.2]),
        }
        sd = SpectralDistribution.from_columns(raw, y="spd", name="D65")
        assert sd.name == "D65"
        np.testing.assert_array_equal(sd.values, [0.1, 0.2])

    def test_to_dict(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2])
        raw = sd.to_dict()
        assert list(raw.keys()) == ["wavelength", "value"]
        np.testing.assert_array_equal(raw["wavelength"], [400, 500])
        np.testing.assert_array_equal(raw["value"], [0.1, 0.2])

    def test_keys_returns_raw_column_keys(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2])
        assert sd.keys() == ("wavelength", "value")

    def test_getitem_returns_columns(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2])
        assert sd["wavelength"] is sd.wavelengths
        assert sd["value"] is sd.values
        with pytest.raises(KeyError, match="unknown spectral column"):
            sd["spd"]

    def test_interpolate(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.interpolate([425, 450, 475], method="linear")
        np.testing.assert_allclose(result.values, [0.25, 0.5, 0.75])
        assert result is not sd

    def test_sample_and_call_return_values(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        sampled = sd.sample([425, 450, 475], method="linear")
        called = sd([425, 450, 475], method="linear")
        np.testing.assert_allclose(sampled, [0.25, 0.5, 0.75])
        np.testing.assert_allclose(called, sampled)
        assert isinstance(sampled, np.ndarray)

    def test_interpolate_rejects_out_of_bounds_by_default(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        with pytest.raises(ValueError, match="outside"):
            sd.interpolate([350, 450])

    def test_interpolate_fill_value(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.interpolate(
            [350, 400, 550],
            method="linear",
            bounds_error=False,
            fill_value=-1.0,
        )
        np.testing.assert_allclose(result.values, [-1.0, 0.0, -1.0])

    def test_reshape(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.reshape(SpectralShape(400, 500, 50))
        np.testing.assert_array_equal(result.wavelengths, [400, 450, 500])
        np.testing.assert_allclose(result.values, [0.0, 0.5, 1.0])

    def test_trim(self):
        sd = SpectralDistribution([400, 450, 500, 550], [0.0, 0.5, 1.0, 1.5])
        result = sd.trim(SpectralShape(425, 525, 50))
        np.testing.assert_array_equal(result.wavelengths, [450, 500])
        np.testing.assert_allclose(result.values, [0.5, 1.0])

    def test_align_constant_extrapolation(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.align(SpectralShape(350, 550, 100), interpolator="linear")
        np.testing.assert_array_equal(result.wavelengths, [350, 450, 550])
        np.testing.assert_allclose(result.values, [0.0, 0.5, 1.0])

    def test_extrapolate_fill(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.extrapolate(
            SpectralShape(350, 550, 100),
            interpolator="linear",
            method="fill",
            fill_value=-1.0,
        )
        np.testing.assert_allclose(result.values, [-1.0, 0.5, -1.0])

    def test_extrapolate_linear(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.extrapolate(
            SpectralShape(350, 550, 100),
            interpolator="linear",
            method="linear",
        )
        np.testing.assert_allclose(result.values, [-0.5, 0.5, 1.5])

    def test_extrapolate_left_right_override(self):
        sd = SpectralDistribution([400, 500], [0.0, 1.0])
        result = sd.align(
            SpectralShape(350, 550, 100),
            interpolator="linear",
            extrapolator="constant",
            left=-1.0,
            right=2.0,
        )
        np.testing.assert_allclose(result.values, [-1.0, 0.5, 2.0])

    def test_interpolate_pchip_and_nearest(self):
        sd = SpectralDistribution([400, 500, 600], [0.0, 1.0, 0.0])
        pchip = sd.interpolate([450, 550], method="pchip")
        nearest = sd.interpolate([425, 525], method="nearest")
        np.testing.assert_allclose(pchip.values, [0.75, 0.75])
        np.testing.assert_allclose(nearest.values, [0.0, 1.0])

    def test_to_numpy_and_pandas(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2])
        np.testing.assert_allclose(sd.to_numpy(), [[400, 0.1], [500, 0.2]])
        df = sd.to_pandas()
        assert list(df.columns) == ["wavelength", "value"]

    def test_arithmetic_with_scalar(self):
        sd = SpectralDistribution([400, 500], [0.1, 0.2])
        np.testing.assert_allclose((sd * 2).values, [0.2, 0.4])
        np.testing.assert_allclose((1 - sd).values, [0.9, 0.8])

    def test_arithmetic_with_distribution(self):
        left = SpectralDistribution([400, 500], [0.1, 0.2])
        right = SpectralDistribution([400, 500], [0.3, 0.4])
        np.testing.assert_allclose((left + right).values, [0.4, 0.6])

    def test_arithmetic_rejects_different_domains(self):
        left = SpectralDistribution([400, 500], [0.1, 0.2])
        right = SpectralDistribution([400, 510], [0.3, 0.4])
        with pytest.raises(ValueError, match="different domains"):
            left + right


class TestMultiSpectralDistribution:
    """Tests for MultiSpectralDistribution."""

    def test_constructs_readonly_arrays(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        assert msd.values.shape == (2, 2)
        assert msd.wavelengths.flags.writeable is False
        assert msd.values.flags.writeable is False

    def test_fill_nan(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, np.nan], [0.3, 0.4]],
            ("X", "Y"),
            fill_nan=0.0,
        )
        np.testing.assert_allclose(msd.values, [[0.1, 0.0], [0.3, 0.4]])
        assert msd.values.flags.writeable is False
        assert msd.metadata["nan_policy"] == "fill"
        assert msd.metadata["nan_fill_value"] == 0.0

    def test_domain_range_aliases(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        assert msd.domain is msd.wavelengths
        assert msd.range is msd.values
        assert msd.domain.flags.writeable is False
        assert msd.range.flags.writeable is False

    def test_rejects_non_2d_values(self):
        with pytest.raises(ValueError, match="values must be 2D"):
            MultiSpectralDistribution([400, 500], [0.1, 0.2], ("X",))

    def test_rejects_label_mismatch(self):
        with pytest.raises(ValueError, match="label count"):
            MultiSpectralDistribution(
                [400, 500],
                [[0.1, 0.2], [0.3, 0.4]],
                ("X",),
            )

    def test_from_columns(self):
        raw = {
            "wavelength": np.array([400, 500]),
            "X": np.array([0.1, 0.3]),
            "Y": np.array([0.2, 0.4]),
        }
        msd = MultiSpectralDistribution.from_columns(raw, ys=("X", "Y"))
        assert msd.labels == ("X", "Y")
        np.testing.assert_array_equal(msd.values, [[0.1, 0.2], [0.3, 0.4]])

    def test_to_dict(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        raw = msd.to_dict()
        assert list(raw.keys()) == ["wavelength", "X", "Y"]
        np.testing.assert_array_equal(raw["X"], [0.1, 0.3])

    def test_keys_returns_raw_column_keys(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        assert msd.keys() == ("wavelength", "X", "Y")

    def test_getitem_returns_wavelength_or_channel(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
            name="cmfs",
        )
        assert msd["wavelength"] is msd.wavelengths
        channel = msd["Y"]
        assert isinstance(channel, SpectralDistribution)
        assert channel.name == "cmfs:Y"
        np.testing.assert_array_equal(channel.values, [0.2, 0.4])
        with pytest.raises(KeyError, match="unknown spectral column"):
            msd["Z"]

    def test_channel(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
            name="cmfs",
        )
        channel = msd.channel("Y")
        assert isinstance(channel, SpectralDistribution)
        assert channel.name == "cmfs:Y"
        np.testing.assert_array_equal(channel.values, [0.2, 0.4])

    def test_interpolate_preserves_labels(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.0, 1.0], [1.0, 3.0]],
            ("X", "Y"),
        )
        result = msd.interpolate([425, 450, 475])
        assert result.labels == ("X", "Y")
        np.testing.assert_allclose(
            result.values,
            [[0.25, 1.5], [0.5, 2.0], [0.75, 2.5]],
        )

    def test_sample_and_call_return_values(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.0, 1.0], [1.0, 3.0]],
            ("X", "Y"),
        )
        sampled = msd.sample([425, 450], method="linear")
        called = msd([425, 450], method="linear")
        np.testing.assert_allclose(sampled, [[0.25, 1.5], [0.5, 2.0]])
        np.testing.assert_allclose(called, sampled)
        assert isinstance(sampled, np.ndarray)

    def test_reshape_preserves_labels(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.0, 1.0], [1.0, 3.0]],
            ("X", "Y"),
        )
        result = msd.reshape(SpectralShape(400, 500, 50))
        assert result.labels == ("X", "Y")
        np.testing.assert_array_equal(result.wavelengths, [400, 450, 500])

    def test_trim_preserves_labels(self):
        msd = MultiSpectralDistribution(
            [400, 450, 500],
            [[0.0, 1.0], [0.5, 1.5], [1.0, 2.0]],
            ("X", "Y"),
        )
        result = msd.trim(SpectralShape(425, 525, 50))
        assert result.labels == ("X", "Y")
        np.testing.assert_array_equal(result.wavelengths, [450, 500])

    def test_align_preserves_labels(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.0, 1.0], [1.0, 3.0]],
            ("X", "Y"),
        )
        result = msd.align(SpectralShape(350, 550, 100), interpolator="linear")
        assert result.labels == ("X", "Y")
        np.testing.assert_allclose(
            result.values,
            [[0.0, 1.0], [0.5, 2.0], [1.0, 3.0]],
        )

    def test_linear_extrapolation_preserves_labels(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.0, 1.0], [1.0, 3.0]],
            ("X", "Y"),
        )
        result = msd.extrapolate(
            SpectralShape(350, 550, 100),
            interpolator="linear",
            method="linear",
        )
        assert result.labels == ("X", "Y")
        np.testing.assert_allclose(
            result.values,
            [[-0.5, 0.0], [0.5, 2.0], [1.5, 4.0]],
        )

    def test_to_numpy_and_pandas(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        np.testing.assert_allclose(msd.to_numpy(), [[400, 0.1, 0.2], [500, 0.3, 0.4]])
        df = msd.to_pandas()
        assert list(df.columns) == ["wavelength", "X", "Y"]

    def test_arithmetic_with_scalar(self):
        msd = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        np.testing.assert_allclose((msd + 1).values, [[1.1, 1.2], [1.3, 1.4]])

    def test_arithmetic_with_multi_distribution(self):
        left = MultiSpectralDistribution(
            [400, 500],
            [[0.1, 0.2], [0.3, 0.4]],
            ("X", "Y"),
        )
        right = MultiSpectralDistribution(
            [400, 500],
            [[1.0, 2.0], [3.0, 4.0]],
            ("X", "Y"),
        )
        np.testing.assert_allclose((left * right).values, [[0.1, 0.4], [0.9, 1.6]])

    def test_arithmetic_rejects_different_labels(self):
        left = MultiSpectralDistribution([400, 500], [[0.1], [0.2]], ("X",))
        right = MultiSpectralDistribution([400, 500], [[0.1], [0.2]], ("Y",))
        with pytest.raises(ValueError, match="different labels"):
            left + right


class TestFromColumns:
    """Tests for the module-level from_columns helper."""

    def test_single_channel(self):
        raw = {"wavelength": np.array([400, 500]), "spd": np.array([0.1, 0.2])}
        result = from_columns(raw, y="spd")
        assert isinstance(result, SpectralDistribution)

    def test_single_channel_fill_nan(self):
        raw = {"wavelength": np.array([400, 500]), "spd": np.array([0.1, np.nan])}
        result = from_columns(raw, y="spd", fill_nan=0.0)
        np.testing.assert_allclose(result.values, [0.1, 0.0])

    def test_multi_channel(self):
        raw = {
            "wavelength": np.array([400, 500]),
            "X": np.array([0.1, 0.3]),
            "Y": np.array([0.2, 0.4]),
        }
        result = from_columns(raw, ys=("X", "Y"))
        assert isinstance(result, MultiSpectralDistribution)

    def test_rejects_ambiguous_channels(self):
        raw = {"wavelength": np.array([400, 500]), "spd": np.array([0.1, 0.2])}
        with pytest.raises(ValueError, match="either y or ys"):
            from_columns(raw, y="spd", ys=("spd",))

    def test_requires_channel_choice(self):
        raw = {"wavelength": np.array([400, 500]), "spd": np.array([0.1, 0.2])}
        with pytest.raises(ValueError, match="provide y or ys"):
            from_columns(raw)


class TestFromDataset:
    """Tests for wrapping registered datasets."""

    def test_illuminant_d65(self):
        result = from_dataset("illuminants", "D65")
        assert isinstance(result, SpectralDistribution)
        assert result.name == "D65"
        assert result.metadata["dataset_category"] == "illuminants"

    def test_D65_illuminant_entrypoint(self):
        result = from_D65_illuminant()
        expected = from_dataset("illuminants", "D65")
        assert isinstance(result, SpectralDistribution)
        assert result.name == "CIE Standard Illuminant D65"
        assert result.metadata["dataset_category"] == "illuminants"
        assert result.metadata["dataset_name"] == "D65"
        assert result.metadata["standard"] == "CIE Standard Illuminant D65"
        np.testing.assert_allclose(result.wavelengths, expected.wavelengths)
        np.testing.assert_allclose(result.values, expected.values)

    def test_standard_observer_cmfs(self):
        result = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
        assert isinstance(result, MultiSpectralDistribution)
        assert result.labels == ("X", "Y", "Z")

    def test_standard_observer_lms_fill_nan(self):
        result = from_dataset(
            "standard_observers.cone_fundamentals",
            "cie2006_lms2_linE_1nm",
            fill_nan=0.0,
        )
        assert isinstance(result, MultiSpectralDistribution)
        assert np.isfinite(result.values).all()
        assert result.metadata["nan_policy"] == "fill"

    def test_canonical_names(self):
        result = from_dataset("Standard Observers CMFS", "CIE 1931 XYZ 1 nm")
        assert isinstance(result, MultiSpectralDistribution)
        assert result.labels == ("X", "Y", "Z")

    def test_standard_observer_subcategory_alias(self):
        result = from_dataset("standard_observers.cmf", "cie1931 xyz_1nm")
        assert isinstance(result, MultiSpectralDistribution)
        assert result.labels == ("X", "Y", "Z")

    def test_non_spectral_dataset_raises(self):
        with pytest.raises(ValueError, match="no wavelength"):
            from_dataset("color_systems", "munsell_srgb")


class TestCommonStandardObserverEntrypoints:
    """Tests for common standard observer spectra shortcuts."""

    def test_xyz_cmfs_wrappers(self):
        wrappers = (
            from_cie1931_xyz_cmfs,
            from_cie1964_xyz_cmfs,
            from_cie2012_xyz_2degree_cmfs,
            from_cie2012_xyz_10degree_cmfs,
        )
        for wrapper in wrappers:
            result = wrapper(interval_nm=1)
            assert isinstance(result, MultiSpectralDistribution)
            assert result.labels == ("X", "Y", "Z")
            assert result.metadata["dataset_category"] == "standard_observers.cmfs"
            assert result.metadata["interval_nm"] == 1.0

    def test_cie1931_wrapper_matches_from_dataset(self):
        result = from_cie1931_xyz_cmfs(interval_nm=1)
        expected = from_dataset("standard_observers.cmfs", "cie1931_xyz_1nm")
        np.testing.assert_allclose(result.wavelengths, expected.wavelengths)
        np.testing.assert_allclose(result.values, expected.values)
        assert result.metadata["dataset_name"] == "cie1931_xyz_1nm"
        assert result.metadata["observer_degree"] == 2

    def test_lms_fundamentals_wrappers(self):
        result_2 = from_cie2006_lms_2degree_fundamentals(
            interval_nm=1,
            energy="linE",
        )
        result_10 = from_cie2006_lms_10degree_fundamentals(
            interval_nm=5,
            energy="LOG E",
        )

        for result in (result_2, result_10):
            assert isinstance(result, MultiSpectralDistribution)
            assert result.labels == ("l", "m", "s")
            assert result.metadata["dataset_category"] == (
                "standard_observers.cone_fundamentals"
            )
            assert np.isfinite(result.values).all()

        assert result_2.metadata["dataset_name"] == "cie2006_lms2_linE_1nm"
        assert result_2.metadata["energy"] == "linE"
        assert result_10.metadata["dataset_name"] == "cie2006_lms10_logE_5nm"
        assert result_10.metadata["observer_degree"] == 10

    def test_individual_cone_fundamentals_wrapper(self):
        result = from_individual_cone_fundamentals(observer_degree=2)
        assert isinstance(result, MultiSpectralDistribution)
        assert result.labels == ("l", "m", "s")
        assert result.metadata["generator_category"] == "individual_cone_fundamentals"
        assert result.metadata["generator_name"] == "stockman_rider_2023"
        assert result.metadata["parameters"]["observer_degree"] == 2
        np.testing.assert_allclose(result.values.max(axis=0), [1.0, 1.0, 1.0])
