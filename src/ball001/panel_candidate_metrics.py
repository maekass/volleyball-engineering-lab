from dataclasses import dataclass
from math import pi

from ball001.cad import outer_radius_mm
from ball001.design import BallDesign
from ball001.panel_candidate_cad import (
    GUIDE_OFFSET_MM,
    build_candidate_panel_guides,
)
from ball001.panel_candidates import (
    BALL001_PANEL_CANDIDATES,
    CandidatePanelArchitecture,
)

MM_PER_M = 1000.0


@dataclass(frozen=True)
class PanelCandidateMetrics:
    name: str
    region_count: int
    guide_count: int
    schematic_boundary_length_m: float
    sphere_surface_area_m2: float
    boundary_length_per_area_m_m2: float
    mean_shared_boundary_per_region_m: float
    mean_region_area_m2: float


def calculate_candidate_metrics(
    design: BallDesign,
    architecture: CandidatePanelArchitecture,
) -> PanelCandidateMetrics:
    radius_mm = outer_radius_mm(design)

    display_radius_mm = (
        radius_mm
        + GUIDE_OFFSET_MM
    )

    guides = build_candidate_panel_guides(
        design,
        architecture,
    )

    display_boundary_length_mm = sum(
        guide.Length()
        for guide in guides
    )

    # The CAD viewer places the guide curves slightly above
    # the ball to avoid visual overlap / flicker.
    #
    # Because the guide geometry is a radial scaling of the
    # nominal surface geometry, scale the displayed length
    # back to the actual BALL 001 radius before calculating
    # engineering metrics.
    nominal_radius_scale = (
        radius_mm
        / display_radius_mm
    )

    schematic_boundary_length_m = (
        display_boundary_length_mm
        * nominal_radius_scale
        / MM_PER_M
    )

    radius_m = (
        radius_mm
        / MM_PER_M
    )

    sphere_surface_area_m2 = (
        4.0
        * pi
        * radius_m**2
    )

    boundary_length_per_area_m_m2 = (
        schematic_boundary_length_m
        / sphere_surface_area_m2
    )

    mean_shared_boundary_per_region_m = (
        2.0
        * schematic_boundary_length_m
        / architecture.region_count
    )

    mean_region_area_m2 = (
        sphere_surface_area_m2
        / architecture.region_count
    )

    return PanelCandidateMetrics(
        name=architecture.name,
        region_count=architecture.region_count,
        guide_count=len(guides),
        schematic_boundary_length_m=(
            schematic_boundary_length_m
        ),
        sphere_surface_area_m2=(
            sphere_surface_area_m2
        ),
        boundary_length_per_area_m_m2=(
            boundary_length_per_area_m_m2
        ),
        mean_shared_boundary_per_region_m=(
            mean_shared_boundary_per_region_m
        ),
        mean_region_area_m2=(
            mean_region_area_m2
        ),
    )


def calculate_all_candidate_metrics(
    design: BallDesign,
) -> tuple[PanelCandidateMetrics, ...]:
    return tuple(
        calculate_candidate_metrics(
            design,
            architecture,
        )
        for architecture in BALL001_PANEL_CANDIDATES
    )