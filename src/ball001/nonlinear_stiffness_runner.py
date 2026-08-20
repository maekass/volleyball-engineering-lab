import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ball001.nonlinear_stiffness_sweep import (
    StiffnessSweepCase,
)


@dataclass(frozen=True)
class CalculixSweepRunResult:
    case: StiffnessSweepCase
    input_path: Path
    return_code: int
    job_finished: bool
    stdout: str
    stderr: str

    @property
    def succeeded(
        self,
    ) -> bool:
        return (
            self.return_code == 0
            and self.job_finished
        )


def find_calculix_executable() -> str:
    executable = shutil.which(
        "ccx"
    )

    if executable is None:
        raise FileNotFoundError(
            "CalculiX executable 'ccx' "
            "was not found on PATH."
        )

    return executable


def run_calculix_case(
    case: StiffnessSweepCase,
    working_directory: Path,
    executable: str | None = None,
) -> CalculixSweepRunResult:
    input_path = (
        working_directory
        / f"{case.solver_name}.inp"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            "CalculiX input deck does not exist: "
            f"{input_path}"
        )

    if executable is None:
        executable = (
            find_calculix_executable()
        )

    completed = subprocess.run(
        [
            executable,
            "-i",
            case.solver_name,
        ],
        cwd=working_directory,
        capture_output=True,
        text=True,
        check=False,
    )

    combined_output = (
        completed.stdout
        + "\n"
        + completed.stderr
    )

    return CalculixSweepRunResult(
        case=case,
        input_path=input_path,
        return_code=(
            completed.returncode
        ),
        job_finished=(
            "Job finished"
            in combined_output
        ),
        stdout=completed.stdout,
        stderr=completed.stderr,
    )


def run_calculix_sweep(
    cases: tuple[
        StiffnessSweepCase,
        ...,
    ],
    working_directory: Path,
    executable: str | None = None,
) -> tuple[
    CalculixSweepRunResult,
    ...,
]:
    results = []

    for case in cases:
        result = run_calculix_case(
            case=case,
            working_directory=(
                working_directory
            ),
            executable=executable,
        )

        results.append(
            result
        )

    return tuple(
        results
    )