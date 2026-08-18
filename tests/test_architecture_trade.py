from ball001.architecture import CONTROL_TOPOLOGIES
from ball001.architecture_trade import calculate_architecture_trade_result
from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM


def test_trade_study_has_three_control_cases() -> None:
    results = [
        calculate_architecture_trade_result(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )
        for topology in CONTROL_TOPOLOGIES
    ]

    assert len(results) == 3


def test_removed_mass_increases_with_topology_complexity() -> None:
    results = [
        calculate_architecture_trade_result(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )
        for topology in CONTROL_TOPOLOGIES
    ]

    removed_masses = [
        result.removed_skin_mass_kg
        for result in results
    ]

    assert removed_masses == sorted(removed_masses)


def test_adjusted_mass_decreases_with_more_seams() -> None:
    results = [
        calculate_architecture_trade_result(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )
        for topology in CONTROL_TOPOLOGIES
    ]

    adjusted_masses = [
        result.adjusted_mass_kg
        for result in results
    ]

    assert adjusted_masses == sorted(
        adjusted_masses,
        reverse=True,
    )


def test_region_count_increases_with_control_complexity() -> None:
    results = [
        calculate_architecture_trade_result(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )
        for topology in CONTROL_TOPOLOGIES
    ]

    region_counts = [
        result.region_count
        for result in results
    ]

    assert region_counts == [2, 4, 8]