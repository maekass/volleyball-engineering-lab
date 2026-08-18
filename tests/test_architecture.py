import pytest

from ball001.architecture import (
    CONTROL_TOPOLOGIES,
    calculate_architecture_result,
    region_count_for_topology,
)
from ball001.design import BALL_001
from ball001.topology import (
    TOPOLOGY_1_SEAM,
    TOPOLOGY_2_SEAM,
    TOPOLOGY_3_SEAM,
)


def test_control_region_counts() -> None:
    assert region_count_for_topology(TOPOLOGY_1_SEAM) == 2
    assert region_count_for_topology(TOPOLOGY_2_SEAM) == 4
    assert region_count_for_topology(TOPOLOGY_3_SEAM) == 8


def test_control_topologies_contains_three_cases() -> None:
    assert len(CONTROL_TOPOLOGIES) == 3


def test_total_seam_length_increases_with_seam_count() -> None:
    results = [
        calculate_architecture_result(
            BALL_001,
            topology,
        )
        for topology in CONTROL_TOPOLOGIES
    ]

    seam_lengths = [
        result.total_seam_length_m
        for result in results
    ]

    assert seam_lengths == sorted(seam_lengths)


def test_three_seam_length_is_three_times_one_seam() -> None:
    one_seam = calculate_architecture_result(
        BALL_001,
        TOPOLOGY_1_SEAM,
    )

    three_seam = calculate_architecture_result(
        BALL_001,
        TOPOLOGY_3_SEAM,
    )

    assert three_seam.total_seam_length_m == pytest.approx(
        3.0 * one_seam.total_seam_length_m
    )