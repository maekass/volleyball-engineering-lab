from dataclasses import dataclass

from ball001.calculix_results import (
    CalculixVerificationResult,
)


@dataclass(frozen=True)
class FormulationComparisonResult:
    s3_radial_displacement_mm: float
    s6_radial_displacement_mm: float

    s3_displacement_error_percent: float
    s6_displacement_error_percent: float

    displacement_change_percent: float

    s3_tangential_stress_n_mm2: float
    s6_tangential_stress_n_mm2: float

    s3_stress_error_percent: float
    s6_stress_error_percent: float

    stress_change_percent: float

    s3_outward_node_fraction: float
    s6_outward_node_fraction: float

    s3_max_tangential_displacement_mm: float
    s6_max_tangential_displacement_mm: float


def relative_change_percent(
    new_value: float,
    reference_value: float,
) -> float:
    if reference_value == 0.0:
        raise ValueError(
            "Reference value must be nonzero."
        )

    return (
        abs(
            new_value
            - reference_value
        )
        / abs(reference_value)
        * 100.0
    )


def compare_shell_formulations(
    s3: CalculixVerificationResult,
    s6: CalculixVerificationResult,
) -> FormulationComparisonResult:
    return FormulationComparisonResult(
        s3_radial_displacement_mm=(
            s3.mean_radial_displacement_mm
        ),
        s6_radial_displacement_mm=(
            s6.mean_radial_displacement_mm
        ),
        s3_displacement_error_percent=(
            s3.displacement_error_percent
        ),
        s6_displacement_error_percent=(
            s6.displacement_error_percent
        ),
        displacement_change_percent=(
            relative_change_percent(
                s6.mean_radial_displacement_mm,
                s3.mean_radial_displacement_mm,
            )
        ),
        s3_tangential_stress_n_mm2=(
            s3.mean_tangential_stress_n_mm2
        ),
        s6_tangential_stress_n_mm2=(
            s6.mean_tangential_stress_n_mm2
        ),
        s3_stress_error_percent=(
            s3.stress_error_percent
        ),
        s6_stress_error_percent=(
            s6.stress_error_percent
        ),
        stress_change_percent=(
            relative_change_percent(
                s6.mean_tangential_stress_n_mm2,
                s3.mean_tangential_stress_n_mm2,
            )
        ),
        s3_outward_node_fraction=(
            s3.outward_node_fraction
        ),
        s6_outward_node_fraction=(
            s6.outward_node_fraction
        ),
        s3_max_tangential_displacement_mm=(
            s3.max_tangential_displacement_mm
        ),
        s6_max_tangential_displacement_mm=(
            s6.max_tangential_displacement_mm
        ),
    )