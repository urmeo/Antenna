"""Minimal Touchstone (.s1p) reader for measured/simulated S11 sweeps.

Handles Touchstone v1 one-port files with a ``# <freq-unit> S <format> R <z0>``
option line, in DB/MA/RI formats. This is the entry point for real VNA and CST
exports once they are added under ``data/``.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Optional, Tuple

_FREQ_SCALE = {"HZ": 1.0, "KHZ": 1e3, "MHZ": 1e6, "GHZ": 1e9}


@dataclass
class Sweep:
    freqs_ghz: List[float]
    s11_db: List[float]


def resonance(sweep: Sweep) -> Tuple[float, float]:
    """Frequency (GHz) and depth (dB) of the deepest return-loss point."""
    i = min(range(len(sweep.s11_db)), key=lambda k: sweep.s11_db[k])
    return sweep.freqs_ghz[i], sweep.s11_db[i]


def band_edges(sweep: Sweep, threshold_db: float = -10.0) -> Optional[Tuple[float, float]]:
    """Lowest/highest frequency where S11 stays at or below ``threshold_db``."""
    below = [f for f, v in zip(sweep.freqs_ghz, sweep.s11_db) if v <= threshold_db]
    return (min(below), max(below)) if below else None


def _to_db(a: float, b: float, fmt: str) -> float:
    if fmt == "DB":
        return a
    if fmt == "MA":
        return 20.0 * math.log10(a) if a > 0 else float("-inf")
    if fmt == "RI":
        mag = abs(complex(a, b))
        return 20.0 * math.log10(mag) if mag > 0 else float("-inf")
    raise ValueError("unknown Touchstone format: %s" % fmt)


def read_s1p(path: str) -> Sweep:
    freq_scale, fmt = _FREQ_SCALE["GHZ"], "MA"
    freqs: List[float] = []
    s11: List[float] = []

    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.split("!", 1)[0].strip()
            if not line:
                continue
            if line.startswith("#"):
                tokens = iter(line[1:].upper().split())
                for token in tokens:
                    if token in _FREQ_SCALE:
                        freq_scale = _FREQ_SCALE[token]
                    elif token in ("DB", "MA", "RI"):
                        fmt = token
                    elif token in ("Y", "Z", "H", "G"):
                        raise ValueError("read_s1p supports only S parameters")
                    elif token == "R":
                        resistance = float(next(tokens, "nan"))
                        if not math.isfinite(resistance) or resistance <= 0:
                            raise ValueError("invalid Touchstone reference resistance")
                    elif token != "S":
                        raise ValueError("unknown Touchstone option: %s" % token)
                continue
            parts = line.split()
            if len(parts) < 3:
                raise ValueError("malformed data line in %s: %r" % (path, line))
            freqs.append(float(parts[0]) * freq_scale / 1e9)
            s11.append(_to_db(float(parts[1]), float(parts[2]), fmt))

    if not freqs:
        raise ValueError("no data points in %s" % path)
    return Sweep(freqs, s11)
