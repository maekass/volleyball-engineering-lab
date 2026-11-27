"""Geometry for the 2026–27 rule cycle and positional jump-load audits."""

from __future__ import annotations

from decimal import Decimal

import numpy as np
import pandas as pd
import pytest
from engines.dvw_rule_simulator import (
    CENTER_LINE_HALF_WIDTH_M,
    FootContact,
    LogoBox,
    RallyContact,
    TeamChallenges,
    assess_logos,
    centerline_sampling_bound,
    classify_contact,
    open_set,
    request_challenge,
    summarize_match,
)
from engines.msk_validation_audit import (
    CommercialClaim,
    audit_claim,
    benchmarks_frame,
    get_benchmark,
    intensity_ratio_of_means,
    positional_total_jump_means,
)

Q = Decimal


def test_center_line_constants_match_ncaa_line_width() -> None:
    assert CENTER_LINE_HALF_WIDTH_M == Q("0.025")
    assert CENTER_LINE_HALF_WIDTH_M * 2 == Q("0.05")


def test_foot_still_on_the_line_is_not_a_complete_cross() -> None:
    contact = FootContact(
        side="negative",
        min_x_m=Q("-0.01"),
        max_x_m=Q("0.04"),
        contacted_court=True,
    )
    result = classify_contact(
        RallyContact(set_number=1, rally_index=1, foot=contact)
    )
    assert result.foot_completely_crossed is False
    assert result.rule_2026_fault is False
    assert result.legacy_fault is False
    assert result.reviewable_centerline is False


def test_complete_foot_contact_is_a_new_fault_without_interference() -> None:
    contact = FootContact(
        side="negative",
        min_x_m=Q("0.026"),
        max_x_m=Q("0.20"),
        contacted_court=True,
    )
    result = classify_contact(
        RallyContact(set_number=1, rally_index=2, foot=contact)
    )
    assert result.foot_completely_crossed is True
    assert result.legacy_fault is False
    assert result.rule_2026_fault is True
    assert result.reviewable_centerline is True


def test_airborne_foot_beyond_the_line_is_not_a_fault() -> None:
    contact = FootContact(
        side="positive",
        min_x_m=Q("-0.30"),
        max_x_m=Q("-0.026"),
        contacted_court=False,
    )
    result = classify_contact(
        RallyContact(set_number=2, rally_index=1, foot=contact)
    )
    assert result.foot_completely_crossed is True
    assert result.rule_2026_fault is False
    assert result.reviewable_centerline is False


def test_interference_was_already_a_fault_before_2026() -> None:
    contact = FootContact(
        side="negative",
        min_x_m=Q("0.026"),
        max_x_m=Q("0.20"),
        contacted_court=True,
    )
    result = classify_contact(
        RallyContact(
            set_number=1,
            rally_index=3,
            foot=contact,
            interference=True,
        )
    )
    assert result.legacy_fault is True
    assert result.rule_2026_fault is True


def test_nonfoot_cross_faults_only_with_interference() -> None:
    quiet = classify_contact(
        RallyContact(set_number=1, rally_index=4, nonfoot_crossed=True)
    )
    assert quiet.rule_2026_fault is False
    contacted = classify_contact(
        RallyContact(
            set_number=1,
            rally_index=5,
            nonfoot_crossed=True,
            interference=True,
        )
    )
    assert contacted.legacy_fault is True
    assert contacted.rule_2026_fault is True
    assert contacted.reviewable_centerline is False


def test_match_log_counts_only_status_changes() -> None:
    overlapping = FootContact(
        side="negative",
        min_x_m=Q("-0.02"),
        max_x_m=Q("0.02"),
        contacted_court=True,
    )
    cleared = FootContact(
        side="negative",
        min_x_m=Q("0.03"),
        max_x_m=Q("0.18"),
        contacted_court=True,
    )
    summary = summarize_match(
        [
            RallyContact(set_number=1, rally_index=1, foot=overlapping),
            RallyContact(set_number=1, rally_index=2, foot=cleared),
            RallyContact(
                set_number=1,
                rally_index=3,
                foot=cleared,
                interference=True,
                net_fault_on_same_action=True,
            ),
        ]
    )
    assert summary.event_count == 3
    assert summary.legacy_faults == 1
    assert summary.rule_2026_faults == 2
    assert summary.newly_faulted == 1
    assert summary.reviewable_centerline == 2
    assert summary.ancillary_net_on_review == 1


