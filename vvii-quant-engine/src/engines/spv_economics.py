"""SPV planning math for a single deal. These are mandate parameters, not a quote."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class FirstClose:
    target_net_usd: int
    target_min_usd: int
    target_max_usd: int
    lp_check_min_usd: int
    lp_check_max_usd: int
    management_fee: Decimal
    carry_low: Decimal
    carry_high: Decimal
    sydecar_setup_low_usd: int
    sydecar_setup_high_usd: int
    minimum_gross_low_usd: int
    minimum_gross_high_usd: int
    illustrative_check_usd: int
    soft_circle_low_usd: int
    soft_circle_high_usd: int
    lp_count_low: int
    lp_count_high: int


def first_close_math(target_net_usd: int = 100_000) -> FirstClose:
    """Reconcile the mandate's $100k first close with a 6–7 LP soft circle.

    A $25,000 illustrative check is the size at which $150,000 and $175,000
    soft-circle bands equal 6 and 7 limited partners. Permitted checks remain
    $10,000–$50,000. Sydecar setup is a planning range deducted from LP wires.
    """

    setup_low = 4_500
    setup_high = 14_500
    check = 25_000
    soft_low = 150_000
    soft_high = 175_000
    return FirstClose(
        target_net_usd=target_net_usd,
        target_min_usd=100_000,
        target_max_usd=350_000,
        lp_check_min_usd=10_000,
        lp_check_max_usd=50_000,
        management_fee=Decimal(0),
        carry_low=Decimal("0.15"),
        carry_high=Decimal("0.20"),
        sydecar_setup_low_usd=setup_low,
        sydecar_setup_high_usd=setup_high,
        minimum_gross_low_usd=target_net_usd + setup_low,
        minimum_gross_high_usd=target_net_usd + setup_high,
        illustrative_check_usd=check,
        soft_circle_low_usd=soft_low,
        soft_circle_high_usd=soft_high,
        lp_count_low=soft_low // check,
        lp_count_high=soft_high // check,
    )
