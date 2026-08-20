from pathlib import Path

from ball001.nonlinear_stiffness_runner import (
    run_calculix_sweep,
)
from ball001.nonlinear_stiffness_sweep import (
    build_stiffness_sweep_cases,
)

WORKING_DIRECTORY = Path(
    "exports/fea/nonlinear_stiffness"
)


def main() -> None:
    cases = (
        build_stiffness_sweep_cases()
    )

    print(
        "BALL 001 — CALCULIX "
        "NONLINEAR STIFFNESS SWEEP"
    )
    print("=" * 88)

    print(
        f"Cases:             "
        f"{len(cases)}"
    )

    print(
        f"Working directory: "
        f"{WORKING_DIRECTORY}"
    )

    print()

    results = run_calculix_sweep(
        cases=cases,
        working_directory=(
            WORKING_DIRECTORY
        ),
    )

    print(
        f"{'Case':<38}"
        f"{'Return':>10}"
        f"{'Finished':>14}"
        f"{'Status':>14}"
    )

    print("-" * 88)

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
            f"{result.case.solver_name:<38}"
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
            "One or more CalculiX cases failed."
        )
        print()

        for result in failed_results:
            print(
                f"--- {result.case.solver_name} ---"
            )

            if result.stdout:
                print(
                    result.stdout
                )

            if result.stderr:
                print(
                    result.stderr
                )

        raise SystemExit(1)

    print(
        "All six CalculiX cases "
        "finished successfully."
    )


if __name__ == "__main__":
    main()