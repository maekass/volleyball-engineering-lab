from dataclasses import dataclass
from math import pi

from ball001.design import BallDesign
from ball001.geometry import radius_from_circumference
from ball001.topology import (
    TOPOLOGY_1_SEAM,
    TOPOLOGY_2_SEAM,
    TOPOLOGY_3_SEAM,
    SeamTopology,
)


@dataclass(frozen=True)
class ArchitectureResult:
    name: str
    seam_count: int
    region_count: int
    total_seam_length_m: float
    seam_length_per_area_m_m2: float


def region_count_for_topology(
    topology: SeamTopology,
) -> int:
    seam_count = len(topology.seams)

    region_counts = {
        1: 2,
        2: 4,
        3: 8,
    }

    try:
        return region_counts[seam_count]
    except KeyError as exc:
        raise ValueError(
            "Region count is currently defined only for "
            "the 1-, 2-, and 3-great-circle control topologies."
        ) from exc


def calculate_architecture_result(
    design: BallDesign,
    topology: SeamTopology,
) -> ArchitectureResult:
    radius_m = radius_from_circumference(
        design.circumference_m
    )

    seam_count = len(topology.seams)
    region_count = region_count_for_topology(topology)

    one_great_circle_length_m = 2.0 * pi * radius_m

    total_seam_length_m = (
        seam_count
        * one_great_circle_length_m
    )

    surface_area_m2 = 4.0 * pi * radius_m**2

    seam_length_per_area_m_m2 = (
        total_seam_length_m
        / surface_area_m2
    )

    return ArchitectureResult(
        name=topology.name,
        seam_count=seam_count,
        region_count=region_count,
        total_seam_length_m=total_seam_length_m,
        seam_length_per_area_m_m2=seam_length_per_area_m_m2,
    )


CONTROL_TOPOLOGIES = (
    TOPOLOGY_1_SEAM,
    TOPOLOGY_2_SEAM,
    TOPOLOGY_3_SEAM,
)