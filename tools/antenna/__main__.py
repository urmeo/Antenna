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

_README = os.path.join(os.path.dirname(__file__), "..", "..", "README.md")


def _cmd_check(args: argparse.Namespace) -> int:
    return check_mod.run(args.data)


def _cmd_tables(args: argparse.Namespace) -> int:
    ds = load(args.data)
    if args.write:
        updated = tables_mod.inject(args.readme, ds)
        print("Updated tables in %s: %s" % (args.readme, ", ".join(updated) or "(none)"))
    else:
        for name, markdown in tables_mod.render_all(ds).items():
            print("### %s\n%s\n" % (name, markdown))
    return 0


def _cmd_design(args: argparse.Namespace) -> int:
    ds = load(args.data)
    er, h = ds.substrate.epsilon_r, ds.substrate.height_mm
    fc = ds.design_frequency_ghz
    print("Closed-form resonance vs %.2f GHz target (er=%.1f, h=%.2f mm)\n" % (fc, er, h))
    print("%-12s %-22s %10s %9s" % ("geometry", "dimensions (mm)", "f_res GHz", "detune"))
    for g in ds.geometries:
        f = resonant_frequency(g.key, g.dimensions_mm, er, h)
        dims = ", ".join("%s=%.2f" % (k, v) for k, v in g.dimensions_mm.items())
        print("%-12s %-22s %10.3f %8.1f%%" % (g.name, dims, f, (f - fc) / fc * 100))
    return 0


def _cmd_synth(args: argparse.Namespace) -> int:
    ds = load(args.data)
    er, h, fc = ds.substrate.epsilon_r, ds.substrate.height_mm, ds.design_frequency_ghz
    print("Dimension to resonate at %.2f GHz (er=%.1f, h=%.2f mm)\n" % (fc, er, h))
    print("%-12s %-9s %10s %12s" % ("geometry", "dim", "current mm", "synth mm"))
    for g in ds.geometries:
        primary = PRIMARY_DIMENSION[g.key]
        target = synthesize_dimension(g.key, g.dimensions_mm, er, h, fc)
        print("%-12s %-9s %10.2f %12.2f" % (g.name, primary, g.dimensions_mm[primary], target))
    return 0


def _cmd_ingest(args: argparse.Namespace) -> int:
    from .touchstone import band_edges, read_s1p, resonance
    print("%-24s %10s %8s %8s %8s" % ("file", "f_res GHz", "S11 dB", "VSWR", "BW %"))
    for path in args.s1p:
        sweep = read_s1p(path)
        f_res, s11_min = resonance(sweep)
        edges = band_edges(sweep)
        bw = metrics.fractional_bandwidth_pct(*edges) if edges else float("nan")
        print("%-24s %10.4f %8.2f %8.3f %8.2f"
              % (os.path.basename(path), f_res, s11_min, metrics.vswr_from_s11_db(s11_min), bw))
    return 0


def _cmd_plot(args: argparse.Namespace) -> int:
    from . import plots
    if args.s1p:
        out = os.path.join(args.out, "s11_overlay.png")
        os.makedirs(args.out, exist_ok=True)
        print("wrote", plots.s11_overlay(args.s1p, out))
    for path in plots.overview(args.out, load(args.data)):
        print("wrote", path)
    return 0


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(prog="antenna", description=__doc__)
    parser.add_argument("--data", default=None, help="path to results.json")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="validate results against the physics").set_defaults(func=_cmd_check)

    p_tables = sub.add_parser("tables", help="render or write the README tables")
    p_tables.add_argument("--write", action="store_true", help="inject into the README")
    p_tables.add_argument("--readme", default=_README)
    p_tables.set_defaults(func=_cmd_tables)

    sub.add_parser("design", help="closed-form resonance per geometry").set_defaults(func=_cmd_design)

    sub.add_parser("synth", help="dimension to resonate at the design frequency").set_defaults(func=_cmd_synth)

    p_ingest = sub.add_parser("ingest", help="resonance/VSWR/bandwidth from Touchstone sweeps")
    p_ingest.add_argument("s1p", nargs="+", help="Touchstone .s1p files")
    p_ingest.set_defaults(func=_cmd_ingest)

    p_plot = sub.add_parser("plot", help="write summary plots (and Touchstone overlays)")
    p_plot.add_argument("--out", default="build/plots")
    p_plot.add_argument("--s1p", nargs="*", help="Touchstone .s1p files to overlay")
    p_plot.set_defaults(func=_cmd_plot)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
