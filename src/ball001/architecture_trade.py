from dataclasses import dataclass

from ball001.architecture import calculate_architecture_result
from ball001.cad import build_layer_solids
from ball001.design import BallDesign
from ball001.mass import calculate_total_mass
from ball001.surface import SeamSpec
from ball001.topology import SeamTopology
from ball001.topology_cad import build_topology_grooved_skin

MM3_PER_M3 = 1_000_000_000.0


@dataclass(frozen=True)
class ArchitectureTradeResult:
    name: str
    seam_count: int
    region_count: int
    total_seam_length_m: float
    seam_length_per_area_m_m2: float
    removed_skin_mass_kg: float
    adjusted_mass_kg: float
    target_delta_kg: float


def calculate_architecture_trade_result(
    design: BallDesign,
    seam: SeamSpec,
    topology: SeamTopology,
) -> ArchitectureTradeResult:
    architecture = calculate_architecture_result(
        design,
        topology,
    )

    skin = design.layers[0]

    original_skin = build_layer_solids(design)[0].solid
    grooved_skin = build_topology_grooved_skin(
        design,
        seam,
        topology,
    )

    removed_volume_mm3 = (
        original_skin.val().Volume()
        - grooved_skin.val().Volume()
    )

    removed_volume_m3 = (
        removed_volume_mm3
        / MM3_PER_M3
    )

    removed_skin_mass_kg = (
        removed_volume_m3
        * skin.density_kg_m3
    )

    baseline_mass_kg = calculate_total_mass(design)

    adjusted_mass_kg = (
        baseline_mass_kg
        - removed_skin_mass_kg
    )

    target_delta_kg = (
        adjusted_mass_kg
        - design.target_mass_kg
    )

    return ArchitectureTradeResult(
        name=architecture.name,
        seam_count=architecture.seam_count,
        region_count=architecture.region_count,
        total_seam_length_m=architecture.total_seam_length_m,
        seam_length_per_area_m_m2=(
            architecture.seam_length_per_area_m_m2
        ),
        removed_skin_mass_kg=removed_skin_mass_kg,
        adjusted_mass_kg=adjusted_mass_kg,
        target_delta_kg=target_delta_kg,
    )