def test_logo_box_must_sit_between_attack_line_and_end_line() -> None:
    legal = LogoBox(
        half="positive",
        near_x_m=Q("3.01"),
        far_x_m=Q("6.01"),
        min_y_m=Q("-1.50"),
        max_y_m=Q("1.50"),
    )
    other_half = LogoBox(
        half="negative",
        near_x_m=Q("-6.01"),
        far_x_m=Q("-3.01"),
        min_y_m=Q("-1.50"),
        max_y_m=Q("1.50"),
    )
    assert assess_logos([legal, other_half]).legal is True

    on_attack_line = legal.model_copy(update={"near_x_m": Q("3.00")})
    front = assess_logos([on_attack_line])
    assert front.legal is False
    assert "marking_clearance" in front.reasons

    oversized = legal.model_copy(update={"far_x_m": Q("6.02")})
    assert "box_limit" in assess_logos([oversized]).reasons

    same_half = legal.model_copy(
        update={"min_y_m": Q("1.60"), "max_y_m": Q("3.20")}
    )
    crowded = assess_logos([legal, same_half])
    assert crowded.legal is False
    assert "one_per_half" in crowded.reasons


def test_sampling_bound_is_two_pixels_across_the_five_centimeter_line() -> None:
    resolved = centerline_sampling_bound(720)
    assert resolved.meters_per_pixel == Q("0.025")
    assert resolved.pixels_across_line == Q("2")
    assert resolved.resolves_line_at_two_pixels is True
    assert centerline_sampling_bound(719).resolves_line_at_two_pixels is False
    with pytest.raises(ValueError):
        centerline_sampling_bound(0)


def test_set_five_challenge_refresh_caps_at_two() -> None:
    fresh = TeamChallenges()
    open_set(fresh, 1)
    assert fresh.remaining == 2
    open_set(fresh, 5)
    assert fresh.remaining == 2

    exhausted = TeamChallenges(remaining=0)
    open_set(exhausted, 5)
    assert exhausted.remaining == 1

    one_left = TeamChallenges(remaining=1)
    open_set(one_left, 5)
    assert one_left.remaining == 2


def test_challenge_inventory_follows_losing_team_and_reviewable_class() -> None:
    state = {"A": TeamChallenges(), "B": TeamChallenges()}
    open_set(state["A"], 1)
    open_set(state["B"], 1)
    reviewable = classify_contact(
        RallyContact(
            set_number=1,
            rally_index=8,
            foot=FootContact(
                side="negative",
                min_x_m=Q("0.04"),
                max_x_m=Q("0.16"),
                contacted_court=True,
            ),
        )
    )
    granted = request_challenge(
        state,
        team="A",
        losing_team="A",
        set_number=1,
        rally_index=8,
        geometry=reviewable,
    )
    assert granted.accepted is True
    assert state["A"].remaining == 1
    second = request_challenge(
        state,
        team="A",
        losing_team="A",
        set_number=1,
        rally_index=8,
        geometry=reviewable,
    )
    assert second.accepted is False
    assert second.reason == "one_challenge_per_dead_ball"
    assert state["A"].remaining == 1

    winner = request_challenge(
        state,
        team="B",
        losing_team="A",
        set_number=1,
        rally_index=9,
        geometry=reviewable,
    )
    assert winner.accepted is False
    assert winner.reason == "only_losing_team"
    assert state["B"].remaining == 2

    not_reviewable = classify_contact(
        RallyContact(set_number=1, rally_index=10, nonfoot_crossed=True)
    )
    denied = request_challenge(
        state,
        team="A",
        losing_team="A",
        set_number=1,
        rally_index=10,
        geometry=not_reviewable,
    )
    assert denied.accepted is False
    assert denied.reason == "not_reviewable"
    assert state["A"].remaining == 1


def test_same_rally_index_in_a_later_set_is_a_new_dead_ball() -> None:
    state = {"A": TeamChallenges()}
    open_set(state["A"], 1)
    reviewable = classify_contact(
        RallyContact(
            set_number=1,
            rally_index=1,
            foot=FootContact(
                side="negative",
                min_x_m=Q("0.04"),
                max_x_m=Q("0.16"),
                contacted_court=True,
            ),
        )
    )
    first = request_challenge(
        state,
        team="A",
        losing_team="A",
        set_number=1,
        rally_index=1,
        geometry=reviewable,
    )
    assert first.accepted is True
    later_set = request_challenge(
        state,
        team="A",
        losing_team="A",
        set_number=2,
        rally_index=1,
        geometry=reviewable,
    )
    assert later_set.accepted is True
    assert later_set.reason == "accepted"
    assert state["A"].remaining == 0
    repeat = request_challenge(
        state,
        team="A",
        losing_team="A",
        set_number=1,
        rally_index=1,
        geometry=reviewable,
    )
    assert repeat.accepted is False
    assert repeat.reason == "one_challenge_per_dead_ball"


