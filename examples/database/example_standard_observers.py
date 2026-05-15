"""Standard observer datasets: CMFs, cones, luminous efficiency, and more."""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np
import matplotlib.pyplot as plt

from color.datasets import (
    get_standard_observer,
    list_standard_observers,
    list_standard_observer_categories,
)


def main() -> None:
    # --- 1. List categories and aliases ---
    print("Categories:", list_standard_observer_categories())
    print("CMFs count:", len(list_standard_observers("cmfs")))
    print("Cone fundamentals count:", len(list_standard_observers("cone")))

#     print(describe("cmfs", "cie2012_xyz2_1nm")


    # --- 2. CIE 1931 2° XYZ CMFs ---
    xyz31 = get_standard_observer("cmfs", "cie1931_xyz_1nm")
    xyz_1008_v2 = get_standard_observer("cmfs", "cie2012_xyz2_1nm")
    wl = xyz31["wavelength"]
    wl2 = xyz_1008_v2["wavelength"]
    print(f"\nCIE 1931: {len(wl)} points, {wl[0]:.0f}–{wl[-1]:.0f} nm")
    print(f"  Peak x at {wl[np.argmax(xyz31['X'])]:.0f} nm")
    print(f"  Peak y at {wl[np.argmax(xyz31['Y'])]:.0f} nm")
    print(f"  Peak z at {wl[np.argmax(xyz31['Z'])]:.0f} nm")

    # --- 3. CIE 2006 LMS cone fundamentals (use alias "lms") ---
    lms = get_standard_observer("lms", "cie2006_lms2_linE_1nm")
    wl_lms = lms["wavelength"]
    print(f"\nCIE 2006 LMS: {len(wl_lms)} points, "
          f"{wl_lms[0]:.0f}–{wl_lms[-1]:.0f} nm")
    print(f"  Peak L at {wl_lms[np.argmax(lms['l'])]:.0f} nm")
    print(f"  Peak M at {wl_lms[np.argmax(lms['m'])]:.0f} nm")
    print(f"  Peak S at {wl_lms[np.argmax(lms['s'])]:.0f} nm")

    # --- 4. CIE 2008 V(λ) luminous efficiency ---
    v2 = get_standard_observer("vl", "cie2008_v2_linE_1nm")
    print(f"\nCIE 2008 V(λ): peak at {v2['wavelength'][np.argmax(v2['V'])]:.0f} nm")

    scotopic = get_standard_observer("luminous_efficiency", "scotopic_v_1nm")
    print(f"Scotopic V'(λ): peak at "
          f"{scotopic['wavelength'][np.argmax(scotopic['V_prime'])]:.0f} nm")

    # --- 5. Prereceptoral filters ---
    macular = get_standard_observer("filter", "macular_ss_5nm")
    lens = get_standard_observer("filter", "lens_ss_5nm")
    print(f"\nMacular pigment: peak at "
          f"{macular['wavelength'][np.argmax(macular['optical_density'])]:.0f} nm")
    print(f"Lens density: {len(lens['wavelength'])} points")

    # --- 6. Chromaticity coordinates ---
    chroma = get_standard_observer("chro", "cie1931_chro_1nm")
    print(f"\nCIE 1931 chromaticity: {len(chroma['wavelength'])} points")

    mb = get_standard_observer("xy", "mb2_chro2_5nm")
    print(f"MacLeod-Boynton: {len(mb['wavelength'])} points")

    # --- 7. Photopigments ---
    cones = get_standard_observer("pigment", "succones")
    print(f"Suction electrode cones (succones): {len(cones['wavelength'])} points")

    # --- 8. Test extra unregistered data ---
    # This is a placeholder for testing  data
    test_data = get_standard_observer("test_data", "just_for_test_with_header")
    print('test data:', test_data.keys())


    # --- 8. Plot ---
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))

    # (a) CIE 1931 XYZ CMFs
    ax = axes[0, 0]
    ax.plot(wl, xyz31["X"], label=r"$X$", color="red")
    ax.plot(wl, xyz31["Y"], label=r"$Y$", color="green")
    ax.plot(wl, xyz31["Z"], label=r"$Z$", color="blue")
    ax.set_title("CIE 2006 2° XYZ CMFs")
    ax.set_xlabel("Wavelength (nm)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (b) CIE 2006 LMS
    ax = axes[0, 1]
    ax.plot(wl_lms, lms["l"], label="L", color="red")
    ax.plot(wl_lms, lms["m"], label="M", color="green")
    ax.plot(wl_lms, lms["s"], label="S", color="blue")
    ax.set_title("CIE 2006 2° LMS Cone Fundamentals")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("log sensitivity")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (c) Luminous efficiency
    ax = axes[0, 2]
    ax.plot(v2["wavelength"], v2["V"] / v2["V"].max(), label="V(λ) photopic", color="orange")
    ax.plot(scotopic["wavelength"], scotopic["V_prime"] / scotopic["V_prime"].max(),
            label="V'(λ) scotopic", color="purple")
    ax.set_title("Luminous Efficiency Functions")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Normalized sensitivity")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (d) Prereceptoral filters
    ax = axes[1, 0]
    ax.plot(macular["wavelength"], macular["optical_density"],
            label="Macular pigment", color="olive")
    ax.plot(lens["wavelength"], lens["optical_density"],
            label="Lens", color="brown")
    ax.set_title("Prereceptoral Filters")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Optical density")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (e) CIE 1931 chromaticity diagram outline
    ax = axes[1, 1]
    ax.plot(chroma["x"], chroma["y"], color="black", linewidth=1.5)
    # Close the locus
    ax.plot([chroma["x"][0], chroma["x"][-1]],
            [chroma["y"][0], chroma["y"][-1]],
            color="black", linewidth=1.5, linestyle="--")
    ax.set_title("CIE 1931 Chromaticity Outline")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)

    # (f) Photopigments
    ax = axes[1, 2]
    ax.plot(cones["wavelength"], cones["l"], label="L cone", color="red")
    ax.plot(cones["wavelength"], cones["m"], label="M cone", color="green")
    ax.plot(cones["wavelength"], cones["s"], label="S cone", color="blue")
    ax.set_title("Suction Electrode Cone Pigments (succones)")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Log absorption")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    out = Path(__file__).resolve().parent / "standard_observers.png"
    plt.savefig(out, dpi=150)
    plt.show()
    print(f"\nPlot saved to {out}")


if __name__ == "__main__":
    main()
