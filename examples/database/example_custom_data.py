"""Adding custom datasets: three methods demonstrated.

Method 1 — Zero-config: drop CSV into standard_observer_data/<folder>/, done.
Method 2 — _CUSTOM_ENTRIES: add column names, descriptions, aliases.
Method 3 — Manual register(): full control, any category, any format.
"""

import sys
import tempfile
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.datasets._registry import DatasetEntry, register, register_computed, get
from color.datasets import list_categories, list_datasets, search


# ---------------------------------------------------------------------------
# Method 3: Manual register()
# ---------------------------------------------------------------------------

def method3_file_register() -> None:
    """Register a CSV file into a custom category."""
    print("=" * 60)
    print("Method 3a: Register a file-based dataset")
    print("=" * 60)

    # 1. Create a temporary CSV (simulating your own data file)
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, prefix="my_led_"
    ) as f:
        # 3-column CSV: wavelength, red, green, blue
        for wl in range(380, 781, 5):
            r = max(0, 1.0 - abs(wl - 630) / 80)
            g = max(0, 1.0 - abs(wl - 530) / 80)
            b = max(0, 1.0 - abs(wl - 460) / 80)
            f.write(f"{wl}, {r:.4f}, {g:.4f}, {b:.4f}\n")
        tmp_path = f.name

    # 2. Register it
    register(DatasetEntry(
        category="my_leds",
        name="rgb_led_model",
        description="Idealized RGB LED emission model",
        file_path=tmp_path,
        metadata={"names": ("wavelength", "red", "green", "blue")},
    ))

    # 3. Load and inspect
    data = get("my_leds", "rgb_led_model")
    print(f"  Keys: {list(data.keys())}")
    print(f"  Points: {len(data['wavelength'])}, "
          f"{data['wavelength'][0]:.0f}–{data['wavelength'][-1]:.0f} nm")
    print(f"  Red peak at {data['wavelength'][np.argmax(data['red'])]:.0f} nm")
    print(f"  Green peak at {data['wavelength'][np.argmax(data['green'])]:.0f} nm")
    print(f"  Blue peak at {data['wavelength'][np.argmax(data['blue'])]:.0f} nm")

    # Cleanup
    Path(tmp_path).unlink()


def method3_computed_register() -> None:
    """Register a computed (formula-based) dataset."""
    print("\n" + "=" * 60)
    print("Method 3b: Register a computed dataset")
    print("=" * 60)

    def gaussian_spd(wavelength_nm=None, center=550.0, width=30.0):
        """Narrow-band Gaussian spectral power distribution."""
        if wavelength_nm is None:
            wavelength_nm = np.arange(380, 781, 1.0)
        spd = np.exp(-0.5 * ((wavelength_nm - center) / width) ** 2)
        return {"wavelength": wavelength_nm, "spd": spd}

    register_computed(
        category="my_spds",
        name="gaussian",
        compute_fn=gaussian_spd,
        description="Narrow-band Gaussian SPD",
    )

    # Load with different parameters
    for center, label in [(450, "Blue"), (550, "Green"), (650, "Red")]:
        data = get("my_spds", "gaussian", center=center, width=20)
        peak = data["wavelength"][np.argmax(data["spd"])]
        print(f"  {label}: requested center={center} nm, peak at {peak:.0f} nm")


def method3_real_file() -> None:
    """Register and load data/test_data/just_for_test.csv."""
    print("\n" + "=" * 60)
    print("Method 3c: Register data/test_data/just_for_test_ext.csv")
    print("=" * 60)

    from color.datasets._utils import data_dir

    csv_path = str(data_dir("test_data", "just_for_test_ext.csv"))
    register(DatasetEntry(
        category="test_data",
        name="just_for_test_ext",
        description="Test CSV from data/test_data/",
        file_path=csv_path,
        metadata={"names": ("wavelength", "l", "m", "s")},
    ))

    data = get("test_data", "just_for_test_ext")
    print(f"  Keys: {list(data.keys())}")
    print(f"  Points: {len(data['wavelength'])}, "
          f"{data['wavelength'][0]:.0f}–{data['wavelength'][-1]:.0f} nm")
    print(f"  l peak at {data['wavelength'][np.argmax(data['l'])]:.0f} nm")
    print(f"  m peak at {data['wavelength'][np.argmax(data['m'])]:.0f} nm")
    print(f"  s peak at {data['wavelength'][np.argmax(data['s'])]:.0f} nm")


def method3_discover() -> None:
    """Show that custom categories appear in list/search APIs."""
    print("\n" + "=" * 60)
    print("Discoverability: list_categories, search")
    print("=" * 60)

    cats = list_categories()
    print(f"  All categories ({len(cats)}): {cats}")

    results = search("LED")
    print(f"  search('LED'): {[r.name for r in results]}")

    results = search("gaussian")
    print(f"  search('gaussian'): {[r.name for r in results]}")

    results = search("test")
    print(f"  search('test'): {[r.name for r in results]}")


# ---------------------------------------------------------------------------
# Method 1 & 2: summary (no code action needed, just documentation)
# ---------------------------------------------------------------------------

def method1_and_2_summary() -> None:
    print("=" * 60)
    print("Method 1 (zero-config) & Method 2 (_CUSTOM_ENTRIES)")
    print("=" * 60)
    print("""
  Method 1 — Zero-config:
    Drop a CSV into standard_observer_data/<folder>/ (new or existing).
    On next import, it auto-scans and registers.
    Column names fall back to (wavelength, col1, col2, ...).

  Method 2 — _CUSTOM_ENTRIES:
    In standard_observers.py, add a dict to _CUSTOM_ENTRIES:

      _CUSTOM_ENTRIES = [
          {
              "category": "mesopic",
              "stem": "v_meso_5nm",
              "columns": ("wavelength", "V_meso"),
              "description": "CIE 201x Mesopic V(λ) (5 nm)",
              "aliases": ["meso"],
          },
      ]

    Then drop v_meso_5nm.csv into standard_observer_data/mesopic/.
    Access: get_standard_observer("meso", "v_meso_5nm")
    """)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    method1_and_2_summary()
    method3_file_register()
    method3_computed_register()
    method3_real_file()
    method3_discover()
    print("\nDone.")


if __name__ == "__main__":
    main()
