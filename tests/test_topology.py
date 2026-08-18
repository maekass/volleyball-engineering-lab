import pytest

from ball001.cad import build_layer_solids
from ball001.design import BALL_001
from ball001.surface import BALL_001_SEAM
from ball001.surface_cad import build_grooved_skin
from ball001.topology import (
    TOPOLOGY_1_SEAM,
    TOPOLOGY_2_SEAM,
    TOPOLOGY_3_SEAM,
    SeamTopology,
)
from ball001.topology_cad import build_topology_grooved_skin


def test_topology_seam_counts() -> None:
    assert len(TOPOLOGY_1_SEAM.seams) == 1
    assert len(TOPOLOGY_2_SEAM.seams) == 2
    assert len(TOPOLOGY_3_SEAM.seams) == 3


def test_topology_names_are_unique() -> None:
    names = {
        TOPOLOGY_1_SEAM.name,
        TOPOLOGY_2_SEAM.name,
        TOPOLOGY_3_SEAM.name,
    }

    assert len(names) == 3


def test_three_seam_topology_has_unique_orientations() -> None:
    orientations = {
        (
            seam.rotation_x_deg,
            seam.rotation_y_deg,
        )
        for seam in TOPOLOGY_3_SEAM.seams
    }

    assert len(orientations) == 3


def test_one_seam_topology_matches_original_groove() -> None:
    original_grooved_skin = build_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
    )

    topology_grooved_skin = build_topology_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
        TOPOLOGY_1_SEAM,
    )

    assert topology_grooved_skin.val().Volume() == pytest.approx(
        original_grooved_skin.val().Volume(),
        rel=1e-8,
    )


def test_more_seams_remove_more_skin_volume() -> None:
    one_seam = build_topology_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
        TOPOLOGY_1_SEAM,
    )

    two_seams = build_topology_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
        TOPOLOGY_2_SEAM,
    )

    three_seams = build_topology_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
        TOPOLOGY_3_SEAM,
    )

    assert three_seams.val().Volume() < two_seams.val().Volume()
    assert two_seams.val().Volume() < one_seam.val().Volume()


def test_two_seam_overlap_prevents_double_counting() -> None:
    original_skin = build_layer_solids(BALL_001)[0].solid
    original_volume = original_skin.val().Volume()

    two_seams = build_topology_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
        TOPOLOGY_2_SEAM,
    )

    two_removed_volume = (
        original_volume
        - two_seams.val().Volume()
    )

    individual_removed_volume = 0.0

    for seam in TOPOLOGY_2_SEAM.seams:
        single_topology = SeamTopology(
            name=f"single_{seam.name}",
            seams=(seam,),
        )

        single_grooved_skin = build_topology_grooved_skin(
            BALL_001,
            BALL_001_SEAM,
            single_topology,
        )

        individual_removed_volume += (
            original_volume
            - single_grooved_skin.val().Volume()
        )

    assert two_removed_volume < individual_removed_volume


def test_three_seam_overlap_prevents_triple_counting() -> None:
    original_skin = build_layer_solids(BALL_001)[0].solid
    original_volume = original_skin.val().Volume()

    three_seams = build_topology_grooved_skin(
        BALL_001,
        BALL_001_SEAM,
        TOPOLOGY_3_SEAM,
    )

    three_removed_volume = (
        original_volume
        - three_seams.val().Volume()
    )

    individual_removed_volume = 0.0

    for seam in TOPOLOGY_3_SEAM.seams:
        single_topology = SeamTopology(
            name=f"single_{seam.name}",
            seams=(seam,),
        )

        single_grooved_skin = build_topology_grooved_skin(
            BALL_001,
            BALL_001_SEAM,
            single_topology,
        )

        individual_removed_volume += (
            original_volume
            - single_grooved_skin.val().Volume()
        )

    assert three_removed_volume < individual_removed_volume


def test_all_topology_volumes_remain_below_original_skin() -> None:
    original_skin = build_layer_solids(BALL_001)[0].solid
    original_volume = original_skin.val().Volume()

    for topology in (
        TOPOLOGY_1_SEAM,
        TOPOLOGY_2_SEAM,
        TOPOLOGY_3_SEAM,
    ):
        grooved_skin = build_topology_grooved_skin(
            BALL_001,
            BALL_001_SEAM,
            topology,
        )

        assert 0 < grooved_skin.val().Volume() < original_volume