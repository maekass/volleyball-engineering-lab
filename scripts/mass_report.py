# LESSON 01 PREDICTION
# Expected heaviest layer: skin
# Expected total mass: slightly above 270 g, roughly 275–285 g
#
# Reasoning:
# For thin spherical layers, mass is approximately proportional to
# thickness × density because the layers cover roughly the same surface area.


from ball001.design import BALL_001
from ball001.geometry import diameter_from_radius, radius_from_circumference
from ball001.mass import calculate_layer_masses, calculate_total_mass


def main() -> None:
    radius_m = radius_from_circumference(BALL_001.circumference_m)
    diameter_m = diameter_from_radius(radius_m)

    print(BALL_001.name)
    print("=" * 50)
    print(f"Nominal circumference: {BALL_001.circumference_m * 1000:.2f} mm")
    print(f"Derived radius:        {radius_m * 1000:.2f} mm")
    print(f"Derived diameter:      {diameter_m * 1000:.2f} mm")
    print(f"Target mass:           {BALL_001.target_mass_kg * 1000:.2f} g")

    print()
    print("PROVISIONAL LAYER MASS MODEL")
    print("-" * 50)

    for result in calculate_layer_masses(BALL_001):
        print(f"{result.name:15s}{result.mass_kg * 1000:8.2f} g")

    total_mass_kg = calculate_total_mass(BALL_001)
    delta_kg = total_mass_kg - BALL_001.target_mass_kg

    print("-" * 50)
    print(f"Model estimate:        {total_mass_kg * 1000:.2f} g")
    print(f"Target delta:          {delta_kg * 1000:+.2f} g")

    print()
    print("NOTE: Layer thicknesses and densities are PENDING inputs.")
    print("This output is not a measured or validated BALL 001 result.")


if __name__ == "__main__":
    main()
