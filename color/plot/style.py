"""Opinionated Matplotlib style helpers for scientific figures.

This module is designed as a drop-in replacement for the earlier
``Plot style helpers`` module.  The public API intentionally keeps the old
names alive:

    - ``PLOT_STYLE_PRESETS``
    - ``colour_cycle``
    - ``plot_style``
    - ``set_plot_style``

The visual system has been redesigned around larger, more balanced default
fonts, CJK/Chinese font fallbacks, real monochrome styles, panel-label helpers,
and safer export defaults.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from contextlib import contextmanager
from itertools import cycle
from pathlib import Path
from os import PathLike
from typing import Any, Iterator

from cycler import cycler


# ---------------------------------------------------------------------------
# Colour system
# ---------------------------------------------------------------------------
# Keep categorical palettes separate from reference/highlight colours.
# Black and yellow are intentionally not part of the default journal cycle:
# black is visually too strong for an ordinary category, while yellow is weak
# on a white background unless it is used deliberately as a highlight.

_ACADEMIC_COLOURS = (
    "#0072B2",  # blue
    "#D55E00",  # vermillion
    "#009E73",  # green
    "#CC79A7",  # purple
    "#E69F00",  # orange
    "#56B4E9",  # sky blue
    "#332288",  # deep indigo
    "#882255",  # wine
)

_MUTED_COLOURS = (
    "#4C78A8",
    "#F58518",
    "#54A24B",
    "#B279A2",
    "#E45756",
    "#72B7B2",
    "#9D755D",
    "#79706E",
)

_PRESENTATION_COLOURS = (
    "#006BA4",
    "#FF800E",
    "#2CA02C",
    "#D62728",
    "#9467BD",
    "#17BECF",
    "#8C564B",
    "#7F7F7F",
)

_MONOCHROME_COLOURS = (
    "#111111",
    "#4D4D4D",
    "#7F7F7F",
    "#B2B2B2",
)

_DARK_COLOURS = (
    "#66C2FF",
    "#FFB000",
    "#00C48C",
    "#FF6B8A",
    "#C9A0FF",
    "#6EE7F9",
    "#F7C59F",
    "#B8B8B8",
)

# Backwards-compatible old name plus newer descriptive names.
_COLOUR_CYCLES: dict[str, tuple[str, ...]] = {
    "journal": _ACADEMIC_COLOURS,
    "journal_single": _ACADEMIC_COLOURS,
    "journal_double": _ACADEMIC_COLOURS,
    "paper": _ACADEMIC_COLOURS,
    "academic": _ACADEMIC_COLOURS,
    "muted": _MUTED_COLOURS,
    "presentation": _PRESENTATION_COLOURS,
    "slide": _PRESENTATION_COLOURS,
    "slides": _PRESENTATION_COLOURS,
    "talk": _PRESENTATION_COLOURS,
    "monochrome": _MONOCHROME_COLOURS,
    "mono": _MONOCHROME_COLOURS,
    "bw": _MONOCHROME_COLOURS,
    "gray": _MONOCHROME_COLOURS,
    "grey": _MONOCHROME_COLOURS,
    "dark": _DARK_COLOURS,
}

_REFERENCE_COLOURS = {
    "black": "#111111",
    "text": "#222222",
    "dark_grey": "#4D4D4D",
    "grey": "#7F7F7F",
    "light_grey": "#D0D0D0",
    "very_light_grey": "#EFEFEF",
    "highlight": "#F0E442",
    "white": "#FFFFFF",
}

_LINESTYLES_MONO = ("-", "--", "-.", ":")


# ---------------------------------------------------------------------------
# Font system
# ---------------------------------------------------------------------------
# Include common CJK fonts first.  Matplotlib will use the first installed font
# that can resolve a glyph.  The JP/TC/HK variants are included because many
# Linux environments ship one of them, and they still cover Chinese glyphs well
# enough for figure labels.

_CJK_SANS_SERIF = [
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

_SERIF_STACK = [
    "Times New Roman",
    "Times",
    "Noto Serif CJK SC",
    "Noto Serif CJK JP",
    "Source Han Serif SC",
    "Songti SC",
    "SimSun",
    "DejaVu Serif",
]


# ---------------------------------------------------------------------------
# rcParams presets
# ---------------------------------------------------------------------------

_BASE_STYLE: dict[str, Any] = {
    # Fonts and math text.
    "font.family": "sans-serif",
    "font.sans-serif": _CJK_SANS_SERIF,
    "font.serif": _SERIF_STACK,
    "axes.unicode_minus": False,
    "mathtext.fontset": "dejavusans",
    "mathtext.default": "regular",
    "text.usetex": False,
    # Figure and axes background.
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white",
    # Avoid implicit resizing of final journal figures.  Use save_figure(...,
    # tight=True) or fig.savefig(..., bbox_inches='tight') when you want tight
    # cropping for a specific file.
    "savefig.bbox": None,
    "savefig.pad_inches": 0.03,
    "figure.autolayout": False,
    # Vector export: keep text editable in PDF/SVG editors where possible.
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
    # Axes.
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.axisbelow": True,
    "axes.grid": False,
    "axes.edgecolor": _REFERENCE_COLOURS["text"],
    "axes.labelcolor": _REFERENCE_COLOURS["text"],
    "axes.titlecolor": _REFERENCE_COLOURS["text"],
    "axes.titleweight": "bold",
    "axes.titlepad": 5.0,
    "axes.labelpad": 4.0,
    # Ticks.
    "xtick.direction": "out",
    "ytick.direction": "out",
    "xtick.color": _REFERENCE_COLOURS["text"],
    "ytick.color": _REFERENCE_COLOURS["text"],
    "xtick.minor.visible": True,
    "ytick.minor.visible": True,
    # Grid.
    "grid.color": _REFERENCE_COLOURS["light_grey"],
    "grid.linewidth": 0.55,
    "grid.linestyle": "-",
    "grid.alpha": 0.45,
    # Lines, markers, patches.
    "patch.linewidth": 0.7,
    # Legend.
    "legend.frameon": False,
    "legend.handlelength": 1.5,
    "legend.handletextpad": 0.45,
    "legend.borderaxespad": 0.35,
    "legend.labelspacing": 0.35,
    "legend.columnspacing": 0.9,
    "legend.title_fontsize": 8.0,
}

_JOURNAL_SINGLE_RAW = {
    **_BASE_STYLE,
    "figure.figsize": (3.54, 2.55),  # about 90 mm wide, single-column friendly.
    "figure.dpi": 130,
    "savefig.dpi": 360,
    "font.size": 8.6,
    "axes.titlesize": 9.0,
    "axes.labelsize": 9.0,
    "xtick.labelsize": 8.0,
    "ytick.labelsize": 8.0,
    "legend.fontsize": 7.8,
    "legend.title_fontsize": 7.8,
    "axes.linewidth": 0.82,
    "lines.linewidth": 1.35,
    "lines.markersize": 4.2,
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "xtick.major.width": 0.72,
    "ytick.major.width": 0.72,
    "xtick.minor.size": 1.8,
    "ytick.minor.size": 1.8,
    "xtick.minor.width": 0.55,
    "ytick.minor.width": 0.55,
}

_JOURNAL_COMPACT_RAW = {
    **_JOURNAL_SINGLE_RAW,
    "figure.figsize": (3.35, 2.25),
    "font.size": 8.0,
    "axes.titlesize": 8.3,
    "axes.labelsize": 8.3,
    "xtick.labelsize": 7.4,
    "ytick.labelsize": 7.4,
    "legend.fontsize": 7.0,
    "legend.title_fontsize": 7.0,
    "lines.linewidth": 1.15,
    "lines.markersize": 3.7,
}

_JOURNAL_DOUBLE_RAW = {
    **_JOURNAL_SINGLE_RAW,
    "figure.figsize": (7.16, 3.85),  # about 182 mm wide, double-column friendly.
    "font.size": 9.0,
    "axes.titlesize": 9.6,
    "axes.labelsize": 9.6,
    "xtick.labelsize": 8.4,
    "ytick.labelsize": 8.4,
    "legend.fontsize": 8.2,
    "legend.title_fontsize": 8.2,
    "lines.linewidth": 1.45,
    "lines.markersize": 4.5,
}

_JOURNAL_LARGE_RAW = {
    **_JOURNAL_SINGLE_RAW,
    "figure.figsize": (4.6, 3.25),
    "font.size": 9.6,
    "axes.titlesize": 10.2,
    "axes.labelsize": 10.2,
    "xtick.labelsize": 8.8,
    "ytick.labelsize": 8.8,
    "legend.fontsize": 8.6,
    "legend.title_fontsize": 8.6,
    "lines.linewidth": 1.55,
    "lines.markersize": 4.8,
}

_JOURNAL_GRID_RAW = {
    **_JOURNAL_SINGLE_RAW,
    "axes.grid": True,
    "grid.alpha": 0.36,
    "grid.linewidth": 0.50,
}

_REPORT_RAW = {
    **_BASE_STYLE,
    "figure.figsize": (5.9, 3.8),
    "figure.dpi": 125,
    "savefig.dpi": 320,
    "font.size": 10.0,
    "axes.titlesize": 11.0,
    "axes.labelsize": 11.0,
    "xtick.labelsize": 9.2,
    "ytick.labelsize": 9.2,
    "legend.fontsize": 9.0,
    "legend.title_fontsize": 9.0,
    "axes.linewidth": 0.9,
    "lines.linewidth": 1.65,
    "lines.markersize": 5.0,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "xtick.major.width": 0.8,
    "ytick.major.width": 0.8,
    "xtick.minor.size": 2.0,
    "ytick.minor.size": 2.0,
    "xtick.minor.width": 0.6,
    "ytick.minor.width": 0.6,
}

_NOTEBOOK_RAW = {
    **_REPORT_RAW,
    "figure.figsize": (6.8, 4.2),
    "figure.dpi": 110,
    "savefig.dpi": 220,
    "font.size": 11.0,
    "axes.titlesize": 12.5,
    "axes.labelsize": 12.0,
    "xtick.labelsize": 10.0,
    "ytick.labelsize": 10.0,
    "legend.fontsize": 9.8,
    "legend.title_fontsize": 9.8,
    "axes.grid": True,
    "grid.alpha": 0.30,
    "lines.linewidth": 1.85,
    "lines.markersize": 5.5,
}

_PRESENTATION_RAW = {
    **_BASE_STYLE,
    "figure.figsize": (7.8, 4.5),
    "figure.dpi": 110,
    "savefig.dpi": 220,
    "font.size": 14.0,
    "axes.titlesize": 16.0,
    "axes.labelsize": 15.0,
    "xtick.labelsize": 12.5,
    "ytick.labelsize": 12.5,
    "legend.fontsize": 12.5,
    "legend.title_fontsize": 12.5,
    "axes.linewidth": 1.15,
    "lines.linewidth": 2.45,
    "lines.markersize": 6.5,
    "xtick.major.size": 4.5,
    "ytick.major.size": 4.5,
    "xtick.major.width": 1.0,
    "ytick.major.width": 1.0,
    "xtick.minor.size": 2.6,
    "ytick.minor.size": 2.6,
    "xtick.minor.width": 0.8,
    "ytick.minor.width": 0.8,
}

_POSTER_RAW = {
    **_PRESENTATION_RAW,
    "figure.figsize": (9.2, 5.6),
    "font.size": 17.0,
    "axes.titlesize": 20.0,
    "axes.labelsize": 18.5,
    "xtick.labelsize": 15.0,
    "ytick.labelsize": 15.0,
    "legend.fontsize": 14.5,
    "legend.title_fontsize": 14.5,
    "axes.linewidth": 1.35,
    "lines.linewidth": 3.0,
    "lines.markersize": 8.0,
}

_DARK_RAW = {
    **_NOTEBOOK_RAW,
    "figure.facecolor": "#111111",
    "axes.facecolor": "#111111",
    "savefig.facecolor": "#111111",
    "savefig.edgecolor": "#111111",
    "axes.edgecolor": "#E6E6E6",
    "axes.labelcolor": "#F0F0F0",
    "axes.titlecolor": "#F0F0F0",
    "text.color": "#F0F0F0",
    "xtick.color": "#E6E6E6",
    "ytick.color": "#E6E6E6",
    "grid.color": "#FFFFFF",
    "grid.alpha": 0.16,
    "axes.grid": True,
}


def _line_cycler(palette_name: str, *, monochrome: bool = False):
    """Return a Matplotlib property cycler for a palette."""
    colours = _COLOUR_CYCLES[palette_name]
    if monochrome:
        return cycler(color=colours) + cycler(linestyle=_LINESTYLES_MONO)
    return cycler(color=colours)


def _with_cycle(params: Mapping[str, Any], palette_name: str, *, monochrome: bool = False) -> dict[str, Any]:
    """Return a copy of *params* with a valid axes.prop_cycle."""
    styled = dict(params)
    styled["axes.prop_cycle"] = _line_cycler(palette_name, monochrome=monochrome)
    return styled


# Public preset mapping.  It deliberately contains valid rcParams only, so old
# code such as ``plt.rcParams.update(PLOT_STYLE_PRESETS["journal"])`` continues
# to work.  The previous ``axes.prop_cycle: None`` placeholder has been removed.
PLOT_STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "journal": _with_cycle(_JOURNAL_SINGLE_RAW, "journal"),
    "journal_single": _with_cycle(_JOURNAL_SINGLE_RAW, "journal"),
    "journal_compact": _with_cycle(_JOURNAL_COMPACT_RAW, "journal"),
    "journal_double": _with_cycle(_JOURNAL_DOUBLE_RAW, "journal"),
    "journal_large": _with_cycle(_JOURNAL_LARGE_RAW, "journal"),
    "journal_grid": _with_cycle(_JOURNAL_GRID_RAW, "journal"),
    "journal_bw": _with_cycle(_JOURNAL_SINGLE_RAW, "monochrome", monochrome=True),
    "monochrome": _with_cycle(_JOURNAL_SINGLE_RAW, "monochrome", monochrome=True),
    "report": _with_cycle(_REPORT_RAW, "academic"),
    "thesis": _with_cycle(_REPORT_RAW, "academic"),
    "notebook": _with_cycle(_NOTEBOOK_RAW, "muted"),
    "presentation": _with_cycle(_PRESENTATION_RAW, "presentation"),
    "poster": _with_cycle(_POSTER_RAW, "presentation"),
    "dark": _with_cycle(_DARK_RAW, "dark"),
}

_STYLE_ALIASES = {
    # Original/backwards-compatible alias.
    "paper": "journal",
    # Common shorthand.
    "single": "journal_single",
    "double": "journal_double",
    "compact": "journal_compact",
    "large": "journal_large",
    "grid": "journal_grid",
    "clean_grid": "journal_grid",
    "paper_bw": "journal_bw",
    "bw": "journal_bw",
    "mono": "monochrome",
    "black_white": "journal_bw",
    "black-and-white": "journal_bw",
    "gray": "journal_bw",
    "grey": "journal_bw",
    "grayscale": "journal_bw",
    "greyscale": "journal_bw",
    "slide": "presentation",
    "slides": "presentation",
    "talk": "presentation",
    "screen": "presentation",
    "lab": "notebook",
}

_STYLE_TO_PALETTE = {
    "journal": "journal",
    "journal_single": "journal",
    "journal_compact": "journal",
    "journal_double": "journal",
    "journal_large": "journal",
    "journal_grid": "journal",
    "journal_bw": "monochrome",
    "monochrome": "monochrome",
    "report": "academic",
    "thesis": "academic",
    "notebook": "muted",
    "presentation": "presentation",
    "poster": "presentation",
    "dark": "dark",
}

_FONT_SIZE_KEYS = (
    "font.size",
    "axes.titlesize",
    "axes.labelsize",
    "xtick.labelsize",
    "ytick.labelsize",
    "legend.fontsize",
    "legend.title_fontsize",
)

_LINE_SIZE_KEYS = (
    "axes.linewidth",
    "lines.linewidth",
    "lines.markersize",
    "xtick.major.size",
    "ytick.major.size",
    "xtick.major.width",
    "ytick.major.width",
    "xtick.minor.size",
    "ytick.minor.size",
    "xtick.minor.width",
    "ytick.minor.width",
    "grid.linewidth",
    "patch.linewidth",
)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def _resolve_style_name(style: str) -> str:
    """Return the canonical style name for *style*."""
    name = _STYLE_ALIASES.get(style, style)
    if name not in PLOT_STYLE_PRESETS:
        supported = ", ".join(available_styles(include_aliases=True))
        raise ValueError(f"unknown plot style {style!r}; supported: {supported}")
    return name


def available_styles(*, include_aliases: bool = False) -> tuple[str, ...]:
    """Return supported style names.

    Parameters
    ----------
    include_aliases:
        If True, include shorthand and backwards-compatible aliases such as
        ``paper``, ``bw``, ``talk`` and ``slides``.
    """
    names = list(PLOT_STYLE_PRESETS)
    if include_aliases:
        names.extend(_STYLE_ALIASES)
    return tuple(dict.fromkeys(names))


def available_palettes() -> tuple[str, ...]:
    """Return supported colour palette names."""
    return tuple(_COLOUR_CYCLES)


def palette(name: str = "journal") -> tuple[str, ...]:
    """Return a finite tuple of colours for *name*.

    This is useful when you need direct colour values for annotations, fills,
    or external plotting libraries.
    """
    if name not in _COLOUR_CYCLES:
        supported = ", ".join(available_palettes())
        raise ValueError(f"unknown colour palette {name!r}; supported: {supported}")
    return _COLOUR_CYCLES[name]


def colour_cycle(name: str = "journal"):
    """Return an infinite cycle of plotting colours.

    This keeps the original British-English function name for compatibility.
    """
    return cycle(palette(name))


def color_cycle(name: str = "journal"):
    """American-English alias for :func:`colour_cycle`."""
    return colour_cycle(name)


def reference_colours() -> dict[str, str]:
    """Return named neutral/highlight colours used by the style system."""
    return dict(_REFERENCE_COLOURS)


def _scale_rcparams(params: dict[str, Any], *, font_scale: float = 1.0, line_scale: float = 1.0) -> dict[str, Any]:
    """Scale numeric font and line rcParams."""
    scaled = dict(params)
    if font_scale <= 0:
        raise ValueError("font_scale must be positive")
    if line_scale <= 0:
        raise ValueError("line_scale must be positive")

    if font_scale != 1.0:
        for key in _FONT_SIZE_KEYS:
            value = scaled.get(key)
            if isinstance(value, (int, float)):
                scaled[key] = value * font_scale

    if line_scale != 1.0:
        for key in _LINE_SIZE_KEYS:
            value = scaled.get(key)
            if isinstance(value, (int, float)):
                scaled[key] = value * line_scale
    return scaled


def _style_rcparams(
    style: str,
    *,
    font_scale: float = 1.0,
    line_scale: float = 1.0,
    palette_name: str | None = None,
    rc: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return Matplotlib rcParams for a named style.

    This private helper intentionally remains available for old code that may
    have imported it despite it not being part of ``__all__``.
    """
    name = _resolve_style_name(style)
    params = dict(PLOT_STYLE_PRESETS[name])

    if palette_name is not None:
        if palette_name not in _COLOUR_CYCLES:
            supported = ", ".join(available_palettes())
            raise ValueError(f"unknown colour palette {palette_name!r}; supported: {supported}")
        params["axes.prop_cycle"] = _line_cycler(
            palette_name,
            monochrome=palette_name in {"monochrome", "mono", "bw", "gray", "grey"},
        )

    params = _scale_rcparams(params, font_scale=font_scale, line_scale=line_scale)

    if rc:
        params.update(rc)
    return params


