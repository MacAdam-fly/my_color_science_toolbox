"""Compare D65 MacAdam limits and an RGBC display as 3D solids."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

SHOW_INTERACTIVE = "--show" in sys.argv
SKIP_SAVE = "--no-save" in sys.argv

if not SHOW_INTERACTIVE:
    matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from color.constants import D65_XYZ
from color.gamut import compute_LCH_gamut_boundary, macadam_limits, DisplayPrimaries
from color.plot import plot_3d_surface, plot_3d_wireframe, plot_style

from _example_helpers import OUTPUT_DIR, rgbc_primaries, save_figure


def _plot_xyy_solid(ax, boundary, *, color: str, label: str) -> None:
    """Plot a boundary surface in CIE xyY coordinates."""
    xyY = boundary.to_xyY()
    plot_3d_surface(
        xyY[..., 0],
        xyY[..., 1],
        xyY[..., 2],
        ax=ax,
        color=color,
        alpha=0.30,
        linewidth=0.0,
        grid=True,
        view=(24.0, -58.0),
    )
    plot_3d_wireframe(
        xyY[..., 0],
        xyY[..., 1],
        xyY[..., 2],
        ax=ax,
        color=color,
        linewidth=0.35,
        rstride=3,
        cstride=5,
        grid=True,
        view=(24.0, -58.0),
    )
    ax.plot([], [], [], color=color, label=label)


def _plot_lab_solid(ax, boundary, *, color: str, label: str) -> None:
    """Plot a boundary surface in CIE Lab coordinates."""
    lab = boundary.to_Lab()
    plot_3d_surface(
        lab[..., 1],
        lab[..., 2],
        lab[..., 0],
        ax=ax,
        color=color,
        alpha=0.30,
        linewidth=0.0,
        grid=True,
        view=(22.0, -46.0),
    )
    plot_3d_wireframe(
        lab[..., 1],
        lab[..., 2],
        lab[..., 0],
        ax=ax,
        color=color,
        linewidth=0.35,
        rstride=3,
        cstride=5,
        grid=True,
        view=(22.0, -46.0),
    )
    ax.plot([], [], [], color=color, label=label)


def _style_xyy_axis(ax) -> None:
    """Apply fixed axes for xyY solids."""
    ax.set_title("CIE xyY surface")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("Y")
    ax.set_xlim(0.0, 0.85)
    ax.set_ylim(0.0, 0.9)
    ax.set_zlim(0.0, 100.0)
    ax.set_box_aspect((0.85, 0.9, 0.75))


def _style_lab_axis(ax, boundaries) -> None:
    """Apply shared axes for Lab solids."""
    lab_points = np.vstack([boundary.to_Lab().reshape(-1, 3) for boundary in boundaries])
    ab_max = float(np.nanmax(np.abs(lab_points[:, 1:3])))
    ab_limit = max(120.0, np.ceil(ab_max / 20.0) * 20.0)
    ax.set_title("CIE Lab surface")
    ax.set_xlabel("a*")
    ax.set_ylabel("b*")
    ax.set_zlabel("L*")
    ax.set_xlim(-ab_limit, ab_limit)
    ax.set_ylim(-ab_limit, ab_limit)
    ax.set_zlim(0.0, 100.0)
    ax.set_box_aspect((1.0, 1.0, 0.75))


def main() -> None:
    """Run the MacAdam / RGBC 3D solid comparison."""
    L_values = np.arange(0.0, 101.0, 1.0)
    hue_values = np.arange(0.0, 361.0, 2.0)

    macadam_d65 = macadam_limits(
        "D65",
        L_values=L_values,
        hue_values=hue_values,
        C_upper=300.0,
        iterations=10,
    )
    rgbc = compute_LCH_gamut_boundary(
        # rgbc_primaries(), # swith to this for a more accurate RGBC gamut
        DisplayPrimaries.from_RGB_colourspace("sRGB"),
        whitepoint_XYZ=D65_XYZ,
        L_values=L_values,
        hue_values=hue_values,
        C_upper=350.0,
        iterations=10,
    )

    for name, boundary in (("MacAdam D65", macadam_d65), ("sRGB", rgbc)):
        print(f"{name:12s} Lab volume: {boundary.lab_volume():.2f}")
        print(f"{name:12s} projected a*b* area: {boundary.projected_ab_area():.2f}")

    colors = {
        "MacAdam D65": "#0072B2",
        "sRGB": "#D55E00",
    }

    with plot_style("journal_double"):
        fig = plt.figure(figsize=(10.5, 4.8))
        ax_xyy = fig.add_subplot(1, 2, 1, projection="3d")
        ax_lab = fig.add_subplot(1, 2, 2, projection="3d")

        _plot_xyy_solid(ax_xyy, macadam_d65, color=colors["MacAdam D65"], label="MacAdam D65")
        _plot_xyy_solid(ax_xyy, rgbc, color=colors["sRGB"], label="sRGB")
        _style_xyy_axis(ax_xyy)

        _plot_lab_solid(ax_lab, macadam_d65, color=colors["MacAdam D65"], label="MacAdam D65")
        _plot_lab_solid(ax_lab, rgbc, color=colors["sRGB"], label="sRGB")
        _style_lab_axis(ax_lab, (macadam_d65, rgbc))

        handles = [
            Patch(facecolor=colors["MacAdam D65"], edgecolor=colors["MacAdam D65"], alpha=0.35, label="MacAdam D65"),
            Patch(facecolor=colors["sRGB"], edgecolor=colors["sRGB"], alpha=0.35, label="sRGB"),
        ]
        fig.legend(handles=handles, loc="upper center", ncol=2, frameon=False)
        fig.subplots_adjust(top=0.84, wspace=0.18)
        output_name = "10_macadam_rgbc_xyY_lab_solids.png"

        if SKIP_SAVE:
            print("Skipping file save because --no-save was passed.")
        elif SHOW_INTERACTIVE:
            path = OUTPUT_DIR / output_name
            fig.savefig(path, dpi=150)
            print(f"Plot saved to {path}")
        else:
            save_figure(fig, output_name)
            return

        if SHOW_INTERACTIVE:
            print("Showing interactive matplotlib window. Drag the 3D axes to rotate.")
            plt.show()
        else:
            plt.close(fig)



if __name__ == "__main__":
    main()
