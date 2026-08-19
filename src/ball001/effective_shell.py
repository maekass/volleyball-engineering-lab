from dataclasses import dataclass

from ball001.design import (
    BallDesign,
    EvidenceClass,
)
from ball001.geometry import radius_from_circumference
from ball001.pressure import (
    PressureLoadCase,
    spherical_membrane_resultant_n_per_m,
)


@dataclass(frozen=True)
class EffectiveShellMaterial:
    name: str
    youngs_modulus_pa: float
    poisson_ratio: float
    evidence: EvidenceClass
    note: str


@dataclass(frozen=True)
class EffectiveShellVerificationResult:
    load_case_name: str
    pressure_pa: float
    wall_thickness_m: float
    membrane_resultant_n_per_m: float
    membrane_stress_pa: float
    membrane_strain: float
    radial_expansion_m: float


BALL001_VERIFICATION_MATERIAL = EffectiveShellMaterial(
    name="BALL 001 numerical verification shell",
    youngs_modulus_pa=1_000_000_000.0,
    poisson_ratio=0.30,
    evidence=EvidenceClass.PENDING,
    note=(
        "Artificial isotropic material used only for solver "
        "verification. It is not a measured, benchmark, or "
        "claimed volleyball material property."
    ),
)


def total_wall_thickness_m(
    design: BallDesign,
) -> float:
    return sum(
        layer.thickness_m
        for layer in design.layers
    )


def validate_effective_material(
    material: EffectiveShellMaterial,
) -> None:
    if material.youngs_modulus_pa <= 0.0:
        raise ValueError(
            "Young's modulus must be positive."
        )

    if not (
        -1.0
        < material.poisson_ratio
        < 0.5
    ):
        raise ValueError(
            "Poisson ratio must lie between -1 and 0.5."
        )


def calculate_effective_shell_verification(
    design: BallDesign,
    load_case: PressureLoadCase,
    material: EffectiveShellMaterial,
) -> EffectiveShellVerificationResult:
    validate_effective_material(
        material
    )

    wall_thickness_m = (
        total_wall_thickness_m(
            design
        )
    )

    if wall_thickness_m <= 0.0:
        raise ValueError(
            "Wall thickness must be positive."
        )

    radius_m = (
        radius_from_circumference(
            design.circumference_m
        )
    )

    membrane_resultant_n_per_m = (
        spherical_membrane_resultant_n_per_m(
            design,
            load_case.pressure_pa,
        )
    )

    membrane_stress_pa = (
        membrane_resultant_n_per_m
        / wall_thickness_m
    )

    membrane_strain = (
        membrane_stress_pa
        / material.youngs_modulus_pa
        * (
            1.0
            - material.poisson_ratio
        )
    )

    radial_expansion_m = (
        radius_m
        * membrane_strain
    )

    return EffectiveShellVerificationResult(
        load_case_name=load_case.name,
        pressure_pa=load_case.pressure_pa,
        wall_thickness_m=(
            wall_thickness_m
        ),
        membrane_resultant_n_per_m=(
            membrane_resultant_n_per_m
        ),
        membrane_stress_pa=(
            membrane_stress_pa
        ),
        membrane_strain=(
            membrane_strain
        ),
        radial_expansion_m=(
            radial_expansion_m
        ),
    )