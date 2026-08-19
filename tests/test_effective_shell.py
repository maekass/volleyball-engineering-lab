import pytest

from ball001.design import (
    BALL_001,
    EvidenceClass,
)
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
    EffectiveShellMaterial,
    calculate_effective_shell_verification,
    total_wall_thickness_m,
    validate_effective_material,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
    BALL001_PRESSURE_CASES,
)


def test_total_wall_thickness_matches_layer_stack() -> None:
    assert (
        total_wall_thickness_m(
            BALL_001
        )
        == pytest.approx(
            0.00265
        )
    )


def test_verification_material_is_pending() -> None:
    assert (
        BALL001_VERIFICATION_MATERIAL.evidence
        == EvidenceClass.PENDING
    )


def test_verification_material_is_valid() -> None:
    validate_effective_material(
        BALL001_VERIFICATION_MATERIAL
    )


def test_membrane_stress_increases_with_pressure() -> None:
    results = [
        calculate_effective_shell_verification(
            BALL_001,
            load_case,
            BALL001_VERIFICATION_MATERIAL,
        )
        for load_case in BALL001_PRESSURE_CASES
    ]

    stresses = [
        result.membrane_stress_pa
        for result in results
    ]

    assert stresses == sorted(
        stresses
    )


def test_nominal_membrane_stress_matches_resultant_over_thickness() -> None:
    result = (
        calculate_effective_shell_verification(
            BALL_001,
            BALL001_NOMINAL_PRESSURE,
            BALL001_VERIFICATION_MATERIAL,
        )
    )

    expected_stress_pa = (
        result.membrane_resultant_n_per_m
        / result.wall_thickness_m
    )

    assert (
        result.membrane_stress_pa
        == pytest.approx(
            expected_stress_pa
        )
    )


def test_radial_expansion_is_positive() -> None:
    result = (
        calculate_effective_shell_verification(
            BALL_001,
            BALL001_NOMINAL_PRESSURE,
            BALL001_VERIFICATION_MATERIAL,
        )
    )

    assert result.radial_expansion_m > 0.0


def test_invalid_youngs_modulus_is_rejected() -> None:
    invalid_material = EffectiveShellMaterial(
        name="invalid",
        youngs_modulus_pa=0.0,
        poisson_ratio=0.30,
        evidence=EvidenceClass.PENDING,
        note="Invalid test material.",
    )

    with pytest.raises(
        ValueError,
        match="Young's modulus",
    ):
        validate_effective_material(
            invalid_material
        )