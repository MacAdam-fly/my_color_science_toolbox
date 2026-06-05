"""Figure export helpers."""

from __future__ import annotations

from os import PathLike
from pathlib import Path
from typing import Any


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
    """Save a Matplotlib figure with explicit scientific-figure defaults."""
    import matplotlib.pyplot as plt

    if fig is None:
        fig = plt.gcf()

    if isinstance(path, (str, PathLike)):
        output: Path | Any = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        save_target: Any = output
    else:
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


__all__ = ["save_figure"]
