import pytest

from ball001.design import BALL_001
from ball001.sensitivity import run_seam_sensitivity

WIDTHS_MM = (
    1.5,
    2.5,
    3.5,
)

DEPTHS_MM = (
    0.2,
    0.4,
    0.6,
)


def test_sensitivity_study_has_nine_cases() -> None:
    results = run_seam_sensitivity(
        BALL_001,
        WIDTHS_MM,
        DEPTHS_MM,
    )

    assert len(results) == 9


def test_baseline_seam_case_is_present() -> None:
    results = run_seam_sensitivity(
        BALL_001,
        WIDTHS_MM,
        DEPTHS_MM,
    )

    baseline = [
        result
        for result in results
        if result.width_m == pytest.approx(0.0025)
        and result.depth_m == pytest.approx(0.0004)
    ]

    assert len(baseline) == 1


def test_removed_mass_increases_with_width() -> None:
    results = run_seam_sensitivity(
        BALL_001,
        WIDTHS_MM,
        (0.4,),
    )

    removed_masses = [
        result.removed_mass_kg
        for result in results
    ]

    assert removed_masses == sorted(removed_masses)


def test_removed_mass_increases_with_depth() -> None:
    results = run_seam_sensitivity(
        BALL_001,
        (2.5,),
        DEPTHS_MM,
    )

    removed_masses = [
        result.removed_mass_kg
        for result in results
    ]

    assert removed_masses == sorted(removed_masses)


def test_skin_thickness_violation_is_rejected() -> None:
    with pytest.raises(ValueError):
        run_seam_sensitivity(
            BALL_001,
            widths_mm=(2.5,),
            depths_mm=(0.8,),
        )