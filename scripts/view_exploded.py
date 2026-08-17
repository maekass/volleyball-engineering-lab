import cadquery as cq
from cadquery.vis import show

from ball001.cad import build_half_section_layers
from ball001.design import BALL_001

EXPLODE_STEP_MM = 35.0

LAYER_COLORS = {
    "skin": cq.Color(0.75, 0.25, 0.20),
    "compliance": cq.Color(0.90, 0.65, 0.25),
    "reinforcement": cq.Color(0.30, 0.45, 0.75),
    "bladder": cq.Color(0.45, 0.25, 0.55),
}


def main() -> None:
    assembly = cq.Assembly(name="BALL_001_exploded_section")

    for index, layer in enumerate(build_half_section_layers(BALL_001)):
        offset_mm = index * EXPLODE_STEP_MM

        assembly.add(
            layer.solid,
            name=layer.name,
            color=LAYER_COLORS[layer.name],
            loc=cq.Location((offset_mm, 0.0, 0.0)),
        )

    show(
        assembly,
        title="BALL 001 — Exploded Layer Inspection",
        edges=False,
    )


if __name__ == "__main__":
    main()