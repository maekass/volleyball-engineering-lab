from pathlib import Path

import pytest

from ball001.calculix_deck import SolverNode
from ball001.calculix_results import (
    FrdStress,
    _mean_tangential_stress_n_mm2,
    _radial_displacement_mm,
    _radial_stress_n_mm2,
    parse_frd_results,
)


def _frd_data_line(
    node_tag: int,
    values: tuple[float, ...],
) -> str:
    return (
        " -1 "
        + f"{node_tag:9d}"
        + "".join(
            f"{value:12.5E}"
            for value in values
        )
        + "\n"
    )


def test_parse_frd_displacement_and_stress(
    tmp_path: Path,
) -> None:
    frd_path = (
        tmp_path
        / "synthetic.frd"
    )

    text = "".join(
        [
            " -4  DISP\n",
            _frd_data_line(
                1,
                (
                    0.01,
                    0.02,
                    0.03,
                ),
            ),
            " -3\n",
            " -4  STRESS\n",
            _frd_data_line(
                1,
                (
                    1.0,
                    2.0,
                    3.0,
                    0.1,
                    0.2,
                    0.3,
                ),
            ),
            " -3\n",
        ]
    )

    frd_path.write_text(
        text
    )

    result = parse_frd_results(
        frd_path
    )

    assert (
        result.displacements_mm[1]
        == pytest.approx(
            (
                0.01,
                0.02,
                0.03,
            )
        )
    )

    stress = (
        result.stresses_n_mm2[1]
    )

    assert (
        stress.sxx_n_mm2
        == pytest.approx(1.0)
    )

    assert (
        stress.syz_n_mm2
        == pytest.approx(0.2)
    )


def test_radial_displacement_on_x_axis() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    radial = _radial_displacement_mm(
        node,
        (
            0.05,
            0.02,
            0.0,
        ),
    )

    assert radial == pytest.approx(
        0.05
    )


def test_radial_stress_on_x_axis() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    stress = FrdStress(
        sxx_n_mm2=0.0,
        syy_n_mm2=0.6,
        szz_n_mm2=0.6,
        sxy_n_mm2=0.0,
        syz_n_mm2=0.0,
        szx_n_mm2=0.0,
    )

    assert (
        _radial_stress_n_mm2(
            node,
            stress,
        )
        == pytest.approx(0.0)
    )


def test_tangential_stress_on_x_axis() -> None:
    node = SolverNode(
        tag=1,
        x_mm=100.0,
        y_mm=0.0,
        z_mm=0.0,
    )

    stress = FrdStress(
        sxx_n_mm2=0.0,
        syy_n_mm2=0.6,
        szz_n_mm2=0.6,
        sxy_n_mm2=0.0,
        syz_n_mm2=0.0,
        szx_n_mm2=0.0,
    )

    assert (
        _mean_tangential_stress_n_mm2(
            node,
            stress,
        )
        == pytest.approx(
            0.6
        )
    )


def test_missing_frd_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError
    ):
        parse_frd_results(
            tmp_path
            / "missing.frd"
        )