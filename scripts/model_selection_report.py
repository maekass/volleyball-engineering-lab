from pathlib import Path

from ball001.model_selection import (
    BALL001_MODEL_SELECTION_TARGET,
    assess_geometry_model,
)
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
    cases = build_stiffness_sweep_cases()

    mechanics = {}

    for case in cases:
        frd_path = (
            RESULT_DIRECTORY
            / f"{case.solver_name}.frd"
        )

        mechanics[
            (
                case.youngs_modulus_mpa,
                case.geometry_mode,
            )
        ] = analyze_stiffness_case(
            case=case,
            mesh_path=MESH_PATH,
            frd_path=frd_path,
        )

    print(
        "BALL 001 — GEOMETRY MODEL "
        "SELECTION"
    )
    print("=" * 94)

    print(
        "Project TARGET criteria:"
    )

    print(
        "  Linear geometry may be retained when"
    )

    print(
        "  |Δu| <= "
        f"{BALL001_MODEL_SELECTION_TARGET.max_displacement_difference_percent:.1f}%"
    )

    print(
        "  AND |ΔS| <= "
        f"{BALL001_MODEL_SELECTION_TARGET.max_stress_difference_percent:.1f}%"
    )

    print()

    print(
        f"{'E [MPa]':>10}"
        f"{'Δu':>12}"
        f"{'ΔS':>12}"
        f"{'u target':>14}"
        f"{'S target':>14}"
        f"{'Recommendation':>20}"
    )

    print("-" * 94)

    for modulus_mpa in (
        100.0,
        20.0,
        5.0,
    ):
        linear = mechanics[
            (
                modulus_mpa,
                GeometryMode.LINEAR,
            )
        ]

        nonlinear = mechanics[
            (
                modulus_mpa,
                GeometryMode.NLGEOM,
            )
        ]

        divergence = (
            compare_linear_and_nlgeom(
                linear,
                nonlinear,
            )
        )

        assessment = (
            assess_geometry_model(
                divergence
            )
        )

        displacement_status = (
            "PASS"
            if assessment.displacement_within_target
            else "FAIL"
        )

        stress_status = (
            "PASS"
            if assessment.stress_within_target
            else "FAIL"
        )

        print(
            f"{modulus_mpa:>10.1f}"
            f"{assessment.displacement_difference_percent:>11.2f}%"
            f"{assessment.stress_difference_percent:>11.2f}%"
            f"{displacement_status:>14}"
            f"{stress_status:>14}"
            f"{assessment.recommendation.value.upper():>20}"
        )

    print()
    print(
        "Decision logic:"
    )

    print(
        "  Retain the least-complex geometry "
        "model only when both sensitivity "
        "targets are satisfied."
    )

    print()
    print(
        "These 2% displacement and 5% stress "
        "limits are BALL 001 project TARGETS."
    )

    print(
        "They are not universal FEA acceptance "
        "criteria or published volleyball standards."
    )

    print()
    print(
        "Effective moduli remain PENDING "
        "sensitivity anchors."
    )

    print(
        "Model responses are SIMULATED."
    )


if __name__ == "__main__":
    main()