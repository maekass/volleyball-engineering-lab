"""Synthetic analytical/numerical checks, not experimental validation."""

from __future__ import annotations

import math

import pytest

from ball001.diffusion_transport import (
    CalibrationObservation,
    ContactInterval,
    SlabMaterial,
    bounded_ideal_sink_release,
    fit_ideal_sink_diffusivity,
    ideal_sink_release_fraction,
    ideal_sink_release_ug_cm2,
    simulate_intermittent_contact,
)


def test_ideal_sink_release_starts_at_zero() -> None:
    assert ideal_sink_release_fraction(0.1, 1e-5, 0.0) == 0.0


def test_ideal_sink_release_is_bounded_and_monotonic() -> None:
    times = (0.0, 0.1, 1.0, 10.0, 100.0)
    fractions = [ideal_sink_release_fraction(0.1, 1e-5, t) for t in times]
    assert fractions == sorted(fractions)
    assert all(0.0 <= f <= 1.0 for f in fractions)


def test_early_time_matches_semi_infinite_solution() -> None:
    fourier = 0.001
    fraction = ideal_sink_release_fraction(1.0, 0.001, 1.0)
    assert fraction == pytest.approx(2 * math.sqrt(fourier / math.pi))


def test_ideal_sink_respects_inventory() -> None:
    material = SlabMaterial(0.1, 1e-5, 100.0)
    assert ideal_sink_release_ug_cm2(material, 1000.0) <= 10.0


def test_zero_contact_has_zero_release_and_conserves_mass() -> None:
    material = SlabMaterial(0.1, 1e-4, 100.0)
    result = simulate_intermittent_contact(
        material, (ContactInterval(1.0, False),),
        transfer_coefficient_cm_h=0.01,
    )
    assert result.released_ug_cm2 == 0.0
    assert result.remaining_ug_cm2 == pytest.approx(result.initial_ug_cm2)
    assert result.mass_balance_error_ug_cm2 == pytest.approx(0.0, abs=1e-9)


def test_intermitttent_contact_releases_less_than_continuous() -> None:
    material = SlabMaterial(0.1, 1e-4, 100.0)
    intermittent = simulate_intermittent_contact(
        material,
        (
            ContactInterval(0.5, True),
            ContactInterval(0.5, False),
            ContactInterval(0.5, True),
        ),
        transfer_coefficient_cm_h=0.02,
    )
    continuous = simulate_intermittent_contact(
        material, (ContactInterval(1.5, True),),
        transfer_coefficient_cm_h=0.02,
    )
    assert 0 < intermittent.released_ug_cm2 < continuous.released_ug_cm2
    assert intermittent.mass_balance_error_ug_cm2 == pytest.approx(
        0.0, abs=1e-8
    )


def test_finite_volume_mesh_refinement_converges() -> None:
    material = SlabMaterial(0.1, 1e-4, 100.0)
    intervals = (ContactInterval(0.75, True),)
    values = [
        simulate_intermittent_contact(
            material, intervals, transfer_coefficient_cm_h=0.02, cells=n
        ).released_ug_cm2
        for n in (20, 40, 80)
    ]
    assert abs(values[2] - values[1]) < abs(values[1] - values[0])


def test_fit_recovers_known_synthetic_diffusivity() -> None:
    true_d = 1e-5
    material = SlabMaterial(0.1, true_d, 100.0)
    observations = tuple(
        CalibrationObservation(
            t, ideal_sink_release_ug_cm2(material, t), "SYNTHETIC-TEST"
        )
        for t in (0.5, 1.0, 2.0, 4.0, 8.0)
    )
    fit = fit_ideal_sink_diffusivity(
        observations,
        thickness_cm=material.thickness_cm,
        measured_initial_concentration_ug_cm3=100.0,
        min_diffusivity_cm2_h=1e-7,
        max_diffusivity_cm2_h=1e-3,
        grid_points=161,
    )
    assert fit.diffusivity_cm2_h == pytest.approx(true_d, rel=0.001)
    assert fit.holdout_rmse_ug_cm2 < 1e-8
    assert not fit.at_grid_boundary


def test_fit_requires_multiple_distinct_times() -> None:
    observations = tuple(
        CalibrationObservation(1.0, 1.0, "SYNTHETIC-TEST")
        for _ in range(4)
    )
    with pytest.raises(ValueError, match="distinct"):
        fit_ideal_sink_diffusivity(
            observations,
            thickness_cm=0.1,
            measured_initial_concentration_ug_cm3=100.0,
            min_diffusivity_cm2_h=1e-7,
            max_diffusivity_cm2_h=1e-3,
        )


def test_uncertainty_envelope_is_ordered() -> None:
    result = bounded_ideal_sink_release(
        thickness_cm=0.1,
        time_h=1.0,
        diffusivity_range_cm2_h=(1e-7, 1e-5),
        concentration_range_ug_cm3=(10.0, 100.0),
    )
    assert result.minimum_release_ug_cm2 <= result.maximum_release_ug_cm2


def test_nonfinite_parameters_rejected() -> None:
    with pytest.raises(ValueError, match="finite"):
        SlabMaterial(0.1, float("nan"), 100.0)