@contextmanager
def plot_style(
    style: str = "journal",
    *,
    font_scale: float = 1.0,
    line_scale: float = 1.0,
    palette_name: str | None = None,
    rc: Mapping[str, Any] | None = None,
) -> Iterator[None]:
    """Temporarily apply a named plotting style.

    Examples
    --------
    >>> with plot_style("journal"):
    ...     ...

    Optional keyword arguments allow quick local tuning without creating a new
    preset:

    >>> with plot_style("journal", font_scale=1.08, line_scale=1.1):
    ...     ...
    """
    import matplotlib.pyplot as plt

    with plt.rc_context(_style_rcparams(style, font_scale=font_scale, line_scale=line_scale, palette_name=palette_name, rc=rc)):
        yield


def set_plot_style(
    style: str = "journal",
    *,
    font_scale: float = 1.0,
    line_scale: float = 1.0,
    palette_name: str | None = None,
    rc: Mapping[str, Any] | None = None,
) -> None:
    """Apply a named plotting style to global Matplotlib rcParams."""
    import matplotlib.pyplot as plt

    plt.rcParams.update(_style_rcparams(style, font_scale=font_scale, line_scale=line_scale, palette_name=palette_name, rc=rc))


def available_cjk_fonts() -> tuple[str, ...]:
    """Return CJK-capable font candidates currently visible to Matplotlib."""
    from matplotlib import font_manager

    installed = {font.name for font in font_manager.fontManager.ttflist}
    return tuple(font for font in _CJK_SANS_SERIF if font in installed)


