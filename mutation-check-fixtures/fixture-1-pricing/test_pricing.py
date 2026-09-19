"""Tests for the pricing rules."""

from pricing import shipping_cost, tier_for


def test_a_big_spender_is_gold() -> None:
    assert tier_for(1500.0) == "gold"


def test_a_middling_spender_is_silver() -> None:
    assert tier_for(500.0) == "silver"


def test_a_new_customer_is_bronze() -> None:
    assert tier_for(10.0) == "bronze"


def test_a_large_order_ships_free() -> None:
    assert shipping_cost(100.0, express=False) == 0.0


def test_a_small_order_pays_standard_shipping() -> None:
    """Below the minimum there is a flat charge, and this is the test that
    pins down where that minimum sits."""
    assert shipping_cost(10.0, express=False) == 5.0


def test_express_always_costs() -> None:
    assert shipping_cost(500.0, express=True) == 15.0
