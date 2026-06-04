#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert selected University of Eastern Finland / University of Kuopio spectral
reflectance datasets to CSV files.

This script is designed for the folder produced by:
    download_uef_spectral_reconstruction.py --out ./uef_spectral_data

Default outputs:
    <out>/summary.csv
    <out>/per_dataset_wide/*.csv
    <out>/all_spectra_wide_raw.csv
    <out>/all_spectra_wide_400_700_10.csv
    <out>/all_spectra_long_400_700_10.csv

No third-party Python packages are required.

Version 1.6 changes:
- Fixed Agfa IT8.7/2 ASCII parsing. The DAT file stores colour coordinates in the same file, so generic numeric parsing can mix Lab/XYZ metadata into spectral bands.
- Agfa is now parsed with a dedicated reader and validated; MATLAB .mat is preferred when present.
- Agfa outputs are rejected if they contain impossible spectral values such as large negatives, 313, 1925, or scientific-notation metadata.
"""
from __future__ import annotations

import argparse
import bisect
import csv
import gzip
import math
import os
import re
import shutil
import sys
import tarfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

VERSION = "1.6"

NUMBER_RE = re.compile(r"[-+]?(?:\d*\.\d+|\d+)(?:[eEdD][-+]?\d+)?")
# Lines that contain only numeric tokens and separators. Useful for old ASCII
# files where labels and spectra alternate.
NUMERIC_LINE_RE = re.compile(r"^[\s,;:+\-\.0-9eEdD]+$")


def nm_grid(start: int, end: int, step: int) -> List[int]:
    return list(range(int(start), int(end) + 1, int(step)))


def format_float(value: Optional[float]) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    return f"{value:.10g}"


def extract_numbers(line: str) -> List[float]:
    values: List[float] = []
    for token in NUMBER_RE.findall(line):
        token = token.replace("D", "E").replace("d", "e")
        try:
            values.append(float(token))
        except ValueError:
            pass
    return values


def read_text_lines(path: Path) -> List[str]:
    """Read a text file, transparently handling gzip payloads.

    A few downloads can end up with a decompressed-looking filename such as
    ``*.asc`` while the bytes are still gzip-compressed. We check the gzip
    magic number rather than trusting the extension.
    """
    data = path.read_bytes()
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    text = data.decode("utf-8", errors="replace")
    return text.splitlines()


def read_numeric_rows(path: Path) -> List[List[float]]:
    rows: List[List[float]] = []
    for line in read_text_lines(path):
        nums = extract_numbers(line)
        if nums:
            rows.append(nums)
    return rows


def crop_or_drop_label(row: Sequence[float], expected_channels: int) -> Optional[List[float]]:
    """Return spectral values from a numeric row.

    Handles common cases:
    - exactly expected_channels values: already a spectrum.
    - expected_channels + 1 values: first value is often a sample index parsed from
      labels such as A1; drop it.
    - more than expected_channels + 1 values: often spectrum followed by colour
      coordinates; keep the first expected_channels values.
    """
    n = len(row)
    if n < expected_channels:
        return None
    if n == expected_channels:
        return [float(v) for v in row]
    if n == expected_channels + 1:
        first = row[0]
        if abs(first - round(first)) < 1e-9:
            return [float(v) for v in row[1:]]
        return [float(v) for v in row[:expected_channels]]
    return [float(v) for v in row[:expected_channels]]


@dataclass
class SpectrumTable:
    dataset: str
    subdataset: str
    wavelengths: List[int]
    spectra: List[List[float]]
    labels: List[str] = field(default_factory=list)
    source_file: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.labels:
            self.labels = [""] * len(self.spectra)
        if len(self.labels) != len(self.spectra):
            raise ValueError(f"labels length mismatch for {self.dataset}/{self.subdataset}")
        expected = len(self.wavelengths)
        bad = [i for i, row in enumerate(self.spectra) if len(row) != expected]
        if bad:
            first = bad[0]
            raise ValueError(
                f"wrong spectrum length in {self.dataset}/{self.subdataset}; "
                f"sample {first + 1} has {len(self.spectra[first])}, expected {expected}"
            )


def parse_flat_or_matrix(
    path: Path,
    wavelengths: Sequence[int],
    n_samples: Optional[int] = None,
    prefer_column_matrix: bool = False,
) -> List[List[float]]:
    """Parse numeric ASCII files stored as flat vectors, sample rows, or channel rows."""
    dim = len(wavelengths)
    rows = read_numeric_rows(path)
    if not rows:
        raise ValueError(f"no numeric data found in {path}")

    # Case 1: sample-by-row matrix.
    row_spectra = [crop_or_drop_label(row, dim) for row in rows]
    row_spectra_clean = [row for row in row_spectra if row is not None]
    if n_samples is not None:
        if len(row_spectra_clean) >= n_samples and not prefer_column_matrix:
            # If there are exactly n_samples plausible rows, this is usually the safest.
            if len(row_spectra_clean) == n_samples:
                return row_spectra_clean[:n_samples]
        # Case 2: channel-by-row matrix, e.g. 31 rows x 289 columns.
        if len(rows) >= dim and all(len(row) >= n_samples for row in rows[:dim]):
            return [
                [float(rows[wl_i][sample_i]) for wl_i in range(dim)]
                for sample_i in range(n_samples)
            ]
        if len(row_spectra_clean) >= n_samples and not prefer_column_matrix:
            return row_spectra_clean[:n_samples]

    # Case 3: unknown n_samples but rows already look like spectra.
    if n_samples is None and len(row_spectra_clean) == len(rows) and len(rows) > 1:
        # Avoid mistaking a 31 x N channel-row matrix for N spectra.
        if len(rows) != dim:
            return row_spectra_clean

    # Case 4: flat vector; order is sample 1 wavelengths, sample 2 wavelengths, ...
    flat: List[float] = [float(v) for row in rows for v in row]
    if n_samples is not None:
        needed = n_samples * dim
        if len(flat) < needed:
            raise ValueError(
                f"not enough numeric values in {path}: got {len(flat)}, need {needed}"
            )
        return [flat[i * dim : (i + 1) * dim] for i in range(n_samples)]

    if len(flat) % dim != 0:
        raise ValueError(
            f"cannot infer sample count for {path}: {len(flat)} numeric values "
            f"is not divisible by {dim} wavelengths"
        )
    inferred_n = len(flat) // dim
    return [flat[i * dim : (i + 1) * dim] for i in range(inferred_n)]


def is_numeric_data_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if not any(ch.isdigit() for ch in stripped):
        return False
    return NUMERIC_LINE_RE.match(stripped) is not None


def looks_like_wavelength_header(nums: Sequence[float], wavelengths: Sequence[int]) -> bool:
    """Return True for rows like 400 405 ... 700 rather than reflectance data."""
    if len(nums) < len(wavelengths):
        return False
    return all(
        abs(float(v) - float(wl)) <= 1e-9
        for v, wl in zip(nums[: len(wavelengths)], wavelengths)
    )


def parse_natural_colors(path: Path) -> Tuple[List[List[float]], List[str]]:
    """Parse Natural colors ASCII data robustly.

    The UEF README describes the Natural colors file as alternating lines:
    label line, then a 61-value spectrum line for 400-700 nm at 5 nm intervals.
    The public ASCII file can contain 219 parseable label/spectrum pairs even
    though the README states 218. This function returns all parseable spectra;
    trimming, if desired, is handled later by --natural-policy readme218.
    """
    wavelengths = nm_grid(400, 700, 5)
    dim = len(wavelengths)
    lines = [line.strip().lstrip("\ufeff") for line in read_text_lines(path) if line.strip()]

    def is_integerish(v: float) -> bool:
        return abs(float(v) - round(float(v))) <= 1e-9

    def looks_like_sequence_header(row: Sequence[float]) -> bool:
        """Rows like 0 1 2 ... 60, 1 2 ... 61, or 400 405 ... 700."""
        if len(row) != dim:
            return False
        if looks_like_wavelength_header(row, wavelengths):
            return True
        diffs = [float(row[i + 1]) - float(row[i]) for i in range(dim - 1)]
        if not diffs:
            return False
        step = diffs[0]
        if max(abs(d - step) for d in diffs) > 1e-9:
            return False
        if all(is_integerish(v) for v in row) and abs(step - round(step)) <= 1e-9:
            if abs(row[0] - 0) <= 1e-9 and abs(step - 1) <= 1e-9:
                return True
            if abs(row[0] - 1) <= 1e-9 and abs(step - 1) <= 1e-9:
                return True
            if abs(row[0] - 400) <= 1e-9 and abs(step - 5) <= 1e-9:
                return True
        return False

    def plausible_aotf(row: Sequence[float]) -> bool:
        # README says values are 12-bit raw A/D output. Some rows can exceed
        # 4096 and should be clipped later if --aotf clip/normalize is used.
        return len(row) == dim and all(-1e-9 <= float(v) <= 100000.0 for v in row)

    def row_from_numbers(nums: Sequence[float]) -> Optional[List[float]]:
        if len(nums) < dim:
            return None

        # Case: 400 v400 405 v405 ... 700 v700
        if len(nums) >= 2 * dim:
            even = [nums[2 * i] for i in range(dim)]
            if looks_like_wavelength_header(even, wavelengths):
                return [float(nums[2 * i + 1]) for i in range(dim)]

        # Case: 400 405 ... 700 v400 v405 ... v700
        if len(nums) >= 2 * dim and looks_like_wavelength_header(nums[:dim], wavelengths):
            return [float(v) for v in nums[dim : dim * 2]]

        # Case: pure wavelength/header row.
        first_window = [float(v) for v in nums[:dim]]
        if looks_like_wavelength_header(first_window, wavelengths):
            return None

        # Case: leading sample index followed by 61 spectral values.
        if len(nums) == dim + 1 and is_integerish(nums[0]) and 0 <= nums[0] <= 10000:
            return [float(v) for v in nums[1:]]

        return first_window

    def clean_label(line: str) -> str:
        return line.strip().lstrip("#").strip()

    spectra: List[List[float]] = []
    labels: List[str] = []
    pending_label = ""

    # Primary parser: line-by-line. This matches the real file exactly:
    # 219 label lines and 219 61-number rows in current public copies.
    for line in lines:
        nums = extract_numbers(line)
        if len(nums) >= dim:
            row = row_from_numbers(nums)
            if row is not None and plausible_aotf(row) and not looks_like_sequence_header(row):
                spectra.append([float(v) for v in row])
                labels.append(pending_label)
                pending_label = ""
            else:
                # Numeric-looking header or other non-spectrum line.
                pending_label = clean_label(line)
        else:
            # A label can contain digits, but it has far fewer than 61 numeric tokens.
            pending_label = clean_label(line)

    # Fallback: line-wrapped spectra. Accumulate numeric-heavy lines until 61
    # values are available. Used only when primary parsing found nothing.
    if len(spectra) == 0:
        pending_label = ""
        current_values: List[float] = []

        def flush_complete() -> None:
            nonlocal current_values, pending_label
            while len(current_values) >= dim:
                row = [float(v) for v in current_values[:dim]]
                if plausible_aotf(row) and not looks_like_sequence_header(row):
                    spectra.append(row)
                    labels.append(pending_label)
                current_values = current_values[dim:]
                pending_label = ""

        for line in lines:
            nums = extract_numbers(line)
            numeric_heavy = is_numeric_data_line(line) or len(nums) >= 8
            if numeric_heavy and nums:
                candidate = row_from_numbers(nums)
                if candidate is not None and len(nums) >= dim:
                    if plausible_aotf(candidate) and not looks_like_sequence_header(candidate):
                        spectra.append([float(v) for v in candidate])
                        labels.append(pending_label)
                        pending_label = ""
                    current_values = []
                else:
                    current_values.extend(nums)
                    flush_complete()
            else:
                if current_values and len(current_values) < dim:
                    current_values = []
                pending_label = clean_label(line)
        flush_complete()

    # De-duplicate exact repeated rows only. Do not trim to 218 here; the caller
    # applies --natural-policy after inspecting the local file count.
    dedup_spectra: List[List[float]] = []
    dedup_labels: List[str] = []
    seen = set()
    for row, label in zip(spectra, labels):
        key = tuple(row)
        if key in seen:
            continue
        seen.add(key)
        dedup_spectra.append(row)
        dedup_labels.append(label)

    return dedup_spectra, dedup_labels


def validate_agfa_spectra(spectra: Sequence[Sequence[float]], source: str = "Agfa") -> None:
    """Reject obviously corrupted Agfa spectra.

    Agfa IT8.7/2 should be 289 spectra sampled from 400 to 700 nm at 10 nm,
    i.e. 31 bands per sample. Values are reflectance percentages in practice,
    so typical values are near 0-100. We allow a small margin above 100 for
    white/calibration data, but reject colour-coordinate/metadata artefacts.
    """
    if len(spectra) != 289:
        raise ValueError(f"{source}: expected 289 spectra, got {len(spectra)}")
    if any(len(row) != 31 for row in spectra):
        bad = next(i for i, row in enumerate(spectra) if len(row) != 31)
        raise ValueError(f"{source}: sample {bad + 1} has {len(spectra[bad])} bands, expected 31")
    vals = [float(v) for row in spectra for v in row]
    if not vals or any((not math.isfinite(v)) for v in vals):
        raise ValueError(f"{source}: non-finite values found")
    mn = min(vals)
    mx = max(vals)
    # Small negative noise could be tolerated, but anything below -1 is not a
    # physical reflectance and usually means Lab/color-coordinate rows were read.
    if mn < -1.0 or mx > 150.0:
        raise ValueError(
            f"{source}: implausible spectral range min={mn:g}, max={mx:g}; "
            "this usually means colour coordinates/metadata were parsed as spectra"
        )


def is_plausible_agfa_row(row: Sequence[float]) -> bool:
    if len(row) != 31:
        return False
    vals = [float(v) for v in row]
    if any((not math.isfinite(v)) for v in vals):
        return False
    if min(vals) < -0.5 or max(vals) > 150.0:
        return False
    # Remove obvious non-spectral rows. Real reflectance spectra are not required
    # to be perfectly smooth, but colour-coordinate rows often alternate between
    # constants such as 0/1/2/65 and Lab values, producing very large jumps.
    diffs = [abs(vals[i + 1] - vals[i]) for i in range(len(vals) - 1)]
    if not diffs:
        return False
    if max(diffs) > 80.0:
        return False
    if sum(d > 40.0 for d in diffs) > 4:
        return False
    # Rows consisting mostly of tiny integers / instrument parameters are not spectra.
    integerish = sum(abs(v - round(v)) < 1e-8 for v in vals)
    if integerish >= 25 and max(vals) <= 100:
        return False
    return True


def parse_agfa_dat(path: Path) -> List[List[float]]:
    """Parse agfait872.dat safely.

    The UEF README states that colour coordinates are stored in the same ASCII
    file as the spectra. Therefore a generic "first 31 numbers per numeric row"
    parser is unsafe. This reader only accepts 31-band rows that pass a strict
    reflectance sanity check.
    """
    rows = read_numeric_rows(path)
    if not rows:
        raise ValueError(f"no numeric data found in {path}")

    spectra: List[List[float]] = []
    seen = set()

    # Primary route: the reflectance rows are expected to appear as exactly 31
    # values. Some local copies may prefix a sample index; accept 32-value rows
    # by dropping the first value when the remaining 31 values look spectral.
    for row in rows:
        candidates: List[List[float]] = []
        if len(row) == 31:
            candidates.append([float(v) for v in row])
        elif len(row) == 32:
            candidates.append([float(v) for v in row[1:]])
        for cand in candidates:
            if is_plausible_agfa_row(cand):
                key = tuple(round(float(v), 8) for v in cand)
                if key not in seen:
                    seen.add(key)
                    spectra.append(cand)

    if len(spectra) >= 289:
        spectra = spectra[:289]
        validate_agfa_spectra(spectra, source=f"Agfa DAT {path}")
        return spectra

    # Secondary route: 31 channel rows x 289 samples.
    if len(rows) >= 31 and all(len(row) >= 289 for row in rows[:31]):
        transposed = [[float(rows[wl_i][sample_i]) for wl_i in range(31)] for sample_i in range(289)]
        try:
            validate_agfa_spectra(transposed, source=f"Agfa DAT channel matrix {path}")
            return transposed
        except ValueError:
            pass

    raise ValueError(
        f"could not safely extract 289 Agfa spectra from {path}; "
        f"found {len(spectra)} plausible 31-band spectral rows. "
        "Use the MATLAB file agfait872.mat.gz if available, or rerun the downloader with --include-matlab."
    )


def parse_agfa_mat(path: Path) -> List[List[float]]:
    """Parse agfait872.mat or agfait872.mat.gz using scipy if available."""
    try:
        import scipy.io  # type: ignore
        import numpy as np  # type: ignore
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError("scipy is required to read agfait872.mat; install with: pip install scipy") from exc

    data = path.read_bytes()
    if data.startswith(b"\x1f\x8b") or path.name.endswith(".gz"):
        data = gzip.decompress(data)
    import io
    mat = scipy.io.loadmat(io.BytesIO(data))

    candidates: List[Tuple[str, List[List[float]]]] = []
    for name, value in mat.items():
        if name.startswith("__"):
            continue
        arr = np.asarray(value)
        if not np.issubdtype(arr.dtype, np.number):
            continue
        arr = np.real(arr).astype(float)
        if arr.ndim != 2:
            continue
        spectra_arr = None
        if arr.shape == (31, 289):
            spectra_arr = arr.T
        elif arr.shape == (289, 31):
            spectra_arr = arr
        elif arr.shape[0] >= 31 and arr.shape[1] >= 289:
            spectra_arr = arr[:31, :289].T
        elif arr.shape[0] >= 289 and arr.shape[1] >= 31:
            spectra_arr = arr[:289, :31]
        if spectra_arr is None:
            continue
        spectra = spectra_arr.tolist()
        try:
            validate_agfa_spectra(spectra, source=f"Agfa MAT variable {name}")
        except ValueError:
            continue
        candidates.append((name, spectra))

    if not candidates:
        raise ValueError(f"no 31x289 or 289x31 plausible Agfa spectral matrix found in {path}")
    # Prefer exact shape variables by construction; first valid candidate is fine.
    return candidates[0][1]


def parse_agfa_dataset(files: Sequence[Path], dat_path: Path) -> Tuple[List[List[float]], str]:
    """Prefer MATLAB Agfa data when present, otherwise parse DAT safely."""
    mat_path = find_exact(files, "agfait872.mat", "agfa")
    if mat_path is None:
        mat_path = find_exact(files, "agfait872.mat.gz", "agfa")
    if mat_path is not None:
        try:
            spectra = parse_agfa_mat(mat_path)
            return spectra, str(mat_path)
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] could not parse Agfa MATLAB file {mat_path}: {exc}; trying DAT", file=sys.stderr)

    spectra = parse_agfa_dat(dat_path)
    return spectra, str(dat_path)

def agfa_labels(n: int) -> List[str]:
    labels: List[str] = []
    for row_letter in "ABCDEFGHIJKL":
        for col in range(1, 23):
            labels.append(f"{row_letter}{col}")
    labels.extend([f"neutral_{i}" for i in range(1, 23)])
    labels.extend(["black", "white", "minolta_white_calibration"])
    if len(labels) < n:
        labels.extend([f"agfa_{i:04d}" for i in range(len(labels) + 1, n + 1)])
    return labels[:n]


def numbered_labels(prefix: str, n: int) -> List[str]:
    return [f"{prefix}_{i:04d}" for i in range(1, n + 1)]


def is_within_directory(directory: Path, target: Path) -> bool:
    directory = directory.resolve()
    target = target.resolve()
    try:
        target.relative_to(directory)
        return True
    except ValueError:
        return False


def unpack_archives(root: Path, out_dir: Path) -> Path:
    """Unpack any raw .gz/.tar.gz archives into a converter work directory."""
    unpack_root = out_dir / "_converter_unpacked"
    unpack_root.mkdir(parents=True, exist_ok=True)

    raw_dir = root / "raw"
    if not raw_dir.exists():
        return unpack_root

    for path in raw_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_parent = path.parent.relative_to(raw_dir)
        target_dir = unpack_root / rel_parent
        target_dir.mkdir(parents=True, exist_ok=True)
        name = path.name
        if name.endswith(".tar.gz"):
            with tarfile.open(path, "r:gz") as tar:
                for member in tar.getmembers():
                    target = target_dir / member.name
                    if not is_within_directory(target_dir, target):
                        raise RuntimeError(f"unsafe tar member path blocked: {member.name}")
                tar.extractall(target_dir)
        elif name.endswith(".gz"):
            target = target_dir / name[:-3]
            if target.exists() and target.stat().st_size > 0:
                continue
            with gzip.open(path, "rb") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
        elif path.suffix.lower() in {".asc", ".dat", ".txt", ".xls", ".xlsx"}:
            target = target_dir / name
            if not target.exists():
                shutil.copy2(path, target)
    return unpack_root


def candidate_files(root: Path, unpack_root: Path) -> List[Path]:
    roots = []
    if (root / "extracted").exists():
        roots.append(root / "extracted")
    roots.append(unpack_root)
    # Last fallback: maybe the user points directly at an extracted directory.
    roots.append(root)

    seen: set = set()
    files: List[Path] = []
    for base in roots:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file():
                key = str(p.resolve()).lower()
                if key not in seen:
                    seen.add(key)
                    files.append(p)
    return files


def find_exact(files: Sequence[Path], filename: str, dataset_hint: Optional[str] = None) -> Optional[Path]:
    hits = [p for p in files if p.name.lower() == filename.lower()]
    if dataset_hint:
        hinted = [p for p in hits if dataset_hint.lower() in str(p).lower()]
        if hinted:
            hits = hinted
    if not hits:
        return None
    # Prefer downloader's extracted directory, then converter unpacked directory.
    def score(p: Path) -> Tuple[int, int, str]:
        s = str(p).lower()
        rank = 0
        if "extracted" in s:
            rank = -2
        elif "_converter_unpacked" in s:
            rank = -1
        return (rank, len(str(p)), str(p))
    return sorted(hits, key=score)[0]


def find_all_exact(files: Sequence[Path], filename: str, dataset_hint: Optional[str] = None) -> List[Path]:
    hits = [p for p in files if p.name.lower() == filename.lower()]
    if dataset_hint:
        hinted = [p for p in hits if dataset_hint.lower() in str(p).lower()]
        if hinted:
            hits = hinted

    def score(p: Path) -> Tuple[int, int, str]:
        s = str(p).lower()
        rank = 0
        if "extracted" in s:
            rank = -2
        elif "_converter_unpacked" in s:
            rank = -1
        return (rank, len(str(p)), str(p))

    return sorted(hits, key=score)


def apply_value_options(table: SpectrumTable, aotf: str, scale_percent: bool) -> None:
    if table.dataset == "natural_colors":
        if aotf in {"clip", "normalize"}:
            table.spectra = [[min(max(v, 0.0), 4096.0) for v in row] for row in table.spectra]
            table.notes += " AOTF values clipped to [0,4096]."
        if aotf == "normalize":
            table.spectra = [[v / 4096.0 for v in row] for row in table.spectra]
            table.notes += " AOTF values divided by 4096."
        return

    if scale_percent:
        values = [v for row in table.spectra for v in row]
        if values:
            vmax = max(values)
            vmin = min(values)
            if vmax > 1.5 and vmax <= 100.0 and vmin >= -1e-9:
                table.spectra = [[v / 100.0 for v in row] for row in table.spectra]
                table.notes += " Values divided by 100 because --scale-percent was enabled."



def prefer_path(paths: Sequence[Path]) -> Path:
    """Choose one copy when the same file exists in extracted/ and _converter_unpacked/."""
    def score(p: Path) -> Tuple[int, int, str]:
        s = str(p).lower()
        if "extracted" in s:
            rank = 0
        elif "_converter_unpacked" in s:
            rank = 1
        else:
            rank = 2
        return (rank, len(str(p)), str(p))
    return sorted(paths, key=score)[0]


def dedupe_by_name(paths: Sequence[Path]) -> List[Path]:
    grouped: Dict[str, List[Path]] = {}
    for p in paths:
        grouped.setdefault(p.name.lower(), []).append(p)
    return [prefer_path(grouped[name]) for name in sorted(grouped)]


def load_tables(root: Path, out_dir: Path, aotf: str, scale_percent: bool, natural_policy: str) -> List[SpectrumTable]:
    unpack_root = unpack_archives(root, out_dir)
    files = candidate_files(root, unpack_root)
    tables: List[SpectrumTable] = []
    used: set = set()

    known_specs = [
        {
            "dataset": "munsell_matt_spectrophotometer",
            "subdataset": "munsell_matt",
            "filename": "munsell380_800_1.asc",
            "hint": "munsell_matt",
            "wavelengths": nm_grid(380, 800, 1),
            "n_samples": 1269,
            "notes": "Matt Munsell spectrophotometer ASCII data.",
        },
        {
            "dataset": "munsell_glossy_all_spectrophotometer",
            "subdataset": "munsell_glossy_all",
            "filename": "munsell380_780_1_glossy.asc",
            "hint": "glossy",
            "wavelengths": nm_grid(380, 780, 1),
            "n_samples": 1600,
            "notes": "Glossy Munsell all spectrophotometer ASCII data; specular excluded in original measurement notes.",
        },
        {
            "dataset": "munsell_glossy_subset_spectrophotometer",
            "subdataset": "munsell_glossy_subset",
            "filename": "munsell400_700_10.asc",
            "hint": "mglossy",
            "wavelengths": nm_grid(400, 700, 10),
            "n_samples": 32,
            "notes": "Optional small glossy Munsell subset.",
            "optional": True,
        },
        {
            "dataset": "agfa_it872",
            "subdataset": "agfa_it872",
            "filename": "agfait872.dat",
            "hint": "agfa",
            "wavelengths": nm_grid(400, 700, 10),
            "n_samples": 289,
            "notes": "Agfa IT8.7/2 target; 288 patches plus Minolta white calibration sample. If colour coordinates are appended in the DAT file, only the spectral channels are exported here.",
        },
    ]

    for spec in known_specs:
        if spec["dataset"] == "agfa_it872":
            path = find_exact(files, "agfait872.mat", "agfa") or find_exact(files, "agfait872.dat", "agfa")
        else:
            path = find_exact(files, spec["filename"], spec.get("hint"))
        if path is None:
            if spec.get("optional", False):
                print(f"[info] optional dataset not present: {spec['dataset']} ({spec['filename']})")
            else:
                print(f"[warn] missing {spec['dataset']}: {spec['filename']}", file=sys.stderr)
            continue
        try:
            if spec["dataset"] == "agfa_it872":
                spectra, actual_source = parse_agfa_dataset(files, path)
                labels = agfa_labels(len(spectra))
                source_file = actual_source
            else:
                spectra = parse_flat_or_matrix(
                    path,
                    spec["wavelengths"],
                    n_samples=spec["n_samples"],
                )
                labels = numbered_labels(spec["subdataset"], len(spectra))
                source_file = str(path)
            table = SpectrumTable(
                dataset=spec["dataset"],
                subdataset=spec["subdataset"],
                wavelengths=list(spec["wavelengths"]),
                spectra=spectra,
                labels=labels,
                source_file=source_file,
                notes=spec["notes"],
            )
            apply_value_options(table, aotf=aotf, scale_percent=scale_percent)
            tables.append(table)
            used.add(path.resolve())
            print(f"[ok] {table.dataset}/{table.subdataset}: {len(table.spectra)} spectra x {len(table.wavelengths)} bands")
        except Exception as exc:  # noqa: BLE001
            print(f"[error] failed to parse {path}: {exc}", file=sys.stderr)

    # Natural colors: label line followed by spectrum line. Try all matching
    # files because some local folders may contain both a bad extracted copy and
    # a valid converter-unpacked copy.
    natural_paths = find_all_exact(files, "natural400_700_5.asc", "natural")
    if natural_paths:
        natural_done = False
        last_error = None
        for path in natural_paths:
            try:
                spectra, labels = parse_natural_colors(path)
                if len(spectra) == 0:
                    last_error = "parsed 0 spectra"
                    continue

                natural_notes = (
                    "Natural colors AOTF ASCII data. The original README describes "
                    "these values as 12-bit raw A/D output and states 218 spectra."
                )
                if len(spectra) != 218:
                    if len(spectra) == 219:
                        msg = (
                            f"[info] natural_colors: README states 218 spectra, "
                            f"but this local file contains 219 parseable 61-band spectra: {path}"
                        )
                        print(msg)
                        natural_notes += " This local file contained 219 parseable spectra."
                    else:
                        print(
                            f"[warn] natural_colors: README states 218 spectra, parsed {len(spectra)} from {path}",
                            file=sys.stderr,
                        )
                        natural_notes += f" Parsed {len(spectra)} spectra from this local file."

                if natural_policy == "readme218" and len(spectra) > 218:
                    spectra = spectra[:218]
                    labels = labels[:218]
                    natural_notes += " Trimmed to the first 218 spectra because --natural-policy readme218 was used."
                elif natural_policy == "skip":
                    print("[info] natural_colors skipped because --natural-policy skip was used")
                    natural_done = True
                    break
                else:
                    natural_notes += " Kept all parseable spectra."

                table = SpectrumTable(
                    dataset="natural_colors",
                    subdataset="natural_colors",
                    wavelengths=nm_grid(400, 700, 5),
                    spectra=spectra,
                    labels=labels or numbered_labels("natural", len(spectra)),
                    source_file=str(path),
                    notes=natural_notes,
                )
                apply_value_options(table, aotf=aotf, scale_percent=scale_percent)
                tables.append(table)
                used.add(path.resolve())
                print(f"[ok] {table.dataset}/{table.subdataset}: {len(table.spectra)} spectra x {len(table.wavelengths)} bands")
                natural_done = True
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                print(f"[warn] failed to parse candidate natural file {path}: {exc}", file=sys.stderr)
        if not natural_done:
            print(f"[warn] natural_colors was found but could not be parsed: {last_error}", file=sys.stderr)
    else:
        print("[warn] missing natural_colors: natural400_700_5.asc", file=sys.stderr)

    # Forest colors: pine.dat, spruce.dat, birch.dat. Dimension is inferred from
    # sample count because the archive name is historically inconsistent while the
    # README describes 390-850 nm, 5 nm, i.e. 93 bands.
    forest_counts = {"spruce.dat": 349, "birch.dat": 337, "pine.dat": 370}
    for filename, n_samples in forest_counts.items():
        path = find_exact(files, filename, "forest")
        if path is None:
            print(f"[warn] missing forest_colors: {filename}", file=sys.stderr)
            continue
        try:
            # Infer whether the file contains 93 bands (390-850) or 95 bands (380-850).
            flat_count = sum(len(r) for r in read_numeric_rows(path))
            if flat_count >= n_samples * 95 and flat_count % n_samples == 0 and flat_count // n_samples == 95:
                wavelengths = nm_grid(380, 850, 5)
            else:
                wavelengths = nm_grid(390, 850, 5)
            spectra = parse_flat_or_matrix(path, wavelengths, n_samples=n_samples)
            sub = path.stem.lower()
            table = SpectrumTable(
                dataset="forest_colors",
                subdataset=sub,
                wavelengths=wavelengths,
                spectra=spectra,
                labels=numbered_labels(sub, len(spectra)),
                source_file=str(path),
                notes="Forest colors ASCII data; subdataset indicates tree type.",
            )
            apply_value_options(table, aotf=aotf, scale_percent=scale_percent)
            tables.append(table)
            used.add(path.resolve())
            print(f"[ok] {table.dataset}/{table.subdataset}: {len(table.spectra)} spectra x {len(table.wavelengths)} bands")
        except Exception as exc:  # noqa: BLE001
            print(f"[error] failed to parse {path}: {exc}", file=sys.stderr)

    # Paper spectra: ASCII files inside paper400_700_10.tar.gz are:
    # newsprintsci.asc, newsprintsce.asc, papersci.asc, papersce.asc,
    # cardboardsci.asc, cardboardsce.asc and mirrorsci.asc. mirrorsci.asc is a
    # calibration mirror spectrum, not a paper/cardboard material sample, so it
    # is skipped. We select exactly one canonical copy of each expected file so
    # extracted/ and _converter_unpacked/ do not get parsed twice.
    paper_expected = [
        "cardboardsce.asc",
        "cardboardsci.asc",
        "newsprintsce.asc",
        "newsprintsci.asc",
        "papersce.asc",
        "papersci.asc",
    ]
    paper_paths: List[Path] = []
    for filename in paper_expected:
        path = find_exact(files, filename, "paper")
        if path is not None:
            paper_paths.append(path)

    if not paper_paths:
        print(
            "[warn] missing paper_spectra ASCII files: expected files such as papersci.asc, papersce.asc, cardboardsci.asc",
            file=sys.stderr,
        )

    for path in paper_paths:
        try:
            wavelengths = nm_grid(400, 700, 10)
            spectra = parse_flat_or_matrix(path, wavelengths, n_samples=None)
            sub = path.stem.lower()
            table = SpectrumTable(
                dataset="paper_spectra",
                subdataset=sub,
                wavelengths=wavelengths,
                spectra=spectra,
                labels=numbered_labels(sub, len(spectra)),
                source_file=str(path),
                notes=(
                    "Paper spectra ASCII data. UEF README says every ASCII line contains one "
                    "31-component spectrum. The file name encodes material class and SCI/SCE measurement mode."
                ),
            )
            apply_value_options(table, aotf=aotf, scale_percent=scale_percent)
            tables.append(table)
            used.add(path.resolve())
            print(f"[ok] {table.dataset}/{table.subdataset}: {len(table.spectra)} spectra x {len(table.wavelengths)} bands")
        except Exception as exc:  # noqa: BLE001
            print(f"[error] failed to parse paper file {path}: {exc}", file=sys.stderr)

    if not tables:
        raise RuntimeError(
            "No spectra were parsed. Check --root: it should point to the folder containing raw/ and extracted/."
        )
    return tables


def sample_id(table: SpectrumTable, index: int) -> str:
    return f"{table.dataset}__{table.subdataset}__{index + 1:04d}"


def write_table_wide(path: Path, table: SpectrumTable) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        header = [
            "sample_id",
            "dataset",
            "subdataset",
            "label",
            "source_file",
            "n_wavelengths",
        ] + [f"nm_{wl}" for wl in table.wavelengths]
        writer.writerow(header)
        for i, values in enumerate(table.spectra):
            writer.writerow(
                [
                    sample_id(table, i),
                    table.dataset,
                    table.subdataset,
                    table.labels[i],
                    table.source_file,
                    len(table.wavelengths),
                ] + [format_float(v) for v in values]
            )


def write_all_wide_raw(path: Path, tables: Sequence[SpectrumTable]) -> None:
    all_wavelengths = sorted({wl for table in tables for wl in table.wavelengths})
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        header = ["sample_id", "dataset", "subdataset", "label", "source_file"] + [f"nm_{wl}" for wl in all_wavelengths]
        writer.writerow(header)
        for table in tables:
            for i, values in enumerate(table.spectra):
                value_map = dict(zip(table.wavelengths, values))
                writer.writerow(
                    [sample_id(table, i), table.dataset, table.subdataset, table.labels[i], table.source_file]
                    + [format_float(value_map.get(wl)) for wl in all_wavelengths]
                )


def interpolate_spectrum(wavelengths: Sequence[int], values: Sequence[float], target: Sequence[int]) -> List[Optional[float]]:
    result: List[Optional[float]] = []
    xs = list(wavelengths)
    ys = list(values)
    for t in target:
        if t < xs[0] or t > xs[-1]:
            result.append(None)
            continue
        j = bisect.bisect_left(xs, t)
        if j < len(xs) and xs[j] == t:
            result.append(float(ys[j]))
        elif j == 0 or j >= len(xs):
            result.append(None)
        else:
            x0, x1 = xs[j - 1], xs[j]
            y0, y1 = ys[j - 1], ys[j]
            if x1 == x0:
                result.append(float(y0))
            else:
                ratio = (t - x0) / (x1 - x0)
                result.append(float(y0 + ratio * (y1 - y0)))
    return result


def write_common_wide(path: Path, tables: Sequence[SpectrumTable], target_wavelengths: Sequence[int]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        header = ["sample_id", "dataset", "subdataset", "label", "source_file"] + [f"nm_{wl}" for wl in target_wavelengths]
        writer.writerow(header)
        for table in tables:
            for i, values in enumerate(table.spectra):
                interp = interpolate_spectrum(table.wavelengths, values, target_wavelengths)
                writer.writerow(
                    [sample_id(table, i), table.dataset, table.subdataset, table.labels[i], table.source_file]
                    + [format_float(v) for v in interp]
                )


def write_common_long(path: Path, tables: Sequence[SpectrumTable], target_wavelengths: Sequence[int]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "dataset", "subdataset", "label", "wavelength_nm", "value", "source_file"])
        for table in tables:
            for i, values in enumerate(table.spectra):
                sid = sample_id(table, i)
                interp = interpolate_spectrum(table.wavelengths, values, target_wavelengths)
                for wl, value in zip(target_wavelengths, interp):
                    writer.writerow([sid, table.dataset, table.subdataset, table.labels[i], wl, format_float(value), table.source_file])


def write_raw_long(path: Path, tables: Sequence[SpectrumTable]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "dataset", "subdataset", "label", "wavelength_nm", "value", "source_file"])
        for table in tables:
            for i, values in enumerate(table.spectra):
                sid = sample_id(table, i)
                for wl, value in zip(table.wavelengths, values):
                    writer.writerow([sid, table.dataset, table.subdataset, table.labels[i], wl, format_float(value), table.source_file])


def write_summary(path: Path, tables: Sequence[SpectrumTable], target_wavelengths: Sequence[int]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "dataset",
            "subdataset",
            "n_samples",
            "wavelength_start_nm",
            "wavelength_end_nm",
            "n_wavelengths",
            "source_file",
            "notes",
        ])
        for table in tables:
            writer.writerow([
                table.dataset,
                table.subdataset,
                len(table.spectra),
                table.wavelengths[0],
                table.wavelengths[-1],
                len(table.wavelengths),
                table.source_file,
                table.notes.strip(),
            ])
        writer.writerow([])
        writer.writerow(["common_grid", "", "", target_wavelengths[0], target_wavelengths[-1], len(target_wavelengths), "", "Used for all_spectra_wide_* and all_spectra_long_* files."])


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert UEF / University of Kuopio spectral datasets to CSV."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path("./uef_spectral_data"),
        help="Folder created by the downloader, usually ./uef_spectral_data",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("./uef_spectral_csv"),
        help="Output folder for CSV files",
    )
    parser.add_argument(
        "--common-start",
        type=int,
        default=400,
        help="Common-grid start wavelength in nm",
    )
    parser.add_argument(
        "--common-end",
        type=int,
        default=700,
        help="Common-grid end wavelength in nm",
    )
    parser.add_argument(
        "--common-step",
        type=int,
        default=10,
        help="Common-grid wavelength step in nm",
    )
    parser.add_argument(
        "--aotf",
        choices=["raw", "clip", "normalize"],
        default="raw",
        help=(
            "How to handle Natural colors AOTF 12-bit raw values: "
            "raw = unchanged; clip = clip to [0,4096]; normalize = clip then divide by 4096."
        ),
    )
    parser.add_argument(
        "--natural-policy",
        choices=["keep-all", "readme218", "skip"],
        default="keep-all",
        help=(
            "How to handle Natural colors when the local ASCII file contains 219 spectra while "
            "the README states 218: keep-all = preserve all parsed spectra; readme218 = keep only "
            "the first 218; skip = do not include Natural colors."
        ),
    )
    parser.add_argument(
        "--scale-percent",
        action="store_true",
        help="For non-AOTF datasets, divide values by 100 if they appear to be 0-100 percent reflectance.",
    )
    parser.add_argument(
        "--raw-long",
        action="store_true",
        help="Also write all_spectra_long_raw.csv. This can be a large file.",
    )
    args = parser.parse_args(argv)

    root = args.root.expanduser().resolve()
    out_dir = args.out.expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if not root.exists():
        print(f"[error] root directory does not exist: {root}", file=sys.stderr)
        return 2

    target_wavelengths = nm_grid(args.common_start, args.common_end, args.common_step)
    print(f"UEF CSV converter v{VERSION}")
    tables = load_tables(root=root, out_dir=out_dir, aotf=args.aotf, scale_percent=args.scale_percent, natural_policy=args.natural_policy)

    per_dir = out_dir / "per_dataset_wide"
    per_dir.mkdir(parents=True, exist_ok=True)
    for table in tables:
        write_table_wide(per_dir / f"{table.dataset}__{table.subdataset}__wide.csv", table)

    write_all_wide_raw(out_dir / "all_spectra_wide_raw.csv", tables)
    common_name = f"all_spectra_wide_{args.common_start}_{args.common_end}_{args.common_step}.csv"
    long_common_name = f"all_spectra_long_{args.common_start}_{args.common_end}_{args.common_step}.csv"
    write_common_wide(out_dir / common_name, tables, target_wavelengths)
    write_common_long(out_dir / long_common_name, tables, target_wavelengths)
    if args.raw_long:
        write_raw_long(out_dir / "all_spectra_long_raw.csv", tables)
    write_summary(out_dir / "summary.csv", tables, target_wavelengths)

    n_samples_total = sum(len(t.spectra) for t in tables)
    print("\nDone.")
    print(f"Parsed tables: {len(tables)}")
    print(f"Total spectra: {n_samples_total}")
    print(f"CSV output: {out_dir}")
    print(f"Recommended modelling file: {out_dir / common_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
