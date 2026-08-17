from pathlib import Path

from ball001.cad import (
    build_half_section_layers,
    build_layer_solids,
    build_outer_sphere,
)
from ball001.design import BALL_001

EXPORT_DIR = Path("exports/cad")


def main() -> None:
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    outer_sphere = build_outer_sphere(BALL_001)

    outer_path = EXPORT_DIR / "ball001_outer.step"
    outer_sphere.export(str(outer_path))

    print(f"Exported: {outer_path}")

    for layer in build_layer_solids(BALL_001):
        layer_path = EXPORT_DIR / f"ball001_{layer.name}.step"
        layer.solid.export(str(layer_path))

        print(
            f"Exported: {layer_path} "
            f"({layer.outer_radius_mm:.3f} -> "
            f"{layer.inner_radius_mm:.3f} mm)"
        )

    print()
    print("HALF-SECTION LAYERS")
    print("-" * 50)

    for layer in build_half_section_layers(BALL_001):
        section_path = EXPORT_DIR / f"ball001_{layer.name}_section.step"
        layer.solid.export(str(section_path))

        print(f"Exported: {section_path}")


if __name__ == "__main__":
    main()