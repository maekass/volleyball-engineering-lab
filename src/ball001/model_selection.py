from dataclasses import dataclass
from enum import Enum

from ball001.nonlinear_stiffness_results import (
    NonlinearDivergenceResult,
)


class RecommendedGeometryModel(str, Enum):
    LINEAR = "linear"
    NLGEOM = "nlgeom"


@dataclass(frozen=True)
class ModelSelectionCriteria:
    max_displacement_difference_percent: float = 2.0
    max_stress_difference_percent: float = 5.0

    def __post_init__(self) -> None:
        if (
            self.max_displacement_difference_percent
            <= 0.0
        ):
            raise ValueError(
                "Displacement-difference target "
                "must be positive."
            )

        if (
            self.max_stress_difference_percent
            <= 0.0
        ):
            raise ValueError(
                "Stress-difference target "
                "must be positive."
            )


@dataclass(frozen=True)
class ModelSelectionAssessment:
    youngs_modulus_mpa: float

    displacement_difference_percent: float
    stress_difference_percent: float

    displacement_within_target: bool
    stress_within_target: bool

    recommendation: RecommendedGeometryModel

    @property
    def linear_model_accepted(
        self,
    ) -> bool:
        return (
            self.recommendation
            is RecommendedGeometryModel.LINEAR
        )


BALL001_MODEL_SELECTION_TARGET = (
    ModelSelectionCriteria(
        max_displacement_difference_percent=2.0,
        max_stress_difference_percent=5.0,
    )
)


def assess_geometry_model(
    divergence: NonlinearDivergenceResult,
    criteria: ModelSelectionCriteria = (
        BALL001_MODEL_SELECTION_TARGET
    ),
) -> ModelSelectionAssessment:
    displacement_within_target = (
        abs(
            divergence.displacement_difference_percent
        )
        <= criteria.max_displacement_difference_percent
    )

    stress_within_target = (
        abs(
            divergence.stress_difference_percent
        )
        <= criteria.max_stress_difference_percent
    )

    if (
        displacement_within_target
        and stress_within_target
    ):
        recommendation = (
            RecommendedGeometryModel.LINEAR
        )

    else:
        recommendation = (
            RecommendedGeometryModel.NLGEOM
        )

    return ModelSelectionAssessment(
        youngs_modulus_mpa=(
            divergence.youngs_modulus_mpa
        ),
        displacement_difference_percent=(
            divergence.displacement_difference_percent
        ),
        stress_difference_percent=(
            divergence.stress_difference_percent
        ),
        displacement_within_target=(
            displacement_within_target
        ),
        stress_within_target=(
            stress_within_target
        ),
        recommendation=recommendation,
    )