import pytest

from ball001.structural_convergence import (
    relative_change_percent,
)


def test_relative_change_percent() -> None:
    result = relative_change_percent(
        current_value=0.99,
        previous_value=1.00,
    )

    assert result == pytest.approx(
        1.0
    )


def test_relative_change_uses_absolute_difference() -> None:
    result = relative_change_percent(
        current_value=1.01,
        previous_value=1.00,
    )

    assert result == pytest.approx(
        1.0
    )


def test_relative_change_handles_negative_values() -> None:
    result = relative_change_percent(
        current_value=-0.99,
        previous_value=-1.00,
    )

    assert result == pytest.approx(
        1.0
    )


def test_zero_previous_value_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="nonzero",
    ):
        relative_change_percent(
            current_value=1.0,
            previous_value=0.0,
        )