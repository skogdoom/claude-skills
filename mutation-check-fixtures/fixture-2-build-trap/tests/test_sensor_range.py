"""Clamping is exercised through the vendor's reference implementation."""

import pytest

accel = pytest.importorskip("wx1_accel", reason="vendor accelerator not installed")

from tempconv import clamp_to_sensor_range


def test_clamping_matches_the_vendor_reference() -> None:
    for celsius in (-100.0, -40.0, 0.0, 125.0, 300.0):
        assert clamp_to_sensor_range(celsius) == accel.clamp(celsius)
