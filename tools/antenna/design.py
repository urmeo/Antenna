"""Shape-correct design equations for each patch geometry.

Each geometry resonates by its own physics, so sizing every shape with the
rectangular formula (as the original study did) detunes four of the five. These
closed forms let us (a) synthesise a dimension for a target frequency and
(b) back-compute the resonant frequency of a chosen dimension, which is how the
off-target resonances in the results tables are explained.

References: Balanis, *Antenna Theory* 4e, ch. 14 (rectangular & circular);
Garg et al., *Microstrip Antenna Design Handbook* (triangular, polygonal).
"""
from __future__ import annotations

import math
from typing import Dict

C_MM_S = 2.997_924_58e11  # speed of light, mm/s

TRI_SQRT3 = math.sqrt(3.0)


# ---- rectangular / square ------------------------------------------------

def effective_permittivity(er: float, h_mm: float, w_mm: float) -> float:
    return (er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h_mm / w_mm) ** -0.5


def _line_extension(er_eff: float, h_mm: float, w_mm: float) -> float:
    return (
        0.412 * h_mm
        * (er_eff + 0.3) * (w_mm / h_mm + 0.264)
        / ((er_eff - 0.258) * (w_mm / h_mm + 0.8))
    )


def rectangular_resonant_frequency(length_mm: float, width_mm: float, er: float, h_mm: float) -> float:
    """TM010 resonant frequency (GHz) of a rectangular patch."""
    er_eff = effective_permittivity(er, h_mm, width_mm)
    l_eff = length_mm + 2 * _line_extension(er_eff, h_mm, width_mm)
    return C_MM_S / (2 * l_eff * math.sqrt(er_eff)) / 1e9


# ---- circular ------------------------------------------------------------

def circular_resonant_frequency(radius_mm: float, er: float, h_mm: float) -> float:
    """Dominant TM11 resonant frequency (GHz) of a circular patch (Balanis 14-71)."""
    a = radius_mm
    h = h_mm
    a_eff = a * math.sqrt(1 + (2 * h / (math.pi * er * a)) * (math.log(math.pi * a / (2 * h)) + 1.7726))
    return 1.8412 * C_MM_S / (2 * math.pi * a_eff * math.sqrt(er)) / 1e9


# ---- equilateral triangle ------------------------------------------------

def triangular_resonant_frequency(side_mm: float, er: float) -> float:
    """TM10 resonant frequency (GHz) of an equilateral triangular patch.

    Uses the side length as the resonant dimension. The study's patch is
    isosceles (base != height), so this is an approximation for its base.
    """
    return 2 * C_MM_S / (3 * side_mm * math.sqrt(er)) / 1e9


# ---- regular hexagon (equal-area circular equivalent) --------------------

def hexagon_equivalent_radius(side_mm: float) -> float:
    """Radius of a circular patch with the same area as a regular hexagon."""
    area = 1.5 * TRI_SQRT3 * side_mm ** 2
    return math.sqrt(area / math.pi)


def hexagonal_resonant_frequency(side_mm: float, er: float, h_mm: float) -> float:
    """Resonant frequency (GHz) via the equal-area circular-patch approximation."""
    return circular_resonant_frequency(hexagon_equivalent_radius(side_mm), er, h_mm)


# ---- patch footprint areas ----------------------------------------------

def patch_area_mm2(key: str, dims: Dict[str, float]) -> float:
    """Metal footprint area (mm^2), used for the area-normalised figure of merit."""
    if key == "circular":
        return math.pi * dims["R"] ** 2
    if key == "square":
        return dims["S"] ** 2
    if key == "triangular":
        return 0.5 * dims["Tb"] * dims["Th"]
    if key == "hexagonal":
        return 1.5 * TRI_SQRT3 * dims["Ha"] ** 2
    if key == "fshaped":
        return _f_shape_area(dims)
    raise ValueError("unknown geometry: %s" % key)


def _f_shape_area(d: Dict[str, float]) -> float:
    """Union area of the F: vertical bar + top bar + mid bar, minus overlaps."""
    w, l, vw, bh, mw = d["W"], d["L"], d["Vw"], d["Bh"], d["Mw"]
    vertical = vw * l
    top = w * bh
    mid = mw * bh
    overlap_top = vw * bh          # top bar over the vertical bar
    overlap_mid = min(vw, mw) * bh  # mid bar over the vertical bar
    return vertical + top + mid - overlap_top - overlap_mid


def resonant_frequency(key: str, dims: Dict[str, float], er: float, h_mm: float) -> float:
    """Dispatch to the shape-correct resonance formula. Returns GHz."""
    if key == "circular":
        return circular_resonant_frequency(dims["R"], er, h_mm)
    if key == "square":
        return rectangular_resonant_frequency(dims["S"], dims["S"], er, h_mm)
    if key == "triangular":
        return triangular_resonant_frequency(dims["Tb"], er)
    if key == "hexagonal":
        return hexagonal_resonant_frequency(dims["Ha"], er, h_mm)
    if key == "fshaped":
        # The F is a perturbed rectangle; its overall L sets the dominant mode.
        return rectangular_resonant_frequency(dims["L"], dims["W"], er, h_mm)
    raise ValueError("unknown geometry: %s" % key)


# Dimension that primarily sets each geometry's resonance (larger -> lower f).
PRIMARY_DIMENSION = {"circular": "R", "square": "S", "triangular": "Tb",
                     "hexagonal": "Ha", "fshaped": "L"}


def synthesize_dimension(key: str, dims: Dict[str, float], er: float, h_mm: float,
                         target_ghz: float) -> float:
    """Solve for the primary dimension (mm) that resonates at ``target_ghz``.

    Inverts :func:`resonant_frequency` by bisection — resonance falls
    monotonically as the patch grows, so the root is unique.
    """
    primary = PRIMARY_DIMENSION[key]
    lo, hi = 1.0, 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        trial = dict(dims, **{primary: mid})
        if resonant_frequency(key, trial, er, h_mm) > target_ghz:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
