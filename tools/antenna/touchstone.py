"""Minimal Touchstone (.s1p) reader for measured/simulated S11 sweeps.

Handles Touchstone v1 one-port files with a ``# <freq-unit> S <format> R <z0>``
option line, in DB/MA/RI formats. Keywords may be reordered or omitted using
the v1 defaults. Other network parameters and Touchstone v2 are unsupported.
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
    reference_ohms: float = 50.0

    def __post_init__(self) -> None:
        self.validate()

    def validate(self) -> None:
        if not isinstance(self.freqs_ghz, (list, tuple)) or not isinstance(self.s11_db, (list, tuple)):
            raise ValueError("sweep frequencies and S11 must be sequences")
        if not self.freqs_ghz or len(self.freqs_ghz) != len(self.s11_db):
            raise ValueError("sweep requires equally sized nonempty frequencies and S11")
        if not _finite(self.reference_ohms) or self.reference_ohms <= 0:
            raise ValueError("reference impedance must be finite and positive")
        previous = -1.0
        for frequency, value in zip(self.freqs_ghz, self.s11_db):
            if not _finite(frequency) or frequency < 0 or frequency <= previous:
                raise ValueError("frequencies must be finite, nonnegative, and strictly increasing")
            if not _finite(value) and value != float("-inf"):
                raise ValueError("S11 must be finite or -inf for zero reflection")
            previous = frequency


def resonance(sweep: Sweep) -> Tuple[float, float]:
    """Return the sampled frequency and S11 of the deepest minimum."""
    sweep.validate()
    i = min(range(len(sweep.s11_db)), key=lambda k: sweep.s11_db[k])
    return sweep.freqs_ghz[i], sweep.s11_db[i]


def band_edges(sweep: Sweep, threshold_db: float = -10.0) -> Optional[Tuple[float, float]]:
    """Interpolate the contiguous threshold band around the deepest minimum.

    Return None if either crossing is outside the sweep or cannot be
    interpolated in dB. Disconnected bands are never merged.
    """
    sweep.validate()
    if not _finite(threshold_db):
        raise ValueError("threshold must be finite")
    low = high = min(range(len(sweep.s11_db)), key=lambda k: sweep.s11_db[k])
    if sweep.s11_db[low] > threshold_db:
        return None
    while low > 0 and sweep.s11_db[low - 1] <= threshold_db:
        low -= 1
    while high + 1 < len(sweep.s11_db) and sweep.s11_db[high + 1] <= threshold_db:
        high += 1
    if low == 0 or high == len(sweep.s11_db) - 1:
        return None
    if not _finite(sweep.s11_db[low]) or not _finite(sweep.s11_db[high]):
        return None

    def crossing(i: int, j: int) -> float:
        fraction = (threshold_db - sweep.s11_db[i]) / (sweep.s11_db[j] - sweep.s11_db[i])
        return sweep.freqs_ghz[i] + fraction * (sweep.freqs_ghz[j] - sweep.freqs_ghz[i])

    return crossing(low - 1, low), crossing(high, high + 1)


def _to_db(a: float, b: float, fmt: str) -> float:
    if fmt == "DB":
        return a
    if fmt == "MA":
        if a < 0:
            raise ValueError("Touchstone magnitude must be nonnegative")
        return 20.0 * math.log10(a) if a > 0 else float("-inf")
    if fmt == "RI":
        mag = abs(complex(a, b))
        return 20.0 * math.log10(mag) if mag > 0 else float("-inf")
    raise ValueError("unknown Touchstone format: %s" % fmt)


def read_s1p(path: str) -> Sweep:
    freq_scale, fmt, reference = _FREQ_SCALE["GHZ"], "MA", 50.0
    options_seen = False
    freqs: List[float] = []
    s11: List[float] = []

    with open(path, "r", encoding="utf-8-sig") as fh:
        for line_number, raw in enumerate(fh, 1):
            line = raw.split("!", 1)[0].strip()
            if not line:
                continue
            if line.startswith("#"):
                if not options_seen:
                    freq_scale, fmt, reference = _options(line[1:])
                    options_seen = True
                continue
            if line.startswith("["):
                raise ValueError("Touchstone v2 is unsupported: %s:%d" % (path, line_number))
            if not options_seen:
                raise ValueError("Touchstone option line required before data: %s:%d" % (path, line_number))
            parts = line.split()
            if len(parts) != 3:
                raise ValueError("one-port data requires exactly three values: %s:%d" % (path, line_number))
            try:
                frequency, a, b = map(float, parts)
                if not all(_finite(value) for value in (frequency, a, b)):
                    raise ValueError("data values must be finite")
                freqs.append(frequency * (freq_scale / 1e9))
                s11.append(_to_db(a, b, fmt))
            except ValueError as exc:
                raise ValueError("%s:%d: %s" % (path, line_number, exc)) from exc

    if not freqs:
        raise ValueError("no data points in %s" % path)
    return Sweep(freqs, s11, reference)


def _finite(value: float) -> bool:
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def _options(line: str) -> Tuple[float, str, float]:
    scale, fmt, reference = _FREQ_SCALE["GHZ"], "MA", 50.0
    tokens = line.upper().split()
    seen = set()
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token in _FREQ_SCALE:
            category, scale = "unit", _FREQ_SCALE[token]
        elif token in ("DB", "MA", "RI"):
            category, fmt = "format", token
        elif token == "S":
            category = "parameter"
        elif token in ("Y", "Z", "H", "G"):
            raise ValueError("only S parameters are supported")
        elif token == "R":
            category = "reference"
            i += 1
            if i == len(tokens):
                raise ValueError("R requires a reference impedance")
            try:
                reference = float(tokens[i])
            except ValueError as exc:
                raise ValueError("invalid reference impedance") from exc
            if not _finite(reference) or reference <= 0:
                raise ValueError("reference impedance must be finite and positive")
        else:
            raise ValueError("unknown Touchstone option: %s" % token)
        if category in seen:
            raise ValueError("duplicate Touchstone %s option" % category)
        seen.add(category)
        i += 1
    return scale, fmt, reference
