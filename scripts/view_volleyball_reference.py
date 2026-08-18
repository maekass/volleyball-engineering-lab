import cadquery as cq
from cadquery.vis import show

from ball001.cad import outer_radius_mm
from ball001.design import BALL_001
from ball001.volleyball_reference_cad import (
    build_schematic_panel_guides,
)


def main() -> None:
    assembly = cq.Assembly(
        name="BALL_001_volleyball_reference"
    )

    sphere = cq.Workplane("XY").sphere(
        outer_radius_mm(BALL_001)
    )

    assembly.add(
        sphere,
        name="volleyball_reference_surface",
        color=cq.Color(
            0.88,
            0.85,
            0.78,
        ),
    )

    guides = build_schematic_panel_guides(
        BALL_001
    )

    for index, guide in enumerate(
        guides,
        start=1,
    ):
        assembly.add(
            guide,
            name=f"panel_guide_{index:02d}",
            color=cq.Color(
                0.25,
                0.15,
                0.12,
            ),
        )

    show(
        assembly,
        title=(
            "BALL 001 — "
            "Schematic 18-Region Volleyball Reference"
        ),
    )


if __name__ == "__main__":
    main()