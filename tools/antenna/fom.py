"""Figure-of-merit helpers for a fair cross-geometry comparison.

The five patches occupy very different areas, so raw main-lobe magnitude is not
apples-to-apples. Area-normalised gain and the gain-bandwidth product put them
on a common footing. Main-lobe magnitude (dB) is treated as gain in dBi — an
approximation until measured realised gain is available.
"""
from __future__ import annotations


def gain_linear(main_lobe_db: float) -> float:
    return 10.0 ** (main_lobe_db / 10.0)


def gain_per_area(main_lobe_db: float, area_mm2: float) -> float:
    """Linear gain per cm^2 of metal footprint."""
    return gain_linear(main_lobe_db) / (area_mm2 / 100.0)


def gain_bandwidth_product(main_lobe_db: float, bandwidth_pct: float) -> float:
    return gain_linear(main_lobe_db) * (bandwidth_pct / 100.0)