def use_cjk_font(preferred: str | Sequence[str] | None = None) -> tuple[str, ...]:
    """Prioritise installed CJK fonts in the active Matplotlib session.

    Parameters
    ----------
    preferred:
        A font name or a sequence of font names to try first.  Missing fonts are
        harmless; Matplotlib will fall back to the rest of the stack.

    Returns
    -------
    tuple[str, ...]
        The font stack that was assigned to ``rcParams['font.sans-serif']``.
    """
    import matplotlib.pyplot as plt

    if preferred is None:
        requested: list[str] = []
    elif isinstance(preferred, str):
        requested = [preferred]
    else:
        requested = list(preferred)

    stack = tuple(dict.fromkeys([*requested, *_CJK_SANS_SERIF]))
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = list(stack)
    plt.rcParams["axes.unicode_minus"] = False
    return stack


def despine(ax: Any | None = None, *, top: bool = True, right: bool = True, left: bool = False, bottom: bool = False) -> Any:
    """Hide selected axes spines and return the axes."""
    import matplotlib.pyplot as plt

    if ax is None:
        ax = plt.gca()
    sides = {"top": top, "right": right, "left": left, "bottom": bottom}
    for side, hide in sides.items():
        if side in ax.spines:
            ax.spines[side].set_visible(not hide)
    return ax


