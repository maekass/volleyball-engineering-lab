from dataclasses import dataclass

from ball001.calculix_results import (
    CalculixVerificationResult,
)
from ball001.formulation_comparison import (
    relative_change_percent,
)


@dataclass(frozen=True)
class GeometricNonlinearityComparison:
    linear_radial_displacement_mm: float
    nonlinear_radial_displacement_mm: float
    displacement_change_percent: float

    linear_displacement_error_percent: float
    nonlinear_displacement_error_percent: float

    linear_tangential_stress_n_mm2: float
    nonlinear_tangential_stress_n_mm2: float
    stress_change_percent: float

    linear_stress_error_percent: float
    nonlinear_stress_error_percent: float

    linear_outward_node_fraction: float
    nonlinear_outward_node_fraction: float

    linear_max_tangential_displacement_mm: float
    nonlinear_max_tangential_displacement_mm: float


def compare_geometric_nonlinearity(
    linear: CalculixVerificationResult,
    nonlinear: CalculixVerificationResult,
) -> GeometricNonlinearityComparison:
    return GeometricNonlinearityComparison(
        linear_radial_displacement_mm=(
            linear.mean_radial_displacement_mm
        ),
        nonlinear_radial_displacement_mm=(
            nonlinear.mean_radial_displacement_mm
        ),
        displacement_change_percent=(
            relative_change_percent(
                nonlinear.mean_radial_displacement_mm,
                linear.mean_radial_displacement_mm,
            )
        ),
        linear_displacement_error_percent=(
            linear.displacement_error_percent
        ),
        nonlinear_displacement_error_percent=(
            nonlinear.displacement_error_percent
        ),
        linear_tangential_stress_n_mm2=(
            linear.mean_tangential_stress_n_mm2
        ),
        nonlinear_tangential_stress_n_mm2=(
            nonlinear.mean_tangential_stress_n_mm2
        ),
        stress_change_percent=(
            relative_change_percent(
                nonlinear.mean_tangential_stress_n_mm2,
                linear.mean_tangential_stress_n_mm2,
            )
        ),
        linear_stress_error_percent=(
            linear.stress_error_percent
        ),
        nonlinear_stress_error_percent=(
            nonlinear.stress_error_percent
        ),
        linear_outward_node_fraction=(
            linear.outward_node_fraction
        ),
        nonlinear_outward_node_fraction=(
            nonlinear.outward_node_fraction
        ),
        linear_max_tangential_displacement_mm=(
            linear.max_tangential_displacement_mm
        ),
        nonlinear_max_tangential_displacement_mm=(
            nonlinear.max_tangential_displacement_mm
        ),
    )