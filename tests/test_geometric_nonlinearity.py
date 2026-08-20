from pathlib import Path

import pytest

from ball001.geometric_nonlinearity import (
    add_nlgeom_to_deck,
    export_nlgeom_deck,
)


def test_add_nlgeom_replaces_plain_step() -> None:
    linear = (
        "*HEADING\n"
        "*STEP\n"
        "*STATIC\n"
        "*END STEP\n"
    )

    nonlinear = add_nlgeom_to_deck(
        linear
    )

    assert "*STEP,NLGEOM\n" in nonlinear
    assert "\n*STEP\n" not in nonlinear


def test_other_deck_content_is_preserved() -> None:
    linear = (
        "*HEADING\n"
        "** BALL 001\n"
        "*STEP\n"
        "*STATIC\n"
        "*DLOAD\n"
        "EALL,P,0.030656\n"
        "*END STEP\n"
    )

    nonlinear = add_nlgeom_to_deck(
        linear
    )

    assert "*STATIC\n" in nonlinear
    assert (
        "EALL,P,0.030656\n"
        in nonlinear
    )
    assert "** BALL 001\n" in nonlinear


def test_missing_plain_step_is_rejected() -> None:
    deck = (
        "*HEADING\n"
        "*STATIC\n"
    )

    with pytest.raises(
        ValueError,
        match="no plain",
    ):
        add_nlgeom_to_deck(
            deck
        )


def test_multiple_plain_steps_are_rejected() -> None:
    deck = (
        "*STEP\n"
        "*STATIC\n"
        "*END STEP\n"
        "*STEP\n"
        "*STATIC\n"
        "*END STEP\n"
    )

    with pytest.raises(
        ValueError,
        match="exactly one",
    ):
        add_nlgeom_to_deck(
            deck
        )


def test_export_nlgeom_deck(
    tmp_path: Path,
) -> None:
    linear_path = (
        tmp_path
        / "linear.inp"
    )

    nonlinear_path = (
        tmp_path
        / "nonlinear"
        / "nlgeom.inp"
    )

    linear_path.write_text(
        "*HEADING\n"
        "*STEP\n"
        "*STATIC\n"
        "*END STEP\n"
    )

    result = export_nlgeom_deck(
        linear_path,
        nonlinear_path,
    )

    assert nonlinear_path.exists()

    text = (
        nonlinear_path.read_text()
    )

    assert "*STEP,NLGEOM" in text

    assert (
        result.nonlinear_step_count
        == 1
    )

    assert (
        result.source_path
        == linear_path
    )

    assert (
        result.output_path
        == nonlinear_path
    )


def test_export_rejects_same_path(
    tmp_path: Path,
) -> None:
    deck_path = (
        tmp_path
        / "model.inp"
    )

    deck_path.write_text(
        "*STEP\n"
    )

    with pytest.raises(
        ValueError,
        match="must differ",
    ):
        export_nlgeom_deck(
            deck_path,
            deck_path,
        )