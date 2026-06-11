"""Font helpers for plotting."""

from __future__ import annotations

from collections.abc import Sequence


CJK_SANS_SERIF = [
    "Noto Sans CJK SC",
    "Noto Sans CJK JP",
    "Noto Sans CJK TC",
    "Noto Sans CJK HK",
    "Source Han Sans SC",
    "Source Han Sans CN",
    "Source Han Sans",
    "Microsoft YaHei",
    "SimHei",
    "PingFang SC",
    "Hiragino Sans GB",
    "Heiti SC",
    "WenQuanYi Micro Hei",
    "WenQuanYi Zen Hei",
    "Arial Unicode MS",
    "Arial",
    "Helvetica",
    "DejaVu Sans",
]

SERIF_STACK = [
    "Times New Roman",
    "Times",
    "Noto Serif CJK SC",
    "Noto Serif CJK JP",
    "Source Han Serif SC",
    "Songti SC",
    "SimSun",
    "DejaVu Serif",
]


def available_cjk_fonts() -> tuple[str, ...]:
    """Return CJK-capable font candidates currently visible to Matplotlib.

    Notes
    -----
    The result depends on the fonts installed in the current environment.
    """
    from matplotlib import font_manager

    installed = {font.name for font in font_manager.fontManager.ttflist}
    return tuple(font for font in CJK_SANS_SERIF if font in installed)


def use_cjk_font(preferred: str | Sequence[str] | None = None) -> tuple[str, ...]:
    """Prioritise CJK fonts in the active Matplotlib session.

    Notes
    -----
    This mutates ``matplotlib.rcParams`` for the current session. Library
    plotting functions do not call it implicitly.
    """
    import matplotlib.pyplot as plt

    if preferred is None:
        requested: list[str] = []
    elif isinstance(preferred, str):
        requested = [preferred]
    else:
        requested = list(preferred)

    stack = tuple(dict.fromkeys([*requested, *CJK_SANS_SERIF]))
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = list(stack)
    plt.rcParams["axes.unicode_minus"] = False
    return stack


__all__ = [
    "CJK_SANS_SERIF",
    "SERIF_STACK",
    "available_cjk_fonts",
    "use_cjk_font",
]
