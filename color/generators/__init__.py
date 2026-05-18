"""Formula and procedural data generators."""

from __future__ import annotations

from . import blackbody  # noqa: F401
from . import ideal  # noqa: F401
from . import illuminants  # noqa: F401
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
    zero_spd,
)
from .illuminants import (
    daylight_spd,
    generate_illuminant,
    illuminant_a_spd,
    list_illuminant_generators,
)
from .leds import (
    generate_led,
    list_led_generators,
    multi_led_spd,
    single_led_spd,
)

__all__ = [
    "GeneratorEntry",
    "generate",
    "describe",
    "clear_cache",
    "list_categories",
    "list_generators",
    "register",
    "blackbody_spd",
    "generate_blackbody",
    "list_blackbody_generators",
    "illuminant_a_spd",
    "daylight_spd",
    "generate_illuminant",
    "list_illuminant_generators",
    "constant_spd",
    "zero_spd",
    "equal_energy_spd",
    "gaussian_spd",
    "generate_ideal",
    "list_ideal_generators",
    "single_led_spd",
    "multi_led_spd",
    "generate_led",
    "list_led_generators",
]
