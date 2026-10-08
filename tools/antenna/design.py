"""Closed-form sizing estimates for each patch geometry.

Triangle, hexagon, and F-shape estimates approximate their actual geometry.
These calculations do not establish a measured or simulated resonance.

References: Balanis, *Antenna Theory* 4e, ch. 14 (rectangular & circular);
Garg et al., *Microstrip Antenna Design Handbook* (triangular, polygonal).
"""
from __future__ import annotations

import math
from typing import Dict

C_MM_S = 2.997_924_58e11

TRI_SQRT3 = math.sqrt(3.0)
DIMENSIONS = {"circular": ("R",), "square": ("S",),
              "triangular": ("Tb", "Th"), "hexagonal": ("Ha",),
              "fshaped": ("W", "L", "Vw", "Bh", "Sh", "Mw")}


def _positive(value: float, name: str) -> None:
    if not _finite(value) or value <= 0:
        raise ValueError("%s must be finite and positive" % name)


def _finite(value: float) -> bool:
    try:
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
    except OverflowError:
        return False


def _material(er: float, h_mm: float) -> None:
    _positive(er, "relative permittivity")
    if er < 1:
        raise ValueError("relative permittivity must be at least 1")
    _positive(h_mm, "substrate height")


def validate_dimensions(key: str, dims: Dict[str, float]) -> None:
    """Validate dimensions and the non-overlapping F-bar layout."""
    if key not in DIMENSIONS:
        raise ValueError("unknown geometry: %s" % key)
    if not isinstance(dims, dict):
        raise ValueError("dimensions must be an object")
    for name in DIMENSIONS[key]:
        if name not in dims:
            raise ValueError("%s requires dimension %s" % (key, name))
    for name, value in dims.items():
        if key == "fshaped" and name == "Sh":
            if not _finite(value) or value < 0:
                raise ValueError("Sh must be finite and nonnegative")
        else:
            _positive(value, "dimension %s" % name)
    if key == "fshaped":
        if dims["Vw"] > dims["W"] or dims["Mw"] > dims["W"]:
            raise ValueError("F bar widths must not exceed W")
        if 2 * dims["Bh"] + dims["Sh"] > dims["L"]:
            raise ValueError("F bars and their gap must fit within L")


def _result(value: float) -> float:
    _positive(value, "calculated value")
    return value


def effective_permittivity(er: float, h_mm: float, w_mm: float) -> float:
    _material(er, h_mm)
    _positive(w_mm, "patch width")
    return _result((er + 1) / 2 + (er - 1) / 2 * (1 + 12 * h_mm / w_mm) ** -0.5)


def _line_extension(er_eff: float, h_mm: float, w_mm: float) -> float:
    return (
        0.412 * h_mm
        * (er_eff + 0.3) * (w_mm / h_mm + 0.264)
        / ((er_eff - 0.258) * (w_mm / h_mm + 0.8))
    )


def rectangular_resonant_frequency(length_mm: float, width_mm: float, er: float, h_mm: float) -> float:
    """TM010 resonant frequency (GHz) of a rectangular patch."""
    _positive(length_mm, "patch length")
    er_eff = effective_permittivity(er, h_mm, width_mm)
    l_eff = length_mm + 2 * _line_extension(er_eff, h_mm, width_mm)
    return _result(C_MM_S / (2 * l_eff * math.sqrt(er_eff)) / 1e9)


def circular_resonant_frequency(radius_mm: float, er: float, h_mm: float) -> float:
    """Dominant TM11 resonant frequency (GHz) of a circular patch (Balanis 14-71)."""
    _material(er, h_mm)
    _positive(radius_mm, "patch radius")
    a = radius_mm
    h = h_mm
    correction = 1 + (2 * h / (math.pi * er * a)) * (math.log(math.pi * a / (2 * h)) + 1.7726)
    _positive(correction, "circular effective-radius correction")
    a_eff = _result(a * math.sqrt(correction))
    return _result(1.8412 * C_MM_S / (2 * math.pi * a_eff * math.sqrt(er)) / 1e9)


