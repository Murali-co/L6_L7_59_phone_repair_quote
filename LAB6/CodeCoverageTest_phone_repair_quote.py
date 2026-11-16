"""Targeted examples that execute every application statement (Lab 6)."""

import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


@pytest.mark.parametrize("args,expected", [
    (("screen", "budget", False, False), 4600),
    (("battery", "flagship", True, True), 800),
    (("camera", "flagship", False, False), 5300),
])
def test_line_quote(args, expected):
    assert repair_quote(*args) == expected


@pytest.mark.parametrize("args", [
    ("speaker", "budget", False, False),
    ("screen", "premium", False, False),
])
def test_line_invalid_quote(args):
    with pytest.raises(ValueError):
        repair_quote(*args)


@pytest.mark.parametrize("args,expected", [
    (("screen", False, 0), 8),
    (("battery", False, 1), 3),
    (("camera", True, 1), 1),
])
def test_line_days(args, expected):
    assert repair_days(*args) == expected


@pytest.mark.parametrize("args,expected", [
    ((10000, 12, False), 6000),
    ((10000, 24, False), 4000),
    ((10000, 48, True), 1000),
    ((10000, 49, False), 0),
])
def test_line_trade_in(args, expected):
    assert trade_in_value(*args) == expected


@pytest.mark.parametrize("price,age", [(0, 12), (10000, -1)])
def test_line_invalid_trade_in(price, age):
    with pytest.raises(ValueError):
        trade_in_value(price, age, False)
