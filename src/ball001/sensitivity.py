from dataclasses import dataclass

from ball001.design import BallDesign, EvidenceClass
from ball001.mass import calculate_total_mass
from ball001.surface import SeamSpec
from ball001.surface_mass import calculate_groove_removed_mass

MM_PER_M = 1000.0


@dataclass(frozen=True)
class SeamSensitivityResult:
    width_m: float
    depth_m: float
    removed_mass_kg: float
    adjusted_mass_kg: float
    target_delta_kg: float


def run_seam_sensitivity(
    design: BallDesign,
    widths_mm: tuple[float, ...],
    depths_mm: tuple[float, ...],
) -> tuple[SeamSensitivityResult, ...]:
    baseline_mass_kg = calculate_total_mass(design)
    skin_thickness_m = design.layers[0].thickness_m

    results = []

    for depth_mm in depths_mm:
        depth_m = depth_mm / MM_PER_M

        if depth_m <= 0:
            raise ValueError("Seam depth must be positive.")

        if depth_m >= skin_thickness_m:
            raise ValueError(
                "Seam depth must remain below skin thickness."
            )

        for width_mm in widths_mm:
            width_m = width_mm / MM_PER_M

            if width_m <= 0:
                raise ValueError("Seam width must be positive.")

            seam = SeamSpec(
                width_m=width_m,
                depth_m=depth_m,
                evidence=EvidenceClass.PENDING,
                note="Sensitivity-study computational input.",
            )

            removed_mass_kg = calculate_groove_removed_mass(
                design,
                seam,
            )

            adjusted_mass_kg = baseline_mass_kg - removed_mass_kg
            target_delta_kg = adjusted_mass_kg - design.target_mass_kg

            results.append(
                SeamSensitivityResult(
                    width_m=width_m,
                    depth_m=depth_m,
                    removed_mass_kg=removed_mass_kg,
                    adjusted_mass_kg=adjusted_mass_kg,
                    target_delta_kg=target_delta_kg,
                )
            )

    return tuple(results)