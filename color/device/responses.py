"""Primary response display definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from color.spectra import (
    MultiSpectralDistribution,
    SpectralDistribution,
    SpectralShape,
    from_cie2006_lms_10degree_fundamentals,
    from_cie2012_xyz_10degree_cmfs,
    from_iprgc_melanopic,
)


LMS_RESPONSE_NAMES = ("l", "m", "s")
XYZ_RESPONSE_NAMES = ("x", "y", "z")
MELANOPIC_RESPONSE_NAME = "mel"
ALLOWED_RESPONSE_NAMES = (*LMS_RESPONSE_NAMES, *XYZ_RESPONSE_NAMES, MELANOPIC_RESPONSE_NAME)
FULL_RESPONSE_NAMES = (*LMS_RESPONSE_NAMES, *XYZ_RESPONSE_NAMES, MELANOPIC_RESPONSE_NAME)
LMS_MEL_RESPONSE_NAMES = (*LMS_RESPONSE_NAMES, MELANOPIC_RESPONSE_NAME)
XYZ_MEL_RESPONSE_NAMES = (*XYZ_RESPONSE_NAMES, MELANOPIC_RESPONSE_NAME)


def _readonly_2d(value: Sequence[Sequence[float]] | np.ndarray, name: str) -> np.ndarray:
    """Return a read-only finite two-dimensional float array."""
    array = np.array(value, dtype=np.float64, copy=True)
    if array.ndim != 2:
        raise ValueError(f"{name} must be a two-dimensional array")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain finite values")
    array.setflags(write=False)
    return array


def _canonical_response_name(name: str) -> str:
    """Return a canonical response name."""
    key = str(name).strip().lower()
    if key == "melanopic":
        key = MELANOPIC_RESPONSE_NAME
    if key not in ALLOWED_RESPONSE_NAMES:
        raise ValueError(
            "response_names may only contain l, m, s, x, y, z and mel"
        )
    return key


def _response_names(value: Sequence[str]) -> tuple[str, ...]:
    """Return canonical response names and validate supported groups."""
    names = tuple(_canonical_response_name(name) for name in value)
    if not names:
        raise ValueError("response_names must not be empty")
    if len(set(names)) != len(names):
        raise ValueError("response_names contain duplicates after canonicalization")
    if MELANOPIC_RESPONSE_NAME not in names:
        raise ValueError("response_names must contain 'mel'")

    has_lms = all(name in names for name in LMS_RESPONSE_NAMES)
    has_xyz = all(name in names for name in XYZ_RESPONSE_NAMES)
    if not has_lms and not has_xyz:
        raise ValueError("response_names must contain a complete LMS or XYZ response group")

    partial_lms = any(name in names for name in LMS_RESPONSE_NAMES) and not has_lms
    partial_xyz = any(name in names for name in XYZ_RESPONSE_NAMES) and not has_xyz
    if partial_lms:
        raise ValueError("response_names must contain l, m and s together")
    if partial_xyz:
        raise ValueError("response_names must contain x, y and z together")
    return names


def _primary_names(value: Sequence[str] | None, count: int) -> tuple[str, ...]:
    """Return primary names with generated defaults."""
    if value is None:
        return tuple(f"P{i}" for i in range(count))
    names = tuple(str(name) for name in value)
    if len(names) != count:
        raise ValueError("primary_names length must match the number of primaries")
    if len(set(names)) != len(names):
        raise ValueError("primary_names must be unique")
    return names


def _as_weights(value: Sequence[float] | np.ndarray, count: int) -> np.ndarray:
    """Return finite primary weights with final axis equal to *count*."""
    weights = np.array(value, dtype=np.float64, copy=False)
    if weights.shape == () or weights.shape[-1] != count:
        raise ValueError(f"weights must have final-axis length {count}")
    if not np.all(np.isfinite(weights)):
        raise ValueError("weights must contain finite values")
    return weights


def _default_shape(
    shape: SpectralShape | None,
    melanopic: SpectralDistribution,
) -> SpectralShape:
    """Return the default spectral integration shape."""
    return melanopic.shape if shape is None else shape


def _as_primary_spds(
    primary_spds: MultiSpectralDistribution | Sequence[SpectralDistribution],
    *,
    shape: SpectralShape,
    primary_names: Sequence[str] | None,
) -> tuple[np.ndarray, tuple[str, ...]]:
    """Return aligned primary SPD values and names."""
    if isinstance(primary_spds, MultiSpectralDistribution):
        aligned = primary_spds.align(
            shape,
            extrapolator="fill",
            fill_value=0.0,
        )
        names = _primary_names(primary_names or aligned.labels, aligned.values.shape[1])
        return aligned.values, names

    spectra = tuple(primary_spds)
    if not spectra:
        raise ValueError("primary_spds must contain at least one primary")
    if not all(isinstance(spectrum, SpectralDistribution) for spectrum in spectra):
        raise ValueError(
            "primary_spds must be a MultiSpectralDistribution or a sequence "
            "of SpectralDistribution"
        )

    aligned_values = [
        spectrum.align(shape, extrapolator="fill", fill_value=0.0).values
        for spectrum in spectra
    ]
    generated_names = tuple(
        spectrum.name if spectrum.name else f"P{index}"
        for index, spectrum in enumerate(spectra)
    )
    names = _primary_names(primary_names or generated_names, len(spectra))
    return np.column_stack(aligned_values), names


def _aligned_lms_values(
    fundamentals: MultiSpectralDistribution,
    shape: SpectralShape,
) -> np.ndarray:
    """Return aligned LMS response values."""
    if not all(label in fundamentals.labels for label in LMS_RESPONSE_NAMES):
        raise ValueError("fundamentals must contain labels ('l', 'm', 's')")
    aligned = fundamentals.align(
        shape,
        extrapolator="fill",
        fill_value=0.0,
        left=0.0,
        right=0.0,
    )
    return aligned.values[:, [aligned.labels.index(name) for name in LMS_RESPONSE_NAMES]]


def _aligned_xyz_values(
    cmfs: MultiSpectralDistribution,
    shape: SpectralShape,
) -> np.ndarray:
    """Return aligned XYZ response values in canonical x, y, z order."""
    if not all(label in cmfs.labels for label in ("X", "Y", "Z")):
        raise ValueError("cmfs must contain labels ('X', 'Y', 'Z')")
    aligned = cmfs.align(
        shape,
        extrapolator="fill",
        fill_value=0.0,
        left=0.0,
        right=0.0,
    )
    return aligned.values[:, [aligned.labels.index(name) for name in ("X", "Y", "Z")]]


def _aligned_melanopic_values(
    melanopic: SpectralDistribution,
    shape: SpectralShape,
) -> np.ndarray:
    """Return aligned melanopic response values."""
    return melanopic.align(
        shape,
        extrapolator="fill",
        fill_value=0.0,
        left=0.0,
        right=0.0,
    ).values


def _response_values_for_names(
    response_names: tuple[str, ...],
    *,
    fundamentals: MultiSpectralDistribution,
    cmfs: MultiSpectralDistribution,
    melanopic: SpectralDistribution,
    shape: SpectralShape,
) -> np.ndarray:
    """Return aligned response values matching *response_names*."""
    value_map: dict[str, np.ndarray] = {}
    if any(name in response_names for name in LMS_RESPONSE_NAMES):
        lms = _aligned_lms_values(fundamentals, shape)
        value_map.update({name: lms[:, index] for index, name in enumerate(LMS_RESPONSE_NAMES)})
    if any(name in response_names for name in XYZ_RESPONSE_NAMES):
        xyz = _aligned_xyz_values(cmfs, shape)
        value_map.update({name: xyz[:, index] for index, name in enumerate(XYZ_RESPONSE_NAMES)})
    value_map[MELANOPIC_RESPONSE_NAME] = _aligned_melanopic_values(melanopic, shape)
    return np.column_stack([value_map[name] for name in response_names])


@dataclass(frozen=True)
class PrimaryResponseDisplay:
    """Display primary responses for silent-substitution calculations.

    Parameters
    ----------
    primary_responses
        Response matrix with shape ``(n_primaries, n_responses)``. Rows are
        primaries; columns are response channels.
    response_names
        Response channel names. Names are case-insensitive and canonicalized
        to lower-case. Allowed names are ``l, m, s, x, y, z, mel``.
    primary_names
        Optional primary names. If omitted, names are generated as
        ``P0, P1, ...``.

    Notes
    -----
    ``mel`` is always required. A complete ``l/m/s`` or ``x/y/z`` group is
    also required so that the object can be used for at least one supported
    silent-substitution mode.
    """

    primary_responses: np.ndarray
    response_names: Sequence[str]
    primary_names: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        responses = _readonly_2d(self.primary_responses, "primary_responses")
        if responses.shape[0] < 1:
            raise ValueError("primary_responses must contain at least one primary")
        names = _response_names(self.response_names)
        if responses.shape[1] != len(names):
            raise ValueError("response_names length must match primary_responses columns")

        object.__setattr__(self, "primary_responses", responses)
        object.__setattr__(self, "response_names", names)
        object.__setattr__(
            self,
            "primary_names",
            _primary_names(self.primary_names, responses.shape[0]),
        )

    @property
    def primary_count(self) -> int:
        """Return the number of display primaries."""
        return self.primary_responses.shape[0]

    @property
    def response_count(self) -> int:
        """Return the number of response channels."""
        return self.primary_responses.shape[1]

    def response_indices(self, names: Sequence[str]) -> tuple[int, ...]:
        """Return response indices for canonical response names."""
        canonical = tuple(_canonical_response_name(name) for name in names)
        missing = [name for name in canonical if name not in self.response_names]
        if missing:
            raise ValueError(f"display does not contain required responses: {missing}")
        return tuple(self.response_names.index(name) for name in canonical)

    @property
    def lms_indices(self) -> tuple[int, int, int]:
        """Return indices for ``l``, ``m`` and ``s`` response channels."""
        return self.response_indices(LMS_RESPONSE_NAMES)

    @property
    def xyz_indices(self) -> tuple[int, int, int]:
        """Return indices for ``x``, ``y`` and ``z`` response channels."""
        return self.response_indices(XYZ_RESPONSE_NAMES)

    @property
    def mel_index(self) -> int:
        """Return the index for the melanopic response channel."""
        return self.response_indices((MELANOPIC_RESPONSE_NAME,))[0]

    @classmethod
    def _from_primary_spds_with_responses(
        cls,
        primary_spds: MultiSpectralDistribution | Sequence[SpectralDistribution],
        *,
        response_names: tuple[str, ...],
        fundamentals: MultiSpectralDistribution | None,
        cmfs: MultiSpectralDistribution | None,
        melanopic: SpectralDistribution | None,
        shape: SpectralShape | None,
        primary_names: Sequence[str] | None,
    ) -> "PrimaryResponseDisplay":
        """Build a display response matrix from primary spectra and responses."""
        fundamentals = fundamentals or from_cie2006_lms_10degree_fundamentals()
        cmfs = cmfs or from_cie2012_xyz_10degree_cmfs()
        melanopic = melanopic or from_iprgc_melanopic()
        common_shape = _default_shape(shape, melanopic)
        primary_values, names = _as_primary_spds(
            primary_spds,
            shape=common_shape,
            primary_names=primary_names,
        )
        response_values = _response_values_for_names(
            response_names,
            fundamentals=fundamentals,
            cmfs=cmfs,
            melanopic=melanopic,
            shape=common_shape,
        )
        primary_responses = primary_values.T @ response_values * common_shape.interval
        return cls(
            primary_responses,
            response_names=response_names,
            primary_names=names,
        )

    @classmethod
    def from_primary_spds(
        cls,
        primary_spds: MultiSpectralDistribution | Sequence[SpectralDistribution],
        *,
        fundamentals: MultiSpectralDistribution | None = None,
        cmfs: MultiSpectralDistribution | None = None,
        melanopic: SpectralDistribution | None = None,
        shape: SpectralShape | None = None,
        primary_names: Sequence[str] | None = None,
    ) -> "PrimaryResponseDisplay":
        """Build full LMS, XYZ and melanopic responses from primary spectra."""
        return cls._from_primary_spds_with_responses(
            primary_spds,
            response_names=FULL_RESPONSE_NAMES,
            fundamentals=fundamentals,
            cmfs=cmfs,
            melanopic=melanopic,
            shape=shape,
            primary_names=primary_names,
        )

    @classmethod
    def from_primary_spds_lms_mel(
        cls,
        primary_spds: MultiSpectralDistribution | Sequence[SpectralDistribution],
        *,
        fundamentals: MultiSpectralDistribution | None = None,
        melanopic: SpectralDistribution | None = None,
        shape: SpectralShape | None = None,
        primary_names: Sequence[str] | None = None,
    ) -> "PrimaryResponseDisplay":
        """Build LMS and melanopic responses from primary spectra."""
        return cls._from_primary_spds_with_responses(
            primary_spds,
            response_names=LMS_MEL_RESPONSE_NAMES,
            fundamentals=fundamentals,
            cmfs=None,
            melanopic=melanopic,
            shape=shape,
            primary_names=primary_names,
        )

    @classmethod
    def from_primary_spds_xyz_mel(
        cls,
        primary_spds: MultiSpectralDistribution | Sequence[SpectralDistribution],
        *,
        cmfs: MultiSpectralDistribution | None = None,
        melanopic: SpectralDistribution | None = None,
        shape: SpectralShape | None = None,
        primary_names: Sequence[str] | None = None,
    ) -> "PrimaryResponseDisplay":
        """Build XYZ and melanopic responses from primary spectra."""
        return cls._from_primary_spds_with_responses(
            primary_spds,
            response_names=XYZ_MEL_RESPONSE_NAMES,
            fundamentals=None,
            cmfs=cmfs,
            melanopic=melanopic,
            shape=shape,
            primary_names=primary_names,
        )

    def responses_from_weights(self, weights: Sequence[float] | np.ndarray) -> np.ndarray:
        """Return full responses for primary weights."""
        weight_array = _as_weights(weights, self.primary_count)
        return weight_array @ self.primary_responses

    def LMS_from_weights(self, weights: Sequence[float] | np.ndarray) -> np.ndarray:
        """Return ``L, M, S`` responses for primary weights."""
        responses = self.responses_from_weights(weights)
        return responses[..., list(self.lms_indices)]

    def XYZ_from_weights(self, weights: Sequence[float] | np.ndarray) -> np.ndarray:
        """Return ``X, Y, Z`` responses for primary weights."""
        responses = self.responses_from_weights(weights)
        return responses[..., list(self.xyz_indices)]

    def melanopic_from_weights(self, weights: Sequence[float] | np.ndarray) -> np.ndarray | np.float64:
        """Return melanopic response for primary weights."""
        values = np.asarray(self.responses_from_weights(weights)[..., self.mel_index])
        return values[()] if values.shape == () else values


__all__ = [
    "PrimaryResponseDisplay",
]
