# Contributing to Antenna

Thanks for your interest. This repo is a small, reproducible antenna study: a CST
Studio Suite VBA macro that builds and simulates five 2.45 GHz patch geometries,
plus a Python toolkit that turns the measured and simulated numbers into the
tables you see in the README. Contributions that improve accuracy,
reproducibility, or add a geometry are welcome.

## What lives where

- `cst/patch-antenna.bas` — the CST VBA macro. Runs inside CST Studio Suite, not
  from a shell (see below).
- `tools/antenna/` — the analysis toolkit (Python, standard-library core).
- `tools/tests/` — the pytest suite.
- `tools/antenna/data/results.json` — the canonical data. Every README table is a
  rendered view of this file, so edit the JSON, not the tables.

## Development setup

The toolkit targets Python 3.9+ and its core is standard-library only:

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip       # editable pyproject installs need pip >= 21.3
pip install -e ".[plots,dev]"   # antenna package + matplotlib (plots) + pytest
```

The core needs nothing beyond the standard library — `pip install -e .` on its
own is enough if you don't need the plots or the test suite.

## Checks

Run both before opening a pull request. CI runs the same two.

```bash
python -m antenna check   # physics validator: tables must match results.json
pytest                    # the test suite
```

`antenna check` reports `0 error(s)` when the data is self-consistent; warnings
and info lines are expected. `pytest` picks up `tools/` and `tools/tests/`
automatically via `pyproject.toml`, so run it from the repo root.

If you change a number in `results.json`, regenerate the README tables so they
stay in sync:

```bash
python -m antenna tables --write
```

There is no separate linter or formatter — keep the diff clean by matching the
surrounding style.

## Running the CST macro

The `.bas` macro is not run from the command line. In CST Studio Suite, open the
VBA macro editor, load `cst/patch-antenna.bas`, set `PatchShape` in `Main` to one
of `circular`, `square`, `triangular`, `hexagonal`, or `fshaped`, and run it. It
builds the substrate, ground plane, patch, feed, port, monitors, and solver from
scratch, then exports the solved sweep to `s11.s1p`. Feed a resulting `.s1p` back
into the toolkit with `python -m antenna ingest path/to/sweep.s1p`.

## Commit style

Short, lowercase, human messages that say what changed. One logical change per
commit.

Examples:

```
updated readme
updated tables
added elliptical patch
```

## Filing an issue

Open an issue on GitHub. For a physics or measurement discrepancy, include the
geometry, whether it is simulation or measurement, the expected vs. observed
number, and the relevant `results.json` field. For a toolkit bug, include the
command you ran and the full output.

## Opening a pull request

1. Branch off `main`.
2. Make your change; keep commits small and focused.
3. Run `python -m antenna check` and `pytest` locally — both must pass.
4. If you touched `results.json`, run `python -m antenna tables --write` and
   commit the regenerated tables.
5. Open a pull request against `main` describing what changed and why.

By contributing you agree your work is released under the project's MIT license.
