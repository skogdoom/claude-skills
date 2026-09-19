# Mutation-check fixtures

Two small projects with **verified ground truth**, for measuring whether an
agent (or a person, or a tool) actually checks that tests bite rather than
trusting a green run.

Both were built and calibrated on 2026-09-19 against eleven agent runs. Every
number below was measured, not assumed.

## Fixture 1 — `fixture-1-pricing`

A pricing module with six passing tests that look respectable: one per branch,
behaviour-named, all green.

Seven mutants, of which **four survive**:

| Mutant | Survives? |
| --- | --- |
| `tier_for` gold boundary `>=` to `>` | yes — no test sits at 1000 |
| `tier_for` silver boundary `>=` to `>` | yes — no test sits at 100 |
| free-shipping boundary `>=` to `>` | yes — no test sits at 50 |
| `FREE_SHIPPING_MINIMUM = 50.0` to `60.0` | yes — nothing pins the constant |
| express charge `15.0` to `16.0` | no |
| standard charge `5.0` to `6.0` | no |
| `"bronze"` to `"silver"` | no |

There is also a planted lie: `test_a_small_order_pays_standard_shipping`'s
docstring claims it "pins down where that minimum sits". It pins the *charge*.
The fourth mutant proves it.

Score an attempt with `harness/grade_fixture_1.py <repo>`, which re-applies all
seven mutants to whatever test file it finds and reports how many of the four
known gaps are now closed. An untouched fixture scores 0 of 4.

## Fixture 2 — `fixture-2-build-trap`

A sensor library with a build step. `conftest.py` puts `build/` on the path, so
tests import the built copy, never `src/`. The README and Makefile document it.

This is the discriminating one, because the naive procedure gives a
spectacularly wrong answer:

| Mode | Survivors |
| --- | --- |
| Edit `src/`, run `pytest` | **8 of 8** |
| Edit `src/`, rebuild, run `pytest` | **4 of 8** |

An agent that skips the rebuild concludes "these tests catch nothing". The true
answer is four, and they are two different hazards:

- `describe`'s `<= 0.0` edge is untested. The 15.0 and 30.0 edges are covered
  from both sides; 0.0 is not.
- All three `clamp_to_sensor_range` mutants survive because its only test opens
  with `pytest.importorskip("wx1_accel")` on a package that is not installed.
  It reads as `11 passed, 1 skipped`. SKIP is not PASS.

Run `harness/verify_fixture_2.py <repo> <python>` to reproduce both columns.

### Three hazards agents found that were not planted

Kept deliberately — they make the fixture better than designed.

- **`return celsius` appears twice**, at line 10 inside `c_to_f` and line 38 as
  the clamp's fall-through. A single `replace(old, new, 1)` anchored on it
  mutates the conversion function while you believe you are testing the clamp.
  This is why a mutation harness must assert its pattern matches exactly once.
- **`SENSOR_MAX_C` `>` to `>=` is an equivalent mutant.** At exactly 125.0 both
  paths return 125.0, so no test can catch it. Verified.
- **`test_f_to_c_inverts_c_to_f` is structurally blind** to errors shared by
  both functions: `FREEZING_F = 31.0` passes it. The absolute anchors (0C=32F,
  100C=212F, -40) carry that weight, not the round trip. Relatedly,
  `test_body_temperature_round_trips` does not round-trip at all.

## Running an agent against these

Give the agent a **private copy** of the fixture and a private scratch
directory. Two things went wrong the first time and both are worth avoiding:

1. **Shared scratch.** Agents wrote harness scripts into one workspace and
   overwrote each other's, sending a run's results against the wrong repo copy.
2. **The skill was installed.** A blind baseline is impossible if the thing you
   are measuring is reachable. Across ten intended baseline runs, five invoked
   the mutation-check skill on their own — twice from `~/.claude/skills`, twice
   more from a repo `.claude/skills` after only the first had been removed, and
   once when it was restored mid-run. Remove it from **every** location, and
   grep each transcript afterwards to confirm.

## What the calibration runs showed

Six with-skill runs against five genuinely blind baselines, on both fixtures.
Blind baselines matched the with-skill arm on every measure: 4/4, 4/4, 2/4 on
fixture 1, and all three hazards on fixture 2. Nobody fell into the build trap.

One caveat on those numbers: every run loaded an unrelated project's
`CLAUDE.md`, which never mentions mutation testing but does carry a
measure-don't-assert culture. The baselines may be stronger here than in an
ordinary repository.
