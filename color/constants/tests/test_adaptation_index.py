from __future__ import annotations

from color import constants
from color.adaptation import matrices as adaptation_runtime_matrices
from color.constants import adaptation_matrices


def test_adaptation_matrices_are_available_from_constants_top_level() -> None:
    assert constants.CAT_VON_KRIES is adaptation_matrices.CAT_VON_KRIES
    assert constants.CAT_BRADFORD is adaptation_matrices.CAT_BRADFORD
    assert constants.CAT_CAT02 is adaptation_matrices.CAT_CAT02
    assert constants.CAT_CAT16 is adaptation_matrices.CAT_CAT16
    assert (
        constants.CHROMATIC_ADAPTATION_TRANSFORMS
        is adaptation_matrices.CHROMATIC_ADAPTATION_TRANSFORMS
    )


def test_adaptation_matrices_submodule_reexports_constants_objects() -> None:
    assert adaptation_matrices.CAT_VON_KRIES is adaptation_runtime_matrices.CAT_VON_KRIES
    assert adaptation_matrices.CAT_BRADFORD is adaptation_runtime_matrices.CAT_BRADFORD
    assert adaptation_matrices.CAT_CAT02 is adaptation_runtime_matrices.CAT_CAT02
    assert adaptation_matrices.CAT_CAT16 is adaptation_runtime_matrices.CAT_CAT16
    assert (
        adaptation_matrices.CHROMATIC_ADAPTATION_TRANSFORMS
        is adaptation_runtime_matrices.CHROMATIC_ADAPTATION_TRANSFORMS
    )
