from dataclasses import dataclass

from ball001.design import EvidenceClass


@dataclass(frozen=True)
class SeamSpec:
    width_m: float
    depth_m: float
    evidence: EvidenceClass
    note: str


BALL_001_SEAM = SeamSpec(
    width_m=0.0025,
    depth_m=0.0004,
    evidence=EvidenceClass.PENDING,
    note="Provisional computational surface-design variables.",
)