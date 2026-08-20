from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NonlinearDeckExport:
    source_path: Path
    output_path: Path
    nonlinear_step_count: int


def add_nlgeom_to_deck(
    deck_text: str,
) -> str:
    lines = deck_text.splitlines(
        keepends=True
    )

    step_indices = []

    for index, line in enumerate(
        lines
    ):
        if line.strip().upper() == "*STEP":
            step_indices.append(
                index
            )

    if not step_indices:
        raise ValueError(
            "Deck contains no plain *STEP card."
        )

    if len(step_indices) != 1:
        raise ValueError(
            "Expected exactly one plain *STEP card, "
            f"found {len(step_indices)}."
        )

    step_index = step_indices[0]

    original_line = lines[
        step_index
    ]

    newline = (
        "\n"
        if original_line.endswith("\n")
        else ""
    )

    lines[
        step_index
    ] = (
        "*STEP,NLGEOM"
        + newline
    )

    return "".join(
        lines
    )


def export_nlgeom_deck(
    linear_deck_path: Path,
    nonlinear_deck_path: Path,
) -> NonlinearDeckExport:
    if not linear_deck_path.exists():
        raise FileNotFoundError(
            "Linear CalculiX deck does not exist: "
            f"{linear_deck_path}"
        )

    if (
        linear_deck_path.resolve()
        == nonlinear_deck_path.resolve()
    ):
        raise ValueError(
            "Nonlinear output path must differ "
            "from the linear source path."
        )

    linear_text = (
        linear_deck_path.read_text()
    )

    nonlinear_text = (
        add_nlgeom_to_deck(
            linear_text
        )
    )

    nonlinear_step_count = (
        nonlinear_text.upper().count(
            "*STEP,NLGEOM"
        )
    )

    if nonlinear_step_count != 1:
        raise ValueError(
            "Expected exactly one NLGEOM step "
            "after deck conversion."
        )

    nonlinear_deck_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    nonlinear_deck_path.write_text(
        nonlinear_text
    )

    return NonlinearDeckExport(
        source_path=linear_deck_path,
        output_path=nonlinear_deck_path,
        nonlinear_step_count=(
            nonlinear_step_count
        ),
    )