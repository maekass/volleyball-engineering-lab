from dataclasses import dataclass

from ball001.cad import build_layer_solids
from ball001.design import BallDesign
from ball001.mass import calculate_total_mass
from ball001.surface import SeamSpec
from ball001.surface_cad import build_grooved_skin

MM3_PER_M3 = 1_000_000_000.0


@dataclass(frozen=True)
class SurfaceAdjustedMassResult:
    baseline_mass_kg: float
    removed_skin_mass_kg: float
    adjusted_mass_kg: float


def calculate_groove_removed_mass(
    design: BallDesign,
    seam: SeamSpec,
) -> float:
    skin = design.layers[0]

    original_skin = build_layer_solids(design)[0].solid
    grooved_skin = build_grooved_skin(design, seam)

    removed_volume_mm3 = (
        original_skin.val().Volume()
        - grooved_skin.val().Volume()
    )

    removed_volume_m3 = removed_volume_mm3 / MM3_PER_M3

    return removed_volume_m3 * skin.density_kg_m3


def calculate_surface_adjusted_mass(
    design: BallDesign,
    seam: SeamSpec,
) -> SurfaceAdjustedMassResult:
    baseline_mass_kg = calculate_total_mass(design)
    removed_skin_mass_kg = calculate_groove_removed_mass(
        design,
        seam,
    )

    adjusted_mass_kg = baseline_mass_kg - removed_skin_mass_kg

    return SurfaceAdjustedMassResult(
        baseline_mass_kg=baseline_mass_kg,
        removed_skin_mass_kg=removed_skin_mass_kg,
        adjusted_mass_kg=adjusted_mass_kg,
    )