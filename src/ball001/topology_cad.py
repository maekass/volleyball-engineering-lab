import cadquery as cq

from ball001.cad import MM_PER_M, build_layer_solids, outer_radius_mm
from ball001.design import BallDesign
from ball001.surface import SeamSpec
from ball001.surface_cad import BOOLEAN_OVERSHOOT_MM, seam_half_height_mm
from ball001.topology import SeamTopology


def _single_solid(
    shape: cq.Shape,
    label: str,
) -> cq.Solid:
    solids = shape.Solids()

    if len(solids) != 1:
        raise ValueError(
            f"{label} must contain exactly one solid; "
            f"found {len(solids)}."
        )

    return solids[0]


def _seam_axis(
    rotation_x_deg: float,
    rotation_y_deg: float,
) -> str:
    orientation = (
        round(rotation_x_deg, 6),
        round(rotation_y_deg, 6),
    )

    if orientation == (0.0, 0.0):
        return "z"

    if orientation == (90.0, 0.0):
        return "y"

    if orientation == (0.0, 90.0):
        return "x"

    raise ValueError(
        "Current topology CAD supports only the three "
        "orthogonal great-circle orientations."
    )


def build_axis_aligned_groove_cutter(
    design: BallDesign,
    seam: SeamSpec,
    axis: str,
) -> cq.Solid:
    radius_mm = outer_radius_mm(design)
    depth_mm = seam.depth_m * MM_PER_M
    inner_radius_mm = radius_mm - depth_mm

    outer_sphere = cq.Workplane("XY").sphere(
        radius_mm + BOOLEAN_OVERSHOOT_MM
    )

    inner_sphere = cq.Workplane("XY").sphere(
        inner_radius_mm
    )

    shallow_shell = outer_sphere.cut(inner_sphere)

    half_height_mm = seam_half_height_mm(
        design,
        seam,
    )

    extent_mm = 2.2 * radius_mm
    band_thickness_mm = 2.0 * half_height_mm

    if axis == "x":
        band_box = cq.Workplane("XY").box(
            band_thickness_mm,
            extent_mm,
            extent_mm,
        )

    elif axis == "y":
        band_box = cq.Workplane("XY").box(
            extent_mm,
            band_thickness_mm,
            extent_mm,
        )

    elif axis == "z":
        band_box = cq.Workplane("XY").box(
            extent_mm,
            extent_mm,
            band_thickness_mm,
        )

    else:
        raise ValueError(
            f"Unsupported seam axis: {axis}"
        )

    cutter = shallow_shell.intersect(
        band_box
    )

    return _single_solid(
        cutter.val(),
        f"{axis}-axis groove cutter",
    )


def build_topology_grooved_skin(
    design: BallDesign,
    seam: SeamSpec,
    topology: SeamTopology,
) -> cq.Workplane:
    if not topology.seams:
        raise ValueError(
            "Topology must contain at least one seam."
        )

    skin = _single_solid(
        build_layer_solids(design)[0].solid.val(),
        "Skin",
    )

    cutters = []

    for topology_seam in topology.seams:
        axis = _seam_axis(
            topology_seam.rotation_x_deg,
            topology_seam.rotation_y_deg,
        )

        cutter = build_axis_aligned_groove_cutter(
            design,
            seam,
            axis,
        )

        cutters.append(cutter)

    cut_result = skin.cut(*cutters)

    grooved_skin = _single_solid(
        cut_result,
        "Topology-grooved skin",
    )

    return cq.Workplane(
        "XY",
        obj=grooved_skin,
    )