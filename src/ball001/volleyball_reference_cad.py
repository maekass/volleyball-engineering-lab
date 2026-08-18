from math import cos, radians, sin

import cadquery as cq

from ball001.cad import outer_radius_mm
from ball001.design import BallDesign

GUIDE_OFFSET_MM = 0.8

MERIDIAN_COUNT = 6
TRANSVERSE_BOUNDARY_POLAR_DEG = (
    60.0,
    120.0,
)

MERIDIAN_TWIST_DEG = 18.0
TRANSVERSE_WAVE_DEG = 6.0

MERIDIAN_SAMPLES = 61
RING_SAMPLES = 120

SCHEMATIC_REGION_COUNT = (
    MERIDIAN_COUNT
    * (len(TRANSVERSE_BOUNDARY_POLAR_DEG) + 1)
)


def spherical_point(
    radius_mm: float,
    polar_deg: float,
    azimuth_deg: float,
) -> cq.Vector:
    polar_rad = radians(polar_deg)
    azimuth_rad = radians(azimuth_deg)

    x_mm = (
        radius_mm
        * sin(polar_rad)
        * cos(azimuth_rad)
    )

    y_mm = (
        radius_mm
        * sin(polar_rad)
        * sin(azimuth_rad)
    )

    z_mm = radius_mm * cos(polar_rad)

    return cq.Vector(
        x_mm,
        y_mm,
        z_mm,
    )


def build_schematic_panel_guides(
    design: BallDesign,
) -> tuple[cq.Edge, ...]:
    display_radius_mm = (
        outer_radius_mm(design)
        + GUIDE_OFFSET_MM
    )

    guides = []

    azimuth_step_deg = 360.0 / MERIDIAN_COUNT

    for meridian_index in range(MERIDIAN_COUNT):
        base_azimuth_deg = (
            meridian_index
            * azimuth_step_deg
        )

        points = []

        for sample_index in range(MERIDIAN_SAMPLES):
            polar_deg = (
                180.0
                * sample_index
                / (MERIDIAN_SAMPLES - 1)
            )

            twist_deg = (
                MERIDIAN_TWIST_DEG
                * sin(radians(polar_deg))
            )

            azimuth_deg = (
                base_azimuth_deg
                + twist_deg
            )

            points.append(
                spherical_point(
                    display_radius_mm,
                    polar_deg,
                    azimuth_deg,
                )
            )

        guides.append(
            cq.Edge.makeSpline(points)
        )

    transverse_specs = (
        (
            TRANSVERSE_BOUNDARY_POLAR_DEG[0],
            0.0,
        ),
        (
            TRANSVERSE_BOUNDARY_POLAR_DEG[1],
            180.0,
        ),
    )

    for base_polar_deg, phase_deg in transverse_specs:
        points = []

        for sample_index in range(RING_SAMPLES):
            azimuth_deg = (
                360.0
                * sample_index
                / RING_SAMPLES
            )

            wave_angle_deg = (
                MERIDIAN_COUNT
                * azimuth_deg
                + phase_deg
            )

            local_polar_deg = (
                base_polar_deg
                + TRANSVERSE_WAVE_DEG
                * cos(radians(wave_angle_deg))
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