from dataclasses import dataclass
from enum import Enum


class GeometryMode(str, Enum):
    LINEAR = "linear"
    NLGEOM = "nlgeom"


@dataclass(frozen=True)
class StiffnessSweepCase:
    label: str
    youngs_modulus_mpa: float
    poisson_ratio: float
    geometry_mode: GeometryMode
    initial_increment: float = 0.05
    time_period: float = 1.0
    minimum_increment: float = 1.0e-5
    maximum_increment: float = 0.10

    def __post_init__(self) -> None:
        if self.youngs_modulus_mpa <= 0.0:
            raise ValueError(
                "Young's modulus must be positive."
            )

        if not (
            -1.0
            < self.poisson_ratio
            < 0.5
        ):
            raise ValueError(
                "Poisson ratio must be between "
                "-1.0 and 0.5."
            )

        if self.initial_increment <= 0.0:
            raise ValueError(
                "Initial increment must be positive."
            )

        if self.time_period <= 0.0:
            raise ValueError(
                "Time period must be positive."
            )

        if self.minimum_increment <= 0.0:
            raise ValueError(
                "Minimum increment must be positive."
            )

        if self.maximum_increment <= 0.0:
            raise ValueError(
                "Maximum increment must be positive."
            )

        if (
            self.minimum_increment
            > self.initial_increment
        ):
            raise ValueError(
                "Minimum increment cannot exceed "
                "initial increment."
            )

        if (
            self.initial_increment
            > self.maximum_increment
        ):
            raise ValueError(
                "Initial increment cannot exceed "
                "maximum increment."
            )

    @property
    def youngs_modulus_n_mm2(
        self,
    ) -> float:
        return self.youngs_modulus_mpa

    @property
    def solver_name(
        self,
    ) -> str:
        return (
            f"ball001_"
            f"{self.label}_"
            f"{self.geometry_mode.value}"
        )


STIFFNESS_LEVELS_MPA = (
    (
        "high_100mpa",
        100.0,
    ),
    (
        "mid_20mpa",
        20.0,
    ),
    (
        "low_5mpa",
        5.0,
    ),
)


def build_stiffness_sweep_cases(
    poisson_ratio: float = 0.35,
) -> tuple[
    StiffnessSweepCase,
    ...,
]:
    cases = []

    for (
        label,
        youngs_modulus_mpa,
    ) in STIFFNESS_LEVELS_MPA:
        for geometry_mode in (
            GeometryMode.LINEAR,
            GeometryMode.NLGEOM,
        ):
            cases.append(
                StiffnessSweepCase(
                    label=label,
                    youngs_modulus_mpa=(
                        youngs_modulus_mpa
                    ),
                    poisson_ratio=(
                        poisson_ratio
                    ),
                    geometry_mode=(
                        geometry_mode
                    ),
                )
            )

    return tuple(
        cases
    )


def _replace_elastic_properties(
    deck_text: str,
    case: StiffnessSweepCase,
) -> str:
    lines = deck_text.splitlines(
        keepends=True
    )

    elastic_indices = [
        index
        for index, line in enumerate(
            lines
        )
        if line.strip()
        .upper()
        .startswith(
            "*ELASTIC"
        )
    ]

    if len(elastic_indices) != 1:
        raise ValueError(
            "Expected exactly one *ELASTIC "
            f"card, found {len(elastic_indices)}."
        )

    elastic_index = (
        elastic_indices[0]
    )

    data_index = None

    for index in range(
        elastic_index + 1,
        len(lines),
    ):
        stripped = (
            lines[index].strip()
        )

        if not stripped:
            continue

        if stripped.startswith("**"):
            continue

        if stripped.startswith("*"):
            break

        data_index = index
        break

    if data_index is None:
        raise ValueError(
            "*ELASTIC card contains no "
            "material data line."
        )

    newline = (
        "\n"
        if lines[
            data_index
        ].endswith("\n")
        else ""
    )

    lines[data_index] = (
        f"{case.youngs_modulus_n_mm2:.9f}, "
        f"{case.poisson_ratio:.9f}"
        f"{newline}"
    )

    return "".join(
        lines
    )


def _set_geometry_mode(
    deck_text: str,
    geometry_mode: GeometryMode,
) -> str:
    lines = deck_text.splitlines(
        keepends=True
    )

    step_indices = [
        index
        for index, line in enumerate(
            lines
        )
        if line.strip()
        .upper()
        .startswith(
            "*STEP"
        )
    ]

    if len(step_indices) != 1:
        raise ValueError(
            "Expected exactly one *STEP "
            f"card, found {len(step_indices)}."
        )

    step_index = step_indices[0]

    newline = (
        "\n"
        if lines[
            step_index
        ].endswith("\n")
        else ""
    )

    if (
        geometry_mode
        is GeometryMode.NLGEOM
    ):
        step_card = (
            "*STEP,NLGEOM"
        )

    else:
        step_card = "*STEP"

    lines[
        step_index
    ] = (
        step_card
        + newline
    )

    return "".join(
        lines
    )


def _set_static_increments(
    deck_text: str,
    case: StiffnessSweepCase,
) -> str:
    lines = deck_text.splitlines(
        keepends=True
    )

    static_indices = [
        index
        for index, line in enumerate(
            lines
        )
        if line.strip()
        .upper()
        .startswith(
            "*STATIC"
        )
    ]

    if len(static_indices) != 1:
        raise ValueError(
            "Expected exactly one *STATIC "
            f"card, found {len(static_indices)}."
        )

    static_index = (
        static_indices[0]
    )

    data_line = (
        f"{case.initial_increment:.9f}, "
        f"{case.time_period:.9f}, "
        f"{case.minimum_increment:.9e}, "
        f"{case.maximum_increment:.9f}\n"
    )

    next_data_index = None

    for index in range(
        static_index + 1,
        len(lines),
    ):
        stripped = (
            lines[index].strip()
        )

        if not stripped:
            continue

        if stripped.startswith("**"):
            continue

        if stripped.startswith("*"):
            break

        next_data_index = index
        break

    if next_data_index is None:
        lines.insert(
            static_index + 1,
            data_line,
        )

    else:
        newline = (
            "\n"
            if lines[
                next_data_index
            ].endswith("\n")
            else ""
        )

        lines[
            next_data_index
        ] = (
            data_line.rstrip("\n")
            + newline
        )

    return "".join(
        lines
    )


def build_stiffness_sweep_deck(
    source_deck_text: str,
    case: StiffnessSweepCase,
) -> str:
    deck_text = (
        _replace_elastic_properties(
            source_deck_text,
            case,
        )
    )

    deck_text = (
        _set_geometry_mode(
            deck_text,
            case.geometry_mode,
        )
    )

    deck_text = (
        _set_static_increments(
            deck_text,
            case,
        )
    )

    return deck_text