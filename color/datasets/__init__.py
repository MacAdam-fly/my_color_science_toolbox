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
from . import reflectance_spectra  # noqa: F401
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
from .reflectance_spectra import get_reflectance_spectrum, list_reflectance_spectra
from .standard_observers import (
    describe_standard_observer,
    get_standard_observer,
    list_standard_observer_categories,
    list_standard_observers,
)

__all__ = [
    "DatasetEntry",  # metadata record for a registered dataset
    "canonicalize_name",  # resolve a dataset name to its canonical name
    "get",  # load a registered dataset as raw arrays
    "describe",  # describe a registered dataset
    "clear_cache",  # clear cached dataset loads
    "list_categories",  # list dataset categories
    "list_datasets",  # list datasets in a category
    "register",  # register a dataset entry
    "search",  # search registered datasets
]

__all__ += [
    "get_illuminant",  # load an illuminant dataset
    "list_illuminants",  # list illuminant datasets
]

__all__ += [
    "get_color_card",  # load a color-card dataset
    "list_color_cards",  # list color-card datasets
]

__all__ += [
    "get_standard_observer",  # load a standard-observer dataset
    "list_standard_observers",  # list standard observers in a category
    "list_standard_observer_categories",  # list standard-observer subcategories
    "describe_standard_observer",  # describe a standard-observer dataset
]

__all__ += [
    "get_gamut_data",  # load a gamut reference dataset
    "list_gamut_data",  # list gamut reference datasets
]

__all__ += [
    "get_color_system",  # load a color-system dataset
    "list_color_systems",  # list color-system datasets
]

__all__ += [
    "get_reflectance_spectrum",  # load a UEF spectral reflectance dataset
    "list_reflectance_spectra",  # list UEF spectral reflectance datasets
]
