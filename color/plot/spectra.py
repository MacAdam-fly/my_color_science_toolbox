"""Spectral plotting helpers."""

from __future__ import annotations

from typing import Sequence

from color.spectra import MultiSpectralDistribution, SpectralDistribution

from .common import finish_figure, get_figure_axes


def style_spectral_axis(
    ax,
    *,
    title: str | None = None,
    ylabel: str = "Value",
    xlabel: str = "Wavelength (nm)",
    grid: bool = True,
):
    """Apply common styling for spectral plots."""
    if title is not None:
        ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if grid:
        ax.grid(True, alpha=0.3)
    return ax


def plot_spectral_distribution(
    sd: SpectralDistribution,
    *,
    ax=None,
    label: str | None = None,
    title: str | None = None,
    ylabel: str = "Value",
    **kwargs,
):
    """Plot a single-channel spectral distribution."""
    if not isinstance(sd, SpectralDistribution):
        raise TypeError("sd must be a SpectralDistribution")
    fig, ax = get_figure_axes(ax)
    line_label = label if label is not None else (sd.name or None)
    ax.plot(sd.wavelengths, sd.values, label=line_label, **kwargs)
    if line_label:
        ax.legend()
    style_spectral_axis(ax, title=title or sd.name or None, ylabel=ylabel)
    finish_figure(fig)
    return fig, ax


def plot_multi_spectral_distribution(
    msd: MultiSpectralDistribution,
    *,
    ax=None,
    labels: Sequence[str] | None = None,
    title: str | None = None,
    ylabel: str = "Value",
    **kwargs,
):
    """Plot selected channels from a multi-channel spectral distribution."""
    if not isinstance(msd, MultiSpectralDistribution):
        raise TypeError("msd must be a MultiSpectralDistribution")
    fig, ax = get_figure_axes(ax)
    selected = tuple(labels) if labels is not None else msd.labels
    for label in selected:
        if label not in msd.labels:
            raise ValueError(f"label {label!r} is not in {msd.labels}")
        index = msd.labels.index(label)
        ax.plot(msd.wavelengths, msd.values[:, index], label=label, **kwargs)
    ax.legend()
    style_spectral_axis(ax, title=title or msd.name or None, ylabel=ylabel)
    finish_figure(fig)
    return fig, ax


__all__ = [
    "plot_multi_spectral_distribution",
    "plot_spectral_distribution",
    "style_spectral_axis",
]
