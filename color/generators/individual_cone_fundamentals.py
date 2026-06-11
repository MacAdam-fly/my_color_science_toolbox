"""Formula-generated individual cone fundamentals."""

from __future__ import annotations

from typing import List

from color.individual_cone_fundamentals import (
    ASANO2016_REFERENCE,
    STOCKMAN_RIDER_REFERENCE,
    generate_asano2016_individual_cone_fundamentals as _generate_asano2016,
    generate_stockman_rider_2023_individual_cone_fundamentals as _generate_stockman_rider_2023,
)

from ._registry import GeneratedDict, GeneratorEntry, generate, list_generators, register


register(GeneratorEntry(
    category="individual_cone_fundamentals",
    name="stockman_rider_2023",
    description="Stockman & Rider 2023 individual LMS cone fundamentals",
    generate_fn=_generate_stockman_rider_2023,
    parameters=(
        "wavelength_nm",
        "observer_degree",
        "photopigment_od",
        "macular_density_460",
        "lens_density_400",
        "l_shift_nm",
        "m_shift_nm",
        "s_shift_nm",
        "l_template",
    ),
    metadata={
        "quantity": "cone_fundamental",
        "value_unit": "relative",
        "wavelength_unit": "nm",
        "energy_basis": "energy",
        "scale": "linear",
        "model": "Stockman/Rider 2023",
        "reference": STOCKMAN_RIDER_REFERENCE,
    },
))


register(GeneratorEntry(
    category="individual_cone_fundamentals",
    name="asano2016",
    description="Asano et al. 2016 individual colorimetric observer LMS fundamentals",
    generate_fn=_generate_asano2016,
    parameters=(
        "wavelength_nm",
        "age",
        "field_size_degree",
        "lens_density_deviation",
        "macular_density_deviation",
        "photopigment_od_deviation",
        "photopigment_shift_nm",
    ),
    metadata={
        "quantity": "cone_fundamental",
        "value_unit": "relative",
        "wavelength_unit": "nm",
        "energy_basis": "energy",
        "scale": "linear",
        "model": "Asano et al. 2016",
        "reference": ASANO2016_REFERENCE,
    },
))


def generate_stockman_rider_2023_individual_cone_fundamentals(**kwargs) -> GeneratedDict:
    """Generate Stockman/Rider 2023 individual LMS cone fundamentals.

    Parameters
    ----------
    **kwargs
        Passed to ``color.individual_cone_fundamentals``. Common parameters
        include observer degree, photopigment optical density, macular/lens
        density and L/M/S wavelength shifts.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"``, ``"l"``, ``"m"`` and ``"s"``.

    Notes
    -----
    The generator returns final corneal-energy LMS fundamentals only. Model
    components are available from the core
    ``color.individual_cone_fundamentals`` module, not from the generator
    registry.
    """
    return generate(
        "individual_cone_fundamentals",
        "stockman_rider_2023",
        **kwargs,
    )


def generate_asano2016_individual_cone_fundamentals(**kwargs) -> GeneratedDict:
    """Generate Asano et al. 2016 individual LMS cone fundamentals.

    Parameters
    ----------
    **kwargs
        Passed to ``color.individual_cone_fundamentals``. Common parameters
        include age, field size, density deviations and L/M/S lambda-max
        shifts.

    Returns
    -------
    dict[str, ndarray]
        Raw mapping with ``"wavelength"``, ``"l"``, ``"m"`` and ``"s"``.

    Notes
    -----
    This entry is intended for generated individual observers. If you only
    need the static CIE 2006 mean LMS fundamentals, use ``color.spectra`` or
    ``color.datasets`` standard-observer wrappers.
    """
    return generate(
        "individual_cone_fundamentals",
        "asano2016",
        **kwargs,
    )


def generate_individual_cone_fundamental(
    name: str = "stockman_rider_2023",
    **kwargs,
) -> GeneratedDict:
    """Generate an individual cone fundamental dataset by model name.

    Parameters
    ----------
    name
        Registered model name, e.g. ``"stockman_rider_2023"`` or
        ``"asano2016"``.
    **kwargs
        Forwarded to the selected model.

    Returns
    -------
    dict[str, ndarray]
        Raw corneal-energy LMS fundamentals.
    """
    return generate("individual_cone_fundamentals", name, **kwargs)


def list_individual_cone_fundamental_generators() -> List[str]:
    """List registered individual cone fundamental generators."""
    return list_generators("individual_cone_fundamentals")


__all__ = [
    "generate_stockman_rider_2023_individual_cone_fundamentals",
    "generate_asano2016_individual_cone_fundamentals",
    "generate_individual_cone_fundamental",
    "list_individual_cone_fundamental_generators",
]
