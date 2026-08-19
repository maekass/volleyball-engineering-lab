from dataclasses import dataclass

from ball001.design import (
    BallDesign,
    EvidenceClass,
)
from ball001.geometry import (
    radius_from_circumference,
)
from ball001.volleyball_benchmark import (
    FIVB_INDOOR_BALL,
)


@dataclass(frozen=True)
class PressureBaselineResult:
    design_name: str
    radius_m: float
    wall_thickness_m: float
    thickness_to_radius_ratio: float
    pressure_pa: float
    pressure_evidence: EvidenceClass
    wall_thickness_evidence: EvidenceClass
    membrane_force_per_length_n_m: float
    homogenized_membrane_stress_pa: float


def total_wall_thickness_m(
    design: BallDesign,
) -> float:
    thickness_m = sum(
        layer.thickness_m
        for layer in design.layers
    )

    if thickness_m <= 0.0:
        raise ValueError(
            "Total wall thickness must be positive."
        )

    return thickness_m


def nominal_fivb_pressure_pa() -> float:
    return 0.5 * (
        FIVB_INDOOR_BALL.internal_pressure_min_pa
        + FIVB_INDOOR_BALL.internal_pressure_max_pa
    )


def calculate_pressure_baseline(
    design: BallDesign,
    pressure_pa: float | None = None,
) -> PressureBaselineResult:
    if pressure_pa is None:
        pressure_pa = nominal_fivb_pressure_pa()

    if pressure_pa <= 0.0:
        raise ValueError(
            "Pressure differential must be positive."
        )

    radius_m = radius_from_circumference(
        design.circumference_m
    )

    wall_thickness_m = total_wall_thickness_m(
        design
    )

    thickness_to_radius_ratio = (
        wall_thickness_m
        / radius_m
    )

    membrane_force_per_length_n_m = (
        pressure_pa
        * radius_m
        / 2.0
    )

    homogenized_membrane_stress_pa = (
        membrane_force_per_length_n_m
        / wall_thickness_m
    )

    return PressureBaselineResult(
        design_name=design.name,
        radius_m=radius_m,
        wall_thickness_m=wall_thickness_m,
        thickness_to_radius_ratio=(
            thickness_to_radius_ratio
        ),
        pressure_pa=pressure_pa,
        pressure_evidence=(
            EvidenceClass.BENCHMARK
        ),
        wall_thickness_evidence=(
            EvidenceClass.PENDING
        ),
        membrane_force_per_length_n_m=(
            membrane_force_per_length_n_m
        ),
        homogenized_membrane_stress_pa=(
            homogenized_membrane_stress_pa
        ),
    )