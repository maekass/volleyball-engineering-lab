"""Mechanistic 1D polymer diffusion and intermittent-contact screening.

Units: length cm; time h; concentration microgram/cm^3; diffusivity cm^2/h;
surface transfer coefficient cm/h; cumulative release microgram/cm^2.

Models are idealized, calibration-ready computational hypotheses, not
product-specific validated exposure predictions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class SlabMaterial:
    thickness_cm: float
    diffusivity_cm2_h: float
    initial_concentration_ug_cm3: float

    def __post_init__(self) -> None:
        values = (
            self.thickness_cm,
            self.diffusivity_cm2_h,
            self.initial_concentration_ug_cm3,
        )
        if not all(math.isfinite(x) for x in values):
            raise ValueError("Slab parameters must be finite.")
        if self.thickness_cm <= 0 or self.diffusivity_cm2_h <= 0:
            raise ValueError("Thickness and diffusivity must be positive.")
        if self.initial_concentration_ug_cm3 < 0:
            raise ValueError("Initial concentration must be non-negative.")


@dataclass(frozen=True)
class ContactInterval:
    duration_h: float
    in_contact: bool

    def __post_init__(self) -> None:
        if not math.isfinite(self.duration_h) or self.duration_h < 0:
            raise ValueError("Contact duration must be finite and non-negative.")


@dataclass(frozen=True)
class TransportResult:
    released_ug_cm2: float
    remaining_ug_cm2: float
    initial_ug_cm2: float
    mass_balance_error_ug_cm2: float
    steps: int


def ideal_sink_release_fraction(
    thickness_cm: float,
    diffusivity_cm2_h: float,
    time_h: float,
) -> float:
    """Fickian planar slab: one impermeable face, one perfect-sink face.

    Initially uniform concentration, constant D, no swelling or reaction.
    Uses the short-time asymptote for small Fourier number and the
    eigenfunction series otherwise. This is NOT a skin-uptake model.
    """

    if not all(
        math.isfinite(v) for v in (thickness_cm, diffusivity_cm2_h, time_h)
    ):
        raise ValueError("Inputs must be finite.")
    if thickness_cm <= 0 or diffusivity_cm2_h <= 0 or time_h < 0:
        raise ValueError("Invalid slab geometry, diffusivity, or time.")
    if time_h == 0:
        return 0.0
    fourier = diffusivity_cm2_h * time_h / (thickness_cm**2)
    if fourier < 0.02:
        return min(1.0, 2.0 * math.sqrt(fourier / math.pi))
    remaining = sum(
        8.0
        / (math.pi**2 * (2 * n + 1) ** 2)
        * math.exp(-((2 * n + 1) ** 2) * math.pi**2 * fourier / 4.0)
        for n in range(200)
    )
    return max(0.0, min(1.0, 1.0 - remaining))


def ideal_sink_release_ug_cm2(material: SlabMaterial, time_h: float) -> float:
    return (
        material.initial_concentration_ug_cm3
        * material.thickness_cm
        * ideal_sink_release_fraction(
            material.thickness_cm, material.diffusivity_cm2_h, time_h
        )
    )


def simulate_intermittent_contact(
    material: SlabMaterial,
    intervals: tuple[ContactInterval, ...],
    *,
    transfer_coefficient_cm_h: float,
    cells: int = 40,
    max_steps: int = 250_000,
) -> TransportResult:
    """Finite-volume mass-conserving 1D diffusion with a Robin-like sink.

    Left face: impermeable. Right face: flux = k * surface-cell C during
    contact, zero otherwise. The last cell is a volume-average approximation
    to the surface concentration; mesh convergence is mandatory.

    The surface sink is *migration from the polymer*, not dermal absorption.
    No replenishment of an external liquid film or back-partition is modeled.
    """

    if not math.isfinite(transfer_coefficient_cm_h):
        raise ValueError("Transfer coefficient must be finite.")
    if transfer_coefficient_cm_h < 0:
        raise ValueError("Transfer coefficient cannot be negative.")
    if cells < 4 or max_steps <= 0:
        raise ValueError("At least four cells and a positive step cap required.")
    dx = material.thickness_cm / cells
    d = material.diffusivity_cm2_h
    c = [material.initial_concentration_ug_cm3] * cells
    initial = material.initial_concentration_ug_cm3 * material.thickness_cm
    released = 0.0
    steps = 0
    for interval in intervals:
        if interval.duration_h == 0:
            continue
        k = transfer_coefficient_cm_h if interval.in_contact else 0.0
        max_dt = 0.4 / (2.0 * d / dx**2 + k / dx)
        n = math.ceil(interval.duration_h / max_dt)
        if steps + n > max_steps:
            raise ValueError("Time-step cap exceeded; refine study settings.")
        dt = interval.duration_h / n
        for _ in range(n):
            delta = [0.0] * cells
            for j in range(cells - 1):
                flux = d * (c[j] - c[j + 1]) / dx
                delta[j] -= flux * dt / dx
                delta[j + 1] += flux * dt / dx
            outflux = k * c[-1]
            delta[-1] -= outflux * dt / dx
            c = [max(0.0, x + change) for x, change in zip(c, delta)]
            released += outflux * dt
        steps += n
    remaining = sum(c) * dx
    return TransportResult(
        released_ug_cm2=released,
        remaining_ug_cm2=remaining,
        initial_ug_cm2=initial,
        mass_balance_error_ug_cm2=initial - remaining - released,
        steps=steps,
    )


@dataclass(frozen=True)
class CalibrationObservation:
    """Measured time-series datum; must be linked to separately audited data."""

    time_h: float
    cumulative_release_ug_cm2: float
    evidence_record_id: str

    def __post_init__(self) -> None:
        if not self.evidence_record_id:
            raise ValueError("Calibration observation requires evidence ID.")
        if not all(
            math.isfinite(v)
            for v in (self.time_h, self.cumulative_release_ug_cm2)
        ):
            raise ValueError("Calibration observation must be finite.")
        if self.time_h <= 0 or self.cumulative_release_ug_cm2 < 0:
            raise ValueError("Invalid calibration time or release.")


@dataclass(frozen=True)
class CalibrationResult:
    diffusivity_cm2_h: float
    train_rmse_ug_cm2: float
    holdout_rmse_ug_cm2: float
    at_grid_boundary: bool
    weak_identifiability: bool
    source_evidence_ids: tuple[str, ...]
    model_assumptions: str = "constant-D, uniform-C0, one-face perfect sink"


def fit_ideal_sink_diffusivity(
    observations: tuple[CalibrationObservation, ...],
    *,
    thickness_cm: float,
    measured_initial_concentration_ug_cm3: float,
    min_diffusivity_cm2_h: float,
    max_diffusivity_cm2_h: float,
    grid_points: int = 151,
) -> CalibrationResult:
    """Fit D to early time points; hold out the last time point.

    Requires a separately measured initial concentration. Does not fit C0
    and D simultaneously because they can be poorly identifiable.
    The caller must independently audit observation evidence IDs.
    """

    if len(observations) < 4:
        raise ValueError("At least four time points (three train, one holdout).")
    ordered = sorted(observations, key=lambda x: x.time_h)
    if len({o.time_h for o in ordered}) != len(ordered):
        raise ValueError("Calibration time points must be distinct.")
    if any(
        ordered[i].cumulative_release_ug_cm2
        > ordered[i + 1].cumulative_release_ug_cm2
        for i in range(len(ordered) - 1)
    ):
        raise ValueError("Cumulative release must be non-decreasing.")
    if (
        not all(
            math.isfinite(x)
            for x in (
                thickness_cm,
                measured_initial_concentration_ug_cm3,
                min_diffusivity_cm2_h,
                max_diffusivity_cm2_h,
            )
        )
        or thickness_cm <= 0
        or measured_initial_concentration_ug_cm3 <= 0
        or min_diffusivity_cm2_h <= 0
        or max_diffusivity_cm2_h <= min_diffusivity_cm2_h
        or grid_points < 5
    ):
        raise ValueError("Invalid measured content, slab geometry, or fit grid.")
    reservoir = thickness_cm * measured_initial_concentration_ug_cm3
    if any(o.cumulative_release_ug_cm2 > reservoir for o in ordered):
        raise ValueError("Observed release exceeds initial chemical inventory.")
    low = math.log10(min_diffusivity_cm2_h)
    high = math.log10(max_diffusivity_cm2_h)
    grid = [
        10 ** (low + (high - low) * i / (grid_points - 1))
        for i in range(grid_points)
    ]
    training, holdout = ordered[:-1], ordered[-1]

    def error(d: float, subset: list[CalibrationObservation]) -> float:
        model = SlabMaterial(
            thickness_cm, d, measured_initial_concentration_ug_cm3
        )
        return sum(
            (
                ideal_sink_release_ug_cm2(model, item.time_h)
                - item.cumulative_release_ug_cm2
            )
            ** 2
            for item in subset
        )

    losses = [error(d, training) for d in grid]
    best_idx = min(range(len(grid)), key=lambda i: losses[i])
    best_d = grid[best_idx]
    best_loss = losses[best_idx]
    # A broad near-optimal profile is a warning, not a confidence interval.
    near = [
        d for d, loss in zip(grid, losses)
        if loss <= best_loss * 1.05 + 1e-14
    ]
    return CalibrationResult(
        diffusivity_cm2_h=best_d,
        train_rmse_ug_cm2=math.sqrt(best_loss / len(training)),
        holdout_rmse_ug_cm2=math.sqrt(error(best_d, [holdout])),
        at_grid_boundary=best_idx in (0, len(grid) - 1),
        weak_identifiability=max(near) / min(near) >= 10.0,
        source_evidence_ids=tuple(
            dict.fromkeys(item.evidence_record_id for item in ordered)
        ),
    )


@dataclass(frozen=True)
class UncertaintyEnvelope:
    minimum_release_ug_cm2: float
    maximum_release_ug_cm2: float


def bounded_ideal_sink_release(
    *,
    thickness_cm: float,
    time_h: float,
    diffusivity_range_cm2_h: tuple[float, float],
    concentration_range_ug_cm3: tuple[float, float],
) -> UncertaintyEnvelope:
    """Deterministic parameter bounds, not a statistical confidence interval."""

    dlo, dhi = diffusivity_range_cm2_h
    clo, chi = concentration_range_ug_cm3
    if dlo > dhi or clo > chi:
        raise ValueError("Bounds must be ordered.")
    low = ideal_sink_release_ug_cm2(
        SlabMaterial(thickness_cm, dlo, clo), time_h
    )
    high = ideal_sink_release_ug_cm2(
        SlabMaterial(thickness_cm, dhi, chi), time_h
    )
    return UncertaintyEnvelope(low, high)
