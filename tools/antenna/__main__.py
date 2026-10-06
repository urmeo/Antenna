"""Command-line entry point: ``python -m antenna <command>``."""
from __future__ import annotations

import argparse
import os
import sys

from . import check as check_mod
from . import metrics
from . import tables as tables_mod
from .design import PRIMARY_DIMENSION, resonant_frequency, synthesize_dimension
from .results import load

_README = "README.md"


def _cmd_check(args: argparse.Namespace) -> int:
    return check_mod.run(args.data)


def _cmd_tables(args: argparse.Namespace) -> int:
    ds = load(args.data)
    if (args.write or args.check) and not os.path.isfile(args.readme):
        raise ValueError("README not found at %s; pass --readme" % args.readme)
    if args.check:
        errors = tables_mod.check(args.readme, ds)
        for error in errors:
            print(error, file=sys.stderr)
        if not errors:
            print("OK - README tables match results.json.")
        return 1 if errors else 0
    if args.write:
        updated = tables_mod.inject(args.readme, ds)
        if not updated:
            raise ValueError("README contains no recognized table markers")
        print("Updated tables in %s: %s" % (args.readme, ", ".join(updated)))
    else:
        for name, markdown in tables_mod.render_all(ds).items():
            print("### %s\n%s\n" % (name, markdown))
    return 0


def _cmd_design(args: argparse.Namespace) -> int:
    ds = load(args.data)
    er, h = ds.substrate.epsilon_r, ds.substrate.height_mm
    fc = ds.design_frequency_ghz
    frequencies = [resonant_frequency(g.key, g.dimensions_mm, er, h) for g in ds.geometries]
    print("Closed-form estimate vs %.2f GHz target (er=%.1f, h=%.2f mm)\n" % (fc, er, h))
    print("%-12s %-22s %10s %9s" % ("geometry", "dimensions (mm)", "f_res GHz", "detune"))
    for g, f in zip(ds.geometries, frequencies):
        dims = ", ".join("%s=%.2f" % (k, v) for k, v in g.dimensions_mm.items())
        print("%-12s %-22s %10.3f %8.1f%%" % (g.name, dims, f, (f - fc) / fc * 100))
    return 0


def _cmd_synth(args: argparse.Namespace) -> int:
    ds = load(args.data)
    er, h, fc = ds.substrate.epsilon_r, ds.substrate.height_mm, ds.design_frequency_ghz
    targets = [synthesize_dimension(g.key, g.dimensions_mm, er, h, fc) for g in ds.geometries]
    print("Estimated dimension for %.2f GHz (er=%.1f, h=%.2f mm)\n" % (fc, er, h))
    print("%-12s %-9s %10s %12s" % ("geometry", "dim", "current mm", "synth mm"))
    for g, target in zip(ds.geometries, targets):
        primary = PRIMARY_DIMENSION[g.key]
        print("%-12s %-9s %10.2f %12.2f" % (g.name, primary, g.dimensions_mm[primary], target))
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    from .touchstone import band_edges, read_s1p, resonance
    sweeps = [read_s1p(path) for path in args.s1p]
    print("%-24s %10s %8s %8s %8s %9s" % ("file", "f_min GHz", "S11 dB", "VSWR", "BW %", "R ohm"))
    for path, sweep in zip(args.s1p, sweeps):
        f_res, s11_min = resonance(sweep)
        edges = band_edges(sweep)
        bw = "%.2f" % metrics.fractional_bandwidth_pct(*edges) if edges else "n/a"
        print("%-24s %10.4f %8.2f %8.3f %8s %9.2f"
              % (os.path.basename(path), f_res, s11_min, metrics.vswr_from_s11_db(s11_min), bw,
                 sweep.reference_ohms))
    print("BW uses interpolated -10 dB crossings around the deepest minimum; n/a means no complete band.")
    return 0


def _cmd_plot(args: argparse.Namespace) -> int:
    from . import plots
    from .touchstone import read_s1p
    ds = load(args.data)
    if args.s1p is not None:
        if not args.s1p:
            raise ValueError("--s1p requires at least one Touchstone file")
        for path in args.s1p:
            read_s1p(path)
    try:
        plots._pyplot()
    except ModuleNotFoundError as exc:
        if exc.name == "matplotlib":
            raise ValueError("plotting requires the plots extra: pip install '.[plots]'") from exc
        raise
    if args.s1p:
        out = os.path.join(args.out, "s11_overlay.png")
        os.makedirs(args.out, exist_ok=True)
        print("wrote", plots.s11_overlay(args.s1p, out))
    for path in plots.overview(args.out, ds):
        print("wrote", path)
    return 0


def main(argv: "list[str] | None" = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--data", default=None, help="path to results.json")

    parser = argparse.ArgumentParser(prog="antenna", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", parents=[common],
                   help="validate results against the physics").set_defaults(func=_cmd_check)

    p_tables = sub.add_parser("tables", parents=[common], help="render or write the README tables")
    table_action = p_tables.add_mutually_exclusive_group()
    table_action.add_argument("--write", action="store_true", help="inject into the README")
    table_action.add_argument("--check", action="store_true", help="check README tables without writing")
    p_tables.add_argument("--readme", default=_README)
    p_tables.set_defaults(func=_cmd_tables)

    sub.add_parser("design", parents=[common],
                   help="closed-form resonance per geometry").set_defaults(func=_cmd_design)

    sub.add_parser("synth", parents=[common],
                   help="dimension to resonate at the design frequency").set_defaults(func=_cmd_synth)

    p_ingest = sub.add_parser("ingest", parents=[common],
                              help="resonance/VSWR/bandwidth from Touchstone sweeps")
    p_ingest.add_argument("s1p", nargs="+", help="Touchstone .s1p files")
    p_ingest.set_defaults(func=_cmd_ingest)

    p_plot = sub.add_parser("plot", parents=[common],
                            help="write summary plots (and Touchstone overlays)")
    p_plot.add_argument("--out", default="outputs")
    p_plot.add_argument("--s1p", nargs="*", help="Touchstone .s1p files to overlay")
    p_plot.set_defaults(func=_cmd_plot)

    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError) as exc:
        print("antenna: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
