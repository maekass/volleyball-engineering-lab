import cadquery as cq
from cadquery.vis import show

from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM
from ball001.topology import (
    TOPOLOGY_1_SEAM,
    TOPOLOGY_2_SEAM,
    TOPOLOGY_3_SEAM,
)
from ball001.topology_cad import build_topology_grooved_skin

DISPLAY_SPACING_MM = 240.0


def main() -> None:
    assembly = cq.Assembly(
        name="BALL_001_topology_comparison",
    )

    topologies = (
        (
            TOPOLOGY_1_SEAM,
            "one_seam",
            cq.Color(0.75, 0.25, 0.20),
            0.0,
        ),
        (
            TOPOLOGY_2_SEAM,
            "two_seams",
            cq.Color(0.85, 0.60, 0.20),
            DISPLAY_SPACING_MM,
        ),
        (
            TOPOLOGY_3_SEAM,
            "three_seams",
            cq.Color(0.35, 0.40, 0.70),
            2.0 * DISPLAY_SPACING_MM,
        ),
    )

    for topology, name, color, offset_mm in topologies:
        grooved_skin = build_topology_grooved_skin(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )

        assembly.add(
            grooved_skin,
            name=name,
            color=color,
            loc=cq.Location(
                (
                    offset_mm,
                    0.0,
                    0.0,
                )
            ),
        )

    show(
        assembly,
        title="BALL 001 — Seam Topology Comparison",
        edges=False,
    )


if __name__ == "__main__":
    main()