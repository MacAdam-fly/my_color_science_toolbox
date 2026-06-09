"""Individual human cone fundamental generators."""

from __future__ import annotations

from .asano2016 import (
    asano2016_model_components,
    generate_asano2016_individual_cone_fundamentals,
)
from ._constants import ASANO2016_REFERENCE, STOCKMAN_RIDER_REFERENCE
from .stockman_rider_2023 import (
    generate_stockman_rider_2023_individual_cone_fundamentals,
    stockman_rider_2023_model_components,
)

__all__ = [
    "STOCKMAN_RIDER_REFERENCE",  # Stockman/Rider 2023 model reference text
    "ASANO2016_REFERENCE",  # Asano et al. 2016 model reference text
]

__all__ += [
    "generate_stockman_rider_2023_individual_cone_fundamentals",  # Stockman/Rider LMS fundamentals
    "stockman_rider_2023_model_components",  # Stockman/Rider model components
    "generate_asano2016_individual_cone_fundamentals",  # Asano 2016 LMS fundamentals
    "asano2016_model_components",  # Asano 2016 model components
]
