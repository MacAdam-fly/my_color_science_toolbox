"""Plot style helpers."""

from __future__ import annotations

from contextlib import contextmanager
from itertools import cycle
from typing import Iterator


_JOURNAL_COLOURS = (
    "#0072B2",  # blue: primary series; Okabe-Ito colourblind-friendly palette.
    "#D55E00",  # vermillion: high-contrast comparison against blue.
    "#009E73",  # bluish green: third categorical series.
    "#CC79A7",  # reddish purple: additional categorical series.
    "#E69F00",  # orange: warm accent or secondary comparison.
    "#56B4E9",  # sky blue: cool accent distinct from primary blue.
    "#000000",  # black: reference, baseline, or neutral emphasis.
    "#F0E442",  # yellow: reserved for highlighted series; use carefully on white.
)

_MONOCHROME_COLOURS = (
    "#000000",  # black: strongest monochrome line.
    "#4d4d4d",  # dark grey: second monochrome series.
    "#7f7f7f",  # mid grey: third monochrome series.
    "#b2b2b2",  # light grey: least prominent monochrome series.
)

_PRESENTATION_COLOURS = (
    "#1f77b4",  # blue: screen-friendly primary series.
    "#ff7f0e",  # orange: warm comparison colour for slides.
    "#2ca02c",  # green: third presentation series.
    "#d62728",  # red: strong highlight colour.
    "#9467bd",  # purple: additional categorical colour.
    "#17becf",  # cyan: cool accent for projected figures.
    "#8c564b",  # brown: subdued category colour.
    "#7f7f7f",  # grey: neutral baseline or reference.
)

_JOURNAL_SINGLE_STYLE = {
    "figure.figsize": (3.5, 2.45),  # approximately 89 mm single-column width.
    "axes.linewidth": 0.75,  # thin axes suitable for compact printed figures.
    "axes.prop_cycle": None,  # filled later with the journal colour cycle.
    "axes.spines.top": False,  # remove top border to reduce visual clutter.
    "axes.spines.right": False,  # remove right border to reduce visual clutter.
    "axes.titlesize": 7,  # compact title size for final journal figures.
    "axes.labelsize": 7,  # axis labels remain readable at single-column size.
    "font.family": "sans-serif",  # use common sans-serif fonts for clean figures.
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],  # preferred fallback chain.
    "font.size": 7,  # base text size aligned with common 5-7 pt final-size guidance.
    "legend.frameon": False,  # frameless legends read cleaner in dense figures.
    "legend.fontsize": 6,  # smaller legend text avoids stealing plot area.
    "lines.linewidth": 1.0,  # clear but lightweight line width for print.
    "lines.markersize": 3.5,  # compact markers for multi-series journal figures.
    "savefig.bbox": "tight",  # trim extra whitespace when saving figures.
    "savefig.dpi": 300,  # common minimum raster resolution for colour/greyscale figures.
    "xtick.direction": "out",  # outward ticks avoid covering plotted data.
    "xtick.labelsize": 6,  # compact x tick labels for final printed size.
    "ytick.direction": "out",  # outward ticks avoid covering plotted data.
    "ytick.labelsize": 6,  # compact y tick labels for final printed size.
}

_JOURNAL_DOUBLE_STYLE = {
    **_JOURNAL_SINGLE_STYLE,
    "figure.figsize": (7.16, 3.9),  # approximately 180-183 mm double-column width.
}

_PRESENTATION_STYLE = {
    "figure.figsize": (7.6, 4.4),  # wider default canvas for slides and reports.
    "axes.linewidth": 1.0,  # slightly heavier axes for projected figures.
    "axes.prop_cycle": None,  # filled later with the presentation colour cycle.
    "axes.spines.top": False,  # remove top border for a cleaner slide style.
    "axes.spines.right": False,  # remove right border for a cleaner slide style.
    "axes.titlesize": 13,  # larger titles for screen viewing.
    "axes.labelsize": 11,  # larger axis labels for projection.
    "font.family": "sans-serif",  # use common sans-serif fonts for screen clarity.
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],  # preferred fallback chain.
    "font.size": 11,  # larger base font for slides and reports.
    "legend.frameon": False,  # frameless legends keep slides uncluttered.
    "legend.fontsize": 10,  # readable legend text for presentation figures.
    "lines.linewidth": 2.0,  # thicker lines remain visible on screens.
    "lines.markersize": 5,  # larger markers for projected scatter points.
    "savefig.bbox": "tight",  # trim extra whitespace when saving figures.
    "savefig.dpi": 180,  # practical raster resolution for slide exports.
    "xtick.direction": "out",  # outward ticks avoid covering plotted data.
    "xtick.labelsize": 10,  # readable x tick labels for presentation figures.
    "ytick.direction": "out",  # outward ticks avoid covering plotted data.
    "ytick.labelsize": 10,  # readable y tick labels for presentation figures.
}

PLOT_STYLE_PRESETS = {
    "journal": _JOURNAL_SINGLE_STYLE,
    "journal_single": _JOURNAL_SINGLE_STYLE,
    "journal_double": _JOURNAL_DOUBLE_STYLE,
    "presentation": _PRESENTATION_STYLE,
}

_STYLE_ALIASES = {
    "paper": "journal",  # backwards-compatible alias for the old project style.
}

_COLOUR_CYCLES = {
    "journal": _JOURNAL_COLOURS,
    "journal_single": _JOURNAL_COLOURS,
    "journal_double": _JOURNAL_COLOURS,
    "paper": _JOURNAL_COLOURS,  # backwards-compatible alias for the old name.
    "monochrome": _MONOCHROME_COLOURS,
    "presentation": _PRESENTATION_COLOURS,
}


def _resolve_style_name(style: str) -> str:
    """Return the canonical style name for *style*."""
    name = _STYLE_ALIASES.get(style, style)
    if name not in PLOT_STYLE_PRESETS:
        supported = ", ".join((*PLOT_STYLE_PRESETS, *_STYLE_ALIASES))
        raise ValueError(f"unknown plot style {style!r}; supported: {supported}")
    return name


def colour_cycle(name: str = "journal"):
    """Return an infinite cycle of plotting colours."""
    if name not in _COLOUR_CYCLES:
        supported = ", ".join(_COLOUR_CYCLES)
        raise ValueError(f"unknown colour cycle {name!r}; supported: {supported}")
    return cycle(_COLOUR_CYCLES[name])


def _style_rcparams(style: str) -> dict:
    """Return matplotlib rcParams for a named style."""
    name = _resolve_style_name(style)
    params = dict(PLOT_STYLE_PRESETS[name])
    from cycler import cycler

    cycle_name = "presentation" if name == "presentation" else "journal"
    params["axes.prop_cycle"] = cycler(color=_COLOUR_CYCLES[cycle_name])
    return params


@contextmanager
def plot_style(style: str = "journal") -> Iterator[None]:
    """Temporarily apply a named plot style using ``matplotlib.rc_context``."""
    import matplotlib.pyplot as plt

    with plt.rc_context(_style_rcparams(style)):
        yield


def set_plot_style(style: str = "journal") -> None:
    """Apply a named plot style to global matplotlib rcParams."""
    import matplotlib.pyplot as plt

    plt.rcParams.update(_style_rcparams(style))


__all__ = [
    "PLOT_STYLE_PRESETS",
    "colour_cycle",
    "plot_style",
    "set_plot_style",
]
