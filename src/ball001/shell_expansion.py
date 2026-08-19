from dataclasses import dataclass

from ball001.design import (
    BallDesign,
    EvidenceClass,
)
from ball001.pressure_baseline import (
    calculate_pressure_baseline,
)


@dataclass(frozen=True)
class EffectiveShellMaterial:
    name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    evidence: EvidenceClass
    note: str


@dataclass(frozen=True)
class ShellExpansionResult:
    material_name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    membrane_stress_pa: float
    biaxial_strain: float
    radial_displacement_m: float
    circumference_change_m: float
    material_evidence: EvidenceClass


SHELL_STIFFNESS_CASES = (
    EffectiveShellMaterial(
        name="low_stiffness",
        youngs_modulus_pa=5_000_000.0,
        poisson_ratio=0.35,
        evidence=EvidenceClass.PENDING,
        note=(
            "Computational sensitivity anchor only; "
            "not a measured volleyball modulus."
        ),
    ),
    EffectiveShellMaterial(
        name="mid_stiffness",
        youngs_modulus_pa=20_000_000.0,
        poisson_ratio=0.35,
        evidence=EvidenceClass.PENDING,
        note=(
            "Computational sensitivity anchor only; "
            "not a measured volleyball modulus."
        ),
    ),
    EffectiveShellMaterial(
        name="high_stiffness",
        youngs_modulus_pa=100_000_000.0,
        poisson_ratio=0.35,
        evidence=EvidenceClass.PENDING,
        note=(
            "Computational sensitivity anchor only; "
            "not a measured volleyball modulus."
        ),
    ),
)


def validate_material(
    material: EffectiveShellMaterial,
) -> None:
    if material.youngs_modulus_pa <= 0.0:
        raise ValueError(
            "Young's modulus must be positive."
        )

    if not -1.0 < material.poisson_ratio < 0.5:
        raise ValueError(
            "Poisson ratio must lie between -1 and 0.5."
        )


def calculate_shell_expansion(
    design: BallDesign,
    material: EffectiveShellMaterial,
    pressure_pa: float | None = None,
) -> ShellExpansionResult:
    validate_material(material)

    baseline = calculate_pressure_baseline(
        design,
        pressure_pa=pressure_pa,
    )

    biaxial_strain = (
        baseline.homogenized_membrane_stress_pa
        * (1.0 - material.poisson_ratio)
        / material.youngs_modulus_pa
    )

    radial_displacement_m = (
        baseline.radius_m
        * biaxial_strain
    )

    circumference_change_m = (
        design.circumference_m
        * biaxial_strain
    )

    return ShellExpansionResult(
        material_name=material.name,
        youngs_modulus_pa=(
            material.youngs_modulus_pa
        ),
        poisson_ratio=material.poisson_ratio,
        membrane_stress_pa=(
            baseline.homogenized_membrane_stress_pa
        ),
        biaxial_strain=biaxial_strain,
        radial_displacement_m=(
            radial_displacement_m
        ),
        circumference_change_m=(
            circumference_change_m
        ),
        material_evidence=material.evidence,
    )


def calculate_stiffness_sensitivity(
    design: BallDesign,
) -> tuple[ShellExpansionResult, ...]:
    return tuple(
        calculate_shell_expansion(
            design,
            material,
        )
        for material in SHELL_STIFFNESS_CASES
    )