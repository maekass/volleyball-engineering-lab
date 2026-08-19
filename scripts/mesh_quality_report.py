from ball001.design import BALL_001
from ball001.mesh import (
    BALL001_MESH_SPECS,
    generate_surface_mesh,
)


def main() -> None:
    print(
        "BALL 001 — SURFACE MESH QUALITY "
        "AND GEOMETRIC CONVERGENCE"
    )

    print("=" * 96)

    print(
        f"{'Mesh':<10}"
        f"{'Size':>10}"
        f"{'Triangles':>12}"
        f"{'Faceted area':>17}"
        f"{'Area error':>14}"
        f"{'Min SICN':>12}"
        f"{'Mean SICN':>12}"
    )

    print("-" * 96)

    for spec in BALL001_MESH_SPECS:
        result = generate_surface_mesh(
            BALL_001,
            spec,
        )

        print(
            f"{result.name:<10}"
            f"{result.target_size_mm:>7.1f} mm"
            f"{result.triangle_count:>12}"
            f"{result.faceted_surface_area_mm2:>14.1f} mm²"
            f"{result.surface_area_error_percent:>11.4f} %"
            f"{result.min_sicn:>12.4f}"
            f"{result.mean_sicn:>12.4f}"
        )

    print()

    print(
        "Area error compares the straight-sided "
        "triangular mesh with the analytical sphere."
    )

    print(
        "SICN is an element shape-quality metric; "
        "negative values would indicate invalid "
        "or tangled elements."
    )

    print(
        "This is geometric mesh convergence, "
        "not structural FEA convergence."
    )


if __name__ == "__main__":
    main()