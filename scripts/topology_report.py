from ball001.cad import build_layer_solids
from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM
from ball001.topology import (
    TOPOLOGY_1_SEAM,
    TOPOLOGY_2_SEAM,
    TOPOLOGY_3_SEAM,
)
from ball001.topology_cad import build_topology_grooved_skin

MM3_PER_M3 = 1_000_000_000.0


def main() -> None:
    skin = BALL_001.layers[0]

    original_skin = build_layer_solids(BALL_001)[0].solid
    original_volume_mm3 = original_skin.val().Volume()

    topologies = (
        TOPOLOGY_1_SEAM,
        TOPOLOGY_2_SEAM,
        TOPOLOGY_3_SEAM,
    )

    print("BALL 001 — SEAM TOPOLOGY REPORT")
    print("=" * 72)
    print(
        f"{'Topology':<24}"
        f"{'Seams':>8}"
        f"{'Removed volume':>20}"
        f"{'Removed mass':>18}"
    )
    print("-" * 72)

    for topology in topologies:
        grooved_skin = build_topology_grooved_skin(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )

        grooved_volume_mm3 = grooved_skin.val().Volume()

        removed_volume_mm3 = (
            original_volume_mm3
            - grooved_volume_mm3
        )

        removed_volume_m3 = (
            removed_volume_mm3
            / MM3_PER_M3
        )

        removed_mass_kg = (
            removed_volume_m3
            * skin.density_kg_m3
        )

        print(
            f"{topology.name:<24}"
            f"{len(topology.seams):>8}"
            f"{removed_volume_mm3:>20.3f}"
            f"{removed_mass_kg * 1000:>18.3f}"
        )

    print()
    print("Evidence class: PENDING computational topology study.")
    print("Results are CAD-derived estimates, not measured values.")


if __name__ == "__main__":
    main()