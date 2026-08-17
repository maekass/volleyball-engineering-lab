import cadquery as cq
from cadquery.vis import show

from ball001.cad import build_half_section_layers
from ball001.design import BALL_001

LAYER_COLORS = {
    "skin": cq.Color(0.75, 0.25, 0.20),
    "compliance": cq.Color(0.90, 0.65, 0.25),
    "reinforcement": cq.Color(0.30, 0.45, 0.75),
    "bladder": cq.Color(0.45, 0.25, 0.55),
}


def main() -> None:
    assembly = cq.Assembly(name="BALL_001_half_section")

    for layer in build_half_section_layers(BALL_001):
        color = LAYER_COLORS.get(
            layer.name,
            cq.Color("gray"),
        )

        assembly.add(
            layer.solid,
            name=layer.name,
            color=color,
        )

    show(assembly)


if __name__ == "__main__":
    main()