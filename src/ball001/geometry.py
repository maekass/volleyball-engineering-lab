from math import pi


def radius_from_circumference(circumference_m: float) -> float:
    if circumference_m <= 0:
        raise ValueError("Circumference must be positive.")

    return circumference_m / (2.0 * pi)


def diameter_from_radius(radius_m: float) -> float:
    if radius_m <= 0:
        raise ValueError("Radius must be positive.")

    return 2.0 * radius_m


def spherical_shell_volume(
    outer_radius_m: float,
    thickness_m: float,
) -> float:
    if outer_radius_m <= 0:
        raise ValueError("Outer radius must be positive.")

    if thickness_m <= 0:
        raise ValueError("Thickness must be positive.")

    inner_radius_m = outer_radius_m - thickness_m

    if inner_radius_m <= 0:
        raise ValueError("Layer thickness exceeds available radius.")

    return (4.0 / 3.0) * pi * (
        outer_radius_m**3 - inner_radius_m**3
    )
