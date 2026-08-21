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
)
from ball001.pressure_envelope import (
    PRESSURE_LEVELS,
    build_pressure_envelope_cases,
)

MESH_PATH = Path(
    "exports/fea/ball001_medium_ccx.msh"
)

RESULT_DIRECTORY = Path(
    "exports/fea/pressure_envelope"
)


def main() -> None:
    cases = build_pressure_envelope_cases()

    mechanics = {}

    for case in cases:
        frd_path = (
            RESULT_DIRECTORY
            / f"{case.solver_name}.frd"
        )

        if not frd_path.exists():
            raise FileNotFoundError(
                "CalculiX result file does not exist: "
                f"{frd_path}"
            )

        mechanics[
            (
                case.pressure_level.label,
                case.geometry_mode,
            )
        ] = analyze_stiffness_case(
            case=case.stiffness_case(),
            mesh_path=MESH_PATH,
            frd_path=frd_path,
        )

    print(
        "BALL 001 — PRESSURE ENVELOPE "
        "MODEL ROBUSTNESS"
    )
    print("=" * 132)

    print(
        f"{'Pressure':>12}"
        f"{'Linear u':>14}"
        f"{'NLGEOM u':>14}"
        f"{'Δu':>11}"
        f"{'Linear S':>14}"
        f"{'NLGEOM S':>14}"
        f"{'ΔS':>11}"
        f"{'u target':>12}"
        f"{'S target':>12}"
        f"{'Model':>12}"
    )

    print(
        f"{'[kPa]':>12}"
        f"{'[mm]':>14}"
        f"{'[mm]':>14}"
        f"{'[%]':>11}"
        f"{'[N/mm²]':>14}"
        f"{'[N/mm²]':>14}"
        f"{'[%]':>11}"
        f"{'':>12}"
        f"{'':>12}"
        f"{'':>12}"
    )

    print("-" * 132)

    assessments = []

    for pressure_level in PRESSURE_LEVELS:
        linear = mechanics[
            (
                pressure_level.label,
                GeometryMode.LINEAR,
            )
        ]

        nonlinear = mechanics[
            (
                pressure_level.label,
                GeometryMode.NLGEOM,
            )
        ]

        divergence = compare_linear_and_nlgeom(
            linear,
            nonlinear,
        )

        assessment = assess_geometry_model(
            divergence
        )

        assessments.append(
            (
                pressure_level,
                assessment,
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
            f"{pressure_level.pressure_kpa:>12.3f}"
            f"{linear.mean_radial_displacement_mm:>14.4f}"
            f"{nonlinear.mean_radial_displacement_mm:>14.4f}"
            f"{assessment.displacement_difference_percent:>10.2f}%"
            f"{linear.mean_tangential_stress_n_mm2:>14.4f}"
            f"{nonlinear.mean_tangential_stress_n_mm2:>14.4f}"
            f"{assessment.stress_difference_percent:>10.2f}%"
            f"{displacement_status:>12}"
            f"{stress_status:>12}"
            f"{assessment.recommendation.value.upper():>12}"
        )

    print()
    print("BALL 001 project TARGET:")

    print(
        "  retain linear geometry only when "
        f"|Δu| <= "
        f"{BALL001_MODEL_SELECTION_TARGET.max_displacement_difference_percent:.1f}% "
        "AND "
        f"|ΔS| <= "
        f"{BALL001_MODEL_SELECTION_TARGET.max_stress_difference_percent:.1f}%."
    )

    print()

    all_linear = all(
        assessment.linear_model_accepted
        for _, assessment in assessments
    )

    if all_linear:
        print("Envelope result:")
        print(
            "  LINEAR geometry remains within "
            "the BALL 001 project targets across "
            "the full pressure envelope at the "
            "20 MPa sensitivity anchor."
        )
    else:
        print("Envelope result:")
        print(
            "  At least one pressure condition "
            "exceeds the BALL 001 linear-model "
            "sensitivity target."
        )
        print(
            "  NLGEOM is therefore required for "
            "an envelope-robust analysis at this "
            "effective stiffness."
        )

    print()
    print(
        "Pressure values are benchmark operating "
        "conditions."
    )
    print(
        "The 20 MPa effective modulus remains a "
        "PENDING sensitivity anchor."
    )
    print("Model responses are SIMULATED.")


if __name__ == "__main__":
    main()
