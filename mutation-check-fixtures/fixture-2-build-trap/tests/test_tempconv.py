"""Tests for the WX-1 temperature helpers."""

import pytest

from tempconv import c_to_f, describe, f_to_c


def test_water_freezes_at_32f() -> None:
    assert c_to_f(0.0) == 32.0


def test_water_boils_at_212f() -> None:
    assert c_to_f(100.0) == 212.0


def test_body_temperature_round_trips() -> None:
    assert f_to_c(98.6) == pytest.approx(37.0)


def test_minus_forty_is_the_same_in_both() -> None:
    assert c_to_f(-40.0) == -40.0


def test_f_to_c_inverts_c_to_f() -> None:
    for celsius in (-273.15, -40.0, 0.0, 21.5, 37.0, 100.0):
        assert f_to_c(c_to_f(celsius)) == pytest.approx(celsius)


def test_a_hard_frost_is_freezing() -> None:
    assert describe(-8.0) == "freezing"


def test_an_autumn_morning_is_cold() -> None:
    assert describe(9.0) == "cold"


def test_a_spring_afternoon_is_mild() -> None:
    assert describe(22.0) == "mild"


def test_a_heatwave_is_hot() -> None:
    assert describe(35.0) == "hot"


def test_the_cold_mild_boundary() -> None:
    assert describe(15.0) == "mild"
    assert describe(14.99) == "cold"


def test_the_mild_hot_boundary() -> None:
    assert describe(30.0) == "hot"
    assert describe(29.99) == "mild"
