import subprocess
from pathlib import Path

import pytest

from ball001.nonlinear_stiffness_runner import (
    CalculixSweepRunResult,
    run_calculix_case,
)
from ball001.nonlinear_stiffness_sweep import (
    GeometryMode,
    StiffnessSweepCase,
)


def _case() -> StiffnessSweepCase:
    return StiffnessSweepCase(
        label="test_20mpa",
        youngs_modulus_mpa=20.0,
        poisson_ratio=0.35,
        geometry_mode=GeometryMode.NLGEOM,
    )


def test_success_requires_return_code_and_job_finished() -> None:
    result = CalculixSweepRunResult(
        case=_case(),
        input_path=Path("model.inp"),
        return_code=0,
        job_finished=True,
        stdout="Job finished",
        stderr="",
    )

    assert result.succeeded


def test_nonzero_return_code_is_failure() -> None:
    result = CalculixSweepRunResult(
        case=_case(),
        input_path=Path("model.inp"),
        return_code=1,
        job_finished=True,
        stdout="Job finished",
        stderr="",
    )

    assert not result.succeeded


def test_missing_job_finished_is_failure() -> None:
    result = CalculixSweepRunResult(
        case=_case(),
        input_path=Path("model.inp"),
        return_code=0,
        job_finished=False,
        stdout="",
        stderr="",
    )

    assert not result.succeeded


def test_missing_input_deck_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="input deck",
    ):
        run_calculix_case(
            case=_case(),
            working_directory=tmp_path,
            executable="ccx",
        )


def test_runner_detects_finished_job(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    case = _case()

    input_path = (
        tmp_path
        / f"{case.solver_name}.inp"
    )

    input_path.write_text(
        "*HEADING\n"
    )

    def fake_run(
        *args: object,
        **kwargs: object,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="Job finished\n",
            stderr="",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    result = run_calculix_case(
        case=case,
        working_directory=tmp_path,
        executable="ccx",
    )

    assert result.succeeded
    assert result.return_code == 0
    assert result.job_finished