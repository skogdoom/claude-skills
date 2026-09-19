"""Order pricing: which tier a customer is in, and what shipping costs."""

FREE_SHIPPING_MINIMUM = 50.0
"""Spend at or above this and standard shipping is free."""


def tier_for(spend: float) -> str:
    """Which loyalty tier a lifetime spend puts a customer in."""
    if spend >= 1000.0:
        return "gold"
    if spend >= 100.0:
        return "silver"
    return "bronze"


def shipping_cost(spend: float, express: bool) -> float:
    """What shipping costs on an order.

    Express is a flat charge regardless of order size. Standard is free once
    the order reaches the free-shipping minimum, and a flat charge below it.
    """
    if express:
        return 15.0
    if spend >= FREE_SHIPPING_MINIMUM:
        return 0.0
    return 5.0
