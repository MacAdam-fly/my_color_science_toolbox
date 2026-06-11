"""Colour appearance models."""

from __future__ import annotations

from .ciecam16 import (
    CIECAM16Specification,
    CIECAM16ViewingConditions,
    CIECAM16_to_XYZ,
    InductionFactors_CIECAM16,
    VIEWING_CONDITIONS_CIECAM16,
    XYZ_to_CIECAM16,
)
from .ciecam02 import (
    CIECAM02Specification,
    CIECAM02ViewingConditions,
    CIECAM02_to_XYZ,
    InductionFactors_CIECAM02,
    VIEWING_CONDITIONS_CIECAM02,
    XYZ_to_CIECAM02,
)

__all__ = [
    "InductionFactors_CIECAM02",  # CIECAM02 surround induction factors
    "VIEWING_CONDITIONS_CIECAM02",  # named Average / Dim / Dark surround presets
    "CIECAM02ViewingConditions",  # complete CIECAM02 viewing-condition container
    "CIECAM02Specification",  # CIECAM02 appearance correlates J, C, h, s, Q, M, H, HC
    "XYZ_to_CIECAM02",  # forward CIECAM02 appearance model
    "CIECAM02_to_XYZ",  # inverse CIECAM02 appearance model
]

__all__ += [
    "InductionFactors_CIECAM16",  # CIECAM16 surround induction factors
    "VIEWING_CONDITIONS_CIECAM16",  # named Average / Dim / Dark CIECAM16 surround presets
    "CIECAM16ViewingConditions",  # complete CIECAM16 viewing-condition container
    "CIECAM16Specification",  # CIECAM16 appearance correlates J, C, h, s, Q, M, H, HC
    "XYZ_to_CIECAM16",  # forward CIECAM16 appearance model
    "CIECAM16_to_XYZ",  # inverse CIECAM16 appearance model
]