def panel_label(
    ax: Any,
    label: str = "a",
    *,
    x: float = -0.12,
    y: float = 1.04,
    fontsize: float | None = None,
    fontweight: str = "bold",
    ha: str = "left",
    va: str = "bottom",
    **kwargs: Any,
) -> Any:
    """Add a journal-style panel label to one axes.

    The label is placed in axes coordinates, so it remains stable when data
    limits change.
    """
    if fontsize is None:
        import matplotlib.pyplot as plt

        size = plt.rcParams.get("axes.labelsize", plt.rcParams.get("font.size", 9.0))
        fontsize = float(size) if isinstance(size, (int, float)) else None

    text_kwargs = {
        "transform": ax.transAxes,
        "fontsize": fontsize,
        "fontweight": fontweight,
        "ha": ha,
        "va": va,
        "clip_on": False,
    }
    text_kwargs.update(kwargs)
    text2d = getattr(ax, "text2D", None)
    if callable(text2d):
        return text2d(x, y, label, **text_kwargs)
    return ax.text(x, y, label, **text_kwargs)


def _flatten_axes(axes: Any | None) -> list[Any]:
    """Return axes as a flat list without requiring NumPy."""
    import matplotlib.pyplot as plt

    if axes is None:
        return list(plt.gcf().axes)
    if hasattr(axes, "transAxes") and hasattr(axes, "text"):
        return [axes]
    if isinstance(axes, Mapping):
        axes = axes.values()
    if hasattr(axes, "flat"):
        axes = list(axes.flat)
    if not isinstance(axes, Iterable) or isinstance(axes, (str, bytes)):
        return [axes]

    flat: list[Any] = []
    for item in axes:
        if item is None:
            continue
        if hasattr(item, "transAxes") and hasattr(item, "text"):
            flat.append(item)
        elif isinstance(item, Iterable) and not isinstance(item, (str, bytes)):
            flat.extend(_flatten_axes(item))
        else:
            flat.append(item)
    return flat


