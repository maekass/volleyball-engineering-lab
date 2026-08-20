import pytest

from ball001.calculix_deck import SolverNode
from ball001.calculix_results import FrdStress
from ball001.nonlinear_stiffness_results import (
    StiffnessCaseMechanics,
    compare_linear_and_nlgeom,
    mean_tangential_stress_n_mm2,
    radial_displacement_mm,
    tangential_displacement_mm,
    unit_radial_vector,
)
from ball001.nonlinear_stiffness_sweep import (
    GeometryMode,
    StiffnessSweepCase,
)


def _case(
    geometry_mode: GeometryMode,
    modulus_mpa: float = 20.0,
) -> StiffnessSweepCase:
    return StiffnessSweepCase(
        label="test",
        youngs_modulus_mpa=(
            modulus_mpa
        ),
        poisson_ratio=0.35,
        geometry_mode=(
            geometry_mode
        ),
    )


def _mechanics(
    geometry_mode: GeometryMode,
    radial_displacement_mm_value: float,
    tangential_stress_n_mm2: float,
    modulus_mpa: float = 20.0,
) -> StiffnessCaseMechanics:
    return StiffnessCaseMechanics(
        case=_case(
            geometry_mode,
            modulus_mpa,
        ),
        displacement_node_count=100,
        stress_node_count=100,
        mean_radial_displacement_mm=(
            radial_displacement_mm_value
        ),
        max_radial_displacement_mm=(
            radial_displacement_mm_value
        ),
        outward_node_fraction=1.0,
        max_tangential_displacement_mm=0.001,
        mean_tangential_stress_n_mm2=(
            tangential_stress_n_mm2
        ),
        mean_mesh_radius_mm=100.0,
        radial_expansion_percent=(
            radial_displacement_mm_value
        ),
    )


def test_unit_radial_vector_on_x_axis() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    assert unit_radial_vector(
        node
    ) == pytest.approx(
        (
            1.0,
            0.0,
            0.0,
        )
    )


def test_radial_displacement_on_x_axis() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    result = radial_displacement_mm(
        node,
        (
            2.0,
            0.0,
            0.0,
        ),
    )

    assert result == pytest.approx(
        2.0
    )


def test_tangential_displacement_on_x_axis() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    result = tangential_displacement_mm(
        node,
        (
            2.0,
            3.0,
            4.0,
        ),
    )

    assert result == pytest.approx(
        5.0
    )


def test_mean_tangential_stress() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    stress = FrdStress(
        sxx_n_mm2=0.0,
        syy_n_mm2=2.0,
        szz_n_mm2=2.0,
        sxy_n_mm2=0.0,
        syz_n_mm2=0.0,
        szx_n_mm2=0.0,
    )

    result = (
        mean_tangential_stress_n_mm2(
            node,
            stress,
        )
    )

    assert result == pytest.approx(
        2.0
    )


def test_comparison_calculates_divergence() -> None:
    linear = _mechanics(
        GeometryMode.LINEAR,
        radial_displacement_mm_value=2.0,
        tangential_stress_n_mm2=0.60,
    )

    nonlinear = _mechanics(
        GeometryMode.NLGEOM,
        radial_displacement_mm_value=2.2,
        tangential_stress_n_mm2=0.63,
    )

    result = compare_linear_and_nlgeom(
        linear,
        nonlinear,
    )

    assert (
        result.displacement_difference_percent
        == pytest.approx(
            10.0
        )
    )

    assert (
        result.stress_difference_percent
        == pytest.approx(
            5.0
        )
    )


def test_comparison_rejects_different_moduli() -> None:
    linear = _mechanics(
        GeometryMode.LINEAR,
        radial_displacement_mm_value=2.0,
        tangential_stress_n_mm2=0.60,
        modulus_mpa=20.0,
    )

    nonlinear = _mechanics(
        GeometryMode.NLGEOM,
        radial_displacement_mm_value=2.2,
        tangential_stress_n_mm2=0.63,
        modulus_mpa=5.0,
    )

    with pytest.raises(
        ValueError,
        match="same Young",
    ):
        compare_linear_and_nlgeom(
            linear,
            nonlinear,
        )