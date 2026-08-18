from ball001.design import EvidenceClass
from ball001.panel_candidates import (
    BALL001_PANEL_CANDIDATES,
)


def test_candidate_region_counts() -> None:
    region_counts = [
        candidate.region_count
        for candidate in BALL001_PANEL_CANDIDATES
    ]

    assert region_counts == [8, 12, 18]


def test_region_count_matches_architecture_definition() -> None:
    for candidate in BALL001_PANEL_CANDIDATES:
        assert candidate.region_count == (
            candidate.meridian_count
            * candidate.zone_count
        )


def test_transverse_boundary_count_matches_zone_count() -> None:
    for candidate in BALL001_PANEL_CANDIDATES:
        assert candidate.transverse_boundary_count == (
            candidate.zone_count - 1
        )


def test_all_candidates_remain_pending() -> None:
    assert all(
        candidate.evidence == EvidenceClass.PENDING
        for candidate in BALL001_PANEL_CANDIDATES
    )


def test_candidate_names_are_unique() -> None:
    names = {
        candidate.name
        for candidate in BALL001_PANEL_CANDIDATES
    }

    assert len(names) == len(BALL001_PANEL_CANDIDATES)