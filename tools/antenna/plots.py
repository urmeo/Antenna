"""Publication-ready plots derived from the canonical data.

``overview`` works from ``data/results.json`` alone (no external data needed).
``s11_overlay`` consumes Touchstone sweeps once real CST/VNA exports are added.
Matplotlib is imported lazily so the rest of the toolkit stays dependency-free.
"""
from __future__ import annotations

import os
from typing import List, Optional

from .design import resonant_frequency
from .results import Dataset, load


def _pyplot():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    return plt


def overview(out_dir: str, ds: Optional[Dataset] = None) -> List[str]:
    ds = ds or load()
    plt = _pyplot()
    os.makedirs(out_dir, exist_ok=True)
    names = [g.name for g in ds.geometries]
    x = range(len(names))
    written: List[str] = []

    # 1. Simulated vs measured return loss.
    sim = [g.simulation.s11_db for g in ds.geometries]
    meas = [g.measurement.s11_db if g.measurement else float("nan") for g in ds.geometries]
    fig, ax = plt.subplots(figsize=(10, 3.52))
    ax.bar([i - 0.2 for i in x], sim, width=0.4, label="Simulation", color="#3b6ea5")
    ax.bar([i + 0.2 for i in x], meas, width=0.4, label="Measurement", color="#c1666b")
    ax.axhline(-10, ls="--", lw=1, color="#555", label="−10 dB threshold")
    ax.set_xticks(list(x)); ax.set_xticklabels(names)
    ax.set_ylabel("S11 (dB)"); ax.set_title("Return loss: simulation vs measurement")
    ax.legend(); fig.tight_layout()
    p1 = os.path.join(out_dir, "s11_sim_vs_meas.png")
    fig.savefig(p1, dpi=150); plt.close(fig); written.append(p1)

    # 2. Closed-form resonance vs the 2.45 GHz target.
    er, h = ds.substrate.epsilon_r, ds.substrate.height_mm
    fres = [resonant_frequency(g.key, g.dimensions_mm, er, h) for g in ds.geometries]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.bar(names, fres, color="#6a9955")
    ax.axhline(ds.design_frequency_ghz, ls="--", lw=1.5, color="#c1666b",
               label="%.2f GHz target" % ds.design_frequency_ghz)
    for rect, f in zip(bars, fres):
        ax.text(rect.get_x() + rect.get_width() / 2, f + 0.02, "%.2f" % f, ha="center", fontsize=9)
    ax.set_ylabel("Resonant frequency (GHz)")
    ax.set_title("Closed-form resonance vs design target")
    ax.legend(); fig.tight_layout()
    p2 = os.path.join(out_dir, "resonance_vs_target.png")
    fig.savefig(p2, dpi=150); plt.close(fig); written.append(p2)
    return written


def s11_overlay(s1p_paths: List[str], out_path: str, labels: Optional[List[str]] = None) -> str:
    from .touchstone import read_s1p
    plt = _pyplot()
    labels = labels or [os.path.splitext(os.path.basename(p))[0] for p in s1p_paths]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for path, label in zip(s1p_paths, labels):
        sweep = read_s1p(path)
        ax.plot(sweep.freqs_ghz, sweep.s11_db, label=label)
    ax.axhline(-10, ls="--", lw=1, color="#555")
    ax.set_xlabel("Frequency (GHz)"); ax.set_ylabel("S11 (dB)")
    ax.set_title("Measured return loss"); ax.legend()
    fig.tight_layout(); fig.savefig(out_path, dpi=150); plt.close(fig)
    return out_path
