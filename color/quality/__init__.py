"""Colour quality metrics."""

from __future__ import annotations

from .ssi import SPECTRAL_SHAPE_SSI, spectral_similarity_index

__all__ = [
    "SPECTRAL_SHAPE_SSI",  # Academy SSI spectral sampling shape
    "spectral_similarity_index",  # compute Academy Spectral Similarity Index
]
