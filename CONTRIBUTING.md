# Contributing

1. Use Python 3.9+; install `python -m pip install -e ".[plots,dev]"`.
2. Run `antenna check` and `python -m pytest`; document any remaining data warnings.
3. Cite source pages or raw traces for numeric changes; regenerate tables with `antenna tables --write --readme README.md` and plots with `antenna plot --out outputs`.

Edit canonical values in `tools/antenna/data/results.json`. Run the CST macro in a fresh project. Use concise commits such as `updated analysis` or `updated readme`.
