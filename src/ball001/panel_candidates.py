from dataclasses import dataclass

from ball001.design import EvidenceClass


@dataclass(frozen=True)
class CandidatePanelArchitecture:
    name: str
    meridian_count: int
    zone_count: int
    evidence: EvidenceClass
    note: str

    @property
    def transverse_boundary_count(self) -> int:
        return self.zone_count - 1

    @property
    def region_count(self) -> int:
        return self.meridian_count * self.zone_count


BALL001_8_REGION = CandidatePanelArchitecture(
    name="BALL 001 — 8-region candidate",
    meridian_count=4,
    zone_count=2,
    evidence=EvidenceClass.PENDING,
    note=(
        "Lower-complexity volleyball-style computational "
        "candidate. Exact panel geometry is not finalized."
    ),
)


BALL001_12_REGION = CandidatePanelArchitecture(
    name="BALL 001 — 12-region candidate",
    meridian_count=4,
    zone_count=3,
    evidence=EvidenceClass.PENDING,
    note=(
        "Intermediate-complexity volleyball-style computational "
        "candidate. Exact panel geometry is not finalized."
    ),
)


BALL001_18_REGION = CandidatePanelArchitecture(
    name="BALL 001 — 18-region candidate",
    meridian_count=6,
    zone_count=3,
    evidence=EvidenceClass.PENDING,
    note=(
        "Higher-complexity BALL 001 control candidate. "
        "It does not reproduce proprietary V200W panel geometry."
    ),
)


BALL001_PANEL_CANDIDATES = (
    BALL001_8_REGION,
    BALL001_12_REGION,
    BALL001_18_REGION,
)