def test_sanders_daily_means_and_published_shares_stay_distinct() -> None:
    mb_total = get_benchmark("sanders2025-mb-daily-total")
    mb_50 = get_benchmark("sanders2025-mb-daily-50")
    assert mb_total.mean == Q("84.1")
    assert mb_total.sd == Q("44.9")
    assert mb_total.unit == "jumps_per_day"
    assert mb_total.cohort_id == "ncaa_d1_women_16_week_daily"
    assert mb_50.reported_share == Q("0.446")
    ratio = intensity_ratio_of_means(mb_50, mb_total)
    assert abs(ratio - mb_50.reported_share) > Q("0.01")
    setter = get_benchmark("sanders2025-s-daily-total")
    assert setter.mean == Q("111.6")
    assert get_benchmark("sanders2025-s-daily-38").reported_share == Q("0.170")
    assert get_benchmark("sanders2025-s-daily-50").reported_share == Q("0.003")


def test_claim_audit_refuses_cross_cohort_and_scores_a_matching_claim() -> None:
    claim = CommercialClaim(
        claim_id="synthetic-mb-total",
        vendor="Synthetic Wearable",
        record_status="synthetic_example",
        cohort_id="ncaa_d1_women_16_week_daily",
        position="MB",
        metric="total_jumps",
        unit="jumps_per_day",
        value=Q("84.1"),
        force_plate_r=None,
        peer_reviewed=False,
        source_url="https://example.edu/vvii/synthetic-claim",
    )
    finding = audit_claim(claim)
    assert finding.status == "z_scored"
    assert finding.z == Q("0.0000")
    assert finding.band == "within_one_sd"
    assert finding.meets_force_plate_gate is False

    mismatch = claim.model_copy(
        update={"unit": "jumps_per_match", "claim_id": "synthetic-unit-mismatch"}
    )
    refused = audit_claim(mismatch)
    assert refused.status == "not_comparable"
    assert refused.reason == "unit_mismatch"

    other_cohort = claim.model_copy(
        update={
            "cohort_id": "professional_match_per_hour",
            "unit": "jumps_per_hour",
            "metric": "match_jump_frequency",
            "position": "S",
            "value": Q("67"),
            "claim_id": "synthetic-skazalski-shape",
        }
    )
    # Same shape as Skazalski but that row has no published SD, so no z-score.
    no_dispersion = audit_claim(other_cohort)
    assert no_dispersion.status == "not_comparable"
    assert no_dispersion.reason == "missing_dispersion"


def test_force_plate_threshold_is_not_inferred_from_percent_agreement() -> None:
    rabello = get_benchmark("rabello-roster-weekly-jumps")
    assert rabello.mean == Q("269")
    assert rabello.sd == Q("90")
    assert rabello.unit == "jumps_per_week"
    assert rabello.force_plate_r is None
    skazalski = get_benchmark("skazalski2018-mb-match-per-hour-on-court")
    assert skazalski.mean == Q("98")
    assert skazalski.sd is None
    assert skazalski.instrument == "vert_classic_imu"


def test_benchmark_frame_and_vector_keep_position_order() -> None:
    frame = benchmarks_frame()
    assert isinstance(frame, pd.DataFrame)
    vector = positional_total_jump_means()
    assert isinstance(vector, np.ndarray)
    assert vector.shape == (4,)
    assert vector.tolist() == [84.1, 59.2, 66.5, 111.6]
    beyond = audit_claim(
        CommercialClaim(
            claim_id="synthetic-mb-outlier",
            vendor="Synthetic Wearable",
            record_status="synthetic_example",
            cohort_id="ncaa_d1_women_16_week_daily",
            position="MB",
            metric="total_jumps",
            unit="jumps_per_day",
            value=Q("84.1") + Q("44.9") * Q("2.1"),
            force_plate_r=Q("0.91"),
            peer_reviewed=True,
            source_url="https://example.edu/vvii/synthetic-outlier",
        )
    )
    assert beyond.band == "beyond_two_sd"
    assert beyond.meets_force_plate_gate is True
