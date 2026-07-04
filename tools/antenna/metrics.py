"""Exact RF relationships shared by every patch geometry.

Return loss (|S11| in dB), reflection-coefficient magnitude, and VSWR are three
views of the same complex reflection at a port. They are linked by closed-form
identities, so any two that disagree signal a recording error — which is exactly
what :mod:`antenna.check` looks for.
"""
from __future__ import annotations

import math

SPEED_OF_LIGHT = 299_792_458.0  # m/s


def reflection_coefficient(s11_db: float) -> float:
    """|Γ| from return loss in dB. Expects s11_db <= 0."""
    return 10.0 ** (s11_db / 20.0)


def vswr_from_s11_db(s11_db: float) -> float:
    """VSWR implied by a return-loss reading."""
    gamma = reflection_coefficient(s11_db)
    return (1.0 + gamma) / (1.0 - gamma)


def s11_db_from_vswr(vswr: float) -> float:
    """Return loss (dB) implied by a VSWR reading."""
    if vswr <= 1.0:
        return float("-inf")
    gamma = (vswr - 1.0) / (vswr + 1.0)
    return 20.0 * math.log10(gamma)


def center_frequency(f_low: float, f_high: float) -> float:
    """Midpoint of a band — the usual proxy for the resonant frequency."""
    return 0.5 * (f_low + f_high)


def fractional_bandwidth_pct(f_low: float, f_high: float, reference: "float | None" = None) -> float:
    """Fractional bandwidth in percent.

    ``reference`` defaults to the band centre; pass the design frequency to
    measure bandwidth relative to the intended operating point instead.
    """
    ref = reference if reference is not None else center_frequency(f_low, f_high)
    return (f_high - f_low) / ref * 100.0