def triangular_resonant_frequency(side_mm: float, er: float) -> float:
    """TM10 resonant frequency (GHz) of an equilateral triangular patch.

    Uses the side length as the resonant dimension. The study's patch is
    isosceles (base != height), so this is an approximation for its base.
    """
    _positive(side_mm, "triangle side")
    _material(er, 1.0)
    return _result(2 * C_MM_S / (3 * side_mm * math.sqrt(er)) / 1e9)


def hexagon_equivalent_radius(side_mm: float) -> float:
    """Radius of a circular patch with the same area as a regular hexagon."""
    _positive(side_mm, "hexagon side")
    return _result(side_mm * math.sqrt(1.5 * TRI_SQRT3 / math.pi))


def hexagonal_resonant_frequency(side_mm: float, er: float, h_mm: float) -> float:
    """Resonant frequency (GHz) via the equal-area circular-patch approximation."""
    return circular_resonant_frequency(hexagon_equivalent_radius(side_mm), er, h_mm)


def patch_area_mm2(key: str, dims: Dict[str, float]) -> float:
    """Metal footprint area (mm^2), used for the area-normalised figure of merit."""
    validate_dimensions(key, dims)
    if key == "circular":
        return _result(math.pi * dims["R"] * dims["R"])
    if key == "square":
        return _result(dims["S"] * dims["S"])
    if key == "triangular":
        return _result(0.5 * dims["Tb"] * dims["Th"])
    if key == "hexagonal":
        return _result(1.5 * TRI_SQRT3 * dims["Ha"] * dims["Ha"])
    if key == "fshaped":
        return _result(_f_shape_area(dims))
    raise ValueError("unknown geometry: %s" % key)


def _f_shape_area(d: Dict[str, float]) -> float:
    """Union area of the F: vertical bar + top bar + mid bar, minus overlaps."""
    w, length, vw, bh, mw = d["W"], d["L"], d["Vw"], d["Bh"], d["Mw"]
    vertical = vw * length
    top = w * bh
    mid = mw * bh
    overlap_top = vw * bh
    overlap_mid = min(vw, mw) * bh
    return vertical + top + mid - overlap_top - overlap_mid


def resonant_frequency(key: str, dims: Dict[str, float], er: float, h_mm: float) -> float:
    """Return the geometry's closed-form frequency estimate in GHz."""
    validate_dimensions(key, dims)
    _material(er, h_mm)
    if key == "circular":
        return circular_resonant_frequency(dims["R"], er, h_mm)
    if key == "square":
        return rectangular_resonant_frequency(dims["S"], dims["S"], er, h_mm)
    if key == "triangular":
        return triangular_resonant_frequency(dims["Tb"], er)
    if key == "hexagonal":
        return hexagonal_resonant_frequency(dims["Ha"], er, h_mm)
    if key == "fshaped":
        return rectangular_resonant_frequency(dims["L"], dims["W"], er, h_mm)
    raise ValueError("unknown geometry: %s" % key)


PRIMARY_DIMENSION = {"circular": "R", "square": "S", "triangular": "Tb",
                     "hexagonal": "Ha", "fshaped": "L"}


def synthesize_dimension(key: str, dims: Dict[str, float], er: float, h_mm: float,
                         target_ghz: float) -> float:
    """Solve for the primary dimension (mm) that resonates at ``target_ghz``.

    Inverts :func:`resonant_frequency` by bisection; resonance falls
    monotonically as the patch grows, so the root is unique.
    """
    if key not in PRIMARY_DIMENSION:
        raise ValueError("unknown geometry: %s" % key)
    validate_dimensions(key, dims)
    _material(er, h_mm)
    _positive(target_ghz, "target frequency")
    primary = PRIMARY_DIMENSION[key]
    lo, hi = 1.0, 200.0
    if key == "fshaped":
        lo = max(lo, 2 * dims["Bh"] + dims["Sh"])
    if lo >= hi:
        raise ValueError("F bar layout exceeds the synthesis search range")

    def freq_at(dim_mm: float) -> float:
        return resonant_frequency(key, dict(dims, **{primary: dim_mm}), er, h_mm)

    if not freq_at(hi) <= target_ghz <= freq_at(lo):
        raise ValueError("target %.3f GHz outside the synthesizable range for %s" % (target_ghz, key))
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if freq_at(mid) > target_ghz:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)
