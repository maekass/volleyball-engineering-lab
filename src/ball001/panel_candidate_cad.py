from math import acos, cos, degrees, radians, sin

import cadquery as cq

from ball001.cad import outer_radius_mm
from ball001.design import BallDesign
from ball001.panel_candidates import CandidatePanelArchitecture

GUIDE_OFFSET_MM = 0.8

MERIDIAN_TWIST_DEG = 18.0
TRANSVERSE_WAVE_DEG = 5.0

MERIDIAN_SAMPLES = 61
RING_SAMPLES = 120


def spherical_point(
    radius_mm: float,
    polar_deg: float,
    azimuth_deg: float,
) -> cq.Vector:
    polar_rad = radians(polar_deg)
    azimuth_rad = radians(azimuth_deg)

    return cq.Vector(
        radius_mm
        * sin(polar_rad)
        * cos(azimuth_rad),
        radius_mm
        * sin(polar_rad)
        * sin(azimuth_rad),
        radius_mm * cos(polar_rad),
    )


def equal_area_boundary_polar_degrees(
    zone_count: int,
) -> tuple[float, ...]:
    if zone_count < 2:
        return ()

    boundaries = []

    for boundary_index in range(1, zone_count):
        cosine_value = (
            1.0
            - 2.0 * boundary_index / zone_count
        )

        boundaries.append(
            degrees(
                acos(cosine_value)
            )
        )

    return tuple(boundaries)


def build_candidate_panel_guides(
    design: BallDesign,
    architecture: CandidatePanelArchitecture,
) -> tuple[cq.Edge, ...]:
    display_radius_mm = (
        outer_radius_mm(design)
        + GUIDE_OFFSET_MM
    )

    guides = []

    azimuth_step_deg = (
        360.0
        / architecture.meridian_count
    )

    for meridian_index in range(
        architecture.meridian_count
    ):
        base_azimuth_deg = (
            meridian_index
            * azimuth_step_deg
        )

        points = []

        for sample_index in range(
            MERIDIAN_SAMPLES
        ):
            polar_deg = (
                180.0
                * sample_index
                / (MERIDIAN_SAMPLES - 1)
            )

            twist_deg = (
                MERIDIAN_TWIST_DEG
                * sin(
                    radians(polar_deg)
                )
            )

            points.append(
                spherical_point(
                    display_radius_mm,
                    polar_deg,
                    (
                        base_azimuth_deg
                        + twist_deg
                    ),
                )
            )

        guides.append(
            cq.Edge.makeSpline(points)
        )

    boundary_polar_degrees = (
        equal_area_boundary_polar_degrees(
            architecture.zone_count
        )
    )

    for boundary_index, base_polar_deg in enumerate(
        boundary_polar_degrees
    ):
        points = []

        phase_deg = (
            180.0
            if boundary_index % 2
            else 0.0
        )

        for sample_index in range(
            RING_SAMPLES
        ):
            azimuth_deg = (
                360.0
                * sample_index
                / RING_SAMPLES
            )

            wave_angle_deg = (
                architecture.meridian_count
                * azimuth_deg
                + phase_deg
            )

            local_polar_deg = (
                base_polar_deg
                + TRANSVERSE_WAVE_DEG
                * cos(
                    radians(
                        wave_angle_deg
                    )
                )
            )

            points.append(
                spherical_point(
                    display_radius_mm,
                    local_polar_deg,
                    azimuth_deg,
                )
            )

        guides.append(
            cq.Edge.makeSpline(
                points,
                periodic=True,
            )
        )

    return tuple(guides)