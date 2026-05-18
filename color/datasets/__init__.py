"""Dataset loading layer for color science reference data.

Provides lazy-loaded, cached access to static datasets in ``color/data/``.
Formula-generated data lives in :mod:`color.generators`.

Quick start::

    from color.datasets import get, list_datasets, list_categories

    # Illuminants
    d65 = get('illuminants', 'D65')

    # Color cards
    macbeth = get('color_cards', 'macbeth')

    # Standard observers
    xyz31 = get('standard_observers.cmfs', 'cie1931_xyz_1nm')

    # Gamut data
    pointer = get('gamut_data', 'pointer', sheet='Calculations')

    # Discovery
    list_categories()
    list_datasets('illuminants')
"""

from __future__ import annotations

# Import category modules to trigger registration
from . import color_cards  # noqa: F401
from . import color_systems  # noqa: F401
from . import gamut_data  # noqa: F401
from . import illuminants  # noqa: F401
from . import standard_observers  # noqa: F401

# Re-export the core registry API
from ._registry import (
    DatasetEntry,
    canonicalize_name,
    clear_cache,
    describe,
    get,
    list_categories,
    list_datasets,
    register,
    search,
)

# Re-export category-specific convenience functions
from .color_cards import get_color_card, list_color_cards
from .color_systems import get_color_system, list_color_systems
from .gamut_data import get_gamut_data, list_gamut_data
from .illuminants import get_illuminant, list_illuminants
from .standard_observers import (
    describe_standard_observer,
    get_standard_observer,
    list_standard_observer_categories,
    list_standard_observers,
)

__all__ = [
    # Core registry
    "DatasetEntry",
    "canonicalize_name",
    "get",
    "describe",
    "clear_cache",
    "list_categories",
    "list_datasets",
    "register",
    "search",
    # Illuminants
    "get_illuminant",
    "list_illuminants",
    # Color cards
    "get_color_card",
    "list_color_cards",
    # Standard observers
    "get_standard_observer",
    "list_standard_observers",
    "list_standard_observer_categories",
    "describe_standard_observer",
    # Gamut data
    "get_gamut_data",
    "list_gamut_data",
    # Color systems
    "get_color_system",
    "list_color_systems",
]
