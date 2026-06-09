"""Read, write and plot spectral CSV data with color.io."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from color.colorimetry import XYZ_to_xy, emission_to_XYZ
from color.io import (
    read_spectral_csv,
    read_spectral_excel,
    read_spectral_json,
    save_figure,
    write_spectral_csv,
    write_spectral_excel,
    write_spectral_json,
)
from color.plot import (
    plot_chromaticity_points,
    plot_cie1931_diagram,
    plot_lines,
    plot_style,
)
from color.spectra import MultiSpectralDistribution, SpectralDistribution


INPUT_DIR = Path(__file__).resolve().parent / "input_csv"
OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def _max_error(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.max(np.abs(np.asarray(a, dtype=float) - np.asarray(b, dtype=float))))


def _print_object_summary(label: str, obj) -> None:
    labels = getattr(obj, "labels", None)
    print(
        f"{label}: {type(obj).__name__}, "
        f"domain={obj.wavelengths[0]:.1f}-{obj.wavelengths[-1]:.1f} nm, "
        f"shape={obj.values.shape}, labels={labels}"
    )


def _read_input_examples():
    """Read four real CSV variants using explicit pandas read options."""
    single_standard = read_spectral_csv(
        INPUT_DIR / "single_spd_standard_header_trailing_blank.csv",
        x="Wavelength(nm)",
        y="Spectrum",
        usecols=[0, 1],
        skipfooter=1,
        engine="python",
        name="standard header SPD",
        metadata={"source_file": "single_spd_standard_header_trailing_blank.csv"},
    )
    single_vendor_header = read_spectral_csv(
        INPUT_DIR / "single_spd_vendor_header.csv",
        encoding="gbk",
        skiprows=1,
        usecols=[0, 1],
        x="Wavelength(nm)",
        y="Spectrum",
        name="vendor header SPD",
        metadata={"source_file": "single_spd_vendor_header.csv"},
    )
    multi_vendor_header = read_spectral_csv(
        INPUT_DIR / "multi_spd_vendor_header.csv",
        encoding="gbk",
        skiprows=1,
        usecols=[0, 1, 2],
        x="Wavelength(nm)",
        ys=("Spectrum", "Spectrum.1"),
        name="vendor header two-channel SPD",
        metadata={"source_file": "multi_spd_vendor_header.csv"},
    )
    chinese_header = read_spectral_csv(
        INPUT_DIR / "single_spd_chinese_header_gbk.csv",
        encoding="gbk",
        usecols=[0, 1],
        x="\u6ce2\u957f",
        y="Count",
        name="GBK Chinese header SPD",
        metadata={"source_file": "single_spd_chinese_header_gbk.csv"},
    )
    return single_standard, single_vendor_header, multi_vendor_header, chinese_header


def _write_and_read_single(single: SpectralDistribution) -> None:
    csv_path = write_spectral_csv(OUTPUT_DIR / "02_roundtrip_single_spectral.csv", single)
    xlsx_path = write_spectral_excel(OUTPUT_DIR / "02_roundtrip_single_spectral.xlsx", single)
    json_path = write_spectral_json(OUTPUT_DIR / "02_roundtrip_single_spectral.json", single)

    from_csv = read_spectral_csv(csv_path)
    from_xlsx = read_spectral_excel(xlsx_path)
    from_json = read_spectral_json(json_path)

    print("Single-channel round-trip")
    print(f"  CSV max error:   {_max_error(single.values, from_csv.values):.3e}")
    print(f"  Excel max error: {_max_error(single.values, from_xlsx.values):.3e}")
    print(f"  JSON max error:  {_max_error(single.values, from_json.values):.3e}")
    print(f"  JSON metadata preserved: {from_json.metadata == single.metadata}")
    print("  Note: CSV/Excel are table formats; JSON is object-level serialization.")


def _write_and_read_multi(multi: MultiSpectralDistribution) -> None:
    csv_path = write_spectral_csv(OUTPUT_DIR / "02_roundtrip_multi_spectral.csv", multi)
    xlsx_path = write_spectral_excel(OUTPUT_DIR / "02_roundtrip_multi_spectral.xlsx", multi)
    json_path = write_spectral_json(OUTPUT_DIR / "02_roundtrip_multi_spectral.json", multi)

    from_csv = read_spectral_csv(csv_path, ys=multi.labels)
    from_xlsx = read_spectral_excel(xlsx_path, ys=multi.labels)
    from_json = read_spectral_json(json_path)

    print("Multi-channel round-trip")
    print(f"  CSV max error:   {_max_error(multi.values, from_csv.values):.3e}")
    print(f"  Excel max error: {_max_error(multi.values, from_xlsx.values):.3e}")
    print(f"  JSON max error:  {_max_error(multi.values, from_json.values):.3e}")
    print(f"  CSV labels:      {from_csv.labels}")
    print(f"  JSON labels:     {from_json.labels}")
    print(f"  JSON metadata preserved: {from_json.metadata == multi.metadata}")


def _spectral_series(obj) -> list[tuple[str, np.ndarray, np.ndarray]]:
    if isinstance(obj, SpectralDistribution):
        return [(obj.name, obj.wavelengths, obj.values)]
    return [
        (f"{obj.name}: {label}", obj.wavelengths, obj.values[:, index])
        for index, label in enumerate(obj.labels)
    ]


def _as_single_channel_spectra(objects) -> list[SpectralDistribution]:
    spectra: list[SpectralDistribution] = []
    for obj in objects:
        if isinstance(obj, SpectralDistribution):
            spectra.append(obj)
        else:
            spectra.extend(obj.channel(label) for label in obj.labels)
    return spectra


def _plot_input_spectra(objects) -> None:
    with plot_style("presentation", font_scale=0.62, line_scale=0.85):
        fig, axes = plt.subplots(2, 2, figsize=(11.0, 6.4))
        for ax, obj in zip(axes.ravel(), objects):
            series_data = _spectral_series(obj)
            plot_lines(
                [(wavelengths, values) for _label, wavelengths, values in series_data],
                ax=ax,
                labels=[label for label, _wavelengths, _values in series_data],
                xlabel="Wavelength / nm",
                ylabel="Signal",
                linewidth=1.1,
                legend=True if len(series_data) > 1 else False,
            )
            ax.set_title(obj.metadata.get("source_file", obj.name), loc="left", fontsize=8.8)
        fig.tight_layout()

    output_path = save_figure(
        OUTPUT_DIR / "02_input_spectra_panels.png",
        fig=fig,
        dpi=170,
        close=True,
    )
    print(f"Spectral panel plot saved to: {output_path}")


def _compute_cie1931_xy(spectra: list[SpectralDistribution]) -> tuple[np.ndarray, list[str]]:
    xy_values: list[np.ndarray] = []
    labels: list[str] = []
    for spectrum in spectra:
        XYZ = emission_to_XYZ(spectrum)
        xy_values.append(XYZ_to_xy(XYZ))
        source = spectrum.metadata.get("source_file", spectrum.name)
        channel = spectrum.metadata.get("channel")
        labels.append(f"{source}:{channel}" if channel else str(source))
    return np.vstack(xy_values), labels


def _plot_cie1931_xy(objects) -> None:
    spectra = _as_single_channel_spectra(objects)
    xy, labels = _compute_cie1931_xy(spectra)

    with plot_style("presentation", font_scale=0.66, line_scale=0.9):
        fig, ax = plot_cie1931_diagram(
            title="CIE 1931 xy from input SPDs",
            show_background=True,
            background_samples=96,
            show_sample_points=False,
        )
        plot_chromaticity_points(
            xy,
            ax=ax,
            color="tab:red",
            sizes=44,
        )
        fig.tight_layout()

    output_path = save_figure(
        OUTPUT_DIR / "02_input_spectra_cie1931_xy.png",
        fig=fig,
        dpi=170,
        close=True,
    )
    print("CIE 1931 xy coordinates")
    for index, (label, point) in enumerate(zip(labels, xy), start=1):
        print(f"  S{index}: {label:48s} xy = ({point[0]:.5f}, {point[1]:.5f})")
    print(f"Chromaticity plot saved to: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    single_standard, single_vendor_header, multi_vendor_header, chinese_header = _read_input_examples()
    input_objects = (single_standard, single_vendor_header, multi_vendor_header, chinese_header)

    print("Spectral data IO example")
    _print_object_summary("single_spd_standard_header_trailing_blank.csv", single_standard)
    _print_object_summary("single_spd_vendor_header.csv", single_vendor_header)
    _print_object_summary("multi_spd_vendor_header.csv", multi_vendor_header)
    _print_object_summary("single_spd_chinese_header_gbk.csv", chinese_header)
    print()

    _plot_input_spectra(input_objects)
    _plot_cie1931_xy(input_objects)
    print()

    _write_and_read_single(single_standard)
    print()
    _write_and_read_multi(multi_vendor_header)
    print(f"\nOutputs written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
