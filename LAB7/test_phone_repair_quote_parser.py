"""Fuzz tests required by Lab 7, plus behaviour and regression checks."""

import pytest
from hypothesis import given, settings, strategies as st
from phone_repair_quote_parser import mask_imei, parse_parts_order, parse_model

@settings(max_examples=200, derandomize=True, deadline=None)
@given(st.text() | st.none())
def test_mask_imei_no_crash(s):
    try:
        result = mask_imei(s)
    except Exception as exc:
        pytest.fail(f"mask_imei({s!r}) raised {type(exc).__name__}: {exc}")
    assert isinstance(result, str)

@settings(max_examples=200, derandomize=True, deadline=None)
@given(st.text() | st.none())
def test_parse_parts_order_no_crash(s):
    try:
        result = parse_parts_order(s)
    except Exception as exc:
        pytest.fail(f"parse_parts_order({s!r}) raised {type(exc).__name__}: {exc}")
    assert isinstance(result, dict)
    assert all(isinstance(part, str) and part.strip() and isinstance(qty, int) and qty > 0
               for part, qty in result.items())

@settings(max_examples=200, derandomize=True, deadline=None)
@given(st.text() | st.none())
def test_parse_model_no_crash(s):
    try:
        result = parse_model(s)
    except Exception as exc:
        pytest.fail(f"parse_model({s!r}) raised {type(exc).__name__}: {exc}")
    assert isinstance(result, tuple) and len(result) == 2
    assert all(isinstance(value, str) for value in result)


@pytest.mark.parametrize("value,expected", [
    ("35-209900-176148-1", "***********1481"),
    ("35 209900 176148 1", "***********1481"),
    ("35\t209900\n1761481", "***********1481"),
    ("1234", "1234"), ("123", "123"), ("", ""), ("---", ""),
    ("123ABC4567", ""), ("１２３４５", ""), ("١٢٣٤٥", ""),
])
def test_mask_imei_examples(value, expected):
    assert mask_imei(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("screen x1; battery x2", {"screen": 1, "battery": 2}),
    ("screenx1; camera X 3", {"screen": 1, "camera": 3}),
    ("screen x1; screen x2", {"screen": 3}),
    ("external camera x2", {"external camera": 2}),
    ("screen xbad; battery x2;;", {"battery": 2}),
    (" x2; screen x0; camera x-1; battery x1.5", {}),
    ("screen x²; battery x١", {}), ("", {}), ("screen", {}),
    ("screen x" + "9" * 5000, {}),
])
def test_parts_order_examples(value, expected):
    assert parse_parts_order(value) == expected


@pytest.mark.parametrize("value,expected", [
    ("Samsung Galaxy S23", ("Samsung", "Galaxy S23")),
    ("  samsung   Galaxy S23  ", ("Samsung", "Galaxy S23")),
    ("samsung\tGalaxy S23", ("Samsung", "Galaxy S23")),
    ("samsung\nGalaxy S23", ("Samsung", "Galaxy S23")),
    ("Samsung", ("Samsung", "")), ("", ("", "")), (" \t ", ("", "")),
])
def test_model_examples(value, expected):
    assert parse_model(value) == expected


@pytest.mark.parametrize("value", [None, 42, 3.14, True, b"screen x1", [], {}, object()])
def test_non_string_inputs(value):
    assert mask_imei(value) == ""
    assert parse_parts_order(value) == {}
    assert parse_model(value) == ("", "")


@given(st.text(alphabet="0123456789", min_size=5, max_size=50))
def test_mask_preserves_only_last_four(digits):
    result = mask_imei(digits)
    assert result.endswith(digits[-4:])
    assert result[:-4] == "*" * (len(digits) - 4)


@given(st.lists(st.tuples(st.sampled_from(["screen", "battery", "camera", "charging_port"]),
                          st.integers(min_value=1, max_value=100)), max_size=20))
def test_valid_orders_preserve_quantities(items):
    expected = {}
    for part, quantity in items:
        expected[part] = expected.get(part, 0) + quantity
    text = "; ".join(f"{part} x{quantity}" for part, quantity in items)
    assert parse_parts_order(text) == expected
