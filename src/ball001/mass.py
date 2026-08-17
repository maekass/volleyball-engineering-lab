from dataclasses import dataclass

from ball001.design import BallDesign
from ball001.geometry import radius_from_circumference, spherical_shell_volume


@dataclass(frozen=True)
class LayerMassResult:
    name: str
    outer_radius_m: float
    inner_radius_m: float
    volume_m3: float
    mass_kg: float


def calculate_layer_masses(
    design: BallDesign,
) -> tuple[LayerMassResult, ...]:
    outer_radius_m = radius_from_circumference(design.circumference_m)

    results = []

    for layer in design.layers:
        volume_m3 = spherical_shell_volume(
            outer_radius_m=outer_radius_m,
            thickness_m=layer.thickness_m,
        )

        mass_kg = volume_m3 * layer.density_kg_m3
        inner_radius_m = outer_radius_m - layer.thickness_m

        results.append(
            LayerMassResult(
                name=layer.name,
                outer_radius_m=outer_radius_m,
                inner_radius_m=inner_radius_m,
                volume_m3=volume_m3,
                mass_kg=mass_kg,
            )
        )

        outer_radius_m = inner_radius_m

    return tuple(results)


def calculate_total_mass(design: BallDesign) -> float:
    return sum(
        result.mass_kg
        for result in calculate_layer_masses(design)
    )
