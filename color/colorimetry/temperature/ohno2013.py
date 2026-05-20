"""Ohno (2013) CCT and Duv helpers."""

from __future__ import annotations

from typing import Sequence

import numpy as np

from color.generators.blackbody import blackbody_spd
from color.spectra import MultiSpectralDistribution, from_dataset

from ._helpers import as_finite_array, as_last_axis_pairs
from .conversions import XYZ_to_uv1960


CCT_MINIMAL_OHNO2013 = 1000.0
CCT_MAXIMAL_OHNO2013 = 100000.0
CCT_DEFAULT_SPACING_OHNO2013 = 1.001
DEFAULT_CMFS_OHNO2013 = "cie1931_xyz_1nm"

_PLANCKIAN_TABLE_CACHE: dict[tuple[object, float, float, float], np.ndarray] = {}


def _load_cmfs(cmfs: str | MultiSpectralDistribution) -> MultiSpectralDistribution:
    """Return XYZ colour matching functions from a dataset name or object."""
    if isinstance(cmfs, MultiSpectralDistribution):
        loaded = cmfs
    else:
        loaded = from_dataset("standard_observers.cmfs", cmfs)
    if loaded.labels != ("X", "Y", "Z"):
        raise ValueError("cmfs must contain X, Y and Z channels")
    return loaded


def _cmfs_cache_key(cmfs: str | MultiSpectralDistribution) -> object:
    """Return a cache key fragment for CMFs."""
    if isinstance(cmfs, str):
        return ("dataset", cmfs)
    return ("object", id(cmfs))


def _CCT_to_uv_Planck1900(
    CCT: float | Sequence[float] | np.ndarray,
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_CMFS_OHNO2013,
) -> np.ndarray:
    """Return CIE 1960 UCS uv coordinates for Planckian radiators."""
    cct = as_finite_array(CCT, name="CCT")
    if np.any(cct <= 0):
        raise ValueError("CCT must be positive")

    cct_shape = cct.shape
    cct_flat = cct.reshape(-1)
    cmfs_obj = _load_cmfs(cmfs)
    wavelengths = cmfs_obj.wavelengths
    interval = float(np.diff(wavelengths).min()) if wavelengths.size > 1 else 1.0

    radiance = np.vstack(
        [
            blackbody_spd(wavelength_nm=wavelengths, temperature=float(temperature))[
                "radiance"
            ]
            for temperature in cct_flat
        ]
    )
    XYZ = (radiance @ cmfs_obj.values) * interval
    uv = XYZ_to_uv1960(XYZ)
    return uv.reshape(cct_shape + (2,))


def _ohno_temperatures(start: float, end: float, spacing: float) -> np.ndarray:
    """Return the Ohno cascade temperature samples."""
    samples = [start, start + 1.0]
    next_temperature = start + 1.0
    next_spacing = spacing
    while True:
        next_temperature *= next_spacing
        if next_temperature >= end:
            break
        samples.append(next_temperature)
        d = (next_temperature - CCT_MINIMAL_OHNO2013) / (
            CCT_MAXIMAL_OHNO2013 - CCT_MINIMAL_OHNO2013
        )
        d = min(max(d, 0.0), 1.0)
        next_spacing = spacing * (1.0 - d) + (1.0 + (spacing - 1.0) / 10.0) * d
    samples.extend([end - 1.0, end])
    return np.asarray(samples, dtype=np.float64)


def planckian_table_Ohno2013(
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_CMFS_OHNO2013,
    start: float = CCT_MINIMAL_OHNO2013,
    end: float = CCT_MAXIMAL_OHNO2013,
    spacing: float = CCT_DEFAULT_SPACING_OHNO2013,
) -> np.ndarray:
    """Generate the Planckian uv table used by Ohno (2013)."""
    start = float(as_finite_array(start, name="start"))
    end = float(as_finite_array(end, name="end"))
    spacing = float(as_finite_array(spacing, name="spacing"))
    if start <= 0:
        raise ValueError("start must be positive")
    if end <= start:
        raise ValueError("end must be greater than start")
    if spacing <= 1.0:
        raise ValueError("spacing must be greater than 1")

    cache_key = (_cmfs_cache_key(cmfs), start, end, spacing)
    cached = _PLANCKIAN_TABLE_CACHE.get(cache_key)
    if cached is not None:
        return np.array(cached, copy=True)

    temperatures = _ohno_temperatures(start, end, spacing)
    uv = _CCT_to_uv_Planck1900(temperatures, cmfs=cmfs)
    table = np.column_stack([temperatures, uv])
    _PLANCKIAN_TABLE_CACHE[cache_key] = np.array(table, copy=True)
    return table


