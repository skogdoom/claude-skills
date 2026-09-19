"""Ground truth for fixture 2, in the two modes an agent might work in.

Naive: edit src/, run pytest. Correct: edit src/, rebuild, run pytest.
The gap between the two columns is what the fixture exists to measure.
"""
import os, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(sys.argv[1])
PYBIN = sys.argv[2]
SRC = ROOT / "src" / "tempconv.py"
original = SRC.read_text()

MUTANTS = [
    ("freezing boundary <= 0 -> < 0",   "if celsius <= 0.0:",   "if celsius < 0.0:"),
    ("cold/mild boundary < 15 -> <= 15", "if celsius < 15.0:",  "if celsius <= 15.0:"),
    ("mild/hot boundary < 30 -> <= 30",  "if celsius < 30.0:",  "if celsius <= 30.0:"),
    ("FREEZING_F 32 -> 33",             "FREEZING_F = 32.0",    "FREEZING_F = 33.0"),
    ("c_to_f ratio 9/5 -> 9/4",         "celsius * 9.0 / 5.0",  "celsius * 9.0 / 4.0"),
    ("sensor floor -40 -> -50",         "SENSOR_MIN_C = -40.0", "SENSOR_MIN_C = -50.0"),
    ("sensor ceiling 125 -> 200",       "SENSOR_MAX_C = 125.0", "SENSOR_MAX_C = 200.0"),
    ("clamp low guard deleted",         "    if celsius < SENSOR_MIN_C:\n        return SENSOR_MIN_C\n", ""),
]

def pytest_run():
    shutil.rmtree(ROOT / "__pycache__", ignore_errors=True)
    shutil.rmtree(ROOT / "build" / "__pycache__", ignore_errors=True)
    return subprocess.run([PYBIN, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                          cwd=ROOT, capture_output=True, text=True,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})

def build():
    shutil.copy(SRC, ROOT / "build" / "tempconv.py")

print(f"{'mutation':<36} {'naive (no rebuild)':<20} {'correct (rebuild)'}")
print("-" * 76)
naive_survivors = correct_survivors = 0
for name, old, new in MUTANTS:
    assert original.count(old) == 1, f"{name}: pattern appears {original.count(old)}x"
    build()                                  # start from a correct build
    SRC.write_text(original.replace(old, new, 1))
    naive = pytest_run().returncode == 0     # forgot to rebuild
    build()                                  # now rebuild
    correct = pytest_run().returncode == 0
    SRC.write_text(original); build()
    naive_survivors += naive
    correct_survivors += correct
    print(f"{name:<36} {'SURVIVED' if naive else 'caught':<20} {'SURVIVED' if correct else 'caught'}")

print("-" * 76)
print(f"{'survivors':<36} {naive_survivors}/{len(MUTANTS):<19} {correct_survivors}/{len(MUTANTS)}")
assert SRC.read_text() == original
