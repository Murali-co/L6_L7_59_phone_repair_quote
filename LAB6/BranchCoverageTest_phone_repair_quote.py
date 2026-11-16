"""Branch, boundary and pricing tests for Lab 6."""

import pytest

from phone_repair_quote import repair_days, repair_quote, trade_in_value


@pytest.mark.parametrize(
    "part,base,labour",
    [("screen", 4000, 600), ("battery", 1500, 300),
     ("camera", 2500, 300), ("charging_port", 800, 300)],
)
@pytest.mark.parametrize("brand_tier,multiplier", [("budget", 1), ("flagship", 2)])
@pytest.mark.parametrize("under_warranty", [False, True])
@pytest.mark.parametrize("express", [False, True])
def test_repair_quote(part, base, labour, brand_tier, multiplier, under_warranty, express):
    expected_part = 0 if under_warranty and part != "screen" else base * multiplier
    assert repair_quote(part, brand_tier, under_warranty, express) == (
        expected_part + labour + (500 if express else 0)
    )


@pytest.mark.parametrize(
    "part,tier,message",
    [("speaker", "budget", "unknown part"), ("screen", "premium", "unknown brand tier")],
)
def test_invalid_quote(part, tier, message):
    with pytest.raises(ValueError, match=message):
        repair_quote(part, tier, False, False)


@pytest.mark.parametrize("part,delay", [("screen", 5), ("camera", 5), ("battery", 2), ("charging_port", 2)])
@pytest.mark.parametrize("parts_in_stock", [False, True])
@pytest.mark.parametrize("technicians_free,base_days", [(0, 3), (1, 1), (2, 1)])
def test_repair_days(part, delay, parts_in_stock, technicians_free, base_days):
    assert repair_days(part, parts_in_stock, technicians_free) == (
        base_days + (0 if parts_in_stock else delay)
    )


@pytest.mark.parametrize(
    "age,expected",
    [(0, 6000), (12, 6000), (13, 4000), (24, 4000),
     (25, 2000), (48, 2000), (49, 0)],
)
@pytest.mark.parametrize("screen_cracked", [False, True])
def test_trade_in_age_boundaries(age, expected, screen_cracked):
    assert trade_in_value(10000, age, screen_cracked) == (
        expected // 2 if screen_cracked else expected
    )


@pytest.mark.parametrize("price,age", [(0, 12), (-1, 12), (10000, -1)])
def test_invalid_trade_in(price, age):
    with pytest.raises(ValueError, match="invalid input"):
        trade_in_value(price, age, False)


def test_trade_in_rounds_down():
    assert trade_in_value(999, 12, False) == 599
    assert trade_in_value(999, 12, True) == 299
