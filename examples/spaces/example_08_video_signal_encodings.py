"""Use explicit video signal encoding helpers."""

from __future__ import annotations

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import numpy as np

from color.spaces import list_colourspace_nodes
from color.spaces.video import (
    ICtCp_to_RGB_BT2020,
    RGB_BT2020_to_ICtCp,
    RGB_to_YCbCr,
    YCbCr_to_RGB,
    eotf_ST2084,
    eotf_inverse_ST2084,
    oetf_ARIBSTDB67,
    oetf_inverse_ARIBSTDB67,
)


def main() -> None:
    """Run compact video signal encoding examples."""
    rgb_bt2020 = np.array([0.45620519, 0.03081071, 0.04091952])
    ictcp = RGB_BT2020_to_ICtCp(rgb_bt2020)
    rgb_bt2020_recovered = ICtCp_to_RGB_BT2020(ictcp)

    rgb_code = np.array([0.25, 0.50, 0.75])
    ycbcr = RGB_to_YCbCr(rgb_code, standard="BT.709")
    rgb_code_recovered = YCbCr_to_RGB(ycbcr, standard="BT.709")

    luminance = np.array([0.0, 100.0, 1000.0])
    pq_signal = eotf_inverse_ST2084(luminance)
    luminance_recovered = eotf_ST2084(pq_signal)

    hlg_scene = np.array([0.0, 0.25, 1.0, 12.0])
    hlg_signal = oetf_ARIBSTDB67(hlg_scene)
    hlg_scene_recovered = oetf_inverse_ARIBSTDB67(hlg_signal)

    nodes = list_colourspace_nodes()

    print("=" * 20 + " video signal encodings " + "=" * 20)
    print("BT.2020 linear RGB:", np.round(rgb_bt2020, 8))
    print("ICtCp:", np.round(ictcp, 12))
    print("ICtCp round-trip max error:", np.max(np.abs(rgb_bt2020_recovered - rgb_bt2020)))
    print("R'G'B' code values:", rgb_code)
    print("YCbCr BT.709:", np.round(ycbcr, 12))
    print("YCbCr round-trip max error:", np.max(np.abs(rgb_code_recovered - rgb_code)))
    print("PQ signal:", np.round(pq_signal, 12))
    print("PQ luminance round-trip:", np.round(luminance_recovered, 8))
    print("HLG signal:", np.round(hlg_signal, 12))
    print("HLG scene round-trip:", np.round(hlg_scene_recovered, 8))
    print("ICtCp registered in convert_color graph:", "ICtCp" in nodes)
    print("YCbCr registered in convert_color graph:", "YCbCr" in nodes)


if __name__ == "__main__":
    main()
