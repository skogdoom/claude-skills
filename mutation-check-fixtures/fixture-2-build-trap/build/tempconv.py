"""Temperature conversion and classification for the WX-1 sensor."""

FREEZING_F = 32.0
SENSOR_MIN_C = -40.0
SENSOR_MAX_C = 125.0


def c_to_f(celsius: float) -> float:
    """Celsius to Fahrenheit."""
    return celsius * 9.0 / 5.0 + FREEZING_F


def f_to_c(fahrenheit: float) -> float:
    """Fahrenheit to Celsius."""
    return (fahrenheit - FREEZING_F) * 5.0 / 9.0


def describe(celsius: float) -> str:
    """Plain-language band for a Celsius reading."""
    if celsius <= 0.0:
        return "freezing"
    if celsius < 15.0:
        return "cold"
    if celsius < 30.0:
        return "mild"
    return "hot"


def clamp_to_sensor_range(celsius: float) -> float:
    """Clamp a reading to what the WX-1 can actually report.

    Readings outside this range are the sensor failing, not the weather.
    """
    if celsius < SENSOR_MIN_C:
        return SENSOR_MIN_C
    if celsius > SENSOR_MAX_C:
        return SENSOR_MAX_C
    return celsius
