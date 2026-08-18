from dataclasses import dataclass

from ball001.design import EvidenceClass


@dataclass(frozen=True)
class PanelRegionReference:
    name: str


@dataclass(frozen=True)
class PanelArchitectureReference:
    name: str
    panel_count: int
    panel_count_evidence: EvidenceClass
    panel_shape_evidence: EvidenceClass
    seam_geometry_evidence: EvidenceClass
    regions: tuple[PanelRegionReference, ...]
    note: str


V200W_PANEL_REFERENCE = PanelArchitectureReference(
    name="Mikasa V200W reference",
    panel_count=18,
    panel_count_evidence=EvidenceClass.BENCHMARK,
    panel_shape_evidence=EvidenceClass.PENDING,
    seam_geometry_evidence=EvidenceClass.PENDING,
    regions=tuple(
        PanelRegionReference(
            name=f"panel_{index:02d}",
        )
        for index in range(1, 19)
    ),
    note=(
        "The 18-panel count is benchmark information. "
        "Exact panel boundaries and seam dimensions are not "
        "assumed from unavailable geometry."
    ),
)