def uv_to_CCT_Ohno2013(
    uv: Sequence[float] | np.ndarray,
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_CMFS_OHNO2013,
    start: float = CCT_MINIMAL_OHNO2013,
    end: float = CCT_MAXIMAL_OHNO2013,
    spacing: float = CCT_DEFAULT_SPACING_OHNO2013,
) -> np.ndarray:
    """Return CCT and Duv from CIE 1960 UCS uv using Ohno (2013)."""
    uv_arr = as_last_axis_pairs(uv, name="uv")
    uv_flat = uv_arr.reshape(-1, 2)
    table = planckian_table_Ohno2013(
        cmfs=cmfs,
        start=start,
        end=end,
        spacing=spacing,
    )

    rows = []
    for uv_i in uv_flat:
        distances = np.linalg.norm(table[:, 1:] - uv_i, axis=1)
        index = int(np.argmin(distances))
        if index == 0:
            index = 1
        elif index == table.shape[0] - 1:
            index = table.shape[0] - 2
        rows.append(
            np.vstack(
                [
                    [*table[index - 1], distances[index - 1]],
                    [*table[index], distances[index]],
                    [*table[index + 1], distances[index + 1]],
                ]
            )
        )

    selected = np.asarray(rows, dtype=np.float64)
    Tip, uip, vip, dip = selected[:, 0, :].T
    Ti, _ui, _vi, di = selected[:, 1, :].T
    Tin, uin, vin, din = selected[:, 2, :].T

    length = np.hypot(uin - uip, vin - vip)
    if np.any(length == 0):
        raise ValueError("Planckian table contains duplicate uv coordinates")
    x = (dip**2 - din**2 + length**2) / (2.0 * length)
    T_t = Tip + (Tin - Tip) * (x / length)

    vtx = vip + (vin - vip) * (x / length)
    sign = np.sign(uv_flat[:, 1] - vtx)
    D_uv_t = np.sqrt(np.maximum(dip**2 - x**2, 0.0)) * sign

    divisor = (Tin - Ti) * (Tip - Tin) * (Ti - Tip)
    if np.any(divisor == 0):
        raise ValueError("Planckian table contains duplicate temperatures")
    a = (Tip * (din - di) + Ti * (dip - din) + Tin * (di - dip)) / divisor
    b = -(
        Tip**2 * (din - di)
        + Ti**2 * (dip - din)
        + Tin**2 * (di - dip)
    ) / divisor
    c = -(
        dip * (Tin - Ti) * Ti * Tin
        + di * (Tip - Tin) * Tip * Tin
        + din * (Ti - Tip) * Tip * Ti
    ) / divisor
    if np.any(a == 0):
        raise ValueError("Ohno parabolic fit produced a zero quadratic term")
    T_p = -b / (2.0 * a)
    D_uv_p = (a * T_p**2 + b * T_p + c) * sign

    result = np.where(
        (np.abs(D_uv_t) >= 0.002)[:, None],
        np.stack([T_p, D_uv_p], axis=-1),
        np.stack([T_t, D_uv_t], axis=-1),
    )
    return result.reshape(uv_arr.shape)


def CCT_to_uv_Ohno2013(
    CCT_Duv: Sequence[float] | np.ndarray,
    *,
    cmfs: str | MultiSpectralDistribution = DEFAULT_CMFS_OHNO2013,
) -> np.ndarray:
    """Return CIE 1960 UCS uv from CCT and Duv using Ohno (2013)."""
    cct_duv = as_last_axis_pairs(CCT_Duv, name="CCT_Duv")
    CCT = cct_duv[..., 0]
    D_uv = cct_duv[..., 1]
    if np.any(CCT <= 0):
        raise ValueError("CCT must be positive")

    uv_0 = _CCT_to_uv_Planck1900(CCT, cmfs=cmfs)
    uv_1 = _CCT_to_uv_Planck1900(CCT + 0.01, cmfs=cmfs)
    du = uv_0[..., 0] - uv_1[..., 0]
    dv = uv_0[..., 1] - uv_1[..., 1]
    h = np.hypot(du, dv)
    if np.any(h == 0):
        raise ValueError("Planckian tangent length is zero")

    uv_result = np.stack(
        [
            uv_0[..., 0] - D_uv * dv / h,
            uv_0[..., 1] + D_uv * du / h,
        ],
        axis=-1,
    )
    return np.where((D_uv == 0)[..., None], uv_0, uv_result)


__all__ = [
    "CCT_MINIMAL_OHNO2013",
    "CCT_MAXIMAL_OHNO2013",
    "CCT_DEFAULT_SPACING_OHNO2013",
    "DEFAULT_CMFS_OHNO2013",
    
    "planckian_table_Ohno2013",
    "uv_to_CCT_Ohno2013",
    "CCT_to_uv_Ohno2013",
]
