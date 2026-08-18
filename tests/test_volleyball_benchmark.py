from ball001.design import BALL_001, EvidenceClass
from ball001.volleyball_benchmark import (
    FIVB_INDOOR_BALL,
    V200W_BENCHMARK,
)


def test_ball001_circumference_is_inside_fivb_range() -> None:
    assert (
        FIVB_INDOOR_BALL.circumference_min_m
        <= BALL_001.circumference_m
        <= FIVB_INDOOR_BALL.circumference_max_m
    )


def test_ball001_target_mass_is_inside_fivb_range() -> None:
    assert (
        FIVB_INDOOR_BALL.mass_min_kg
        <= BALL_001.target_mass_kg
        <= FIVB_INDOOR_BALL.mass_max_kg
    )


def test_fivb_pressure_range_is_positive() -> None:
    assert FIVB_INDOOR_BALL.internal_pressure_min_pa > 0

    assert (
        FIVB_INDOOR_BALL.internal_pressure_max_pa
        > FIVB_INDOOR_BALL.internal_pressure_min_pa
    )


def test_v200w_is_eighteen_panel_benchmark() -> None:
    assert V200W_BENCHMARK.panel_count == 18


def test_v200w_public_seam_dimensions_remain_unknown() -> None:
    assert V200W_BENCHMARK.seam_width_m is None
    assert V200W_BENCHMARK.seam_depth_m is None


def test_benchmark_evidence_classes() -> None:
    assert FIVB_INDOOR_BALL.evidence == EvidenceClass.BENCHMARK
    assert V200W_BENCHMARK.evidence == EvidenceClass.BENCHMARK