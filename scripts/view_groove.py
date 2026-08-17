import cadquery as cq
from cadquery.vis import show

from ball001.cad import build_layer_solids
from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM
from ball001.surface_cad import build_grooved_skin

DISPLAY_OFFSET_MM = 240.0


def main() -> None:
    assembly = cq.Assembly(name="BALL_001_groove_comparison")

    smooth_skin = build_layer_solids(BALL_001)[0].solid
    grooved_skin = build_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
    )

    assembly.add(
        smooth_skin,
        name="smooth_skin",
        color=cq.Color(0.80, 0.75, 0.68),
    )

    assembly.add(
        grooved_skin,
        name="grooved_skin",
        color=cq.Color(0.70, 0.20, 0.15),
        loc=cq.Location((DISPLAY_OFFSET_MM, 0.0, 0.0)),
    )

    show(
        assembly,
        title="BALL 001 — Smooth vs Grooved Skin",
        edges=False,
    )


if __name__ == "__main__":
    main()