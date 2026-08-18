from ball001.design import EvidenceClass
from ball001.panel_reference import V200W_PANEL_REFERENCE


def test_v200w_reference_has_eighteen_regions() -> None:
    assert len(V200W_PANEL_REFERENCE.regions) == 18
    assert V200W_PANEL_REFERENCE.panel_count == 18


def test_panel_region_names_are_unique() -> None:
    names = {
        region.name
        for region in V200W_PANEL_REFERENCE.regions
    }

    assert len(names) == 18


def test_panel_count_is_benchmark_evidence() -> None:
    assert (
        V200W_PANEL_REFERENCE.panel_count_evidence
        == EvidenceClass.BENCHMARK
    )


def test_exact_panel_shape_remains_pending() -> None:
    assert (
        V200W_PANEL_REFERENCE.panel_shape_evidence
        == EvidenceClass.PENDING
    )


def test_exact_seam_geometry_remains_pending() -> None:
    assert (
        V200W_PANEL_REFERENCE.seam_geometry_evidence
        == EvidenceClass.PENDING
    )