"""Video signal colour encoding helpers."""

from __future__ import annotations

from .ictcp import (
    ICtCp_to_RGB_BT2020,
    RGB_BT2020_to_ICtCp,
)
from .transfer import (
    eotf_ST2084,
    eotf_inverse_ST2084,
    oetf_ARIBSTDB67,
    oetf_inverse_ARIBSTDB67,
)
from .ycbcr import (
    RGB_to_YCbCr,
    WEIGHTS_YCBCR,
    YCbCr_to_RGB,
    code_value_range,
    matrix_YCbCr,
    offset_YCbCr,
    ranges_YCbCr,
    round_BT2100,
)

__all__ = [
    "RGB_BT2020_to_ICtCp",  # encode BT.2020 linear RGB to ICtCp
    "ICtCp_to_RGB_BT2020",  # decode ICtCp to BT.2020 linear RGB
]

__all__ += [
    "eotf_ST2084",  # decode PQ signal values to luminance
    "eotf_inverse_ST2084",  # encode luminance values with PQ
    "oetf_ARIBSTDB67",  # encode scene values with HLG OETF
    "oetf_inverse_ARIBSTDB67",  # decode HLG OETF signal values
]

__all__ += [
    "WEIGHTS_YCBCR",  # YCbCr luma weighting presets
    "round_BT2100",  # ITU-R BT.2100 half-up rounding rule
    "code_value_range",  # RGB code value range helper
    "ranges_YCbCr",  # YCbCr code range helper
    "matrix_YCbCr",  # YCbCr-to-RGB matrix helper
    "offset_YCbCr",  # RGB-to-YCbCr offset helper
    "RGB_to_YCbCr",  # encode non-linear RGB to YCbCr
    "YCbCr_to_RGB",  # decode YCbCr to non-linear RGB
]
