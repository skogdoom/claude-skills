# tempconv

Helpers for the WX-1 temperature sensor.

The tests import the **built** package from `build/`, not the sources in
`src/`. Run `make build` after editing `src/tempconv.py`, or use `make test`,
which builds first.

`tests/test_sensor_range.py` needs the vendor's `wx1_accel` package, which is
not on PyPI. It is skipped when that is missing.
