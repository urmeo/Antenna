"""Render the README result tables from the canonical data file.

Every table a reader sees is produced here, so the numbers cannot drift from
``data/results.json``. Tables are injected into the README between
``<!-- BEGIN:name -->`` / ``<!-- END:name -->`` markers.
"""
from __future__ import annotations

import re
from typing import Dict, List, Sequence, Tuple

from . import fom
from .design import patch_area_mm2
from .results import Dataset, load

MINUS = "−"

# Invisible header padding so every README table renders at full page width
# with evenly distributed columns (GitHub sizes tables to their content).
# Totals browser-verified against GitHub's rendered HTML; chunks of 10 NBSP
# + space wrap instead of forcing a horizontal scrollbar on narrow screens.
_PAD_CHUNK = "&nbsp;" * 10 + " "
_HEADER_PAD = {"sim-table": 6, "measurement-table": 16, "delta-table": 4, "fom-table": 7}


def _num(value: float, decimals: int) -> str:
    text = "%.*f" % (decimals, abs(value))
    return (MINUS + text) if value < 0 else text


def _signed(value: float, decimals: int) -> str:
    text = "%.*f" % (decimals, abs(value))
    return ("+" + text) if value >= 0 else (MINUS + text)


def _table(headers: Sequence[str], rows: Sequence[Tuple[List[str], bool]]) -> str:
    def emphasise(cells: List[str], bold: bool) -> List[str]:
        return ["**%s**" % c for c in cells] if bold else cells

    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(emphasise(cells, bold)) + " |" for cells, bold in rows]
    return "\n".join(lines)


def simulation_table(ds: Dataset) -> str:
    headers = ["Geometry", "S11 (dB)", "VSWR", "Bandwidth (%)", "Main Lobe (dB)", "Side Lobe (dB)"]
    rows = []
    for g in ds.geometries:
        s = g.simulation
        rows.append(([g.name, _num(s.s11_db, 2), _num(s.vswr, 3), _num(s.bandwidth_pct, 2),
                      _num(s.main_lobe_db, 2), _num(s.side_lobe_db, 1)], g.highlight))
    return _table(headers, rows)


def measurement_table(ds: Dataset) -> str:
    headers = ["Geometry", "S11 (dB)", "VSWR"]
    rows = []
    for g in ds.geometries:
        if g.measurement is None:
            continue
        m = g.measurement
        rows.append(([g.name, _num(m.s11_db, 2), _num(m.vswr, 3)], g.highlight))
    return _table(headers, rows)


def delta_table(ds: Dataset) -> str:
    headers = ["Geometry", "S11 sim (dB)", "S11 meas (dB)", "ΔS11 (dB)",
               "VSWR sim", "VSWR meas", "ΔVSWR"]
    rows = []
    for g in ds.geometries:
        if g.measurement is None:
            continue
        s, m = g.simulation, g.measurement
        rows.append(([g.name, _num(s.s11_db, 2), _num(m.s11_db, 2), _signed(m.s11_db - s.s11_db, 2),
                      _num(s.vswr, 3), _num(m.vswr, 3), _signed(m.vswr - s.vswr, 3)], False))
    return _table(headers, rows)


def figure_of_merit_table(ds: Dataset) -> str:
    headers = ["Geometry", "Footprint (mm²)", "Main Lobe (dB)",
               "Gain ÷ area (cm⁻²)", "Gain × BW"]
    rows = []
    for g in ds.geometries:
        s = g.simulation
        area = patch_area_mm2(g.key, g.dimensions_mm)
        rows.append(([g.name, _num(area, 0), _num(s.main_lobe_db, 2),
                      _num(fom.gain_per_area(s.main_lobe_db, area), 3),
                      _num(fom.gain_bandwidth_product(s.main_lobe_db, s.bandwidth_pct), 3)], g.highlight))
    return _table(headers, rows)


TABLES = {
    "sim-table": simulation_table,
    "measurement-table": measurement_table,
    "delta-table": delta_table,
    "fom-table": figure_of_merit_table,
}


def _pad_header(markdown: str, pad: int) -> str:
    lines = markdown.split("\n")
    cells = [c.strip() for c in lines[0].strip("|").split("|")]
    share, extra = divmod(pad, len(cells))
    padded = [c + _PAD_CHUNK * (share + (1 if i < extra else 0)) for i, c in enumerate(cells)]
    lines[0] = "| " + " | ".join(padded) + "|"
    return "\n".join(lines)


def render_all(ds: Dataset) -> Dict[str, str]:
    return {name: _pad_header(fn(ds), _HEADER_PAD[name]) for name, fn in TABLES.items()}


def inject(readme_path: str, ds: "Dataset | None" = None) -> List[str]:
    """Replace each marked block in the README. Returns the names updated."""
    ds = ds or load()
    with open(readme_path, "r", encoding="utf-8") as fh:
        original = text = fh.read()

    updated: List[str] = []
    for name, markdown in render_all(ds).items():
        pattern = re.compile(
            r"(<!-- BEGIN:%s -->\n).*?(\n<!-- END:%s -->)" % (re.escape(name), re.escape(name)),
            re.DOTALL,
        )
        if pattern.search(text):
            text = pattern.sub(lambda mo: mo.group(1) + markdown + mo.group(2), text)
            updated.append(name)

    if updated and text != original:
        with open(readme_path, "w", encoding="utf-8") as fh:
            fh.write(text)
    return updated
