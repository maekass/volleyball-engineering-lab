import pytest

from ball001.structural_model_decision import (
    BALL001_STRUCTURAL_EVIDENCE,
    BALL001_STRUCTURAL_MODEL,
    GeometryModel,
    ShellFormulation,
    StructuralModelDecision,
)


def test_default_mesh_is_medium_eight_mm() -> None:
    assert (
        BALL001_STRUCTURAL_MODEL.working_mesh_size_mm
        == pytest.approx(8.0)
    )

    assert (
        BALL001_STRUCTURAL_MODEL.verification_mesh_size_mm
        == pytest.approx(5.0)
    )


def test_default_formulation_is_s3() -> None:
    assert (
        BALL001_STRUCTURAL_MODEL.default_formulation
        is ShellFormulation.S3
    )

    assert (
        BALL001_STRUCTURAL_MODEL.verification_formulation
        is ShellFormulation.S6
    )


def test_default_geometry_is_linear() -> None:
    assert (
        BALL001_STRUCTURAL_MODEL.default_geometry_model
        is GeometryModel.LINEAR
    )

    assert (
        BALL001_STRUCTURAL_MODEL.escalation_geometry_model
        is GeometryModel.NLGEOM
    )


def test_20_mpa_nominal_case_retains_linear_geometry() -> None:
    evidence = BALL001_STRUCTURAL_EVIDENCE

    assert not BALL001_STRUCTURAL_MODEL.requires_nlgeom(
        evidence.anchor_20mpa_displacement_change_percent,
        evidence.anchor_20mpa_stress_change_percent,
    )


def test_full_pressure_envelope_retains_linear_geometry() -> None:
    evidence = BALL001_STRUCTURAL_EVIDENCE

    assert not BALL001_STRUCTURAL_MODEL.requires_nlgeom(
        evidence.pressure_envelope_max_displacement_change_percent,
        evidence.pressure_envelope_max_stress_change_percent,
    )


def test_5_mpa_case_requires_nlgeom() -> None:
    evidence = BALL001_STRUCTURAL_EVIDENCE

    assert BALL001_STRUCTURAL_MODEL.requires_nlgeom(
        evidence.anchor_5mpa_displacement_change_percent,
        evidence.anchor_5mpa_stress_change_percent,
    )


def test_verification_mesh_must_be_finer() -> None:
    with pytest.raises(
        ValueError,
        match="finer",
    ):
        StructuralModelDecision(
            working_mesh_size_mm=8.0,
            verification_mesh_size_mm=12.0,
            default_formulation=ShellFormulation.S3,
            verification_formulation=ShellFormulation.S6,
            default_geometry_model=GeometryModel.LINEAR,
            escalation_geometry_model=GeometryModel.NLGEOM,
            displacement_sensitivity_target_percent=2.0,
            stress_sensitivity_target_percent=5.0,
        )


def test_exact_sensitivity_boundary_retains_linear_model() -> None:
    assert not BALL001_STRUCTURAL_MODEL.requires_nlgeom(
        2.0,
        5.0,
    )


def test_stress_alone_can_trigger_nlgeom() -> None:
    assert BALL001_STRUCTURAL_MODEL.requires_nlgeom(
        1.0,
        5.1,
    )