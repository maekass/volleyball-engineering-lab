from math import isclose, pi

import pytest

from ball001.geometry import (
    diameter_from_radius,
    radius_from_circumference,
    spherical_shell_volume,
)


def test_radius_from_circumference() -> None:
    circumference_m = 0.660

    radius_m = radius_from_circumference(circumference_m)

    reconstructed_circumference_m = 2.0 * pi * radius_m

    assert isclose(
        reconstructed_circumference_m,
        circumference_m,
        rel_tol=1e-12,
    )


def test_diameter_is_twice_radius() -> None:
    assert diameter_from_radius(0.105) == pytest.approx(0.210)


def test_shell_volume_is_positive() -> None:
    volume_m3 = spherical_shell_volume(
        outer_radius_m=0.105,
        thickness_m=0.001,
    )

    assert volume_m3 > 0


def test_negative_circumference_is_rejected() -> None:
    with pytest.raises(ValueError):
        radius_from_circumference(-0.660)
