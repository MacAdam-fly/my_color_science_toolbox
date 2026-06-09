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
    """Generate Stockman/Rider individual LMS cone fundamentals."""
    return generate(
        "individual_cone_fundamentals",
        "stockman_rider_2023",
        **kwargs,
    )


def generate_asano2016_individual_cone_fundamentals(**kwargs) -> GeneratedDict:
    """Generate Asano et al. 2016 individual LMS cone fundamentals."""
    return generate(
        "individual_cone_fundamentals",
        "asano2016",
        **kwargs,
    )


def generate_individual_cone_fundamental(
    name: str = "stockman_rider_2023",
    **kwargs,
) -> GeneratedDict:
    """Generate an individual cone fundamental dataset by model name."""
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
