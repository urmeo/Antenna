"""Exact RF identities for readings at the same frequency and port reference.

S11 is a signed dB magnitude; conventional return loss has the opposite sign.
"""
from __future__ import annotations

import math


def reflection_coefficient(s11_db: float) -> float:
    """Return |Γ| from S11 in dB; -inf represents zero reflection."""
    _s11(s11_db)
    try:
        return 10.0 ** (s11_db / 20.0)
    except OverflowError as exc:
        raise ValueError("S11 magnitude is too large to represent") from exc


def vswr_from_s11_db(s11_db: float) -> float:
    """Return VSWR; S11 >= 0 dB represents total reflection or worse."""
    _s11(s11_db)
    if s11_db >= 0.0:
        return float("inf")
    gamma = reflection_coefficient(s11_db)
    if gamma >= 1.0:
        return float("inf")
    return (1.0 + gamma) / (1.0 - gamma)


def s11_db_from_vswr(vswr: float) -> float:
    """Return S11 in dB for VSWR >= 1, including infinite VSWR."""
    if (not _finite(vswr) and vswr != float("inf")) or vswr < 1.0:
        raise ValueError("VSWR must be at least 1")
    if vswr == 1.0:
        return float("-inf")
    if math.isinf(vswr):
        return 0.0
    gamma = (vswr - 1.0) / (vswr + 1.0)
    return 20.0 * math.log10(gamma)


def center_frequency(f_low: float, f_high: float) -> float:
    """Return a band midpoint, which need not be its resonance."""
    _band(f_low, f_high)
    return f_low + (f_high - f_low) / 2.0


def fractional_bandwidth_pct(f_low: float, f_high: float, reference: "float | None" = None) -> float:
    """Fractional bandwidth in percent.

    ``reference`` defaults to the band centre; pass the design frequency to
    measure bandwidth relative to the intended operating point instead.
    """
    _band(f_low, f_high)
    ref = reference if reference is not None else center_frequency(f_low, f_high)
    _positive(ref, "bandwidth reference")
    bandwidth = (f_high - f_low) / ref * 100.0
    if not math.isfinite(bandwidth):
        raise ValueError("fractional bandwidth is too large to represent")
    return bandwidth


def _positive(value: float, name: str) -> None:
    if not _finite(value) or value <= 0:
        raise ValueError("%s must be finite and positive" % name)


def _band(f_low: float, f_high: float) -> None:
    for value in (f_low, f_high):
        if not _finite(value) or value < 0:
            raise ValueError("band frequencies must be finite and nonnegative")
    if f_low > f_high:
        raise ValueError("band edges must be ordered")
    if f_high == 0:
        raise ValueError("band must include a positive frequency")


def _s11(value: float) -> None:
    if not _finite(value) and value != float("-inf"):
        raise ValueError("S11 must be finite or -inf for zero reflection")


def _finite(value: float) -> bool:
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False
