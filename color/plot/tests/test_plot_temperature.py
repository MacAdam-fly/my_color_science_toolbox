"""Tests for temperature plotting helpers."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytest

from color.plot import (
    daylight_locus_uv1960,
    duv_offset_grid_uv1960,
    planckian_locus_uv1960,
    plot_duv_offsets_uv1960,
    plot_mired_curve,
    plot_temperature_loci_uv1960,
)


def _close(fig) -> None:
    plt.close(fig)


def test_planckian_locus_uv1960_shape() -> None:
    uv = planckian_locus_uv1960(cct_min=2000.0, cct_max=10000.0, samples=24)
    assert uv.shape == (24, 2)
    assert np.all(np.isfinite(uv))


def test_daylight_locus_uv1960_shape() -> None:
    uv = daylight_locus_uv1960(cct_min=4000.0, cct_max=12000.0, samples=20)
    assert uv.shape == (20, 2)
    assert np.all(np.isfinite(uv))


def test_duv_offset_grid_uv1960_shape() -> None:
    grid = duv_offset_grid_uv1960(
        [3000.0, 6500.0],
        [-0.01, 0.0, 0.01],
    )
    assert grid.shape == (2, 3, 2)
    assert np.all(np.isfinite(grid))


def test_temperature_loci_plot_returns_fig_ax() -> None:
    fig, ax = plot_temperature_loci_uv1960(
        planckian_cct_min=2000.0,
        planckian_cct_max=10000.0,
        daylight_cct_min=4000.0,
        daylight_cct_max=10000.0,
        samples=24,
        daylight_samples=20,
        background_samples=32,
    )
    assert fig is ax.figure
    assert len(ax.images) == 1
    assert len(ax.lines) >= 3
    _close(fig)


def test_duv_offsets_plot_returns_fig_ax() -> None:
    fig, ax = plot_duv_offsets_uv1960(
        ccts=[3000.0, 6500.0],
        duvs=[-0.01, 0.0, 0.01],
    )
    assert fig is ax.figure
    assert len(ax.lines) >= 3
    assert len(ax.collections) >= 1
    _close(fig)


def test_mired_curve_returns_fig_ax() -> None:
    fig, ax = plot_mired_curve(cct_min=2000.0, cct_max=12000.0, samples=20)
    assert fig is ax.figure
    assert len(ax.lines) == 1
    _close(fig)


def test_temperature_helpers_reject_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        planckian_locus_uv1960(samples=1)
    with pytest.raises(ValueError):
        daylight_locus_uv1960(cct_min=25000.0, cct_max=4000.0)
    with pytest.raises(ValueError):
        duv_offset_grid_uv1960([[6500.0]], [0.0])
