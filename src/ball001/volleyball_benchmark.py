from dataclasses import dataclass

from ball001.design import EvidenceClass


@dataclass(frozen=True)
class FIVBBallStandard:
    circumference_min_m: float
    circumference_max_m: float
    mass_min_kg: float
    mass_max_kg: float
    internal_pressure_min_pa: float
    internal_pressure_max_pa: float
    evidence: EvidenceClass


@dataclass(frozen=True)
class VolleyballBenchmark:
    name: str
    panel_count: int
    construction: str
    surface: str
    material: str
    seam_width_m: float | None
    seam_depth_m: float | None
    evidence: EvidenceClass
    note: str


FIVB_INDOOR_BALL = FIVBBallStandard(
    circumference_min_m=0.650,
    circumference_max_m=0.670,
    mass_min_kg=0.260,
    mass_max_kg=0.280,
    internal_pressure_min_pa=29_430.0,
    internal_pressure_max_pa=31_882.0,
    evidence=EvidenceClass.BENCHMARK,
)


V200W_BENCHMARK = VolleyballBenchmark(
    name="Mikasa V200W",
    panel_count=18,
    construction="Laminated",
    surface="Double Dimple Microfiber",
    material="Microfiber + PU",
    seam_width_m=None,
    seam_depth_m=None,
    evidence=EvidenceClass.BENCHMARK,
    note=(
        "Public benchmark information only. Exact panel-boundary "
        "and seam dimensions are not assumed."
    ),
)