"""Load and plot standard observer datasets."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from _datasets_plot_helpers import save_figure
from color.datasets import (
    get_standard_observer,
    list_standard_observer_categories,
    list_standard_observers,
)
from color.plot import plot_cie1931_diagram, plot_lines, plot_style


def main() -> None:
    print("Categories:", list_standard_observer_categories())
    print("CMFs count:", len(list_standard_observers("cmfs")))
    print("Cone fundamentals count:", len(list_standard_observers("cone")))

    xyz31 = get_standard_observer("cmfs", "cie1931 xyz_1nm")
    wl = xyz31["wavelength"]
    print(f"\nCIE 1931: {len(wl)} points, {wl[0]:.0f}-{wl[-1]:.0f} nm")
    print(f"  Peak X at {wl[np.argmax(xyz31['X'])]:.0f} nm")
    print(f"  Peak Y at {wl[np.argmax(xyz31['Y'])]:.0f} nm")
    print(f"  Peak Z at {wl[np.argmax(xyz31['Z'])]:.0f} nm")

    lms = get_standard_observer("lms", "cie2006_lms2_linE_1nm")
    wl_lms = lms["wavelength"]
    print(f"\nCIE 2006 LMS: {len(wl_lms)} points, {wl_lms[0]:.0f}-{wl_lms[-1]:.0f} nm")
    print(f"  Peak L at {wl_lms[np.argmax(lms['l'])]:.0f} nm")
    print(f"  Peak M at {wl_lms[np.argmax(lms['m'])]:.0f} nm")
    print(f"  Peak S at {wl_lms[np.argmax(lms['s'])]:.0f} nm")

    photopic = get_standard_observer("vl", "cie2008_v2_linE_1nm")
    scotopic = get_standard_observer("luminous_efficiency", "scotopic_v_1nm")
    print(f"\nCIE 2008 V(lambda): peak at {photopic['wavelength'][np.argmax(photopic['V'])]:.0f} nm")
    print(f"Scotopic V'(lambda): peak at {scotopic['wavelength'][np.argmax(scotopic['V_prime'])]:.0f} nm")

    macular = get_standard_observer("filter", "macular_ss_5nm")
    lens = get_standard_observer("filter", "lens_ss_5nm")
    print(f"\nMacular pigment: peak at {macular['wavelength'][np.argmax(macular['optical_density'])]:.0f} nm")
    print(f"Lens density: {len(lens['wavelength'])} points")

    chroma = get_standard_observer("chro", "cie1931_chro_1nm")
    mb = get_standard_observer("xy", "mb2_chro2_5nm")
    cones = get_standard_observer("pigment", "succones")
    print(f"\nCIE 1931 chromaticity: {len(chroma['wavelength'])} points")
    print(f"MacLeod-Boynton: {len(mb['wavelength'])} points")
    print(f"Suction electrode cones: {len(cones['wavelength'])} points")

    with plot_style("journal_double"):
        fig, axes = plt.subplots(2, 3, figsize=(16, 10))

        plot_lines(
            [(wl, xyz31["X"]), (wl, xyz31["Y"]), (wl, xyz31["Z"])],
            ax=axes[0, 0],
            labels=["X", "Y", "Z"],
            colors=["red", "green", "blue"],
            title="CIE 1931 XYZ CMFs",
            xlabel="Wavelength (nm)",
            ylabel="Response",
        )

        plot_lines(
            [
                (wl_lms, np.nan_to_num(lms["l"], nan=0.0)),
                (wl_lms, np.nan_to_num(lms["m"], nan=0.0)),
                (wl_lms, np.nan_to_num(lms["s"], nan=0.0)),
            ],
            ax=axes[0, 1],
            labels=["L", "M", "S"],
            colors=["red", "green", "blue"],
            title="CIE 2006 2 Degree LMS Fundamentals",
            xlabel="Wavelength (nm)",
            ylabel="Sensitivity",
        )

        plot_lines(
            [
                (photopic["wavelength"], photopic["V"] / photopic["V"].max()),
                (scotopic["wavelength"], scotopic["V_prime"] / scotopic["V_prime"].max()),
            ],
            ax=axes[0, 2],
            labels=["V(lambda) photopic", "V'(lambda) scotopic"],
            colors=["orange", "purple"],
            title="Luminous Efficiency Functions",
            xlabel="Wavelength (nm)",
            ylabel="Normalised sensitivity",
        )

        plot_lines(
            [
                (macular["wavelength"], macular["optical_density"]),
                (lens["wavelength"], lens["optical_density"]),
            ],
            ax=axes[1, 0],
            labels=["Macular pigment", "Lens"],
            colors=["olive", "brown"],
            title="Prereceptoral Filters",
            xlabel="Wavelength (nm)",
            ylabel="Optical density",
        )

        plot_cie1931_diagram(
            ax=axes[1, 1],
            title="CIE 1931 Chromaticity Outline",
            whitepoint_xy=None,
            show_sample_points=False,
        )

        plot_lines(
            [
                (cones["wavelength"], np.nan_to_num(cones["l"], nan=0.0)),
                (cones["wavelength"], np.nan_to_num(cones["m"], nan=0.0)),
                (cones["wavelength"], np.nan_to_num(cones["s"], nan=0.0)),
            ],
            ax=axes[1, 2],
            labels=["L cone", "M cone", "S cone"],
            colors=["red", "green", "blue"],
            title="Suction Electrode Cone Pigments",
            xlabel="Wavelength (nm)",
            ylabel="Log absorption",
        )
        axes[1, 2].legend(fontsize=8)

        save_figure(fig, "03_standard_observers.png")


if __name__ == "__main__":
    main()
