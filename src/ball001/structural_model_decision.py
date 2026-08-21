from dataclasses import dataclass
from enum import Enum


class GeometryModel(str, Enum):
    LINEAR = "linear"
    NLGEOM = "nlgeom"


class ShellFormulation(str, Enum):
    S3 = "S3"
    S6 = "S6"


@dataclass(frozen=True)
class StructuralModelDecision:
    working_mesh_size_mm: float
    verification_mesh_size_mm: float

    default_formulation: ShellFormulation
    verification_formulation: ShellFormulation

    default_geometry_model: GeometryModel
    escalation_geometry_model: GeometryModel

    displacement_sensitivity_target_percent: float
    stress_sensitivity_target_percent: float

    def __post_init__(self) -> None:
        if self.working_mesh_size_mm <= 0.0:
            raise ValueError(
                "Working mesh size must be positive."
            )

        if self.verification_mesh_size_mm <= 0.0:
            raise ValueError(
                "Verification mesh size must be positive."
            )

        if (
            self.verification_mesh_size_mm
            >= self.working_mesh_size_mm
        ):
            raise ValueError(
                "Verification mesh must be finer "
                "than the working mesh."
            )

        if (
            self.displacement_sensitivity_target_percent
            <= 0.0
        ):
            raise ValueError(
                "Displacement sensitivity target "
                "must be positive."
            )

        if (
            self.stress_sensitivity_target_percent
            <= 0.0
        ):
            raise ValueError(
                "Stress sensitivity target "
                "must be positive."
            )

    def requires_nlgeom(
        self,
        displacement_difference_percent: float,
        stress_difference_percent: float,
    ) -> bool:
        return (
            abs(displacement_difference_percent)
            > self.displacement_sensitivity_target_percent
            or abs(stress_difference_percent)
            > self.stress_sensitivity_target_percent
        )


@dataclass(frozen=True)
class StructuralVerificationEvidence:
    medium_to_fine_displacement_change_percent: float
    medium_to_fine_stress_change_percent: float

    s3_to_s6_displacement_change_percent: float
    s3_to_s6_stress_change_percent: float

    stiff_nlgeom_displacement_change_percent: float
    stiff_nlgeom_stress_change_percent: float

    anchor_20mpa_displacement_change_percent: float
    anchor_20mpa_stress_change_percent: float

    anchor_5mpa_displacement_change_percent: float
    anchor_5mpa_stress_change_percent: float

    pressure_envelope_max_displacement_change_percent: float
    pressure_envelope_max_stress_change_percent: float


BALL001_STRUCTURAL_MODEL = StructuralModelDecision(
    working_mesh_size_mm=8.0,
    verification_mesh_size_mm=5.0,
    default_formulation=ShellFormulation.S3,
    verification_formulation=ShellFormulation.S6,
    default_geometry_model=GeometryModel.LINEAR,
    escalation_geometry_model=GeometryModel.NLGEOM,
    displacement_sensitivity_target_percent=2.0,
    stress_sensitivity_target_percent=5.0,
)


BALL001_STRUCTURAL_EVIDENCE = StructuralVerificationEvidence(
    medium_to_fine_displacement_change_percent=0.008,
    medium_to_fine_stress_change_percent=0.060,
    s3_to_s6_displacement_change_percent=0.043,
    s3_to_s6_stress_change_percent=0.112,
    stiff_nlgeom_displacement_change_percent=0.024,
    stiff_nlgeom_stress_change_percent=0.081,
    anchor_20mpa_displacement_change_percent=1.14,
    anchor_20mpa_stress_change_percent=4.40,
    anchor_5mpa_displacement_change_percent=4.64,
    anchor_5mpa_stress_change_percent=20.53,
    pressure_envelope_max_displacement_change_percent=1.19,
    pressure_envelope_max_stress_change_percent=4.58,
)