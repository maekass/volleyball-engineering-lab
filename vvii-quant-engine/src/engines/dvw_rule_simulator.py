"""Geometry and match-log impact for the 2026–27 NCAA women's volleyball rules.

Court figures follow the women's rules book: an 18 m by 9 m court, lines 5 cm
wide, the attack-line edge farthest from the center line 3 m from the axis, and
a commercial-logo box no larger than 3 m by 3 m between the attack line and the
end line. Rule 15.2.4.3 makes a complete foot cross that contacts the
opponent's court a fault. Rule 18.1.4.7 makes that foot fault reviewable.
Counts are rule-status changes, not a forecast of how officials or coaches behave.

Sources:
- https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/rules/women/PRWVB_RulesBook.pdf
- https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/rules/women/2026-27PRWVB_D1RulesChanges.pdf
- https://ncaaorg.s3.amazonaws.com/championships/sports/volleyball/rules/women/2026-27PRWVB_CRSmanual.pdf
- https://www.ncaa.org/news/media-center-changes-to-center-line-faults-approved-in-womens-volleyball/
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, model_validator

CENTER_LINE_WIDTH_M = Decimal("0.05")
CENTER_LINE_HALF_WIDTH_M = Decimal("0.025")
COURT_LENGTH_M = Decimal(18)
LINE_WIDTH_M = Decimal("0.05")
ATTACK_FAR_EDGE_M = Decimal(3)
END_INNER_M = Decimal(9) - LINE_WIDTH_M
SIDELINE_INNER_M = Decimal("4.5") - LINE_WIDTH_M
LOGO_BOX_LIMIT_M = Decimal(3)


class FootContact(BaseModel):
    """Contact patch plus the optional projection of the whole foot.

    ``min_x_m`` and ``max_x_m`` are the part that touches the court. The
    projection bounds include a part in the air above the center line. A
    raised heel still occupies that line, so the contact patch alone does
    not decide a complete cross.
    """

    model_config = ConfigDict(frozen=True)

    side: str
    min_x_m: Decimal
    max_x_m: Decimal
    contacted_court: bool
    projection_min_x_m: Decimal | None = None
    projection_max_x_m: Decimal | None = None

    @model_validator(mode="after")
    def ordered_patch(self) -> FootContact:
        if self.side not in {"negative", "positive"}:
            raise ValueError("side must be negative or positive")
        if self.min_x_m > self.max_x_m:
            raise ValueError("min_x_m exceeds max_x_m")
        has_min = self.projection_min_x_m is not None
        has_max = self.projection_max_x_m is not None
        if has_min != has_max:
            raise ValueError("projection bounds are supplied as a pair")
        if (
            self.projection_min_x_m is not None
            and self.projection_max_x_m is not None
            and self.projection_min_x_m > self.projection_max_x_m
        ):
            raise ValueError("projection_min_x_m exceeds projection_max_x_m")
        return self


class RallyContact(BaseModel):
    model_config = ConfigDict(frozen=True)

    set_number: int
    rally_index: int
    foot: FootContact | None = None
    nonfoot_crossed: bool = False
    interference: bool = False
    safety_hazard: bool = False
    net_fault_on_same_action: bool = False


class ContactClassification(BaseModel):
    model_config = ConfigDict(frozen=True)

    foot_completely_crossed: bool
    legacy_fault: bool
    rule_2026_fault: bool
    reviewable_centerline: bool
    ancillary_net: bool


class LogoBox(BaseModel):
    model_config = ConfigDict(frozen=True)

    half: str
    near_x_m: Decimal
    far_x_m: Decimal
    min_y_m: Decimal
    max_y_m: Decimal

    @model_validator(mode="after")
    def known_half(self) -> LogoBox:
        if self.half not in {"negative", "positive"}:
            raise ValueError("half must be negative or positive")
        return self


class LogoAssessment(BaseModel):
    model_config = ConfigDict(frozen=True)

    legal: bool
    reasons: tuple[str, ...]


class SamplingBound(BaseModel):
    model_config = ConfigDict(frozen=True)

    meters_per_pixel: Decimal
    pixels_across_line: Decimal
    resolves_line_at_two_pixels: bool
    label: str


class MatchImpact(BaseModel):
    model_config = ConfigDict(frozen=True)

    event_count: int
    legacy_faults: int
    rule_2026_faults: int
    newly_faulted: int
    reviewable_centerline: int
    ancillary_net_on_review: int


def _projection(foot: FootContact) -> tuple[Decimal, Decimal]:
    low = (
        foot.min_x_m
        if foot.projection_min_x_m is None
        else foot.projection_min_x_m
    )
    high = (
        foot.max_x_m
        if foot.projection_max_x_m is None
        else foot.projection_max_x_m
    )
    return low, high


def foot_completely_crossed(foot: FootContact) -> bool:
    """True when the whole foot, including any part above the line, is past it.

    The line belongs to both courts. A heel still above the line means the
    foot has not completely crossed, even if the toes touch the far court.
    """

    low, high = _projection(foot)
    if foot.side == "negative":
        return low > CENTER_LINE_HALF_WIDTH_M
    return high < -CENTER_LINE_HALF_WIDTH_M


def _contacts_opponents_court(foot: FootContact) -> bool:
    if not foot.contacted_court:
        return False
    if foot.side == "negative":
        return foot.max_x_m > CENTER_LINE_HALF_WIDTH_M
    return foot.min_x_m < -CENTER_LINE_HALF_WIDTH_M


def _overlaps_center_line(foot: FootContact) -> bool:
    low, high = _projection(foot)
    return low <= CENTER_LINE_HALF_WIDTH_M and high >= -CENTER_LINE_HALF_WIDTH_M


def classify_contact(event: RallyContact) -> ContactClassification:
    """Classify one contact under Rule 15.2.4.

    A foot may touch the opponent's court while part of it remains on or
    above the center line, unless that contact interferes (Rule 15.2.4.2).
    A complete cross that also touches the court is a fault whether or not
    it interferes (Rule 15.2.4.3). Only that complete foot-cross is the
    center-line fact a challenge reviews. Interference on a partial cross
    is a fault, and it is not that reviewable fact.
    """

    foot = event.foot
    crossed = foot is not None and foot_completely_crossed(foot)
    foot_contact_fault = bool(crossed and foot is not None and foot.contacted_court)
    partial_interference = bool(
        foot is not None
        and _contacts_opponents_court(foot)
        and _overlaps_center_line(foot)
        and event.interference
        and not crossed
    )
    penetrated = foot_contact_fault or partial_interference or (
        foot is not None and _contacts_opponents_court(foot)
    )
    legacy = (penetrated or event.nonfoot_crossed) and (
        event.interference or event.safety_hazard
    )
    other_body = event.nonfoot_crossed and event.interference
    safety = event.safety_hazard and (penetrated or event.nonfoot_crossed)
    rule_2026 = foot_contact_fault or partial_interference or other_body or safety
    return ContactClassification(
        foot_completely_crossed=crossed,
        legacy_fault=legacy,
        rule_2026_fault=rule_2026,
        reviewable_centerline=foot_contact_fault,
        ancillary_net=foot_contact_fault and event.net_fault_on_same_action,
    )


def summarize_match(events: list[RallyContact] | tuple[RallyContact, ...]) -> MatchImpact:
    rows = [classify_contact(event) for event in events]
    return MatchImpact(
        event_count=len(rows),
        legacy_faults=sum(row.legacy_fault for row in rows),
        rule_2026_faults=sum(row.rule_2026_fault for row in rows),
        newly_faulted=sum(row.rule_2026_fault and not row.legacy_fault for row in rows),
        reviewable_centerline=sum(row.reviewable_centerline for row in rows),
        ancillary_net_on_review=sum(row.ancillary_net for row in rows),
    )


def assess_logos(logos: list[LogoBox] | tuple[LogoBox, ...]) -> LogoAssessment:
    reasons: list[str] = []
    counts = {"positive": 0, "negative": 0}
    for logo in logos:
        counts[logo.half] += 1
        low_x = min(logo.near_x_m, logo.far_x_m)
        high_x = max(logo.near_x_m, logo.far_x_m)
        low_y = min(logo.min_y_m, logo.max_y_m)
        high_y = max(logo.min_y_m, logo.max_y_m)
        if (high_x - low_x) > LOGO_BOX_LIMIT_M or (high_y - low_y) > LOGO_BOX_LIMIT_M:
            reasons.append("box_limit")
        if logo.half == "positive":
            inside = low_x > ATTACK_FAR_EDGE_M and high_x < END_INNER_M
        else:
            inside = high_x < -ATTACK_FAR_EDGE_M and low_x > -END_INNER_M
        inside = inside and low_y > -SIDELINE_INNER_M and high_y < SIDELINE_INNER_M
        if not inside:
            reasons.append("marking_clearance")
    for count in counts.values():
        if count > 1:
            reasons.append("one_per_half")
    ordered = tuple(dict.fromkeys(reasons))
    return LogoAssessment(legal=not ordered, reasons=ordered)


def centerline_sampling_bound(frame_pixels_across_court: int) -> SamplingBound:
    """Pixels across a 5 cm line if one frame spans the 18 m court length.

    This is a geometric sampling bound for a single camera aimed at the floor
    plane. It is not a lens calibration, and it does not score a vendor.
    """

    if frame_pixels_across_court <= 0:
        raise ValueError("frame_pixels_across_court must be positive")
    meters_per_pixel = COURT_LENGTH_M / Decimal(frame_pixels_across_court)
    pixels_across_line = CENTER_LINE_WIDTH_M / meters_per_pixel
    return SamplingBound(
        meters_per_pixel=meters_per_pixel,
        pixels_across_line=pixels_across_line,
        resolves_line_at_two_pixels=pixels_across_line >= 2,
        label="geometric sampling bound; not a calibrated camera model",
    )


@dataclass
class TeamChallenges:
    remaining: int = 2
    used_rallies: set[tuple[int, int]] = field(default_factory=set)


@dataclass(frozen=True)
class ChallengeDecision:
    accepted: bool
    reason: str
    team: str = ""
    set_number: int = 0
    rally_index: int = 0


@dataclass(frozen=True)
class ChallengeResolution:
    """Rule 18.1.5.8. A reversal keeps the challenge. A confirmed call, or a
    review that stands for lack of indisputable evidence, spends it.
    """

    outcome: str
    charged: bool
    remaining: int


def open_set(state: TeamChallenges, set_number: int) -> None:
    """Each team starts a match with two challenges.

    At the start of a fifth set the team receives one additional challenge,
    and the inventory cannot exceed two. A dead ball is the pair
    (set number, rally index), so the same rally index in a later set is a
    new challenge opportunity.
    """

    if set_number == 1:
        state.remaining = 2
        state.used_rallies.clear()
    elif set_number == 5:
        state.remaining = min(2, state.remaining + 1)


def request_challenge(
    states: dict[str, TeamChallenges],
    team: str,
    losing_team: str,
    set_number: int,
    rally_index: int,
    geometry: ContactClassification,
    category: str = "center_line",
) -> ChallengeDecision:
    """Accept or refuse the request. Inventory changes only at resolution.

    ``geometry`` is the measured contact. It does not decide whether a
    center-line call may be challenged. A coach can challenge a whistled
    foot fault that the measurement later shows never left the line.
    ``geometry`` is retained so a caller can pass the classification it
    already computed; resolution reads that classification separately.
    """

    del geometry
    team_state = states[team]
    dead_ball = (set_number, rally_index)

    def refused(reason: str) -> ChallengeDecision:
        return ChallengeDecision(False, reason, team, set_number, rally_index)

    if dead_ball in team_state.used_rallies:
        return refused("one_challenge_per_dead_ball")
    team_state.used_rallies.add(dead_ball)
    if team != losing_team:
        return refused("only_losing_team")
    if category != "center_line":
        return refused("not_reviewable")
    if team_state.remaining <= 0:
        return refused("no_challenges_remaining")
    return ChallengeDecision(True, "accepted", team, set_number, rally_index)


def resolve_challenge(
    states: dict[str, TeamChallenges],
    decision: ChallengeDecision,
    *,
    called_fault: bool,
    geometry: ContactClassification,
    conclusive: bool = True,
) -> ChallengeResolution:
    """Apply Rule 18.1.5.8 after the review is watched.

    The reviewed fact is whether the foot completely crossed and contacted
    the opponent's court. When that fact disagrees with the call, the
    outcome is reversed and the challenge is retained. When the video
    confirms the call, or is not conclusive, the challenge is spent.
    """

    if not decision.accepted:
        raise ValueError("an unaccepted challenge has no resolution")
    team_state = states[decision.team]
    actual_complete_cross = geometry.reviewable_centerline
    if not conclusive:
        outcome = "stands"
        reversed_outcome = False
    else:
        reversed_outcome = called_fault != actual_complete_cross
        outcome = "reversed" if reversed_outcome else "confirmed"
    if reversed_outcome:
        return ChallengeResolution(outcome, False, team_state.remaining)
    if team_state.remaining <= 0:
        raise ValueError("no challenge remains to charge")
    team_state.remaining -= 1
    return ChallengeResolution(outcome, True, team_state.remaining)
