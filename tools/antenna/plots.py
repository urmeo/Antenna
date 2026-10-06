"""Report comparisons and plots of supplied Touchstone sweeps."""
from __future__ import annotations

import os
from typing import List, Optional

from .design import resonant_frequency
from .results import Dataset, load, validate

FIGSIZE = (9.6, 4.0)
DPI = 150

def _pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def _save(plt, fig, path: str) -> str:
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        fig.savefig(path, dpi=DPI)
    finally:
        plt.close(fig)
    return path


def overview(out_dir: str, ds: Optional[Dataset] = None) -> List[str]:
    ds = ds or load()
    validate(ds)
    er, h = ds.substrate.epsilon_r, ds.substrate.height_mm
    fres = [resonant_frequency(g.key, g.dimensions_mm, er, h) for g in ds.geometries]
    plt = _pyplot()
    os.makedirs(out_dir, exist_ok=True)
    names = [g.name for g in ds.geometries]
    x = range(len(names))
    written: List[str] = []

    sim = [g.simulation.s11_db for g in ds.geometries]
    meas = [g.measurement.s11_db if g.measurement else float("nan") for g in ds.geometries]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    ax.bar([i - 0.2 for i in x], sim, width=0.4, label="Simulation", color="#3b6ea5")
    ax.bar([i + 0.2 for i in x], meas, width=0.4, label="Measurement", color="#c1666b")
    ax.axhline(-10, ls="--", lw=1, color="#555", label="−10 dB threshold")
    ax.set_xticks(list(x)); ax.set_xticklabels(names)
    ax.set_ylabel("S11 (dB)"); ax.set_title("Reported S11 minima at each shape's resonance")
    ax.legend(); fig.tight_layout()
    p1 = os.path.join(out_dir, "s11_sim_vs_meas.png")
    written.append(_save(plt, fig, p1))

    fig, ax = plt.subplots(figsize=FIGSIZE)
    for i, g in enumerate(ds.geometries):
        low, high = g.simulation.band_edges_ghz
        ax.plot([low, high], [i, i], lw=12, solid_capstyle="round", color="#3b6ea5")
        ax.text((low + high) / 2, i + 0.17, "%.4f to %.4f" % (low, high),
                ha="center", fontsize=9)
    ax.axvline(ds.design_frequency_ghz, ls="--", color="#c1666b",
               label="%.2f GHz target" % ds.design_frequency_ghz)
    ax.set_yticks(list(x)); ax.set_yticklabels(names)
    ax.set_ylim(-0.5, len(names) - 0.4)
    ax.set_xlabel("Frequency (GHz)"); ax.set_title("Reported bands: raw sweeps unavailable")
    ax.legend(loc="upper right"); fig.tight_layout()
    p_band = os.path.join(out_dir, "reported_bands.png")
    written.append(_save(plt, fig, p_band))

    fig, ax = plt.subplots(figsize=FIGSIZE)
    bars = ax.bar(names, fres, color="#6a9955")
    ax.axhline(ds.design_frequency_ghz, ls="--", lw=1.5, color="#c1666b",
               label="%.2f GHz target" % ds.design_frequency_ghz)
    for rect, f in zip(bars, fres):
        ax.text(rect.get_x() + rect.get_width() / 2, f + 0.02, "%.2f" % f, ha="center", fontsize=9)
    ax.set_ylabel("Resonant frequency (GHz)")
    ax.set_title("Approximate closed form resonance vs design target")
    ax.legend(); fig.tight_layout()
    p2 = os.path.join(out_dir, "resonance_vs_target.png")
    written.append(_save(plt, fig, p2))
    return written


def s11_overlay(s1p_paths: List[str], out_path: str, labels: Optional[List[str]] = None) -> str:
    from .touchstone import read_s1p
    if not s1p_paths:
        raise ValueError("provide at least one sweep")
    sweeps = [read_s1p(path) for path in s1p_paths]
    plt = _pyplot()
    if labels and len(labels) != len(s1p_paths):
        raise ValueError("got %d labels for %d sweeps" % (len(labels), len(s1p_paths)))
    labels = labels or [os.path.splitext(os.path.basename(p))[0] for p in s1p_paths]
    fig, ax = plt.subplots(figsize=FIGSIZE)
    for sweep, label in zip(sweeps, labels):
        ax.plot(sweep.freqs_ghz, sweep.s11_db, label=label)
    ax.axhline(-10, ls="--", lw=1, color="#555")
    ax.set_xlabel("Frequency (GHz)"); ax.set_ylabel("S11 (dB)")
    ax.set_title("Supplied S11 sweeps"); ax.legend()
    fig.tight_layout()
    return _save(plt, fig, out_path)
