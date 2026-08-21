from pathlib import Path

from ball001.pressure_envelope import (
    build_pressure_envelope_cases,
)
from ball001.pressure_envelope_runner import (
    run_pressure_envelope,
)

WORKING_DIRECTORY = Path(
    "exports/fea/pressure_envelope"
)


def main() -> None:
    cases = build_pressure_envelope_cases()

    print(
        "BALL 001 — CALCULIX "
        "PRESSURE ENVELOPE"
    )
    print("=" * 92)

    print(
        f"Cases:             "
        f"{len(cases)}"
    )

    print(
        f"Working directory: "
        f"{WORKING_DIRECTORY}"
    )

    print()

    results = run_pressure_envelope(
        cases=cases,
        working_directory=WORKING_DIRECTORY,
    )

    print(
        f"{'Case':<42}"
        f"{'Return':>10}"
        f"{'Finished':>14}"
        f"{'Status':>14}"
    )

    print("-" * 92)

    for result in results:
        status = (
            "PASS"
            if result.succeeded
            else "FAIL"
        )

        finished = (
            "yes"
            if result.job_finished
            else "no"
        )

        print(
            f"{result.case.solver_name:<42}"
            f"{result.return_code:>10}"
            f"{finished:>14}"
            f"{status:>14}"
        )

    failed_results = [
        result
        for result in results
        if not result.succeeded
    ]

    print()

    if failed_results:
        print(
            "One or more pressure-envelope "
            "CalculiX cases failed."
        )
        print()

        for result in failed_results:
            print(
                f"--- {result.case.solver_name} ---"
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print(result.stderr)

        raise SystemExit(1)

    print(
        "All six pressure-envelope "
        "CalculiX cases finished successfully."
    )


if __name__ == "__main__":
    main()
