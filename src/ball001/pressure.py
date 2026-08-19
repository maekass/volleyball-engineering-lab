from dataclasses import dataclass
from math import pi

from ball001.design import BallDesign, EvidenceClass
from ball001.geometry import radius_from_circumference
from ball001.volleyball_benchmark import FIVB_INDOOR_BALL


@dataclass(frozen=True)
class PressureLoadCase:
    name: str
    pressure_pa: float
    evidence: EvidenceClass
    note: str


@dataclass(frozen=True)
class PressureBenchmarkResult:
    name: str
    pressure_pa: float
    membrane_resultant_n_per_m: float
    hemisphere_pressure_resultant_n: float
    great_circle_membrane_balance_n: float


FIVB_MIN_PRESSURE = PressureLoadCase(
    name="FIVB minimum",
    pressure_pa=FIVB_INDOOR_BALL.internal_pressure_min_pa,
    evidence=EvidenceClass.BENCHMARK,
    note="Lower bound of the indoor-volleyball benchmark range.",
)


BALL001_NOMINAL_PRESSURE = PressureLoadCase(
    name="BALL 001 nominal",
    pressure_pa=(
        FIVB_INDOOR_BALL.internal_pressure_min_pa
        + FIVB_INDOOR_BALL.internal_pressure_max_pa
    )
    / 2.0,
    evidence=EvidenceClass.TARGET,
    note=(
        "Computational nominal pressure selected as the midpoint "
        "of the benchmark range."
    ),
)


FIVB_MAX_PRESSURE = PressureLoadCase(
    name="FIVB maximum",
    pressure_pa=FIVB_INDOOR_BALL.internal_pressure_max_pa,
    evidence=EvidenceClass.BENCHMARK,
    note="Upper bound of the indoor-volleyball benchmark range.",
)


BALL001_PRESSURE_CASES = (
    FIVB_MIN_PRESSURE,
    BALL001_NOMINAL_PRESSURE,
    FIVB_MAX_PRESSURE,
)


def spherical_membrane_resultant_n_per_m(
    design: BallDesign,
    pressure_pa: float,
) -> float:
    if pressure_pa <= 0.0:
        raise ValueError(
            "Internal pressure must be positive."
        )

    radius_m = radius_from_circumference(
        design.circumference_m
    )

    return pressure_pa * radius_m / 2.0


def calculate_pressure_benchmark(
    design: BallDesign,
    load_case: PressureLoadCase,
) -> PressureBenchmarkResult:
    radius_m = radius_from_circumference(
        design.circumference_m
    )

    membrane_resultant_n_per_m = (
        spherical_membrane_resultant_n_per_m(
            design,
            load_case.pressure_pa,
        )
    )

    hemisphere_pressure_resultant_n = (
        load_case.pressure_pa
        * pi
        * radius_m**2
    )

    great_circle_membrane_balance_n = (
        2.0
        * pi
        * radius_m
        * membrane_resultant_n_per_m
    )

    return PressureBenchmarkResult(
        name=load_case.name,
        pressure_pa=load_case.pressure_pa,
        membrane_resultant_n_per_m=(
            membrane_resultant_n_per_m
        ),
        hemisphere_pressure_resultant_n=(
            hemisphere_pressure_resultant_n
        ),
        great_circle_membrane_balance_n=(
            great_circle_membrane_balance_n
        ),
    )