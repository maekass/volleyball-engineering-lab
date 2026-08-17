from ball001.cad import MM_PER_M, build_layer_solids
from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM
from ball001.surface_cad import build_grooved_skin

MM3_PER_M3 = 1_000_000_000.0


def main() -> None:
    skin = BALL_001.layers[0]

    original_skin = build_layer_solids(BALL_001)[0].solid
    grooved_skin = build_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
    )

    original_volume_mm3 = original_skin.val().Volume()
    grooved_volume_mm3 = grooved_skin.val().Volume()

    removed_volume_mm3 = original_volume_mm3 - grooved_volume_mm3
    removed_volume_m3 = removed_volume_mm3 / MM3_PER_M3

    removed_mass_kg = removed_volume_m3 * skin.density_kg_m3

    width_mm = BALL_001_SEAM.width_m * MM_PER_M
    depth_mm = BALL_001_SEAM.depth_m * MM_PER_M

    print("BALL 001 — GROOVE REPORT")
    print("=" * 50)
    print(f"Seam width:             {width_mm:.3f} mm")
    print(f"Seam depth:             {depth_mm:.3f} mm")
    print(f"Skin thickness:         {skin.thickness_m * MM_PER_M:.3f} mm")
    print()
    print(f"Original skin volume:   {original_volume_mm3:.3f} mm^3")
    print(f"Grooved skin volume:    {grooved_volume_mm3:.3f} mm^3")
    print(f"Removed volume:         {removed_volume_mm3:.3f} mm^3")
    print(f"Estimated mass removed: {removed_mass_kg * 1000:.3f} g")
    print()
    print(f"Evidence class:         {BALL_001_SEAM.evidence}")
    print("NOTE: Seam dimensions are provisional computational inputs.")
    print("This is a CAD-derived estimate, not a measured result.")


if __name__ == "__main__":
    main()