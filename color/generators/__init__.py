"""Formula and procedural data generators."""

from __future__ import annotations

from . import blackbody  # noqa: F401
from . import ideal  # noqa: F401
from . import illuminants  # noqa: F401
from . import individual_cone_fundamentals  # noqa: F401
from . import leds  # noqa: F401
from ._registry import (
    GeneratorEntry,
    clear_cache,
    describe,
    generate,
    list_categories,
    list_generators,
    register,
)
from .blackbody import (
    blackbody_spd,
    generate_blackbody,
    list_blackbody_generators,
)
from .ideal import (
    constant_spd,
    equal_energy_spd,
    gaussian_spd,
    generate_ideal,
    list_ideal_generators,
    multi_gaussian_spd,
    zero_spd,
)
from .illuminants import (
    daylight_spd,
    generate_illuminant,
    illuminant_a_spd,
    list_illuminant_generators,
)
from .individual_cone_fundamentals import (
    cone_absorbance_spectra,
    generate_individual_cone_fundamental,
    generate_individual_cone_fundamentals,
    lens_density_spectrum,
    list_individual_cone_fundamental_generators,
    macular_density_spectrum,
)
from .leds import (
    generate_led,
    list_led_generators,
    multi_led_spd,
    single_led_spd,
)

# Core generator registry.
__all__ = [
    "GeneratorEntry",  # metadata record for a registered generator
    "generate",  # generate data from a registered generator
    "describe",  # describe a registered generator
    "clear_cache",  # clear cached generator outputs
    "list_categories",  # list generator categories
    "list_generators",  # list generators in a category
    "register",  # register a generator entry
]

# Blackbody and Planck-family generators.
__all__ += [
    "blackbody_spd",  # generate a blackbody spectral power distribution
    
    "generate_blackbody",  # generate a registered blackbody dataset
    "list_blackbody_generators",  # list blackbody generator names
]

# Illuminant generators.
__all__ += [
    "illuminant_a_spd",  # generate CIE Illuminant A SPD
    "daylight_spd",  # generate CIE daylight SPD

    "generate_illuminant",  # generate a registered illuminant dataset
    "list_illuminant_generators",  # list illuminant generator names
]

# Ideal analytic spectra.
__all__ += [
    "constant_spd",  # generate a constant ideal spectrum
    "zero_spd",  # generate a zero-valued ideal spectrum
    "equal_energy_spd",  # generate an equal-energy ideal spectrum
    "gaussian_spd",  # generate a Gaussian ideal spectrum
    "multi_gaussian_spd",  # generate a multi-Gaussian ideal spectrum

    "generate_ideal",  # generate a registered ideal spectrum
    "list_ideal_generators",  # list ideal generator names
]

# LED spectral generators.
__all__ += [
    "single_led_spd",  # generate a single LED spectrum
    "multi_led_spd",  # generate a multi-channel LED mixture spectrum

    "generate_led",  # generate a registered LED spectrum
    "list_led_generators",  # list LED generator names
]

# Individual cone fundamental generators.
__all__ += [
    "macular_density_spectrum",  # generate Stockman/Rider macular density
    "lens_density_spectrum",  # generate Stockman/Rider lens density
    "cone_absorbance_spectra",  # generate L/M/S photopigment absorbances

    "generate_individual_cone_fundamentals",  # generate Stockman/Rider LMS fundamentals
    "generate_individual_cone_fundamental",  # generate a registered individual LMS model
    "list_individual_cone_fundamental_generators",  # list individual LMS generator names
]