def _default_panel_labels(n: int, *, case: str = "lower") -> tuple[str, ...]:
    """Return default panel labels for n panels."""
    letters = "abcdefghijklmnopqrstuvwxyz"
    labels = []
    for i in range(n):
        q, r = divmod(i, len(letters))
        label = letters[r] if q == 0 else f"{letters[r]}{q + 1}"
        labels.append(label.upper() if case == "upper" else label)
    return tuple(labels)


def add_panel_labels(
    axes: Any | None = None,
    labels: Sequence[str] | None = None,
    *,
    case: str = "lower",
    x: float = -0.12,
    y: float = 1.04,
    **kwargs: Any,
) -> list[Any]:
    """Add panel labels to a sequence/grid of axes and return text artists.

    Examples
    --------
    >>> fig, axs = plt.subplots(2, 2)
    >>> add_panel_labels(axs)              # a, b, c, d
    >>> add_panel_labels(axs, ["A", "B", "C", "D"], x=-0.1)
    """
    flat_axes = _flatten_axes(axes)
    if labels is None:
        labels = _default_panel_labels(len(flat_axes), case=case)
    if len(labels) < len(flat_axes):
        raise ValueError("not enough labels for the number of axes")
    return [panel_label(ax, label, x=x, y=y, **kwargs) for ax, label in zip(flat_axes, labels)]


