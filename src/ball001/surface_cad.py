from math import sin

import cadquery as cq

from ball001.cad import MM_PER_M, build_layer_solids, outer_radius_mm
from ball001.design import BallDesign
from ball001.surface import SeamSpec

BOOLEAN_OVERSHOOT_MM = 0.1


def seam_half_height_mm(
    design: BallDesign,
    seam: SeamSpec,
) -> float:
    radius_mm = outer_radius_mm(design)
    width_mm = seam.width_m * MM_PER_M

    half_angle_rad = (width_mm / 2.0) / radius_mm

    return radius_mm * sin(half_angle_rad)


def build_equatorial_groove_cutter(
    design: BallDesign,
    seam: SeamSpec,
) -> cq.Workplane:
    radius_mm = outer_radius_mm(design)
    depth_mm = seam.depth_m * MM_PER_M
    inner_radius_mm = radius_mm - depth_mm

    outer_cutter_sphere = cq.Workplane("XY").sphere(
        radius_mm + BOOLEAN_OVERSHOOT_MM
    )
    inner_cutter_sphere = cq.Workplane("XY").sphere(inner_radius_mm)

    shallow_shell = outer_cutter_sphere.cut(inner_cutter_sphere)

    half_height_mm = seam_half_height_mm(design, seam)

    band_box = cq.Workplane("XY").box(
        2.2 * radius_mm,
        2.2 * radius_mm,
        2.0 * half_height_mm,
    )

    return shallow_shell.intersect(band_box)


def build_grooved_skin(
    design: BallDesign,
    seam: SeamSpec,
) -> cq.Workplane:
    skin = build_layer_solids(design)[0].solid
    groove_cutter = build_equatorial_groove_cutter(design, seam)

    return skin.cut(groove_cutter)