from dataclasses import dataclass

from ball001.nonlinear_stiffness_sweep import (
    GeometryMode,
    StiffnessSweepCase,
    build_stiffness_sweep_deck,
)


@dataclass(frozen=True)
class PressureLevel:
    label: str
    pressure_kpa: float

    def __post_init__(self) -> None:
        if self.pressure_kpa <= 0.0:
            raise ValueError(
                "Pressure must be positive."
            )

    @property
    def pressure_n_mm2(self) -> float:
        return (
            self.pressure_kpa
            / 1000.0
        )


@dataclass(frozen=True)
class PressureEnvelopeCase:
    pressure_level: PressureLevel
    geometry_mode: GeometryMode

    youngs_modulus_mpa: float = 20.0
    poisson_ratio: float = 0.35

    @property
    def solver_name(self) -> str:
        return (
            "ball001_pressure_"
            f"{self.pressure_level.label}_"
            f"{self.geometry_mode.value}"
        )

    def stiffness_case(
        self,
    ) -> StiffnessSweepCase:
        return StiffnessSweepCase(
            label=(
                "pressure_"
                f"{self.pressure_level.label}"
            ),
            youngs_modulus_mpa=(
                self.youngs_modulus_mpa
            ),
            poisson_ratio=(
                self.poisson_ratio
            ),
            geometry_mode=(
                self.geometry_mode
            ),
        )


PRESSURE_LEVELS = (
    PressureLevel(
        label="min",
        pressure_kpa=29.430,
    ),
    PressureLevel(
        label="nominal",
        pressure_kpa=30.656,
    ),
    PressureLevel(
        label="max",
        pressure_kpa=31.882,
    ),
)


def build_pressure_envelope_cases(
) -> tuple[
    PressureEnvelopeCase,
    ...,
]:
    cases = []

    for pressure_level in PRESSURE_LEVELS:
        for geometry_mode in (
            GeometryMode.LINEAR,
            GeometryMode.NLGEOM,
        ):
            cases.append(
                PressureEnvelopeCase(
                    pressure_level=(
                        pressure_level
                    ),
                    geometry_mode=(
                        geometry_mode
                    ),
                )
            )

    return tuple(cases)


def _replace_pressure_load(
    deck_text: str,
    pressure_n_mm2: float,
) -> str:
    lines = deck_text.splitlines(
        keepends=True
    )

    matches = []

    for index, line in enumerate(
        lines
    ):
        stripped = line.strip()

        if stripped.startswith("**"):
            continue

        fields = [
            field.strip().upper()
            for field in stripped.split(",")
        ]

        if (
            len(fields) >= 3
            and fields[0] == "EALL"
            and fields[1] == "P"
        ):
            matches.append(index)

    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one EALL pressure "
            f"load, found {len(matches)}."
        )

    index = matches[0]

    newline = (
        "\n"
        if lines[index].endswith("\n")
        else ""
    )

    lines[index] = (
        "EALL,P,"
        f"{pressure_n_mm2:.9f}"
        f"{newline}"
    )

    return "".join(lines)


def build_pressure_envelope_deck(
    source_deck_text: str,
    case: PressureEnvelopeCase,
) -> str:
    deck_text = (
        build_stiffness_sweep_deck(
            source_deck_text,
            case.stiffness_case(),
        )
    )

    return _replace_pressure_load(
        deck_text,
        case.pressure_level.pressure_n_mm2,
    )