def move_titles_to_panel_labels(
    axes: Any | None = None,
    labels: Sequence[str] | None = None,
    *,
    clear_titles: bool = True,
    **kwargs: Any,
) -> list[Any]:
    """Convert existing axes titles or supplied labels into panel labels.

    This is useful when an old script used ``ax.set_title('a')`` or
    ``ax.set_title('A')`` for subplot tags.  By default the original titles are
    cleared after the panel labels are added.
    """
    flat_axes = _flatten_axes(axes)
    if labels is None:
        labels = [ax.get_title() or label for ax, label in zip(flat_axes, _default_panel_labels(len(flat_axes)))]
    artists = add_panel_labels(flat_axes, labels, **kwargs)
    if clear_titles:
        for ax in flat_axes:
            ax.set_title("")
    return artists


# Short aliases for panel-label helpers.
label_panel = panel_label
label_subplots = add_panel_labels
set_panel_labels = add_panel_labels


def save_figure(
    path: str | Path | Any,
    fig: Any | None = None,
    *,
    tight: bool = True,
    dpi: int | float | None = None,
    transparent: bool = False,
    close: bool = False,
    **kwargs: Any,
) -> Path | Any:
    """Save a figure with sensible scientific-figure defaults.

    Unlike the style presets, this helper opts into tight cropping explicitly.
    This avoids the hidden global-size change caused by setting
    ``savefig.bbox='tight'`` in rcParams.
    """
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.gcf()

    if isinstance(path, (str, PathLike)):
        output: Path | Any = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        save_target: Any = output
    else:
        # File-like objects such as io.BytesIO are supported because
        # matplotlib.figure.Figure.savefig supports them.
        output = path
        save_target = path

    save_kwargs: dict[str, Any] = {
        "transparent": transparent,
    }
    if dpi is not None:
        save_kwargs["dpi"] = dpi
    if tight:
        save_kwargs.setdefault("bbox_inches", "tight")
        save_kwargs.setdefault("pad_inches", 0.04)
    save_kwargs.update(kwargs)

    fig.savefig(save_target, **save_kwargs)
    if close:
        plt.close(fig)
    return output


def mm_to_inches(mm: float) -> float:
    """Convert millimetres to inches for figure sizing."""
    return mm / 25.4


def cm_to_inches(cm: float) -> float:
    """Convert centimetres to inches for figure sizing."""
    return cm / 2.54


__all__ = [
    "PLOT_STYLE_PRESETS",
    "add_panel_labels",
    "available_cjk_fonts",
    "available_palettes",
    "available_styles",
    "cm_to_inches",
    "color_cycle",
    "colour_cycle",
    "despine",
    "label_panel",
    "label_subplots",
    "mm_to_inches",
    "move_titles_to_panel_labels",
    "palette",
    "panel_label",
    "plot_style",
    "reference_colours",
    "save_figure",
    "set_panel_labels",
    "set_plot_style",
    "use_cjk_font",
]
