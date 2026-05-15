"""Color tool framework for conversions, metrics, appearance models, gamut, and balancing."""

from __future__ import annotations

from importlib import import_module

from .core.types import ArrayLike

__all__ = [
    "ArrayLike",
    "ColorAppearanceToolkit",
    "BrightnessBalancingToolkit",
    "ComplementaryToolkit",
    "ColorConversionSuite",
    "DeltaEToolkit",
    "GamutToolkit",
]


def __getattr__(name: str):
    lazy_exports = {
        "ColorAppearanceToolkit": ("color_agent.tools.appearance", "ColorAppearanceToolkit"),
        "BrightnessBalancingToolkit": ("color_agent.tools.balance", "BrightnessBalancingToolkit"),
        "ComplementaryToolkit": ("color_agent.tools.complementary", "ComplementaryToolkit"),
        "ColorConversionSuite": ("color_agent.tools.conversion", "ColorConversionSuite"),
        "DeltaEToolkit": ("color_agent.tools.delta_e", "DeltaEToolkit"),
        "GamutToolkit": ("color_agent.tools.gamut", "GamutToolkit"),
    }
    if name in lazy_exports:
        module_name, attribute_name = lazy_exports[name]
        module = import_module(module_name)
        value = getattr(module, attribute_name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
