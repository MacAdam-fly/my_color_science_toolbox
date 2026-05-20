"""Plot RGB colour-space gamuts and exercise RGB/XYZ round-trips."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import matplotlib.pyplot as plt
import numpy as np

from color.spaces import RGB_to_XYZ, XYZ_to_RGB, get_RGB_colourspace


def _xy_from_XYZ(XYZ: np.ndarray) -> np.ndarray:
    """Return xy chromaticity coordinates from XYZ values."""
    denominator = np.sum(XYZ, axis=-1)
    return XYZ[..., :2] / denominator[..., None]


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "output"
    output_dir.mkdir(exist_ok=True)

    sample_rgb = np.array([0.25, 0.5, 0.75])
    for name in ["sRGB", "Display P3", "Rec.2020", "DCI-P3"]:
        XYZ = RGB_to_XYZ(sample_rgb, colourspace=name)
        recovered = XYZ_to_RGB(XYZ, colourspace=name)
        print(f"{name}: XYZ={np.round(XYZ, 6)}, recovered={np.round(recovered, 6)}")

    fig, ax = plt.subplots(figsize=(7.2, 5.8))
    for name, color in [
        ("sRGB", "tab:blue"),
        ("Display P3", "tab:green"),
        ("Rec.2020", "tab:red"),
        ("DCI-P3", "tab:purple"),
    ]:
        space = get_RGB_colourspace(name)
        primaries_xyz = RGB_to_XYZ(
            np.identity(3),
            colourspace=space,
            apply_decoding=False,
        )
        primaries_xy = _xy_from_XYZ(primaries_xyz)
        closed = np.vstack([primaries_xy, primaries_xy[0]])
        ax.plot(closed[:, 0], closed[:, 1], marker="o", color=color, label=name)
        ax.scatter(*space.white_xy, color=color, marker="x", s=55)

    ax.set_title("RGB Colour-Space Gamuts in CIE xy")
    ax.set_xlabel("CIE x")
    ax.set_ylabel("CIE y")
    ax.set_xlim(0.0, 0.85)
    ax.set_ylim(0.0, 0.9)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=9)
    fig.tight_layout()

    output_path = output_dir / "rgb_colourspaces_xy.png"
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Plot saved to {output_path}")

    RGB_list = [
        [0.1, 0.2, 0.4],
        [0.5, 0.5, 0.5],
        [0.9, 0.8, 0.7],
    ]

    # 测试转换链路
    for name in ["sRGB", "Display P3", "Rec.2020", "DCI-P3"]:
        space = get_RGB_colourspace(name)
        primaries_xyz = RGB_to_XYZ(
            RGB_list,
            colourspace=space,
            apply_decoding=True,
        )
        recovered_rgb = XYZ_to_RGB(
            primaries_xyz,
            colourspace=space,
            apply_encoding=True,
        )
        print(f"{name} primaries round-trip: {np.round(recovered_rgb, 6)}")


if __name__ == "__main__":
    main()
