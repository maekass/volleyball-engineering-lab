from pathlib import Path

from ball001.nonlinear_stiffness_results import (
    analyze_stiffness_case,
    compare_linear_and_nlgeom,
)
from ball001.nonlinear_stiffness_sweep import (
    GeometryMode,
    build_stiffness_sweep_cases,
)

MESH_PATH = Path(
    "exports/fea/ball001_medium_ccx.msh"
)

RESULT_DIRECTORY = Path(
    "exports/fea/nonlinear_stiffness"
)


def main() -> None:
    cases = (
        build_stiffness_sweep_cases()
    )

    results = {}

    for case in cases:
        frd_path = (
            RESULT_DIRECTORY
            / f"{case.solver_name}.frd"
        )

        result = analyze_stiffness_case(
            case=case,
            mesh_path=MESH_PATH,
            frd_path=frd_path,
        )

        results[
            (
                case.youngs_modulus_mpa,
                case.geometry_mode,
            )
        ] = result

    comparisons = []

    for modulus_mpa in (
        100.0,
        20.0,
        5.0,
    ):
        linear = results[
            (
                modulus_mpa,
                GeometryMode.LINEAR,
            )
        ]

        nonlinear = results[
            (
                modulus_mpa,
                GeometryMode.NLGEOM,
            )
        ]

        comparisons.append(
            compare_linear_and_nlgeom(
                linear,
                nonlinear,
            )
        )

    print(
        "BALL 001 — NONLINEAR "
        "STIFFNESS DIVERGENCE"
    )
    print("=" * 122)

    print(
        f"{'E':>8}"
        f"{'Linear u':>14}"
        f"{'NLGEOM u':>14}"
        f"{'Δu':>11}"
        f"{'Lin Δr/r':>13}"
        f"{'NL Δr/r':>13}"
        f"{'Linear S':>14}"
        f"{'NLGEOM S':>14}"
        f"{'ΔS':>11}"
    )

    print(
        f"{'[MPa]':>8}"
        f"{'[mm]':>14}"
        f"{'[mm]':>14}"
        f"{'[%]':>11}"
        f"{'[%]':>13}"
        f"{'[%]':>13}"
        f"{'[N/mm²]':>14}"
        f"{'[N/mm²]':>14}"
        f"{'[%]':>11}"
    )

    print("-" * 122)

    for result in comparisons:
        print(
            f"{result.youngs_modulus_mpa:>8.1f}"
            f"{result.linear_radial_displacement_mm:>14.4f}"
            f"{result.nonlinear_radial_displacement_mm:>14.4f}"
            f"{result.displacement_difference_percent:>10.2f}%"
            f"{result.linear_radial_expansion_percent:>12.2f}%"
            f"{result.nonlinear_radial_expansion_percent:>12.2f}%"
            f"{result.linear_tangential_stress_n_mm2:>14.4f}"
            f"{result.nonlinear_tangential_stress_n_mm2:>14.4f}"
            f"{result.stress_difference_percent:>10.2f}%"
        )

    print()
    print(
        "Δu and ΔS are NLGEOM differences "
        "relative to the corresponding "
        "linear-geometry solution."
    )

    print(
        "Δr/r is mean radial expansion divided "
        "by the nominal mesh radius."
    )

    print()
    print(
        "No universal linear/nonlinear cutoff "
        "is imposed here. The divergence is "
        "reported directly so model-selection "
        "criteria can be justified from the "
        "observed numerical sensitivity."
    )

    print()
    print(
        "The 100, 20, and 5 MPa effective "
        "moduli are PENDING sensitivity anchors, "
        "not measured volleyball properties."
    )

    print(
        "All values are SIMULATED."
    )


if __name__ == "__main__":
    main()