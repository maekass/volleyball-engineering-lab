from ball001.design import BALL_001
from ball001.mass import calculate_layer_masses, calculate_total_mass


def test_every_layer_has_positive_mass() -> None:
    results = calculate_layer_masses(BALL_001)

    assert all(result.mass_kg > 0 for result in results)


def test_layer_count_matches_design() -> None:
    results = calculate_layer_masses(BALL_001)

    assert len(results) == len(BALL_001.layers)


def test_total_mass_equals_sum_of_layers() -> None:
    results = calculate_layer_masses(BALL_001)

    expected_mass_kg = sum(result.mass_kg for result in results)

    assert calculate_total_mass(BALL_001) == expected_mass_kg
