"""Adding custom datasets without keeping test files in color/data/.

This example creates temporary files at runtime and registers them through the
dataset registry.  It demonstrates common "add a new file" scenarios without
polluting the repository's reference data tree.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.datasets import list_categories, list_datasets, search
from color.datasets._registry import DatasetEntry, get, register
from color.generators._registry import GeneratorEntry, generate, register as register_generator


def write_no_header_csv(path: Path) -> None:
    """Create a simple no-header RGB LED CSV."""
    with path.open("w", encoding="utf-8") as f:
        for wl in range(380, 781, 20):
            red = max(0.0, 1.0 - abs(wl - 630) / 90)
            green = max(0.0, 1.0 - abs(wl - 530) / 80)
            blue = max(0.0, 1.0 - abs(wl - 460) / 70)
            f.write(f"{wl},{red:.4f},{green:.4f},{blue:.4f}\n")


def demo_csv_no_header(tmp: Path) -> None:
    """New CSV file with no header: use explicit DatasetEntry.columns."""
    print("=" * 60)
    print("1. CSV without header -> explicit columns")
    print("=" * 60)

    csv_path = tmp / "rgb_led_no_header.csv"
    write_no_header_csv(csv_path)

    register(DatasetEntry(
        category="example_leds",
        name="rgb_no_header",
        description="Temporary RGB LED CSV without header",
        file_path=str(csv_path),
        columns=("wavelength", "red", "green", "blue"),
    ))

    data = get("example_leds", "rgb_no_header")
    print("  keys:", list(data.keys()))
    print("  red peak:", data["wavelength"][np.argmax(data["red"])])


def demo_csv_with_header(tmp: Path) -> None:
    """New CSV file with header: let header='auto' detect column names."""
    print("\n" + "=" * 60)
    print("2. CSV with header -> auto-detected names")
    print("=" * 60)

    csv_path = tmp / "measured_spd.csv"
    csv_path.write_text(
        "wavelength,spd,uncertainty\n"
        "450,0.2,0.01\n"
        "550,1.0,0.02\n"
        "650,0.3,0.01\n",
        encoding="utf-8",
    )

    register(DatasetEntry(
        category="example_spds",
        name="measured_with_header",
        description="Temporary measured SPD with file header",
        file_path=str(csv_path),
        read_options={"header": "auto"},
    ))

    data = get("example_spds", "measured_with_header")
    print("  keys:", list(data.keys()))
    print("  max spd:", data["spd"].max())


def demo_csv_header_override(tmp: Path) -> None:
    """New CSV file with unsuitable header: override with columns."""
    print("\n" + "=" * 60)
    print("3. CSV with header -> override names")
    print("=" * 60)

    csv_path = tmp / "vendor_spd.csv"
    csv_path.write_text(
        "lambda,power\n"
        "500,0.8\n"
        "510,0.9\n"
        "520,0.7\n",
        encoding="utf-8",
    )

    register(DatasetEntry(
        category="example_spds",
        name="vendor_renamed",
        description="Temporary vendor SPD with normalized column names",
        file_path=str(csv_path),
        columns=("wavelength", "spd"),
        read_options={"header": "auto"},
    ))

    data = get("example_spds", "vendor_renamed")
    print("  keys:", list(data.keys()))
    print("  first wavelength:", data["wavelength"][0])


def demo_xlsx_named_sheet(tmp: Path) -> None:
    """New Excel workbook: read a named sheet."""
    print("\n" + "=" * 60)
    print("4. XLSX workbook -> named sheet")
    print("=" * 60)

    xlsx_path = tmp / "lamp_measurements.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        pd.DataFrame({"operator": ["lab"], "date": ["2026-05-15"]}).to_excel(
            writer, sheet_name="metadata", index=False
        )
        pd.DataFrame({
            "wavelength": [460, 560, 660],
            "spd": [0.2, 1.0, 0.4],
        }).to_excel(writer, sheet_name="spd", index=False)

    register(DatasetEntry(
        category="example_spds",
        name="xlsx_named_sheet",
        description="Temporary XLSX SPD loaded from a named sheet",
        file_path=str(xlsx_path),
        read_options={"sheet": "spd", "header": True},
    ))

    data = get("example_spds", "xlsx_named_sheet")
    print("  keys:", list(data.keys()))
    print("  rows:", len(data["wavelength"]))


def demo_custom_parser(tmp: Path) -> None:
    """Special static file: register a parser function."""
    print("\n" + "=" * 60)
    print("5. Special static file -> parser_fn")
    print("=" * 60)

    custom_path = tmp / "semicolon_spd.txt"
    custom_path.write_text(
        "wl;value\n"
        "500;0.8\n"
        "510;0.9\n"
        "520;0.7\n",
        encoding="utf-8",
    )

    def read_semicolon(path: str, **kwargs):
        rows = Path(path).read_text(encoding="utf-8").strip().splitlines()[1:]
        wavelength = []
        spd = []
        for row in rows:
            wl, value = row.split(";")
            wavelength.append(float(wl))
            spd.append(float(value))
        return {"wavelength": np.array(wavelength), "spd": np.array(spd)}

    register(DatasetEntry(
        category="example_spds",
        name="semicolon_parser",
        description="Temporary semicolon SPD parsed by parser_fn",
        file_path=str(custom_path),
        parser_fn=read_semicolon,
    ))

    data = get("example_spds", "semicolon_parser")
    print("  keys:", list(data.keys()))
    print("  peak:", data["wavelength"][np.argmax(data["spd"])])


def demo_generated_data() -> None:
    """Generated data: register a formula in color.generators."""
    print("\n" + "=" * 60)
    print("6. Generated data -> color.generators")
    print("=" * 60)

    def gaussian_spd(wavelength_nm=None, center=550.0, width=30.0):
        if wavelength_nm is None:
            wavelength_nm = np.arange(380, 781, 1.0)
        spd = np.exp(-0.5 * ((wavelength_nm - center) / width) ** 2)
        return {"wavelength": wavelength_nm, "spd": spd}

    register_generator(GeneratorEntry(
        category="example_spds",
        name="gaussian",
        description="Generated Gaussian SPD",
        generate_fn=gaussian_spd,
        parameters=("wavelength_nm", "center", "width"),
    ))

    data = generate("example_spds", "gaussian", center=610, width=25)
    print("  peak:", data["wavelength"][np.argmax(data["spd"])])


def demo_discovery() -> None:
    """Show that custom datasets participate in list/search APIs."""
    print("\n" + "=" * 60)
    print("Discovery")
    print("=" * 60)

    print("  example_leds:", list_datasets("example_leds"))
    print("  example_spds:", list_datasets("example_spds"))
    print("  categories contain example_spds:", "example_spds" in list_categories())
    print("  search('temporary'):", [entry.name for entry in search("temporary")])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="color_dataset_example_") as tmp_dir:
        tmp = Path(tmp_dir)
        demo_csv_no_header(tmp)
        demo_csv_with_header(tmp)
        demo_csv_header_override(tmp)
        demo_xlsx_named_sheet(tmp)
        demo_custom_parser(tmp)
        demo_generated_data()
        demo_discovery()

    print("\nTemporary files were removed. Registered data remains cached for this process.")


if __name__ == "__main__":
    main()
