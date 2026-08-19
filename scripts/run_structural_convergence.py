from ball001.structural_convergence import (
    StructuralConvergenceResult,
    compare_consecutive_results,
    is_converged,
)

CONVERGENCE_TOLERANCE = 0.01


def print_convergence_report(
    results: tuple[
        StructuralConvergenceResult,
        ...,
    ],
) -> None:
    comparisons = compare_consecutive_results(
        results
    )

    print(
        "BALL 001 — STRUCTURAL MESH "
        "CONVERGENCE REPORT"
    )
    print("=" * 72)

    print(
        f"{'Mesh':<12}"
        f"{'Size':>10}"
        f"{'Nodes':>12}"
        f"{'Elements':>12}"
        f"{'Disp.':>14}"
    )

    print("-" * 72)

    for result in results:
        print(
            f"{result.mesh_label:<12}"
            f"{result.characteristic_length_mm:>8.2f} mm"
            f"{result.node_count:>12}"
            f"{result.element_count:>12}"
            f"{result.displacement_m * 1000:>11.4f} mm"
        )

    print()
    print("CONSECUTIVE CHANGE")
    print("-" * 72)

    for comparison in comparisons:
        print(
            f"{comparison.coarse_label}"
            f" -> {comparison.fine_label}: "
            f"{comparison.relative_displacement_change * 100:.3f}%"
        )

    print()

    converged = is_converged(
        results,
        tolerance=CONVERGENCE_TOLERANCE,
    )

    print(
        "Convergence tolerance: "
        f"{CONVERGENCE_TOLERANCE * 100:.1f}%"
    )

    print(
        "Final convergence status: "
        f"{'PASS' if converged else 'FAIL'}"
    )

    print()
    print(
        "Results must originate from actual structural "
        "simulation runs and be classified SIMULATED."
    )


def main() -> None:
    raise SystemExit(
        "No structural FEA results exist yet. "
        "Run the BALL 001 structural solver first, then "
        "pass those SIMULATED results to "
        "print_convergence_report()."
    )


if __name__ == "__main__":
    main()