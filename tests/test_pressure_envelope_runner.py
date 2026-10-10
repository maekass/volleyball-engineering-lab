from pathlib import Path
from subprocess import CompletedProcess
from unittest.mock import patch

from ball001.nonlinear_stiffness_sweep import GeometryMode
from ball001.pressure_envelope import PRESSURE_LEVELS, PressureEnvelopeCase
from ball001.pressure_envelope_runner import run_pressure_envelope_case


def test_stale_frd_does_not_count_as_solver_success(tmp_path: Path) -> None:
    case = PressureEnvelopeCase(
        pressure_level=PRESSURE_LEVELS[1],
        geometry_mode=GeometryMode.LINEAR,
    )
    (tmp_path / f"{case.solver_name}.inp").write_text("*HEADING\n")
    (tmp_path / f"{case.solver_name}.frd").write_text("old output")
    with patch("ball001.pressure_envelope_runner.subprocess.run") as runner:
        runner.return_value = CompletedProcess(
            args=["ccx"], returncode=0, stdout="Job finished", stderr=""
        )
        result = run_pressure_envelope_case(case, tmp_path, executable="ccx")
    assert result.job_finished
    assert not result.results_fresh
    assert not result.succeeded


def test_fresh_nonempty_frd_is_required(tmp_path: Path) -> None:
    case = PressureEnvelopeCase(
        pressure_level=PRESSURE_LEVELS[1],
        geometry_mode=GeometryMode.LINEAR,
    )
    (tmp_path / f"{case.solver_name}.inp").write_text("*HEADING\n")

    def mock_run(*args: object, **kwargs: object) -> CompletedProcess[str]:
        (tmp_path / f"{case.solver_name}.frd").write_text("new result")
        return CompletedProcess(
            args=["ccx"], returncode=0, stdout="Job finished", stderr=""
        )

    with patch(
        "ball001.pressure_envelope_runner.subprocess.run", side_effect=mock_run
    ):
        result = run_pressure_envelope_case(case, tmp_path, executable="ccx")
    assert result.results_fresh
    assert result.succeeded
