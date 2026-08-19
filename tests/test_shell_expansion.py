import pytest

from ball001.design import (
    BALL_001,
    EvidenceClass,
)
from ball001.shell_expansion import (
    SHELL_STIFFNESS_CASES,
    EffectiveShellMaterial,
    calculate_shell_expansion,
    calculate_stiffness_sensitivity,
)


def test_three_stiffness_cases_exist() -> None:
    results = calculate_stiffness_sensitivity(
        BALL_001
    )

    assert len(results) == 3


def test_stiffness_cases_are_pending() -> None:
    assert all(
        material.evidence
        == EvidenceClass.PENDING
        for material in SHELL_STIFFNESS_CASES
    )


def test_displacement_decreases_with_stiffness() -> None:
    results = calculate_stiffness_sensitivity(
        BALL_001
    )

    displacements = [
        result.radial_displacement_m
        for result in results
    ]

    assert (
        displacements[0]
        > displacements[1]
        > displacements[2]
    )


def test_strain_and_displacement_are_positive() -> None:
    result = calculate_shell_expansion(
        BALL_001,
        SHELL_STIFFNESS_CASES[1],
    )

    assert result.biaxial_strain > 0.0
    assert result.radial_displacement_m > 0.0
    assert result.circumference_change_m > 0.0


def test_circumference_change_matches_strain() -> None:
    result = calculate_shell_expansion(
        BALL_001,
        SHELL_STIFFNESS_CASES[1],
    )

    assert result.circumference_change_m == pytest.approx(
        BALL_001.circumference_m
        * result.biaxial_strain
    )


def test_nonpositive_modulus_is_rejected() -> None:
    invalid_material = EffectiveShellMaterial(
        name="invalid",
        youngs_modulus_pa=0.0,
        poisson_ratio=0.35,
        evidence=EvidenceClass.PENDING,
        note="Invalid test fixture.",
    )

    with pytest.raises(ValueError):
        calculate_shell_expansion(
            BALL_001,
            invalid_material,
        )


def test_invalid_poisson_ratio_is_rejected() -> None:
    invalid_material = EffectiveShellMaterial(
        name="invalid",
        youngs_modulus_pa=20_000_000.0,
        poisson_ratio=0.5,
        evidence=EvidenceClass.PENDING,
        note="Invalid test fixture.",
    )

    with pytest.raises(ValueError):
        calculate_shell_expansion(
            BALL_001,
            invalid_material,
        )