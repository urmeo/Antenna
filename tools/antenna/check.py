"""Validate the canonical results against the physics they must obey.

Errors are hard contradictions (a self-inconsistent simulation row); warnings
are unresolved data issues we already know about (the measurement VSWR that
disagrees with its own return loss, bandwidths that don't follow from the band
edges). CI fails only on errors, so the known-pending items stay visible without
blocking the build.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from . import metrics
from .design import resonant_frequency
from .results import Dataset, load

VSWR_TOL = 0.01
BANDWIDTH_TOL_PCT = 0.3
DETUNE_TOL_PCT = 2.0


@dataclass
class Issue:
    level: str  # "error" | "warning" | "info"
    geometry: str
    field: str
    message: str


def consistency_issues(ds: Dataset) -> List[Issue]:
    issues: List[Issue] = []
    er = ds.substrate.epsilon_r
    h = ds.substrate.height_mm
    fc = ds.design_frequency_ghz

    for g in ds.geometries:
        sim = g.simulation

        # 1. Simulation S11 <-> VSWR must agree exactly (both are one |Gamma|).
        implied = metrics.vswr_from_s11_db(sim.s11_db)
        if abs(implied - sim.vswr) > VSWR_TOL:
            issues.append(Issue("error", g.name, "sim VSWR",
                "S11 %.2f dB implies VSWR %.3f, table says %.3f" % (sim.s11_db, implied, sim.vswr)))

        # 2. Bandwidth must follow from the stated band edges.
        f_lo, f_hi = sim.band_edges_ghz
        bw_center = metrics.fractional_bandwidth_pct(f_lo, f_hi)
        bw_design = metrics.fractional_bandwidth_pct(f_lo, f_hi, reference=fc)
        if min(abs(bw_center - sim.bandwidth_pct), abs(bw_design - sim.bandwidth_pct)) > BANDWIDTH_TOL_PCT:
            issues.append(Issue("warning" if sim.bandwidth_pending else "error", g.name, "bandwidth",
                "edges %.4f-%.4f GHz give %.2f%% (or %.2f%% vs %.2f GHz), table says %.2f%%"
                % (f_lo, f_hi, bw_center, bw_design, fc, sim.bandwidth_pct)))

        # 3. Does the geometry actually resonate near the design frequency?
        f_res = resonant_frequency(g.key, g.dimensions_mm, er, h)
        detune = abs(f_res - fc) / fc * 100.0
        if detune > DETUNE_TOL_PCT:
            issues.append(Issue("info", g.name, "resonance",
                "closed-form resonance %.3f GHz is %.1f%% off the %.2f GHz target" % (f_res, detune, fc)))

        # 4. Measurement S11 <-> VSWR (known-pending until verified against raw traces).
        if g.measurement is not None:
            m = g.measurement
            m_implied = metrics.vswr_from_s11_db(m.s11_db)
            if abs(m_implied - m.vswr) > VSWR_TOL:
                level = "error" if m.verified else "warning"
                issues.append(Issue(level, g.name, "meas VSWR",
                    "S11 %.2f dB implies VSWR %.3f, table says %.3f%s"
                    % (m.s11_db, m_implied, m.vswr, "" if m.verified else " (unverified)")))

    return issues


def run(path: "str | None" = None) -> int:
    ds = load(path)
    issues = consistency_issues(ds)
    if not issues:
        print("OK - all results are physically consistent.")
        return 0

    order = {"error": 0, "warning": 1, "info": 2}
    for issue in sorted(issues, key=lambda i: (order[i.level], i.geometry)):
        print("[%-7s] %-11s %-11s %s" % (issue.level.upper(), issue.geometry, issue.field, issue.message))

    counts = {level: sum(1 for i in issues if i.level == level) for level in order}
    print("\n%(error)d error(s), %(warning)d warning(s), %(info)d info." % counts)
    return 1 if counts["error"] else 0
