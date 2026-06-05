"""Opinionated Matplotlib style helpers for scientific figures.

The visual system is intentionally small: public styles express broad output
targets, while minor size and line variations are handled through
``font_scale``, ``line_scale`` and local ``rc`` overrides.

Journal-oriented presets intentionally suppress axes titles.  Publication
figures should use panel labels plus captions instead of in-axes titles; users
can still override the title rcParams explicitly when needed.
"""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import contextmanager
from itertools import cycle
from typing import Any, Iterator

from cycler import cycler

from .fonts import CJK_SANS_SERIF, SERIF_STACK


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

_COLOUR_CYCLES: dict[str, tuple[str, ...]] = {
    "journal": _ACADEMIC_COLOURS,
    "presentation": _PRESENTATION_COLOURS,
    "monochrome": _MONOCHROME_COLOURS,
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
# rcParams presets
# ---------------------------------------------------------------------------

_BASE_STYLE: dict[str, Any] = {
    # Fonts and math text.
    "font.family": "sans-serif",
    "font.sans-serif": CJK_SANS_SERIF,
    "font.serif": SERIF_STACK,
    "axes.unicode_minus": False,
    "mathtext.fontset": "dejavusans",
    "mathtext.default": "regular",
    "text.usetex": False,
    # Figure and axes background.
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.facecolor": "white",
    "savefig.edgecolor": "white",
    # Avoid implicit resizing of final journal figures.  Use
    # color.io.save_figure(..., tight=True) or fig.savefig(...,
    # bbox_inches='tight') when you want tight cropping for a specific file.
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
    "axes.titleweight": "normal",
    "axes.titlepad": 4.0,
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

_JOURNAL_NO_TITLE = {
    "axes.titlesize": 0.0,
    "axes.titlepad": 0.0,
    "axes.titleweight": "normal",
}

_JOURNAL_SINGLE_RAW = {
    **_BASE_STYLE,
    **_JOURNAL_NO_TITLE,
    "figure.figsize": (3.54, 2.55),  # about 90 mm wide, single-column friendly.
    "figure.dpi": 130,
    "savefig.dpi": 360,
    "font.size": 8.6,
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

_JOURNAL_DOUBLE_RAW = {
    **_JOURNAL_SINGLE_RAW,
    "figure.figsize": (7.16, 3.85),  # about 182 mm wide, double-column friendly.
    "font.size": 9.0,
    "axes.labelsize": 9.6,
    "xtick.labelsize": 8.4,
    "ytick.labelsize": 8.4,
    "legend.fontsize": 8.2,
    "legend.title_fontsize": 8.2,
    "lines.linewidth": 1.45,
    "lines.markersize": 4.5,
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


# Preset mapping.  It deliberately contains valid rcParams only.
PLOT_STYLE_PRESETS: dict[str, dict[str, Any]] = {
    "journal": _with_cycle(_JOURNAL_SINGLE_RAW, "journal"),
    "journal_double": _with_cycle(_JOURNAL_DOUBLE_RAW, "journal"),
    "presentation": _with_cycle(_PRESENTATION_RAW, "presentation"),
    "monochrome": _with_cycle(_JOURNAL_SINGLE_RAW, "monochrome", monochrome=True),
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
    if style not in PLOT_STYLE_PRESETS:
        supported = ", ".join(available_styles(include_aliases=True))
        raise ValueError(f"unknown plot style {style!r}; supported: {supported}")
    return style


def available_styles(*, include_aliases: bool = False) -> tuple[str, ...]:
    """Return supported style names.

    Parameters
    ----------
    include_aliases:
        Kept for call-site compatibility. No extra aliases are exposed.
    """
    return tuple(PLOT_STYLE_PRESETS)


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
    """Return an infinite cycle of plotting colours."""
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
            monochrome=palette_name == "monochrome",
        )

    params = _scale_rcparams(params, font_scale=font_scale, line_scale=line_scale)

    if rc:
        params.update(rc)
    return params


def style_rcparams(
    style: str = "journal",
    *,
    font_scale: float = 1.0,
    line_scale: float = 1.0,
    palette_name: str | None = None,
    rc: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a copy of rcParams for a named plotting style.

    This is the safe public way to inspect or reuse a style dictionary.  The
    returned mapping is independent from ``PLOT_STYLE_PRESETS``.
    """
    return _style_rcparams(
        style,
        font_scale=font_scale,
        line_scale=line_scale,
        palette_name=palette_name,
        rc=rc,
    )


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

    with plt.rc_context(style_rcparams(style, font_scale=font_scale, line_scale=line_scale, palette_name=palette_name, rc=rc)):
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

    plt.rcParams.update(style_rcparams(style, font_scale=font_scale, line_scale=line_scale, palette_name=palette_name, rc=rc))


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


def mm_to_inches(mm: float) -> float:
    """Convert millimetres to inches for figure sizing."""
    return mm / 25.4


def cm_to_inches(cm: float) -> float:
    """Convert centimetres to inches for figure sizing."""
    return cm / 2.54


__all__ = [
    "available_palettes",
    "available_styles",
    "cm_to_inches",
    "colour_cycle",
    "despine",
    "mm_to_inches",
    "palette",
    "plot_style",
    "reference_colours",
    "set_plot_style",
    "style_rcparams",
]
