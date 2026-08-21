from ball001.structural_model_decision import (
    BALL001_STRUCTURAL_EVIDENCE,
    BALL001_STRUCTURAL_MODEL,
)


def main() -> None:
    model = BALL001_STRUCTURAL_MODEL
    evidence = BALL001_STRUCTURAL_EVIDENCE

    print(
        "BALL 001 — FINAL STRUCTURAL "
        "MODEL DECISION"
    )
    print("=" * 88)

    print()
    print("DEFAULT WORKING MODEL")
    print("-" * 88)

    print(
        f"Mesh size:              "
        f"{model.working_mesh_size_mm:.1f} mm"
    )

    print(
        f"Shell formulation:      "
        f"{model.default_formulation.value}"
    )

    print(
        f"Geometry formulation:   "
        f"{model.default_geometry_model.value.upper()}"
    )

    print()
    print("VERIFICATION REFERENCES")
    print("-" * 88)

    print(
        f"Fine mesh:              "
        f"{model.verification_mesh_size_mm:.1f} mm"
    )

    print(
        f"Quadratic formulation:  "
        f"{model.verification_formulation.value}"
    )

    print(
        f"Nonlinear formulation:  "
        f"{model.escalation_geometry_model.value.upper()}"
    )

    print()
    print("MODEL-FORM EVIDENCE")
    print("-" * 88)

    print(
        f"{'Study':<38}"
        f"{'Δu':>14}"
        f"{'ΔS':>14}"
        f"{'Decision':>18}"
    )

    print("-" * 88)

    print(
        f"{'Medium → fine mesh':<38}"
        f"{evidence.medium_to_fine_displacement_change_percent:>13.3f}%"
        f"{evidence.medium_to_fine_stress_change_percent:>13.3f}%"
        f"{'MEDIUM':>18}"
    )

    print(
        f"{'S3 → S6 formulation':<38}"
        f"{evidence.s3_to_s6_displacement_change_percent:>13.3f}%"
        f"{evidence.s3_to_s6_stress_change_percent:>13.3f}%"
        f"{'S3':>18}"
    )

    print(
        f"{'1 GPa linear → NLGEOM':<38}"
        f"{evidence.stiff_nlgeom_displacement_change_percent:>13.3f}%"
        f"{evidence.stiff_nlgeom_stress_change_percent:>13.3f}%"
        f"{'LINEAR':>18}"
    )

    print(
        f"{'20 MPa linear → NLGEOM':<38}"
        f"{evidence.anchor_20mpa_displacement_change_percent:>13.2f}%"
        f"{evidence.anchor_20mpa_stress_change_percent:>13.2f}%"
        f"{'LINEAR':>18}"
    )

    print(
        f"{'5 MPa linear → NLGEOM':<38}"
        f"{evidence.anchor_5mpa_displacement_change_percent:>13.2f}%"
        f"{evidence.anchor_5mpa_stress_change_percent:>13.2f}%"
        f"{'NLGEOM':>18}"
    )

    print(
        f"{'20 MPa pressure envelope max':<38}"
        f"{evidence.pressure_envelope_max_displacement_change_percent:>13.2f}%"
        f"{evidence.pressure_envelope_max_stress_change_percent:>13.2f}%"
        f"{'LINEAR':>18}"
    )

    print()
    print("BALL 001 MODEL-SELECTION TARGET")
    print("-" * 88)

    print(
        "Retain linear geometry only when:"
    )

    print(
        f"  |Δu| <= "
        f"{model.displacement_sensitivity_target_percent:.1f}%"
    )

    print(
        f"  |ΔS| <= "
        f"{model.stress_sensitivity_target_percent:.1f}%"
    )

    print()
    print("FINAL DECISION")
    print("-" * 88)

    print(
        "Use the 8 mm S3 linear shell model as "
        "the default BALL 001 structural working model."
    )

    print(
        "Use the 5 mm mesh and S6 formulation as "
        "verification references rather than defaults."
    )

    print(
        "Escalate to NLGEOM whenever either project "
        "model-form sensitivity target is exceeded."
    )

    print()
    print(
        "At the 20 MPa PENDING stiffness anchor, "
        "linear geometry remains within target across "
        "29.430–31.882 kPa."
    )

    print(
        "At the 5 MPa PENDING stiffness anchor, "
        "NLGEOM is required by the project criteria."
    )

    print()
    print("EVIDENCE STATUS")
    print("-" * 88)

    print(
        "Structural responses:              SIMULATED"
    )

    print(
        "Effective stiffness anchors:       PENDING"
    )

    print(
        "Pressure operating envelope:       BENCHMARK"
    )

    print(
        "Physical model correlation:        PENDING"
    )

    print()
    print(
        "The selected model is the least-complex "
        "structural formulation currently justified "
        "by the numerical evidence."
    )


if __name__ == "__main__":
    main()