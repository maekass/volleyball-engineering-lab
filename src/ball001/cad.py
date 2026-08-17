from dataclasses import dataclass

import cadquery as cq

from ball001.design import BallDesign
from ball001.geometry import radius_from_circumference

MM_PER_M = 1000.0


@dataclass(frozen=True)
class CadLayer:
    name: str
    outer_radius_mm: float
    inner_radius_mm: float
    solid: cq.Workplane


def outer_radius_mm(design: BallDesign) -> float:
    radius_m = radius_from_circumference(design.circumference_m)
    return radius_m * MM_PER_M


def build_outer_sphere(design: BallDesign) -> cq.Workplane:
    radius_mm = outer_radius_mm(design)

    return cq.Workplane("XY").sphere(radius_mm)


def build_layer_solids(
    design: BallDesign,
) -> tuple[CadLayer, ...]:
    current_outer_radius_mm = outer_radius_mm(design)

    layers = []

    for layer in design.layers:
        thickness_mm = layer.thickness_m * MM_PER_M
        current_inner_radius_mm = current_outer_radius_mm - thickness_mm

        outer_sphere = cq.Workplane("XY").sphere(current_outer_radius_mm)
        inner_sphere = cq.Workplane("XY").sphere(current_inner_radius_mm)

        shell = outer_sphere.cut(inner_sphere)

        layers.append(
            CadLayer(
                name=layer.name,
                outer_radius_mm=current_outer_radius_mm,
                inner_radius_mm=current_inner_radius_mm,
                solid=shell,
            )
        )

        current_outer_radius_mm = current_inner_radius_mm

    return tuple(layers)

def build_half_section_layers(
    design: BallDesign,
) -> tuple[CadLayer, ...]:
    full_layers = build_layer_solids(design)
    radius_mm = outer_radius_mm(design)

    section_box = (
        cq.Workplane("XY")
        .box(
            radius_mm,
            2.2 * radius_mm,
            2.2 * radius_mm,
            centered=(False, True, True),
        )
    )

    section_layers = []

    for layer in full_layers:
        section_solid = layer.solid.intersect(section_box)

        section_layers.append(
            CadLayer(
                name=layer.name,
                outer_radius_mm=layer.outer_radius_mm,
                inner_radius_mm=layer.inner_radius_mm,
                solid=section_solid,
            )
        )

    return tuple(section_layers)