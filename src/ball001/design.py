from dataclasses import dataclass
from enum import StrEnum


class EvidenceClass(StrEnum):
    BENCHMARK = "BENCHMARK"
    LITERATURE = "LITERATURE"
    TARGET = "TARGET"
    SIMULATED = "SIMULATED"
    MEASURED = "MEASURED"
    PENDING = "PENDING"


@dataclass(frozen=True)
class Layer:
    name: str
    thickness_m: float
    density_kg_m3: float
    evidence: EvidenceClass
    note: str


@dataclass(frozen=True)
class BallDesign:
    name: str
    circumference_m: float
    target_mass_kg: float
    layers: tuple[Layer, ...]


BALL_001 = BallDesign(
    name="BALL 001",
    circumference_m=0.660,
    target_mass_kg=0.270,
    layers=(
        Layer(
            name="skin",
            thickness_m=0.0008,
            density_kg_m3=1200.0,
            evidence=EvidenceClass.PENDING,
            note="Provisional computational design variable.",
        ),
        Layer(
            name="compliance",
            thickness_m=0.0010,
            density_kg_m3=250.0,
            evidence=EvidenceClass.PENDING,
            note="Provisional computational design variable.",
        ),
        Layer(
            name="reinforcement",
            thickness_m=0.00025,
            density_kg_m3=1100.0,
            evidence=EvidenceClass.PENDING,
            note="Provisional computational design variable.",
        ),
        Layer(
            name="bladder",
            thickness_m=0.0006,
            density_kg_m3=920.0,
            evidence=EvidenceClass.PENDING,
            note="Provisional computational design variable.",
        ),
    ),
)