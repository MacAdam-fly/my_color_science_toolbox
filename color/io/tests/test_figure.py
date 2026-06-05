"""Tests for figure IO helpers."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from color.io import save_figure


def test_save_figure_writes_file(tmp_path) -> None:
    fig, ax = plt.subplots()
    ax.plot([0.0, 1.0], [0.0, 1.0])

    output = save_figure(tmp_path / "figure.png", fig=fig)

    assert output.exists()
    assert output.stat().st_size > 0
    plt.close(fig)
