from pathlib import Path

import pytest

from ball001.calculix_deck import (
    export_calculix_verification_deck,
)
from ball001.design import BALL_001
from ball001.effective_shell import (
    BALL001_VERIFICATION_MATERIAL,
    total_wall_thickness_m,
)
from ball001.mesh import (
    MEDIUM_MESH,
    generate_surface_mesh,
)
from ball001.pressure import (
    BALL001_NOMINAL_PRESSURE,
)


@pytest.fixture(scope="module")
def verification_deck(
    tmp_path_factory,
):
    directory = tmp_path_factory.mktemp(
        "calculix"
    )

    mesh_path = Path(
        directory
    ) / "medium.msh"

    deck_path = Path(
        directory
    ) / "verify.inp"

    mesh_summary = generate_surface_mesh(
        BALL_001,
        MEDIUM_MESH,
        output_path=mesh_path,
    )

    deck_summary = (
        export_calculix_verification_deck(
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
    )


def test_deck_preserves_mesh_counts(
    verification_deck,
) -> None:
    (
        mesh_summary,
        deck_summary,
        _,
    ) = verification_deck

    assert (
        deck_summary.node_count
        == mesh_summary.node_count
    )

    assert (
        deck_summary.triangle_count
        == mesh_summary.triangle_count
    )


def test_deck_uses_s3_shell_elements(
    verification_deck,
) -> None:
    _, _, text = verification_deck

    assert (
        "*ELEMENT, TYPE=S3, ELSET=EALL"
        in text
    )


def test_deck_contains_shell_section(
    verification_deck,
) -> None:
    _, _, text = verification_deck

    assert (
        "*SHELL SECTION, "
        "ELSET=EALL, "
        "MATERIAL=VERIFICATION"
        in text
    )

    assert "2.650000000" in text


def test_deck_contains_nominal_pressure(
    verification_deck,
) -> None:
    _, summary, text = (
        verification_deck
    )

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


def test_constraint_nodes_are_unique(
    verification_deck,
) -> None:
    _, summary, _ = (
        verification_deck
    )

    assert len(
        {
            summary.pin_x_tag,
            summary.pin_y_tag,
            summary.pin_z_tag,
        }
    ) == 3


def test_deck_requests_two_dimensional_shell_output(
    verification_deck,
) -> None:
    _, _, text = verification_deck

    assert (
        "*EL FILE, OUTPUT=2D"
        in text
    )

    assert "*NODE FILE" in text