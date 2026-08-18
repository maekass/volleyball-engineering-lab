import cadquery as cq
from cadquery.vis import show

from ball001.cad import outer_radius_mm
from ball001.design import BALL_001
from ball001.panel_candidate_cad import (
    build_candidate_panel_guides,
)
from ball001.panel_candidates import (
    BALL001_PANEL_CANDIDATES,
)

DISPLAY_SPACING_MM = 260.0


def main() -> None:
    assembly = cq.Assembly(
        name="BALL_001_panel_candidates"
    )

    candidate_count = len(
        BALL001_PANEL_CANDIDATES
    )

    for candidate_index, candidate in enumerate(
        BALL001_PANEL_CANDIDATES
    ):
        x_offset_mm = (
            candidate_index
            - (candidate_count - 1) / 2.0
        ) * DISPLAY_SPACING_MM

        location = cq.Location(
            cq.Vector(
                x_offset_mm,
                0.0,
                0.0,
            )
        )

        sphere = (
            cq.Workplane("XY")
            .sphere(
                outer_radius_mm(
                    BALL_001
                )
            )
        )

        assembly.add(
            sphere,
            name=(
                f"surface_"
                f"{candidate.region_count}"
            ),
            loc=location,
            color=cq.Color(
                0.88,
                0.85,
                0.78,
            ),
        )

        guides = (
            build_candidate_panel_guides(
                BALL_001,
                candidate,
            )
        )

        for guide_index, guide in enumerate(
            guides,
            start=1,
        ):
            assembly.add(
                guide,
                name=(
                    f"candidate_"
                    f"{candidate.region_count}_"
                    f"guide_"
                    f"{guide_index:02d}"
                ),
                loc=location,
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
            "8 / 12 / 18 Region Candidates"
        ),
    )


if __name__ == "__main__":
    main()