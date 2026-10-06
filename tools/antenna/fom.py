"""Exploratory pattern proxies; reported magnitude is not verified gain."""
from __future__ import annotations

import math


def _finite(value: float) -> bool:
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def gain_linear(main_lobe_db: float) -> float:
    if not _finite(main_lobe_db):
        raise ValueError("pattern magnitude must be finite")
    try:
        return 10.0 ** (main_lobe_db / 10.0)
    except OverflowError as exc:
        raise ValueError("pattern magnitude exceeds numeric range") from exc


def gain_per_area(main_lobe_db: float, area_mm2: float) -> float:
    """Linear pattern proxy per cm^2 of metal footprint."""
    if not _finite(area_mm2) or area_mm2 <= 0:
        raise ValueError("area must be finite and positive")
    return gain_linear(main_lobe_db) / (area_mm2 / 100.0)


def gain_bandwidth_product(main_lobe_db: float, bandwidth_pct: float) -> float:
    if not _finite(bandwidth_pct) or bandwidth_pct < 0:
        raise ValueError("bandwidth must be finite and nonnegative")
    return gain_linear(main_lobe_db) * (bandwidth_pct / 100.0)
