from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent
COLOR_PACKAGE = ROOT / "color"

VERSION = "1.0.1"

RUNTIME_DATA_PATTERNS = (
    "data/color_cards/*.csv",
    "data/color_cards/*.xls",
    "data/color_cards/*.xlsx",
    "data/color_difference/*.xls",
    "data/color_systems/*.xls",
    "data/gamut_data/*.csv",
    "data/gamut_data/*.xls",
    "data/illuminants/*.csv",
    "data/illuminants/*.xls",
    "data/illuminants/reference/*.xlsx",
    "data/reflectance_spectra/uef_csv/*.csv",
    "data/standard_observer_data/*/*.csv",
)


def package_data_files() -> list[str]:
    """Return runtime data files relative to the ``color`` package."""

    files: list[str] = []
    for pattern in RUNTIME_DATA_PATTERNS:
        files.extend(
            path.relative_to(COLOR_PACKAGE).as_posix()
            for path in sorted(COLOR_PACKAGE.glob(pattern))
            if path.is_file()
        )
    return files


def package_documentation_files() -> list[str]:
    """Return installed documentation files relative to the ``color`` package."""

    docs_root = COLOR_PACKAGE / "docs"
    if not docs_root.exists():
        return []
    return [
        path.relative_to(COLOR_PACKAGE).as_posix()
        for path in sorted(docs_root.rglob("*.md"))
        if path.is_file()
    ]


setup(
    name="color-science-toolbox",
    version=VERSION,
    description="A low-level color-science toolkit for spectra, colorimetry, spaces, gamut, recovery, device, plotting, and IO.",
    long_description=(ROOT / "readme.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="MacAdam-fly",
    python_requires=">=3.9",
    packages=find_packages(
        include=("color", "color.*"),
        exclude=("color.tests", "color.tests.*"),
    ),
    package_data={"color": package_data_files() + package_documentation_files()},
    include_package_data=False,
    install_requires=[
        "numpy>=1.26",
        "scipy>=1.13",
        "pandas>=2.3",
        "matplotlib>=3.9",
        "pillow>=11.3",
        "imageio>=2.37",
        "openpyxl>=3.1",
        "xlrd>=2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.4",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Scientific/Engineering",
    ],
)
