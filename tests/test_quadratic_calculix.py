from pathlib import Path

import pytest

from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
    total_wall_thickness_m,
)
from ball001.mesh import MEDIUM_MESH
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)
from ball001.quadratic_calculix import (
    export_quadratic_calculix_deck,
    load_quadratic_solver_mesh,
)
from ball001.quadratic_mesh import (
    generate_quadratic_surface_mesh,
)


@pytest.fixture(scope="module")
def s6_deck(
    tmp_path_factory,
):
    directory = tmp_path_factory.mktemp(
        "calculix_s6"
    )

    mesh_path = (
        Path(directory)
        / "quadratic.msh"
    )

    deck_path = (
        Path(directory)
        / "verify_s6.inp"
    )

    mesh_summary = (
        generate_quadratic_surface_mesh(
            BALL_001,
            MEDIUM_MESH,
            output_path=mesh_path,
        )
    )

    deck_summary = (
        export_quadratic_calculix_deck(
            mesh_path=mesh_path,
            deck_path=deck_path,
            load_case=(
                BALL001_NOMINAL_PRESSURE
            ),
            material=(
                BALL001_VERIFICATION_MATERIAL
            ),
            shell_thickness_m=(
                total_wall_thickness_m(
                    BALL_001
                )
            ),
        )
    )

    return (
        mesh_summary,
        deck_summary,
        deck_path.read_text(),
        mesh_path,
    )


def test_s6_deck_preserves_triangle_count(
    s6_deck,
) -> None:
    (
        mesh_summary,
        deck_summary,
        _,
        _,
    ) = s6_deck

    assert (
        deck_summary.triangle_count
        == mesh_summary.triangle_count
    )


def test_s6_deck_uses_quadratic_shell_elements(
    s6_deck,
) -> None:
    _, _, text, _ = s6_deck

    assert (
        "*ELEMENT, TYPE=S6, ELSET=EALL"
        in text
    )


def test_s6_mesh_has_six_nodes_per_element(
    s6_deck,
) -> None:
    _, _, _, mesh_path = s6_deck

    solver_mesh = (
        load_quadratic_solver_mesh(
            mesh_path
        )
    )

    first = solver_mesh.triangles[0]

    assert len(
        {
            first.node_1,
            first.node_2,
            first.node_3,
            first.node_4,
            first.node_5,
            first.node_6,
        }
    ) == 6


def test_s6_pressure_is_positive(
    s6_deck,
) -> None:
    _, summary, text, _ = s6_deck

    assert (
        summary.applied_pressure_n_mm2
        == pytest.approx(
            0.030656
        )
    )

    assert (
        "EALL, P, 0.030656000"
        in text
    )


def test_s6_constraint_nodes_are_unique(
    s6_deck,
) -> None:
    _, summary, _, _ = s6_deck

    assert len(
        {
            summary.pin_x_tag,
            summary.pin_y_tag,
            summary.pin_z_tag,
        }
    ) == 3


def test_s6_deck_requests_2d_output(
    s6_deck,
) -> None:
    _, _, text, _ = s6_deck

    assert (
        "*EL FILE, OUTPUT=2D"
        in text
    )